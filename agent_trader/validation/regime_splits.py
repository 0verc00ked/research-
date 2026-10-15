"""Partition a price/return series into regime windows.

Gate: any backtest must show results across at least one bear, one calm, and
one shock window, AND at least one window after 2025-01-01 (post-LLM-cutoff).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

import numpy as np
import pandas as pd

RegimeKind = Literal["bear", "calm", "shock", "other"]


@dataclass
class RegimeWindow:
    kind: RegimeKind
    start: datetime
    end: datetime
    note: str = ""


def partition_regimes(
    prices: pd.Series,
    *,
    bear_dd_threshold: float = 0.15,
    calm_rv_percentile: float = 25.0,
    shock_jump_sigma: float = 4.0,
    window_days: int = 30,
    require_post_cutoff: datetime = datetime(2025, 1, 1),
) -> list[RegimeWindow]:
    """Heuristic but defensible partition.

    - bear: rolling 60-day drawdown > threshold
    - calm: 30-day realized vol below the calm_rv_percentile of full history
    - shock: any day with |return| > shock_jump_sigma * trailing 60-day std
    Returns disjoint windows of `window_days` length anchored on the trigger.
    """
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("prices must have a DatetimeIndex")
    prices = prices.sort_index()
    rets = prices.pct_change().dropna()
    rolling_max = prices.rolling(60, min_periods=10).max()
    dd = (prices / rolling_max - 1.0).abs()
    rv = rets.rolling(30, min_periods=10).std() * np.sqrt(252)
    trail_std = rets.rolling(60, min_periods=10).std()

    bear_trigger = dd > bear_dd_threshold
    calm_threshold = np.nanpercentile(rv.dropna(), calm_rv_percentile)
    calm_trigger = rv < calm_threshold
    shock_trigger = rets.abs() > shock_jump_sigma * trail_std

    windows: list[RegimeWindow] = []
    occupied = pd.Series(False, index=prices.index)
    half = pd.Timedelta(days=window_days // 2)

    def take(kind: RegimeKind, trig: pd.Series, note: str) -> None:
        for ts in trig[trig].index:
            if occupied.loc[ts]:
                continue
            lo, hi = ts - half, ts + half
            sub = prices.loc[lo:hi]
            if len(sub) < 5:
                continue
            windows.append(
                RegimeWindow(kind=kind, start=sub.index[0].to_pydatetime(), end=sub.index[-1].to_pydatetime(), note=note)
            )
            occupied.loc[lo:hi] = True

    take("shock", shock_trigger, f">{shock_jump_sigma}σ daily move")
    take("bear", bear_trigger, f"60d DD > {bear_dd_threshold:.0%}")
    take("calm", calm_trigger, f"30d RV < P{calm_rv_percentile:.0f}")

    has_post = any(w.start >= require_post_cutoff for w in windows)
    if not has_post and len(prices) > 0 and prices.index[-1] >= require_post_cutoff:
        last = prices.index[-1].to_pydatetime()
        windows.append(
            RegimeWindow(
                kind="other",
                start=(prices.index[-1] - pd.Timedelta(days=window_days)).to_pydatetime(),
                end=last,
                note=f"forced post-cutoff window (>={require_post_cutoff.date()})",
            )
        )

    return windows
