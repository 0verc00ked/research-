"""L5 — Power-improvement variants of SVC.

Section 7.5.1 documented SVC's low power. We explore four variants that
might preserve Type-I while gaining power:

  V1. Adaptive cross-trial variance — compute σ²_SR from the empirically
      observed Sharpes in the tree, not from the iid assumption σ² = 1/τ.
      Under correlation (real backtests share data), empirical σ²_SR can
      be much smaller, giving a tighter and more powerful threshold.

  V2. Sidak correction instead of Bonferroni — uses α_Sidak = 1 - (1-α)^(1/N)
      instead of α/N. Tighter under independence; equivalent at small α.

  V3. Half-Kraft — uses N_eff_v3 = N_bp · 2^(K/2). The argument: Kraft's
      2^K bound assumes EVERY codeword decodes to a valid strategy, which
      is false in practice (most byte sequences are syntactically invalid).
      Half the bits gives a (still loose but tighter) bound.

  V4. Bayesian Sharpe credible interval — instead of point-estimate
      threshold, use the lower bound of an approximate Bayesian credible
      interval on true Sharpe. Equivalent to original DSR under flat prior
      but generalises.

For each variant, test on:
  S1 (null, iid trials):  Type-I should still be ≤ α
  S2 (null, correlated):  Type-I should still be ≤ α (key for V1)
  S3 (real edge):         Power should be > baseline SVC

Any variant that passes S1 AND S2 (Type-I control) AND beats baseline on
S3 (power) is a real improvement.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.validation import TrialNode  # noqa: E402
from agent_trader.validation.svc import (  # noqa: E402
    _expected_max_sharpe_logN,
    log2_effective_N,
    mdl_dsr,
)
from agent_trader.validation.dsr import EULER_MASCHERONI  # noqa: E402

REPORT = ROOT / "research" / "phase11_svc" / "A8c_power_variants.md"


# ---------------------------------------------------------------------------
# Variants — return boolean reject-at-alpha
# ---------------------------------------------------------------------------

def baseline_svc_reject(returns: np.ndarray, path: list[TrialNode], alpha: float) -> bool:
    r = mdl_dsr(returns, path=path)
    return r.mdl_dsr > 1 - alpha


def variant_v1_adaptive_var_reject(
    returns: np.ndarray, path: list[TrialNode], alpha: float,
    all_trial_sharpes: np.ndarray,
) -> bool:
    """V1: use empirical cross-trial Sharpe variance instead of 1/tau."""
    if len(all_trial_sharpes) < 5:
        emp_var = 1.0 / max(len(returns), 2)
    else:
        emp_var = float(np.var(all_trial_sharpes, ddof=1))
        # don't go below the iid lower bound
        emp_var = max(emp_var, 1.0 / len(returns))
    r = mdl_dsr(
        returns, path=path,
        sharpe_variance_across_trials=emp_var,
    )
    return r.mdl_dsr > 1 - alpha


def variant_v3_half_kraft_reject(
    returns: np.ndarray, path: list[TrialNode], alpha: float,
) -> bool:
    """V3: halve K in N_eff. Same MDL-DSR structure, smaller K factor."""
    # build a half-K version of the path
    half_path = [
        TrialNode(p.strategy_name, p.code_hash, p.code_length // 2,
                  p.params, p.dataset_hash, nu=p.nu)
        for p in path
    ]
    r = mdl_dsr(returns, path=half_path)
    return r.mdl_dsr > 1 - alpha


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

def scenario_iid_null(K: int, tau: int, rng) -> tuple[np.ndarray, np.ndarray]:
    """K iid null strategies. Return (best_returns, all_sharpes)."""
    R = rng.normal(0.0, 0.01, size=(K, tau))
    sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
    best = R[int(np.argmax(sharpes))]
    return best, sharpes


def scenario_correlated_null(K: int, tau: int, rng, rho: float = 0.5) -> tuple[np.ndarray, np.ndarray]:
    """K null strategies with cross-strategy correlation rho.

    Model: each strategy is alpha * common_factor + sqrt(1-alpha^2) * idio
    where alpha = sqrt(rho).
    """
    alpha_corr = math.sqrt(rho)
    common = rng.normal(0.0, 0.01, size=tau)
    idio = rng.normal(0.0, 0.01, size=(K, tau))
    R = alpha_corr * common + math.sqrt(1 - rho) * idio
    sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
    best = R[int(np.argmax(sharpes))]
    return best, sharpes


def scenario_real_edge(K: int, tau: int, true_annual_sr: float, rng) -> tuple[np.ndarray, np.ndarray]:
    """One genuine edge among K-1 nulls."""
    sigma = 0.01
    mu = (true_annual_sr / math.sqrt(252)) * sigma
    R = rng.normal(0.0, sigma, size=(K, tau))
    R[0] += mu
    sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
    best_idx = int(np.argmax(sharpes))
    return R[best_idx], sharpes


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_scenario(
    label: str,
    scenario_fn,
    n_simulations: int,
    K: int,
    tau: int,
    alpha: float,
    K_strategy_bits: int = 30,
    extra_args: dict | None = None,
) -> dict:
    rng = np.random.default_rng(20260522)
    rej_base = rej_v1 = rej_v3 = 0
    for _ in range(n_simulations):
        kwargs = dict(K=K, tau=tau, rng=rng)
        kwargs.update(extra_args or {})
        best, all_sr = scenario_fn(**kwargs)
        path = [TrialNode("root", "h", K_strategy_bits, {}, "d", nu=K)]
        if baseline_svc_reject(best, path, alpha):
            rej_base += 1
        if variant_v1_adaptive_var_reject(best, path, alpha, all_sr):
            rej_v1 += 1
        if variant_v3_half_kraft_reject(best, path, alpha):
            rej_v3 += 1
    return {
        "label": label,
        "n": n_simulations,
        "baseline": rej_base / n_simulations,
        "v1_adaptive_var": rej_v1 / n_simulations,
        "v3_half_kraft": rej_v3 / n_simulations,
    }


def main():
    alpha = 0.05
    K = 50
    tau = 500
    n_sims = 1500
    K_strategy_bits = 0   # focus on the branching factor only
    print(f"Setup: K={K}, tau={tau}, alpha={alpha}, sims={n_sims}, K_strategy_bits={K_strategy_bits}\n")

    results = []
    print("[S1] iid null world (Type-I should ≤ alpha)")
    r = run_scenario("S1 iid null", scenario_iid_null, n_sims, K, tau, alpha,
                     K_strategy_bits=K_strategy_bits)
    print(f"  baseline = {r['baseline']:.4f}  V1 = {r['v1_adaptive_var']:.4f}  "
          f"V3 = {r['v3_half_kraft']:.4f}")
    results.append(r)

    print("\n[S2] correlated null world (rho=0.5)")
    r = run_scenario("S2 correlated null", scenario_correlated_null, n_sims, K, tau, alpha,
                     K_strategy_bits=K_strategy_bits, extra_args={"rho": 0.5})
    print(f"  baseline = {r['baseline']:.4f}  V1 = {r['v1_adaptive_var']:.4f}  "
          f"V3 = {r['v3_half_kraft']:.4f}")
    results.append(r)

    print("\n[S3] real edge at varying true Sharpe")
    s3_results = []
    for true_sr in (1.0, 1.5, 2.0, 3.0):
        r = run_scenario(
            f"S3 true_sr={true_sr}", scenario_real_edge, n_sims, K, tau, alpha,
            K_strategy_bits=K_strategy_bits,
            extra_args={"true_annual_sr": true_sr},
        )
        s3_results.append((true_sr, r))
        print(f"  true_SR={true_sr}: baseline = {r['baseline']:.4f}  "
              f"V1 = {r['v1_adaptive_var']:.4f}  V3 = {r['v3_half_kraft']:.4f}")

    # Verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    s1, s2 = results[0], results[1]

    def verdict_for(variant_key: str) -> str:
        type_I_iid = s1[variant_key]
        type_I_corr = s2[variant_key]
        baseline_power = sum(r["baseline"] for _, r in s3_results) / len(s3_results)
        variant_power = sum(r[variant_key] for _, r in s3_results) / len(s3_results)
        controls_typeI = type_I_iid <= alpha + 0.02 and type_I_corr <= alpha + 0.02
        gains_power = variant_power > baseline_power + 0.01
        if controls_typeI and gains_power:
            return f"IMPROVEMENT (Type-I {type_I_iid:.3f}/{type_I_corr:.3f}, avg power {variant_power:.3f} vs {baseline_power:.3f})"
        if controls_typeI:
            return f"safe but no power gain (Type-I {type_I_iid:.3f}/{type_I_corr:.3f}, avg power {variant_power:.3f} vs {baseline_power:.3f})"
        return f"BREAKS Type-I (Type-I {type_I_iid:.3f}/{type_I_corr:.3f})"

    print(f"  V1 (adaptive variance): {verdict_for('v1_adaptive_var')}")
    print(f"  V3 (half Kraft):        {verdict_for('v3_half_kraft')}")

    # Report
    lines = [
        "# SVC A8c — Power-improvement variants\n",
        "Date: 2026-05-22\n",
        f"Setup: K={K} alternatives, tau={tau}, alpha={alpha}, {n_sims} sims per cell.\n",
        "## Variants\n",
        "- **V1 — Adaptive variance:** use empirical cross-trial Sharpe variance instead "
        "of the iid lower bound σ² = 1/τ.",
        "- **V3 — Half-Kraft:** use K/2 instead of K. Kraft's bound is very loose for "
        "natural strategies; halving acknowledges this.",
        "",
        "## Type-I results (null worlds)\n",
        "| Scenario | Baseline | V1 adaptive var | V3 half-Kraft |",
        "|---|---:|---:|---:|",
        f"| S1 iid null | {s1['baseline']:.4f} | {s1['v1_adaptive_var']:.4f} | "
        f"{s1['v3_half_kraft']:.4f} |",
        f"| S2 correlated null (ρ=0.5) | {s2['baseline']:.4f} | {s2['v1_adaptive_var']:.4f} | "
        f"{s2['v3_half_kraft']:.4f} |",
        "",
        "## Power results (real edge)\n",
        "| true SR | Baseline | V1 adaptive var | V3 half-Kraft |",
        "|---:|---:|---:|---:|",
    ]
    for true_sr, r in s3_results:
        lines.append(f"| {true_sr} | {r['baseline']:.4f} | {r['v1_adaptive_var']:.4f} | "
                     f"{r['v3_half_kraft']:.4f} |")
    lines.extend([
        "",
        "## Verdict\n",
        f"- **V1 adaptive variance:** {verdict_for('v1_adaptive_var')}",
        f"- **V3 half-Kraft:**         {verdict_for('v3_half_kraft')}",
        "",
        "## Interpretation\n",
        "An 'IMPROVEMENT' verdict means the variant preserves Type-I control on both null "
        "scenarios AND beats baseline average power on the real-edge scenarios.",
        "",
        "If no variant produces an IMPROVEMENT verdict, the conclusion is that SVC's "
        "baseline tradeoff is near-Pareto-optimal: you can buy power only by relaxing "
        "Type-I, and the existing calibration is on the right side of the frontier for "
        "the retail-validation use case.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
