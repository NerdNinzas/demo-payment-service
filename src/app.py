import asyncio

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from src import db, gateway, logbuf, metrics
from src.payments import process_payment
from src import statuspage

app = FastAPI(title="demo-payment-service")


@app.get("/", response_class=HTMLResponse)
def status_page():
    return statuspage.html()


@app.get("/health")
def health():
    util = round(100 * db.in_use / db.POOL_SIZE, 1)
    return {"ok": True, "db_connections_in_use": db.in_use, "pool_size": db.POOL_SIZE,
            "db_connection_utilization": util, **metrics.snapshot()}


@app.get("/logs")
def logs(limit: int = 50):
    return {"logs": logbuf.recent(limit)}


@app.post("/pay")
async def pay(amount_cents: int = 1999):
    try:
        result = await asyncio.wait_for(process_payment(amount_cents), timeout=4)
        metrics.record(True)
        return result
    except asyncio.TimeoutError:
        metrics.record(False)
        logbuf.log("ERROR", f"payment timed out waiting for a DB connection (pool {db.in_use}/{db.POOL_SIZE})")
        raise HTTPException(503, "timeout acquiring database connection — pool exhausted?")
    except gateway.GatewayTimeout:
        metrics.record(False)
        logbuf.log("ERROR", "card gateway timeout after retries")
        raise HTTPException(504, "gateway timeout")
