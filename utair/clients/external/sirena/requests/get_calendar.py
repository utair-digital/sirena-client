from datetime import date
from typing import Optional, List

from pydantic import Field, root_validator

from utair.clients.external.sirena.requests.common import Passenger
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class GetCalendarSegment(RequestModelABC):
    departure: str = Field(description="Код города или порта отправления")
    arrival: str = Field(description="Код города или порта прибытия")
    # по дэфолту название date, поэтому переименовал
    departure_date: date = Field(description="Дата вылета")
    ndays: Optional[int] = Field(description="Глубина периода для поиска даты вылета",
                                 default=0)
    company: Optional[str] = Field(description="Код авиакомпании",
                                   default=None)
    flight: Optional[str] = Field(description="Номер рейса",
                                  default=None)
    subclass: Optional[str] = Field(description="Класс бронирования",
                                    default=None)
    # по дэфолту название class, поэтому переименовал
    service_class: Optional[str] = Field(description="Класс обслуживания",
                                         default=None)
    time_from: Optional[int] = Field(description="Самое раннее время вылета",
                                     default=None)
    time_till: Optional[int] = Field(description="Самое позднее время вылета",
                                     default=None)

    @root_validator
    def check_subclass_or_class(cls, values):
        if values.get("subclass") or values.get("service_class"):
            return values
        raise ValueError("Одно из значений является обязательным: 'subclass', 'service_class'")

    def build(self) -> dict:
        return {
            "departure": self.departure,
            "arrival": self.arrival,
            "date": self.departure_date.strftime("%d.%m.%y"),
            "ndays": self.ndays,
            "company": self.company,
            "flight": self.flight,
            "subclass": self.subclass,
            "class": self.service_class,
            "time_from": self.time_from,
            "time_till": self.time_till,
        }


class GetCalendar(RequestModelABC):
    segments: List[GetCalendarSegment] = Field(description="Сегмент маршрута")
    passenger: Optional[Passenger] = Field(description="Данные пассажира")

    lang: str = 'en'

    _method_name: str = 'calendar'

    def build(self) -> dict:
        request = {
            "segment": [s.build() for s in self.segments],
            "passenger": self.passenger.build()
        }
        return request
