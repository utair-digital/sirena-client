from datetime import date
from typing import Optional, Union, List
from pydantic import Field
from ..base.models.base_client_request import RequestModelABC


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
    exp_date: Optional[date] = Field(default=None)
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
            'exp_date': self.exp_date.strftime("%d.%m.%Y") if self.exp_date else None,
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
    age: Union[str, int] = Field(description="Возраст")
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


class ExchangePassenger(RequestModelABC):
    last_name: str = Field(description="Фамилия")
    first_name: str = Field(description="Имя")
    second_name: Optional[str] = Field(description="Отчество", default=None)

    @property
    def name(self) -> str:
        if self.second_name:
            return f'{self.first_name} {self.second_name}'

        return self.first_name

    def build(self) -> dict:
        request = {
            'lastname': self.last_name,
            'firstname': self.name
        }
        return request


class ExchangeSegment(RequestModelABC):
    airline: str = Field(description="Код маркетингового перевозчика")
    flight_number: str = Field(description="Маркетинговый номер рейса")
    flight_date: date = Field(description="Дата вылета")
    departure_code: str = Field(description="Код города или порта отправления")
    arrival_code: str = Field(description="Код города или порта прибытия")
    subclass: Optional[str] = Field(description="Класс бронирования", default=None)

    @property
    def formatted_flight_date(self) -> str:
        return self.flight_date.strftime('%d.%m.%Y')

    def build(self) -> dict:
        request = {
            'carrier': self.airline,
            'flight': self.flight_number,
            'date': self.formatted_flight_date,
            'departure': self.departure_code,
            'arrival': self.arrival_code,
            'subclass': self.subclass,
        }
        return request


class ExchangeSegments(RequestModelABC):
    original: List[ExchangeSegment]
    desired: List[ExchangeSegment]

    def build(self) -> dict:
        request = {
            'original': [s.build() for s in self.original],
            'desired': [s.build() for s in self.desired],
        }

        return request


class Passenger(RequestModelABC):
    """
    Информация о пассажире, используется в GetCalendar, GetPricingRoute
    """
    code: str = Field(description="Код категории пассажира")
    age: Optional[int] = Field(description="Возраст пассажира (кол-во полных лет)", default=None)
    sex: Optional[str] = Field(description="Пол пассажира", default=None)
    doc: Optional[str] = Field(description="Основной документ", default=None)
    doc2: Optional[str] = Field(description="Документ на льготу", default=None)
    citizenship: Optional[str] = Field(description="Гражданство", default=None)
    residence: Optional[str] = Field(description="Страна проживания", default=None)
    count: Optional[int] = Field(description="Количество пассажиров с такими параметрами", default=1)

    def build(self) -> dict:
        return {
            "code": self.code,
            "age": self.age,
            "sex": self.sex,
            "doc": self.doc,
            "doc2": self.doc2,
            "citizenship": self.citizenship,
            "residence": self.residence,
            "count": self.count,
        }


class RequestParams(RequestModelABC):
    """
    Параметры запроса, используется в GetPricingRoute, GetPricingMonoBrand
    """
    min_results: Optional[int] = Field(description="Минимальное желаемое количество разных оценок", default=None)
    max_results: Optional[int] = Field(description="Максимальное количество вариантов, возвращаемых в ответе",
                                       default=None)
    timeout: Optional[int] = Field(description="Таймаут выполнения запроса (секунды)", default=None)
    mix_scls: Optional[bool] = Field(description="Комбинировать подклассы на сегментах по маршруту перевозки",
                                     default=None)
    mix_ac: Optional[bool] = Field(description="Комбинировать рейсы разных перевозчиков по маршруту перевозки",
                                   default=None)
    comb_rules: Optional[str] = Field(description="Правила комбинирования рейсов авиакомпаний", default=None)
    fingering_order: Optional[str] = Field(description="Порядок перебора вариантов при оценке", default=None)
    price_child_aaa: Optional[bool] = Field(description="Провести тарификацию ребёнка по взрослому тарифу, если не "
                                                        "найдено скидок", default=None)
    asynchronous_fares: Optional[bool] = Field(description="Не применять тарифы с одновременным бронированием и "
                                                           "оформлением", default=None)
    show_tmb: Optional[bool] = Field(description="Готовить и показывать справку по норме провоза багажа",
                                     default=None)
    formpay: Optional[str] = Field(description="Форма оплаты для оценки", default=None)
    pt_baggage: Optional[bool] = Field(description="Показывать только 'багажные' тарифы", default=None)

    def build(self) -> dict:
        return {
            "min_results": self.min_results,
            "max_results": self.max_results,
            "timeout": self.timeout,
            "mix_scls": self.mix_scls,
            "mix_ac": self.mix_ac,
            "comb_rules": self.comb_rules,
            "fingering_order": self.fingering_order,
            "price_child_aaa": self.price_child_aaa,
            "asynchronous_fares": self.asynchronous_fares,
            "show_tmb": self.show_tmb,
            "formpay": self.formpay,
            "pt_baggage": self.pt_baggage,
            # et_if_possible, n_prices
        }


class AnswerParams(RequestModelABC):
    """
    Параметры ответа, используется в GetPricingRoute, GetPricingMonoBrand
    """
    show_available: Optional[bool] = Field(description="Добавлять в ответ информацию о наличии мест на подклассе",
                                           default=None)
    show_io_matching: Optional[bool] = Field(description="Добавлять в ответ информацию о соответствии сегментов "
                                                         "запроса сегментам ответа", default=None)
    show_flighttime: Optional[bool] = Field(description="Добавлять в ответ информацию о времени перелета и времени "
                                                        "следования по сегментам", default=None)
    show_varianttotal: Optional[bool] = Field(description="Добавлять в ответ информацию об общей стоимости перевозки "
                                                          "по варианту", default=None)
    show_baseclass: Optional[bool] = Field(description="Добавлять к каждому подклассу код его базового класса",
                                           default=None)
    show_reg_latin: Optional[bool] = Field(description="Указывать необходимость оформления билета на латинице",
                                           default=None)
    show_upt_rec: Optional[bool] = Field(description="Выдать детализацию УПТ", default=None)
    show_fareexpdate: Optional[bool] = Field(description="Указывать дату истечения срока действия тарифа", default=None)
    show_n_blanks: Optional[bool] = Field(description="Возвращать количество билетов, необходимых для оформления "
                                                      "перевозки", default=None)
    regroup: Optional[bool] = Field(description="Перегруппировка ответа", default=None)
    split_companies: Optional[bool] = Field(description="При перегруппировке ответа объединять в один вариант только "
                                                        "рейсы одной авиакомпании. Автоматически установит параметр "
                                                        "запроса mix_ac='false'", default=None)
    reference_style_codes: Optional[bool] = Field(description="Возвращать коды авиакомпаний по правилам, принятым в "
                                                              "справочных запросах (может вернуть латинский код а/к "
                                                              "вместо русского)", default=None)
    mark_cityport: Optional[bool] = Field(description="Добавлять в ответ признаки city или airport для пунктов",
                                          default=None)
    show_tml: Optional[bool] = Field(description="Добавлять в ответ информацию о ТЛ на оформление перевозки",
                                     default=None)
    show_brand_info: Optional[bool] = Field(description="Добавлять в ответ информацию о составе брендов", default=None)
    show_cat18: Optional[bool] = Field(description="Добавлять в ответ примечания из кат. 18 УПТ", default=None)
    lang: str = 'en'

    def build(self) -> dict:
        return {
            "lang": self.lang,
            "show_available": self.show_available,
            "show_io_matching": self.show_io_matching,
            "show_flighttime": self.show_flighttime,
            "show_varianttotal": self.show_varianttotal,
            "show_baseclass": self.show_baseclass,
            "show_reg_latin": self.show_reg_latin,
            "show_upt_rec": self.show_upt_rec,
            "show_fareexpdate": self.show_fareexpdate,
            "show_n_blanks": self.show_n_blanks,
            "regroup": self.regroup,
            "split_companies": self.split_companies,
            "reference_style_codes": self.reference_style_codes,
            "mark_cityport": self.mark_cityport,
            "show_tml": self.show_tml,
            "show_brand_info": self.show_brand_info,
            "show_cat18": self.show_cat18,
            # "return_date", "show_et", "show_regroup_io_matching", "show_trcantpr", "joint_type"
        }
