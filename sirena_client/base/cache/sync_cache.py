from typing import Optional
from .base_cache import BaseCacheController
from redis import Redis


class SyncCacheController(BaseCacheController):

    @property
    def exists(self) -> bool:
        one = self.get()
        return bool(one)

    def purge(self):
        self._backend.delete(self._cache_key_body)
        self._backend.delete(self._cache_key_id)

    def get(self) -> (Optional[bytes], Optional[int]):
        key = self._backend.get(self._cache_key_body)
        key_id = self._backend.get(self._cache_key_id)
        key_id = int(key_id) if key_id else None
        return key, key_id

    def set(self, key_text: bytes, key_id: int) -> (bytes, int):
        self._backend.mset({self._cache_key_body: key_text, self._cache_key_id: key_id})
        self._backend.expireat(self._cache_key_body, self.get_ttl)
        self._backend.expireat(self._cache_key_id, self.get_ttl)
        return self.get()

    def spin_up(self):
        if not self._redis_url:
            return
        if not self.is_available:
            self._backend = Redis.from_url(self._redis_url)
