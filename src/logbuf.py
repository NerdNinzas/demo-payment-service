"""Ring buffer of recent service log lines, exposed at /logs for observers."""
import time
from collections import deque

_buf: deque[dict] = deque(maxlen=200)


def log(level: str, msg: str) -> None:
    _buf.append({"ts": time.time(), "level": level, "msg": msg})


def recent(limit: int = 50) -> list[dict]:
    return list(_buf)[-limit:]
