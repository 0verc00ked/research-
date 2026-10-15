from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class RiskLimits:
    """Hard caps. Any breach trips the kill-switch.

    Defaults track SYNTHESIS.md §6 kill-switch criteria.
    """
    max_drawdown_pct: float = 0.15
    max_consecutive_losses: int = 5
    max_monthly_burn_inr: Decimal = Decimal("4000")
    max_ops_per_sec: int = 10  # SEBI threshold; staying under avoids per-strategy registration
    max_position_pct_of_capital: float = 1.0


@dataclass
class RiskState:
    capital_inr: Decimal
    peak_capital_inr: Decimal
    consecutive_losses: int = 0
    month_burn_inr: Decimal = Decimal("0")
    breaches: list[str] = field(default_factory=list)
    tripped: bool = False

    @property
    def drawdown_pct(self) -> float:
        if self.peak_capital_inr <= 0:
            return 0.0
        return float((self.peak_capital_inr - self.capital_inr) / self.peak_capital_inr)


class KillSwitch:
    """Deterministic, no LLM. Checked before every order."""

    def __init__(self, limits: RiskLimits, state: RiskState):
        self.limits = limits
        self.state = state

    def check(self) -> list[str]:
        breaches: list[str] = []
        if self.state.drawdown_pct > self.limits.max_drawdown_pct:
            breaches.append(f"drawdown {self.state.drawdown_pct:.2%} > {self.limits.max_drawdown_pct:.2%}")
        if self.state.consecutive_losses >= self.limits.max_consecutive_losses:
            breaches.append(f"consec_losses {self.state.consecutive_losses} >= {self.limits.max_consecutive_losses}")
        if self.state.month_burn_inr > self.limits.max_monthly_burn_inr:
            breaches.append(f"month_burn ₹{self.state.month_burn_inr} > ₹{self.limits.max_monthly_burn_inr}")
        if breaches:
            self.state.tripped = True
            self.state.breaches = breaches
        return breaches

    def trip(self, reason: str) -> None:
        self.state.tripped = True
        self.state.breaches.append(reason)
