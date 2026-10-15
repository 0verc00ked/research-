"""Feature engineering for HMM regime input.

We feed the HMM a low-dimensional but informative feature vector per day:
  - log return (signed) — captures direction
  - 20d realized vol — captures vol regime
  - VIX level (normalized z-score) — forward-looking vol expectation
  - 20d return autocorr(1) — captures trend persistence vs mean-reversion

Standardization is fit on training data only (no lookahead).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class FeatureScaler:
    mean: np.ndarray
    std: np.ndarray

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mean) / np.where(self.std > 0, self.std, 1.0)


def build_features(
    nifty_close: pd.Series, vix_close: pd.Series, *, lookback: int = 20
) -> tuple[pd.DataFrame, pd.DatetimeIndex]:
    """Build aligned feature matrix. NaN-rows from initial lookback are dropped."""
    common = nifty_close.index.intersection(vix_close.index)
    n = nifty_close.loc[common].sort_index()
    v = vix_close.loc[common].sort_index()
    log_ret = np.log(n / n.shift(1))
    rv = log_ret.rolling(lookback).std() * np.sqrt(252)
    vix_z = (v - v.rolling(252, min_periods=60).mean()) / v.rolling(252, min_periods=60).std()
    autocorr = log_ret.rolling(lookback).apply(
        lambda x: float(pd.Series(x).autocorr(lag=1)) if pd.Series(x).std() > 0 else 0.0,
        raw=False,
    )
    df = pd.DataFrame({
        "log_ret": log_ret,
        "rv20": rv,
        "vix_z": vix_z,
        "autocorr20": autocorr,
    }).dropna()
    return df, df.index


def fit_scaler(X: np.ndarray) -> FeatureScaler:
    return FeatureScaler(mean=X.mean(axis=0), std=X.std(axis=0))
