from typing import Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, field_validator, Field
from xmltodict import unparse
from utair.clients.external.sirena.base.types import AsymEncryptionHandShake, PublicMethods


class RequestModelABC(BaseModel, ABC):
    _method_name: str = ''
    _nested: bool = False   # Вложенная часть

    @field_validator("rloc", check_fields=False)
    def format_rloc(cls, rloc: Optional[str]) -> Optional[str]:
        """
        Форматирование рлока
        """
        if rloc and '/' in rloc:
            return rloc.split('/')[0]
        return rloc

    @field_validator("last_name", check_fields=False)
    def format_last_name(cls, last_name: Optional[str]) -> Optional[str]:
        """
        Форматирование фамилии
        """
        if not last_name:
            return last_name
        sub_map = {
            'ё': 'е',
            'Ё': 'Е',
            '-': '',
            'ъ': 'ь',
            'Ъ': 'ь',
        }
        for k, v in sub_map.items():
            last_name = last_name.replace(k, v)
        return last_name

    @property
    def method_name(self) -> str:
        if not self._method_name and not self._nested:
            raise Exception("Method name must be provided")
        return self._method_name

    @abstractmethod
    def build(self) -> dict:
        raise NotImplementedError()

    @classmethod
    def _remove_empty_values(cls, payload: dict) -> dict:
        """
        Удаляем пустые значения из запроса
        """
        return cls._recursive_filter(payload, None, list(), dict())

    @classmethod
    def _recursive_filter(cls, item, *forbidden):
        if isinstance(item, list):
            return [cls._recursive_filter(entry, *forbidden) for entry in item if entry not in forbidden]
        if isinstance(item, dict):
            result = {}
            for key, value in item.items():
                if isinstance(value, float):
                    value = str(value)
                value = cls._recursive_filter(value, *forbidden)
                if key not in forbidden and value not in forbidden:
                    result[key] = value
            return result
        return item

    def prepare_payload(self) -> bytes:
        """
        Подготовка запроса
        """
        blank_dict = {
            'sirena': {
                'query': {
                    self.method_name: self._remove_empty_values(self.build())
                }
            }
        }
        xml_query = unparse(blank_dict).encode('utf-8')
        return xml_query


class KeyInfoRequest(RequestModelABC):

    _method_name: str = PublicMethods.KEY_INFO.value

    def build(self) -> dict:
        return dict()


class AsymEncryptionHandShakeRequest(RequestModelABC):

    _method_name: str = AsymEncryptionHandShake.ASYM_HAND_SHAKE.value

    def build(self) -> dict:
        return dict()


class IClientPubKeyRequest(RequestModelABC):
    pub_key: str = Field(description="Публичный ключ для добавления в сирену")

    _method_name: str = PublicMethods.I_CLIENT_PUB_KEY.value

    def build(self) -> dict:
        return dict(
            pub_key=self.pub_key
        )
