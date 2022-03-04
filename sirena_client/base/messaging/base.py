from abc import abstractmethod
from typing import Optional
from zlib import compress, decompress
from .message import MessageABC
from .header import Header


class RequestABC(MessageABC):
    """
    Абстрактный класс низкоуровнего запроса к шлюзу сирены
    """
    encryption_flag: Optional[int] = None  # Не зашифрованный запрос

    def __init__(
            self,
            body: bytes,
            msg_id: int,
            gzip_request: bool = False,
            gzip_response: bool = False,
            **kwargs,
    ):
        self.body = body
        self.msg_id = msg_id
        self.is_compressed_request = gzip_request
        self.is_compressed_response = gzip_response

        self.method_name = kwargs.get('method_name')

    @abstractmethod
    def make_message(self, client_id: int) -> bytes:
        raise NotImplemented

    def prepare_message(self) -> (bytes, bin, bin):
        body = self.body
        flag = 0x00
        if self.is_compressed_request:
            body = compress(self.body)
            flag = flag | self._request_compression_flag
        if self.is_compressed_response:
            flag = flag | self._response_compression_flag

        if self.encryption_flag is not None:
            flag = flag | self.encryption_flag
        return body, flag, 0x00


class ResponseABC(MessageABC):
    """
    Абстрактный класс низкоуровнего ответа от шлюза сирены
    """
    def __init__(self, header: Header, **kwargs):
        self.body_len = header.chunk_len
        self.is_compressed = header.is_compressed
        self.timestamp = header.timestamp
        self.msg_id = header.msg_id
        self.success = bool(header)
        self.key_id = header.key_id

        self.payload = None
        self.method_name = kwargs.get('method_name')

    def __nonzero__(self) -> bool:
        return self.success

    __bool__ = __nonzero__

    def __repr__(self):
        return f"{self.__class__.__name__} with ID: {self.msg_id}, status: {self.success}"

    def decode(self):
        self.payload = self.payload.decode('utf-8') if self.payload else None

    def parse(self, body) -> bytes:
        """Обработчик тела ответа"""
        result = body
        if self.is_compressed:
            try:
                result = decompress(result)
            except Exception:
                raise
        self.payload = result
        self.decode()
        return result
