from typing import List, Optional
from pydantic import Field
from ..base.models.base_client_request import RequestModelABC


class SsrUnitForAdd(RequestModelABC):
    first_name: str = Field(description="Имя")
    last_name: str = Field(description="Фамилия")
    company: Optional[str] = Field(description="Компания", default=None)
    flight: Optional[str] = Field(description="Рейс", default=None)
    departure: Optional[str] = Field(description="Пункт отправления", default=None)
    arrival: Optional[str] = Field(description="Пункт прибытия", default=None)
    departure_date: Optional[str] = Field(description="Дата вылета", default=None)

    _nested: bool = True

    def build(self) -> dict:
        return {
            'name': self.first_name,
            'surname': self.last_name,
            'company': self.company,
            'flight': self.flight,
            'departure': self.departure,
            'arrival': self.arrival,
            'date': self.departure_date.strftime("%d.%m.%y"),
        }


class SSRForAdd(RequestModelABC):
    """
    Объект услуги для добавления в методе svc_add
    """
    segment_id: Optional[str] = Field(description="Идентификатор сегмента", default=None)
    passenger_id: Optional[str] = Field(description="Идентификатор пассажира", default=None)
    text: Optional[str] = Field(
        None,
        description="текст SSR — text, обязателен при указании SSR, требующих ввод свободного текста."
    )
    name: Optional[str] = Field(
        default=None,
        description="Наименование услуги — name, необязательный параметр;"
    )
    ssr_type: str = Field(description="Тип услуги")
    units: List[SsrUnitForAdd] = Field(default_factory=list),

    _nested: bool = True

    def build(self) -> dict:
        return {
            '@seg_id': 'segment_id',
            '@pass_id': 'passenger_id',
            '@text': 'text',
            '@type': 'type',
            'unit': [u.build() for u in self.units]
        }


class AddSSRRequest(RequestModelABC):
    """
    Добавление в PNR запроса на спецобслуживание (add_ssr)
    Запрос используется для добавления в заказ информации
    о запросах на спецобслуживание (SSR).
    """

    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")
    version: int = Field(description="Версия PNR")
    ssrs: List[SSRForAdd] = Field(description="Объекты услуг для добавления")

    lang: str = 'en'

    _method_name: str = 'add_ssr'

    def build(self) -> dict:
        request_params = {}

        answer_params = {
            "lang": self.lang
        }

        request = {
            "regnum": self.rloc,
            "surname": self.last_name,
            "ssr": [s.build() for s in self.ssrs],
            "request_params": request_params,
            "answer_params": answer_params,
        }
        return request
