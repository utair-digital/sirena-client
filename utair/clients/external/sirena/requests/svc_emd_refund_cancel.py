from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import (
    RequestModelABC,
)


class CancelRefundServicesRequest(RequestModelABC):
    """
    Прерывание операции возврата оформленных услуг.

    Запрос может использоваться для отказа от возврата услуг после подачи запроса svc_emd_refund_query
    до истечения времени, отведенного на подтверждение операции.
    При обработке запроса PNR разблокируется.
    """

    rloc: str = Field(description="Номер PNR")
    version: str = Field(description="Версия брони", default="ignore")

    lang: str = "en"

    _method_name: str = "svc_emd_refund_cancel"

    def build(self) -> dict:
        request = {
            "regnum": {"#text": self.rloc, "@version": self.version},
        }
        return request
