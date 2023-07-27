from pydantic import Field
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.requests.common import PaymentCost, PaymentDocument


class SVCEmdIssueConfirm(RequestModelABC):
    """
    Оформление EMD на доп. услуги, второй шаг

    Подтверждение и оплата EMD на доп. услуги могут быть проведены только при условии, что PNR находится в состоянии
    ожидания, когда будет подтверждена оплата доп. услуг.
    При этом запрос просмотра состояния PNR выдает параметр <common_status> со значением being_paid_for.

    На вход запрос получает:

    номер и актуальную версию PNR;
    оплаченную стоимость — элемент <cost>;
    информацию о форме оплаты и платежном средстве — <paydoc>.
    Оплаченная стоимость должна совпадать со стоимостью, возвращенной запросом svc_emd_issue_query.

    В качестве результата запрос возвращает либо диагностическое сообщение об ошибке,
    либо ответ, аналогичный ответу на запрос pnr_status.
    """

    rloc: str = Field(description="Номер PNR")
    payment_document: PaymentDocument = Field(
        description="Способы оплаты. может быть объектом или списком объектов"
    )
    payment_cost: PaymentCost = Field(
        description="Сумма и валюта оплаты"
    )
    version: str = Field(description="Версия брони", default="ignore")

    lang: str = 'en'

    _method_name: str = 'svc_emd_issue_confirm'

    def build(self) -> dict:
        request = {
            "regnum": {
                "@version": self.version,
                "#text": self.rloc
            },
            "paydoc": self.payment_document.build(),
            "cost": self.payment_cost.build(),
            "answer_params": {
                "lang": self.lang
            }
        }
        return request
