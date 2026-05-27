from datetime import date
from typing import List, Literal, Optional, Union

from pydantic import Field, model_validator

from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.requests.add_ssr_to_order import SSRForAdd
from utair.clients.external.sirena.requests.pricing_common import (
    PricingAcomp,
    PricingAnswerParams,
    PricingFlightFilter,
    PricingRequestParams,
)

__all__ = [
    "GetPricingRoute",
    "PricingRouteSegment",
    "PricingRoutePassenger",
    "PricingAcomp",
    "PricingFlightFilter",
    "PricingRequestParams",
    "PricingAnswerParams",
]


class PricingRouteSegment(RequestModelABC):
    """
    Сегмент маршрута для запроса pricing_route
    """

    departure: str = Field(description="Код города или порта отправления")
    arrival: str = Field(description="Код города или порта прибытия")
    # по дэфолту название date, поэтому переименовал
    departure_date: date = Field(description="Дата вылета")

    company: Optional[Union[str, List[str]]] = Field(
        description="Код(ы) маркетингового перевозчика",
        default=None,
    )
    flight: Optional[str] = Field(
        description="Маркетинговый номер рейса",
        default=None,
    )
    subclass: Optional[Union[str, List[str]]] = Field(
        description="Класс(ы) бронирования",
        default=None,
    )
    # по дэфолту название class, поэтому переименовал
    service_class: Optional[Union[str, List[str]]] = Field(
        description="Класс(ы) обслуживания (Э/Y, Б/C, П/F)",
        default=None,
    )
    cabin: Optional[Union[str, List[str]]] = Field(
        description="Кабина(ы) (PFJCWY)",
        default=None,
    )

    direct: Optional[bool] = Field(
        description="Признак вывода только прямых рейсов",
        default=True,
    )
    connections: Optional[str] = Field(
        description="Правило отображения стыковочных рейсов ('only' или код пункта стыковки)",
        default=None,
    )
    time_from: Optional[int] = Field(
        description="Самое раннее время вылета (включительно)",
        default=0,
    )
    time_till: Optional[int] = Field(
        description="Самое позднее время вылета (не включительно)",
        default=2400,
    )

    desire: Optional[PricingFlightFilter] = Field(
        description="Список рейсов, которые будут рассматриваться при оценке",
        default=None,
    )
    ignore: Optional[PricingFlightFilter] = Field(
        description="Список рейсов, исключаемых из рассмотрения",
        default=None,
    )

    segment_id: Optional[int] = Field(
        description="Идентификатор сегмента (атрибут @id). Учитываются только значения > 0.",
        default=None,
    )
    joint_id: Optional[int] = Field(
        description="Идентификатор сегмента стыковочного рейса (атрибут @joint_id). "
        "Учитываются только значения > 0.",
        default=None,
    )
    marriage_id: Optional[int] = Field(
        description="Идентификатор марьяжного сегмента (атрибут @marriage_id). "
        "Учитываются только значения > 0. Нельзя одновременно с joint_id.",
        default=None,
    )

    _nested: bool = True

    @model_validator(mode="after")
    def _check_connections_and_marriage(self) -> "PricingRouteSegment":
        if self.connections and self.direct:
            raise ValueError(
                "Параметр 'connections' допускается передавать только совместно с direct=False"
            )
        if (
            self.joint_id is not None
            and self.joint_id > 0
            and self.marriage_id is not None
            and self.marriage_id > 0
        ):
            raise ValueError(
                "Нельзя одновременно указывать ненулевые значения 'marriage_id' и 'joint_id'"
            )
        return self

    def build(self) -> dict:
        request: dict = {
            "departure": self.departure,
            "arrival": self.arrival,
            "date": self.departure_date.strftime("%d.%m.%y"),
            "company": self.company,
            "flight": self.flight,
            "subclass": self.subclass,
            "class": self.service_class,
            "cabin": self.cabin,
            "direct": self.direct,
            "connections": self.connections,
            "time_from": self.time_from,
            "time_till": self.time_till,
            "desire": self.desire.build() if self.desire else None,
            "ignore": self.ignore.build() if self.ignore else None,
        }
        if self.segment_id is not None and self.segment_id > 0:
            request["@id"] = self.segment_id
        if self.joint_id is not None and self.joint_id > 0:
            request["@joint_id"] = self.joint_id
        if self.marriage_id is not None and self.marriage_id > 0:
            request["@marriage_id"] = self.marriage_id
        return request


class PricingRoutePassenger(RequestModelABC):
    """
    Информация о пассажире для запроса pricing_route
    Атрибут @id не описан в таблице, но используется в примерах и в orig_id ответа.
    """

    code: str = Field(description="Код категории пассажира")
    age: Optional[int] = Field(
        description="Возраст пассажира (кол-во полных лет)",
        default=None,
    )
    sex: Optional[Literal["male", "female"]] = Field(
        description="Пол пассажира",
        default=None,
    )
    doc: Optional[str] = Field(description="Основной документ", default=None)
    doc2: Optional[str] = Field(description="Документ на льготу", default=None)
    citizenship: Optional[str] = Field(description="Гражданство", default=None)
    residence: Optional[str] = Field(description="Страна/город/округ/регион проживания", default=None)
    count: Optional[int] = Field(
        description="Количество пассажиров с такими параметрами",
        default=1,
    )
    n_seats: Optional[int] = Field(
        description="Количество мест, занимаемых пассажиром (для EXST)",
        default=None,
    )
    passenger_id: Optional[int] = Field(
        description="Идентификатор пассажира (атрибут @id), для связи с SSR pass_id",
        default=None,
    )

    _nested: bool = True

    def build(self) -> dict:
        request: dict = {
            "code": self.code,
            "age": self.age,
            "sex": self.sex,
            "doc": self.doc,
            "doc2": self.doc2,
            "citizenship": self.citizenship,
            "residence": self.residence,
            "count": self.count,
            "n_seats": self.n_seats,
        }
        if self.passenger_id is not None and self.passenger_id > 0:
            request["@id"] = self.passenger_id
        return request


class GetPricingRoute(RequestModelABC):
    """
    Поиск вариантов перевозки и оценка их стоимости (pricing_route)
    """

    segments: List[PricingRouteSegment] = Field(description="Сегменты маршрута")
    passengers: List[PricingRoutePassenger] = Field(description="Данные пассажира(-ов)")
    special_services: Optional[List[SSRForAdd]] = Field(
        description="SSR, добавляемые в запрос (специальные тарифы, accounting code, FQTV и т.п.)",
        default=None,
    )
    request_params: Optional[PricingRequestParams] = Field(
        description="Дополнительные параметры запроса",
        default=None,
    )
    answer_params: Optional[PricingAnswerParams] = Field(
        description="Дополнительные параметры ответа",
        default=None,
    )

    _method_name: str = "pricing_route"

    @model_validator(mode="after")
    def _check_limits(self) -> "GetPricingRoute":
        """
        Из документации Sirena:
        - Без указания номеров рейсов возможно передавать данные не более 4 сегментов;
        - При указании на каждом сегменте номеров рейсов возможно передавать данные не более 4 стыковочных рейсов;
        - Общее количество пассажиров не должно превышать девяти.
        """
        if self.segments:
            has_flight = [bool(s.flight) for s in self.segments]
            if not any(has_flight) and len(self.segments) > 4:
                raise ValueError(
                    "Без указания номеров рейсов возможно передавать не более 4 сегментов"
                )
            if all(has_flight) and len(self.segments) > 4:
                raise ValueError(
                    "При указании на каждом сегменте номеров рейсов возможно передавать "
                    "не более 4 стыковочных рейсов"
                )

        total_pax = sum((p.count or 1) for p in self.passengers)
        if total_pax > 9:
            raise ValueError("Общее количество пассажиров не должно превышать девяти")
        return self

    def build(self) -> dict:
        request: dict = {
            "segment": [s.build() for s in self.segments],
            "passenger": [p.build() for p in self.passengers],
            "request_params": self.request_params.build() if self.request_params else {},
            "answer_params": self.answer_params.build() if self.answer_params else {},
        }
        if self.special_services:
            request["special_services"] = {
                "ssrs": {"ssr": [s.build() for s in self.special_services]}
            }
        return request
