from pydantic import Field
from typing import Optional, Union
from sirena_client.base.models.base_client_request import RequestModelABC


class PaymentCost(RequestModelABC):
    """
    Цена
    """
    currency: str = Field(description="Валюта")
    amount: float = Field(description="Сумма")

    def build(self) -> dict:
        return {
            '@curr': self.currency,
            '#text': self.amount
        }


class PaymentDocument(RequestModelABC):
    """
    Информация о форме оплаты
    """
    form_pay: Optional[str] = Field(default=None)
    payment_type: Optional[str] = Field(default=None)
    payment_number: Optional[str] = Field(default=None)
    exp_date: Optional[str] = Field(default=None)
    holder: Optional[str] = Field(default=None)
    auth_code: Optional[str] = Field(default=None)
    rrn: Optional[str] = Field(default=None)
    pan_id: Optional[str] = Field(default=None)
    amount: Optional[str] = Field(default=None)
    cost: Optional[PaymentCost] = Field(default=None)

    def build(self) -> dict:
        return {
            'formpay': self.form_pay,
            'type': self.payment_type,
            'num': self.payment_number,
            'exp_date': self.exp_date,
            'holder': self.holder,
            'cost': self.cost.build() if self.cost else None,
            'auth_code': self.auth_code,
            'rrn': self.rrn,
            'pan_id': self.pan_id,
            'summ': self.amount
        }


class BLPricingPassenger(RequestModelABC):

    pass_id: str = Field(description="Идентификатор пассажира")
    last_name: str = Field(description="Фамилия")
    first_name: str = Field(description="Имя")
    age: Union[str, int] = Field(description="Возвраст")
    category: str = Field(description="Категория")
    nationality: str = Field(description="Национальность")
    doccode: str = Field(description="Тип документа")
    doc: str = Field(description="Номер документа")
    sex: str = Field(description="Пол")
    pspexpire: str = Field(description="Дата до которой действителен документ")

    def build(self) -> dict:
        request = {
            "@pass_id": self.pass_id,
            "lastname": self.last_name,
            "firstname": self.first_name,
            "age": self.age,
            "category": self.category,
            "nationality": self.nationality,
            "doccode": self.doccode,
            "doc": self.doc,
            "sex": self.sex,
            "pspexpire": self.pspexpire
        }
        return request
