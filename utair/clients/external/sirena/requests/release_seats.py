from typing import List, Optional
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class PassengersForReleaseSeats(RequestModelABC):
    """
    Модель пассажиров для сдачи/возврата мест
    """
    first_name: str = Field(description="Имя + Отчество пассажира")
    last_name: str = Field(description="Фамилия пассажира")

    _nested: bool = True

    def build(self) -> dict:
        return {
            'name': self.first_name,
            'surname': self.last_name
        }


class SegmentsForReleaseSeats(RequestModelABC):
    """
    Модель сегментов для сдачи/возврата мест
    """
    company: str = Field(description="Код авиакомпании")
    flight: str = Field(description="Номер рейса")
    departure: str = Field(description="Код пункта отправления")
    arrival: str = Field(description="Код пункта назначения")
    departure_date: str = Field(description="Дата вылета")

    _nested: bool = True

    def build(self) -> dict:
        return {
            'company': self.company,
            'flight': self.flight,
            'departure': self.departure,
            'arrival': self.arrival,
            'date': self.departure_date,
        }


class ReleaseSeatsRequest(RequestModelABC):
    """
    Запрос используется для возврата (части) мест PNR после оформления билетов (без возврата билетов).
    """

    rloc: str = Field(description="Номер бронирования")
    surname: str = Field(description="Фамилия пассажира")
    segments: Optional[List[SegmentsForReleaseSeats]] = Field(
        description="Список сегментов для сдачи", default_factory=list
    )
    passenger: List[PassengersForReleaseSeats] = Field(description="Список пассажиров для сдачи мест")

    lang: str = 'en'

    _method_name: str = 'release_seats'

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
        if self.segments:
            request["segment"] = [p.build() for p in self.segments]

        return request
