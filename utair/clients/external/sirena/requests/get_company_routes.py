from pydantic import Field
from typing import Optional
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class GetCompanyRoutes(RequestModelABC):

    company: str = Field(description="Код авиакомпании")
    joint_type: Optional[str] = Field(default=None, description="Тип стыковки")
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
        if self.joint_type:
            request["request_params"] = {"joint_type": self.joint_type}
        return request
