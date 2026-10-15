"""Intraday price fetcher + post-disclosure reaction computer.

Strategy: one yfinance fetch per ticker for the full window (cheap), then
look up bars by timestamp locally. Avoids N×M = 100×10000 individual fetches.

yfinance 60m bars are reliable for the last ~730 days. We default to 60m
which is sufficient resolution to answer "is the absorption window in our
LLM-latency strike zone?" Sub-hour resolution would need a paid source.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf


@dataclass
class PriceReaction:
    ticker: str
    disclosure_ts_utc: datetime
    price_at_disclosure: float
    ret_1h: float          # over next 1 bar (~60m)
    ret_2h: float          # over next 2 bars
    ret_4h: float          # over next 4 bars
    ret_eod_next: float    # close-to-close: bar containing disclosure → next session close
    abs_eod_next: float    # magnitude
    n_bars_available_after: int


def fetch_intraday_history(
    ticker: str,
    start: datetime,
    end: datetime,
    *,
    interval: str = "60m",
    cache_dir: Path | str = "data_cache/intraday",
) -> pd.DataFrame:
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    cache_file = cache / f"{ticker.replace('.', '_')}_{start.date()}_{end.date()}_{interval}.csv"
    if cache_file.exists():
        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
    else:
        df = yf.download(
            ticker,
            start=start,
            end=end,
            interval=interval,
            progress=False,
            auto_adjust=False,
            prepost=False,
        )
        if df is None or df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.to_csv(cache_file)
    df.index = pd.to_datetime(df.index, utc=True)
    return df


def compute_reaction(
    bars: pd.DataFrame, disclosure_ts_utc: datetime
) -> PriceReaction | None:
    if bars.empty:
        return None
    ts = pd.Timestamp(disclosure_ts_utc)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    # nearest bar at or after disclosure
    later = bars.index[bars.index >= ts]
    if len(later) == 0:
        return None
    bar_at = later[0]
    bar_idx = bars.index.get_loc(bar_at)
    if not isinstance(bar_idx, int):
        # if a slice came back, take the first
        bar_idx = int(np.array(bar_idx).min())
    p0 = float(bars["Close"].iloc[bar_idx])
    if p0 <= 0 or not np.isfinite(p0):
        return None

    def _ret(offset: int) -> float:
        if bar_idx + offset >= len(bars):
            return float("nan")
        p = float(bars["Close"].iloc[bar_idx + offset])
        if not np.isfinite(p) or p <= 0:
            return float("nan")
        return p / p0 - 1.0

    ret_1 = _ret(1)
    ret_2 = _ret(2)
    ret_4 = _ret(4)

    # EOD next session: find the close of the bar that is in the next trading day
    ts_date = bar_at.normalize()
    next_session = bars.index[bars.index.normalize() > ts_date]
    if len(next_session) == 0:
        ret_eod = float("nan")
    else:
        last_next_day = next_session[next_session.normalize() == next_session[0].normalize()][-1]
        p_eod = float(bars.loc[last_next_day, "Close"])
        ret_eod = p_eod / p0 - 1.0 if p_eod > 0 else float("nan")

    return PriceReaction(
        ticker=str(bars.attrs.get("ticker", "?")),
        disclosure_ts_utc=disclosure_ts_utc,
        price_at_disclosure=p0,
        ret_1h=ret_1,
        ret_2h=ret_2,
        ret_4h=ret_4,
        ret_eod_next=ret_eod,
        abs_eod_next=abs(ret_eod) if np.isfinite(ret_eod) else float("nan"),
        n_bars_available_after=int(len(bars) - bar_idx - 1),
    )
