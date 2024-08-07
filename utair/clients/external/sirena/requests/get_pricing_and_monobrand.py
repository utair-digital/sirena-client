from datetime import date
from typing import Optional, List

from pydantic import Field

from utair.clients.external.sirena.requests.common import Passenger, RequestParams, AnswerParams
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.requests.add_ssr_to_order import SSRForAdd


class PricingRouteAndMonoBrandSegment(RequestModelABC):
    departure: str = Field(description="Код города или порта отправления")
    arrival: str = Field(description="Код города или порта прибытия")
    # по дэфолту название date, поэтому переименовал
    departure_date: date = Field(description="Дата вылета")
    company: Optional[str] = Field(description="Код маркетингового перевозчика", default=None)
    flight: Optional[str] = Field(description="Маркетинговый номер рейса", default=None)
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


class GetPricingRouteAndMonoBrand(RequestModelABC):
    """
    Поиск вариантов перевозки и оценка их стоимости
    """
    segments: List[PricingRouteAndMonoBrandSegment] = Field(description="Сегмент маршрута")
    passengers: List[Passenger] = Field(description="Данные пассажира(-ов)")
    ssrs: List[SSRForAdd] = Field(description="Данные SSR", default=None)

    request_params: Optional[RequestParams] = Field(description="Дополнительные параметры запроса",
                                                    default=None)
    answer_params: Optional[AnswerParams] = Field(description="Дополнительные параметры ответа",
                                                  default=None)

    lang: str = 'en'

    _method_name: str = 'pricing_route_and_mono_brand'

    def build(self) -> dict:
        request = {
            "segment": [s.build() for s in self.segments],
            "passenger": [p.build() for p in self.passengers],
            "request_params": self.request_params.build() if self.request_params else {},
            "answer_params": self.answer_params.build() if self.answer_params else {}
        }
        if self.ssrs:
            request.update(
                {
                    "special_services": {
                        "ssrs": {
                            "ssr": [s.build() for s in self.ssrs]
                        }
                    }
                }
            )

        return request
