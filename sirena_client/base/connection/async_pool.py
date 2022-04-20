import collections
from typing import Union, Set
from .async_connection import AsyncConnection

import asyncio
import sys

from asyncio.locks import Lock as _Lock


class Lock(_Lock):

    """
    Fixes an issue with all Python versions that leaves pending waiters
    without being awakened when the first waiter is canceled.
    Code adapted from the PR https://github.com/python/cpython/pull/1031
    Waiting once it is merged to make a proper condition to relay on
    the stdlib implementation or this one patched
    """

    # NB: hacks
    if sys.version_info < (3, 7, 0):
        async def acquire(self):
            """Acquire a lock.
            This method blocks until the lock is unlocked, then sets it to
            locked and returns True.
            """
            if not self._locked and all(w.cancelled() for w in self._waiters):
                self._locked = True
                return True

            fut = self._loop.create_future()

            self._waiters.append(fut)
            try:
                await fut
                self._locked = True
                return True
            except asyncio.CancelledError:
                if not self._locked:  # pragma: no cover
                    self._wake_up_first()
                raise
            finally:
                self._waiters.remove(fut)

        def _wake_up_first(self):
            """Wake up the first waiter who isn't cancelled."""
            for fut in self._waiters:
                if not fut.done():
                    fut.set_result(True)
                    break


class CloseEvent:
    def __init__(self, on_close):
        self._close_init = asyncio.Event()
        self._close_done = asyncio.Event()
        self._on_close = on_close

    async def wait(self):
        await self._close_init.wait()
        await self._close_done.wait()

    def is_set(self):
        return self._close_done.is_set() or self._close_init.is_set()

    def set(self):
        if self._close_init.is_set():
            return

        task = asyncio.ensure_future(self._on_close())
        task.add_done_callback(self._cleanup)
        self._close_init.set()

    def _cleanup(self, task):
        self._on_close = None
        self._close_done.set()


class _AsyncConnectionContextManager:

    __slots__ = ('_pool', '_conn')

    def __init__(self, pool):
        self._pool = pool
        self._conn = None

    async def __aenter__(self):
        conn = await self._pool.acquire()
        self._conn = conn
        return self._conn

    async def __aexit__(self, exc_type, exc_value, tb):
        try:
            await self._pool.release(self._conn)
        finally:
            self._pool = None
            self._conn = None


class AsyncConnectionPool:

    def __init__(
            self,
            host: str,
            port: Union[str, int],
            min_size: int = 2,
            max_size: int = 4,
            **kwargs,
    ):
        self.host = host
        self.port = port

        self.min_size = min_size
        self.max_size = max_size

        self._pool: collections.deque[AsyncConnection] = collections.deque(maxlen=max_size)
        self._used: Set[AsyncConnection] = set()
        self._acquiring: int = 0
        self._cond = asyncio.Condition(lock=Lock())
        self._close_state = CloseEvent(self._do_close)

    def __repr__(self):
        return f"Pool size: {self.size}, Free size: {self.free_size}, Closed: {self._closed}"

    @property
    def free_size(self):
        return len(self._pool)

    @property
    def size(self):
        """Current pool size."""
        return self.free_size + len(self._used) + self._acquiring

    @property
    def _closed(self):
        """
        True if pool is closed.
        NB: protected property to match sync socket interface
        """
        return self._close_state.is_set()

    async def wait_closed(self):
        """Wait until pool gets closed."""
        await self._close_state.wait()

    async def _create_new_connection(self) -> AsyncConnection:
        conn = AsyncConnection(self.host, self.port)
        await conn.connect()
        return conn

    async def clear(self):
        async with self._cond:
            await self._do_clear()

    async def close(self):
        if not self._close_state.is_set():
            self._close_state.set()

    async def _do_clear(self):
        waiters = []
        while self._pool:
            conn = self._pool.popleft()
            waiters.append(conn.disconnect())
        await asyncio.gather(*waiters)

    async def _do_close(self):
        async with self._cond:
            assert not self._acquiring, self._acquiring
            waiters = []
            while self._pool:
                conn = self._pool.popleft()
                waiters.append(conn.disconnect())
            for conn in self._used:
                waiters.append(conn.disconnect())
            await asyncio.gather(*waiters)

    def _drop_closed(self):
        for i in range(self.free_size):
            conn = self._pool[0]
            if not conn.connected:
                self._pool.popleft()
            else:
                self._pool.rotate(-1)

    async def fill_free(self):
        self._drop_closed()
        while self.size < self.min_size:
            self._acquiring += 1
            try:
                conn = await self._create_new_connection()
                # TODO чё-нибудь писануть в стрим, чтоб проверить?
                self._pool.append(conn)
            finally:
                self._acquiring -= 1
                self._drop_closed()
        if self.free_size:
            return

    async def acquire(self) -> AsyncConnection:
        if self._closed:
            raise Exception("Pool is closed")
        async with self._cond:
            if self._closed:
                raise Exception("Pool is closed")
            while True:
                await self.fill_free()
                if self.free_size:
                    conn = self._pool.popleft()
                    assert conn.connected, conn
                    assert conn not in self._used, (conn, self._used)
                    self._used.add(conn)
                    return conn
                else:
                    await self._cond.wait()

    async def release(self, c: AsyncConnection):
        assert c in self._used, ("Invalid connection, maybe from other pool", c)
        self._used.remove(c)
        self._pool.append(c)
        # Не отключаем соединение, просто возвращаем его обратно в пул
        # TODO нужно как-нибудь проверять переодически соединения
        #   health check/heartbeat
        # if c.connected:
        #     await c.disconnect()
        asyncio.ensure_future(self._wakeup())

    async def _wakeup(self, closing_conn=None):
        async with self._cond:
            self._cond.notify()
        if closing_conn is not None:
            await closing_conn.wait_closed()

    def get(self):
        """
        async with pool.get() as conn:
            await conn.read()
            await conn.write()
        """
        return _AsyncConnectionContextManager(self)
