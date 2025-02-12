import asyncio
import random
import socket
import sys
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
        if not all((self.reader, self.writer)):
            return False
        if self.writer.is_closing():
            return False
        return True

    async def write(self, data: bytes):
        self.writer.write(data)
        await self.writer.drain()

    async def read(self, size: int) -> bytes:
        try:
            data: bytes = await asyncio.wait_for(self.reader.read(size), timeout=60)
            return data
        except IOError:
            await self.disconnect()
            raise

    async def connect(self):
        if self.connected:
            return
        await self._tcp_reconnect()

    async def _tcp_reconnect(self):
        max_tries = 5
        _try = 1
        while _try <= max_tries:
            try:
                self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

                _sock = self.writer.get_extra_info("socket")
                _sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                _sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
                keep_cnt = 9 if sys.platform != "win32" else 10
                _sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, keep_cnt)
                if sys.platform != 'darwin':
                    _sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)

                return
            except (IOError, asyncio.TimeoutError):
                pass
            await asyncio.sleep(1.0)
            _try += 1
        raise ConnectionError(f'Can not get connection to {self.host}:{self.port}')

    async def disconnect(self):
        if not self.connected:
            return
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except:     # noqa
            pass
        self.writer = None
        self.reader = None
