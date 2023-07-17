from pydantic import Field
from typing import List
from ..base.models.base_client_request import RequestModelABC


class SVCEmdVoidRequest(RequestModelABC):
    """
    Аннулирование емд услуг.
    Аннулировать емд услуг можно только в течение суток с момента оформления.
    """

    rloc: str = Field(description="Номер PNR")
    service_ids: List[str] = Field()
    version: str = Field(description="Версия брони", default="ignore")

    lang: str = 'en'

    _method_name: str = 'svc_emd_void'

    def build(self) -> dict:
        request = {
            "regnum": {
                "#text": self.rloc,
                "@version": self.version
            },
            "svc": [{"@id": x} for x in self.service_ids],
            "answer_params": {
                "lang": self.lang
            }
        }
        return request
