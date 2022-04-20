from typing import Optional
from .base_cache import BaseCacheController
from aioredis import Redis, create_connection

_ASYNC_BACKEND: Optional[Redis] = None


class AsyncCacheController(BaseCacheController):

    @property
    async def exists(self) -> bool:
        one = await self.get()
        return bool(one)

    async def get(self) -> (Optional[bytes], Optional[int]):
        key = await self._backend.get(self._cache_key_body)
        key_id = await self._backend.get(self._cache_key_id)
        key_id = int(key_id) if key_id else None
        return key, key_id

    async def purge(self):
        await self._backend.delete(self._cache_key_body)
        await self._backend.delete(self._cache_key_id)

    async def set(self, key_text: bytes, key_id: int) -> (bytes, int):
        await self._backend.mset({self._cache_key_body: key_text, self._cache_key_id: key_id})
        await self._backend.expireat(self._cache_key_body, self.get_ttl)
        await self._backend.expireat(self._cache_key_id, self.get_ttl)
        return await self.get()

    async def spin_up(self):
        if not self._redis_url:
            return
        if self.is_available:
            return
        global _ASYNC_BACKEND
        if not _ASYNC_BACKEND:
            _ASYNC_BACKEND = Redis(
                pool_or_conn=await create_connection(
                    address=self._redis_url
                )
            )
        self._backend = _ASYNC_BACKEND
