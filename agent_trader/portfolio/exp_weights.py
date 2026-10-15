"""Hedge / exponentiated-weights algorithm (Freund & Schapire 1997;
Cesa-Bianchi & Lugosi 2006, *Prediction, Learning, and Games*).

Convex weights p_t over K strategies. After each round the weights of
strategies that gained more get multiplicatively up-weighted.

**Mathematical claim:** for returns scaled into [-B, B] via the linear
transform g = (r + B) / (2B) ∈ [0, 1],

    Σ_t Σ_i p_t^i · g_t^i  ≥  max_i Σ_t g_t^i  −  √(T · ln K / 2)

That is, the algorithm's cumulative *gain* is within √(T·ln K / 2) of the
best single strategy in hindsight. Translating back to raw returns, the
worst-case regret on the cumulative weighted return is

    R_T ≤ 2B · √(T · ln K / 2)  =  B · √(2T · ln K)

**Important:** this bound applies to the raw convex combination Σ p^i r^i.
If you scale the allocation by a Kelly factor or any other multiplier, the
algorithm changes and the bound no longer applies in its clean form.
Compose carefully — see `allocator.py`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class ExpWeightsConfig:
    n_strategies: int
    bound_b: float = 0.05            # |return| upper bound per period (5% daily)
    eta: float | None = None         # learning rate; default = √(8 ln K / T_hint)
    t_hint: int = 252                # used only to pick default eta
    warmup_floor: float = 1e-3       # min weight floor to allow recovery


class ExpWeights:
    def __init__(self, cfg: ExpWeightsConfig):
        if cfg.n_strategies < 2:
            raise ValueError("need >=2 strategies")
        self.cfg = cfg
        self.k = cfg.n_strategies
        self._w = np.ones(self.k) / self.k
        self.eta = cfg.eta or math.sqrt(8.0 * math.log(self.k) / cfg.t_hint)
        self.t = 0
        self._cum_strategy_returns = np.zeros(self.k)
        self._cum_algo_return = 0.0
        self._last_weights: np.ndarray | None = None

    @property
    def weights(self) -> np.ndarray:
        return self._w.copy()

    def allocate(self) -> np.ndarray:
        """Return current convex weights (used to split capital). Saves them
        so observe() can compute the actual ensemble return correctly."""
        self._last_weights = self._w.copy()
        return self._last_weights

    def observe(self, returns: np.ndarray) -> None:
        """`returns` shape (K,): per-strategy realised return for the period.

        Updates weights and tracks regret accounting.
        """
        if returns.shape != (self.k,):
            raise ValueError(f"expected shape ({self.k},), got {returns.shape}")
        if self._last_weights is None:
            # If observe() is called without a preceding allocate(), use current.
            self._last_weights = self._w.copy()

        # Algo return = w · r at the weights *used* for this period
        algo_ret = float(np.dot(self._last_weights, returns))
        self._cum_algo_return += algo_ret
        self._cum_strategy_returns += returns

        # Map to [0, 1] gains
        b = self.cfg.bound_b
        gains = np.clip((returns + b) / (2.0 * b), 0.0, 1.0)

        # Multiplicative update
        self._w *= np.exp(self.eta * gains)
        self._w /= self._w.sum()
        # Floor to allow recovery from a bad streak
        if self.cfg.warmup_floor > 0:
            self._w = np.maximum(self._w, self.cfg.warmup_floor)
            self._w /= self._w.sum()

        self.t += 1
        self._last_weights = None

    def empirical_regret(self) -> float:
        """Cumulative regret in raw-return units: best-in-hindsight minus algo."""
        best_cum = float(self._cum_strategy_returns.max())
        return best_cum - self._cum_algo_return

    def theoretical_regret_bound(self, t: int | None = None) -> float:
        """Worst-case regret bound on cumulative raw return at horizon t."""
        t = t if t is not None else max(self.t, 1)
        return self.cfg.bound_b * math.sqrt(2.0 * t * math.log(self.k))
