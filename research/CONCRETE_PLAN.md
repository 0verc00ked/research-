# Concrete 12-Week Plan — Agent Trader

**Date:** 2026-05-21
**Author:** Claude Opus 4.7, in conversation with Nikhil
**Status:** Proposed. Replaces the vague "next steps" lists in earlier docs.

This plan is what I would actually do with 12 weeks of focused work. Every week has a deliverable. Every gate has a numeric criterion. Every branch has a kill-or-continue answer. Read this once, then execute. Do not relitigate without new evidence.

---

## §1 Reframed objective

**We are not optimizing for profit.** Profit is a downstream observation, not a steerable variable. We are optimizing for **information** — a system that can reliably distinguish "I have edge" from "I got lucky" with **bounded loss** if I don't.

If after 12 weeks we have learned that we have no edge in any of the three channels below, and spent ≤₹50k doing so (infra + tiny live + my time at ₹0 opportunity cost), that is a **successful outcome**. The alternative — finding out we have no edge by losing ₹2L over a year of false confidence — is what we are buying insurance against.

Hold this frame for the entire 12 weeks. It will be tempting to abandon it the first time something looks profitable. Don't.

---

## §2 Three honest edge candidates

We will pursue all three in parallel. They are independent; failure of one doesn't doom the others. They are ranked by my honest probability of survival.

### E1 — Indian microstructure seasonalities (no LLM)
*Probability of yielding a passing strategy: ~30%*

Known, documented, classical-evidence-backed patterns specific to Indian markets:
- **Weekly-expiry-day mean reversion on NIFTY** (Thursdays, 14:30–15:25 IST). Retail panic-sells/buys near close on expiring weeklies. Index futures often revert toward VWAP.
- **First-30-min vs last-30-min** intraday on NIFTY futures. Opening volatility tends to overshoot; last-30-min has trend continuation.
- **Day-of-week effect** on Indian small/mid-cap indices. Mondays and Fridays show different drift profiles than mid-week. Documented in multiple Indian-market papers (Patel 2008; Auwalu Ibrahim 2024).
- **India-VIX-percentile regime filter.** When VIX > 80th percentile of trailing 60d, index futures have negative skew in next-3-day returns.

None of these need an LLM. All are mechanically testable. Most will fail the harness. Maybe one survives.

### E2 — Disclosure-text comprehension on mid-caps (LLM uniquely positioned)
*Probability of yielding a passing strategy: ~15%*

This is the **one place an LLM has a defensible mechanism advantage**: unstructured-text comprehension on novel content under time pressure.

- BSE Corporate Announcements feed (free, public, structured RSS): ~500–1000 announcements/day
- NSE equivalent: ~300–500/day
- LLM (Haiku 4.5, ~0.8 s TTFT) reads each filing in 5–15 s; classifies as material/non-material × positive/negative/neutral with confidence
- The candidate edge exists only on mid-cap names where algorithmic NLP coverage is thin and the absorption window between disclosure and full price reaction is on the order of minutes to ~1 hour
- Large-caps are dead (Bloomberg/Reuters arbitraged this years ago)
- Micro-caps are dead (liquidity ≈ 0; you can't get in)
- Mid-caps (market cap ₹2k–20k Cr) are the sweet spot — algo coverage thin, retail liquidity adequate for ₹15–25k position

**Contamination is structurally absent here**: the LLM is reading a filing that did not exist before this minute, on a company about which the LLM's training data is, at best, stale by months.

This is the most ambitious channel. Most likely to fail on cost/liquidity, not on alpha.

### E3 — Bounded-ruin online-learning allocator (mathematical, alpha-agnostic)
*Probability of being valuable: ~80%*

Not a strategy. A **portfolio meta-layer** with a provable regret bound, that runs over whatever strategies survive E1/E2. Even if E1 produces nothing and E2 produces nothing, E3 is still worth building because:
- It makes future strategy work safer
- It gives you a real mathematical artifact in the codebase
- It enforces capital allocation discipline that no off-the-shelf retail framework has

This is the only of the three I have ~complete confidence will be done well; whether it has anything to allocate to is the open question.

---

## §3 Refined architecture

```
                           ┌──────────────────────────────┐
                           │  validation/  (HARNESS)      │
                           │  CPCV · PBO · DSR · trial_log│  ◄── G0 gate
                           └──────────────┬───────────────┘
                                          │ promotes
                                          ▼
   E1 ─► strategies/microstructure_*  ─┐
                                       ├─► portfolio/  ◄── E3 (allocator)
   E2 ─► strategies/disclosure_*    ──┘    bounded-ruin
                                                │
                                                ▼
                                     ┌─────────────────┐
                                     │ KillSwitch      │
                                     └────────┬────────┘
                                              ▼
                                     ┌─────────────────┐
                                     │ Broker.place    │
                                     └────────┬────────┘
                                              ▼
                                       AuditLog (SEBI)
```

Note what changed from previous architecture: **the LLM-as-online-analyst pillar (regime tagging) is gone from v1**. Reason: it's a hedge, not a bet. Defer it to v2 after the harness can ablate it cleanly. The disclosure parser is a different LLM role with a stronger mechanism.

---

## §4 Twelve weeks, week by week

### Weeks 1–2: Validation harness + clean data

**Deliverables (code in `agent_trader/`):**
- `validation/trial_log.py` — append-only SQLite registry. Every strategy run gets a row: hash of code, params, dataset, N_trials_so_far, results.
- `validation/cpcv.py` — Combinatorial Purged Cross-Validation. N=8, k=2 holdout, purge ±label_horizon, embargo 2% of T. ~150 LoC.
- `validation/pbo.py` — wraps `pypbo` if Python-3.12-compatible; else port to numpy. CSCV S=16 → PBO scalar. ~120 LoC.
- `validation/dsr.py` — Deflated Sharpe Ratio. Reads N_trials from `trial_log`. ~80 LoC.
- `validation/regime_splits.py` — partitions any time-series dataset into ≥1 bear, ≥1 calm, ≥1 shock window. Includes ≥1 post-2025-01 window (post-LLM-cutoff). ~80 LoC.
- `data/qlib_indian.py` — Kite Connect → qlib bin format adapter. Backfills NIFTY/BANKNIFTY/SENSEX OHLCV + India-VIX from 2018-01.
- Data audit script — verifies survivorship cleanliness (delisted constituents, expired contracts), point-in-time correctness, gap reporting.

**Gate G0a:** harness produces a structured pass/fail report on a known-overfit synthetic strategy (constructed to fail PBO). If it doesn't catch the synthetic overfit, the harness itself is broken — fix before proceeding.

**Capital spend so far: ₹0 + 2 weeks time + ₹3.5k infra**

### Weeks 3–4: E1 — three boring strategies through the harness

Hand-write three deterministic strategies, no LLM:

- **S1: NIFTY weekly expiry-day VWAP-reversion** (every Thursday 14:30–15:25). One-paragraph mechanism: retail flow near close on expiring weeklies creates predictable index-futures dislocation; mean revert within 55 min with hard stop. Three parameters max.
- **S2: India-VIX-regime filtered momentum** on NIFTY futures, daily bars. One-paragraph mechanism: in VIX>P80 regimes the index has documented negative skew over 3-day windows; short futures with tight stop, otherwise no position. Two parameters.
- **S3: Day-of-week NIFTY-Junior pair-trade.** Long NIFTY/short NIFTYJR (or vice versa) based on documented day-of-week dispersion. Two parameters.

For each:
- Pre-register the hypothesis (commit to git BEFORE running the backtest — no peeking)
- Run through harness
- Record pass/fail in `trial_log` honestly
- N_trials counter increments for each parameter tweak you make

**Gate G0b — STOP at end of week 4 and write a postmortem.** Expected outcome: 0–1 of the three pass. If 0 pass: that is information, not failure. We learned that the obvious patterns are too obvious. Move to E2 + E3.

**Capital spend: ₹0 + 4 weeks time + ₹7k infra cumulative**

### Weeks 5–6: E3 — the bounded-ruin allocator

**Deliverables:**
- `portfolio/exp_weights.py` — exponentiated-weights / Hedge algorithm with theoretical regret bound √(2T log K). Tested on synthetic adversarial sequences to confirm bound holds empirically.
- `portfolio/bayesian_sizing.py` — Normal-Inverse-Gamma conjugate sizing. Prior: μ₀=0, κ₀=100 (skeptical). After n trades, posterior mean estimate is `n·x̄ / (100+n)`. Position size scales by fractional Kelly on the posterior, not on raw realized mean.
- `portfolio/kelly.py` — fractional Kelly utility, capped at f*/10.
- `portfolio/allocator.py` — composition: weights from `exp_weights`, sizing per slot from `bayesian_sizing`, hard ruin cap from `kelly`. Single `allocate()` entrypoint that takes strategies + recent returns + capital and returns a per-strategy capital allocation vector.

**Gate G0c:** synthetic-data validation. Construct an adversarial 5-strategy environment where the best strategy is unknown a priori. Confirm:
- Cumulative regret ≤ theoretical bound at T=252, K=5
- Bayesian posterior is shrunken to ≤30% of MLE estimate at n=30
- No allocation can exceed f*/10 even when posterior mean is large

**Capital spend: ₹0 + 6 weeks time + ₹10.5k infra cumulative**

### Weeks 7–8: E2 — the disclosure channel, evaluated honestly

**Deliverables (no live trading yet):**
- `analyst/disclosure_subscriber.py` — BSE + NSE corporate-announcements RSS subscriber. Persists every disclosure with timestamp, attachment, source.
- `analyst/disclosure_classifier.py` — Haiku-4.5 classifier. Output: `{materiality: 0..1, sentiment: -1..1, instrument: NSE_ticker, confidence: 0..1, summary: str}`. Strict JSON schema, refusal on ambiguity.
- **Manually label 200 historical disclosures** (from past 6 months, mix of large/mid/small caps) — this is *your* work, not the LLM's. The labels become the ground truth.
- Measure: LLM classification accuracy vs your labels. Target: ≥85% on materiality (binary), ≥75% on direction (3-class). If below, the channel is dead.
- **The critical measurement: absorption window.** For each historical disclosure in the labeled set that the LLM (and you) flag as material+directional, plot price-vs-time from disclosure publication. Measure the half-life of the move. If the median half-life on mid-caps is <5 min, channel is dead. If 10–60 min, channel is alive. If >60 min, it doesn't need an LLM (you could read manually).

**Gate G0d at end of week 8:**
- Classification accuracy ≥85% materiality AND ≥75% direction → continue
- Median absorption half-life on mid-caps in [10 min, 60 min] → continue
- Either fails → kill E2, do not invest more time. Re-prioritize remaining weeks toward E1 deeper work.

**LLM API cost for this phase:** ~200 historical disclosures × 2k tokens in / 300 tokens out × Haiku rate ≈ ₹40 total. Negligible.

**Capital spend: ₹40 LLM + 8 weeks time + ₹14k infra cumulative**

### Weeks 9–10: Backtest the surviving channels through the harness

Whatever passed weeks 3–8 (likely 0–2 strategies) gets backtested through `validation/` again at higher resolution:
- Full CPCV with all folds
- PBO on the parameter grid you actually swept (honestly counted in `trial_log`)
- DSR with N_trials reflecting *all* iterations across all 10 weeks
- Stress test under simulated worst-fee scenarios (1.2× rated fees; 2× slippage)
- Paper-traded forward-test design: how would these strategies have run live over the last 6 months had you been live?

If anything has DSR ≥ 0.95 AND PBO ≤ 0.5 AND positive in ≥1 post-2025-01 window AND defensible mechanism: it advances to paper.
If nothing does: weeks 11–12 become a postmortem + decision-tree.

**Capital spend: ₹40 + 10 weeks time + ₹17.5k infra cumulative**

### Weeks 11–12: Paper trading + decision

**If anything survived week 10:**
- Wire to Upstox Sandbox + Alpaca paper (for cross-venue sanity)
- Run for 14 days minimum (≥10 trades preferred; tight on options weekly cycle)
- Daily compare paper P&L vs same-day expected from backtest model
- KPI: |paper Sharpe – backtest Sharpe| / σ(backtest Sharpe) ≤ 1.0. If divergence > 1σ: backtest lied; back to harness.

**If nothing survived:**
- Write postmortem: which hypothesis died why, what we'd test differently, what (if anything) was learned about the channels
- Honest decision: do we continue another 12 weeks, or is the answer "this is not worth more time"?

**End-of-12-week deliverable regardless of outcome:** A signed decision document — go-to-G2-live, run-another-12-weeks, or stop.

**Capital spend ceiling: ₹50k (₹42k infra/data + ~₹100 LLM + 12 weeks of your time)**

---

## §5 Capital plan

| Period | Spend | What |
|---|---|---|
| Weeks 1–12 | ≤₹42k | Infra (₹3.5k × 12 = ₹42k) + LLM API ~₹100 + data ~₹0 (Kite included) |
| Week 13+ (only if G0d passes) | ₹5k | G2 plumbing — smallest possible live trades to verify order pipeline |
| Week 17+ (only if G2 passes 30 days clean) | +₹10–20k | G3 edge-detect tier |
| Year 2+ (only if G3 demonstrates t-stat > 2 over 3 months / 50 trades) | 2× steps | G4 scale |

Total exposure if everything fails: **~₹50k**. That is the budget of this experiment. Past it, we stop.

---

## §6 What "successful failure" looks like at week 12

If I had to bet, the most likely outcome is:
- 0 of 3 E1 strategies pass the harness
- E2 fails on absorption-window measurement (median <5 min on tradable mid-caps)
- E3 is built cleanly and works as designed but has nothing to allocate to
- Spend: ₹42k, mostly infra

That outcome is a **win**, not a loss. You'll have:
1. A working validation harness that future-you (or anyone else) can submit strategies to
2. A real bounded-ruin allocator with a regret-bound proof
3. A disclosure-subscriber + classifier (works for non-trading use too — your day job is security, this kind of pipeline has analog uses)
4. Hard evidence that the obvious edges are not there, recorded honestly in `trial_log`
5. A scaffold you (or future research) can hand to a quant friend and they'll respect it
6. The discipline of having actually run a quant project honestly — that itself is rare among retail
7. Zero live trading losses

The alternative — going live at week 4 with a half-tested strategy because backtest looked good — is the path where you lose ₹50k in actual trades over 6 months instead of ₹42k in infra over 3 months, *plus* you've taught yourself to trust an overfit signal.

---

## §7 When to abandon the whole project

Hard kill criteria for the **project itself**, not just for a strategy:

- **Week 4:** Harness can't catch synthetic overfit → stop, the foundation is broken
- **Week 8:** E2 absorption window <5 min on mid-caps AND zero E1 strategies survive → reconsider scope. Maybe the right move is a hand-trading plan with no algo, or to abandon
- **Week 12:** Nothing in paper-test phase, postmortem identifies no realistic adjustment → stop and walk away with ₹42k spent. That is the cost of having genuinely answered the question.
- **Anytime:** SEBI framework changes materially → re-plan. Compliance risk is non-negotiable.
- **Anytime:** Personal capacity / interest / mental cost exceeds the math gains → stop. This is a hobby project, not a job.

---

## §8 What I'm 100% committing to (honestly)

I commit to building (in order):
1. Weeks 1–2: `validation/` harness (the highest-leverage code in the project)
2. Weeks 5–6: `portfolio/` allocator with regret-bound proof
3. Throughout: integrity of the `trial_log` — every tweak counts, no peeking
4. Honest reporting of results — pass, fail, or "this question doesn't have a clean answer yet"

I do **not** commit to producing a profitable strategy. I cannot. The math does not support that commitment. What I can guarantee is the framework that will tell you honestly whether one exists.

**This plan, executed honestly, has more value than the typical 99% of retail "AI trading" projects, even if it ends in week 12 with zero profitable strategies.** That's not a low bar — most retail projects end in losses and false lessons. This one ends in knowledge and bounded spend.

---

## §9 Open questions I cannot resolve from this chair

These need *your* decisions before week 1 starts:

- **Q-A:** Are you OK with the ₹50k budget ceiling? If hard ceiling is lower (e.g., ₹25k), the plan compresses but doesn't fundamentally change.
- **Q-B:** Are you OK with the 12-week timeline? If you want to compress, the right cut is dropping E2 (disclosure channel) since it's the most speculative.
- **Q-C:** Do you want me to actually start writing `validation/` now, or do you want to push back on the plan first?
- **Q-D:** Should I save this plan to `research/CONCRETE_PLAN.md` (done) as the canonical execution doc, replacing the looser "next steps" in SYNTHESIS §8? My recommendation: yes — make this the file you read at the start of every work session.
- **Q-E:** Are you OK with me using your GitHub token to fetch `pypbo`, `qlib` etc. during the harness build? If yes, leave the token in `.env` for now. If not, I'll use only what's pip-installable from PyPI.
