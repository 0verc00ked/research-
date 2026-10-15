"""Minimal daily-bar backtester.

Intentionally tiny. nautilus_trader replaces this when a strategy survives W9.

Contract:
  - You give a `signal_fn(date, history) -> position` that returns +1/0/-1
    (or fractional) for the bar's *opening* position.
  - Returns are computed as position × close-to-close return of underlying,
    minus per-trade transaction costs charged at each position change.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    returns: np.ndarray  # per-bar strategy returns
    positions: np.ndarray  # per-bar positions
    n_trades: int  # round-trip count
    equity_curve: np.ndarray
    dates: pd.DatetimeIndex
    annual_sharpe: float = 0.0

    @property
    def total_return(self) -> float:
        return float(self.equity_curve[-1] / self.equity_curve[0] - 1.0) if len(self.equity_curve) else 0.0


SignalFn = Callable[[pd.Timestamp, pd.DataFrame], float]


def run_daily(
    underlying: pd.DataFrame,
    signal_fn: SignalFn,
    *,
    cost_per_side: float = 0.0005,  # 5 bps per side
    warmup: int = 60,  # bars before first signal
) -> BacktestResult:
    """`underlying` indexed by date with at least a 'Close' column.

    `signal_fn(date, history)` is called for each bar t. `history` is the
    underlying truncated to bars [0..t] inclusive (T0 lookahead-safe). It
    returns the desired position *for the next bar* (i.e., applied at t+1's
    open-to-close return — we approximate as close-to-close of t+1).
    """
    close = underlying["Close"].to_numpy()
    dates = underlying.index
    n = len(close)
    positions = np.zeros(n)
    returns = np.zeros(n)

    for t in range(warmup, n - 1):
        history = underlying.iloc[: t + 1]
        pos = signal_fn(dates[t], history)
        positions[t + 1] = pos

    # close-to-close pct change for the underlying, multiplied by position held
    pct = np.zeros(n)
    pct[1:] = close[1:] / close[:-1] - 1.0
    raw = positions * pct

    # cost on each position change
    pos_change = np.abs(np.diff(positions, prepend=0.0))
    costs = pos_change * cost_per_side
    returns = raw - costs

    n_trades = int((pos_change > 0).sum())
    equity = np.cumprod(1.0 + returns)

    sharpe = 0.0
    if returns.std(ddof=1) > 0:
        sharpe = float(returns.mean() / returns.std(ddof=1) * np.sqrt(252))

    return BacktestResult(
        returns=returns,
        positions=positions,
        n_trades=n_trades,
        equity_curve=equity,
        dates=dates,
        annual_sharpe=sharpe,
    )


def run_pair_daily(
    asset_a: pd.DataFrame,
    asset_b: pd.DataFrame,
    signal_fn: Callable[[pd.Timestamp, pd.DataFrame, pd.DataFrame], float],
    *,
    cost_per_side: float = 0.0005,
    warmup: int = 60,
) -> BacktestResult:
    """Pair backtest. signal_fn returns +1 = long A short B, -1 = inverse.

    Per-bar return = position * (return_A - return_B); costs charged on both
    legs at each position change.
    """
    # align on common dates
    common = asset_a.index.intersection(asset_b.index)
    a = asset_a.loc[common, ["Close"]].rename(columns={"Close": "A"})
    b = asset_b.loc[common, ["Close"]].rename(columns={"Close": "B"})
    df = a.join(b)
    close_a = df["A"].to_numpy()
    close_b = df["B"].to_numpy()
    dates = df.index
    n = len(df)
    positions = np.zeros(n)

    for t in range(warmup, n - 1):
        history = df.iloc[: t + 1]
        # signal_fn expects (date, hist_a, hist_b)
        pos = signal_fn(dates[t], history[["A"]].rename(columns={"A": "Close"}), history[["B"]].rename(columns={"B": "Close"}))
        positions[t + 1] = pos

    pct_a = np.zeros(n)
    pct_b = np.zeros(n)
    pct_a[1:] = close_a[1:] / close_a[:-1] - 1.0
    pct_b[1:] = close_b[1:] / close_b[:-1] - 1.0
    raw = positions * (pct_a - pct_b)

    pos_change = np.abs(np.diff(positions, prepend=0.0))
    costs = pos_change * cost_per_side * 2  # both legs
    returns = raw - costs

    n_trades = int((pos_change > 0).sum())
    equity = np.cumprod(1.0 + returns)
    sharpe = float(returns.mean() / returns.std(ddof=1) * np.sqrt(252)) if returns.std(ddof=1) > 0 else 0.0

    return BacktestResult(
        returns=returns,
        positions=positions,
        n_trades=n_trades,
        equity_curve=equity,
        dates=dates,
        annual_sharpe=sharpe,
    )
