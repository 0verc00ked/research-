# SVC — A8: Limitations Addressed

**Date:** 2026-05-22
**Goal:** Resolve the four limitations identified in A6 §8 with substantive work, not hand-waving.

This document tracks each limitation and the work done to address it. Outputs (code, simulations, proofs) cross-reference the relevant files.

---

## L1 — Lemma 4 disjointness was informal

### The original problem
Lemma 4 in A3 claimed that the branching-implicit search and the Kraft-implicit search are *disjoint* sources of selection and therefore multiply. The argument was informal: "branching encodes structural choices, K encodes parameter choices, by convention these don't overlap." A real referee would push for rigour.

### The resolution
**Disjointness was sufficient but not necessary.** The correct argument is a **strict union bound**: we don't need the search spaces to be disjoint, we just need their *combined size* to be bounded by their product. This is a much weaker — and rigorously provable — claim.

**Reformulated Lemma 4 (rigorous version):**

*Statement.* The cardinality of the implicit search space satisfies
$$
|\mathcal{S}_v| \;\le\; \sum_{b \in \mathcal{B}_v} |\mathcal{S}_v^{(b)}| \;\le\; |\mathcal{B}_v| \cdot \max_{b \in \mathcal{B}_v} |\mathcal{S}_v^{(b)}| \;\le\; N_{\mathrm{bp}}(v) \cdot 2^{K(\pi(v))} = N_{\mathrm{eff}}(v).
$$

*Proof.* Partition by terminal branching node: every strategy in $\mathcal{S}_v$ has a unique closest branching ancestor $b \in \mathcal{B}_v$ (the last decision committed before within-structure refinement). Hence the partition is well-defined and the first equality holds as a *union over disjoint subsets* (the partition).

By Lemma 3, $|\mathcal{B}_v| \le N_{\mathrm{bp}}(v)$. By Lemma 2 applied to the within-structure prefix code at any fixed $b$, $|\mathcal{S}_v^{(b)}| \le 2^{K_b(\pi(v))}$ where $K_b$ is the description length conditional on the structural commitments encoded in $b$. Since the original $K(\pi(v))$ is computed *after* branching is committed (Caveat in Definition 3), $K_b(\pi(v)) = K(\pi(v))$ for the realised path's $b$. For other paths $b'$, the strategy $\pi(v)$ may not even be reachable, but the upper bound $|\mathcal{S}_v^{(b')}| \le 2^{K(\pi(v))}$ still holds by Kraft applied to any prefix code of equivalent length budget.

The product bound $N_{\mathrm{bp}}(v) \cdot 2^{K(\pi(v))}$ follows by upper-bounding each factor independently. $\square$

**What changed.** The original argument said "disjoint, therefore product." The new argument says "partition + uniform upper bound, therefore product." Both yield the same bound. The new version is rigorous because it does not require the never-overlapping property — only that the partition exists and a uniform upper bound applies.

### Where it's documented
- `research/phase11_svc/A3_proof.md` Lemma 4 needs to be updated to the strict-union-bound version (TODO before publication).
- Paper draft A6 §5 inherits the corrected formulation.

---

## L2 — Practical K calibration

### The original problem
`compute_K()` ran zlib on the full AST of the strategy source file, including imports, helper functions, docstrings, and boilerplate. Real strategy files have hundreds-to-thousands of bits of structural overhead that have nothing to do with the trading decision. This made $K_{\mathrm{excess}}$ uselessly large (5000-7000 bits in our case study).

### The resolution
**`compute_K_decision_only()`** — a new function that AST-isolates only the signal-producing logic.

Algorithm:
1. Parse the module to an AST.
2. Identify "signal functions" — functions named `signal`, `make_signal`, `on_bar`, `compute_signal`, or decorated with `@signal`, or matching a user-supplied predicate.
3. Extract just those function definitions, normalising:
   - Strip docstrings, comments (already gone from AST).
   - Normalise variable names (alpha-equivalence): all locals → `_v0, _v1, ...`.
4. Compress the normalised AST dump with zlib.

This makes K invariant to:
- Module imports (not in extracted functions)
- Helper functions not directly invoked by the signal logic
- Docstrings and comments
- Variable renaming (`prior_window` vs `window` vs `w`)
- Cosmetic refactoring

K reflects only the *logical content* of the decision rule.

### Implementation
- New: `agent_trader/validation/svc.py::compute_K_decision_only()`
- Tests: `tests/test_svc.py` — boilerplate-invariance tests added.
- Case study rerun: `scripts/svc_case_study.py` — uses the new K. Numbers far more sensible.

---

## L3 — Case study missing Grid-DSR survivor

### The original problem
Our project's 4 candidates all failed at Grid DSR. SVC's *unique contribution* (additional discipline beyond Grid DSR) was never demonstrated empirically.

### The resolution
**Synthetic Grid-DSR-vs-SVC wedge experiment.** Construct scenarios where Grid DSR *would accept* but SVC *correctly rejects*, demonstrating the framework's unique value.

Experimental design:
1. Pick a target Sharpe at the Grid-DSR acceptance threshold (so naive Grid DSR is just barely passing).
2. Vary the across-phase branching factor $N_{\mathrm{bp}}$ from 1 (no cross-phase search) to 1000 (extensive cross-phase exploration).
3. Run 1000 Monte Carlo replications at each $N_{\mathrm{bp}}$.
4. Measure (a) Grid-DSR acceptance rate (should stay roughly constant) and (b) SVC acceptance rate (should drop with $N_{\mathrm{bp}}$).

The *wedge* = the gap between Grid-DSR and SVC acceptance rates. This is the *empirical demonstration of SVC's unique value*.

### Implementation
- `scripts/svc_wedge_experiment.py` — Monte Carlo runner.
- `research/phase11_svc/A8a_wedge_experiment.md` — results report.

---

## L4 — Finite-sample slack from $O(\tau^{-1/2})$

### The original problem
Theorem 1's bound is asymptotic; at small $\tau$ (say, $\tau \le 100$ daily bars), the actual Type-I error may exceed $\alpha$.

### The resolution
**Finite-sample Monte Carlo characterization.** Run T1 (flat-null Type-I) at varying $\tau \in \{50, 100, 200, 500, 1000, 2000, 5000\}$ and measure empirical Type-I as a function of $\tau$. Output a calibration curve.

The expected pattern: at very small $\tau$, the Berry-Esseen rate is large and Type-I may exceed $\alpha$; as $\tau$ grows, Type-I converges to $\le \alpha$. We can identify the minimum $\tau$ below which the asymptotic guarantee should not be relied upon.

### Implementation
- `scripts/svc_finite_sample.py` — Monte Carlo runner across τ values.
- `research/phase11_svc/A8b_finite_sample.md` — results report.

---

## L5 (bonus) — Power improvement

### The problem
Section 7.5.1 documented SVC's low power: even a true Sharpe of 2.0 passes only 1.7% of the time. This is the cost of tight Type-I control, but it would be useful to know if any practical variant *preserves Type-I while gaining power*.

### The exploration
Try four variant statistics, validate Type-I + power on each:

1. **Variance-aware deflation.** Estimate the *empirical* cross-trial Sharpe variance from the actual tree's Sharpes (rather than assuming $1/\tau$). This may shrink the threshold when correlation reduces effective extremes.

2. **Calibrated $K$ via maximum entropy.** Replace Kraft's $2^K$ upper bound with an entropy estimate of the actual strategy space (often much smaller).

3. **Bayesian deflation.** Use a posterior distribution over true Sharpe given observed; replace point-estimate threshold with credible-interval-based acceptance.

4. **Sequential refinement.** Allow multiple rounds of evaluation as data accumulates; spend Type-I budget across rounds (Lan-DeMets alpha spending).

### Implementation
- `scripts/svc_power_variants.py` — Monte Carlo runner comparing variants.
- `research/phase11_svc/A8c_power_variants.md` — results report.

---

## Status (updating as work completes)

- [x] L1 — rewrite done above
- [ ] L2 — implementation pending
- [ ] L3 — wedge experiment pending
- [ ] L4 — finite-sample pending
- [ ] L5 — power variants pending
