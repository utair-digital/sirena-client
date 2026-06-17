from typing import List
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import (
    RequestModelABC,
)


class EmdPrintRequest(RequestModelABC):
    """Запрос печатной формы EMD"""

    emds: List[str] = Field(description="Список EMD для формирования печатной формы")

    lang: str = "en"

    _method_name: str = "emd_print"

    def build(self) -> dict:
        request = {"emd": self.emds, "answer_params": {"lang": self.lang}}
        return request
