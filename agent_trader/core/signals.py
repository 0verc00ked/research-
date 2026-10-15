from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from threading import Lock

from .types import Signal


class SignalStore:
    """Append-only JSONL store. Analyst writes, strategy reads.

    Append-only because the audit trail is a SEBI requirement and because
    strategies must be able to replay deterministically.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def append(self, signal: Signal) -> None:
        line = signal.model_dump_json()
        with self._lock, self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def read_all(self) -> list[Signal]:
        if not self.path.exists():
            return []
        out: list[Signal] = []
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                out.append(Signal.model_validate(json.loads(line)))
        return out

    def read_since(self, ts: datetime) -> Iterator[Signal]:
        for s in self.read_all():
            if s.ts >= ts:
                yield s
