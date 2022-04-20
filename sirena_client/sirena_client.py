from typing import Optional
from .base.client.sync_client_batchable import SyncBatchableClient as SyncClient
from .base.client.async_client_batchable import AsyncBatchableClient as AsyncClient
from .base.connection.async_pool import AsyncConnectionPool
from .config import SirenaClientConfig

_CONNECTION_POOL: Optional[AsyncConnectionPool] = None


class SirenaClient:
    """
    Общий интерфейс для получения синхронного или асинхронного клиента сирены
    """
    _sync_client: SyncClient = None
    _async_client: AsyncClient = None

    def __init__(self, config: SirenaClientConfig):
        self.config = config

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

    async def __aenter__(self) -> AsyncClient:
        if not self._async_client:
            self._async_client = AsyncClient(
                host=self.config.host,
                port=self.config.port,
                client_id=self.config.client_id,
                private_key=self.config.private_key,
                private_key_path=self.config.private_key_path,
                pool=self._connection_pool if self.config.use_connection_pool else None,
                redis_url=self.config.redis_url,
                logger_name=self.config.logger_name
            )
        await self._async_client.connect(ignore=False)
        self._async_client._ignore_connection_calls = True
        return self._async_client

    async def __aexit__(self, exc_type, exc, tb):
        # В случае если при создании объекта был передан пул соединений
        # подключение и отключением управляет сам пул
        await self._async_client.disconnect(ignore=False)
        self._ignore_connection_calls = False

    def __enter__(self) -> SyncClient:
        if not self._sync_client:
            self._sync_client = SyncClient(
                host=self.config.host,
                port=self.config.port,
                client_id=self.config.client_id,
                private_key=self.config.private_key,
                private_key_path=self.config.private_key_path,
                redis_url=self.config.redis_url,
                logger_name=self.config.logger_name
            )
        self._sync_client._ignore_connection_calls = True
        self._sync_client.connect(ignore=False)
        return self._sync_client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._sync_client.disconnect(ignore=False)
        self._ignore_connection_calls = False
