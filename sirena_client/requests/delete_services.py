from typing import List, Union
from pydantic import Field
from sirena_client.base.models.base_client_request import RequestModelABC


class DeleteServices(RequestModelABC):

    rloc: str = Field(description="Номер бронирования")
    service_ids: List[int] = Field(description="Идентификаторы услуг")

    version: Union[str, int] = "ignore"

    lang: str = 'en'

    _method_name: str = 'svc_del'

    def build(self) -> dict:
        request = {
            'regnum': {
                '#text': self.rloc,
                '@version': self.version
            },
            'svc': [{
                '@id': item
            } for item in self.service_ids],
            "answer_params": {
                "lang": "en"
            }
        }
        return request
