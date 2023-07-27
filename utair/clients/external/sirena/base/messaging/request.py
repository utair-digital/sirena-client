from time import time
from struct import pack

from Crypto.Cipher import PKCS1_v1_5, DES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA1
from Crypto.Signature import pkcs1_15


from utair.clients.external.sirena.base.messaging.base import RequestABC, Header


class Request(RequestABC):
    """Класс открытого(незашифрованного) запроса"""

    encryption_flag = None

    def make_message(self, client_id=None) -> bytes:
        body, meta = self.prepare_message()
        header = Header(
            len(body),
            int(time()),
            self.msg_id,
            client_id,
            meta,
            0x00
        )
        msg = bytes(header) + body
        return msg


class RequestEncryptedSym(RequestABC):
    """Класс запроса, шифрованного симметричным ключом"""

    encryption_flag: int = 0x08     # Симметричный ключ
    block_size: int = 8

    def __init__(
            self,
            body: bytes,
            msg_id: int,
            gzip_request: bool = False,
            gzip_response: bool = False,
            key: DES = None,
            key_id: int = None,
            **kwargs
    ):
        super().__init__(body, msg_id, gzip_request, gzip_response, **kwargs)
        self.key = key
        self.key_id = key_id

    @classmethod
    def pad(cls, message_bytes: bytes) -> bytes:
        """Do pad message with standart PKCS padding"""

        one = 8 - len(message_bytes) % cls.block_size
        if one > 0:
            message_bytes += bytes([one]) * one
        return message_bytes

    def make_message(self, client_id=None) -> bytes:
        body, meta = self.prepare_message()
        body = self.pad(body)
        encrypted_body = self.key.encrypt(body)
        header = Header(
            len(encrypted_body),
            int(time()),
            self.msg_id,
            client_id,
            meta,
            0x00,
            self.key_id
        )
        msg = bytes(header) + encrypted_body
        return msg


class RequestEncryptedAsym(RequestABC):
    """Класс запроса, шифрованного асимметричным ключом"""

    encryption_flag: int = 0x40     # Ассиметричный ключ

    def __init__(
            self,
            body: bytes,
            msg_id: int = None,
            gzip_request: bool = False,     # noqa
            gzip_response: bool = False,    # noqa
            pub_key: RSA.RsaKey = None,
            private_key: RSA.RsaKey = None,
            **kwargs
    ):
        # TODO: сжатие для данного класса запроса не работает
        #   Пока что всегда проставляем false
        gzip_request: bool = False
        gzip_response: bool = False

        super().__init__(body, msg_id, gzip_request, gzip_response, **kwargs)
        self.pub_key = pub_key
        self.private_key = private_key

    def encrypt(self, plaintext):
        """
        Составление тела запроса для ассиметричного ключа
        :param plaintext: Оригинальное тело запроса
        :return:
        """
        message_encrypted = PKCS1_v1_5.new(self.pub_key).encrypt(plaintext)
        message_sha_encoded = SHA1.new(message_encrypted)

        signer = pkcs1_15.new(self.private_key)
        signature = signer.sign(message_sha_encoded)

        password_crypted_len = pack('!i', len(message_encrypted))  # first 4 bytes network byte order
        body = password_crypted_len + message_encrypted + signature
        return body

    def make_message(self, client_id=None):
        body, meta = self.prepare_message()
        body = self.encrypt(body)
        header = Header(
            len(body),
            int(time()),
            self.msg_id,
            client_id,
            meta,
            0x00,
        )
        msg = bytes(header) + body
        return msg
