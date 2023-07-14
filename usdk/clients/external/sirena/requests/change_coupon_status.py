from pydantic import Field
from ..base.models.base_client_request import RequestModelABC


class ChangeCouponStatusRequest(RequestModelABC):
    """
    Запрос используется для изменения статуса купона
    """

    doc_type: str = Field(description="Тип документа")
    doc_number: str = Field(description="Номер документа")
    coupon_number: str = Field(description="Номер купона")
    coupon_status: str = Field(description="Новый статус купона")

    lang: str = 'en'

    _method_name: str = 'change_edoc_stat'

    def build(self) -> dict:
        request_params = {}

        answer_params = {
            "lang": self.lang
        }

        request = {
            "doctype": self.doc_type,
            "docnum": self.doc_number,
            "coupon": self.coupon_number,
            "status": self.coupon_status,
            "request_params": request_params,
            "answer_params": answer_params,
        }

        return request
