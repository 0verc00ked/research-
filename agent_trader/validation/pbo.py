"""Probability of Backtest Overfitting via Combinatorially Symmetric CV.

Bailey, Borwein, López de Prado, Zhu (2014; J. Computational Finance).

Inputs a (T x M) matrix of per-bar returns for M strategy variants over T bars.
Splits time into S equal blocks; for each balanced bipartition (S/2 train,
S/2 test):
  - Pick best variant on train half (highest in-sample Sharpe)
  - Compute its OOS rank on test half (rank / M)
  - Logit λ = log(rank / (1 - rank))
PBO = P(λ < 0) = probability that the best in-sample strategy underperforms
the median out-of-sample. Lower is better.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np


@dataclass
class PBOResult:
    pbo: float
    n_splits: int
    median_logit: float
    in_sample_sr_mean: float
    out_sample_sr_mean: float


def _sharpe_per_variant(block: np.ndarray) -> np.ndarray:
    """block shape: (rows, M variants). Returns Sharpe per variant (annualised)."""
    mean = block.mean(axis=0)
    std = block.std(axis=0, ddof=1)
    sr = np.where(std > 0, mean / np.where(std > 0, std, 1.0) * np.sqrt(252), 0.0)
    return sr


def cscv_pbo(returns_matrix: np.ndarray, *, s_blocks: int = 16) -> PBOResult:
    """`returns_matrix` shape: (T, M). M = number of strategy variants tried."""
    r = np.asarray(returns_matrix, dtype=float)
    if r.ndim != 2:
        raise ValueError(f"expected 2D (T, M), got shape {r.shape}")
    t, m = r.shape
    if s_blocks % 2 != 0:
        raise ValueError("s_blocks must be even")
    if t < s_blocks * 2:
        raise ValueError(f"need T >= {s_blocks * 2}, got {t}")

    edges = np.linspace(0, t, s_blocks + 1, dtype=int)
    blocks = [r[edges[i] : edges[i + 1]] for i in range(s_blocks)]

    logits: list[float] = []
    is_sr_means: list[float] = []
    oos_sr_means: list[float] = []
    half = s_blocks // 2

    for train_blocks in combinations(range(s_blocks), half):
        train_set = set(train_blocks)
        train_concat = np.concatenate([blocks[i] for i in train_blocks], axis=0)
        test_concat = np.concatenate(
            [blocks[i] for i in range(s_blocks) if i not in train_set], axis=0
        )
        sr_in = _sharpe_per_variant(train_concat)
        sr_out = _sharpe_per_variant(test_concat)
        i_star = int(np.argmax(sr_in))
        # Rank of i_star in OOS (1 = worst, M = best); normalise to (0,1).
        ranks = sr_out.argsort().argsort() + 1  # 1..M
        omega = ranks[i_star] / (m + 1)  # in (0, 1), avoids div-by-zero
        omega = float(np.clip(omega, 1e-6, 1 - 1e-6))
        lam = float(np.log(omega / (1 - omega)))
        logits.append(lam)
        is_sr_means.append(float(sr_in[i_star]))
        oos_sr_means.append(float(sr_out[i_star]))

    logits_a = np.asarray(logits)
    return PBOResult(
        pbo=float(np.mean(logits_a < 0)),
        n_splits=len(logits),
        median_logit=float(np.median(logits_a)),
        in_sample_sr_mean=float(np.mean(is_sr_means)),
        out_sample_sr_mean=float(np.mean(oos_sr_means)),
    )
