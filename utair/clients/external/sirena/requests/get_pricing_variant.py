from datetime import date
from pydantic import Field
from typing import Optional, List
from utair.clients.external.sirena.base.models.base_client_request import (
    RequestModelABC,
)
from utair.clients.external.sirena.requests.add_ssr_to_order import SSRForAdd


class PricingVariantSegment(RequestModelABC):
    seg_id: str = Field(description="Ид сегмента")
    departure: str = Field(description="Код города или порта отправления")
    arrival: str = Field(description="Код города или порта прибытия")
    departure_date: date = Field(description="Дата вылета")
    company: str = Field(description="Код маркетингового перевозчика")
    flight: str = Field(description="Маркетинговый номер рейса")
    subclass: str = Field(description="Класс бронирования")
    joint_id: str = Field(description="ID соединения (для группировки сегментов)")

    def build(self) -> dict:
        return {
            "@id": self.seg_id,
            "departure": self.departure,
            "arrival": self.arrival,
            "date": self.departure_date.strftime("%d.%m.%y"),
            "company": self.company,
            "flight": self.flight,
            "subclass": self.subclass,
            "@joint_id": self.joint_id,
        }


class PricingVariantPassenger(RequestModelABC):
    pass_id: str = Field(description="Ид пассажира")
    code: str = Field(description="Код категории пассажира")
    age: Optional[int] = Field(
        description="Возраст пассажира (кол-во полных лет)", default=None
    )
    count: Optional[int] = Field(
        description="Количество пассажиров с такими параметрами", default=1
    )

    def build(self) -> dict:
        return {
            "@id": self.pass_id,
            "code": self.code,
            "age": self.age,
            "count": self.count,
        }


class PricingVariantSvc(RequestModelABC):
    rfisc: str = Field(description="Рфиск услуги")
    service_type: str = Field(description="Тип услуги")
    seat_characteristics: Optional[str] = Field(
        default="", description="Значимые характеристики для услуг места"
    )

    def build(self) -> dict:
        return {
            "@rfisc": self.rfisc,
            "@service_type": self.service_type,
            "@seat_characteristics": self.seat_characteristics,
        }


class PricingVariantBrand(RequestModelABC):
    seg_id: str = Field(description="Ид сегмента")
    code: str = Field(description="Код бренда")

    def build(self) -> dict:
        return {"@seg_id": self.seg_id, "#text": self.code}


class GetPricingVariant(RequestModelABC):
    """Оценка варианта перевозки с отображением доступных дополнительных услуг"""

    segments: List[PricingVariantSegment] = Field(description="Сегменты маршрута")
    brands: List[PricingVariantBrand] = Field(description="Бренды сегментов")
    passengers: List[PricingVariantPassenger] = Field(description="Данные пассажиров")
    svcs: list[PricingVariantSvc] = Field(
        description="Список услуг для оценки", default_factory=list
    )
    ssrs: List[SSRForAdd] = Field(description="Данные SSR", default_factory=list)

    show_svc: bool = Field(
        default=True, description="Добавлять в ответ информацию о доступных услугах"
    )
    show_available: bool = Field(default=True, description="Показать доступность мест")
    show_et: bool = Field(
        default=True, description="Показать информацию об электронном билете"
    )
    show_baseclass: bool = Field(default=True, description="Показать базовый класс")
    regroup: bool = Field(default=True, description="Перегруппировать варианты")

    lang: str = "en"

    _method_name: str = "pricing_variant"

    def build(self) -> dict:
        request_params = {"brand": [item.build() for item in self.brands]}
        answer_params = {
            "show_svc": self.show_svc,
            "show_available": self.show_available,
            "show_et": self.show_et,
            "show_baseclass": self.show_baseclass,
            "regroup": self.regroup,
            "lang": self.lang,
            "svcs": {"svc": [item.build() for item in self.svcs]},
        }

        request = {
            "segment": [s.build() for s in self.segments],
            "passenger": [p.build() for p in self.passengers],
            "request_params": request_params,
            "answer_params": answer_params,
        }

        if self.ssrs:
            request.update(
                {"special_services": {"ssrs": {"ssr": [s.build() for s in self.ssrs]}}}
            )

        return request
