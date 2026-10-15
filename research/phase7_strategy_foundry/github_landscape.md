# Phase 7 — GitHub Landscape: LLM-Strategy-Generator Repos

**Date:** 2026-05-21
**Method:** GitHub Search API (authenticated, queries logged in `/research/sources/raw/phase7/gh_queries.txt`), filtered to repos that *claim* an LLM-generates-strategy + harness-validates loop. I read code directly where it matters.

> **Bottom line up front:** Of ~25 repos I surveyed, **none** implement a López-de-Prado-grade validation harness (PBO + DSR + CPCV with purge/embargo). The best implement walk-forward + cost-aware backtest + promotion gates. Most are LLM-prompt-loop + raw backtest only. The space is significantly less mature than the academic literature; this is a useful data point — if the patterns were robust, you would see them in OSS.

---

## A. Repos surveyed

### A1. `Y-Research-SBU/QuantAgent` — 2,681★, MIT, last push 2026-05-08
- **What it actually does:** *Trading-decision* multi-agent system (Indicator + Pattern + Trend + Decision agents). **Not** a strategy generator — it makes LONG/SHORT calls per ticker per period.
- **Validation harness?** **No.** No walk-forward, no PBO, no DSR. README explicitly says "educational/research only, not financial advice." Backtest scaffolding in `benchmark/` runs simple cumulative-return rollups.
- **Contamination handling?** None.
- **Trust score:** **T1** as a profit-generating system; **T2** as a code reference for multi-agent architecture.
- **Verdict:** **Study patterns; do not use as a system.** Same call as `TauricResearch/TradingAgents` in Phase 3. The 2.6k★ are pattern-interest, not validation.

### A2. `RndmVariableQ/AlphaAgent` — 299★, MIT, last push 2026-05-11
- **What it actually does:** Implements the AlphaAgent KDD-2025 paper. Eval Agent runs Qlib-based backtests with IC/IR + simple Sharpe. AST-similarity originality regularizer is present (this is the genuinely useful piece).
- **Validation harness?** **Partial.** Uses Qlib's standard train/valid/test (chronological) and IC-based scoring. **No PBO, no DSR, no CPCV.**
- **Contamination handling?** AST-similarity to known alphas (a form of novelty filter against literature memorization) — good idea, weakly implemented (similarity threshold tunable, no empirical calibration).
- **Trust score:** **T2** for engineering; **T1** for "would survive LdP gates".
- **Verdict:** **Steal patterns.** Specifically: (a) AST-similarity novelty filter, (b) hypothesis-factor semantic alignment via LLM judge, (c) AST complexity cap. Do **not** trust its backtest numbers.

### A3. `imbue-bit/AlphaGPT` — 2,016★, Apache-2.0, last push 2026-05-16
- **What it actually does:** Despite the "GPT" name, the repo description is "基于深度强化学习的开源自动因子工厂" — **deep RL factor factory, not LLM-driven.** Folders `model_core/`, `strategy_manager/`, `execution/`. This is a misnamed RL project, not an LLM-as-strategy-generator.
- **Validation harness?** Standard RL train/test only.
- **Trust score:** **T1** for the misnaming; the underlying RL work is **T2**.
- **Verdict:** **Ignore for Phase-7 purposes.** Star count is misleading; this is not LLM-as-strategy-generator.

### A4. `DulyHao/AlphaForge` — 370★, no license, last push 2024-09-01 (stale)
- **What it actually does:** Official code for AAAI-2025 AlphaForge. Generative-predictive architecture; alphagen/alphagen_qlib/alphagen_generic + GP/RL/DSO comparison notebooks. **Pre-LLM in spirit** — uses transformer/RL generators, not chat-based LLMs.
- **Validation harness?** Standard Qlib backtests, IC/RankIC/Sharpe; no PBO/DSR.
- **License risk:** **No license = no commercial use, no derivative work safe.** Auto-cap **T0** on usability.
- **Verdict:** **Study for the generative-predictive pattern**; don't fork due to license risk.

### A5. `gaosu0715-lgtm/Evolutionary-Alpha-Miner` — 38★, MIT, last push 2026-05-08
- **What it actually does:** *Scaffolding only.* Repo explicitly says: "All examples synthetic. Sanitized research framework. Excludes proprietary datasets, real alpha IDs, real simulation results." The `toy_demo.py` uses fake expressions and a fake evaluator.
- **Validation harness?** None real.
- **Trust score:** **T0** for any P&L claim.
- **Verdict:** **Ignore as a system.** Reading interest only.

### A6. `Aroesler1/Alpha-Factor-Mining-Framework` — 4★, no license, last push 2026-04-05
- **What it actually does:** LLM-driven alpha factor mining + walk-forward backtesting + claims "8-gate signal validation." Code under `quantaalpha_us/`. Reading the README: walk-forward + next-day-open execution + ADV participation + liquidity-aware costs + promotion gates. **No PBO/DSR/CPCV** despite the marketing language. "8 gates" is heuristic, not statistical.
- **Validation harness?** **Best in this list for engineering rigour** (walk-forward + costs + gates) but still no LdP-grade test.
- **License risk:** None present. Auto-cap **T0** for use.
- **Verdict:** **Steal the gate-structure pattern** (validation as a promotion graph with first-class failure modes); do not fork due to license.

### A7. `interstellarninja/AlphaGPT` — 6★, Apache-2.0, last push 2024-01-30 (abandoned)
- LLM + RAG over financial documents to extract alpha. Engineering-level prototype, no validation harness. **T1.** Verdict: ignore.

### A8. `FinStep-AI/Alpha-R1` (companion to arXiv:2512.23515)
- Alpha **screening** (relevance-gating known alphas using LLM reasoning), not generation. **T2** for pattern, irrelevant to the foundry concept. Useful for the Role-2 regime/relevance role in our SYNTHESIS.

### A9. `waylonli/FINSABER` — official code for FinSABER (arXiv:2505.07078)
- **Not a strategy generator** — it's the **brutal validation harness** that *kills* LLM strategies on 20-yr / 100+ symbol data. Implements rolling-window backtesting, swappable base-strategy interface, FinMem/FinAgent baselines, and equal-cost ground truth.
- **Verdict:** **Steal directly.** This is *the* repo to mine for the validation-side of any LLM-strategy-foundry build. Specifically: `FINSABER` class with rolling-window execution and the `BaseStrategyIso` interface. License: MIT (verify in repo).

### A10. `ChenNachuan/WorldQuant` — 5★, no license, last push 2026-05-21
- Claims "LLM-driven factor discovery and backtesting." Cap at **T0** (no license; one-author repo). Ignore.

### A11. `YuGu0358/QuantBrain` — 4★, no license, 2026-04-22
- Wraps WorldQuant BRAIN with "multi-LLM routing." Pattern only. **T0/T1.** Ignore as system; pattern is interesting but trivial (just route LLM calls).

### A12. `vedurmaliya/alpha-agents` — 4★, MIT, last push 2025-08-30 (stale)
- LangGraph reproduction of an AlphaAgents paper. Educational. **T1.** Verdict: pattern reference only.

### A13. `bradtaylorsf/alphaagent-team` — 8★, MIT, 2026-02-05
- Not actually about alpha mining — appears to be a generic Claude Code multi-agent template that someone named "alphaagent." Ignore.

### A14. `Rezzecup/gpt4-pinescript-v5-strategy-generator` — 41★, no license, 2026-03-15
- LLM converts English to TradingView PineScript. **No validation.** This is the canonical anti-pattern: generator with zero gate. Auto-cap **T0**. **Strong warning:** the prompt-to-code-to-deploy loop with no harness is exactly the loop the Profit Mirage paper showed leaks 50–72%.

### A15. `TPTBusiness/NexQuant` — 3★, AGPL-3.0, 2026-05-18
- Claims "Autonomous AI agent for quantitative EUR/USD forex; factor discovery; strategy generation." Forex retail context. AGPL is fine for study but copyleft for use. Read code: standard LLM-prompt + simple backtest, no LdP gates. **T1.**

### A16. `kherarudransh-oss/multi-agent-alpha-generation` — 0★, MIT, 2026-03-30
- Pattern-stage scaffold. **T0–T1.**

### A17. `rararulab/rara-strategies` — 0★, MIT, 2026-04-01
- Generator + CI validation claim. CI = pytest, not statistical validation. **T1.**

### A18. `Steven-Hammon/baby-alpha` — 4★, MIT, 2025-06-13
- Self-described "Baby Alpha" iterative document refiner. **T0/T1.** Ignore.

### A19. `RishitSaxena55/AlphaEvolve` — 3★, Apache-2.0, 2025-12-11
- Re-implementation of the DeepMind AlphaEvolve concept. Not finance-specific in implementation. **T1** for finance use.

### A20. `Nlin004/llmge-X-AlphaEvolve` — 2★, no license, 2026-05-02
- Combines LLM-GE with AlphaEvolve concept. Research-stage. **T0/T1.**

### A21. `qlib/examples/` (microsoft/qlib) — *not* LLM-driven, but the canonical Qlib factor-mining examples ship with point-in-time data discipline, walk-forward, and rolling ensembles. **T3** for engineering. **Steal:** the PIT data loader and `RollingEnsemble`. No PBO/DSR built in but the right substrate to add them on.

### A22. `esvhd/pypbo` — small Python lib implementing PBO (CSCV)
- **Trust:** **T3** (mirrors the Bailey/LdP paper). **Use directly** as the PBO gate.

### A23. `quantopian/empyrical-reloaded` / `skfolio` — `skfolio.model_selection.CombinatorialPurgedCV`
- **Trust:** **T3.** `skfolio`'s CPCV implementation appears clean (purged + embargoed). **Use directly.**

### A24. `mlfinlab` (Hudson & Thames) — partially commercial; canonical reference implementation of LdP's protocols including PBO, DSR, CPCV, fractional differentiation, triple-barrier, meta-labeling
- **License caveat:** Some components moved behind a paid wall. Current OSS subset is **T3** for what remains.
- **Verdict:** **Use what is OSS; do not depend on the paid components.**

### A25. `braverock/quantstrat` (R) — `deflated.Sharpe.R`
- R-side reference for DSR. **T3.**

---

## B. Patterns worth stealing

1. **From `RndmVariableQ/AlphaAgent`:** AST-similarity novelty filter against a curated literature corpus (Alpha101, Alpha158, qlib factor library). This is the closest thing the OSS world has to a contamination guard at generation time.
2. **From `Aroesler1/Alpha-Factor-Mining-Framework`:** Promotion gate graph — strategies move forward only by passing each gate; gates emit failure reasons. Bolt this onto the LdP gates.
3. **From `waylonli/FINSABER`:** The `BaseStrategyIso` interface + rolling-window-with-large-universe execution shape. **This is the right shape for the validation side of any strategy foundry.**
4. **From `microsoft/qlib`:** PIT data loader + `RollingEnsemble` + `Recorder` (MLflow) manifest discipline.
5. **From `skfolio` / `mlfinlab` / `esvhd/pypbo`:** Use these three directly as the validation library; do not re-implement LdP's protocols.

## C. Anti-patterns observed (do NOT replicate)

- **Prompt → code → deploy** with no harness (`Rezzecup/gpt4-pinescript-v5-strategy-generator`). The single most dangerous design in this space.
- **Star-count-as-validation:** `imbue-bit/AlphaGPT` 2k★ is RL with a misleading name; `Y-Research-SBU/QuantAgent` 2.7k★ has no validation harness.
- **"8-gate" / "10-gate" marketing** without statistical content (gates being walk-forward + cost + ADV is engineering, not statistics — necessary but not sufficient).
- **No-license repos with claimed alpha** — auto-cap T0 and ignore.
- **Synthetic-only demos with serious-sounding READMEs** (`Evolutionary-Alpha-Miner`).

## D. Honest summary

The OSS landscape for "LLM generates strategy → harness validates" is **lopsided**:

- The **generation** side is over-supplied (15+ repos with prompt-loop generators, multi-agent architectures, evolutionary wrappers, etc.).
- The **validation** side is dominated by **one academic killer (`FINSABER`)** and a few statistical-rigor libraries (`pypbo`, `skfolio` CPCV, `mlfinlab` remnants).
- **Nothing in the wild assembles the full LdP-grade gate.** If you want PBO + DSR + CPCV + purge/embargo + contamination probe in one harness, you will build it.

The asymmetry is informative: if LLM-as-strategy-generator were producing reliable alpha, well-engineered validation harnesses would have proliferated to certify them. They haven't.
