from pydantic import Field
from ..base.models.base_client_request import RequestModelABC


class UnArchiveOrder(RequestModelABC):

    rloc: str = Field(description="Номер бронирования")

    lang: str = 'en'

    _method_name: str = 'unarchive_pnr'

    def build(self) -> dict:
        request = {
            "regnum": self.rloc
        }
        return request
