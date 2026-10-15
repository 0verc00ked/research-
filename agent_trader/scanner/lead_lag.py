"""Cross-asset lead-lag scanner.

For each pair (X, Y) and lag k>0, tests H0: corr(X_t, Y_{t+k}) = 0 against
H1: ≠ 0 using Fisher z-transform. Multiple-testing correction via
Benjamini–Hochberg FDR at the user-specified level.

A "lead-lag relationship" means X at time t carries information about Y at
time t+k. Tradable only if k > 0 (Y still in the future).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests


@dataclass
class LeadLagResult:
    lead: str          # X — moves first
    lagger: str        # Y — moves later
    lag_days: int      # k > 0
    n: int             # paired sample size
    corr: float        # observed Pearson r
    z: float           # Fisher z-stat
    p: float           # two-sided p
    fdr_q: float | None = None
    pass_fdr: bool = False


def _fisher_z_test(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Pearson r + Fisher z-transform test. Returns (r, z_stat, p_two_sided)."""
    n = len(x)
    if n < 30:
        return 0.0, 0.0, 1.0
    r = float(np.corrcoef(x, y)[0, 1])
    r = max(min(r, 0.999999), -0.999999)
    z = 0.5 * math.log((1 + r) / (1 - r))
    se = 1.0 / math.sqrt(n - 3)
    z_stat = z / se
    # two-sided p via standard normal
    from math import erf, sqrt
    p = 2 * (1 - 0.5 * (1 + erf(abs(z_stat) / sqrt(2))))
    return r, z_stat, max(p, 1e-300)


def scan(
    returns: pd.DataFrame,
    *,
    lags: tuple[int, ...] = (1, 2, 3, 5, 10),
    fdr_level: float = 0.05,
    min_corr_abs: float = 0.05,
) -> list[LeadLagResult]:
    """`returns` shape (T, N) — per-asset log returns aligned on a common index.

    Tests EVERY (X, Y, k) ordered pair where k > 0 (X leads Y by k days).
    Self-pairs at the same lag are skipped (that's autocorrelation, not
    cross-asset lead-lag).
    """
    assets = list(returns.columns)
    rmat = returns.dropna().to_numpy()
    n_rows, n_assets = rmat.shape
    if n_rows < 50:
        raise ValueError(f"need at least 50 paired bars, got {n_rows}")

    raw: list[LeadLagResult] = []
    for k in lags:
        if k <= 0 or k >= n_rows - 30:
            continue
        x_block = rmat[:-k]
        y_block = rmat[k:]
        # vectorised: for each pair (i, j) compute corr(x_block[:, i], y_block[:, j])
        n_paired = x_block.shape[0]
        x_c = x_block - x_block.mean(axis=0)
        y_c = y_block - y_block.mean(axis=0)
        cov = (x_c.T @ y_c) / (n_paired - 1)
        sx = x_block.std(axis=0, ddof=1)
        sy = y_block.std(axis=0, ddof=1)
        denom = sx[:, None] * sy[None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            corr = np.where(denom > 0, cov / denom, 0.0)
        # Convert each to Fisher z + p
        for i, lead in enumerate(assets):
            for j, lagger in enumerate(assets):
                if i == j:
                    continue
                r = float(np.clip(corr[i, j], -0.999999, 0.999999))
                if abs(r) < min_corr_abs:
                    continue
                z_raw = 0.5 * math.log((1 + r) / (1 - r))
                se = 1.0 / math.sqrt(n_paired - 3)
                z_stat = z_raw / se
                from math import erf, sqrt
                p = max(2 * (1 - 0.5 * (1 + erf(abs(z_stat) / sqrt(2)))), 1e-300)
                raw.append(LeadLagResult(
                    lead=lead, lagger=lagger, lag_days=k,
                    n=n_paired, corr=r, z=z_stat, p=p,
                ))

    if not raw:
        return []

    pvals = np.array([r.p for r in raw])
    reject, qvals, _, _ = multipletests(pvals, alpha=fdr_level, method="fdr_bh")
    for r, q, ok in zip(raw, qvals, reject):
        r.fdr_q = float(q)
        r.pass_fdr = bool(ok)

    raw.sort(key=lambda r: (not r.pass_fdr, r.p))
    return raw
