from pydantic import Field
from typing import Optional, Union
from datetime import date
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class AvailabilityRequest(RequestModelABC):
    """
    Запрос используется для получения информации о наличии мест на направлении.
    """

    departure: str = Field(description="Код города или порта отправления")
    arrival: str = Field(description="Код города или порта прибытия")
    departure_date: Optional[date] = Field(default=None, description="Дата вылета")
    company: Optional[str] = Field(default=None, description="Код авиакомпании")
    flight: Optional[str] = Field(default=None, description="Номер рейса")
    baseclass: Optional[str] = Field(default=None, description="Класс обслуживания")
    subclass: Optional[str] = Field(default=None, description="Класс бронирования")
    direct: Optional[bool] = Field(default=None, description="Признак вывода только прямых рейсов")
    connections: Optional[str] = Field(default=None, description="Правило отображения стыковочных рейсов")
    time_from: Optional[int] = Field(default=None, description="Минимальное время вылета")
    time_till: Optional[int] = Field(default=None, description="Максимальное время вылета")

    joint_type: str = Field(default='jtAll', description="Способ выбора стыковок")
    check_tch_restrictions: Optional[bool] = Field(default=False, description="Признак обязательного учета ограничений на продажу в сеансе ТКП")
    use_dag: Optional[bool] = Field(default=False, description="Признак обязательного учета ограничений на продажу по картотекам ДАР/ДАГ")
    use_iak: Optional[bool] = Field(default=False, description="Признак обязательного учета ограничений на продажу по картотеке ИАК")
    use_a02: Optional[bool] = Field(default=False, description="Признак необходимости использования таблицы А02 для определения класса обслуживания")

    show_flighttime: Optional[bool] = Field(default=None, description="Получение информации о времени перелета")
    show_baseclass: Optional[bool] = Field(default=None, description="Выводить базовый класс для каждого подкласса в ответе")
    return_date: Optional[bool] = Field(default=None, description="Добавить в атрибуты ответа дату, на которую выдается наличие мест")
    mark_cityport: Optional[bool] = Field(default=None, description="Добавить в тэги пунктов ответного сообщения признаки city или airport")
    show_et: Optional[bool] = Field(default=None, description="Добавить в ответ признак доступности оформления ЭБ на рейсе")

    lang: str = 'en'
    _method_name: str = 'availability'

    def format_date(self, dt: Union[date, None]) -> Union[str, None]:
        return dt.strftime("%d.%m.%Y") if dt else None

    def build(self) -> dict:
        request_params = {
            'joint_type': self.joint_type,
            'check_tch_restrictions': self.check_tch_restrictions,
            'use_dag': self.use_dag,
            'use_iak': self.use_iak,
            'use_a02': self.use_a02,
        }

        answer_params = {
            "show_flighttime": self.show_flighttime,
            "show_baseclass": self.show_baseclass,
            "return_date": self.format_date(self.return_date),
            "mark_cityport": self.mark_cityport,
            "show_et": self.show_et,
        }

        request = {
            "departure": self.departure,
            "arrival": self.arrival,
            "date": self.format_date(self.departure_date),
            "company": self.company,
            "flight": self.flight,
            "baseclass": self.baseclass,
            "subclass": self.subclass,
            "direct": self.direct,
            "connections": self.connections,
            "time_from": self.time_from,
            "time_till": self.time_till,
            "request_params": request_params,
            "answer_params": answer_params,
        }

        if self.direct is not None:
            request["direct"] = self.direct

        return request
