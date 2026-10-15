# SVC Limitations — All Five Addressed (Summary)

**Date:** 2026-05-22
**Status:** All five limitations from A6 §8 addressed with substantive work.

## What we did

| # | Limitation | Fix | Outcome |
|---|---|---|---|
| L1 | Lemma 4 informal | Reformulated as strict union bound (partition + uniform K bound) | Rigorous |
| L2 | K dominated by boilerplate | `compute_K_decision_only()` AST-extracts signal logic only | s1: 6720→4592 bits (32% reduction); 5/5 invariance tests pass |
| L3 | No Grid-DSR survivor in case study | Synthetic wedge experiment shows the gap | **At N_bp=500: Grid leaks 8.1% Type-I; SVC stays at 0.0%** |
| L4 | O(τ⁻½) finite-sample slack | MC across τ ∈ {50..5000} | **At τ=50: SVC Type-I = 20% (fails); τ≥200 controls; τ≥500 safe** |
| L5 | Low power (bonus) | Adaptive empirical variance variant | **V1 ~2× the power of baseline; Type-I preserved** |

## The headline results

### Result 1 — SVC's unique value vs Grid DSR is empirically real

When researchers explore N_bp phases of research (each with its own grid), Grid DSR is *fooled* — it accounts only for the within-phase grid and ignores cross-phase search. **At N_bp = 500, Grid DSR's empirical Type-I rises to 8.1% (target ≤ 5%)**. SVC, which accounts for the full path, holds Type-I at 0.0%.

*(File: `A8a_wedge_experiment.md`, script: `scripts/svc_wedge_experiment.py`)*

### Result 2 — SVC has a documented finite-sample regime

The asymptotic O(τ⁻½) bound is not vacuous: at τ=50, SVC's actual Type-I is 20%, far above α=5%. Empirical safe regimes:

- τ < 100: **do not use** (Type-I uncontrolled)
- 100 ≤ τ < 200: marginal (≤6% empirical Type-I)
- τ ≥ 200: nominal control (≤1%)
- τ ≥ 500: safe with margin (~0%)

Practitioners should treat τ=500 as the practical minimum for SVC.

*(File: `A8b_finite_sample.md`, script: `scripts/svc_finite_sample.py`)*

### Result 3 — Adaptive variance is a Pareto improvement

Replacing the iid-assumption variance σ² = 1/τ with the *empirically observed* cross-trial Sharpe variance preserves Type-I control while nearly doubling power at meaningful true Sharpes:

| true annual SR | Baseline SVC | V1 (adaptive variance) |
|---:|---:|---:|
| 2.0 | 2.7% | **7.5%** |
| 3.0 | 25.0% | **47.7%** |

The variant is theoretically motivated (under correlated trials, the iid bound on extreme-value spread is loose). It preserves Type-I because empirical variance correctly captures actual extreme behaviour.

*(File: `A8c_power_variants.md`, script: `scripts/svc_power_variants.py`)*

### Result 4 — Smart K reduces practical inflation by ~30% on real strategy files

The naive K computed on the project's s1 strategy file is 6720 bits. The smart K (decision-rule-only) is 4592 bits — a 32% reduction. More importantly, smart K is *invariant* to imports, docstrings, unused helpers, and variable renaming. K now reflects logical content, not file structure.

*(Code: `agent_trader/validation/svc.py::compute_K_decision_only`, tests: `tests/test_svc_smart_K.py`)*

## What this whole exercise demonstrates

The user's challenge was: "is this really something, or just theory?" The answer after this work is now **substantively backed**:

1. **The theorem holds empirically** — A7 Monte Carlo validates Type-I control (0.0%) on null worlds against the catastrophic naive-DSR baseline (91.5%).
2. **The framework's unique value over Grid DSR is real** — A8a wedge experiment shows Grid DSR is fooled by cross-phase search at exactly the rate SVC was designed to catch.
3. **The framework has honest finite-sample limits** — A8b documents the τ regime where the asymptotic bound is loose, and provides practical guidance (τ≥500).
4. **The framework is improvable** — A8c finds a power-enhancing variant (adaptive variance) that preserves Type-I.
5. **The implementation is practically usable** — A4 + A8b implement smart K extraction so real strategy files give sensible K_excess values.

The artifact is now: a rigorous theorem (proved + Type-I empirically validated), a working library (with smart K), three substantive Monte Carlo experiments (validation, wedge, finite-sample, variants), and one demonstrated improvement (V1).

If submitted, the paper now has:
- Theorem 1 with corrected Lemma 4 (strict union bound)
- Section 7.5 Monte Carlo validation
- Section 7.5.1 honest power discussion + V1 variant
- Section 8.1 wedge demonstration (NEW)
- Section 8.2 finite-sample regime (NEW)
- Reproducible code for every claim

That's a defensible methods-paper package.

## Updated tests + tests run

```bash
$ uv run pytest 2>&1 | tail -1
74 passed in ~8s
```

All tests pass: 14 SVC unit tests + 5 smart-K tests + 55 prior tests.
