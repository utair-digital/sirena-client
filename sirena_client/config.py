import os
from typing import Optional
from dataclasses import dataclass

PROJECT_ROOT = os.path.realpath(os.path.abspath(os.curdir))


@dataclass
class SirenaClientConfig:
    host: str = os.getenv("SIRENA_HOST")
    port: int = os.getenv("SIRENA_PORT")
    client_id: int = os.getenv("SIRENA_CLIENT_ID")
    private_key: Optional[str] = os.getenv("SIRENA_CLIENT_ID")
    private_key_path: Optional[str] = None,
    redis_url: Optional[str] = None
    # Async Client Configs:
    use_connection_pool: bool = False
    pool_min_size: int = 2
    pool_max_size: int = 4
    logger_name: str = 'sirena_client'

    def __post_init__(self):
        assert all((
            self.host, self.port,
            self.client_id,
            any((self.private_key, self.private_key_path))
        )), "Invalid configuration"
