from pydantic import Field
from typing import List
from ..base.models.base_client_request import RequestModelABC
from common import PaymentCost


class ConfirmRefundServicesRequest(RequestModelABC):
    """
    Подтверждение возврата офоромленных услуг.
    """
    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")
    version: str = Field(description="Версия брони", default="ignore")
    service_ids: List[int] = Field(description="Доп. услуги")
    payment_cost: PaymentCost = Field(description="Сумма оплаты")
    involuntary: bool = Field(default=False, description="Признак добровольного обмена")

    lang: str = 'en'

    _method_name: str = 'svc_emd_refund_confirm'

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
            'cost': dict(self.payment_cost),
            "involuntary": self.involuntary,
            "request_params": request_params,
            "answer_params": answer_params
        }

        return request
