from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any


class AuditLog:
    """Append-only JSONL log. Day-one shape compatible with SEBI's 5-year
    retail-algo audit requirement (2026-04-01 framework).

    Every order, signal, kill-switch trip, broker response, and model call
    must land here. Never delete. Rotate by month; keep 60 months.
    """

    def __init__(self, dir: str | Path = "audit_logs"):
        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _path(self, ts: datetime) -> Path:
        return self.dir / f"{ts.strftime('%Y-%m')}.jsonl"

    def write(self, kind: str, payload: dict[str, Any]) -> None:
        ts = datetime.now(timezone.utc)
        record = {"ts": ts.isoformat(), "kind": kind, "payload": payload}
        line = json.dumps(record, default=str, ensure_ascii=False)
        with self._lock, self._path(ts).open("a", encoding="utf-8") as f:
            f.write(line + "\n")
