"""Prometheus-style counters (simplified)."""
payments_total = 0
payments_failed = 0


def record(success: bool) -> None:
    global payments_total, payments_failed
    payments_total += 1
    if not success:
        payments_failed += 1
    _recent.append(success)
    del _recent[:-200]


_recent: list[bool] = []


def snapshot() -> dict:
    # success rate over the most recent window so recovery is visible quickly
    window = _recent[-50:]
    rate = 100.0 if not window else round(100 * sum(window) / len(window), 1)
    return {"payments_total": payments_total, "payment_success_rate": rate}
