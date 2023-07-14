from datetime import date
from typing import Optional, List

from pydantic import Field

from .common import Passenger, RequestParams, AnswerParams
from ..base.models.base_client_request import RequestModelABC


class PricingMonoBrandSegment(RequestModelABC):
    departure: str = Field(description="Код города или порта отправления")
    arrival: str = Field(description="Код города или порта прибытия")
    # по дэфолту название date, поэтому переименовал
    departure_date: date = Field(description="Дата вылета")
    company: str = Field(description="Код маркетингового перевозчика")
    flight: str = Field(description="Маркетинговый номер рейса")
    subclass: Optional[str] = Field(description="Класс бронирования",
                                    default=None)
    # по дэфолту название class, поэтому переименовал
    service_class: Optional[str] = Field(description="Класс обслуживания",
                                         default=None)
    direct: Optional[bool] = Field(description="Признак вывода только прямых рейсов",
                                   default=True)
    connections: Optional[str] = Field(description="Правило отображения стыковочных рейсов",
                                       default=None)
    time_from: Optional[int] = Field(description="Самое раннее время вылета (включительно)",
                                     default=0)
    time_till: Optional[int] = Field(description="Самое позднее время вылета (не включительно)",
                                     default=2400)
    desire: Optional[str] = Field(description="Список рейсов, которые будут рассматриваться при оценке",
                                  default=None)
    ignore: Optional[str] = Field(description="Список рейсов, исключаемых из рассмотрения",
                                  default=None)

    def build(self) -> dict:
        return {
            "departure": self.departure,
            "arrival": self.arrival,
            "date": self.departure_date.strftime("%d.%m.%y"),
            "company": self.company,
            "flight": self.flight,
            "subclass": self.subclass,
            "class": self.service_class,
            "direct": self.direct,
            "connections": self.connections,
            "time_from": self.time_from,
            "time_till": self.time_till,
            "desire": self.desire,
            "ignore": self.ignore,
        }


class GetPricingMonoBrand(RequestModelABC):
    segments: List[PricingMonoBrandSegment] = Field(description="Сегмент маршрута")
    passengers: List[Passenger] = Field(description="Данные пассажира(-ов)")
    special_services: Optional[dict] = Field(description="Данные SSR",
                                             default={})
    request_params: Optional[RequestParams] = Field(description="Дополнительные параметры запроса",
                                                    default=None)
    answer_params: Optional[AnswerParams] = Field(description="Дополнительные параметры ответа",
                                                  default=None)

    lang: str = 'en'

    _method_name: str = 'pricing_mono_brand'

    def build(self) -> dict:
        request = {
            "segment": [s.build() for s in self.segments],
            "passenger": [p.build() for p in self.passengers],
            "special_services": self.special_services,
            "request_params": self.request_params.build() if self.request_params else {},
            "answer_params": self.answer_params.build() if self.answer_params else {}
        }
        return request
