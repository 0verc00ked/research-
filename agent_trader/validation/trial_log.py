"""Append-only SQLite registry of every backtest trial.

The `n_trials_for(strategy_name)` count is the load-bearing number for DSR:
every parameter sweep, every prompt re-roll, every hypothesis tweak increments
it. Lying here defeats the entire harness.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any

_SCHEMA = """
CREATE TABLE IF NOT EXISTS trial (
    trial_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts              TEXT NOT NULL,
    strategy_name   TEXT NOT NULL,
    code_hash       TEXT NOT NULL,
    params_json     TEXT NOT NULL,
    dataset_hash    TEXT NOT NULL,
    metrics_json    TEXT NOT NULL,
    gates_json      TEXT NOT NULL,
    verdict         TEXT NOT NULL,
    notes           TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_strategy ON trial(strategy_name);
"""


@dataclass
class TrialRecord:
    strategy_name: str
    code_hash: str
    params: dict[str, Any]
    dataset_hash: str
    metrics: dict[str, Any]
    gates: dict[str, Any]
    verdict: str  # "PASS" | "FAIL" | "INCONCLUSIVE"
    notes: str = ""
    trial_id: int | None = None
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def hash_code(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()[:16]


def hash_dataset(*parts: bytes | str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8") if isinstance(p, str) else p)
    return h.hexdigest()[:16]


class TrialLog:
    def __init__(self, path: str | Path = "trial_log.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, isolation_level=None)

    def record(self, rec: TrialRecord) -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO trial
                (ts, strategy_name, code_hash, params_json, dataset_hash,
                 metrics_json, gates_json, verdict, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    rec.ts,
                    rec.strategy_name,
                    rec.code_hash,
                    json.dumps(rec.params, default=str, sort_keys=True),
                    rec.dataset_hash,
                    json.dumps(rec.metrics, default=str),
                    json.dumps(rec.gates, default=str),
                    rec.verdict,
                    rec.notes,
                ),
            )
            return cur.lastrowid  # type: ignore[return-value]

    def n_trials_for(self, strategy_name: str) -> int:
        with self._lock, self._connect() as conn:
            (n,) = conn.execute(
                "SELECT COUNT(*) FROM trial WHERE strategy_name = ?", (strategy_name,)
            ).fetchone()
            return int(n)

    def all_for(self, strategy_name: str) -> list[TrialRecord]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                """SELECT trial_id, ts, strategy_name, code_hash, params_json,
                          dataset_hash, metrics_json, gates_json, verdict, notes
                   FROM trial WHERE strategy_name = ? ORDER BY trial_id ASC""",
                (strategy_name,),
            ).fetchall()
        return [
            TrialRecord(
                trial_id=r[0],
                ts=r[1],
                strategy_name=r[2],
                code_hash=r[3],
                params=json.loads(r[4]),
                dataset_hash=r[5],
                metrics=json.loads(r[6]),
                gates=json.loads(r[7]),
                verdict=r[8],
                notes=r[9],
            )
            for r in rows
        ]
