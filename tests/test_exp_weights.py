import math

import numpy as np

from agent_trader.portfolio import ExpWeights, ExpWeightsConfig


def _make(k=4, t_hint=252, b=0.05):
    return ExpWeights(ExpWeightsConfig(n_strategies=k, t_hint=t_hint, bound_b=b))


def test_initial_weights_uniform():
    e = _make(k=5)
    np.testing.assert_allclose(e.weights, np.full(5, 0.2))


def test_winner_takes_more_weight():
    rng = np.random.default_rng(0)
    e = _make(k=4, t_hint=252)
    for _ in range(252):
        r = rng.normal(0, 0.01, size=4)
        r[0] += 0.003  # strategy 0 has real edge
        e.allocate()
        e.observe(r)
    w = e.weights
    assert w[0] > 0.25, f"winner should exceed uniform; got {w}"
    assert w[0] == w.max(), f"winner should be the heaviest; got {w}"


def test_regret_bound_holds_empirically():
    """On any adversarial sequence with returns in [-B, B], empirical regret
    must stay under the theoretical bound."""
    rng = np.random.default_rng(42)
    T, K, B = 500, 5, 0.05
    e = ExpWeights(ExpWeightsConfig(n_strategies=K, t_hint=T, bound_b=B))
    for _ in range(T):
        # Adversarial: random permutation of fixed gain levels
        r = rng.choice([-B, -B / 2, 0, B / 2, B], size=K, replace=True)
        e.allocate()
        e.observe(r)
    reg = e.empirical_regret()
    bound = e.theoretical_regret_bound()
    assert reg <= bound + 1e-9, f"regret {reg} exceeds bound {bound}"


def test_weights_sum_to_one_always():
    rng = np.random.default_rng(7)
    e = _make(k=6)
    for _ in range(120):
        r = rng.normal(0, 0.02, size=6)
        e.allocate()
        e.observe(r)
        s = float(e.weights.sum())
        assert abs(s - 1.0) < 1e-9


def test_shape_mismatch_raises():
    import pytest

    e = _make(k=4)
    with pytest.raises(ValueError):
        e.observe(np.zeros(3))


def test_recovery_floor_keeps_losers_alive():
    """A strategy that loses badly for 100 days then becomes the best should
    still be reachable by Hedge (warmup_floor > 0)."""
    e = ExpWeights(ExpWeightsConfig(n_strategies=3, bound_b=0.05, warmup_floor=1e-3))
    for _ in range(100):
        e.allocate()
        e.observe(np.array([-0.05, 0.01, 0.01]))
    # Strategy 0 has been losing; its weight should still be above the floor
    assert e.weights[0] >= 9e-4
