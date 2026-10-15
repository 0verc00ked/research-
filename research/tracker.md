# Research Tracker

Single source of truth for phase status, open questions, decisions.

## Status

| Phase | State | Started | Done | Output |
|-------|-------|---------|------|--------|
| 0 Scaffold | ✅ done | 2026-05-21 | 2026-05-21 | this dir |
| 1 Foundations | ✅ done | 2026-05-21 | 2026-05-21 | `phase1_foundations/` |
| 2 Evidence | ✅ done (V-1 partial, ap-south-1 measurement pending EC2) | 2026-05-21 | 2026-05-21 | `phase2_evidence/` |
| 3 GitHub mining | ✅ done | 2026-05-21 | 2026-05-21 | `phase3_github/` (25+ dossiers + patterns) |
| 4 Infra & latency | ✅ done | 2026-05-21 | 2026-05-21 | `phase4_infra/infra_cost_model.md` |
| 5 Capital & paper | ✅ done | 2026-05-21 | 2026-05-21 | `phase5_capital/` (3 files) |
| 6 Synthesis | ✅ v1 done | 2026-05-21 | 2026-05-21 | `SYNTHESIS.md` |
| 7 Strategy-foundry eval | ✅ done, rejected | 2026-05-21 | 2026-05-21 | `phase7_strategy_foundry/` |

## Decisions log
- 2026-05-21: Scope locked to India-accessible markets, minimal-capital live testing. (User confirmed.)
- 2026-05-21: GitHub PAT stored in `.env` (gitignored); user will revoke post-research.
- 2026-05-21: Phases 1, 3, 4, 5 launched in parallel.
- 2026-05-21: **Architecture call: LLM-as-analyst + rules-as-trader.** Fully autonomous LLM-in-order-path rejected — no evidence base supports it (FinSABER, StockBench negative results).
- 2026-05-21: **Market finalists: NIFTY/SENSEX weekly OTM options (primary), MCX commodity futures (secondary).** Crypto disqualified by tax regime; offshore/HFT/prediction markets ruled out.
- 2026-05-21: **Hard floors:** live capital ₹15k, monthly burn ~₹2.5–3k, hosting must be Indian (SEBI 2026-04-01).
- 2026-05-21: **Stack:** openalgo (execution), qlib (data), nautilus_trader (production backtest), vectorbt (research), TradingAgents graph (analyst pattern only, not as system).
- 2026-05-21: Phase 2 reduced to 9-item verification list (V-1..V-9 in SYNTHESIS.md). Not blocking strategic decision; blocks G2 live plumbing.
- 2026-05-21: **Phase 7 verdict — LLM-as-strategy-generator ("foundry") architecture rejected.** Zero peer-reviewed evidence of clearing PBO+DSR+CPCV on contamination-free OOS; 3 converging rigorous negative results. Foundry probability 5–10% vs analyst 8–15% over 2-yr OOS. Decision: keep current LLM-as-analyst architecture, tighten G0 thresholds, build validation harness as hard prerequisite (V-10). LLM-as-research-aid for hypothesis brainstorming is permitted but does not enter the runtime.
- 2026-05-21: **Plan refined to `CONCRETE_PLAN.md`** — 12 weeks, ₹50k ceiling, three parallel edge channels (E1 microstructure / E2 disclosure-text / E3 bounded-ruin allocator). LLM-as-online-analyst (regime tagging) deferred to v2 — replaced by the *disclosure-text comprehension* role (E2), where LLM has a defensible unique mechanism advantage (real-time unstructured-text on novel content) that contamination cannot kill. Online-allocator architecture (Primitives 1+2: exponentiated weights + Bayesian skeptical sizing) provides a provable regret bound. Read CONCRETE_PLAN.md at the start of each work session.
- 2026-05-21: **W1-2 LANDED.** `agent_trader/validation/` shipped (CPCV+PBO+DSR+trial_log+regime_splits+harness). 30/30 tests pass. G0a self-test confirmed.
- 2026-05-21: **W3-4 LANDED, ALL THREE FAILED — as expected (70% prior).** S1 DSR 0.000 + CPCV 0.39. S2 PBO 0.634 (overfit signature). S3 every variant Sharpe ≤ -1.06 (cost-killed). 56 trials logged. ₹0 spent. Postmortem at `research/postmortem_w3_w4.md`. Harness is doing exactly what it should.
- 2026-05-21: **W5-6 LANDED.** `agent_trader/portfolio/` shipped: ExpWeights (Hedge) + NIG Bayesian sizing + fractional Kelly + Allocator composition. 55/55 tests pass including G0c gates: (a) regret ≤ theoretical bound at T=252 K=5, (b) posterior shrunk >70% at n=30, (c) total exposure cap inviolable, (d) zero-deployment when no posterior edge, (e) no-ruin over 1000d iid noise. Demo script `scripts/w5_allocator_demo.py` confirms: World A (1 edge + 4 noise) → edge wins 60% weight, +15.8% P&L; World B (all noise) → **0 deployment**; World C (edge vs loser) → edge takes 83.8%. The bounded-ruin guarantee holds.
- 2026-05-21: **W7-8 G0d FAILED.** Disclosure-text classification (headline-only) showed 1.04× materiality discrimination ratio (needed ≥2.0×). Channel dies for this methodology; would need PDF reading to revive. Postmortem at `research/phase8_disclosure/g0d_evaluation.md`.
- 2026-05-21: **D3+D1+D5 LANDED, ZERO STRATEGIES SURVIVED.** Built `agent_trader/regime/` (HMM, 5/6 known events correct), `agent_trader/scanner/` (lead-lag, 424 FDR-significant pairs found), `agent_trader/setups/` (conjunctive search, 377 trials honestly counted). 3 setups passed train BH-FDR, 1 (`regime_calm`) passed val, **0 passed OOS** — sign flipped 2024→2026. Textbook overfit caught by post-cutoff gate. Cumulative: **383 setups tested, 0 surviving harness.** Strong Bayesian update: retail tradable edge at these features+horizon may not exist. Consolidated postmortem: `research/phase9_research_engine/D3_D1_D5_postmortem.md`.

## Open questions (to resolve before live testing)
- O-1: Indian tax treatment of agent-executed F&O trades — STCG vs business income classification.
- O-2: SEBI algo-trading approval requirement for retail (post-2024 framework) — is broker-side API access enough, or is per-strategy approval needed?
- O-3: Crypto: which Indian FIU-registered exchanges have working algo APIs and what are real fills like?
- O-4: LLM inference cost per decision at chosen horizon — does the edge survive the API bill?
- O-5: Minimum capital for NSE F&O after lot-size + SPAN margin changes (post 2024 expiry reform).

## Risks
- R-1: Overfitting any backtest. Mitigation: walk-forward only, OOS holdout, paper-trade before live.
- R-2: API/regulatory change mid-build (SEBI is actively reshaping retail algo rules).
- R-3: LLM cost > strategy edge. Mitigation: model the budget before coding.
- R-4: My own bias toward "AI must work" — hold decisions to evidence bar.
