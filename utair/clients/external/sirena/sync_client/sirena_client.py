from utair.clients.external.sirena.config import SirenaClientConfig
from utair.clients.external.sirena.base.client.sync_client_batchable import SyncBatchableClient


class SirenaClient(SyncBatchableClient):
    """
    Синхронный клиент сирены
    """

    def __init__(self, config: SirenaClientConfig):
        self.config = config
        super().__init__(
            host=self.config.host,
            port=self.config.port,
            client_id=self.config.client_id,
            private_key=self.config.private_key,
            private_key_path=self.config.private_key_path,
            redis_url=self.config.redis_url,
            logger_name=self.config.logger_name
        )

    def __enter__(self) -> "SirenaClient":
        self._ignore_connection_calls = True
        self.connect(ignore=False)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect(ignore=False)
        self._ignore_connection_calls = False
