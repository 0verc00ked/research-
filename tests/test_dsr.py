import numpy as np

from agent_trader.validation import deflated_sharpe_ratio, expected_max_sharpe


def test_expected_max_grows_with_trials():
    em_low = expected_max_sharpe(1.0, n_trials=10)
    em_mid = expected_max_sharpe(1.0, n_trials=100)
    em_high = expected_max_sharpe(1.0, n_trials=1000)
    assert em_low < em_mid < em_high


def test_dsr_real_edge():
    """Strong real edge (Sharpe ~2 over many samples) should have DSR near 1."""
    rng = np.random.default_rng(42)
    n = 1000
    r = rng.normal(loc=0.001, scale=0.01, size=n)
    res = deflated_sharpe_ratio(r, n_trials=1)
    assert res.dsr > 0.95
    assert res.sharpe_observed > 0.5


def test_dsr_punishes_many_trials():
    """Same observed Sharpe, more trials → lower DSR."""
    rng = np.random.default_rng(7)
    n = 500
    r = rng.normal(loc=0.001, scale=0.01, size=n)
    dsr_1 = deflated_sharpe_ratio(r, n_trials=1).dsr
    dsr_100 = deflated_sharpe_ratio(r, n_trials=100).dsr
    dsr_1000 = deflated_sharpe_ratio(r, n_trials=1000).dsr
    assert dsr_1 > dsr_100 > dsr_1000


def test_dsr_zero_edge_low():
    rng = np.random.default_rng(123)
    r = rng.normal(loc=0.0, scale=0.01, size=500)
    res = deflated_sharpe_ratio(r, n_trials=100)
    assert res.dsr < 0.95
