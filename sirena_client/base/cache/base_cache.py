from time import time


class BaseCacheController:
    """
    Кэширование симметричного ключа

    Каждый симметричный ключ, (DES)
    действителен в течение полутора часов.
    По истечении этого времени сервер удаляет ключ и на зашифрованные
    им сообщения возвращает ошибку с атрибутом crypt_error=5
    ("Неизвестный симметричный ключ").
    """
    # Время жизни закэшированного ключа
    key_ttl: int = int(60 * 59 * 1.5)

    # название симметричного ключа в кэше
    _cache_key_body: str = 'sirena_sym_key_seed_cache'
    _cache_key_id: str = 'syrena_sym_key_id_cache'

    def __init__(
            self,
            redis_url,
    ):
        self._redis_url = redis_url
        self._backend = None

    @property
    def get_ttl(self):
        return int(time() + self.key_ttl)

    @property
    def is_available(self) -> bool:
        return True if self._backend else False
