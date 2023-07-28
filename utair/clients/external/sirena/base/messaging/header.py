from time import time
from struct import unpack, pack
from dataclasses import dataclass
from utair.clients.external.sirena.base.messaging.message import MessageABC


@dataclass
class Header(MessageABC):
    """
    Заголовок запроса и ответа
    """
    chunk_len: int
    timestamp: int
    msg_id: int
    client_id: int
    meta_flag: int     # Флаг компрессии и шифрования
    success_flag: int  # Флаг успешности
    key_id: int = 0
    """
    Формат заголовка (длина 100 байт)

    Смещение	Длина (байт)	Тип	            Описание
    0	        4	            Целое число	    Длина текста сообщения (без заголовка)
    4	        4	            Целое число	    Время создания запроса (кол-во секунд с 1 января 1970 GMT)
    8	        4	            Целое число	    Идентификатор сообщения
    12	        32          	 	Зарезервировано (заполнено нулевым байтом)
    44	        2	            Целое число	    Идентификатор клиента
    46	        1	             	1-й байт    флагов сообщения
    47	        1	             	2-й байт    флагов сообщения
    48	        4	            Целое число	Идентификатор симметричного ключа
    52	        48          	 	Зарезервировано (заполнено нулевым байтом)
    """
    # https://docs.python.org/3/library/struct.html#format-characters
    _format = "!III32xHBBI48x"  # network (= big-endian)
    size: int = 100

    # Флаг "Запрос не обработан" устанавливается сервером в случаях,
    # если сообщение от клиента не удалось правильно обработать в виду временных обстоятельств,
    # и клиенту следует повторить попытку
    _is_error_flag = 0x01

    @classmethod
    def parse(cls, header: bytes) -> "Header":
        return Header(*unpack(cls._format, header))

    @property
    def is_compressed(self) -> bool:
        return bool(self.meta_flag & self._response_compression_flag)

    @property
    def is_asym_encrypted(self) -> bool:
        return bool(self.meta_flag & self._is_asym_encrypted_flag)

    @property
    def is_sym_encrypted(self) -> bool:
        return bool(self.meta_flag & self._is_sym_encrypted_flag)

    @property
    def is_not_encrypted(self) -> bool:
        return not self.is_asym_encrypted and not self.is_sym_encrypted

    def __bytes__(self) -> bytes:
        return self.to_bytes()

    def __nonzero__(self) -> bool:
        return not bool(self.success_flag & self._is_error_flag)

    __bool__ = __nonzero__

    def to_bytes(self) -> bytes:
        header = pack(
            self._format, self.chunk_len, int(time()),
            self.msg_id, self.client_id, self.meta_flag, self.success_flag, self.key_id
        )
        return header
