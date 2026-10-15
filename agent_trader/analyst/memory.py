from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class MemoryItem(BaseModel):
    ts: datetime
    kind: str
    payload: dict[str, Any]


class LayeredMemory:
    """FinMem-style layered memory: short / mid / long.

    Stub. Persistence layer (sqlite or DuckDB) will land when the analyst
    actually runs against a model. For now, in-memory deques.
    """

    def __init__(self, short_cap: int = 32, mid_cap: int = 256, long_cap: int = 2048):
        self.short: deque[MemoryItem] = deque(maxlen=short_cap)
        self.mid: deque[MemoryItem] = deque(maxlen=mid_cap)
        self.long: deque[MemoryItem] = deque(maxlen=long_cap)

    def write(self, item: MemoryItem, layer: str = "short") -> None:
        {"short": self.short, "mid": self.mid, "long": self.long}[layer].append(item)

    def recall(self, layer: str = "short") -> list[MemoryItem]:
        return list({"short": self.short, "mid": self.mid, "long": self.long}[layer])
