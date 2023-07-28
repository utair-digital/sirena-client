from pydantic import Field
from typing import List, Union
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.requests.common import PaymentDocument, PaymentCost


class ConfirmExchangeRequest(RequestModelABC):
    """
    Подтверждение обмена
    """
    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")
    cost: PaymentCost = Field(description="Цена")
    payment_documents: Union[List[PaymentDocument], PaymentDocument] = Field(description="Информация о форме оплаты")

    lang: str = 'en'

    _method_name: str = 'exchange_confirm'

    def build(self) -> dict:
        pay_docs = [self.payment_documents] if not isinstance(self.payment_documents, list) else self.payment_documents

        request = {
            'regnum': self.rloc,
            'surname': self.last_name,

            'cost': dict(self.cost),
            'paydoc': [doc.build() for doc in pay_docs],

            'answer_params': {
                'lang': self.lang,
            },
        }

        return request
