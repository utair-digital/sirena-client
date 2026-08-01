from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class AddRemarkRequest(RequestModelABC):
    """
    Запрос используется для добавления ремарок в заказ.
    """

    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")
    remark_type: str = Field(description="Тип ремарки")
    remark_text: str = Field(description="Текст ремарки")

    lang: str = 'en'

    _method_name: str = 'add_remark'

    def build(self) -> dict:
        request_params = {}

        answer_params = {
            "lang": self.lang
        }

        request = {
            "regnum": self.rloc,
            "surname": self.last_name,
            "type": remark_type,
            "remark": remark_text,
            "request_params": request_params,
            "answer_params": answer_params,
        }
        return request
