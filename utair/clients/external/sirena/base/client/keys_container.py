from typing import Optional, Dict
from Crypto.PublicKey import RSA
from Crypto import Random
from dataclasses import dataclass, field
from Crypto.Cipher import DES

from utair.clients.external.sirena.exceptions import SirenaEncryptionKeyError


@dataclass
class KeysContainer:
    """
    Контейнер ключей
    """
    # Asymmetric
    private_key: Optional[RSA.RsaKey] = field(repr=False, default=None)
    public_key: Optional[RSA.RsaKey] = field(repr=False, default=None)

    # Symmetric
    _sym_key_seed: Optional[bytes] = field(repr=False, default=None)
    _sym_key: DES = field(repr=False, default=None)
    # При одновременном использовании нескольких симметричных ключей клиент должен указывать
    # в заголовке идентификатор используемого ключа для шифрования каждого сообщения.
    # Если идентификатор ключа не указан (заполнен нулями),
    # для работы берется последний зарегистрированный симметричный ключ.
    _sym_key_id: int = field(repr=False, default=None)

    def __post_init__(self):
        self.reset_des_ecb()

    def reset_des_ecb(self):
        # будущий DES.ECB должен быть 8 байт
        self._sym_key_seed = Random.get_random_bytes(8)
        self._sym_key = None

    @property
    def get_des_key(self) -> DES:
        if not self._sym_key:
            self._sym_key = DES.new(self.sym_key_seed, DES.MODE_ECB)
        return self._sym_key

    @property
    def sym_key_seed(self) -> Optional[bytes]:
        return self._sym_key_seed

    @sym_key_seed.setter
    def sym_key_seed(self, value: bytes):
        if not isinstance(value, bytes) or len(value) != 8:
            raise RuntimeError("Invalid sym key seed, must be 8 bytes bytearray")
        self._sym_key_seed = value

    @property
    def sym_key_id(self) -> Optional[int]:
        return self._sym_key_id

    @sym_key_id.setter
    def sym_key_id(self, value: int):
        if not isinstance(value, int):
            raise RuntimeError("Invalid sym key id, must be integer")
        self._sym_key_id = value

    @staticmethod
    def parse_rsa_key(data: bytes) -> RSA.RsaKey:
        return RSA.import_key(data)

    def is_able_to_asym(self):
        if any((not self.private_key, not self.public_key)):
            raise RuntimeError("Unable to do asymmetric encrypted request, keys not found")

    def is_able_to_sym(self):
        if not self.sym_key_seed:
            raise RuntimeError("Unable to do symmetric encrypted request")

    def set_pub_key(self, key_info: Dict):
        """
        param: key_info: key_info method response
        """
        pub_key = key_info.get('key_manager', {}).get('server_public_key')
        if not pub_key:
            raise SirenaEncryptionKeyError('Can not register symmenric key! key_info server_public_key not found')
        self.public_key = self.parse_rsa_key(pub_key)
