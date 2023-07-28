from pydantic import Field
from typing import Optional
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class GetItineraryReceipt(RequestModelABC):

    rloc: str = Field(description="Номер бронирования")
    last_name: str = Field(description="Фамилия пассажира")
    version: Optional[str] = Field(description="Версия брони", default=None)

    lang: str = 'en'

    _method_name: str = 'get_itin_receipts'

    def build(self) -> dict:
        request = {
            'regnum': {
                '#text': self.rloc,
                '@version': self.version
            },
            'surname': self.last_name
        }
        return request
