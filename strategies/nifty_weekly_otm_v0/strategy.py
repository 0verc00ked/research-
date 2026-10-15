"""First hypothesis: NIFTY weekly OTM option BUY gated by LLM regime+event.

This is intentionally a stub at scaffold time. The shape compiles, the
interface is honored, and the smoke test exercises it with synthetic bars.
Real signal logic lands after G0 gate criteria are encoded in the backtest
runner and the V-9 contamination probes have run on the chosen model.
"""
from __future__ import annotations

from collections.abc import Sequence

from agent_trader.core.strategy import Strategy
from agent_trader.core.types import Bar, Decision, Position, Regime, Signal


class NiftyWeeklyOtmV0(Strategy):
    name = "nifty_weekly_otm_v0"

    def __init__(self, min_conviction: float = 0.6):
        self.min_conviction = min_conviction

    def on_bar(
        self,
        bars: Sequence[Bar],
        signals: Sequence[Signal],
        positions: Sequence[Position],
    ) -> Decision:
        if not signals:
            return Decision(reasoning="no signal yet")
        latest = signals[-1]
        if latest.role == "disabled":
            return Decision(reasoning="LLM disabled by V-9 outcome; rule-only mode TBD")
        if latest.conviction < self.min_conviction:
            return Decision(reasoning=f"conviction {latest.conviction} < {self.min_conviction}")
        if latest.regime not in (Regime.BULL_TREND, Regime.BEAR_TREND, Regime.HIGH_VOL):
            return Decision(reasoning=f"regime {latest.regime} not tradable in v0")
        # Order construction lands once the option-chain + sizing module exists.
        return Decision(reasoning="would trade; order construction TBD")
