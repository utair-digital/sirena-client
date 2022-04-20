from typing import Dict
from pydantic import Field
from sirena_client.base.models.base_client_request import RequestModelABC


class PlainRequest(RequestModelABC):
    """
    Запрос в сирену без привязки к методу и данным
    """

    body: Dict = Field(description="Целевой запрос в сирену")
    method: str = Field(description="Целевой метод")

    def build(self) -> dict:
        return self.body

    @property
    def method_name(self) -> str:
        return self.method
