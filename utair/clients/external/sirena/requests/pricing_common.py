from typing import List, Literal, Optional, Union

from pydantic import Field

from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.requests.params_base import BaseAnswerParams, BaseRequestParams


class PricingAcomp(RequestModelABC):
    name: str = Field(description="Код авиакомпании (атрибут @name)")
    flights: Optional[List[str]] = Field(
        description="Номера рейсов. '*' — все рейсы указанной авиакомпании.",
        default=None,
    )

    _nested: bool = True

    def build(self) -> dict:
        request: dict = {"@name": self.name}
        if self.flights:
            request["flight"] = list(self.flights) if len(self.flights) > 1 else self.flights[0]
        return request


class PricingFlightFilter(RequestModelABC):
    """Структура элементов <desire> и <ignore>."""

    acomps: List[PricingAcomp] = Field(description="Список авиакомпаний/рейсов фильтра")

    _nested: bool = True

    def build(self) -> dict:
        if not self.acomps:
            return {}
        items = [a.build() for a in self.acomps]
        return {"acomp": items if len(items) > 1 else items[0]}


class PricingCombRule(RequestModelABC):
    comb: Literal["yes", "no"] = Field(description="Разрешить комбинирование")
    acomps: List[str] = Field(description="Коды авиакомпаний (или '*')")

    _nested: bool = True

    def build(self) -> dict:
        request: dict = {"@comb": self.comb}
        if self.acomps:
            request["acomp"] = list(self.acomps) if len(self.acomps) > 1 else self.acomps[0]
        return request


class PricingFormPay(RequestModelABC):
    code: str = Field(description="Код формы оплаты")
    type: Optional[str] = Field(
        description="Тип платёжного средства/системы",
        default=None,
    )
    num: Optional[str] = Field(
        description="Номер/идентификатор платёжного средства",
        default=None,
    )

    _nested: bool = True

    def build(self) -> dict:
        request: dict = {"#text": self.code}
        if self.type is not None:
            request["@type"] = self.type
        if self.num is not None:
            request["@num"] = self.num
        return request


class PricingRequestParams(BaseRequestParams):
    """
    Специфичные параметры <request_params> для pricing-запросов
    """

    min_results: Optional[Union[int, Literal["spOnePass"]]] = Field(
        description="Минимальное желаемое количество разных оценок "
        "(число или спец-значение 'spOnePass')",
        default=None,
    )
    max_results: Optional[int] = Field(
        description="Максимальное количество вариантов, возвращаемых в ответе",
        default=None,
    )
    timeout: Optional[int] = Field(
        description="Таймаут выполнения запроса (секунды, от 5 до 150)",
        default=None,
    )
    mix_scls: Optional[bool] = Field(
        description="Комбинировать подклассы на сегментах по маршруту перевозки",
        default=None,
    )
    mix_ac: Optional[bool] = Field(
        description="Комбинировать рейсы разных перевозчиков по маршруту перевозки",
        default=None,
    )
    comb_rules: Optional[Union[str, List[PricingCombRule]]] = Field(
        description="Правила комбинирования рейсов авиакомпаний",
        default=None,
    )
    fingering_order: Optional[str] = Field(
        description="Порядок перебора вариантов при оценке "
        "(ordinary, differentFirst, differentFlightsCombFirst, differentFlightsFirst)",
        default=None,
    )
    price_child_aaa: Optional[bool] = Field(
        description="Провести тарификацию ребёнка по взрослому тарифу, если не найдено скидок",
        default=None,
    )
    asynchronous_fares: Optional[bool] = Field(
        description="Не применять тарифы с одновременным бронированием и оформлением",
        default=None,
    )
    show_tmb: Optional[bool] = Field(
        description="Готовить и показывать справку по норме провоза багажа",
        default=None,
    )
    formpay: Optional[Union[str, PricingFormPay]] = Field(
        description="Форма оплаты для оценки",
        default=None,
    )
    pt_baggage: Optional[bool] = Field(
        description="Показывать только 'багажные' тарифы",
        default=None,
    )
    # далее идут недокументированные параметры:
    et_if_possible: Optional[bool] = Field(
        description="Оформление ЭБ при возможности",
        default=False,
    )
    allow_change_of_airport: Optional[bool] = Field(
        description="Пересадки со сменой аэропорта",
        default=False,
    )
    real_seats: Optional[bool] = Field(
        description="Учитывать реальное количество мест",
        default=None,
    )
    # --------------------------------

    _nested: bool = True

    # реализация для обратной совместимости:
    @staticmethod
    def _build_comb_rules(
        comb_rules: Optional[Union[str, List[PricingCombRule]]],
    ) -> Optional[Union[str, dict]]:
        if comb_rules is None:
            return None
        if isinstance(comb_rules, str):
            return comb_rules
        rules = [r.build() for r in comb_rules]
        return {"rule": rules if len(rules) > 1 else rules[0]}
    # --------------------------------

    def build(self) -> dict:
        # реализация для обратной совместимости:
        formpay: Optional[Union[str, dict]]
        if isinstance(self.formpay, PricingFormPay):
            formpay = self.formpay.build()
        else:
            formpay = self.formpay
        # --------------------------------
        request = {
            **super().build(),
            "min_results": self.min_results,
            "max_results": self.max_results,
            "timeout": self.timeout,
            "mix_scls": self.mix_scls,
            "mix_ac": self.mix_ac,
            "comb_rules": self._build_comb_rules(self.comb_rules),
            "fingering_order": self.fingering_order,
            "price_child_aaa": self.price_child_aaa,
            "asynchronous_fares": self.asynchronous_fares,
            "show_tmb": self.show_tmb,
            "formpay": formpay,
            "pt_baggage": self.pt_baggage,
            "allow_change_of_airport": self.allow_change_of_airport,
            "et_if_possible": self.et_if_possible,
        }
        if self.real_seats:
            request["real_seats"] = self.real_seats
        return request


class PricingAnswerParams(BaseAnswerParams):
    """
    Специфичные параметры <answer_params> для pricing-запросов
    """

    show_available: Optional[bool] = Field(
        description="Добавлять в ответ информацию о наличии мест на подклассе",
        default=None,
    )
    show_io_matching: Optional[bool] = Field(
        description="Добавлять в ответ информацию о соответствии сегментов запроса сегментам ответа",
        default=None,
    )
    show_flighttime: Optional[bool] = Field(
        description="Добавлять в ответ информацию о времени перелета и времени следования по сегментам",
        default=None,
    )
    show_varianttotal: Optional[bool] = Field(
        description="Добавлять в ответ информацию об общей стоимости перевозки по варианту",
        default=None,
    )
    show_baseclass: Optional[bool] = Field(
        description="Добавлять к каждому подклассу код его базового класса",
        default=None,
    )
    show_reg_latin: Optional[bool] = Field(
        description="Указывать необходимость оформления билета на латинице",
        default=None,
    )
    show_upt_rec: Optional[bool] = Field(description="Выдать детализацию УПТ", default=None)
    show_fareexpdate: Optional[bool] = Field(
        description="Указывать дату истечения срока действия тарифа",
        default=None,
    )
    show_n_blanks: Optional[bool] = Field(
        description="Возвращать количество билетов, необходимых для оформления перевозки",
        default=None,
    )
    regroup: Optional[bool] = Field(description="Перегруппировка ответа", default=None)
    split_companies: Optional[bool] = Field(
        description="При перегруппировке ответа объединять в один вариант только рейсы одной "
        "авиакомпании. Автоматически установит параметр запроса mix_ac='false'",
        default=None,
    )
    reference_style_codes: Optional[bool] = Field(
        description="Возвращать коды авиакомпаний по правилам, принятым в справочных запросах. "
        "По доке default=true на стороне шлюза",
        default=None,
    )
    mark_cityport: Optional[bool] = Field(
        description="Добавлять в ответ признаки city или airport для пунктов",
        default=None,
    )
    show_tml: Optional[bool] = Field(
        description="Добавлять в ответ информацию о ТЛ на оформление перевозки",
        default=None,
    )
    show_brand_info: Optional[bool] = Field(
        description="Добавлять в ответ информацию о составе брендов",
        default=None,
    )
    show_cat18: Optional[bool] = Field(
        description="Добавлять в ответ примечания из кат. 18 УПТ",
        default=None,
    )
    show_joint_id: Optional[bool] = Field(
        description="Добавлять в ответ информацию о joint_id на сегментах перевозки",
        default=None,
    )
    show_meals: Optional[bool] = Field(
        description="Добавлять в ответ информацию о компоновке кабин и питании, включённом в билет",
        default=None,
    )
    show_bag_norm_full: Optional[bool] = Field(
        description="Добавлять в ответ детальную информацию о нормах бесплатного провоза "
        "багажа и ручной клади",
        default=None,
    )

    _nested: bool = True

    def build(self) -> dict:
        return {
            **super().build(),
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
            "show_joint_id": self.show_joint_id,
            "show_meals": self.show_meals,
            "show_bag_norm_full": self.show_bag_norm_full,
        }
