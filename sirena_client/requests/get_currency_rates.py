from pydantic import Field
from typing import Optional
from sirena_client.base.models.base_client_request import RequestModelABC


class GetCurrencyRates(RequestModelABC):

    currency_one: str = Field(description="Код валюты")
    currency_two: Optional[str] = Field(description="Код валюты", default="NUC")
    owner: Optional[str] = Field(description="Источник курса", default="IATA")
    lang: str = 'en'

    _method_name: str = 'get_currency_rates'

    def build(self) -> dict:
        request = {
            'curr1': self.currency_one,
            'curr2': self.currency_two,
            'owner': self.owner,
            "answer_params": {
                "lang": self.lang
            }
        }
        return request
