from typing import Optional, Union
from datetime import date

from pydantic import Field

from sirena_client.base.models.base_client_request import RequestModelABC


class GetCompanyRoutes(RequestModelABC):

    company: str = Field(description="Код авиакомпании")
    lang: str = "en"

    _method_name: str = "get_company_routes"

    def build(self) -> dict:
        answer_params = {
            "lang": self.lang,
        }
        request = {
            "company": self.company,
            "answer_params": answer_params,
        }
        return request