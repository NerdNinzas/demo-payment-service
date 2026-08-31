"""Upstream card-network gateway (simulated)."""
import asyncio
import random


class GatewayTimeout(Exception):
    pass


async def charge(amount_cents: int) -> str:
    await asyncio.sleep(0.05)
    if random.random() < 0.08:
        raise GatewayTimeout("card network timeout")
    return f"ch_{random.randint(10**9, 10**10)}"
