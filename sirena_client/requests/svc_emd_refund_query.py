from pydantic import Field
from typing import List
from sirena_client.base.models.base_client_request import RequestModelABC


class SVCRefundRequest(RequestModelABC):
    """
    Запрос на возврат оформленных услуг.
    """
    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")
    version: str = Field(description="Версия брони", default="ignore")
    service_ids: List[int] = Field(description="Доп. услуги")
    involuntary: bool = Field(default=False, description="Признак добровольного обмена")

    lang: str = 'en'

    _method_name: str = 'svc_emd_refund_query'

    def build(self) -> dict:
        request_params = {}

        answer_params = {
            "lang": self.lang
        }

        request = {
            'regnum': {
                '#text': self.rloc,
                '@version': self.version
            },
            'svc': [{'@id': i} for i in self.service_ids],
            "involuntary": self.involuntary,
            "request_params": request_params,
            "answer_params": answer_params
        }

        return request
