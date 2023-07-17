from pydantic import Field
from typing import List, Union
from ..base.models.base_client_request import RequestModelABC
from common import PaymentDocument, ExchangePassenger, ExchangeSegments


class ExchangePricingRequest(RequestModelABC):
    """
    Поиск вариантов перевозки и оценка их стоимости
    """
    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия пассажира")
    payment_documents: Union[List[PaymentDocument], PaymentDocument] = Field(description="Форма оплаты для АПШ")
    passengers: List[ExchangePassenger] = Field(description="Список пассажиров для обмена")
    segments: Union[List[ExchangeSegments], ExchangeSegments] = Field(description="Список пассажиров для обмена")
    involuntary: bool = Field(default=False, description="Признак добровольного обмена")

    lang: str = 'en'

    _method_name: str = 'exchange_pricing'

    def build(self) -> dict:
        pay_docs = [self.payment_documents] if not isinstance(self.payment_documents, list) else self.payment_documents
        segments = [self.segments] if not isinstance(self.segments, list) else self.segments

        request = {
            'regnum': self.rloc,
            'surname': self.last_name,

            'involuntary': self.involuntary,
            'paydoc': [doc.build() for doc in pay_docs],

            'passengers': {
                'passenger': [p.build() for p in self.passengers]
            },

            'segments': {
                'segment': [s.build() for s in segments]
            },

            'answer_params': {
                'lang': self.lang,
            }
        }

        return request
