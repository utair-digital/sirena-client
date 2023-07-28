from typing import List
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class PassengerForAddFFInfo(RequestModelABC):
    """
    Объект пассажира для добавления карты лояльности
    """
    passenger_id: str = Field(..., description="Идентификатор пассажира")
    loyalty_card: str = Field(..., description="Номер карточки, идентифицирующей клиента")
    segments: List[str] = Field(default_factory=list, description="Идентификаторы сегментов")

    def build(self) -> dict:
        return {
            '@id': 'passenger_id',              # FIXME
            'freq_flier_id': 'loyalty_card',    # FIXME
            'segment': [
                {'@id': s} for s in self.segments
            ]
        }


class AddFFInfoRequest(RequestModelABC):
    """
    Добавление ремарки о часто летающем пассажире
    Запрос используется для внесения в заказ информации о номере карточки,
    идентифицирующей пассажира в системе поощрения часто летающих пассажиров.
    """

    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")
    passengers: List[PassengerForAddFFInfo] = Field(
        description="Информация о карточке, идентифицирующей часто летающего пассажира, "
                    "и сегментах, на которых должна действовать данная карточка."
    )

    lang: str = 'en'

    _method_name: str = 'add_ff_info'

    def build(self) -> dict:
        request = {
            "regnum": self.rloc,
            "surname": self.last_name,
            "passenger": [p.build() for p in self.passengers]
        }
        return request
