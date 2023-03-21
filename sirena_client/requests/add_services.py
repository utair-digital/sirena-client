from pydantic import Field
from typing import List, Optional
from sirena_client.base.models.base_client_request import RequestModelABC


class ServiceForAdd(RequestModelABC):
    """
    Объект услуги для добавления в методе svc_add
    """
    passenger_id: int = Field(description="Идентификатор пассажира")
    segment_id: int = Field(description="Идентификатор сегмента")
    rfisc: str = Field(description="Подкод услуги")
    emd: str = Field(description="тип EMD — emd, обязательный параметр, A — для EMD-A, S — для EMD-S;")
    service_type: str = Field(description="Тип услуги")
    qtty: int = Field(description="Кол-во услуг")
    ssr: str = Field(
        None,
        description="код SSR — ssr, обязателен при бронировании услуг, требующих SSR;"
    )
    rfic: Optional[str] = Field(
        default=None,
        description="Код услуги — rfic, обязателен при бронировании нестандартных (carrier-specific) услуг;"
    )
    text: str = Field(
        None,
        description="текст SSR — text, обязателен при указании SSR, требующих ввод свободного текста."
    )
    name: Optional[str] = Field(
        default=None,
        description="Наименование услуги — name, необязательный параметр;"
    )
    # TODO Не понятно что это, в доках нет: https://wiki.sirena-travel.ru/xmlgate:16ancillary_services:04svc_add
    # seat_type: str = None,

    _nested: bool = True

    def build(self) -> dict:
        return {
            '@pass_id': self.passenger_id,
            '@seg_id': self.segment_id,
            '@rfisc': self.rfisc,
            '@emd': self.emd,
            '@service_type': self.service_type,
            '@name': self.name,
            '@rfic': self.rfic,
            '@qtty': self.qtty,
            '@ssr': self.ssr,
            '@text': self.text,
        }


class AddServicesRequest(RequestModelABC):
    """
    Добавление доп. услуги в PNR
    Дополнительные услуги могут быть добавлены как в PNR с оформленными билетами,
    так и в еще не оплаченный заказ.
    """

    rloc: str = Field(description="Номер PNR")
    version: int = Field(description="Версия PNR")
    services: List[ServiceForAdd] = Field(description="Объекты услуг для добавления")

    # TODO надо проверить возвращается ли simple ответ, если переданны show_svc и прочии с ними
    simple: bool = Field(
        False,
        description="Если требуется подавать подряд несколько запросов на добавление доп. "
                    "услуг в PNR, то обработку запросов можно ускорить, "
                    "указав системе требование не возвращать информацию о PNR в ответ "
                    "(и, соответственно, не проводить полную тарификацию PNR и доп. услуг)."
                    "Для этого в секцию <answer_params> вносится параметр <simple>true<simple>,"
                    "и при этом ответ на запрос будет состоять из элемента <ok> без содержимого."
                    "Добавив все нужные услуги, необходимо подать запрос <order> "
                    "для получения и проверки их статусов."
    )
    show_svc: bool = Field(
        default=True, description="Добавлять в ответ информацию о доступных услугах"
    )
    show_insurance_info: bool = Field(
        default=True, description="Добавлять в ответ информацию о страховках в PNR"
    )
    add_ssr: bool = Field(
        default=True, description="Добавлять в ответ информацию об SSR в PNR"
    )
    tick_info: bool = Field(
        default=True, description="Добавлять в ответ информацию о статусе билетов"
    )
    add_remarks: bool = Field(
        default=True, description="Добавлять в ответ информацию о ремарках в PNR"
    )

    lang: str = 'en'

    _method_name: str = 'svc_add'

    def build(self) -> dict:
        request = {
            "regnum": {
                '#text': self.rloc,
                '@version': self.version
            },
            "svc": [item.build() for item in self.services],
            "answer_params": {
                "simple": self.simple,
                "show_svc": self.show_svc,
                "show_insurance_info": self.show_insurance_info,
                "add_ssr": self.add_ssr,
                "tickinfo": self.tick_info,
                "add_remarks": self.add_remarks,
                "lang": self.lang
            }
        }
        return request
