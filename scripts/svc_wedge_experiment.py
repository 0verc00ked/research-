"""L3 — The Grid-DSR-vs-SVC Wedge.

Demonstrates SVC's unique value: scenarios where Grid DSR accepts (false
positive — the strategy is null) but SVC correctly rejects.

Construction:
  - Fix a within-phase grid of fixed size (K_grid = 20)
  - Vary across-phase branching N_bp from 1 to 1000
  - For each N_bp, simulate the situation:
      * The researcher tested N_bp other phases, in each of which they
        ran a 20-cell grid; for each phase, only the best of the 20
        was retained.
      * Finally, the researcher picks the *best across the N_bp phases*.
      * Reported Sharpe = max of (best-of-grid) across N_bp phases.
  - All strategies are null (true Sharpe = 0).
  - Compute:
      * Naive DSR (N=1)
      * Grid DSR (N=K_grid = 20 — what Grid DSR would naively count)
      * SVC MDL-DSR (N_eff = N_bp * K_grid * 2^K)
  - The wedge: at large N_bp, Grid DSR's false-positive rate stays
    around its design level (~5%, because Grid DSR only knows about
    the within-phase grid). SVC's false-positive rate stays near 0%.

The empirical demonstration: SVC catches inflation that Grid DSR misses.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.validation import (  # noqa: E402
    TrialNode,
    deflated_sharpe_ratio,
    mdl_dsr,
)

REPORT = ROOT / "research" / "phase11_svc" / "A8a_wedge_experiment.md"


def simulate_one(n_bp: int, k_grid: int, tau: int, rng) -> tuple[float, np.ndarray]:
    """Simulate one researcher's experience:
      - n_bp phases, each with k_grid strategies
      - All null
      - Report max-by-Sharpe across all n_bp * k_grid candidates
      - Return the reported Sharpe and the returns of that best candidate
    """
    total = n_bp * k_grid
    R = rng.normal(0.0, 0.01, size=(total, tau))
    sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
    best = int(np.argmax(sharpes))
    return float(sharpes[best]), R[best]


def main():
    alpha = 0.05
    k_grid = 20
    tau = 500
    n_simulations = 1000
    n_bp_values = [1, 5, 25, 100, 500]
    K_strategy_bits = 30  # K_excess for a simple strategy after smart K extraction

    rng_master = np.random.default_rng(20260522)
    results = []
    for n_bp in n_bp_values:
        rng = np.random.default_rng(rng_master.integers(0, 2**31))
        rejections_naive = 0
        rejections_grid = 0
        rejections_svc = 0
        for _ in range(n_simulations):
            _, best_returns = simulate_one(n_bp, k_grid, tau, rng)

            # Naive DSR (N=1)
            naive = deflated_sharpe_ratio(best_returns, n_trials=1)
            if naive.dsr > 1 - alpha:
                rejections_naive += 1

            # Grid DSR — what the practitioner would compute (just the grid)
            grid = deflated_sharpe_ratio(best_returns, n_trials=k_grid)
            if grid.dsr > 1 - alpha:
                rejections_grid += 1

            # SVC MDL-DSR — full accounting of across-phase branching
            path = [
                TrialNode("phases", "h", 0, {}, "d", nu=n_bp),
                TrialNode("grid",   "h", K_strategy_bits, {}, "d", nu=k_grid),
            ]
            svc = mdl_dsr(best_returns, path=path)
            if svc.mdl_dsr > 1 - alpha:
                rejections_svc += 1

        results.append({
            "n_bp": n_bp,
            "n_simulations": n_simulations,
            "naive_typeI": rejections_naive / n_simulations,
            "grid_typeI":  rejections_grid  / n_simulations,
            "svc_typeI":   rejections_svc   / n_simulations,
        })
        print(
            f"  N_bp={n_bp:>4d}  Naive={rejections_naive/n_simulations:.4f}  "
            f"Grid={rejections_grid/n_simulations:.4f}  "
            f"SVC={rejections_svc/n_simulations:.4f}"
        )

    # Compute the wedge: Grid_typeI - SVC_typeI
    print("\nThe Grid-DSR-vs-SVC wedge:")
    print("  N_bp |   Grid  |   SVC   | Wedge (Grid - SVC)")
    print("  -----|---------|---------|---------------------")
    for r in results:
        wedge = r["grid_typeI"] - r["svc_typeI"]
        print(f"  {r['n_bp']:>4d} | {r['grid_typeI']:.4f} | {r['svc_typeI']:.4f} | {wedge:+.4f}")

    # Write report
    lines = [
        "# SVC A8a — Grid-DSR-vs-SVC Wedge Experiment\n",
        "Date: 2026-05-22\n",
        "Demonstrates SVC's unique value by constructing scenarios where Grid DSR "
        "is fooled but SVC catches the inflation.\n",
        f"**Setup:** {n_simulations} simulations per N_bp value. Within-phase grid = {k_grid}. "
        f"K_excess = {K_strategy_bits} bits. tau = {tau}. alpha = {alpha}.\n",
        "All strategies are null (true Sharpe = 0). The researcher 'searches' across "
        "N_bp phases, in each running a 20-cell grid. Reports the best Sharpe across all "
        "phases.\n",
        "Naive DSR uses N=1 (the indefensible default).",
        "Grid DSR uses N=20 (the grid the researcher acknowledges).",
        "SVC MDL-DSR uses N_eff = N_bp × 20 × 2^K (honest accounting).\n",
        "## Results\n",
        "| N_bp | Naive Type-I | Grid Type-I | SVC Type-I | Wedge (Grid − SVC) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        wedge = r["grid_typeI"] - r["svc_typeI"]
        lines.append(
            f"| {r['n_bp']} | {r['naive_typeI']:.4f} | {r['grid_typeI']:.4f} | "
            f"{r['svc_typeI']:.4f} | {wedge:+.4f} |"
        )

    # The crucial interpretation
    lines.extend([
        "",
        "## Interpretation\n",
        "**Grid DSR Type-I should stay around its design level (≤ 0.05) regardless of N_bp**, "
        "because Grid DSR only knows about the within-phase grid (size 20) and not the "
        "across-phase exploration. This is by construction.",
        "",
        "**SVC Type-I should also stay around its design level (≤ 0.05) at all N_bp values**, "
        "because SVC accounts for the across-phase branching.",
        "",
        "**The wedge appears when:** the researcher's reported Sharpe happens to clear Grid DSR's "
        "threshold (which is ignorant of the cross-phase search) but is correctly rejected by SVC. "
        "Each row of Grid_Type-I above α represents false positives Grid DSR would allow.",
        "",
        "## What this proves\n",
        "If Grid DSR Type-I exceeds SVC Type-I, that excess is the empirical demonstration of "
        "SVC's unique contribution beyond Grid DSR. Specifically, Grid DSR is *guaranteed* to "
        "leak Type-I at level α (its design), but for any N_bp > 1 the *true* selection is much "
        "larger than the grid, so Grid DSR's nominal α understates the actual false-positive risk. "
        "SVC closes that gap.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
