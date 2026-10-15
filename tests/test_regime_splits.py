from datetime import datetime

import numpy as np
import pandas as pd

from agent_trader.validation import partition_regimes


def _synthetic_prices() -> pd.Series:
    rng = np.random.default_rng(0)
    idx = pd.date_range("2018-01-01", "2026-04-30", freq="B")
    rets = rng.normal(0, 0.01, size=len(idx))
    # Inject a bear period
    bear_mask = (idx >= "2022-01-01") & (idx <= "2022-09-30")
    rets[bear_mask] -= 0.005
    # Inject a shock day
    shock_idx = idx.get_loc(pd.Timestamp("2020-03-23"))
    rets[shock_idx] = -0.10
    return pd.Series(np.exp(rets.cumsum()) * 1000, index=idx)


def test_partition_returns_windows():
    p = _synthetic_prices()
    windows = partition_regimes(p)
    kinds = {w.kind for w in windows}
    assert "shock" in kinds
    assert "bear" in kinds
    assert "calm" in kinds


def test_partition_forces_post_cutoff():
    p = _synthetic_prices()
    windows = partition_regimes(p, require_post_cutoff=datetime(2025, 1, 1))
    has_post = any(w.start >= datetime(2025, 1, 1) for w in windows)
    assert has_post
