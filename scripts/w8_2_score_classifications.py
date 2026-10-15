"""W8.2 — score the blind LLM classifications against market-as-ground-truth.

G0d gate (CONCRETE_PLAN.md §4):
  - LLM-material disclosures must have median |ret_eod_next| ≥ ~2x non-material
  - Of LLM-flagged directional disclosures, direction accuracy ≥ 60%
  - Otherwise: channel dies
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CLASSIFIED = ROOT / "research" / "phase8_disclosure" / "batch_v1_classified.json"
TRUTH = ROOT / "research" / "phase8_disclosure" / "batch_v1_truth.json"
REPORT = ROOT / "research" / "phase8_disclosure" / "g0d_evaluation.md"


def main():
    classified = json.loads(CLASSIFIED.read_text())
    truth = json.loads(TRUTH.read_text())
    truth_by_id = {t["id"]: t for t in truth}
    rows = []
    for c in classified:
        t = truth_by_id[c["id"]]
        rows.append({
            "id": c["id"],
            "scrip_name": c["scrip_name"],
            "materiality": c["classification"]["materiality"],
            "direction": c["classification"]["direction"],
            "confidence": c["classification"]["confidence"],
            "reasoning": c["classification"]["reasoning"],
            "ret_eod_next": t["ret_eod_next"],
            "abs_eod": t["abs_eod"],
            "stratum": t["stratum"],
        })

    abs_list = [r["abs_eod"] for r in rows]
    eod_list = [r["ret_eod_next"] for r in rows]
    median_overall = float(np.median(abs_list))

    # --- Materiality discrimination ---
    mat = [r for r in rows if r["materiality"] == 1]
    nonmat = [r for r in rows if r["materiality"] == 0]
    mat_abs = [r["abs_eod"] for r in mat]
    nonmat_abs = [r["abs_eod"] for r in nonmat]
    med_mat = float(np.median(mat_abs)) if mat_abs else 0.0
    med_nonmat = float(np.median(nonmat_abs)) if nonmat_abs else 0.0
    ratio = med_mat / med_nonmat if med_nonmat else float("inf")

    # --- Direction accuracy on directional calls ---
    directional = [r for r in rows if r["direction"] in (-1, 1) and r["materiality"] == 1]
    correct = sum(1 for r in directional if np.sign(r["ret_eod_next"]) == r["direction"])
    dir_acc = correct / len(directional) if directional else float("nan")

    # --- Confidence calibration ---
    # Are high-confidence calls more accurate?
    hi_conf = [r for r in directional if (r["confidence"] or 0) >= 0.7]
    hi_correct = sum(1 for r in hi_conf if np.sign(r["ret_eod_next"]) == r["direction"])
    hi_acc = hi_correct / len(hi_conf) if hi_conf else float("nan")

    # --- Stratum breakdown ---
    by_stratum: dict[str, dict] = {}
    for s in ("mover", "nonmover", "random"):
        sub = [r for r in rows if r["stratum"] == s]
        if not sub:
            continue
        sub_mat = [r for r in sub if r["materiality"] == 1]
        by_stratum[s] = {
            "n": len(sub),
            "flagged_material": len(sub_mat),
            "share_flagged": len(sub_mat) / len(sub) if sub else 0.0,
            "median_abs": float(np.median([r["abs_eod"] for r in sub])),
        }

    # --- Write report ---
    lines = [
        "# W8.2 — G0d Gate Evaluation",
        f"\nDate: 2026-05-21",
        f"\nClassifier: Claude Opus 4.7 (Claude Code session, blind to reactions)",
        f"\nSample: {len(rows)} mid-cap BSE disclosures, stratified by |ret_eod_next|.\n",
        "## Headline numbers\n",
        f"- median |ret_eod_next| overall: **{median_overall:.4f}**",
        f"- LLM-flagged material (n={len(mat)}): median |ret| = **{med_mat:.4f}**",
        f"- LLM-flagged non-material (n={len(nonmat)}): median |ret| = **{med_nonmat:.4f}**",
        f"- **materiality discrimination ratio: {ratio:.2f}x**",
        "",
        f"- LLM directional calls (material × ±1): n={len(directional)}",
        f"- **direction accuracy: {dir_acc:.2%}** ({correct}/{len(directional)})" if directional else "- direction accuracy: (no directional calls)",
        f"- high-confidence (≥0.7) directional calls: n={len(hi_conf)}, accuracy {hi_acc:.2%}" if hi_conf else "- (no high-confidence directional calls)",
        "",
        "## G0d gate criteria\n",
        "| criterion | threshold | observed | pass? |",
        "|---|---|---|---|",
        f"| materiality discrimination ratio | ≥ 2.0x | {ratio:.2f}x | {'✅' if ratio >= 2.0 else '❌'} |",
        f"| direction accuracy on directional calls | ≥ 60% | {dir_acc:.2%} | {'✅' if dir_acc >= 0.60 else '❌'} |",
        "",
        "## By stratum (sanity)\n",
        "| stratum | n | share LLM flagged material | median |ret| |",
        "|---|---:|---:|---:|",
    ]
    for s, d in by_stratum.items():
        lines.append(f"| {s} | {d['n']} | {d['share_flagged']:.0%} | {d['median_abs']:.4f} |")

    # --- Per-disclosure detail ---
    lines.append("\n## Per-disclosure detail (sorted by |ret_eod_next|)\n")
    lines.append("| id | scrip | material | dir | conf | actual ret_eod | reasoning |")
    lines.append("|---|---|---:|---:|---:|---:|---|")
    rows_sorted = sorted(rows, key=lambda r: -r["abs_eod"])
    for r in rows_sorted:
        lines.append(
            f"| {r['id']} | {r['scrip_name'][:32]} | {r['materiality']} | "
            f"{r['direction']} | {(r['confidence'] or 0):.2f} | {r['ret_eod_next']:+.4f} | "
            f"{(r['reasoning'] or '')[:60]} |"
        )

    # --- Verdict ---
    lines.append("\n## Verdict\n")
    pass_ratio = ratio >= 2.0
    pass_acc = isinstance(dir_acc, float) and not np.isnan(dir_acc) and dir_acc >= 0.60
    if pass_ratio and pass_acc:
        lines.append("**G0d PASSED.** Both materiality discrimination and direction accuracy clear thresholds. Channel is alive — proceed to W9.")
    elif pass_ratio and not pass_acc:
        lines.append("**G0d MARGINAL.** Materiality discrimination works but direction accuracy fails. Channel may be useful as a *risk filter* (avoid trading on flagged dates) rather than a *direction signal*. Consider scope reduction.")
    elif not pass_ratio and pass_acc:
        lines.append("**G0d MARGINAL.** Direction accuracy is OK but the LLM cannot distinguish material from non-material disclosures. Practical value limited.")
    else:
        lines.append("**G0d FAILED.** Headline-only classification does not discriminate. The LLM needs to read the attached PDFs (which requires an API key for production-scale processing). Channel dies for the current methodology.")
        lines.append("\n**Honest reading:** the absorption window is generous (slow), but headline-only signal is too weak. To salvage, one of: (a) get an API key + read PDFs; (b) narrow to specific high-information categories; (c) abandon E2 and reallocate W9–10 budget.")

    REPORT.write_text("\n".join(lines))
    print(f"\nReport written: {REPORT}")
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
