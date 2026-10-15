# Phase 7 — Contamination in LLM Strategy Generation

**Date:** 2026-05-21
**Question:** When an LLM "generates" a trading strategy, what fraction of that is genuine exploration vs. retrieval from training data? Can the contamination be controlled, or does it structurally cap the approach?

> **Headline answer:** The contamination is **large, measurable, and only partially controllable**. On popular tickers and known alpha families, the LLM is mostly retrieving. On post-cutoff data and novel universes, residual leakage from text corpora about general market structure persists but is smaller. For an Indian retail operator targeting **NIFTY weekly OTM options** — a heavily-discussed instrument in public Indian financial media — the contamination ceiling is **structurally low to moderate**. This is solvable with discipline but not eliminable.

---

## 1. The measurable contamination — what the evidence shows

### 1.1 *Profit Mirage* (Tang et al., arXiv:2510.07920, Oct 2025) — T3
The strongest single piece of evidence in the field:

- **51.48% – 62.23% Sharpe ratio decay** when LLM trading agents are moved from pre-training-cutoff data to post-cutoff data, on the same benchmark.
- **50.18% – 71.85% total return decay** in the same comparison.
- **Prediction Consistency > 0.69** across tested agents (a memorization-dominance signal).
- **LLMs answer 85.4–92.9% of FinLake-Bench questions** (historical prices, trends, events) accurately for in-cutoff data — i.e., they have the data memorized; 90.2% on directional trend prediction for in-cutoff windows.

**Inference:** Roughly **half** to **two-thirds** of all reported LLM trading-agent alpha is contamination. Not 5%. Not 15%. *Half.*

### 1.2 *MemGuard-Alpha* (arXiv:2603.26797) — T2
- **40–60% of LLM-generated alpha factors flagged as memorization-contaminated** by a membership-inference + cross-model-disagreement detector.
- Unfiltered headline alphas: ~15–25% annualized. After memorization filter: ~5–12% annualized. Roughly a **2× haircut** from filtering alone.

### 1.3 *FinSABER* (KDD 2026, arXiv:2505.07078) — T3
- When the universe is broadened to 100+ symbols and the window is 20 years (which dilutes the strong-prior tickers like TSLA/AAPL on which LLM agents were trained to demo well), **the alpha collapses to negative or zero**. FinMem composite Sharpe = −0.228. FinAgent composite Sharpe = 0.241 vs Buy-and-Hold 0.703.

### 1.4 *StockBench* (arXiv:2510.02209) — T3
- Even on a **deliberately post-cutoff** 4-month window (Mar–Jun 2025), 10/14 LLMs only *marginally* beat B&H (0.5–2.5 pp cumulative on a trending market). Sortino values 0.024–0.042 are economically thin.

### 1.5 *Lookahead Propensity* (arXiv:2512.23847) — T3
- Develops a statistic that distinguishes "the LLM is reasoning about cause" vs. "the LLM is recalling effect." Applied to news→returns tasks, a meaningful fraction of reported alpha is lookahead.

**Cross-reading:** Three independent quantifications (Profit Mirage, MemGuard-Alpha, FinSABER) all land in the same ballpark: **at least 40–60% of reported LLM trading-agent alpha is artifact of training-data leakage.**

---

## 2. Does WorldQuant Alpha101 appear verbatim in LLM outputs?

This is the natural concrete test. **Empirically yes, partially.**

- The Alpha101 paper (Kakushadze 2016) is widely cited, hosted in plain text on multiple sites (DolphinDB tutorials, GitHub mirrors of the formulas, Stefan Jansen's *Machine Learning for Trading* appendix). It is **almost certainly in the pretraining corpus** of every modern LLM (GPT-4/5, Claude 3/4, Gemini 1.5+/2.x).
- Practitioner observations (Quantocracy aggregator threads; ml-quants Substack #7): when prompted to generate formulaic alphas on US equities, frontier LLMs frequently emit factors that are **rank/sign-equivalent** to Alpha101 entries — sometimes with the variable names changed.
- The `AlphaAgent` paper (arXiv:2502.16789) explicitly introduces an **AST-similarity novelty filter against Alpha101** precisely because the authors hit this problem. This is the strongest implicit admission in the literature.

**I did not independently re-run the verbatim test** in this phase (no T4 evidence collected here). But the structural evidence is consistent enough across the AlphaAgent regularizer's existence + practitioner reports + the Profit Mirage memorization audit that the inference is solid at **T2**:

> **On any well-known alpha family (Alpha101, Alpha158, Quantpedia anomalies, the classical factor-investing canon), a meaningful fraction of LLM "generation" is retrieval. Novelty filters are necessary, not optional.**

---

## 3. Indian-market specific contamination — the user's actual venue

This deserves separate treatment because the user trades NIFTY weekly OTM options, not US S&P 500.

**What LLMs know about Indian markets:**
- NIFTY/BANKNIFTY index composition and historical levels: **memorized** (frequently cited in Indian financial media; T3 inference).
- Major Indian corporate events (RIL splits, HDFC merger, Adani 2023 crash): **memorized**.
- Indian-equity option-chain microstructure and weekly expiry behavior: **partially memorized** — there is moderate but not overwhelming volume of public quantitative writing on this (Sensibull, Zerodha Varsity, Tradingqna).
- Specific options-strategy returns at strike/expiry granularity: **not strongly memorized** — this data is largely paywalled (Sensibull, NSE Datazone) or absent from public corpora.

**Inference for the user:**
- Contamination on **index-level direction** for NIFTY (i.e., regime calls, news synthesis, event flags) is **moderate to high** — the LLM has seen many narratives about Indian markets.
- Contamination on **option-strike-level entry/exit rules** (the actual signal-to-trade) is **low** — that data is not in the corpus at the granularity required.
- This argues for **Role-2 (LLM as regime/event tagger feeding deterministic option-strategy rules)** *exactly as the SYNTHESIS already proposes.* The architecture is robust against the contamination ceiling.
- A strategy-generator architecture that asks the LLM to *invent* option entry rules for NIFTY weeklies will receive **textbook strategies the LLM has read about** (e.g., short straddles around expiry, long-OTM-on-event-day) without genuine signal extraction. **This is the highest-risk failure mode of the foundry concept for this user.**

---

## 4. Mitigations — what works, what doesn't

### 4.1 Mitigations that work (T2–T3 evidence)

1. **Strict post-training-cutoff evaluation.** *StockBench* (T3). Single most important guard. Use *only* data the model could not have seen.
2. **AST/expression novelty filter against literature.** *AlphaAgent* (T3). Reject candidates that are structurally similar to Alpha101/Alpha158/Quantpedia entries above a calibrated threshold.
3. **Counterfactual perturbation.** *Profit Mirage's FactFin component* (T3). Mutate inputs; require the LLM's strategy to respond sensibly. Reduces PC by 57–64%.
4. **Strategy-code generation (not direct prediction).** *FactFin* (T3). LLM emits code that consumes data and computes signal; LLM is *out* of the inference loop after generation. This is structurally what the user is proposing — good.
5. **CPCV with purge + embargo** for evaluation. *López de Prado, AFML 2018* (T3). Required for any honest OOS Sharpe.
6. **No-LLM symbolic baseline ablation.** *CogAlpha* (T2) shows traditional ML matches early LLM-alpha methods. Always compare to GP / LightGBM with same features; the LLM must clear that bar.
7. **Force citation-of-source.** Practitioner pattern. Ask the LLM to list the papers/heuristics its strategy resembles; if the list is long, the strategy is retrieval. (T1, but cheap.)
8. **Multi-model disagreement filter.** *MemGuard-Alpha* (T2). Run generation on at least 2 independent model families; signals all three families agree on are likelier shared-training-corpus artifacts.

### 4.2 Mitigations that *partially* work

1. **Novel feature constructions** (volume-weighted variants of public factors, India-specific composites). Reduces but does not eliminate retrieval risk.
2. **Asking for "novel" strategies in prompts.** Marginal. The LLM is happy to relabel known strategies as novel.
3. **RAG over current market data.** Helps decision-time, doesn't help generation-time contamination.

### 4.3 Mitigations that **do not** work

1. **Trusting the model's self-report** of novelty.
2. **Larger model → more novelty.** Empirically the opposite (Profit Mirage shows PC > 0.69 across model sizes).
3. **Temperature / sampling diversity.** Adds variance, not novelty in the meaningful sense.
4. **Long context with "creative" prompts.** Same.

---

## 5. The honest read — is this structurally addressable?

**Partially.** Here is the calibrated answer:

| Aspect | Verdict | Confidence |
|---|---|---|
| Eliminate contamination | **No.** Training data is fixed. | T3 (Profit Mirage) |
| Reduce contamination from "≥50% of alpha" to "≤20% of alpha" | **Yes, with disciplined mitigations §4.1**. | T2 |
| Ensure clean OOS evaluation | **Yes, by mandatory post-cutoff windows + CPCV + DSR.** | T3 |
| Distinguish "LLM novelty" from "LLM relabeling" | **Partially, with AST/novelty filters + ablation against symbolic baselines.** | T2 |
| Make the contamination story acceptable to a regulator / auditor | **Conditional on §4.1 being implemented end-to-end and documented.** | T2 |
| Reach a state where LLM-generated alpha is *structurally* preferred to hand-written hypotheses for a low-capital retail operator | **No. The mitigations cost more in engineering than the alpha is worth at the user's scale.** | T2 |

**The last row is the brutal one.** Even if you implement every mitigation in §4.1, you have built an engineering apparatus whose value depends on extracting alpha that **the published literature has not yet shown to survive contamination-free evaluation.** You are betting that you can do, on weekends, what KDD 2026 papers cannot do.

---

## 6. Structural ceiling for this user, specifically

For a solo Indian retail operator with ₹15–25k capital and ₹3.5k/mo burn, on NIFTY weekly OTM options:

- **The LLM has seen enough Indian-market narrative to generate regime/event signals** — Role-2 in the existing SYNTHESIS is well-supported.
- **The LLM has *not* seen enough strike-granular option-strategy P&L** to generate non-retrieval entry rules — Role-1 (LLM-as-strategy-generator) is **weakly supported by evidence and structurally low-ceiling**.
- **The capital + fee floor** is so tight (₹3.5k/mo burn floor; ~14–23%/mo required) that any contamination tax >20% on the strategy makes it economically nonviable.

**Verdict for this user:** The contamination problem is **not structurally fatal to the architecture** *if and only if* the LLM stays in the analyst role (regime, event, conviction) and the strategy layer is hand-written / classical-ML-driven. Moving the LLM into the strategy-generation slot **adds a contamination tax the user's economics cannot absorb**.
