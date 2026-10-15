"""V2 — Head-to-head comparison: SVC vs classical multiple-testing methods.

Compares Type-I control and power on identical scenarios across:
  M0  Naive Sharpe test (no correction)
  M1  Bonferroni (parametric, conservative)
  M2  Bailey-LdP DSR (extreme-value parametric)
  M3  SVC MDL-DSR (extreme-value + tree-aware)
  M4  Bootstrap max-Sharpe quantile (non-parametric, captures correlation)
  M5  Permutation max-Sharpe quantile (non-parametric, exact)

Scenarios:
  S1 iid null, K=50
  S2 correlated null, K=50, rho=0.5
  S3 real edge true_SR ∈ {1, 2, 3}

A method that controls Type-I on S1/S2 AND has high power on S3 is best.
Bootstrap/Permutation typically need more compute but can outperform
parametric methods under non-iid trials.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.validation import TrialNode, mdl_dsr  # noqa: E402

REPORT = ROOT / "research" / "phase11_svc" / "V2_head_to_head.md"


# Methods return reject(boolean) given observed SR, the full trial matrix, K, alpha
# We pass the full matrix so methods that need it (bootstrap, permutation) can use it.

def method_naive(best_sr: float, R: np.ndarray, alpha: float) -> bool:
    """No correction. Reject if standardised SR > Φ^{-1}(1-α)."""
    n = R.shape[1]
    sigma_sr = 1.0 / math.sqrt(n - 1)
    return best_sr > sigma_sr * norm.ppf(1 - alpha)


def method_bonferroni(best_sr: float, R: np.ndarray, alpha: float) -> bool:
    K, n = R.shape
    sigma_sr = 1.0 / math.sqrt(n - 1)
    return best_sr > sigma_sr * norm.ppf(1 - alpha / K)


def method_bailey_ldp(best_sr: float, R: np.ndarray, alpha: float) -> bool:
    """Parametric extreme-value deflation (Bailey-LdP)."""
    K, n = R.shape
    sigma_sr = 1.0 / math.sqrt(n - 1)
    # E[max] under N=K
    z1 = norm.ppf(1 - 1.0 / K)
    z2 = norm.ppf(1 - 1.0 / (K * math.e))
    em = (1 - 0.5772) * z1 + 0.5772 * z2
    expected_max = sigma_sr * em
    return best_sr > expected_max + sigma_sr * norm.ppf(1 - alpha)


def method_svc(best_sr: float, R: np.ndarray, alpha: float,
               best_returns: np.ndarray, K_strategy_bits: int = 0) -> bool:
    """SVC with the same N as Bailey-LdP (flat tree, N_bp=K).

    Passes sharpe_variance_across_trials=1/(τ-1) explicitly so the comparison
    against Bailey-LdP DSR is apples-to-apples (both use the iid Gaussian
    lower bound on Sharpe variance).
    """
    K, tau = R.shape
    path = [TrialNode("root", "h", K_strategy_bits, {}, "d", nu=K)]
    res = mdl_dsr(
        best_returns, path=path,
        sharpe_variance_across_trials=1.0 / (tau - 1),
    )
    return res.mdl_dsr > 1 - alpha


def method_bootstrap(best_sr: float, R: np.ndarray, alpha: float,
                     n_bootstrap: int = 200, rng=None) -> bool:
    """Bootstrap the null distribution of max-Sharpe by resampling the rows
    of R with replacement (preserving correlation structure across columns).
    Reject if observed best_sr > 1-alpha quantile of bootstrap max-Sharpes.
    """
    if rng is None:
        rng = np.random.default_rng(42)
    K, n = R.shape
    # Demean each strategy to simulate the null
    R0 = R - R.mean(axis=1, keepdims=True)
    boot_maxes = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        Rb = R0[:, idx]
        sharpes = Rb.mean(axis=1) / np.where(Rb.std(axis=1, ddof=1) > 0, Rb.std(axis=1, ddof=1), 1.0)
        boot_maxes[b] = sharpes.max()
    threshold = np.quantile(boot_maxes, 1 - alpha)
    return best_sr > threshold


def method_permutation_signflip(best_sr: float, R: np.ndarray, alpha: float,
                                 n_permutations: int = 200, rng=None) -> bool:
    """Sign-flip permutation test for the null Sharpe distribution.

    Under H_0 (zero mean returns), the distribution of returns is symmetric
    around zero (approximately, for daily returns). Sign-flipping each
    observation is therefore valid: returns and -returns are exchangeable
    under H_0. This generates a proper null distribution of max-Sharpe.

    (The naive row-permutation approach is invalid because Sharpe is
    order-invariant — permuting time within a strategy doesn't change SR.)
    """
    if rng is None:
        rng = np.random.default_rng(42)
    K, n = R.shape
    R0 = R - R.mean(axis=1, keepdims=True)  # centre under H_0
    perm_maxes = np.empty(n_permutations)
    for p in range(n_permutations):
        signs = rng.choice([-1.0, 1.0], size=(K, n))
        Rp = R0 * signs
        sds = Rp.std(axis=1, ddof=1)
        sharpes = Rp.mean(axis=1) / np.where(sds > 0, sds, 1.0)
        perm_maxes[p] = sharpes.max()
    threshold = np.quantile(perm_maxes, 1 - alpha)
    return best_sr > threshold


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------

def scenario_iid_null(K: int, tau: int, rng) -> np.ndarray:
    return rng.normal(0.0, 0.01, size=(K, tau))


def scenario_correlated_null(K: int, tau: int, rng, rho: float = 0.5) -> np.ndarray:
    a = math.sqrt(rho)
    common = rng.normal(0.0, 0.01, size=tau)
    idio = rng.normal(0.0, 0.01, size=(K, tau))
    return a * common + math.sqrt(1 - rho) * idio


def scenario_edge(K: int, tau: int, rng, true_sr_annual: float) -> tuple[np.ndarray, int]:
    sigma = 0.01
    mu = (true_sr_annual / math.sqrt(252)) * sigma
    R = rng.normal(0.0, sigma, size=(K, tau))
    R[0] += mu
    return R, 0


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_one(R: np.ndarray, alpha: float, rng) -> dict:
    sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
    best_idx = int(np.argmax(sharpes))
    best_sr = float(sharpes[best_idx])
    best_returns = R[best_idx]
    return {
        "naive": method_naive(best_sr, R, alpha),
        "bonferroni": method_bonferroni(best_sr, R, alpha),
        "bailey_ldp": method_bailey_ldp(best_sr, R, alpha),
        "svc": method_svc(best_sr, R, alpha, best_returns),
        "bootstrap": method_bootstrap(best_sr, R, alpha, rng=rng),
        "permutation": method_permutation_signflip(best_sr, R, alpha, rng=rng),
    }


def main():
    alpha = 0.05
    K = 50
    tau = 500
    n_sims_null = 500    # fewer due to bootstrap/permutation cost
    n_sims_edge = 500

    print(f"V2 — Head-to-Head (K={K}, tau={tau}, alpha={alpha}, sims={n_sims_null})\n")

    rng_master = np.random.default_rng(20260522)
    methods = ["naive", "bonferroni", "bailey_ldp", "svc", "bootstrap", "permutation"]

    results = {}

    print("[S1] iid null")
    rng = np.random.default_rng(rng_master.integers(0, 2**31))
    counts = {m: 0 for m in methods}
    for _ in range(n_sims_null):
        R = scenario_iid_null(K, tau, rng)
        out = run_one(R, alpha, rng)
        for m, v in out.items():
            counts[m] += int(v)
    results["S1 iid null"] = {m: c / n_sims_null for m, c in counts.items()}
    print(f"  {results['S1 iid null']}")

    print("\n[S2] correlated null (rho=0.5)")
    rng = np.random.default_rng(rng_master.integers(0, 2**31))
    counts = {m: 0 for m in methods}
    for _ in range(n_sims_null):
        R = scenario_correlated_null(K, tau, rng, rho=0.5)
        out = run_one(R, alpha, rng)
        for m, v in out.items():
            counts[m] += int(v)
    results["S2 corr null"] = {m: c / n_sims_null for m, c in counts.items()}
    print(f"  {results['S2 corr null']}")

    for true_sr in (1.5, 2.0, 3.0):
        print(f"\n[S3 true_sr={true_sr}] real edge")
        rng = np.random.default_rng(rng_master.integers(0, 2**31))
        counts = {m: 0 for m in methods}
        for _ in range(n_sims_edge):
            R, _ = scenario_edge(K, tau, rng, true_sr_annual=true_sr)
            out = run_one(R, alpha, rng)
            for m, v in out.items():
                counts[m] += int(v)
        results[f"S3 SR={true_sr}"] = {m: c / n_sims_edge for m, c in counts.items()}
        print(f"  {results[f'S3 SR={true_sr}']}")

    # Format the report
    lines = [
        "# V2 — Head-to-Head Comparison Battery\n",
        "Date: 2026-05-22\n",
        f"**Setup:** K={K}, τ={tau}, α={alpha}, {n_sims_null} null sims / {n_sims_edge} edge sims, "
        f"bootstrap & permutation use 200 resamples each.\n",
        "## Type-I (should be ≤ α=0.05)\n",
        "| Method | iid null | correlated null (ρ=0.5) |",
        "|---|---:|---:|",
    ]
    for m in methods:
        lines.append(f"| {m} | {results['S1 iid null'][m]:.4f} | "
                     f"{results['S2 corr null'][m]:.4f} |")

    lines.extend([
        "",
        "## Power (higher is better, given Type-I controlled)\n",
        "| Method | true SR=1.5 | true SR=2.0 | true SR=3.0 |",
        "|---|---:|---:|---:|",
    ])
    for m in methods:
        lines.append(
            f"| {m} | {results['S3 SR=1.5'][m]:.4f} | "
            f"{results['S3 SR=2.0'][m]:.4f} | {results['S3 SR=3.0'][m]:.4f} |"
        )

    # Verdict per method
    lines.extend([
        "",
        "## Per-method verdict\n",
        "| Method | Controls Type-I? | Power at SR=2.0 | Notes |",
        "|---|---|---:|---|",
    ])
    for m in methods:
        controls = (results["S1 iid null"][m] <= alpha + 0.02
                    and results["S2 corr null"][m] <= alpha + 0.02)
        controls_str = "✅" if controls else "❌"
        note = {
            "naive": "Should fail Type-I dramatically — the bar everyone else has to beat",
            "bonferroni": "Conservative parametric — usually controls Type-I but loses power",
            "bailey_ldp": "Static-N parametric extreme value — should match SVC for flat trees",
            "svc": "**Our framework** — should match bailey_ldp here (same N for flat tree)",
            "bootstrap": "Non-parametric, captures correlation — may have higher power on S2",
            "permutation": "Non-parametric exact — gold-standard but computationally heavy",
        }[m]
        lines.append(f"| {m} | {controls_str} | {results['S3 SR=2.0'][m]:.4f} | {note} |")
    lines.extend([
        "",
        "## Interpretation\n",
        "For a *flat trial-tree* (the scenario tested here), SVC reduces to Bailey-LdP DSR; they "
        "should produce identical verdicts. SVC's *unique* value over Bailey-LdP appears when "
        "the tree is non-trivial — see the V1.5 wedge experiment (A8a). What V2 tests is whether "
        "SVC is at least as good as the established alternatives in the baseline (flat) case.",
        "",
        "Bootstrap and permutation, being non-parametric, may show different behavior under "
        "correlation (S2). If they reject substantially more often than SVC on S2, that suggests "
        "SVC's parametric extreme-value formula is over-conservative when trials are positively "
        "correlated.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
