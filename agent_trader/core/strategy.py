from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from .types import Bar, Decision, Position, Signal


class Strategy(ABC):
    """Single interface used identically by backtest, paper, and live.

    Backtest-to-live parity is non-negotiable. If a strategy needs to do
    something the backtest can't simulate, it doesn't go live.
    """

    name: str

    @abstractmethod
    def on_bar(
        self,
        bars: Sequence[Bar],
        signals: Sequence[Signal],
        positions: Sequence[Position],
    ) -> Decision: ...

    def on_start(self) -> None:
        """Optional. Called once before the first on_bar."""

    def on_stop(self, reason: str) -> None:
        """Optional. Called on kill-switch, market close, or graceful shutdown."""
