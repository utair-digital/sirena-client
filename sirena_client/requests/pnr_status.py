from pydantic import Field
from ..base.models.base_client_request import RequestModelABC


class PnrStatus(RequestModelABC):
    rloc: str = Field(description="Номер PNR")

    lang: str = "en"

    _method_name: str = "pnr_status"

    def build(self) -> dict:
        request = {
            "regnum": {
                "#text": self.rloc,
            },
        }
        return request
