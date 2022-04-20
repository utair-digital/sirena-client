import asyncio
import random
from typing import Union, Optional


class AsyncConnection:

    def __init__(
            self,
            host: str,
            port: Union[str, int]
    ):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.id = random.randint(0, 9999)   # Debugging

    @property
    def connected(self) -> bool:
        return all((self.reader, self.writer))

    async def write(self, data: bytes):
        self.writer.write(data)
        await self.writer.drain()

    async def read(self, size: int) -> bytes:
        data: bytes = await self.reader.read(size)
        return data

    async def connect(self):
        if self.connected:
            return
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        if not any((self.writer, self.writer)):
            raise ConnectionError(f'Can not get connection to {self.host}:{self.port}')

    async def disconnect(self):
        if not self.connected:
            return
        self.writer.close()
        self.writer = None
        self.reader = None
