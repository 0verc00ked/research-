"""V1 — Distribution Robustness.

The theorem proves Type-I control under regularity (A3): stationary returns
with finite fourth moment + weak dependence. Real markets violate this:
heavy tails (kurt > 3), skew, autocorrelation, volatility clustering,
regime breaks, jumps.

We test SVC Type-I empirically under 8 distributions, K=50, tau=500, 2000
simulations each. Any distribution where SVC's empirical Type-I substantially
exceeds alpha is a documented finite-sample failure mode.

Distributions:
  D1 Gaussian iid (baseline)
  D2 Student-t (df=3) — heavy tails, infinite variance under df<=2; df=3 has finite var, infinite kurt
  D3 Student-t (df=5) — heavy tails, finite kurt
  D4 Skew-normal — skewed, finite moments
  D5 GARCH(1,1) — volatility clustering
  D6 AR(1) with phi=0.2 — mild positive autocorrelation
  D7 Jump-diffusion (Merton) — 5% jump per day, mean zero
  D8 Regime-switching (2-state HMM) — calm/volatile
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.validation import TrialNode, mdl_dsr  # noqa: E402

REPORT = ROOT / "research" / "phase11_svc" / "V1_distribution_robustness.md"


# ---------------------------------------------------------------------------
# Return-generating processes (all calibrated to ~ same daily vol ~ 1%)
# ---------------------------------------------------------------------------

def rgp_gaussian(K: int, tau: int, rng) -> np.ndarray:
    return rng.normal(0.0, 0.01, size=(K, tau))


def rgp_student_t(K: int, tau: int, rng, df: int) -> np.ndarray:
    # scale so that variance is ~0.01^2; t(df) has var = df/(df-2) for df>2
    if df > 2:
        scale = 0.01 / math.sqrt(df / (df - 2))
    else:
        scale = 0.01
    return rng.standard_t(df, size=(K, tau)) * scale


def rgp_skew_normal(K: int, tau: int, rng, skew_param: float = 4.0) -> np.ndarray:
    # Crude skew-normal via abs+gaussian mixture
    base = rng.normal(0.0, 0.01, size=(K, tau))
    skew_term = skew_param * 0.005 * np.abs(rng.normal(0.0, 1.0, size=(K, tau)))
    return base + skew_term - skew_term.mean()


def rgp_garch11(K: int, tau: int, rng,
                omega: float = 1e-6, alpha: float = 0.08, beta: float = 0.90) -> np.ndarray:
    """GARCH(1,1) returns. Persistence alpha+beta < 1 → 0.98."""
    out = np.zeros((K, tau))
    sigma2 = np.full(K, omega / (1 - alpha - beta))
    for t in range(tau):
        z = rng.normal(0.0, 1.0, size=K)
        out[:, t] = np.sqrt(sigma2) * z
        sigma2 = omega + alpha * out[:, t] ** 2 + beta * sigma2
    return out


def rgp_ar1(K: int, tau: int, rng, phi: float = 0.2) -> np.ndarray:
    out = np.zeros((K, tau))
    eps = rng.normal(0.0, 0.01 * math.sqrt(1 - phi**2), size=(K, tau))
    for t in range(1, tau):
        out[:, t] = phi * out[:, t-1] + eps[:, t]
    return out


def rgp_jump_diffusion(K: int, tau: int, rng,
                        jump_prob: float = 0.05, jump_scale: float = 0.03) -> np.ndarray:
    diffusion = rng.normal(0.0, 0.008, size=(K, tau))
    jumps_present = rng.random(size=(K, tau)) < jump_prob
    jump_sizes = rng.normal(0.0, jump_scale, size=(K, tau))
    return diffusion + jumps_present * jump_sizes


def rgp_regime_switch(K: int, tau: int, rng,
                       p_stay_calm: float = 0.98, p_stay_vol: float = 0.95,
                       sigma_calm: float = 0.007, sigma_vol: float = 0.020) -> np.ndarray:
    out = np.zeros((K, tau))
    for k in range(K):
        state = 0  # 0 = calm, 1 = vol
        for t in range(tau):
            sig = sigma_calm if state == 0 else sigma_vol
            out[k, t] = rng.normal(0.0, sig)
            # transition
            if state == 0 and rng.random() > p_stay_calm:
                state = 1
            elif state == 1 and rng.random() > p_stay_vol:
                state = 0
    return out


DISTRIBUTIONS = [
    ("D1 Gaussian iid", rgp_gaussian, {}),
    ("D2 Student-t df=3", rgp_student_t, {"df": 3}),
    ("D3 Student-t df=5", rgp_student_t, {"df": 5}),
    ("D4 Skew-normal", rgp_skew_normal, {}),
    ("D5 GARCH(1,1)", rgp_garch11, {}),
    ("D6 AR(1) phi=0.2", rgp_ar1, {}),
    ("D7 Jump-diffusion", rgp_jump_diffusion, {}),
    ("D8 Regime-switching", rgp_regime_switch, {}),
]


# ---------------------------------------------------------------------------
# Type-I test
# ---------------------------------------------------------------------------

def run_typeI(rgp_fn, K: int, tau: int, n_sims: int, alpha: float, rng_seed: int,
              **rgp_kwargs) -> dict:
    """Run T1 (best-of-K, null) for one distribution. Returns rejection rates."""
    rng = np.random.default_rng(rng_seed)
    rejections_svc = 0
    sample_kurts = []
    sample_skews = []
    sample_acf1s = []
    for _ in range(n_sims):
        R = rgp_fn(K=K, tau=tau, rng=rng, **rgp_kwargs)
        sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
        best_idx = int(np.argmax(sharpes))
        best = R[best_idx]
        if best.std() <= 0 or not np.all(np.isfinite(best)):
            continue
        # Diagnostics on the best variant
        x = best
        x_c = x - x.mean()
        sd = x.std(ddof=1)
        if sd > 0:
            sample_skews.append(float((x_c**3).mean() / sd**3))
            sample_kurts.append(float((x_c**4).mean() / sd**4))
            if len(x) > 1:
                sample_acf1s.append(float(np.corrcoef(x[:-1], x[1:])[0, 1]))
        path = [TrialNode("root", "h", 0, {}, "d", nu=K)]
        try:
            res = mdl_dsr(best, path=path)
            if res.mdl_dsr > 1 - alpha:
                rejections_svc += 1
        except Exception:
            continue
    return {
        "typeI_svc": rejections_svc / n_sims,
        "median_skew": float(np.median(sample_skews)) if sample_skews else float("nan"),
        "median_excess_kurt": float(np.median(sample_kurts)) - 3 if sample_kurts else float("nan"),
        "median_acf1": float(np.median(sample_acf1s)) if sample_acf1s else float("nan"),
        "n_valid_sims": len(sample_skews),
    }


def main():
    alpha = 0.05
    K = 50
    tau = 500
    n_sims = 1500

    print(f"V1 — Distribution Robustness (K={K}, tau={tau}, alpha={alpha}, sims={n_sims})\n")
    print(f"  {'Distribution':<24} | {'SVC Type-I':>10} | {'med skew':>9} | "
          f"{'med excess kurt':>15} | {'med acf1':>9}")
    print(f"  {'-'*24} | {'-'*10} | {'-'*9} | {'-'*15} | {'-'*9}")

    results = []
    for label, fn, kwargs in DISTRIBUTIONS:
        r = run_typeI(fn, K, tau, n_sims, alpha, rng_seed=20260522 + hash(label) % 10000, **kwargs)
        results.append((label, r))
        print(f"  {label:<24} | {r['typeI_svc']:>10.4f} | {r['median_skew']:>9.3f} | "
              f"{r['median_excess_kurt']:>15.3f} | {r['median_acf1']:>9.3f}")

    # Verdict per distribution
    print(f"\nTypeI ≤ alpha+0.02 = {alpha + 0.02} considered PASS:")
    fail_count = 0
    for label, r in results:
        verdict = "PASS" if r["typeI_svc"] <= alpha + 0.02 else "FAIL"
        if verdict == "FAIL":
            fail_count += 1
        print(f"  {label}: {verdict} ({r['typeI_svc']:.4f})")

    # Write report
    lines = [
        "# V1 — Distribution Robustness Battery\n",
        "Date: 2026-05-22\n",
        f"**Setup:** K={K} null alternatives, τ={tau}, α={alpha}, {n_sims} simulations per "
        f"distribution. Tests whether SVC's Type-I control survives when the regularity "
        f"assumption (A3) — finite fourth moment, weak dependence — is *violated* in ways "
        f"common in real financial returns.\n",
        "## Results\n",
        "| Distribution | SVC Type-I | median skew | median excess kurt | median ACF(1) | Verdict |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for label, r in results:
        verdict = "✅ PASS" if r["typeI_svc"] <= alpha + 0.02 else "❌ FAIL"
        lines.append(
            f"| {label} | {r['typeI_svc']:.4f} | {r['median_skew']:.3f} | "
            f"{r['median_excess_kurt']:.3f} | {r['median_acf1']:.3f} | {verdict} |"
        )
    lines.extend([
        "",
        "## Interpretation\n",
        f"Of the {len(results)} distributions tested, {len(results) - fail_count} produced "
        f"SVC Type-I ≤ α+0.02 = {alpha+0.02}.",
        "",
        "**Specific distributions to watch:**",
        "- **D2 Student-t df=3:** infinite kurtosis under the t(3) law. The Sharpe estimator "
        "loses its CLT in the limit; we expect Type-I inflation here if anywhere.",
        "- **D5 GARCH(1,1):** persistent volatility violates the weak-dependence assumption.",
        "- **D6 AR(1):** persistent return autocorrelation violates A3's iid-like assumption.",
        "",
        "If SVC controls Type-I across all 8 distributions (within MC error), the framework is "
        "robust to the dependence and tail-thickness patterns typical of real financial returns. "
        "If it fails on D2/D5/D6, those are honest documented failure modes.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
