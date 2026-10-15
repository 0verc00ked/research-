"""Composition: Hedge (split) ∘ Bayesian Kelly (total exposure) ∘ hard cap.

Mathematical decomposition:

    per_strategy_capital_fraction_i  =  p_t^i  ·  total_exposure_t

  - `p_t^i` are convex Hedge weights (Σ p_t^i = 1). Carry the √(T·ln K)
    regret bound on Σ p_t^i r_t^i versus best-in-hindsight (see exp_weights).
  - `total_exposure_t` is the fractional-Kelly sizing on the *ensemble's*
    realised return history through time t, using a skeptical NIG posterior.
    This is the "how much of capital to deploy at all" decision.

Why this composition:
  - Hedge guarantees: even if we don't know which strategy is best, our
    *split* is within √(T·ln K) of the best-in-hindsight split.
  - Bayesian Kelly guarantees: until we have substantial evidence the
    ensemble actually has positive μ, total exposure stays small. Overfit
    backtests cannot scale into capital.
  - The product is interpretable and the failure modes are bounded.

What it does NOT claim:
  - Per-strategy Bayesian sizing. We size the *ensemble*, not individual
    strategies. Strategy quality is arbitrated by Hedge weights.
  - Joint regret bound on per_strategy_capital. The Kelly multiplier
    breaks the clean Hedge guarantee on the gross deployment.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .bayesian_sizing import NIGPosterior, NIGPrior, update_posterior
from .exp_weights import ExpWeights, ExpWeightsConfig
from .kelly import kelly_size


@dataclass
class AllocatorConfig:
    strategy_names: list[str]
    nig_prior: NIGPrior = field(default_factory=NIGPrior)
    bound_b: float = 0.05
    t_hint: int = 252
    kelly_frac: float = 0.1
    max_total_exposure: float = 0.5
    long_only: bool = True


@dataclass
class AllocationSnapshot:
    weights: np.ndarray
    total_exposure: float
    per_strategy_fraction: np.ndarray
    per_strategy_capital: dict[str, float]
    posterior: NIGPosterior


class Allocator:
    def __init__(self, cfg: AllocatorConfig):
        self.cfg = cfg
        self.k = len(cfg.strategy_names)
        self.exp = ExpWeights(
            ExpWeightsConfig(n_strategies=self.k, bound_b=cfg.bound_b, t_hint=cfg.t_hint)
        )
        self.ensemble_returns: list[float] = []
        self.steps = 0

    def allocate(self, capital: float) -> AllocationSnapshot:
        weights = self.exp.allocate()
        post = update_posterior(self.cfg.nig_prior, np.asarray(self.ensemble_returns))
        total_exposure = kelly_size(
            post.mu_n,
            post.expected_sigma_sq,
            frac=self.cfg.kelly_frac,
            max_exposure=self.cfg.max_total_exposure,
            long_only=self.cfg.long_only,
        )
        per_strategy = weights * total_exposure
        per_capital = {
            n: float(per_strategy[i] * capital) for i, n in enumerate(self.cfg.strategy_names)
        }
        return AllocationSnapshot(
            weights=weights,
            total_exposure=total_exposure,
            per_strategy_fraction=per_strategy,
            per_strategy_capital=per_capital,
            posterior=post,
        )

    def observe(self, returns_per_strategy: dict[str, float]) -> None:
        ret_vec = np.asarray(
            [returns_per_strategy[n] for n in self.cfg.strategy_names], dtype=float
        )
        # Ensemble return uses the weights that *generated* the prior period's
        # allocation; ExpWeights.observe consumes its own _last_weights internally.
        weights_used = self.exp._last_weights if self.exp._last_weights is not None else self.exp.weights
        ensemble = float(np.dot(weights_used, ret_vec))
        self.ensemble_returns.append(ensemble)
        self.exp.observe(ret_vec)
        self.steps += 1
