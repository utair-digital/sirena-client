from typing import List, Union
from pydantic import Field
from sirena_client.base.models.base_client_request import RequestModelABC


class RemoveSegments(RequestModelABC):

    rloc: str = Field(description="Номер бронирования")
    last_name: str = Field(description="Фамилия пассажира")
    segments: List[str] = Field(description="Список идентификаторов сегментов для удаления")

    version: Union[str, int] = "ignore"

    lang: str = 'en'

    _method_name: str = 'remove_segments'

    def build(self) -> dict:
        request = {
            "regnum": {
                '#text': self.rloc,
                '@version': self.version
            },
            "surname": self.last_name,
            "remove": {
                "segment": [{"@seg_id": seg_id} for seg_id in self.segments]
            },
        }
        return request
