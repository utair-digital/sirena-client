import aiofile
import os
import json

from typing import Optional

from opentelemetry import trace
from .base_client import BaseClient
from ..connection import AsyncConnection, AsyncConnectionPool
from ..messaging import RequestABC, ResponseABC, Header
from ..models.base_client_request import RequestModelABC, KeyInfoRequest, AsymEncryptionHandShakeRequest
from ..models.base_client_response import ResponseModelABC
from ..cache.async_cache import AsyncCacheController
from ...exceptions import (
    SirenaEncryptionKeyError,
    SirenaMaxRetriesExceededError,
    SirenaEmptyResponse
)


class AsyncClient(BaseClient):

    def __init__(
            self,
            host: str,
            port: int,
            client_id: int,
            redis_url: str = None,
            private_key: str = None,
            private_key_path: str = None,
            pool: Optional[AsyncConnectionPool] = None,
            logger_name: str = 'sirena_client',
    ):
        """
        :param host: хост сирены
        :param port: порт
        :param client_id: ID клиента
        :param redis_url: URL Redis для кэширования симметричного ключа
        :param private_key: приватный ключ строкой
        :param private_key_path: путь к файлу с приватным ключом
        """
        super().__init__(
            host=host,
            port=port,
            redis_url=redis_url,
            private_key_path=private_key_path,
            private_key=private_key,
            client_id=client_id,
            logger_name=logger_name
        )

        self._connection: Optional[AsyncConnectionPool] = pool
        self._inited_with_pool = True if pool else False
        self._hand_shaking = False

        self.cache: AsyncCacheController = AsyncCacheController(self.redis_url)

        if not self._inited_with_pool:
            self._connection = AsyncConnectionPool(self.host, self.port)

    async def query(self, request: RequestModelABC, silent: bool = False) -> ResponseModelABC:
        """
        Точка входа для клиента
        Запрос к сирене
        """
        with trace.get_tracer("sirena-client").start_span(f"sirena request: {request.method_name}") as span:
            span.set_attribute("method", request.method_name)
            span.set_attribute("sirena.client", self.client_id)
            span.set_attribute("sirena.host", self.host)

            await self.connect(self._ignore_connection_calls)
            async with self._connection.get() as connection:
                await self._hand_shake(connection)
                result = await self._query(request, connection)
                self.logger.info(f"Sirena request: {request.method_name}", extra=dict(
                    sirena_request=json.dumps(request.build(), indent=4),
                    sirena_response=json.dumps(request.build(), indent=4)
                ))
            await self.disconnect(self._ignore_connection_calls)
        if not silent:
            result.raise_for_error()
        return result

    async def _hand_shake(self, connection: AsyncConnection, force: bool = False):
        """
        Обмениваемся ключами и сохраняем их
        """
        await self.cache.spin_up()
        if self.hand_shake_done and not force:
            return

        if not force and self.cache.is_available:
            # Берём из кэша, если есть
            seed, _id = await self.cache.get()
            if all((seed, _id)):
                self._keys.sym_key_seed, self._keys.sym_key_id = seed, _id
                self.hand_shake_done = True
                return

        if self.cache.is_available:
            # Чистим кэш
            await self.cache.purge()

        if not self._keys.private_key:
            # TODO test from string
            await self.load_private_key()

        self.logger.debug(f"Handshaking, is_force: {force}")
        self._keys.reset_des_ecb()
        # Запрашиваем у сирены паб ключ
        key_info = await self._query(KeyInfoRequest(), connection)
        key_info.raise_for_error()
        self._keys.set_pub_key(key_info.data)

        # Обмениваемся ключами, получаем симметричный ключ
        response = await self._query(AsymEncryptionHandShakeRequest(), connection)
        response.raise_for_error()
        self._keys.sym_key_id = response.response.key_id

        # Кэшируем ключ
        if self.cache.is_available:
            await self.cache.set(self._keys.sym_key_seed, self._keys.sym_key_id)
        self.logger.debug(f"Handshake done.")
        self.hand_shake_done = True

    async def _query(self, request: RequestModelABC, connection: AsyncConnection) -> ResponseModelABC:
        attempts = 0
        hand_shake_retried = False
        while attempts < self.max_request_retries:
            attempts += 1
            try:
                _request: RequestABC = self.request_factory(request)
                _response: ResponseABC = await self._send_msg(_request, connection)
                if not bool(_response):
                    continue    # Сирена просит попробовать еще раз
                response: ResponseModelABC = ResponseModelABC.parse(_response)
                return response
            except SirenaEncryptionKeyError:
                if hand_shake_retried:
                    raise
                await self._hand_shake(connection, force=True)
                hand_shake_retried = True
                attempts -= 1

        raise SirenaMaxRetriesExceededError()

    async def _send_msg(self, r: RequestABC, connection: AsyncConnection) -> Optional[ResponseABC]:
        """
        Низкоуровневый запрос в сирену
        """
        # Один раз пишем в стрим
        message: bytes = r.make_message(self.client_id)
        await connection.write(message)
        # Получаем заголовок
        header: Header = Header.parse(await self._read_header(connection))
        # Готовим ответ, складываем в него информацию полученную из заголовка
        response: ResponseABC = self.response_factory(header, r.method_name)
        # Получаем тело в ответ
        body: bytes = await self._read_body(response, connection)
        response.parse(body)
        return response

    # noinspection PyMethodMayBeStatic
    async def _read_header(self, connection: AsyncConnection) -> bytes:
        """ Читаем заголовок """
        header: bytes = await connection.read(Header.size)
        if not header:
            raise SirenaEmptyResponse()
        while len(header) < Header.size:
            header += await connection.read(Header.size - len(header))
        return header

    async def _read_body(self, r: ResponseABC, connection: AsyncConnection) -> bytes:
        """ Читаем тело """
        data: bytes = b''
        # Читаем из стрима по всему размеру
        while r.body_len > 0:
            chunk = await connection.read(min(r.body_len, self.read_chunk_size))
            data += chunk
            r.body_len -= len(chunk)
        return data

    async def __aenter__(self) -> "AsyncClient":
        await self.connect(ignore=False)
        self._ignore_connection_calls = True
        return self

    async def __aexit__(self, *args, **kwargs):
        # В случае если при создании объекта был передан пул соединений
        # подключением и отключением управляет сам пул
        await self.disconnect(ignore=False)
        self._ignore_connection_calls = False

    async def connect(self, ignore: bool = False):
        if any((
            ignore,
            self.connected,
            self._inited_with_pool,
        )):
            return
        # Если пул соединений не был передан при создания объекта - покдлючимся сами
        self._connection = AsyncConnectionPool(
            self.host,
            self.port,
        )
        await self._connection.fill_free()

    async def disconnect(self, ignore: bool = False):
        if any((
            # В случае если при создании объекта был передан пул соединений
            # подключение и отключением управляет сам пул
            ignore, self.connected, self._inited_with_pool
        )):
            return
        await self._connection.close()

    async def load_private_key(self) -> bool:
        if super().load_private_key():
            return True
        async with aiofile.async_open(os.path.abspath(self.private_key_path)) as key_file:
            self._keys.private_key = self._keys.parse_rsa_key(await key_file.read())
        return True
