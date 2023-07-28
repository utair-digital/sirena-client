from pydantic import Field
from typing import List, Union
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.requests.common import PaymentDocument


class SVCEmdIssueQuery(RequestModelABC):
    """
    Оформление EMD на доп. услуги, первый шаг:

    Оформлять доп. услуги можно только после оформления авиабилетов на соответствующих услугам пассажиро-сегментах.
    Услуги и ассоциированные с ними SSR к моменту начала оформления должны быть подтверждены,
    для оформления EMD требуется наличие оценки (блока <price> с соответствующим svc-id).

    На вход запрос получает:

    номер и актуальную версию PNR;
    список оформляемых доп. услуг — набор элементов <svc>;
    информацию о форме оплаты — <paydoc>.
    Каждый элемент <svc> должен содержать атрибут id с уникальным идентификатором оформляемой доп. услуги.

    Все оформляемые одним запросом доп. услуги должны иметь один и тот же тип (service_type).
    Ответ содержит информацию о сумме к оплате и времени, в течение которого оплата должна быть подтверждена.
    В течение указанного времени PNR блокируется от внесения изменений.
    """

    rloc: str = Field(description="Номер PNR")
    service_ids: List[int] = Field(description="Список оформляемых доп. услуг — набор элементов")
    payment_document: Union[PaymentDocument, List[PaymentDocument]] = Field(
        description="Способы оплаты. может быть объектом или списком объектов"
    )
    version: str = Field(description="Версия брони", default="ignore")

    lang: str = 'en'

    _method_name: str = 'svc_emd_issue_query'

    def build(self) -> dict:
        pay_docs = self.payment_document if isinstance(self.payment_document, list) else [self.payment_document]
        request = {
            "regnum": {
                "@version": self.version,
                "#text": self.rloc
            },
            "svc": [{'@id': i} for i in self.service_ids],
            "paydoc": [doc.build() for doc in pay_docs],
            "answer_params": {
                "lang": self.lang
            }
        }
        return request
