from typing import List
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class PassengersForDivideOrder(RequestModelABC):
    """
    Модель отделяемого пассажира(ов)
    """
    first_name: str = Field(description="Имя + Отчество пассажира")
    last_name: str = Field(description="Фамилия пассажира")

    _nested: bool = True

    def build(self) -> dict:
        return {
            'name': self.first_name,
            'surname': self.last_name
        }


class DivideOrderRequest(RequestModelABC):
    """
    Запрос используется для отделения части пассажиров из PNR
    при осуществлении операций возврата/отмены части выпущенных билетов.
    """

    rloc: str = Field(description="Номер бронирования")
    surname: str = Field(description="Фамилия пассажира")
    passenger: List[PassengersForDivideOrder] = Field(description="Список пассажиров для разделения заказа")

    lang: str = 'en'

    _method_name: str = 'divide_order'

    def build(self) -> dict:
        request_params = {}

        answer_params = {
            "lang": self.lang
        }

        request = {
            "regnum": self.rloc,
            "surname": self.surname,
            "passenger": [p.build() for p in self.passenger],
            "request_params": request_params,
            "answer_params": answer_params,
        }

        return request
