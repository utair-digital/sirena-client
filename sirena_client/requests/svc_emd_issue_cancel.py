from pydantic import Field
from sirena_client.base.models.base_client_request import RequestModelABC


class SVCEmdIssueCancelRequest(RequestModelABC):
    """
    Отмена первой стадии оплаты услуг
    """

    rloc: str = Field(description="Номер PNR")
    version: int = Field(description="Версия брони", default="ignore")

    lang: str = 'en'

    _method_name: str = 'svc_emd_issue_cancel'

    def build(self) -> dict:
        request = {
            'regnum': {
                '#text': self.rloc,
                '@version': self.version
            },
        }
        return request
