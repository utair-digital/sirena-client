from pydantic import Field
from typing import Optional
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class GetOrderSvc(RequestModelABC):
    rfisc: str = Field(description="Рфиск услуги")
    service_type: str = Field(description="Тип услуги")
    seat_characteristics: Optional[str] = Field(default="", description="Значимые характеристики для услуг места")

    def build(self) -> dict:
        return {
            "@rfisc": self.rfisc,
            "@service_type": self.service_type,
            "@seat_characteristics": self.seat_characteristics
        }


class GetOrder(RequestModelABC):

    rloc: str = Field(description="Номер PNR")
    last_name: str = Field(description="Фамилия любого из пассажиров")

    version: Optional[int] = Field(description="Версия брони", default=0)
    tick_ser: Optional[str] = Field(description="Серия бланков для оценки перевозки", default=None)
    no_pricing: bool = Field(default=False, description="Не возвращать данные по оценке")
    prev_pricing_params: bool = Field(
        default=False, description="Тарифицировать, используя форму оплаты и тип билета предыдущей оценки"
    )
    form_pay: Optional[str] = Field(default=None, description="Форма оплаты для оценки PNR")
    tick_info: bool = Field(default=False, description="Добавлять в ответ информацию о статусе билетов")
    show_tickinfo_agency: bool = Field(
        default=False, description="Добавлять в информацию о статусе билетов код оформившего билеты агентства"
    )
    show_actions: bool = Field(
        default=False, description="Добавлять в ответ информацию о доступных операциях с заказом"
    )
    add_common_status: bool = Field(
        default=False, description="Добавлять в ответ информацию о 'максимальном' статусе сегментов"
    )
    show_upt_rec: bool = Field(
        default=False, description="Добавлять в информацию о тарификации PNR данные для получения текстов УПТ"
    )
    add_remarks: bool = Field(
        default=False, description="Добавлять в ответ информацию о ремарках в PNR"
    )
    add_ssr: bool = Field(
        default=False, description="Добавлять в ответ информацию об SSR в PNR"
    )
    add_pay_code: bool = Field(
        default=False, description="Добавлять в ответ код оплаты для оплаты в системах приема платежей"
    )
    show_ersp: bool = Field(
        default=False, description="Добавлять в ответ информацию о ERSP-коде, с которым сделан заказ"
    )
    show_insurance_info: bool = Field(
        default=False, description="Добавлять в ответ информацию о страховках в PNR"
    )
    show_zh: bool = Field(
        default=False, description="Добавлять в ответ информацию о сегментах Аэроэкспресс в PNR"
    )
    add_remote_recloc: bool = Field(
        default=False, description="Добавлять в данные сегментов PNR информацию о номерах инвенторных PNR"
    )
    show_comission: bool = Field(
        default=False, description="Добавлять в ответ информацию о величине агентского вознаграждения"
    )
    show_bag_norm: bool = Field(
        default=False, description="Добавлять в ответ информацию о норме бесплатного провоза багажа"
    )
    show_svc: bool = Field(
        default=False, description="Добавлять в ответ информацию о доступных услугах"
    )
    show_originator: bool = Field(
        default=False, description="Добавлять в ответ информацию о создателе"
    )
    regroup: bool = Field(
        default=False, description="Uknown"
    )
    seat_map_v2: bool = Field(default=False, description="Unknown")

    svcs: list[GetOrderSvc] = Field(default=[], description="Сервисы")

    lang: str = 'en'

    _method_name: str = 'order'

    def build(self) -> dict:
        request_params = {
            'tick_ser': self.tick_ser,
            'no_pricing': self.no_pricing,
            'prev_pricing_params': self.prev_pricing_params,
            'formpay': self.form_pay
        }
        answer_params = {
            'tickinfo': self.tick_info,
            'show_tickinfo_agency': self.show_tickinfo_agency,
            'show_actions': self.show_actions,
            'add_common_status': self.add_common_status,
            'show_upt_rec': self.show_upt_rec,
            'add_remarks': self.add_remarks,
            'add_ssr': self.add_ssr,
            'add_paycode': self.add_pay_code,
            'show_ersp': self.show_ersp,
            'show_insurance_info': self.show_insurance_info,
            'show_zh': self.show_zh,
            'add_remote_recloc': self.add_remote_recloc,
            'show_comission': self.show_comission,
            'show_bag_norm': self.show_bag_norm,
            'show_svc': self.show_svc,
            'show_originator': self.show_originator,
            'regroup': self.regroup,
            'seat_map_v2': self.seat_map_v2,
            'lang': self.lang,
            'svcs': {"svc": [item.build() for item in self.svcs]}
        }

        request = {
            'regnum': {
                '#text': self.rloc,
                '@version': self.version
            },
            'surname': self.last_name,
            'request_params': request_params,
            'answer_params': answer_params
        }
        return request
