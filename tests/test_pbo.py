import numpy as np

from agent_trader.validation import cscv_pbo


def test_genuine_edge_low_pbo():
    """One variant has real edge, the rest are noise. Best-on-train should
    still be best-on-test → low PBO."""
    rng = np.random.default_rng(0)
    t, m = 1000, 20
    noise = rng.normal(0, 0.01, size=(t, m))
    noise[:, 0] += 0.002  # variant 0 has real edge
    pbo = cscv_pbo(noise, s_blocks=10)
    assert pbo.pbo < 0.3


def test_pure_noise_high_pbo():
    """All variants are i.i.d. noise. Best-on-train is luck; OOS rank random
    → PBO ≈ 0.5."""
    rng = np.random.default_rng(7)
    t, m = 800, 50
    noise = rng.normal(0, 0.01, size=(t, m))
    pbo = cscv_pbo(noise, s_blocks=10)
    # Pure noise → CSCV PBO should hover around 0.5 but has wide variance
    # across seeds; accept a generous band.
    assert 0.25 < pbo.pbo < 0.75


def test_overfit_winner_high_pbo():
    """Construct an "overfit winner" — its first half is great, second half
    is the worst. PBO should catch it."""
    rng = np.random.default_rng(13)
    t, m = 800, 20
    r = rng.normal(0, 0.01, size=(t, m))
    half = t // 2
    r[:half, 0] += 0.003  # great in-sample
    r[half:, 0] -= 0.003  # awful out-of-sample
    pbo = cscv_pbo(r, s_blocks=8)
    assert pbo.pbo > 0.6


def test_odd_s_raises():
    import pytest

    with pytest.raises(ValueError):
        cscv_pbo(np.zeros((100, 5)), s_blocks=7)
