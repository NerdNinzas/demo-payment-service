from src import db, gateway


async def process_payment(amount_cents: int) -> dict:
    conn = await db.acquire()
    try:
        charge_id = await gateway.charge(amount_cents)
        await conn.execute(f"INSERT INTO payments (charge_id, amount) VALUES ('{charge_id}', {amount_cents})")
        return {"status": "succeeded", "charge_id": charge_id}
    finally:
        db.release(conn)
