"""Tiny fake DB layer with a bounded connection pool."""
import asyncio

POOL_SIZE = 20
_pool = asyncio.Semaphore(POOL_SIZE)
in_use = 0


class Connection:
    async def execute(self, query: str) -> dict:
        await asyncio.sleep(0.02)
        return {"ok": True, "query": query}


async def acquire() -> Connection:
    global in_use
    await _pool.acquire()
    in_use += 1
    return Connection()


def release(_: Connection) -> None:
    global in_use
    in_use -= 1
    _pool.release()
