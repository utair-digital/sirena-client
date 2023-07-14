import os
import socket
import json

from typing import Optional
from ...exceptions import (
    SirenaEncryptionKeyError,
    SirenaMaxRetriesExceededError,
    SirenaEmptyResponse
)
from .base_client import BaseClient
from ..cache.sync_cache import SyncCacheController
from ..messaging import Header, RequestABC, ResponseABC
from ..models.base_client_request import RequestModelABC, KeyInfoRequest, AsymEncryptionHandShakeRequest
from ..models.base_client_response import ResponseModelABC


class SyncClient(BaseClient):

    def __init__(
            self,
            host: str,
            port: int,
            client_id: int,
            redis_url: str = None,
            private_key: str = None,
            private_key_path: str = None,
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
        self._connection: Optional[socket] = None
        self.cache: SyncCacheController = SyncCacheController(self.redis_url)

    def query(self, request: RequestModelABC, silent: bool = False) -> ResponseModelABC:
        """
        Точка входа для клиента
        Запрос к сирене
        """
        self.connect(self._ignore_connection_calls)
        self._hand_shake()
        result = self._query(request)
        self.logger.info(f"Sirena request: {request.method_name}", extra=dict(
            sirena_request=json.dumps(request.build(), indent=4),
            sirena_response=json.dumps(request.build(), indent=4)
        ))
        self.disconnect(self._ignore_connection_calls)
        if not silent:
            result.raise_for_error()
        return result

    def _hand_shake(self, force: bool = False):
        """
        Обмениваемся ключами и сохраняем их
        """
        self.cache.spin_up()
        if self.hand_shake_done and not force:
            return

        if not force and (self.cache.is_available and self.cache.exists):
            # Берём из кэша, если есть
            seed, _id = self.cache.get()
            if all((seed, _id)):
                self._keys.sym_key_seed, self._keys.sym_key_id = seed, _id
                self.hand_shake_done = True
                return

        if self.cache.is_available:
            # Чистим кэш
            self.cache.purge()

        if not self._keys.private_key:
            if self.private_key:
                # Парсим из строки, если есть строка
                self._keys.private_key = self._keys.parse_rsa_key(self.private_key)
            else:
                # Читаем из файла приватный ключ
                with open(os.path.abspath(self.private_key_path)) as key_file:
                    self._keys.private_key = self._keys.parse_rsa_key(key_file.read()) # noqa
        self.logger.debug(f"Handshaking, is_force:{force}")
        self._keys.reset_des_ecb()
        # Запрашиваем у сирены паб ключ
        key_info = self._query(KeyInfoRequest())
        key_info.raise_for_error()
        self._keys.set_pub_key(key_info.data)

        # Обмениваемся ключами, получаем симметричный ключ
        self._keys.is_able_to_asym()
        response = self._query(AsymEncryptionHandShakeRequest())
        response.raise_for_error()
        self._keys.sym_key_id = response.response.key_id

        # Кэшируем ключ
        if self.cache.is_available:
            self.cache.set(self._keys.sym_key_seed, self._keys.sym_key_id)
        self.logger.debug(f"Handshake done.")
        self.hand_shake_done = True

    def _query(self, request: RequestModelABC) -> ResponseModelABC:
        attempts = 0
        hand_shake_retried = False
        while attempts < self.max_request_retries:
            attempts += 1
            try:
                _request: RequestABC = self.request_factory(request)
                _response: ResponseABC = self._send_msg(_request)
                if not bool(_response):
                    continue    # Сирена просит попробовать еще раз
                response: ResponseModelABC = ResponseModelABC.parse(_response)
                return response
            except SirenaEncryptionKeyError:
                if hand_shake_retried:
                    raise
                self._hand_shake(force=True)
                hand_shake_retried = True
                attempts -= 1

        raise SirenaMaxRetriesExceededError()

    def _send_msg(self, r: RequestABC) -> ResponseABC:
        """
        Низкоуровневый запрос в сирену
        """
        message: bytes = r.make_message(self.client_id)
        self._connection.send(message)
        # Получаем заголовок
        header: Header = Header.parse(self._read_header())
        # Готовим ответ, складываем в него информацию полученную из заголовка
        response: ResponseABC = self.response_factory(header, r.method_name)
        # Получаем тело в ответ
        body: bytes = self._read_body(response)
        response.parse(body)
        # Возвращаем только ответы
        return response

    def _read_header(self) -> bytes:
        """ Читаем заголовок """
        header: bytes = self._connection.recv(Header.size)
        if not header:
            raise SirenaEmptyResponse()
        while len(header) < Header.size:
            header += self._connection.recv(Header.size - len(header))
        return header

    def _read_body(self, r: ResponseABC) -> bytes:
        data: bytes = b''
        # Читаем из стрима по всему размеру
        while r.body_len > 0:
            chunk = self._connection.recv(min(r.body_len, self.read_chunk_size))
            data += chunk
            r.body_len -= len(chunk)
        return data

    def __enter__(self) -> "SyncClient":
        self._ignore_connection_calls = True
        self.connect(ignore=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect(ignore=False)
        self._ignore_connection_calls = False

    def connect(self, ignore: bool = False):
        if ignore:
            return
        if self.connected:
            return
        _sock = socket.socket()
        _sock.connect((self.host, self.port))
        if not _sock:
            raise ConnectionError(f'Can not get connection to {self.host}:{self.port}')
        self._connection = _sock

    def disconnect(self, ignore: bool = False):
        if any((
            ignore, not self.connected
        )):
            return
        if not self._connection:
            return
        self._connection.close()
        self._connection = None
