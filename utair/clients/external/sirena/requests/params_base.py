from typing import Optional

from pydantic import Field

from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class BaseRequestParams(RequestModelABC):
    """
    Общие параметры секции <request_params> (Table 1.5).
    """

    ersp_code: Optional[str] = Field(
        description="Код интернет-пункта продажи",
        default=None,
    )

    _nested: bool = True

    def build(self) -> dict:
        return {"ersp_code": self.ersp_code}


class BaseAnswerParams(RequestModelABC):
    """
    Общие параметры секции <answer_params> (Table 1.4).
    """

    lang: Optional[str] = Field(
        description="Язык ответа (en|ru). По умолчанию — язык виртуального пульта.",
        default="en",
    )
    curr: Optional[str] = Field(
        description="Валюта ответа (код валюты). По умолчанию — валюта виртуального пульта.",
        default=None,
    )

    _nested: bool = True

    def build(self) -> dict:
        return {"lang": self.lang, "curr": self.curr}
