from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class GetETicket(RequestModelABC):

    ticket_number: str = Field(description="Номер билета")
    show_passenger: bool = Field(description="Отображать пассажира", default=True)

    lang: str = 'en'

    _method_name: str = 'eticket_display'

    # TODO Валидация билета/емд?
    # if ticket_number[:3] != "298":
    #     raise SirenaClaimError()

    def build(self) -> dict:
        request = {
            "ticket_number": self.ticket_number,
            "answer_params": {
                "show_passenger": self.show_passenger,
                "lang": self.lang
            }
        }
        return request
