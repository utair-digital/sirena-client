from pydantic import Field
from ..base.models.base_client_request import RequestModelABC


class CancelExchangeRequest(RequestModelABC):
    """
    Отмена возврата
    """
    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")

    lang: str = 'en'

    _method_name: str = 'exchange_cancel'

    def build(self) -> dict:
        request = {
            'regnum': self.rloc,
            'surname': self.last_name,

            'answer_params': {
                'lang': self.lang,
            },
        }

        return request
