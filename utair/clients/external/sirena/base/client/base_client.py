import json
from typing import Optional, Union
from logging import getLogger
from abc import ABC

from socket import socket

from utair.clients.external.sirena.base.messaging import (
    Header, Request, RequestEncryptedSym, RequestEncryptedAsym, RequestABC
)

from utair.clients.external.sirena.base.models.base_client_request import RequestModelABC
from utair.clients.external.sirena.base.connection.async_pool import AsyncConnectionPool
from utair.clients.external.sirena.base.cache.base_cache import BaseCacheController
from utair.clients.external.sirena.base.client.keys_container import KeysContainer

from utair.clients.external.sirena.base.messaging.response import (
    ResponseABC,
    Response,
    ResponseEncryptedAsym,
    ResponseEncryptedSym
)
from utair.clients.external.sirena.base.models.base_client_response import ResponseModelABC
from utair.clients.external.sirena.base.types import PublicMethods, AsymEncryptionHandShake


class BaseClient(ABC):
    compress_response: bool = True
    compress_request: bool = True

    # Размер куска, который мы читаем за раз в байтах (если он больше тела)
    read_chunk_size: int = 1024
    # Максимальное кол-во попыток сделать запрос сирене и дождаться ответа
    max_request_retries: int = 5

    def __init__(
            self,
            host: str,
            port: int,
            client_id: int,
            redis_url: str = None,
            private_key: Optional[str] = None,
            private_key_path: Optional[str] = None,
            logger_name: str = 'sirena_client',
            **kwargs
    ):
        """
        :param host: хост сирены
        :param port: порт
        :param client_id: ID клиента
        :param redis_url: URL Redis для кэширования симметричного ключа
        :param private_key_path: путь к файлу с приватным ключом
        :param kwargs: остальные параметры
        """
        self.host = host
        self.port = port
        self.client_id = client_id
        self.msg_count = 0

        self.redis_url = redis_url

        self.private_key_path = private_key_path
        self.private_key = private_key

        if not any((
            self.private_key, self.private_key_path
        )):
            raise Exception("Private key or private key path is required for encryption")

        self._connection: Optional[Union[AsyncConnectionPool, socket]] = None
        self._ignore_connection_calls = False

        self._keys = KeysContainer()
        self._handshake: bool = False

        self._cache: Optional[BaseCacheController] = None
        self.logger = getLogger(logger_name)

    @property
    def connected(self) -> bool:
        if self._connection is None:
            return False
        return self._connection._closed # noqa

    @property
    def hand_shake_done(self) -> bool:
        return self._handshake

    @hand_shake_done.setter
    def hand_shake_done(self, value: bool = True):
        self._handshake = value

    @property
    def next_message_id(self) -> int:
        # NB: максимально unsigned 4 byte int
        self.msg_count += 1
        return self.msg_count

    def request_factory(self, client_request: RequestModelABC) -> RequestABC:
        if client_request.method_name == AsymEncryptionHandShake.ASYM_HAND_SHAKE.value:
            # Запрос для получения ключа симметричного шифрования
            self._keys.is_able_to_asym()
            return RequestEncryptedAsym(
                self._keys.sym_key_seed,
                self.next_message_id,
                # Компрессия не поддерживается при шифровании ассимитричным ключем
                False, False,
                self._keys.public_key,
                self._keys.private_key,
                method_name=client_request.method_name
            )
        if client_request.method_name in PublicMethods._value2member_map_:  # noqa
            return Request(
                body=client_request.prepare_payload(),
                msg_id=self.next_message_id,
                gzip_request=self.compress_request,
                gzip_response=self.compress_response,
                method_name=client_request.method_name
            )
        self._keys.is_able_to_sym()
        return RequestEncryptedSym(
            body=client_request.prepare_payload(),
            msg_id=self.next_message_id,
            gzip_request=self.compress_request,
            gzip_response=self.compress_response,
            key=self._keys.get_des_key,
            key_id=self._keys.sym_key_id,
            method_name=client_request.method_name
        )

    def response_factory(self, header: Header, method_name: str) -> ResponseABC:
        if header.is_not_encrypted:
            response = Response
        elif header.is_sym_encrypted:
            response = ResponseEncryptedSym
        elif header.is_asym_encrypted:
            response = ResponseEncryptedAsym
        else:
            raise RuntimeError("Unable to define header encryption")

        return response(
            header=header,
            key=self._keys.get_des_key,
            private_key=self._keys.private_key,
            public_key=self._keys.public_key,
            method_name=method_name
        )

    def load_private_key(self) -> bool:
        if not self.private_key:
            return False
        self._keys.private_key = self._keys.parse_rsa_key(self.private_key) # noqa
        return True

    def _request_log(self, request: RequestModelABC, response: ResponseModelABC):
        self.logger.info(f"Sirena request: {request.method_name}", extra=dict(
            integrator_name="sirena",
            api_method=request.method_name,
            request_body=json.dumps(request.build(), indent=4),
            response_body=json.dumps(response.payload or {}, indent=4),
        ))
