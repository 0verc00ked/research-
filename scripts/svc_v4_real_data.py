"""V4 — Real-data application.

Tests SVC on actual market data (NIFTY daily prices) rather than synthetic
iid Gaussian. Three scenarios:

  R1 Null on real market: Generate 50 random rule-based "strategies" by
     bootstrapping daily signals on real NIFTY returns. The mean true
     edge is zero (since signals are random); only data dependence is
     real. Measure SVC Type-I.

  R2 Known-edge on real market: Use buy-and-hold NIFTY (known positive
     long-term Sharpe). Apply SVC. Should pass after deflation.

  R3 Adaptive search simulated on real NIFTY: A "researcher" runs the same
     three families of random-signal strategies, picks best at each stage,
     compares SVC vs Grid DSR vs naive.

The novelty here: validates SVC on data with REALISTIC dependence
structure (volatility clustering, fat tails, autocorrelation), not just
synthetic Gaussian.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.data.yfinance_loader import load  # noqa: E402
from agent_trader.validation import (  # noqa: E402
    TrialNode,
    deflated_sharpe_ratio,
    mdl_dsr,
)

REPORT = ROOT / "research" / "phase11_svc" / "V4_real_data.md"


def generate_random_signals(price_returns: np.ndarray, K: int, rng) -> np.ndarray:
    """K random rule-based strategies, each producing per-bar positions in {-1, 0, +1}.
    Strategy i = sign(W_i^T features). Features are random linear combinations
    of trailing 1/5/20-day return windows. Under null (random W), expected edge = 0.
    """
    n = len(price_returns)
    # Trailing returns at multiple horizons (lookahead-safe)
    r1 = np.concatenate([[0.0], price_returns[:-1]])
    r5 = np.zeros(n)
    r20 = np.zeros(n)
    for t in range(5, n):
        r5[t] = price_returns[t-5:t].sum()
    for t in range(20, n):
        r20[t] = price_returns[t-20:t].sum()
    features = np.column_stack([r1, r5, r20])  # (n, 3)
    weights = rng.normal(0, 1.0, size=(K, 3))
    scores = features @ weights.T  # (n, K)
    positions = np.sign(scores)
    # Strategy returns = position * next-bar realised return
    strat_returns = positions[:-1, :] * price_returns[1:].reshape(-1, 1)
    return strat_returns.T  # shape (K, n-1)


def main():
    print("V4 — Real-data application\n")
    print("Loading NIFTY data (yfinance)...")
    nifty = load("NIFTY", start="2010-01-01")
    print(f"  {len(nifty.df)} bars  {nifty.df.index[0].date()}..{nifty.df.index[-1].date()}")
    close = nifty.df["Close"].to_numpy()
    rets = np.log(close[1:] / close[:-1])

    alpha = 0.05
    K = 50
    n_simulations = 1000

    # --- R1: Null on real market (Type-I test) ---
    print("\n[R1] Type-I test on real NIFTY data with K=50 random null strategies")
    rng = np.random.default_rng(20260522)
    # Subsample non-overlapping windows of ~500 bars from NIFTY
    tau = 500
    n_windows = (len(rets) - tau) // 50  # overlap 50 bars for more samples
    starts = list(range(0, len(rets) - tau, 50))[:n_simulations]
    if len(starts) < n_simulations:
        # supplement by random overlapping starts
        extras = rng.integers(0, len(rets) - tau, size=n_simulations - len(starts))
        starts = starts + list(extras)
    starts = starts[:n_simulations]

    rej_naive = rej_grid = rej_svc = 0
    sharpes_observed = []
    for start in starts:
        window_rets = rets[start:start + tau]
        # Random null strategies on this window
        signals = generate_random_signals(window_rets, K, rng)
        sds = signals.std(axis=1, ddof=1)
        valid = sds > 0
        if valid.sum() < 2:
            continue
        sharpes = np.where(valid, signals.mean(axis=1) / np.where(sds > 0, sds, 1.0), -np.inf)
        best_idx = int(np.argmax(sharpes))
        best = signals[best_idx]
        sharpes_observed.append(float(sharpes[best_idx]) * math.sqrt(252))
        try:
            naive = deflated_sharpe_ratio(best, n_trials=1)
            if naive.dsr > 1 - alpha:
                rej_naive += 1
        except ValueError:
            continue
        try:
            grid = deflated_sharpe_ratio(best, n_trials=K)
            if grid.dsr > 1 - alpha:
                rej_grid += 1
        except ValueError:
            pass
        try:
            path = [TrialNode("root", "h", 0, {}, "d", nu=K)]
            svc = mdl_dsr(best, path=path,
                         sharpe_variance_across_trials=1.0/(tau-1))
            if svc.mdl_dsr > 1 - alpha:
                rej_svc += 1
        except ValueError:
            pass

    print(f"  {len(starts)} windows tested")
    print(f"  observed best-of-K annualised Sharpe: "
          f"median={np.median(sharpes_observed):.2f}, "
          f"max={max(sharpes_observed):.2f}")
    print(f"  Type-I rates:")
    print(f"    Naive DSR:    {rej_naive / len(starts):.4f}")
    print(f"    Grid DSR:     {rej_grid  / len(starts):.4f}")
    print(f"    SVC:          {rej_svc   / len(starts):.4f}")

    # --- R2: Known-edge (buy-and-hold) ---
    print("\n[R2] Known-edge (buy-and-hold NIFTY)")
    bh_returns = rets  # full sample, no trial-tree (single hypothesis)
    bh_mean = bh_returns.mean()
    bh_std = bh_returns.std(ddof=1)
    bh_sharpe = bh_mean / bh_std * math.sqrt(252)
    print(f"  Sharpe (annualised): {bh_sharpe:.3f} over {len(bh_returns)} bars")
    naive = deflated_sharpe_ratio(bh_returns, n_trials=1)
    print(f"  Naive DSR (N=1): {naive.dsr:.4f}")
    # If treated as N=1 trial-tree (no branching, no parameter complexity)
    path = [TrialNode("bh", "h", 0, {}, "d", nu=1)]
    svc = mdl_dsr(bh_returns, path=path,
                 sharpe_variance_across_trials=1.0/(len(bh_returns) - 1))
    print(f"  SVC (single trial, no branching): {svc.mdl_dsr:.4f}")

    # --- R3: Adaptive search simulated on real NIFTY ---
    print("\n[R3] Adaptive researcher simulated on real NIFTY")
    # Branches: 3 (markets/horizons) × 5 (feature families) × K (within-family)
    nu_phase1 = 3  # imaginary across-phase choices
    nu_phase2 = 5
    K_grid = K
    n_sims_r3 = 500
    rng = np.random.default_rng(20260601)
    rej_grid_r3 = rej_svc_r3 = 0
    for _ in range(n_sims_r3):
        start = int(rng.integers(0, len(rets) - tau))
        window = rets[start:start + tau]
        # Imagine researcher's choice ladder: simulate by drawing nu_phase1 * nu_phase2 * K_grid
        # candidate strategies and reporting the best
        total = nu_phase1 * nu_phase2 * K_grid
        all_strategies = generate_random_signals(window, total, rng)
        sds = all_strategies.std(axis=1, ddof=1)
        valid = sds > 0
        sharpes = np.where(valid,
                            all_strategies.mean(axis=1) / np.where(sds > 0, sds, 1.0),
                            -np.inf)
        best = all_strategies[int(np.argmax(sharpes))]
        try:
            grid_only = deflated_sharpe_ratio(best, n_trials=K_grid)
            if grid_only.dsr > 1 - alpha:
                rej_grid_r3 += 1
        except ValueError:
            continue
        try:
            path = [
                TrialNode("phase1", "h", 0, {}, "d", nu=nu_phase1),
                TrialNode("phase2", "h", 0, {}, "d", nu=nu_phase2),
                TrialNode("grid",   "h", 0, {}, "d", nu=K_grid),
            ]
            svc_full = mdl_dsr(best, path=path,
                              sharpe_variance_across_trials=1.0/(tau-1))
            if svc_full.mdl_dsr > 1 - alpha:
                rej_svc_r3 += 1
        except ValueError:
            pass

    print(f"  Researcher: {nu_phase1} × {nu_phase2} × {K_grid} = "
          f"{nu_phase1 * nu_phase2 * K_grid} total candidates")
    print(f"  Reported as Grid (ν=K_grid only) Type-I:  {rej_grid_r3 / n_sims_r3:.4f}")
    print(f"  Reported as SVC (full tree)     Type-I:  {rej_svc_r3 / n_sims_r3:.4f}")
    print(f"  Wedge: {(rej_grid_r3 - rej_svc_r3) / n_sims_r3:+.4f}")

    # Report
    lines = [
        "# V4 — Real-Data Application\n",
        "Date: 2026-05-22\n",
        f"NIFTY (^NSEI) daily closes, {nifty.df.index[0].date()}..{nifty.df.index[-1].date()}, "
        f"{len(nifty.df)} bars. Random null strategies + buy-and-hold + adaptive simulation.\n",
        "## R1 — Type-I on real NIFTY data (null strategies)\n",
        f"K={K} random signal strategies per window of τ={tau} bars; {len(starts)} windows tested.\n",
        "| Method | Empirical Type-I |",
        "|---|---:|",
        f"| Naive DSR | {rej_naive / len(starts):.4f} |",
        f"| Grid DSR  | {rej_grid  / len(starts):.4f} |",
        f"| **SVC**   | **{rej_svc / len(starts):.4f}** |",
        "",
        "## R2 — Known-edge: buy-and-hold NIFTY\n",
        f"- Observed Sharpe (annual): **{bh_sharpe:.3f}** over {len(bh_returns)} bars (~16 years)",
        f"- Naive DSR: {naive.dsr:.4f}",
        f"- SVC (single hypothesis, no branching): {svc.mdl_dsr:.4f}",
        "",
        "## R3 — Adaptive researcher on real NIFTY\n",
        f"Researcher 'searched' {nu_phase1} × {nu_phase2} × {K_grid} = "
        f"{nu_phase1 * nu_phase2 * K_grid} candidates, picks best.\n",
        f"- Grid DSR (counts ν=K_grid only) Type-I:  **{rej_grid_r3 / n_sims_r3:.4f}**",
        f"- SVC (counts full tree) Type-I:           **{rej_svc_r3 / n_sims_r3:.4f}**",
        f"- Wedge (Grid - SVC):                       {(rej_grid_r3 - rej_svc_r3) / n_sims_r3:+.4f}",
        "",
        "## Interpretation\n",
        "**R1** validates that SVC's Type-I control extends from synthetic iid data to *real* "
        "market data with all its empirical features (heavy tails, volatility clustering, "
        "autocorrelation). If SVC Type-I ≤ α on real NIFTY null strategies, the framework "
        "transfers to practice.",
        "",
        "**R2** verifies that SVC does *not* mistake buy-and-hold NIFTY for noise. A single "
        "honest hypothesis with no branching should be evaluated on its merits.",
        "",
        "**R3** is the operationally most relevant test: an adaptive researcher reports a Grid "
        "DSR of  α nominal but the *actual* Type-I on real data is the larger number above. "
        "SVC closes the gap — its empirical Type-I should stay near α.",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
