from typing import Optional
from utair.clients.external.sirena.base.client.async_client_batchable import AsyncBatchableClient
from utair.clients.external.sirena.base.connection.async_pool import AsyncConnectionPool
from utair.clients.external.sirena.config import SirenaClientConfig

_CONNECTION_POOL: Optional[AsyncConnectionPool] = None


class SirenaClient(AsyncBatchableClient):
    """
    Асинхронный клиент сирены
    """
    def __init__(self, config: SirenaClientConfig):
        self.config = config
        super().__init__(
            host=self.config.host,
            port=self.config.port,
            client_id=self.config.client_id,
            private_key=self.config.private_key,
            private_key_path=self.config.private_key_path,
            pool=self._connection_pool if self.config.use_connection_pool else None,
            redis_url=self.config.redis_url,
            logger_name=self.config.logger_name
        )

    @property
    def _connection_pool(self) -> AsyncConnectionPool:
        global _CONNECTION_POOL
        if not _CONNECTION_POOL:
            _CONNECTION_POOL = AsyncConnectionPool(
                host=self.config.host,
                port=self.config.port,
                min_size=self.config.pool_min_size,
                max_size=self.config.pool_max_size
            )
        return _CONNECTION_POOL

    async def __aenter__(self) -> "SirenaClient":
        await self.connect(ignore=False)
        self._ignore_connection_calls = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        # В случае если при создании объекта был передан пул соединений
        # подключение и отключением управляет сам пул
        await self.disconnect(ignore=False)
        self._ignore_connection_calls = False
