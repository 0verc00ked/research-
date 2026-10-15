"""Normal-Inverse-Gamma conjugate posterior for unknown (μ, σ²).

Skeptical prior: μ₀ = 0 (we believe true edge is zero), κ₀ = 100 (strong
prior, posterior mean only moves ~23% of the way to MLE at n=30 observations).
This shrinks overfit backtest means mechanically — the posterior cannot
believe an extreme μ without commensurate evidence.

Posterior update (closed form):
    κ_n = κ_0 + n
    μ_n = (κ_0 μ_0 + n x̄) / κ_n
    α_n = α_0 + n/2
    β_n = β_0 + ½ Σ(r - x̄)² + κ_0 n (x̄ - μ_0)² / (2 κ_n)

Posterior summary used for sizing:
    E[μ | r] = μ_n
    E[σ² | r] = β_n / (α_n - 1)
    Var[μ | r] = E[σ²] / κ_n
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class NIGPrior:
    mu_0: float = 0.0
    kappa_0: float = 100.0   # skeptical — needs ~100 obs to halfway-trust the data
    alpha_0: float = 2.0
    beta_0: float = 1e-4     # tuned for ~1% per-period vol scale


@dataclass(frozen=True)
class NIGPosterior:
    mu_n: float
    kappa_n: float
    alpha_n: float
    beta_n: float
    n: int

    @property
    def expected_sigma_sq(self) -> float:
        if self.alpha_n <= 1.0:
            return float("inf")
        return self.beta_n / (self.alpha_n - 1.0)

    @property
    def var_mu(self) -> float:
        return self.expected_sigma_sq / self.kappa_n

    @property
    def shrinkage_factor(self) -> float:
        """How much the MLE has been shrunk toward μ₀. n / κ_n at μ₀ = 0."""
        return self.n / self.kappa_n if self.kappa_n > 0 else 0.0


def update_posterior(prior: NIGPrior, returns: np.ndarray) -> NIGPosterior:
    r = np.asarray(returns, dtype=float)
    n = int(r.size)
    if n == 0:
        return NIGPosterior(prior.mu_0, prior.kappa_0, prior.alpha_0, prior.beta_0, 0)

    x_bar = float(r.mean())
    kappa_n = prior.kappa_0 + n
    mu_n = (prior.kappa_0 * prior.mu_0 + n * x_bar) / kappa_n
    alpha_n = prior.alpha_0 + n / 2.0
    ssq = float(((r - x_bar) ** 2).sum())
    correction = prior.kappa_0 * n * (x_bar - prior.mu_0) ** 2 / (2.0 * kappa_n)
    beta_n = prior.beta_0 + 0.5 * ssq + correction
    return NIGPosterior(mu_n=mu_n, kappa_n=kappa_n, alpha_n=alpha_n, beta_n=beta_n, n=n)
