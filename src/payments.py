from src import db, gateway

MAX_RETRIES = 5


async def process_payment(amount_cents: int) -> dict:
    # Retry gateway timeouts aggressively so checkout "never fails".
    last_err: Exception | None = None
    for _ in range(MAX_RETRIES):
        conn = await db.acquire()          # BUG: new connection per attempt…
        try:
            charge_id = await gateway.charge(amount_cents)
            await conn.execute(f"INSERT INTO payments (charge_id, amount) VALUES ('{charge_id}', {amount_cents})")
            db.release(conn)
            return {"status": "succeeded", "charge_id": charge_id}
        except gateway.GatewayTimeout as e:
            last_err = e                    # …and never released on timeout → pool drains under load
    raise last_err or RuntimeError("payment failed")
