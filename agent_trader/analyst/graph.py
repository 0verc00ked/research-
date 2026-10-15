from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ..core.types import Regime, Signal
from .memory import LayeredMemory


class LLMClient(Protocol):
    def generate(self, prompt: str, system: str = "") -> str: ...


class AnalystGraph:
    """TradingAgents-style debate graph (stub).

    Role is set per V-9 contamination-probe outcome:
      - "forecast": all probes clean
      - "regime_only": mild contamination (default per SYNTHESIS.md §5)
      - "disabled": probe disqualified; no LLM in signal path
    """

    def __init__(
        self,
        client: LLMClient | None = None,
        memory: LayeredMemory | None = None,
        role: str = "regime_only",
        model: str = "stub",
    ):
        self.client = client
        self.memory = memory or LayeredMemory()
        self.role = role
        self.model = model

    def run(self, context: dict, ts: datetime) -> Signal:
        if self.role == "disabled" or self.client is None:
            return Signal(ts=ts, role="disabled", model=self.model, notes="LLM disabled")
        # TODO: real multi-agent debate. For now: deterministic stub.
        return Signal(
            ts=ts,
            regime=Regime.UNKNOWN,
            conviction=0.0,
            event_flags=[],
            notes="stub graph; wire real debate after V-9 probes pass",
            model=self.model,
            role=self.role,
        )
