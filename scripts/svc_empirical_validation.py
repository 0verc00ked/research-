"""SVC Empirical Validation — Monte Carlo tests of Theorem 1 claims.

Tests four substantive claims about MDL-DSR:

  T1. Type-I error control on a flat tree under the null hypothesis
      (all strategies have true Sharpe = 0). Empirical rejection rate at
      alpha should be ≤ alpha + Monte Carlo error.

  T2. Type-I error control on an adaptive tree (researcher branches based
      on observed in-sample Sharpe; reports OOS Sharpe). With honest
      data-splitting (A1), Type-I should still be controlled.

  T3. Power: under a true edge (Sharpe > 0), what fraction of strategies
      are correctly detected? Compare vs naive DSR / Grid DSR.

  T4. E[SR_max | N] calibration: simulate the actual maximum of N
      independent null Sharpes; compare to the Bailey-LdP prediction
      used inside MDL-DSR.

If T1, T2 hold (empirical Type-I ≤ alpha), the theorem's central claim is
empirically validated. If they fail, the theorem has a bug we have not
identified.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.validation import (  # noqa: E402
    TrialNode,
    deflated_sharpe_ratio,
    mdl_dsr,
)
from agent_trader.validation.svc import _expected_max_sharpe_logN  # noqa: E402

REPORT = ROOT / "research" / "phase11_svc" / "A7_empirical_validation.md"


# ---------------------------------------------------------------------------
# T1: Type-I on flat tree
# ---------------------------------------------------------------------------

def t1_flat_tree_typeI(
    n_simulations: int = 2000,
    K_alternatives: int = 50,
    tau: int = 500,
    alpha: float = 0.05,
    seed: int = 2026,
) -> dict:
    """Flat tree: at the root, the researcher picks the *best of K* iid null
    strategies. Each strategy generates tau iid N(0, sigma²) returns.
    Report MDL-DSR verdict on the best-of-K. Repeat n_simulations times.
    """
    rng = np.random.default_rng(seed)
    rejections_mdl = 0
    rejections_naive = 0
    rejections_grid = 0

    for sim in range(n_simulations):
        all_returns = rng.normal(0.0, 0.01, size=(K_alternatives, tau))
        sharpes = all_returns.mean(axis=1) / all_returns.std(axis=1, ddof=1)
        best_idx = int(np.argmax(sharpes))
        best_returns = all_returns[best_idx]

        # Tree: root with nu=K_alternatives, K=0 (no extra parameters)
        path = [TrialNode("flat_root", "h", 0, {}, "d", nu=K_alternatives)]
        svc = mdl_dsr(best_returns, path=path)
        if svc.mdl_dsr > 1 - alpha:
            rejections_mdl += 1

        naive = deflated_sharpe_ratio(best_returns, n_trials=1)
        if naive.dsr > 1 - alpha:
            rejections_naive += 1
        grid = deflated_sharpe_ratio(best_returns, n_trials=K_alternatives)
        if grid.dsr > 1 - alpha:
            rejections_grid += 1

    return {
        "n_simulations": n_simulations,
        "K": K_alternatives,
        "tau": tau,
        "alpha": alpha,
        "type_I_naive_dsr": rejections_naive / n_simulations,
        "type_I_grid_dsr": rejections_grid / n_simulations,
        "type_I_svc_mdl_dsr": rejections_mdl / n_simulations,
    }


# ---------------------------------------------------------------------------
# T2: Type-I on adaptive tree with honest data-splitting
# ---------------------------------------------------------------------------

def t2_adaptive_tree_typeI(
    n_simulations: int = 2000,
    branch_factors: tuple[int, ...] = (5, 4, 3),
    tau_train: int = 500,
    tau_test: int = 500,
    alpha: float = 0.05,
    seed: int = 2026,
) -> dict:
    """Adaptive researcher:
      - At each level, has branch_factors[depth] alternatives
      - Computes in-sample Sharpe on train data, picks the best
      - Continues to the next level on the chosen strategy
      - At the leaf, reports the *test* Sharpe
    All strategies have true Sharpe = 0. With honest train/test split, the
    SVC verdict on the test Sharpe should respect Type-I.
    """
    rng = np.random.default_rng(seed)
    rejections_mdl = 0
    rejections_naive = 0
    rejections_grid_naive = 0
    total_grid_size = math.prod(branch_factors)

    for sim in range(n_simulations):
        # Simulate adaptive selection on train, evaluate on test
        # At each level we pick best-of-branch on TRAIN data (independent of test).
        # The leaf strategy gets a fresh test return stream of length tau_test.
        n_paths = total_grid_size  # number of possible final strategies
        # Generate train return for each candidate leaf (path-conditional but we
        # treat them as iid for simulation simplicity)
        train_returns = rng.normal(0.0, 0.01, size=(n_paths, tau_train))
        test_returns = rng.normal(0.0, 0.01, size=(n_paths, tau_test))
        train_sharpes = train_returns.mean(axis=1) / train_returns.std(axis=1, ddof=1)
        # Researcher picks the best leaf by training Sharpe; reports test Sharpe
        best_leaf = int(np.argmax(train_sharpes))
        reported = test_returns[best_leaf]

        # Build the trial-tree path the researcher actually traversed
        path = [
            TrialNode(f"depth_{d}", "h", 0, {}, "d", nu=nu)
            for d, nu in enumerate(branch_factors)
        ]
        svc = mdl_dsr(reported, path=path)
        if svc.mdl_dsr > 1 - alpha:
            rejections_mdl += 1

        naive = deflated_sharpe_ratio(reported, n_trials=1)
        if naive.dsr > 1 - alpha:
            rejections_naive += 1
        grid = deflated_sharpe_ratio(reported, n_trials=total_grid_size)
        if grid.dsr > 1 - alpha:
            rejections_grid_naive += 1

    return {
        "n_simulations": n_simulations,
        "branch_factors": list(branch_factors),
        "total_grid_size": total_grid_size,
        "tau_test": tau_test,
        "alpha": alpha,
        "type_I_naive_dsr": rejections_naive / n_simulations,
        "type_I_grid_dsr": rejections_grid_naive / n_simulations,
        "type_I_svc_mdl_dsr": rejections_mdl / n_simulations,
    }


# ---------------------------------------------------------------------------
# T3: Power on real edges
# ---------------------------------------------------------------------------

def t3_power(
    true_annual_sharpes: tuple[float, ...] = (0.5, 1.0, 1.5, 2.0, 3.0),
    n_simulations: int = 1000,
    K_alternatives: int = 50,
    tau: int = 500,
    alpha: float = 0.05,
    seed: int = 2026,
) -> dict:
    """One genuine edge strategy hides among K-1 noise strategies.
    Researcher reports best-of-K. We measure detection rate of the edge.
    """
    rng = np.random.default_rng(seed)
    sigma = 0.01
    powers = {}
    for true_sr in true_annual_sharpes:
        mu = (true_sr / math.sqrt(252)) * sigma
        edge_picked = 0
        edge_passed = 0
        for sim in range(n_simulations):
            returns = rng.normal(0.0, sigma, size=(K_alternatives, tau))
            returns[0] += mu   # strategy 0 has real edge
            sharpes = returns.mean(axis=1) / returns.std(axis=1, ddof=1)
            best_idx = int(np.argmax(sharpes))
            if best_idx == 0:
                edge_picked += 1
            best_returns = returns[best_idx]
            path = [TrialNode("flat", "h", 0, {}, "d", nu=K_alternatives)]
            svc = mdl_dsr(best_returns, path=path)
            if svc.mdl_dsr > 1 - alpha:
                edge_passed += 1
        powers[true_sr] = {
            "edge_picked_rate": edge_picked / n_simulations,
            "passes_svc_rate": edge_passed / n_simulations,
        }
    return {"n_simulations": n_simulations, "K": K_alternatives, "tau": tau, "powers": powers}


# ---------------------------------------------------------------------------
# T4: Calibration of E[SR_max | N]
# ---------------------------------------------------------------------------

def t4_calibration(
    N_values: tuple[int, ...] = (1, 10, 100, 1_000, 10_000),
    n_simulations: int = 3000,
    tau: int = 500,
    seed: int = 2026,
) -> dict:
    """For each N, draw N iid null Sharpes (with tau observations each),
    compute the empirical max-Sharpe. Compare to the Bailey-LdP prediction
    used inside MDL-DSR.
    """
    rng = np.random.default_rng(seed)
    out = {}
    for N in N_values:
        empirical_maxes = []
        for sim in range(n_simulations):
            R = rng.normal(0.0, 0.01, size=(N, tau))
            sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
            empirical_maxes.append(sharpes.max())
        emp_mean = float(np.mean(empirical_maxes))
        # Predicted by Bailey-LdP (per-period, sigma_SR ≈ 1/sqrt(tau-1))
        log2_N = math.log2(N) if N > 0 else 0.0
        var_for_em = 1.0 / (tau - 1)
        predicted = _expected_max_sharpe_logN(log2_N, var_for_em)
        out[N] = {
            "empirical_mean_max_sharpe": emp_mean,
            "predicted_mean_max_sharpe": predicted,
            "abs_error": abs(emp_mean - predicted),
            "relative_error": abs(emp_mean - predicted) / max(abs(predicted), 1e-9),
        }
    return {"n_simulations": n_simulations, "tau": tau, "by_N": out}


# ---------------------------------------------------------------------------
# Runner & report
# ---------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("SVC Empirical Validation — Monte Carlo Tests of Theorem 1")
    print("=" * 78)

    print("\n[T1] Type-I on flat tree...")
    r1 = t1_flat_tree_typeI()
    print(f"  K={r1['K']}, tau={r1['tau']}, alpha={r1['alpha']}, sims={r1['n_simulations']}")
    print(f"    Naive DSR Type-I: {r1['type_I_naive_dsr']:.4f}  "
          f"(target <= {r1['alpha']:.2f}, expected high)")
    print(f"    Grid  DSR Type-I: {r1['type_I_grid_dsr']:.4f}  "
          f"(target <= {r1['alpha']:.2f})")
    print(f"    SVC  MDL-DSR Type-I: {r1['type_I_svc_mdl_dsr']:.4f}  "
          f"(target <= {r1['alpha']:.2f})  *theorem's central claim*")

    print("\n[T2] Type-I on adaptive tree (honest data-splitting)...")
    r2 = t2_adaptive_tree_typeI()
    print(f"  branches={r2['branch_factors']}, total_grid={r2['total_grid_size']}, "
          f"alpha={r2['alpha']}, sims={r2['n_simulations']}")
    print(f"    Naive DSR Type-I: {r2['type_I_naive_dsr']:.4f}")
    print(f"    Grid  DSR Type-I (N=total_grid): {r2['type_I_grid_dsr']:.4f}")
    print(f"    SVC  MDL-DSR Type-I: {r2['type_I_svc_mdl_dsr']:.4f}  *theorem*")

    print("\n[T3] Power at various true Sharpes (K=50 alternatives)...")
    r3 = t3_power()
    print(f"  K={r3['K']}, tau={r3['tau']}, sims={r3['n_simulations']}")
    print(f"    true_SR  | edge_picked | passes_SVC")
    print(f"    ---------+-------------+-----------")
    for sr, d in r3["powers"].items():
        print(f"    {sr:6.2f}   |    {d['edge_picked_rate']:.3f}    |   "
              f"{d['passes_svc_rate']:.3f}")

    print("\n[T4] Calibration of E[SR_max | N] (per-period units)...")
    r4 = t4_calibration()
    print(f"  tau={r4['tau']}, sims={r4['n_simulations']}")
    print(f"      N    | empirical | predicted |  rel_err")
    print(f"    -------+-----------+-----------+--------")
    for N, d in r4["by_N"].items():
        print(f"    {N:>6} | {d['empirical_mean_max_sharpe']:.4f}    | "
              f"{d['predicted_mean_max_sharpe']:.4f}    |  "
              f"{d['relative_error']:.3f}")

    # Verdict
    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    t1_pass = r1["type_I_svc_mdl_dsr"] <= r1["alpha"] + 0.02
    t2_pass = r2["type_I_svc_mdl_dsr"] <= r2["alpha"] + 0.02
    # Exclude N=1 from calibration check: predicted is exactly 0 (max of 1 = 1),
    # so relative error is meaningless. Real calibration matters for N >= 10.
    t4_errors = [d["relative_error"] for N, d in r4["by_N"].items() if N >= 10]
    t4_pass = max(t4_errors) < 0.10
    print(f"  T1 (flat null Type-I):    {'PASS' if t1_pass else 'FAIL'}")
    print(f"  T2 (adaptive null Type-I): {'PASS' if t2_pass else 'FAIL'}")
    print(f"  T4 (E[SR_max] calibration): {'PASS' if t4_pass else 'FAIL'}")
    if t1_pass and t2_pass and t4_pass:
        print("\n  ** Theorem 1's central claims are empirically validated **")
    else:
        print("\n  ** Empirical validation reveals issues; theorem needs review **")

    # Write report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SVC A7 — Empirical Validation of Theorem 1\n",
        "Date: 2026-05-22\n",
        "Validates the central claims of Theorem 1 via Monte Carlo simulation. "
        "If empirical Type-I error on null worlds is ≤ alpha + MC error, the "
        "theorem's correctness claim is empirically supported.\n",
        "## T1 — Type-I error, flat tree, null world\n",
        f"Setup: K={r1['K']} iid null strategies, tau={r1['tau']} obs each, "
        f"alpha={r1['alpha']}, {r1['n_simulations']} simulations.\n",
        "| Statistic | Empirical Type-I | Target |",
        "|---|---:|---:|",
        f"| Naive DSR (N=1) | {r1['type_I_naive_dsr']:.4f} | ≤ {r1['alpha']:.2f} |",
        f"| Grid  DSR (N=K) | {r1['type_I_grid_dsr']:.4f} | ≤ {r1['alpha']:.2f} |",
        f"| **SVC MDL-DSR** | **{r1['type_I_svc_mdl_dsr']:.4f}** | **≤ {r1['alpha']:.2f}** |",
        "",
        "## T2 — Type-I error, adaptive tree, null world\n",
        f"Setup: branching factors {r2['branch_factors']} = total {r2['total_grid_size']} leaves, "
        f"adaptive selection on train, evaluation on test, {r2['n_simulations']} sims.\n",
        "| Statistic | Empirical Type-I |",
        "|---|---:|",
        f"| Naive DSR | {r2['type_I_naive_dsr']:.4f} |",
        f"| Grid  DSR (N=grid total) | {r2['type_I_grid_dsr']:.4f} |",
        f"| **SVC MDL-DSR** | **{r2['type_I_svc_mdl_dsr']:.4f}** |",
        "",
        "## T3 — Power on real edges\n",
        f"Setup: one true-edge strategy among K={r3['K']}, tau={r3['tau']}, "
        f"{r3['n_simulations']} simulations.\n",
        "| true SR (annual) | edge picked from K | passes SVC |",
        "|---:|---:|---:|",
    ]
    for sr, d in r3["powers"].items():
        lines.append(f"| {sr:.2f} | {d['edge_picked_rate']:.3f} | {d['passes_svc_rate']:.3f} |")

    lines.extend([
        "",
        "## T4 — Calibration of E[SR_max | N]\n",
        f"Empirical vs predicted maximum Sharpe of N iid null strategies, tau={r4['tau']}, "
        f"{r4['n_simulations']} sims per N.\n",
        "| N | empirical mean max | predicted (Bailey-LdP) | relative error |",
        "|---:|---:|---:|---:|",
    ])
    for N, d in r4["by_N"].items():
        lines.append(
            f"| {N} | {d['empirical_mean_max_sharpe']:.4f} | "
            f"{d['predicted_mean_max_sharpe']:.4f} | "
            f"{d['relative_error']:.3f} |"
        )
    lines.extend([
        "",
        "## Verdict\n",
        f"- T1 (flat null Type-I): {'**PASS**' if t1_pass else '**FAIL**'} — "
        f"observed {r1['type_I_svc_mdl_dsr']:.4f} vs target ≤ {r1['alpha']:.2f}",
        f"- T2 (adaptive null Type-I): {'**PASS**' if t2_pass else '**FAIL**'} — "
        f"observed {r2['type_I_svc_mdl_dsr']:.4f} vs target ≤ {r2['alpha']:.2f}",
        f"- T4 (E[SR_max] calibration): {'**PASS**' if t4_pass else '**FAIL**'} — "
        f"max relative error {max(d['relative_error'] for d in r4['by_N'].values()):.3f}",
        "",
        "**Conclusion:** "
        + (
            "Theorem 1's central claims are empirically supported on the tested scenarios."
            if (t1_pass and t2_pass and t4_pass)
            else "Empirical validation reveals issues that must be addressed in the proof."
        ),
    ])
    REPORT.write_text("\n".join(lines))
    print(f"\nReport written: {REPORT}")


if __name__ == "__main__":
    main()
