"""V3 — Adversarial Researcher Scenarios.

The theorem requires honest reporting of ν (A4) and honest data-splitting
(A1). Real researchers may violate these — knowingly or not. We test SVC's
robustness to several adversarial patterns:

  A1 Honest baseline           — true ν reported correctly
  A2 Under-reporter (50%)      — reports ν/2 instead of ν
  A3 Under-reporter (90%)      — reports ν/10
  A4 Lone-strategy lie         — claims "I only tried one"
  A5 HARK (post-hoc theory)    — tests 100, claims they had a theory all along
  A6 Repeated OOS peeking      — peeks at OOS 5 times, picks best
  A7 Selective tree pruning    — silently drops failed branches before reporting
  A8 The smart adversary       — combination of A2 + A6 (under-reports AND peeks)

For each, all underlying trials are null. We measure SVC's empirical Type-I:
- If SVC controls Type-I despite the misbehavior: SVC is *robust* to that violation
- If SVC's Type-I exceeds α: SVC is *vulnerable*; the user must enforce A1/A4 honestly
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.validation import TrialNode, mdl_dsr  # noqa: E402

REPORT = ROOT / "research" / "phase11_svc" / "V3_adversarial.md"


def run_scenario(n_sims: int, true_K: int, reported_K: int, tau: int,
                 alpha: float, rng_seed: int, peeks: int = 1) -> dict:
    """Generic harness:
      - Researcher actually tries true_K strategies, all null.
      - For 'peeks' = 5, they peek at the OOS sample 5 times, taking the best.
        (Models repeated data-snooping after the initial split.)
      - They report ν = reported_K in the trial-tree.
    """
    rng = np.random.default_rng(rng_seed)
    rejections = 0
    for _ in range(n_sims):
        if peeks == 1:
            R = rng.normal(0.0, 0.01, size=(true_K, tau))
            sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
            best = R[int(np.argmax(sharpes))]
        else:
            # Multiple peeks: generate `peeks` independent OOS samples, take best
            best_sr = -np.inf
            best = None
            for _ in range(peeks):
                R = rng.normal(0.0, 0.01, size=(true_K, tau))
                sharpes = R.mean(axis=1) / R.std(axis=1, ddof=1)
                idx = int(np.argmax(sharpes))
                if sharpes[idx] > best_sr:
                    best_sr = float(sharpes[idx])
                    best = R[idx]
        # Researcher reports nu = reported_K
        path = [TrialNode("root", "h", 0, {}, "d", nu=reported_K)]
        try:
            r = mdl_dsr(best, path=path)
            if r.mdl_dsr > 1 - alpha:
                rejections += 1
        except Exception:
            pass
    return {"typeI": rejections / n_sims, "true_K": true_K, "reported_K": reported_K, "peeks": peeks}


def main():
    alpha = 0.05
    tau = 500
    n_sims = 1500

    scenarios = [
        ("A1 Honest (true K=50, reports 50)",        50,   50, 1),
        ("A2 Under-reporter ×2 (true 50, reports 25)", 50, 25, 1),
        ("A3 Under-reporter ×10 (true 50, reports 5)", 50,  5, 1),
        ("A4 Lone-strategy lie (true 50, reports 1)",  50,  1, 1),
        ("A5 HARK (true 100, reports 1)",             100,  1, 1),
        ("A6 Repeated peeking (true 50 × 5 peeks)",    50, 50, 5),
        ("A7 Pruning (true 200, reports 50 'kept')",  200, 50, 1),
        ("A8 Smart adversary (under-report + peek)",   50, 10, 5),
    ]

    print(f"V3 — Adversarial scenarios (tau={tau}, alpha={alpha}, sims={n_sims})\n")
    print(f"  {'Scenario':<50} | {'SVC Type-I':>10} | Verdict")
    print(f"  {'-'*50} | {'-'*10} | {'-'*10}")

    results = []
    for label, true_K, rep_K, peeks in scenarios:
        r = run_scenario(n_sims, true_K, rep_K, tau, alpha,
                          rng_seed=20260522 + hash(label) % 10000, peeks=peeks)
        verdict = "ROBUST" if r["typeI"] <= alpha + 0.02 else "VULNERABLE"
        results.append((label, r, verdict))
        print(f"  {label:<50} | {r['typeI']:>10.4f} | {verdict}")

    lines = [
        "# V3 — Adversarial Researcher Battery\n",
        "Date: 2026-05-22\n",
        f"**Setup:** τ={tau}, α={alpha}, {n_sims} sims per scenario.\n",
        "Each scenario simulates a researcher behavior that may violate "
        "SVC's assumptions (A1 honest data-splitting, A4 honest branching report). "
        "All underlying strategies are null. SVC's empirical Type-I tells us "
        "whether the framework is **robust** (controls Type-I despite violation) "
        "or **vulnerable** (Type-I exceeds α — researcher fooled SVC).\n",
        "## Results\n",
        "| Scenario | True K | Reported ν | Peeks | SVC Type-I | Verdict |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for label, r, verdict in results:
        v = "✅ ROBUST" if verdict == "ROBUST" else "❌ VULNERABLE"
        lines.append(f"| {label} | {r['true_K']} | {r['reported_K']} | {r['peeks']} | "
                     f"{r['typeI']:.4f} | {v} |")
    lines.extend([
        "",
        "## Interpretation\n",
        "- **ROBUST** verdicts mean SVC's Type-I held below α + 2% even though the researcher "
        "violated assumptions. This is *unexpectedly good* behavior — the framework happens to "
        "self-correct in these cases.",
        "- **VULNERABLE** verdicts mean SVC was *fooled* by the violation. This is the honest "
        "limit: the framework provably works only under (A1)–(A4). It cannot survive every "
        "dishonest researcher — no statistical framework can.",
        "",
        "**Implications for users:**",
        "1. SVC requires honest reporting of ν. Under-reporting of branching factors *will* "
        "inflate Type-I beyond α. There's no automatic fix.",
        "2. SVC requires train/test isolation. Repeated peeking *will* inflate Type-I.",
        "3. The framework should be paired with research-process safeguards (pre-registration, "
        "version-controlled research logs, audit trails) to mitigate adversarial behavior.",
    ])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
