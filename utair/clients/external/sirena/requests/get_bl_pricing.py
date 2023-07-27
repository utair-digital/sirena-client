from typing import Union
from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.requests.common import PaymentDocument, BLPricingPassenger


class GetBLPricing(RequestModelABC):
    """
    Получение оценки стоимости изменения перс. данных пассажира.
    """

    rloc: str = Field(description="Номер бронирования")
    last_name: str = Field(description="Фамилия пассажира")
    passenger: BLPricingPassenger = Field(description="Данные пассажира")
    payment_info: PaymentDocument = Field(description="Информация об оплате")

    version: Union[str, int] = "ignore"

    lang: str = 'en'

    _method_name: str = 'bl_pricing'

    def build(self) -> dict:
        request = {
            "regnum": {
                "#text": self.rloc,
                "@version": self.version,
            },
            "surname": self.last_name,
            "passenger": self.passenger.build(),
            "paydoc": self.payment_info.build(),
            "answer_params": {
                "lang": self.lang
            },
        }
        return request
