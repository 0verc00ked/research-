"""Deflated Sharpe Ratio (Bailey & López de Prado, 2014, SSRN 2460551).

Adjusts an observed Sharpe for:
  - Multiple testing (via N_trials and variance of Sharpes across them)
  - Higher-moment effects (skewness, kurtosis of returns)
  - Sample length (T)

DSR is the probability that the *true* Sharpe is > 0 given the observed
Sharpe and the multiple-testing/moment context. Gate at DSR ≥ 0.95.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

EULER_MASCHERONI = 0.5772156649015329


@dataclass
class DSRResult:
    sharpe_observed: float
    sharpe_expected_max_under_null: float
    dsr: float
    n_trials: int
    n_obs: int
    skew: float
    kurt: float


def expected_max_sharpe(
    sharpe_variance_across_trials: float,
    n_trials: int,
) -> float:
    """Bailey/LdP eq (5): expected max of N i.i.d. SR draws with given variance,
    using Gumbel extreme-value approximation."""
    if n_trials <= 1:
        return 0.0
    z1 = norm.ppf(1 - 1.0 / n_trials)
    z2 = norm.ppf(1 - 1.0 / (n_trials * math.e))
    em = (1 - EULER_MASCHERONI) * z1 + EULER_MASCHERONI * z2
    return float(math.sqrt(sharpe_variance_across_trials) * em)


def deflated_sharpe_ratio(
    returns: np.ndarray,
    *,
    n_trials: int,
    sharpe_variance_across_trials: float | None = None,
    periods_per_year: int = 252,
) -> DSRResult:
    """`returns` are per-bar (any frequency) strategy returns.

    If `sharpe_variance_across_trials` is None we use a conservative default of
    Var[SR] = 1.0 / periods_per_year (≈ 1.0 in per-period SR units). This is
    Bailey/LdP's "trial Sharpe variance" — supply the empirical value across
    your own logged trials when you have ≥10 trials in `trial_log` for this
    strategy family.
    """
    r = np.asarray(returns, dtype=float)
    n = len(r)
    if n < 30:
        raise ValueError(f"need >= 30 returns for DSR, got {n}")

    mean = r.mean()
    std = r.std(ddof=1)
    if std <= 0:
        return DSRResult(0.0, 0.0, 0.0, n_trials, n, 0.0, 0.0)

    sr_period = mean / std  # per-period SR
    sr_annual = sr_period * math.sqrt(periods_per_year)

    # Higher moments of returns (not of SR)
    skew = float(((r - mean) ** 3).mean() / std**3)
    # Excess kurtosis -> Pearson kurtosis = excess + 3
    excess_kurt = float(((r - mean) ** 4).mean() / std**4 - 3.0)
    kurt = excess_kurt + 3.0

    # Variance of estimated SR (in per-period units), AFML eq.
    var_sr_hat = (1 - skew * sr_period + (kurt - 1) / 4 * sr_period**2) / (n - 1)
    if var_sr_hat <= 0:
        return DSRResult(sr_annual, 0.0, 0.0, n_trials, n, skew, kurt)

    sigma_sr_hat = math.sqrt(var_sr_hat)

    # Expected max SR under null across n_trials
    var_for_em = (
        sharpe_variance_across_trials
        if sharpe_variance_across_trials is not None
        else 1.0 / periods_per_year
    )
    sr_zero_period = expected_max_sharpe(var_for_em, n_trials)
    sr_zero_annual = sr_zero_period * math.sqrt(periods_per_year)

    # DSR = Φ((SR - SR_0) / σ_SR)
    z = (sr_period - sr_zero_period) / sigma_sr_hat
    dsr = float(norm.cdf(z))

    return DSRResult(
        sharpe_observed=sr_annual,
        sharpe_expected_max_under_null=sr_zero_annual,
        dsr=dsr,
        n_trials=n_trials,
        n_obs=n,
        skew=skew,
        kurt=kurt,
    )
