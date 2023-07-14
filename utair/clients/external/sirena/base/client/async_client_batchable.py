from typing import Optional, List
from opentelemetry import trace

from .async_client import AsyncClient
from ..connection.async_connection import AsyncConnection
from ..connection.async_pool import AsyncConnectionPool
from ..messaging import Header, RequestABC, ResponseABC
from ..messaging.batch import Batch
from ..models.base_client_request import RequestModelABC
from ..models.base_client_response import ResponseModelABC
from ...exceptions import SirenaEncryptionKeyError


class AsyncBatchableClient(AsyncClient):

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
            pool=pool,
            logger_name=logger_name
        )

    async def batch_query(
            self,
            request: List[RequestModelABC],
    ) -> List[ResponseModelABC]:
        """
        Точка входа для клиента
        Запрос к сирене
        """
        attempts = 0
        hand_shake_retried = False

        with trace.get_tracer("sirena-client").start_span(
                f"sirena request: batch request of len {len(request)}"
        ) as span:
            span.set_attribute("sirena.client", self.client_id)
            span.set_attribute("sirena.host", self.host)

            await self.connect(self._ignore_connection_calls)

            async with self._connection.get() as connection:
                await self._hand_shake(connection)
                batch: Batch = Batch.create([self.request_factory(r) for r in request])

                while attempts < self.max_request_retries:
                    try:
                        attempts += 1
                        batch: Batch = await self._make_batch_request(batch, connection)
                        batch.received = 0
                        if not batch.retries_needed:
                            break
                    except SirenaEncryptionKeyError:
                        # Один раз попробуем сделать хендшейк заново
                        if hand_shake_retried:
                            raise
                        await self._hand_shake(connection, force=True)
                        hand_shake_retried = True
                        attempts -= 1

            await self.disconnect(self._ignore_connection_calls)
        return batch.responses

    async def _make_batch_request(
            self,
            batch: Batch,
            connection: AsyncConnection
    ) -> Batch:
        """
        Запрос в сирену пачкой
        """
        for b in batch.requests:
            # Пишем все запросы в стрим
            if not b.should_try:
                continue
            message: bytes = b.sirena_request.make_message(self.client_id)
            await connection.write(message)

        # Длинна динамична и может меняться в зависимости от неуспешных ответов
        batch_len = len(batch)
        while batch.received < batch_len:
            # Читаем ответы по очереди, соотносим к айдишнику запроса
            # Получаем заголовок
            header: Header = Header.parse(await self._read_header(connection))
            # Соответствующий на сообщение запрос
            _request: RequestABC = batch.get_request(header.msg_id)
            # Готовим ответ, складываем в него информацию полученную из заголовка
            _response: ResponseABC = self.response_factory(header, _request.method_name)
            _response.parse(await self._read_body(_response, connection))

            batch.add_response(ResponseModelABC.parse(_response), header.msg_id)
            batch.received += 1

        # Обнуляем счётчик, на случай, если нужно будет сделать ретрай
        batch.received = 0
        return batch
