"""S2 — India-VIX regime conditional momentum.

Pre-registered: research/preregistration.md §S2.
DO NOT modify after first backtest run.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class S2Params:
    mom_lookback: int  # 5, 10, 20
    hold_days: int  # 3, 5
    vix_low_pct: float  # 20, 30
    vix_high_pct: float  # 70, 80

    @classmethod
    def grid(cls) -> list["S2Params"]:
        return [
            cls(mom_lookback=m, hold_days=h, vix_low_pct=lo, vix_high_pct=hi)
            for m in (5, 10, 20)
            for h in (3, 5)
            for lo in (20.0, 30.0)
            for hi in (70.0, 80.0)
        ]


def make_signal(params: S2Params, vix_df: pd.DataFrame):
    """Return signal_fn(date, nifty_history) -> next-bar position.

    Holds the position for `hold_days` after entry. Re-evaluates on bar after
    hold expires.
    """
    state = {"hold": 0, "pos": 0.0}

    def _fn(date: pd.Timestamp, history: pd.DataFrame) -> float:
        if state["hold"] > 0:
            state["hold"] -= 1
            return state["pos"]

        if len(history) < 252:
            return 0.0
        if date not in vix_df.index:
            return 0.0

        # trailing 252d VIX, percentile of latest
        vix_trail = vix_df.loc[vix_df.index <= date]["Close"].iloc[-252:]
        if len(vix_trail) < 252:
            return 0.0
        vix_today = vix_trail.iloc[-1]
        vix_pct = (vix_trail <= vix_today).mean() * 100.0

        prior_ret = float(
            history["Close"].iloc[-1] / history["Close"].iloc[-params.mom_lookback - 1] - 1.0
        )

        target = 0.0
        if vix_pct < params.vix_low_pct and prior_ret > 0:
            target = +1.0
        elif vix_pct > params.vix_high_pct and prior_ret > 0:
            target = -1.0

        if target != 0.0:
            state["hold"] = params.hold_days - 1
            state["pos"] = target
        return target

    return _fn
