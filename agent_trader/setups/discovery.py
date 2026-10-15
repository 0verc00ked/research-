"""Conjunctive-setup discovery with honest multiple-testing accounting.

Given a feature matrix of binary conditions and a forward-return label, find
combinations of 1, 2, or 3 conditions whose conditional mean forward return
is significantly different from zero AFTER Benjamini-Hochberg FDR
correction across the entire search space.

Why combinations and not a tree:
  - Explicit. We can write down the search space size = N_trials and feed
    that to the harness's DSR check.
  - Interpretable. Every surviving setup is a conjunction of named
    conditions, debuggable by humans.
  - Resistant to overfitting in a way trees are not (no greedy split
    selection that finds noise).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests


@dataclass
class SetupResult:
    conditions: tuple[str, ...]   # which feature conditions must hold (True)
    n: int                        # sample count in this conjunction
    mean_ret: float
    std_ret: float
    t_stat: float
    p: float
    fdr_q: float | None = None
    pass_fdr: bool = False

    @property
    def name(self) -> str:
        return " AND ".join(self.conditions)


def search(
    features: pd.DataFrame,
    forward_return: pd.Series,
    *,
    max_order: int = 3,
    min_n: int = 50,
    fdr_level: float = 0.05,
) -> tuple[list[SetupResult], int]:
    """`features` is a (T, F) boolean dataframe; columns are condition names.
    `forward_return` is a (T,) numeric series aligned to features.

    Returns (results, total_trials). total_trials is the honest N_trials count
    you must pass to DSR.
    """
    assert features.index.equals(forward_return.index)
    raw_results: list[SetupResult] = []
    cols = list(features.columns)
    fmat = features.to_numpy(dtype=bool)
    y = forward_return.to_numpy(dtype=float)
    valid_y = ~np.isnan(y)

    total_trials = 0
    for order in range(1, max_order + 1):
        for combo in combinations(range(len(cols)), order):
            mask = np.all(fmat[:, list(combo)], axis=1) & valid_y
            n = int(mask.sum())
            total_trials += 1
            if n < min_n:
                continue
            sub = y[mask]
            mean = float(sub.mean())
            std = float(sub.std(ddof=1))
            if std <= 0:
                continue
            t_stat = mean / (std / math.sqrt(n))
            # two-sided p via normal approximation (n is large enough)
            from math import erf, sqrt
            p = max(2 * (1 - 0.5 * (1 + erf(abs(t_stat) / sqrt(2)))), 1e-300)
            raw_results.append(SetupResult(
                conditions=tuple(cols[i] for i in combo),
                n=n, mean_ret=mean, std_ret=std,
                t_stat=t_stat, p=p,
            ))

    if not raw_results:
        return [], total_trials

    pvals = np.array([r.p for r in raw_results])
    reject, qvals, _, _ = multipletests(pvals, alpha=fdr_level, method="fdr_bh")
    for r, q, ok in zip(raw_results, qvals, reject):
        r.fdr_q = float(q)
        r.pass_fdr = bool(ok)

    raw_results.sort(key=lambda r: (not r.pass_fdr, r.p))
    return raw_results, total_trials


def split_train_val_test(
    features: pd.DataFrame,
    forward_return: pd.Series,
    *,
    train_end: str = "2022-01-01",
    val_end: str = "2024-01-01",
) -> tuple[tuple[pd.DataFrame, pd.Series], tuple[pd.DataFrame, pd.Series], tuple[pd.DataFrame, pd.Series]]:
    train_mask = features.index < pd.Timestamp(train_end, tz=features.index.tz)
    val_mask = (features.index >= pd.Timestamp(train_end, tz=features.index.tz)) & (
        features.index < pd.Timestamp(val_end, tz=features.index.tz)
    )
    test_mask = features.index >= pd.Timestamp(val_end, tz=features.index.tz)
    return (
        (features.loc[train_mask], forward_return.loc[train_mask]),
        (features.loc[val_mask], forward_return.loc[val_mask]),
        (features.loc[test_mask], forward_return.loc[test_mask]),
    )
