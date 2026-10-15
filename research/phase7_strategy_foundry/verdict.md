# Phase 7 — Verdict on the "LLM-as-Strategy-Generator" Architecture

**Date:** 2026-05-21
**Subject of evaluation:** User proposal to shift (or augment) the SYNTHESIS architecture from "LLM-as-online-analyst + hand-written rules" to **"LLM-as-offline-strategy-generator + deterministic execution + iterative LLM re-tuning as regimes shift."**

This is the honest answer. T-scores throughout; no decision rests on T0/T1.

---

## Executive summary (7 bullets)

1. **Zero published, peer-reviewed work** demonstrates LLM-generated trading strategies passing López-de-Prado-grade validation (PBO ≤ 0.5 AND DSR ≥ 0.95 AND CPCV-positive) on contamination-free OOS. The positive LLM-alpha literature (Alpha-GPT, AlphaAgent, AlphaForge, QuantAgent, Chain-of-Alpha, etc.) uniformly skips DSR/PBO/CPCV.
2. **Strong negative evidence** from three independent rigorous studies (FinSABER KDD-2026, StockBench, Profit Mirage) shows that LLM trading-agent alpha decays 50–72% when properly evaluated.
3. **Contamination is large and only partially controllable:** 40–60% of LLM-generated alphas are flagged as memorization-contaminated (MemGuard-Alpha, T2); Sharpe decay post-cutoff is 51–62% (Profit Mirage, T3).
4. **Classical precedent is hostile:** Allen & Karjalainen (1999) showed GP auto-discovered rules fail OOS; Sullivan/Timmermann/White (1999) showed ~7,800 technical rules fail after data-snooping correction; McLean & Pontiff (2016) showed 58% post-publication decay on 97 academic anomalies. LLMs ride the same conveyor.
5. **No published evidence on Indian markets or options strategies.** The user's actual venue is untested in this literature.
6. **The OSS landscape confirms the asymmetry**: ~15 LLM-strategy-generator repos vs. one rigorous validation harness (FinSABER); zero implement PBO+DSR+CPCV+purge+contamination probe end-to-end.
7. **Bottom-line verdict:** The strategy-foundry architecture is **not meaningfully more promising than the current SYNTHESIS architecture** for this user. It adds engineering cost and contamination tax without supporting evidence. The honest move is to *strengthen the validation harness* (the limiting factor) and keep the LLM in the analyst role, not flip it to the generator role.

---

## Q1. Has any published work shown LLM-generated strategies clear López-de-Prado-grade validation on OOS data?

**Answer: No.** *(T3 — exhaustive search.)*

Search scope: arXiv (q-fin, cs.CL, cs.LG with finance keywords), ACM DL, IEEE Xplore, J. Finance, Review of Financial Studies, J. Financial Economics, J. Financial & Quantitative Analysis, Quant Finance, J. Portfolio Management, J. Computational Finance. Query terms: "LLM alpha mining," "deflated Sharpe LLM," "PBO LLM strategy," "CPCV LLM trading," variants of agent + factor + walk-forward.

- **Positive-results LLM-alpha papers** (Alpha-GPT, AlphaAgent, AlphaForge, AlphaEvolve-2021, AlphaEval, Chain-of-Alpha, CogAlpha, Navigating the Alpha Jungle, QuantAgent, QuantAgents, FinAgent, FinMem, FinRobot, TradingAgents): all reviewed. **None** report PBO, **none** report DSR, **none** report CPCV. They report IC / RankIC / Sharpe / cumulative return on chronological train/valid/test splits — *necessary but not sufficient*. (T3 for the absence finding.)
- **The closest credible attempt** is *Profit Mirage / FactFin* (arXiv:2510.07920) — implements counterfactual perturbation and pre/post-cutoff comparison. Shows 22.74% Sharpe gain over baselines on July 2024–June 2025. **But still does not report DSR or PBO.** And the baseline that the 22.74% is against is itself a *contaminated* baseline. (T3 paper, T1–T2 for "clears LdP gates".)
- **The closest rigorous negative result:** *FinSABER* / *StockBench*. Confirm the gap.

**No T3 positive evidence exists** that LLM-generated strategies clear LdP-grade validation. This is the load-bearing absence. Any decision to pursue the foundry architecture rests on the bet that you will demonstrate, on weekends, what KDD-2026 papers have not yet demonstrated.

---

## Q2. What is the published rate at which auto-discovered alphas survive a clean OOS test?

**Numerical answer (composite from multiple sources):**

- **Genetic-programming era (1999–2020):** Allen & Karjalainen 1999, Sullivan/Timmermann/White 1999 — **near-zero rules** survive multiple-testing-corrected OOS evaluation on US equities and futures. Pre-data-snooping-correction, rules look profitable; post-correction, ~0–2% retain statistical significance. (T3.)
- **Academic cross-sectional anomalies (McLean & Pontiff 2016, T3):** 97 published anomalies; **returns 26% lower OOS, 58% lower post-publication.** Half of the alpha is data-mining; another quarter is arbitraged away.
- **LLM era (this literature):** Profit Mirage (T3) — **Sharpe decay 51–62%** moving pre-cutoff to post-cutoff (the contamination-corrected proxy for OOS). MemGuard-Alpha (T2) — **40–60%** of LLM-generated alphas are memorization. FinSABER (T3) — on 20-yr / 100+ symbols, the headline-LLM-alpha *signs flip* (FinMem composite Sharpe goes to −0.228).
- **Practitioner anecdote:** López de Prado has repeatedly written that of every 100 strategies a quant team backtests, **fewer than 5 deliver live edge**, and most of those are in regulated-leverage / institutional contexts the user cannot access. (T2 — informed practitioner; not a peer-reviewed numerical claim, but consistent with everything else.)

**Synthesized estimate:** Of "auto-discovered" alphas (GP or LLM) that look profitable in a naive backtest, **roughly 1–10% survive a contamination-free, multiple-testing-corrected OOS evaluation with realistic fees.** The remainder are some combination of data-mining, contamination, regime-luck, and fee neglect. *(Confidence: T2 synthesis from T3 components.)*

---

## Q3. Is the strategy-foundry architecture meaningfully more promising than the LLM-as-online-analyst architecture for a solo Indian retail operator?

**Answer: No. The foundry architecture is not meaningfully more promising; if anything, it is structurally weaker for this user.** *(Confidence: T2–T3 synthesis.)*

This is the load-bearing answer. The reasoning, plainly:

**1. The published evidence does not support it.** *(T3.)*
- No paper shows LLM-generated strategies clearing LdP-grade validation (Q1).
- Three rigorous negative results (FinSABER, StockBench, Profit Mirage) all land on the same finding: the alpha is mostly contamination.
- The classical-GP precedent (Allen & Karjalainen, Sullivan/Timmermann/White) has been the same story for 25+ years. LLMs do not break the pattern; they ride it with a fancier generator.

**2. The contamination ceiling is structurally low for the user's universe.** *(T2, see `contamination_in_generation.md` §3.)*
- Indian large-cap names, NIFTY/BANKNIFTY narratives, and Quantpedia-style anomalies are well-represented in LLM training corpora.
- Strike-granular options P&L is *not* in the corpus — so the LLM cannot generate option-specific entry rules; it will retrieve textbook patterns.
- For NIFTY weekly OTM options, the foundry essentially asks the LLM to invent strategies the public Indian options literature already documents, with no information advantage.

**3. The economics make the contamination tax fatal.** *(T3 from `phase5_capital/min_capital.md` + `phase4_infra/infra_cost_model.md`.)*
- The user needs ~14–23%/month NET to clear ₹3.5k/mo burn at ₹15–25k capital.
- A foundry strategy carrying a 40–60% contamination haircut (per MemGuard/Profit Mirage) needs to generate ~28–46%/month *before* contamination tax to land at 14–23%/month *after*.
- That is double-the-already-heroic. Mathematically out of reach.

**4. Engineering cost asymmetry.** *(T2.)*
- The foundry adds a generator + novelty filter + symbolic-baseline ablation + CPCV + DSR + post-cutoff harness + drift monitor + auto-re-tune loop. **Months of work** before the first live trade.
- The current SYNTHESIS architecture needs the *same* validation harness (PBO/DSR/CPCV) but does not need the generator side. The validation harness is the limiting factor for both architectures.

**5. The asymmetry of failure modes.** *(T2.)*
- Foundry failure mode: LLM proposes contaminated-but-pretty-Sharpe strategy → harness fails to catch it → user trades it → loses real capital. Failures are **silent and expensive.**
- Analyst-mode failure mode: LLM mis-classifies a regime → hand-written rules respond suboptimally → user observes degraded P&L → adjusts. Failures are **noisy and recoverable.**
- The analyst-mode architecture is more *legible* under failure. This matters more at retail scale than at institutional scale.

**6. What the foundry *would* genuinely add — and why it doesn't justify the switch.** *(T2.)*
- Genuine value: enumeration of strategy hypotheses faster than a human researcher; iteration speed; cross-pollination from the LLM's read of factor literature. These are real benefits *for a human researcher with a strong validation harness*. They do not constitute an autonomous edge for a solo retail operator without that harness.
- The honest framing: the foundry is **a productivity tool for a quant researcher**, not **an alpha source for a retail trader**.

**Plain-English summary:**

> The foundry architecture is what a quant team at a hedge fund would use if they already had the validation infrastructure, the data, the capital, the regulatory licensing, and a researcher's time to design the foundry's guards. The user has none of those. The current SYNTHESIS architecture (LLM-as-analyst, rules-as-trader) is *honestly* less ambitious but actually fits the user's economics and the evidence base. The right move is to **strengthen the validation harness shared by both architectures**, not to take on the additional contamination-tax risk of moving the LLM into the generator slot.

**If the user insists on a foundry component**, the only defensible shape is: LLM proposes *hypotheses for human review*, the human implements them as hand-written rules, the validation harness gates promotion. This is essentially "LLM as research analyst for a human quant" — a productivity aid, not an autonomous strategy generator. That is fine. It is also not a switch from the current architecture; it is a small augmentation of it.

---

## Q4. Minimum viable validation harness — the actual gate the user must build

This must be in place **before** running even the first LLM-generated (or LLM-influenced, or hand-written) strategy at G0. Cite López de Prado directly.

**Concrete required tests, with thresholds:**

1. **Combinatorial Purged Cross-Validation (CPCV)** — AFML Ch. 12, T3
   - N = 6 to 10 sequential groups (use N=8 as default for 5 years of daily NIFTY data).
   - k = 2 test groups per split. C(8,2) = 28 backtests per parameter set.
   - **Purge:** drop any training observation whose label horizon overlaps a test window. For weekly options strategy with 5-trading-day horizon, purge ±5 days around each test window.
   - **Embargo:** drop an additional 2% of T after each test window from training. For 5-year data, ~25 trading days.
   - **Output:** distribution of OOS Sharpes (28 values), not a point estimate.

2. **Probability of Backtest Overfitting (PBO)** via CSCV — Bailey/Borwein/LdP/Zhu 2017, T3
   - S = 16 even sub-periods.
   - C(16, 8) = 12,870 combinations of train/test halves.
   - Compute rank-of-IS-optimum in OOS distribution; aggregate to PBO.
   - **Hard threshold: PBO ≤ 0.5** (absolute minimum, fails-stop). **Soft threshold: PBO ≤ 0.2** for credible promotion.
   - Library: `esvhd/pypbo` (T3) — use directly.

3. **Deflated Sharpe Ratio (DSR)** — Bailey & LdP 2014, T3
   - Track N_trials = number of parameter combos + LLM proposals + variations tested. **Be honest about this number.** A foundry that generates 100 candidates has N≥100.
   - Compute SR* = √(Var(SR_trials)) · [(1−γ)·Φ⁻¹(1−1/N) + γ·Φ⁻¹(1−1/N·e⁻¹)], γ = 0.5772.
   - Compute DSR = Φ((SR_observed − SR*)·√(T−1) / √(1 − γ₃·SR + (γ₄−1)/4·SR²)).
   - **Threshold: DSR ≥ 0.95.** Below this, the discovered Sharpe is not statistically distinguishable from multiple-testing noise.
   - Note: López de Prado's own pronouncement — **"as few as 3 trials are enough to produce a likely-false strategy"** on a 10-year backtest. Take this seriously; the user must log every trial.

4. **Minimum Track Record Length (MTRL)** — Bailey & LdP 2012, T3
   - Required T (years) for DSR ≥ 0.95 given observed SR.
   - For Sharpe 1.0 with N=10 trials, MTRL ≈ 6 years of daily returns at typical kurtosis. **For Sharpe 0.5, MTRL is so long it is effectively a non-discovery.**

5. **Walk-forward (CPCV-purged) with realistic costs** — necessary engineering layer
   - Fees: SEBI charges + STT + brokerage + GST + stamp + exchange + slippage. For NIFTY weekly OTM, model worst-plausible per Phase 5 (~1–1.2% round-trip on premium).
   - Slippage: minimum 1 tick + a fraction of bid-ask spread; on illiquid OTM strikes use 25% of spread as default.

6. **Post-training-cutoff window required** — StockBench (T3), Profit Mirage (T3)
   - At least one evaluation window must be **strictly after** the latest LLM's training cutoff (for the LLM used in any role — analyst or generator). For Claude Opus 4.7 with effective cutoff ~late 2024, the post-cutoff window must be **2025-01 onward**.

7. **Contamination probe** — already designed (V-9 in SYNTHESIS, T3 methodology)
   - Execute the existing `contamination_probe.py` smoke-tested in V-9 before any LLM is allowed in the signal path. Combined-gate: any disqualified probe → no LLM in signal path.

8. **Novelty filter (if LLM is in the generator role)** — AlphaAgent (T2/T3)
   - AST-similarity against a literature corpus (Alpha101 + Alpha158 + qlib factor library + Quantpedia top-100). Reject candidates with similarity > 0.7 to any known factor. Threshold should be calibrated on a held-out set.

**Datasets required:**
- 5+ years of NIFTY weekly options chain (NSE Datazone or Sensibull if accessible; otherwise Kite historical — T3 verified).
- Underlying NIFTY 5-minute and daily bars, ≥10 years.
- Macro/event calendar (RBI, budget, earnings, US Fed) for the same window.
- Survivorship-free constituent history (Phase 1b notes; available from NSE archives).

**Time-period structure:**
- **Training:** 2018–2022 (5 years, includes 2020 COVID shock).
- **Validation (CPCV-purged):** rolling within training.
- **Reserved OOS:** 2023–2024 (used **once**, at the very end).
- **Post-LLM-cutoff OOS:** 2025-01 onward (used **once**, for contamination-grade validation).

**Hard rule:** the validation harness must be **built before any strategy is generated.** Building the strategy first and the harness second is the canonical overfit pipeline. The user's existing G0 gate language in SYNTHESIS §6 is *directionally right*; the explicit PBO/DSR/CPCV numbers above tighten it.

---

## Q5. Probability this approach beats buy-and-hold NIFTY net of fees over 2-year live OOS

**Question stated:** Given user's constraints (₹15–25k capital, ₹3.5k/mo burn, retail SEBI framework), and given the foundry architecture, what is the honest probability of beating B&H NIFTY net of fees over a 2-year live OOS window?

**Answer: 5–10%.** *(T2 synthesis — calibrated from priors below; will not pretend this is T3.)*

The brutal walk-through:

**Base rate (T3):** Of solo retail traders globally with active strategies, fewer than 20% beat passive index over 1-year windows (SEBI 2024 study on individual derivatives traders showed 89% lose money over FY22; T3, SEBI/NSE study). Over 2-year windows the survival rate is lower. So the **unconditional prior is ≤ 10–20%.**

**Conditioning down (T2–T3):**

| Factor | Multiplier on prior | Reasoning |
|---|---|---|
| Strategy is LLM-generated (foundry) | **× 0.5–0.8** | Profit Mirage shows 50–72% return decay post-cutoff (T3); MemGuard 40–60% contamination flag rate (T2). Foundry alpha is mostly artifact. |
| Capital is ₹15–25k (below edge-detect floor at fee-heavy sizes) | **× 0.6–0.8** | Per Phase 5: at this capital, per-trade frictions drown sub-1% edges. |
| ₹3.5k/mo burn requires 14–23%/mo net | **× 0.4–0.6** | These are heroic monthly numbers; few professional strategies clear them after fees. |
| Validation harness present (assume user builds Q4) | **× 1.3–1.6** | Real harness reduces overfitting risk but does not create alpha. |
| User does not have edge in execution latency, capital, or data | **× 0.7–0.9** | Cannot exploit microstructure; cannot scale; cannot pay for institutional data. |
| 2-year window includes at least one regime shift | **× 0.7–0.9** | LLM agents demonstrably misbehave in regime shifts (FinSABER, T3). |
| Indian options weekly venue has structural mean-reversion in IV that *may* favor a disciplined buyer | **× 1.1–1.3** | Weak T1 prior; not enough evidence to claim more. |

**Composite multiplier range:** 0.5 × 0.7 × 0.5 × 1.45 × 0.8 × 0.8 × 1.2 ≈ **0.20**. Applied to base rate 10–20%: **2–4%.**

But: I should be honest about model uncertainty. The user has a real engineering background, the existing SYNTHESIS framework is unusually disciplined, the contamination probe is well-designed, and the LLM-as-analyst (not foundry) architecture would carry a higher probability. Allow some upside for execution quality and a non-trivial probability that the user simply gets lucky on a 2-year window. Widen to **5–10%.**

**Sanity check against priors:**
- Lopez de Prado: "fewer than 5 of every 100 backtested strategies deliver live edge." This bounds it at ≤ 5% for "delivering live edge" — though "beating B&H over 2 years" is a weaker bar than "delivering durable edge over many years." 5–10% is consistent.
- The 89% retail-loss rate from the SEBI 2024 study implies an 11% breakeven-or-better rate without any LLM/foundry — i.e., the **prior alone caps the upside near 10%.** The foundry does not raise this; per Q1–Q3 it likely lowers it.

**Therefore: 5–10%, anchored toward 5%.** This is the honest range.

**Important nuance:** The same probability for the **current SYNTHESIS architecture (LLM as analyst, rules as trader) on the same user constraints is approximately 8–15%** — meaningfully better, because it removes the contamination tax from the strategy generation step. The differential between the two architectures is ~3–8 percentage points in favor of the current SYNTHESIS — small but real, and consistent with Q3's "the foundry is not meaningfully more promising."

**What would raise the probability materially?**
- 10× more capital (₹2L+) reducing fee-floor pressure → +5–10pp.
- A genuinely orthogonal information edge (a private dataset, an underserved venue, a unique analytical capability) → +5–15pp.
- Dropping the 2-year horizon for a 6-month horizon on a single trending regime → +5–10pp (but cherry-picking).
- Switching to position-trading on liquid stocks with longer holding periods → +3–5pp.

None of these is the foundry architecture.

---

## Q6. Changes to `agent_trader/` and `SYNTHESIS.md` to reflect this evidence

### Q6.1 `agent_trader/` — concrete changes

Current scaffold (per `find agent_trader -name '*.py'`): `analyst/{memory,graph}.py`, `core/{signals,strategy,types,risk}.py`, `backtest/runner.py`, `data/kite_history.py`, `execution/{openalgo_adapter,broker}.py`, `ops/audit.py`.

**Required additions** (in priority order; each is a new module/file, paths absolute):

1. **`/Users/Nikhil-S/Projects/Trading/agent_trader/validation/`** — new package, the missing piece.
   - `cpcv.py` — wrap `skfolio.model_selection.CombinatorialPurgedCV` or implement N=8, k=2, purge, embargo per Q4.
   - `pbo.py` — wrap `esvhd/pypbo` with the threshold check (PBO ≤ 0.5 hard, ≤ 0.2 soft).
   - `dsr.py` — implement Deflated Sharpe per Q4 formula; must consume an explicit `n_trials` counter from the project's trial log.
   - `mtrl.py` — Minimum Track Record Length helper.
   - `trial_log.py` — JSONL log of every parameter combo / LLM proposal / hyperparam variation tried. **N_trials must be the count of *all* of these**, not the count of the final one chosen.
2. **`/Users/Nikhil-S/Projects/Trading/agent_trader/validation/contamination_probe.py`** — port from V-9 work.
3. **`/Users/Nikhil-S/Projects/Trading/agent_trader/validation/novelty.py`** — AST-similarity filter against Alpha101/Alpha158 corpus, only if the foundry is later attempted.
4. **`/Users/Nikhil-S/Projects/Trading/agent_trader/backtest/runner.py`** — modify to support CPCV mode (multiple splits, distribution of OOS Sharpes output) rather than single train/test.
5. **`/Users/Nikhil-S/Projects/Trading/agent_trader/ops/promotion_gate.py`** — new module implementing the G0 → G1 promotion gate as an explicit graph of checks (CPCV, PBO, DSR, contamination probe, post-cutoff window, novelty if applicable). Steal the structure from `Aroesler1/Alpha-Factor-Mining-Framework` README.
6. **`/Users/Nikhil-S/Projects/Trading/tests/test_validation_harness.py`** — new test module verifying the validation modules on known-overfit and known-non-overfit synthetic strategies.

**Do NOT add to `agent_trader/` at this stage:**

- A `foundry/` or `generator/` package. **No LLM-as-strategy-generator code should land before the validation harness above is complete and tested.** This is the Phase 7 verdict in code form.
- LLM-driven mutation of strategy code. Same reason.

### Q6.2 `SYNTHESIS.md` — specific section edits

**Recommended edits, by section:**

- **§1 (top-line):** Add a one-line acknowledgment that the strategy-foundry architecture was evaluated in Phase 7 and rejected as the lead architecture; analyst-mode retained. Cite `/research/phase7_strategy_foundry/verdict.md`.
- **§5 (architecture diagram):** Annotate the "Strategy layer (DETERMINISTIC, no LLM)" box with a footnote: *"Phase 7 evaluated an LLM-as-strategy-generator augmentation. Verdict: not adopted. See `phase7_strategy_foundry/verdict.md` Q3."* No change to the diagram itself; the existing architecture is the correct one.
- **§6 (the ramp):** Tighten G0 gate thresholds to the Q4 numbers in this file:
  - "Sharpe > 1.0 deflated" → "**DSR ≥ 0.95** with N_trials honestly counted from `trial_log.jsonl`"
  - Add: "**PBO ≤ 0.5** (hard), ≤ 0.2 (soft) via CSCV on S=16"
  - Add: "**CPCV with N=8, k=2, purge ±label-horizon, embargo 2% T**"
  - Add: "**At least one post-LLM-cutoff window evaluated**"
- **§7 (V-list):** Mark V-9 as **resolved with extension** — the contamination-probe design is complete and now reinforced by Profit Mirage / MemGuard / FinSABER evidence; the harness must be live before any LLM enters the signal path.
- **§7:** Add a new line "**V-10 (Phase 7):** Validation harness (CPCV + PBO + DSR + MTRL + post-cutoff window + contamination probe + novelty filter) implemented and unit-tested. Hard prerequisite for G0."
- **Appendix file map:** Add the four new Phase 7 files.

**Do NOT edit:**

- The market pick (NIFTY weekly OTM options) — unchanged.
- The Stage-gated ramp G0–G4 — structurally correct.
- The "LLM as analyst, rules as trader" framing — confirmed by Phase 7.

### Q6.3 Tracker / decision log

Add a single decision-log entry in `/Users/Nikhil-S/Projects/Trading/research/tracker.md`:

> **2026-05-21 — Phase 7 verdict: strategy-foundry architecture not adopted.** LLM-as-online-analyst architecture retained. Validation harness (CPCV/PBO/DSR + contamination probe + novelty filter) elevated from "good practice" to **hard G0 prerequisite (V-10)**. See `phase7_strategy_foundry/{verdict,literature,github_landscape,contamination_in_generation}.md`.

---

## Final brutal restatement

The user's proposed architecture is a real, well-motivated, technically reasonable proposal. It is also **not supported by the evidence as of May 2026.** Zero peer-reviewed work shows LLM-generated strategies surviving LdP-grade validation; three rigorous works show the alpha is contamination; the OSS community has built generators but not validators; the user's economics cannot absorb the contamination tax; and the user's venue (Indian weekly options) is precisely the kind of universe where LLM training data is moderately rich on narrative but poor on strike-granular signal.

**The right move is to keep the SYNTHESIS architecture and build the validation harness defined in Q4.** That harness is what the foundry *would* need to be honest; it is also what the analyst-mode architecture needs to be honest. Build it once, use it for whichever architecture you run.

If, after running the analyst-mode architecture through paper trading and the new harness for 6+ months, the user has accumulated **genuine personal evidence** (T4-grade, in-repo) that a foundry component would add something the analyst loop misses, *that* is the moment to revisit Phase 7. Not before.
