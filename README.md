# PayFlow — Payment Service

A lightweight payment-processing API for PayFlow, built with FastAPI.
Handles card charges through the upstream gateway with a bounded database
connection pool, exposes health telemetry, and serves a public status page.

## Endpoints

| Method | Path       | Description                                   |
|--------|------------|-----------------------------------------------|
| GET    | `/`        | Public status page (live metrics + logs)      |
| GET    | `/health`  | Health + telemetry (success rate, pool usage) |
| GET    | `/logs`    | Recent service log lines                       |
| POST   | `/pay`     | Process a payment                              |

## Run locally

```bash
pip install -r requirements.txt
uvicorn src.app:app --reload --port 9000
```

Then open http://localhost:9000/ for the status page.

## Deploy

Configured for Render via `render.yaml` — connect the repo and it deploys
automatically on every push to `main`.

---
© NerdNinzas
