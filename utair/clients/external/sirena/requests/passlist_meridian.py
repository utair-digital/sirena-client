from datetime import date

from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import (
    RequestModelABC,
)


class PasslistMeridianRequest(RequestModelABC):
    """Запрос списка пассажиров указанного рейса"""

    company: str = Field(description="Код авиакомпании")
    flight_number: str = Field(description="Номер рейса")
    flight_date: date = Field(description="Дата вылета рейса")

    _method_name: str = "passlist_meridian"

    def build(self) -> dict:
        request = {
            "company": self.company,
            "flight": self.flight_number,
            "date": self.flight_date.strftime("%d.%m.%Y"),
        }
        return request
