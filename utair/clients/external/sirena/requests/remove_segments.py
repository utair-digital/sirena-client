from typing import List, Union
from pydantic import Field, model_validator
from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC


class RemoveSegmentsRequest(RequestModelABC):

    rloc: str = Field(description="Номер бронирования")
    last_name: str = Field(description="Фамилия пассажира")
    segments: List[str] = Field(description="Список идентификаторов сегментов для удаления")
    ssrs: List[str] = Field(description="Список идентификаторов SSR для удаления")

    version: Union[str, int] = "ignore"

    lang: str = 'en'

    _method_name: str = 'modify_pnr'

    @model_validator(mode='after')
    def validate_has_items_to_remove(self):
        if not self.segments and not self.ssrs:
            raise ValueError("Должен быть указан хотя бы один сегмент или SSR для удаления")
        return self

    def build(self) -> dict:
        request = {
            "regnum": {
                '#text': self.rloc,
                '@version': self.version
            },
            "surname": self.last_name,
            "remove": {},
        }
        remove_data = {}
        if self.segments:
            remove_data["segment"] = [{"@seg_id": seg_id} for seg_id in self.segments]
        if self.ssrs:
            remove_data["ssr"] = [{"@key": ssr_id} for ssr_id in self.ssrs]
        request["remove"] = remove_data
        return request
