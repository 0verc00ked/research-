# SVC — Sequential Validation Calculus

**Goal:** A novel mathematical artifact that addresses an under-formalized problem the quantitative finance field actually has: how to honestly count `N_trials` when research is *sequential, branching, and adaptive*.

**Status:** Phase A1 (lit review) starting 2026-05-21.

## The problem statement (one paragraph)

López de Prado's Deflated Sharpe Ratio (DSR) and Probability of Backtest Overfitting (PBO) correctly punish strategies for testing N alternatives — but they assume N is a static, ex-ante count. Real quant research is dynamic: you run experiment 1, observe its result, *use that result to decide* experiment 2, branch when something looks promising, peek at OOS, refine parameters. **There is no honest framework for counting N under such adaptive research.** Bonferroni (over all branches not taken) overcounts; "I tried 5 things" undercounts. Gelman & Loken's "Garden of Forking Paths" (2013) named this problem philosophically — no published work computationally formalizes it for backtest validation specifically.

## The artifact

A formal framework consisting of:

1. **Trial-Tree formalism (Definition 1):** A research project is a DAG T = (V, E, φ, π) where vertices are trials, edges encode "result of u informed v", φ maps each trial to a strategy in strategy space 𝒮, and π records observed performance.

2. **Effective N (Definition 2):** N_eff(v) = some honest function of the tree structure leading to v. Several candidate definitions to evaluate; the right one is the goal.

3. **MDL-augmented DSR (Definition 3):** MDL-DSR(v) = Φ((SR(v) − E[SR_max | N_eff] − c · K(φ(v))/√T) / σ_SR) where K(·) is the algorithmic description length of the strategy code in some prefix code.

4. **Theorem (the core result):** Under stated assumptions, Type-I error of using MDL-DSR ≥ threshold τ as an acceptance rule is bounded above by α regardless of the tree structure (i.e., regardless of how the researcher branched).

5. **Implementation:** Python library extending `agent_trader/validation/`. Tree-tracking is just an upgrade of our existing `trial_log.py` (already an append-only SQLite registry — easy to add parent_id and branching metadata).

6. **Case study:** Apply retrospectively to our own ~390 trials across the project. Report how many "would have been accepted by standard DSR" vs "rejected by SVC."

## Why this matters

- **Real problem:** Every honest quant researcher faces this. The current default is to ignore the problem or apply Bonferroni-with-fudge-factor.
- **Real novelty:** Gelman-Loken philosophical. We're computational.
- **Real proof:** The Type-I bound is mathematically substantive. Small but real.
- **Real implementation:** Library, not paper-ware.
- **Real case study:** Our 390 trials are an unusual and clean dataset.
- **Real publishability:** Methods paper to *Quantitative Finance*, *J. Portfolio Management*, or arXiv quant-fin.

## Phases (per task list)

| Phase | What | Estimated hours |
|---|---|---:|
| A1 | Literature review — confirm novelty, position contribution | 5-10 |
| A2 | Formal definitions + theorem statement | 5-8 |
| A3 | Theorem proof | 10-15 |
| A4 | Library implementation | 15-20 |
| A5 | Case study on our 390 trials | 5-8 |
| A6 | Methods paper draft (LaTeX or .md) | 10-15 |
| **Total** | | **50-76** |

## What I will explicitly NOT promise

- World-first. I'll know after A1.
- A theorem that's hard to prove. I'm targeting a substantive but tractable result, not a Fields-medal contribution.
- That it produces a profitable strategy. SVC is a *validation methodology*; it's orthogonal to whether any strategy passes it.
- Submission to a specific journal. The artifact ends as code + paper draft + case study. Submission is a separate decision.

## Kill criteria

- A1 surfaces published work that already does this (e.g., a 2024-2026 paper I missed). Then we pivot — either to a closely-related novel angle or to an alternative artifact (B/C/D/E from the menu).
- A3 proof has a gap I cannot close in 20 hours of focused work. Then we restate as a weaker conjecture and demonstrate empirically, or pivot.
- The retrospective case study (A5) shows SVC verdicts are indistinguishable from standard DSR on our data. Then we still have the library + framework, but the practical demonstration is weaker.

## Working hypothesis for A2 (to test, not assume)

**Effective N at leaf v ≈ number of distinct strategy candidates that could have been reached by varying decisions along the path from root to v.**

This is essentially "branching count" — at each decision point in the research process, count the alternatives, multiply along the path. This dominates the actual choices made, providing an upper bound on the search space implicitly explored.

The MDL term then adds a penalty for strategies that are themselves over-parameterised (high K(φ(v))) — this catches a class of overfitting that pure N_trials counting misses (a strategy with N_trials=1 but 50 free parameters is suspect).
