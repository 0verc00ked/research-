"""Thin yfinance loader for Indian indices. Daily bars only.

Caveats — all worth a T1 warning:
  - yfinance is unofficial; data quality varies. Verify spot-checks.
  - No survivorship correction on index constituents (we only use index level).
  - No corporate-action adjustment is exposed by yfinance for indices.
  - INTRADAY DATA IS NOT RELIABLE for >60 days — daily only here.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yfinance as yf

INDIAN_TICKERS = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "INDIAVIX": "^INDIAVIX",
    "SENSEX": "^BSESN",
    "NIFTYNEXT50": "^NSMIDCP",
}


@dataclass
class LoadedSeries:
    name: str
    ticker: str
    df: pd.DataFrame  # columns: Open, High, Low, Close, Volume
    fingerprint: str  # hash of (ticker, start, end, len) for dataset_hash


def _fingerprint(ticker: str, df: pd.DataFrame) -> str:
    if df.empty:
        return hashlib.sha256(ticker.encode()).hexdigest()[:16]
    h = hashlib.sha256()
    h.update(ticker.encode())
    h.update(str(df.index[0]).encode())
    h.update(str(df.index[-1]).encode())
    h.update(str(len(df)).encode())
    h.update(str(df["Close"].iloc[-1]).encode())
    return h.hexdigest()[:16]


def load(
    name_or_ticker: str,
    start: str = "2010-01-01",
    end: str | None = None,
    cache_dir: str | Path = "data_cache",
) -> LoadedSeries:
    ticker = INDIAN_TICKERS.get(name_or_ticker.upper(), name_or_ticker)
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    cache_file = cache / f"{ticker.replace('^', '_')}_{start}_{end or 'latest'}.csv"

    if cache_file.exists():
        df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
    else:
        raw = yf.download(
            ticker,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False,
        )
        if raw is None or raw.empty:
            raise RuntimeError(f"yfinance returned no data for {ticker}")
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.to_csv(cache_file)

    df = df.dropna(subset=["Close"])
    return LoadedSeries(
        name=name_or_ticker.upper(),
        ticker=ticker,
        df=df,
        fingerprint=_fingerprint(ticker, df),
    )


def load_many(names: list[str], **kwargs) -> dict[str, LoadedSeries]:
    return {n: load(n, **kwargs) for n in names}
