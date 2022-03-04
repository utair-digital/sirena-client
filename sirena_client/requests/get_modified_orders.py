from pydantic import Field
from datetime import datetime
from sirena_client.base.models.base_client_request import RequestModelABC


class GetModifiedOrders(RequestModelABC):

    last_time: datetime = Field(description="Дата с которой нужно отобразить измененные заказы")

    lang: str = 'en'

    _method_name: str = 'modified_orders'

    def build(self) -> dict:
        return {
            "last_time": self.last_time.strftime('%H:%M %d.%m.%Y'),
            "answer_params": {
                "lang": self.lang
            }
        }
