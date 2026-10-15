from agent_trader.portfolio import kelly_optimal, kelly_size


def test_kelly_optimal_basic():
    assert kelly_optimal(0.001, 0.0001) == 10.0


def test_kelly_optimal_zero_variance():
    assert kelly_optimal(0.001, 0.0) == 0.0


def test_kelly_size_long_only_blocks_negative_mu():
    assert kelly_size(-0.001, 0.0001, frac=0.1, max_exposure=0.5) == 0.0


def test_kelly_size_capped():
    # μ/σ² = 50; frac 0.1 → 5; cap should bring to 0.5
    assert kelly_size(0.005, 0.0001, frac=0.1, max_exposure=0.5) == 0.5


def test_kelly_size_uncapped_at_normal_range():
    # μ/σ² = 0.0005/0.0001 = 5; frac 0.1 → 0.5 — right at cap
    assert abs(kelly_size(0.0005, 0.0001, frac=0.1, max_exposure=0.5) - 0.5) < 1e-12
    # μ/σ² = 0.00001/0.0001 = 0.1; frac 0.1 → 0.01 — under cap
    assert abs(kelly_size(0.00001, 0.0001, frac=0.1, max_exposure=0.5) - 0.01) < 1e-12


def test_kelly_size_allows_short_when_not_long_only():
    f = kelly_size(-0.001, 0.0001, frac=0.1, max_exposure=0.5, long_only=False)
    assert f < 0
    assert f >= -0.5
