import numpy as np

from agent_trader.validation import combinatorial_purged_cv


def test_n_folds_default():
    rng = np.random.default_rng(0)
    r = rng.normal(0, 0.01, size=500)
    res = combinatorial_purged_cv(r, n_groups=8, k_test=2)
    # C(8, 2) = 28
    assert res.n_folds == 28


def test_consistent_positive_strategy():
    rng = np.random.default_rng(1)
    r = rng.normal(loc=0.002, scale=0.01, size=2000)
    res = combinatorial_purged_cv(r)
    assert res.folds_positive_ratio > 0.7
    assert res.mean_oos_sharpe > 1.0


def test_zero_edge_folds_around_half():
    rng = np.random.default_rng(99)
    r = rng.normal(loc=0.0, scale=0.01, size=2000)
    res = combinatorial_purged_cv(r)
    assert 0.3 < res.folds_positive_ratio < 0.7


def test_short_series_raises():
    import pytest

    with pytest.raises(ValueError):
        combinatorial_purged_cv(np.zeros(5))
