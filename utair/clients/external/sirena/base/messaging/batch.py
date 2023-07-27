from dataclasses import dataclass
from typing import List, Dict
from utair.clients.external.sirena.base.messaging.request import RequestABC
from utair.clients.external.sirena.base.models.base_client_response import ResponseModelABC


@dataclass
class Request:
    sirena_request: RequestABC                  # Подготовленный низкоуровневый запрос в сирену
    client_response: ResponseModelABC = None    # Высокоуровневый ответ клиенту

    @property
    def should_try(self):
        """ Нужно попробовать отправить запрос, если ответа нет, либо сирена просит попробовать ещё раз"""
        return self.client_response is None or self.client_response.should_retry


@dataclass
class Batch:
    _request_map: Dict[int, Request]
    received: int = 0

    def __len__(self) -> int:
        if retries := self.retries_needed:
            return retries
        return len(self._request_map.values())

    @property
    def retries_needed(self) -> int:
        return len([r for r in self.requests if r.should_try])

    @classmethod
    def create(
            cls,
            sirena_requests: List[RequestABC]
    ) -> "Batch":
        return cls(_request_map={r.msg_id: Request(r) for r in sirena_requests})

    def get_request(self, msg_id: int) -> RequestABC:
        return self._request_map[msg_id].sirena_request

    def add_response(self, response: ResponseModelABC, msg_id: int):
        self._request_map[msg_id].client_response = response

    @property
    def responses(self) -> List[ResponseModelABC]:
        return [b.client_response for b in self._request_map.values()]

    @property
    def requests(self) -> List[Request]:
        return [r for r in self._request_map.values()]
