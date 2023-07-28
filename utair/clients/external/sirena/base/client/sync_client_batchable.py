from typing import List

from utair.clients.external.sirena.base.client.sync_client import SyncClient
from utair.clients.external.sirena.base.messaging import Header, RequestABC, ResponseABC
from utair.clients.external.sirena.base.messaging.batch import Batch
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.base.models.base_client_response import ResponseModelABC
from utair.clients.external.sirena.exceptions import SirenaEncryptionKeyError


class SyncBatchableClient(SyncClient):

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

    def batch_query(
            self,
            request: List[RequestModelABC],
    ) -> List[ResponseModelABC]:
        """
        Точка входа для клиента
        Запрос к сирене
        """
        attempts = 0
        hand_shake_retried = False

        self.connect(self._ignore_connection_calls)
        self._hand_shake()
        batch: Batch = Batch.create([self.request_factory(r) for r in request])

        while attempts < self.max_request_retries:
            try:
                attempts += 1
                batch: Batch = self._make_batch_request(batch)
                batch.received = 0
                if not batch.retries_needed:
                    break
            except SirenaEncryptionKeyError:
                # Один раз попробуем сделать хендшейк заново
                if hand_shake_retried:
                    raise
                self._hand_shake(force=True)
                hand_shake_retried = True
                attempts -= 1

        self.disconnect(self._ignore_connection_calls)
        return batch.responses

    def _make_batch_request(
            self,
            batch: Batch,
    ) -> Batch:
        """
        Запрос в сирену пачкой
        """
        for b in batch.requests:
            # Пишем все запросы в стрим
            if not b.should_try:
                continue
            message: bytes = b.sirena_request.make_message(self.client_id)
            self._connection.send(message)

        # Длинна динамична и может менятся в зависимости от неуспешных ответов
        batch_len = len(batch)
        while batch.received < batch_len:
            # Читаем ответы по очереди, соотносим к айдишнику запроса
            # Получаем заголовок
            header: Header = Header.parse(self._read_header())
            # Соотвествующий на сообщение запрос
            _request: RequestABC = batch.get_request(header.msg_id)
            # Готовим ответ, складываем в него информацию полученную из заголовка
            _response: ResponseABC = self.response_factory(header, _request.method_name)
            _response.parse(self._read_body(_response))

            batch.add_response(ResponseModelABC.parse(_response), header.msg_id)
            batch.received += 1

        # Обнуляем счётчик, на случай, если нужно будет сделать ретрай
        batch.received = 0
        return batch
