"""V5 — Edge cases and numerical stability.

Tests that SVC's implementation gracefully handles extreme parameter values
without numerical failure, silent wrong answers, or assertion errors.

Cases:
  E1  K_strategy_bits = 0 (no parameter complexity)
  E2  K_strategy_bits = 10000 (extreme complexity → log2_N = 10000)
  E3  τ = 30 (minimum allowed by mdl_dsr; n<30 raises)
  E4  τ = 100,000 (very long sample)
  E5  Single-trial tree (root only, no branching)
  E6  Very deep tree (depth 100)
  E7  Very wide tree (single root with ν=1000)
  E8  Near-zero variance (returns are essentially constant)
  E9  Returns with all-zero std (degenerate)
  E10 Mixed positive/negative log2_N components

For each case: does SVC return finite, in-range values? Does it crash?
Does it produce something sensible? We check both numerical integrity and
qualitative correctness.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.validation import (  # noqa: E402
    TrialNode,
    branching_product,
    effective_N,
    log2_effective_N,
    mdl_dsr,
)

REPORT = ROOT / "research" / "phase11_svc" / "V5_edge_cases.md"


def assert_finite_in_range(name: str, val: float, *, low: float = 0.0, high: float = 1.0) -> tuple[bool, str]:
    if not math.isfinite(val):
        return False, f"{name}={val} is not finite"
    if val < low - 1e-9 or val > high + 1e-9:
        return False, f"{name}={val} outside [{low}, {high}]"
    return True, f"{name}={val:.4f} ok"


def run_cases():
    rng = np.random.default_rng(20260522)
    results = []

    # E1 — K_strategy_bits = 0
    name = "E1 K=0 (no parameter complexity)"
    r = rng.normal(0, 0.01, size=500)
    path = [TrialNode("root", "h", 0, {}, "d", nu=10)]
    try:
        res = mdl_dsr(r, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"log2_N={res.log2_N_eff:.2f}, mdl_dsr={res.mdl_dsr:.4f}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E2 — K_strategy_bits = 10000
    name = "E2 K=10000 (extreme)"
    path = [TrialNode("root", "h", 10000, {}, "d", nu=10)]
    try:
        res = mdl_dsr(r, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"log2_N={res.log2_N_eff:.0f}, mdl_dsr={res.mdl_dsr}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E3 — tau = 30 (minimum)
    name = "E3 tau=30 (minimum allowed)"
    r_short = rng.normal(0, 0.01, size=30)
    path = [TrialNode("root", "h", 0, {}, "d", nu=10)]
    try:
        res = mdl_dsr(r_short, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"n_obs={res.n_obs}, mdl_dsr={res.mdl_dsr:.4f}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E4 — tau = 100_000
    name = "E4 tau=100,000 (very long)"
    r_long = rng.normal(0, 0.01, size=100_000)
    path = [TrialNode("root", "h", 0, {}, "d", nu=10)]
    try:
        res = mdl_dsr(r_long, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"n_obs={res.n_obs}, mdl_dsr={res.mdl_dsr:.4f}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E5 — Single-trial tree
    name = "E5 Single-trial tree (no branching)"
    path = [TrialNode("root", "h", 0, {}, "d", nu=1)]
    try:
        res = mdl_dsr(r, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"N_bp={res.n_bp}, log2_N={res.log2_N_eff:.2f}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E6 — Very deep tree
    name = "E6 Very deep tree (depth 100)"
    deep_path = [TrialNode(f"d{i}", "h", 0, {}, "d", nu=2) for i in range(100)]
    try:
        res = mdl_dsr(r, path=deep_path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"depth=100, log2_N={res.log2_N_eff:.2f}, N_bp={res.n_bp}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E7 — Very wide tree (single root with ν=1000)
    name = "E7 Very wide tree (ν=1000)"
    path = [TrialNode("root", "h", 0, {}, "d", nu=1000)]
    try:
        res = mdl_dsr(r, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"N_bp={res.n_bp}, log2_N={res.log2_N_eff:.2f}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E8 — Near-zero variance (degenerate but not zero)
    name = "E8 Near-zero variance (1e-10 std)"
    r_const = np.full(500, 0.0001) + rng.normal(0, 1e-10, size=500)
    path = [TrialNode("root", "h", 0, {}, "d", nu=10)]
    try:
        res = mdl_dsr(r_const, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"std={r_const.std(ddof=1):.2e}, mdl_dsr={res.mdl_dsr:.4f}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E9 — Exact zero std (should be handled gracefully)
    name = "E9 Exact zero std (returns all equal)"
    r_zero = np.full(500, 0.001)
    path = [TrialNode("root", "h", 0, {}, "d", nu=10)]
    try:
        res = mdl_dsr(r_zero, path=path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"std=0, mdl_dsr={res.mdl_dsr}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E10 — Mixed deep+wide tree
    name = "E10 Mixed deep+wide (5 levels × ν=10)"
    mixed_path = [TrialNode(f"L{i}", "h", 0, {}, "d", nu=10) for i in range(5)]
    try:
        res = mdl_dsr(r, path=mixed_path)
        ok, msg = assert_finite_in_range("mdl_dsr", res.mdl_dsr)
        details = f"N_bp={res.n_bp}, log2_N={res.log2_N_eff:.2f}"
    except Exception as e:
        ok, msg, details = False, f"EXCEPTION: {e}", ""
    results.append((name, ok, msg, details))

    # E11 — Monotonicity: more branching → lower MDL-DSR
    name = "E11 Monotonicity: more branching → lower SVC"
    r_strong = rng.normal(0.001, 0.01, size=500)
    mvalues = []
    for nu in (1, 10, 100, 1000):
        p = [TrialNode("root", "h", 0, {}, "d", nu=nu)]
        try:
            m = mdl_dsr(r_strong, path=p).mdl_dsr
            mvalues.append(m)
        except Exception:
            mvalues.append(float("nan"))
    monotonic = all(mvalues[i] >= mvalues[i+1] - 1e-9 for i in range(len(mvalues)-1))
    results.append((
        name, monotonic, "monotonic ✓" if monotonic else "NOT monotonic",
        f"values for ν=1,10,100,1000: {[f'{v:.4f}' for v in mvalues]}"
    ))

    return results


def main():
    results = run_cases()
    print(f"V5 — Edge cases and numerical stability\n")
    print(f"  {'Case':<45} | {'Verdict':<10} | Details")
    print(f"  {'-'*45} | {'-'*10} | {'-'*60}")
    failures = 0
    for name, ok, msg, details in results:
        verdict = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"  {name:<45} | {verdict:<10} | {details[:60]}")
    print(f"\n  Total: {len(results) - failures}/{len(results)} PASS")

    lines = [
        "# V5 — Edge Cases and Numerical Stability\n",
        "Date: 2026-05-22\n",
        f"{len(results)} edge cases tested; {len(results) - failures} pass, {failures} fail.\n",
        "## Results\n",
        "| Case | Verdict | Details |",
        "|---|---|---|",
    ]
    for name, ok, msg, details in results:
        v = "✅ PASS" if ok else "❌ FAIL"
        lines.append(f"| {name} | {v} | {details} |")
    lines.extend([
        "",
        "## Interpretation\n",
        "All cases that produce finite, in-range mdl_dsr values are PASS. Cases that throw "
        "exceptions or produce out-of-range values are FAIL.",
        "",
        f"Of {len(results)} edge cases tested, {len(results) - failures} pass. Failures (if "
        "any) document implementation bugs that need to be fixed before publication.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
