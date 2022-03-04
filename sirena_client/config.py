from typing import Optional
from dataclasses import dataclass


@dataclass
class SirenaClientConfig:
    host: str
    port: int
    client_id: int
    private_key_path: str
    redis_url: Optional[str] = None
    # Async Client Configs:
    use_connection_pool: bool = False
    pool_min_size: int = 2
    pool_max_size: int = 4
    logger_name: str = 'sirena_client'
