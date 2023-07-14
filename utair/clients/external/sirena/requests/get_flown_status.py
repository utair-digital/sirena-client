from pydantic import Field
from ..base.models.base_client_request import RequestModelABC


class GetFlownStatusRequest(RequestModelABC):
    """
    Запрос используется для получения статуса электронных билетов, выпущенных в PNR.
    """

    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")

    lang: str = 'en'

    _method_name: str = 'view_flown_status'

    def build(self) -> dict:
        request_params = {}

        answer_params = {
            "lang": self.lang
        }

        request = {
            "regnum": self.rloc,
            "surname": self.last_name,
            "request_params": request_params,
            "answer_params": answer_params,
        }
        return request
