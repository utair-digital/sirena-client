from typing import List
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import (
    RequestModelABC,
)


class EmdPrintRequest(RequestModelABC):
    """Запрос печатной формы EMD"""

    emds: List[str] = Field(description="Список EMD для формирования печатной формы")

    _method_name: str = "emd_print"

    def build(self) -> dict:
        request = {"emd": self.emds}
        return request
