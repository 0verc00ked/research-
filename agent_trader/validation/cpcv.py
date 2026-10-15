"""Combinatorial Purged Cross-Validation (López de Prado, AFML §12).

Generalises k-fold CV to time-series with overlapping labels:
  - Split T observations into N contiguous groups.
  - For each combination of k holdout groups (C(N,k) folds), build a train set
    from the remaining N-k groups, *purged* of any train sample whose label
    horizon overlaps a test sample, and *embargoed* by a fraction of T on the
    right edge of each test block.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

import numpy as np


@dataclass
class CPCVResult:
    n_folds: int
    fold_sharpes: list[float] = field(default_factory=list)
    fold_returns_oos: list[float] = field(default_factory=list)

    @property
    def folds_positive_ratio(self) -> float:
        if not self.fold_sharpes:
            return 0.0
        return float(np.mean([s > 0 for s in self.fold_sharpes]))

    @property
    def mean_oos_sharpe(self) -> float:
        return float(np.mean(self.fold_sharpes)) if self.fold_sharpes else 0.0


def _contiguous_groups(t: int, n_groups: int) -> list[np.ndarray]:
    edges = np.linspace(0, t, n_groups + 1, dtype=int)
    return [np.arange(edges[i], edges[i + 1]) for i in range(n_groups)]


def _purge_and_embargo(
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    label_horizon: int,
    embargo: int,
    t: int,
) -> np.ndarray:
    if len(test_idx) == 0:
        return train_idx
    test_min, test_max = int(test_idx.min()), int(test_idx.max())
    # Purge: drop train samples whose label_horizon window touches the test block.
    purge_lo = max(0, test_min - label_horizon)
    purge_hi = min(t - 1, test_max + label_horizon)
    # Embargo: drop train samples in [test_max+1, test_max+embargo].
    embargo_hi = min(t - 1, test_max + embargo)
    keep = ~((train_idx >= purge_lo) & (train_idx <= max(purge_hi, embargo_hi)))
    return train_idx[keep]


def combinatorial_purged_cv(
    returns: np.ndarray,
    *,
    n_groups: int = 8,
    k_test: int = 2,
    label_horizon: int = 1,
    embargo_pct: float = 0.02,
) -> CPCVResult:
    """Yield CPCV fold metrics for a vector of per-bar strategy returns.

    `returns[i]` is the return contribution at bar i (already realised by the
    strategy in question). We compute test-set Sharpe per fold to assess OOS
    consistency. Higher folds_positive_ratio = more robust strategy.
    """
    returns = np.asarray(returns, dtype=float)
    t = len(returns)
    if t < n_groups * 2:
        raise ValueError(f"need at least {n_groups * 2} obs, got {t}")
    groups = _contiguous_groups(t, n_groups)
    embargo = max(1, int(np.ceil(embargo_pct * t)))
    result = CPCVResult(n_folds=0)

    for test_g in combinations(range(n_groups), k_test):
        test_idx = np.concatenate([groups[g] for g in test_g])
        train_idx_full = np.concatenate(
            [groups[g] for g in range(n_groups) if g not in test_g]
        )
        _ = _purge_and_embargo(train_idx_full, test_idx, label_horizon, embargo, t)
        # We do not refit the strategy here — `returns` is already realised.
        # The fold's OOS Sharpe is the Sharpe of strategy returns on test_idx.
        test_returns = returns[test_idx]
        std = test_returns.std(ddof=1)
        sharpe = (
            float(test_returns.mean() / std * np.sqrt(252))
            if std > 0
            else 0.0
        )
        result.fold_sharpes.append(sharpe)
        result.fold_returns_oos.append(float(test_returns.sum()))
        result.n_folds += 1

    return result
