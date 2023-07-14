from struct import unpack
from Crypto.Cipher import DES, PKCS1_v1_5
from Crypto.PublicKey import RSA
from .base import ResponseABC, Header
from ..types import AsymEncryptionHandShake


class Response(ResponseABC):
    """
    Не зашифрованный ответ
    """


class ResponseEncryptedSym(ResponseABC):
    """
    Ответ зашифрованный симмитричным ключем
    """

    def __init__(
            self,
            header: Header,
            key: DES,
            **kwargs    # noqa
    ):
        super().__init__(
            header,
            method_name=kwargs.get('method_name')
        )
        self.key: DES = key

    def decrypt(self, body: bytes) -> str:
        plaintext = self.key.decrypt(body)
        return plaintext

    def parse(self, body):
        """Обработчик тела ответа"""
        body = self.decrypt(body)
        decompressed = super(ResponseEncryptedSym, self).parse(body)
        self.payload = self.un_pad(decompressed)

    @classmethod
    def un_pad(cls, message_bytes: bytes) -> bytes:
        """Распаковать сообщение по стандартам PKCS padding"""
        one = message_bytes[-1]
        if 0 < one < 8:
            return message_bytes[:-one]
        return message_bytes


class ResponseEncryptedAsym(ResponseABC):
    """
    Ответ зашифрованный ассимитричным ключем
    """
    def __init__(
            self,
            header: Header,
            private_key: RSA.RsaKey,
            public_key: RSA.RsaKey,
            **kwargs,   # noqa
    ):
        self.private_key = private_key
        self.public_key = public_key
        super().__init__(header, method_name=kwargs.get('method_name'))

    def parse(self, body):
        """Обработчик тела ответа на запрос"""
        # Длина зашифрованного сообщения в сетевом формате находится в первых 4 байтах сообщения
        message_size_bytes = 4
        (len_encrypted,) = unpack('!i', body[:message_size_bytes])
        # минус 4 байта в начале + длинна шифрованного сообщения
        message = bytes(body[message_size_bytes:len_encrypted + message_size_bytes])

        try:
            key: bytes = PKCS1_v1_5.new(self.private_key).decrypt(message, b'')
            # Ожидаем получить тут открытый ключ, если что-то пойдет не так - падаем сильно и громко

            # Подкидываем фейковый XML, так как это единственный метод, который отвечает просто данными без структуры
            self.payload = f"""<?xml version="1.0" encoding="UTF-8"?>
            <sirena>
              <answer>
                <{AsymEncryptionHandShake.ASYM_HAND_SHAKE.value}>
                    {key}
                </{AsymEncryptionHandShake.ASYM_HAND_SHAKE.value}>
              </answer>
            </sirena>
            """
        except Exception as e:   # noqa
            self.payload = f"""<?xml version="1.0" encoding="UTF-8"?>
            <sirena>
              <answer>
                <{AsymEncryptionHandShake.ASYM_HAND_SHAKE.value}>
                    <error code="-42">Unable to decrypt AsymEncryption body, reason: {str(e)}</error> 
                </{AsymEncryptionHandShake.ASYM_HAND_SHAKE.value}>
              </answer>
            </sirena>
            """
