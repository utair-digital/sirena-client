from typing import List, Union
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class RemoveSsrsRequest(RequestModelABC):

    rloc: str = Field(description="Номер бронирования")
    last_name: str = Field(description="Фамилия пассажира")
    ssr_keys: List[int] = Field(description="Список идентификаторов сср для удаления")

    version: str

    lang: str = 'en'

    _method_name: str = 'modify_pnr'

    def build(self) -> dict:
        request = {
            "regnum": {
                '#text': self.rloc,
                '@version': self.version
            },
            "surname": self.last_name,
            "remove": {
                "ssr": [{"@key": ind} for ind in self.ssr_keys]
            }
        }
        return request
