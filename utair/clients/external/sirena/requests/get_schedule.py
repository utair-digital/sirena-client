from typing import Optional, Union
from datetime import date
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class GetSchedule(RequestModelABC):

    departure: Optional[str] = Field(default=None, description="Код города или порта отправления")
    arrival: Optional[str] = Field(default=None, description="Код города или порта прибытия")
    company: Optional[str] = Field(default=None, description="Код авиакомпании")
    date_from: Optional[date] = Field(default=None, description="Дата вылета или дата начала периода")
    date_to: Optional[date] = Field(default=None, description="Дата окончания периода")
    time_from: Optional[str] = Field(default=None, description="Минимальное время вылета (время в формате HH24MI)")
    time_till: Optional[str] = Field(default=None, description="Максимальное время вылета (время в формате HH24MI)")
    direct: Optional[bool] = Field(default=None, description="Признак вывода только прямых рейсов")

    only_m2_joints: Optional[bool] = Field(
        default=False, description="Выбираются только стыковки, созданные по договорам М2"
    )

    show_flighttime: bool = Field(default=False, description="Получение информации о длительности перелета")
    full_date: bool = Field(default=True, description="Вывод дат в формате ДД.ММ.ГГГГ")
    mark_cityport: bool = Field(default=False, description="Вывод признака порт/город в данных о пунктах перевозки")
    show_et: bool = Field(default=False, description="Вывод признака возможности оформления ЭБ на рейсе")

    lang: str = "en"

    _method_name: str = "schedule"

    def format_date(self, dt: Union[date, None]) -> Union[str, None]:
        return dt.strftime("%d.%m.%Y") if dt else None

    def build(self) -> dict:
        request_params = {
            "only_m2_joints": self.only_m2_joints,
        }
        answer_params = {
            "show_flighttime": self.show_flighttime,
            "full_date": self.full_date,
            "mark_cityport": self.mark_cityport,
            "show_et": self.show_et,
            "lang": self.lang,
        }

        request = {
            "departure": self.departure,
            "arrival": self.arrival,
            "company": self.company,
            "date": self.format_date(self.date_from),
            "date2": self.format_date(self.date_to),
            "time_from": self.time_from,
            "time_till": self.time_till,
            "request_params": request_params,
            "answer_params": answer_params
        }

        if self.direct is not None:
            request["direct"] = self.direct

        return request
