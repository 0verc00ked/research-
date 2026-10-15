import math

import numpy as np

from agent_trader.portfolio import NIGPrior, update_posterior


def test_no_data_returns_prior():
    p = update_posterior(NIGPrior(), np.array([]))
    assert p.n == 0
    assert p.mu_n == 0.0
    assert p.kappa_n == 100.0


def test_shrinkage_30_obs():
    """At n=30 with κ₀=100, posterior mean should be 30/130 ≈ 0.231 of MLE."""
    prior = NIGPrior(mu_0=0.0, kappa_0=100.0, alpha_0=2.0, beta_0=1e-4)
    rng = np.random.default_rng(0)
    r = rng.normal(loc=0.01, scale=0.01, size=30)
    post = update_posterior(prior, r)
    mle = float(r.mean())
    expected = (30 / 130) * mle
    np.testing.assert_allclose(post.mu_n, expected, rtol=1e-9)
    assert post.shrinkage_factor < 0.3, "MLE should be shrunk by >70%"


def test_shrinkage_relaxes_with_data():
    """At n=1000, posterior should be ~90% of MLE."""
    prior = NIGPrior()
    rng = np.random.default_rng(1)
    r = rng.normal(0.005, 0.01, size=1000)
    post = update_posterior(prior, r)
    assert post.shrinkage_factor > 0.85


def test_expected_sigma_sq_positive():
    rng = np.random.default_rng(2)
    r = rng.normal(0, 0.01, size=50)
    post = update_posterior(NIGPrior(), r)
    assert post.expected_sigma_sq > 0


def test_var_mu_shrinks_with_n():
    rng = np.random.default_rng(3)
    r = rng.normal(0, 0.01, size=500)
    post_full = update_posterior(NIGPrior(), r)
    post_short = update_posterior(NIGPrior(), r[:50])
    assert post_full.var_mu < post_short.var_mu


def test_mle_recovery_with_weak_prior():
    """With κ₀ near 0, posterior mean ≈ MLE."""
    weak = NIGPrior(kappa_0=0.001)
    rng = np.random.default_rng(4)
    r = rng.normal(0.002, 0.01, size=200)
    post = update_posterior(weak, r)
    np.testing.assert_allclose(post.mu_n, float(r.mean()), rtol=1e-3)
