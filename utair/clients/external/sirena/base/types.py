from enum import Enum


class PublicMethods(Enum):
    """
    Публичные методы, которые не требуют шифрования при запросе
    """
    KEY_INFO = 'key_info'
    I_CLIENT_PUB_KEY = 'iclient_pub_key'


class AsymEncryptionHandShake(Enum):
    ASYM_HAND_SHAKE = 'asym_hand_shake'
