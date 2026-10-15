"""S1 — Thursday (NIFTY weekly expiry) reversion.

Pre-registered: research/preregistration.md §S1.
DO NOT modify after first backtest run. Modifications = new N_trials.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

THURSDAY = 3  # Monday=0, Thursday=3


@dataclass(frozen=True)
class S1Params:
    prior_window: int  # 3, 5, 10, 15
    reversion_threshold: float  # 0.005, 0.01, 0.02

    @classmethod
    def grid(cls) -> list["S1Params"]:
        return [
            cls(prior_window=w, reversion_threshold=t)
            for w in (3, 5, 10, 15)
            for t in (0.005, 0.01, 0.02)
        ]


def make_signal(params: S1Params):
    """Return a signal_fn (date, history) -> position for the NEXT bar.

    Logic: on Thursday close, look at prior_window-day return; if > threshold,
    next-bar position = -1; if < -threshold, next-bar position = +1; else
    position = 0 (closing any existing).

    Hold for 2 bars (Friday + Monday) then back to 0 unless re-triggered.
    """
    held_remaining = {"n": 0, "pos": 0.0}

    def _fn(date: pd.Timestamp, history: pd.DataFrame) -> float:
        if held_remaining["n"] > 0:
            held_remaining["n"] -= 1
            return held_remaining["pos"]

        if date.weekday() != THURSDAY:
            return 0.0
        if len(history) < params.prior_window + 1:
            return 0.0
        ret = float(
            history["Close"].iloc[-1] / history["Close"].iloc[-params.prior_window - 1] - 1.0
        )
        if ret > params.reversion_threshold:
            held_remaining["n"] = 1  # hold Fri + Mon (signal applied at t+1)
            held_remaining["pos"] = -1.0
            return -1.0
        if ret < -params.reversion_threshold:
            held_remaining["n"] = 1
            held_remaining["pos"] = +1.0
            return +1.0
        return 0.0

    return _fn
