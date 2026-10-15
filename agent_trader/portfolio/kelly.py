"""Fractional Kelly with hard exposure cap.

For continuous-time / Gaussian returns the Kelly criterion sizes positions at
f* = μ / σ². We use a fraction of this (default 0.1 = "Kelly/10") for two
reasons:
  1. Robustness to wrong edge estimates. Thorp 2006: at fractional Kelly
     << 1, ruin probability in finite time is bounded.
  2. Risk aversion. Full Kelly maximises long-run growth rate but has high
     volatility; fractional Kelly trades some growth for much less vol.

Plus a hard cap on total exposure so that even a wildly overconfident
posterior cannot deploy more than (e.g.) 50% of capital.
"""
from __future__ import annotations


def kelly_optimal(mu: float, sigma_sq: float) -> float:
    """Unconstrained Kelly fraction. Negative if μ < 0 (would short)."""
    if sigma_sq <= 0:
        return 0.0
    return mu / sigma_sq


def kelly_size(
    mu: float,
    sigma_sq: float,
    *,
    frac: float = 0.1,
    max_exposure: float = 0.5,
    long_only: bool = True,
) -> float:
    """Return allocation as a fraction of capital, capped.

    - `frac`: fraction of full Kelly to deploy (Kelly/10 = 0.1 is the project
      default; Thorp/Kelly literature recommends ≤ 0.5 for robustness).
    - `max_exposure`: hard cap on the returned fraction.
    - `long_only`: if True (default), negative posterior μ returns 0 (strategy
      is disabled by allocator rather than shorted). Strategies decide their
      own direction; the allocator never inverts a strategy.
    """
    f_star = kelly_optimal(mu, sigma_sq)
    if long_only and f_star <= 0.0:
        return 0.0
    sized = f_star * frac
    if long_only:
        return min(max(sized, 0.0), max_exposure)
    return max(min(sized, max_exposure), -max_exposure)
