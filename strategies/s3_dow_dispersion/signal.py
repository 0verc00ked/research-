"""S3 — Day-of-week NIFTY vs BANKNIFTY dispersion.

Pre-registered: research/preregistration.md §S3.
DO NOT modify after first backtest run.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri")


@dataclass(frozen=True)
class S3Params:
    entry_day: int  # 0..4
    direction: int  # +1 = long_nifty/short_bnk, -1 = inverse
    hold_days: int  # 1, 2

    @classmethod
    def grid(cls) -> list["S3Params"]:
        return [
            cls(entry_day=d, direction=dr, hold_days=h)
            for d in range(5)
            for dr in (+1, -1)
            for h in (1, 2)
        ]


def make_signal(params: S3Params):
    """Pair signal_fn(date, nifty_hist, bnk_hist) -> next-bar pair position.

    +1 = long NIFTY, short BANKNIFTY (computed at entry_day close, applied
    over the next hold_days bars).
    """
    state = {"hold": 0, "pos": 0.0}

    def _fn(date: pd.Timestamp, hist_a: pd.DataFrame, hist_b: pd.DataFrame) -> float:
        if state["hold"] > 0:
            state["hold"] -= 1
            return state["pos"]

        if date.weekday() != params.entry_day:
            return 0.0
        state["hold"] = params.hold_days - 1
        state["pos"] = float(params.direction)
        return state["pos"]

    return _fn
