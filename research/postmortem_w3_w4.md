# Postmortem — W3-4: Three Boring Strategies

**Date:** 2026-05-21 (executed same day as preregistration; W3-4 timeline compressed because backtests were fast on yfinance daily data)
**Pre-registration:** `research/preregistration.md`
**Run script:** `scripts/w3_run_all.py`
**Trial log:** `trial_log.db` (56 rows recorded)

## Headline

**All three strategies FAILED the harness.** This was the expected outcome (70% prior in the pre-registration). The harness is working; the obvious patterns are not exploitable.

Cumulative spend: **₹0** (free yfinance data, local compute). We learned that S1, S2, S3 are dead without paying live to discover it. That is the win condition.

## Per-strategy results

### S1 — Thursday reversion

| Metric | Value | Gate | Pass? |
|---|---|---|---|
| Best in-sample Sharpe | 0.017 | — | — |
| All-variants Sharpe (min/med/max) | -0.62 / -0.46 / 0.02 | — | — |
| DSR | 0.000 | ≥ 0.95 | ❌ |
| PBO | 0.218 | ≤ 0.5 | ✅ |
| CPCV folds positive | 0.39 | ≥ 0.60 | ❌ |
| n_trades (best) | 310 | ≥ 50 | ✅ |

**Verdict:** FAIL on DSR + CPCV.
**Diagnosis:** The best variant scrapes a Sharpe of 0.02 — essentially zero edge. Expected-max-under-null at n_trials=12 is 1.66, so the observed Sharpe is below pure-luck threshold. Median variant Sharpe is -0.46, meaning the hypothesis space mostly *loses money* after costs. The "reversion" isn't there at daily resolution, at least net of 0.05% × 2 per round trip.

**What this rules out:** Daily-bar post-expiry reversion on NIFTY at the parameter grid tested.
**What it does NOT rule out:** Intraday Thursday-close mean reversion (e.g., 14:45 → 15:25 intraday window). yfinance daily can't see this; would need Kite intraday data. Documented as future hypothesis if the team revisits.

### S2 — VIX regime conditional momentum

| Metric | Value | Gate | Pass? |
|---|---|---|---|
| Best in-sample Sharpe | 0.070 | — | — |
| All-variants Sharpe (min/med/max) | -0.35 / -0.09 / 0.07 | — | — |
| DSR | 0.000 | ≥ 0.95 | ❌ |
| PBO | 0.634 | ≤ 0.5 | ❌ |
| CPCV folds positive | 0.57 | ≥ 0.60 | ❌ |
| n_trades (best) | 303 | ≥ 50 | ✅ |

**Verdict:** FAIL on all three substantive gates.
**Diagnosis:** Classic overfit signature. In-sample best Sharpe 0.07 looks ok-ish, but PBO of 0.634 means the in-sample winner is **below median** in 63% of bipartitions — the parameter grid contains no genuinely better-than-median variant; you'd pick badly out-of-sample more often than not. Mean in-sample Sharpe 0.19, mean OOS Sharpe -0.17 — full sign reversal across folds.

**What this rules out:** The hypothesis that India-VIX percentile + simple momentum produces tradable signal on daily NIFTY, in the parameter ranges tested.
**What it does NOT rule out:** VIX as a *risk filter* (avoiding trades, not entering them). The strategy here used VIX to *enter* — a defensive use is a different hypothesis. If we revisit, that becomes trial #57+.

### S3 — Day-of-week dispersion

| Metric | Value | Gate | Pass? |
|---|---|---|---|
| Best in-sample Sharpe | **-1.06** | — | — |
| All-variants Sharpe (min/med/max) | -2.15 / -1.64 / -1.06 | — | — |
| DSR | 0.000 | ≥ 0.95 | ❌ |
| PBO | 0.296 | ≤ 0.5 | ✅ |
| CPCV folds positive | 0.04 | ≥ 0.60 | ❌ |
| n_trades (best) | 1602 | ≥ 50 | ✅ |

**Verdict:** FAIL — and emphatically.
**Diagnosis:** Every single variant has *negative* Sharpe. The "best" variant is the least-bad loser. 1602 trades means transaction costs (0.1% per round trip on the pair × ~800 round trips) drowned everything. The day-of-week effect, if it exists at all in NIFTY/BANKNIFTY dispersion, is smaller than 0.1% per round trip.

**What this rules out:** Day-of-week NIFTY-vs-BANKNIFTY pair trading at any tested entry day or direction or hold-days, with realistic retail costs.
**What it does NOT rule out:** Day-of-week effects on a single index (no pair, half the cost), or on a less-correlated pair. Both are different hypotheses.

## Aggregate observations

1. **PBO behaved sensibly across all three.** S1 PBO=0.22 (well-shuffled variants, no single winner emerges), S2 PBO=0.63 (parameter sweep dominated by overfit), S3 PBO=0.30 (everything loses similarly, no overfit because no one's winning). This pattern is what we want from a working PBO implementation.

2. **DSR with n_trials accounting was decisive.** Even the strategy with the highest raw Sharpe (S2 best = 0.07) got DSR=0.000 because the expected-max-under-null at 24 trials is 1.98 — i.e., a Sharpe of ~2 would be needed just to beat random chance from selecting the best of 24 noise variants. The observed 0.07 is nowhere near that.

3. **CPCV folds-positive ratio is informative.** S3 at 0.04 (only 1 of 28 folds positive) is a much stronger signal of "this is consistently losing" than the headline Sharpe alone. S1 at 0.39 is genuinely random-noise-around-zero.

4. **Costs dominate.** S3's 1602 trades × 0.1% = 160% drag. Even a modest gross edge would be eaten. This validates the CONCRETE_PLAN §3 break-even bar of ~23%/month — retail costs are a brutal hurdle.

5. **Honest n_trials counting matters.** If we had naively reported "best Sharpe 0.07 over 24 variants" as if n_trials=1, DSR would have been near 0.99 — wildly misleading. The harness *only* refuses these strategies because n_trials is honestly the variant count.

## What we learned that holds beyond these three strategies

- **The simplest "obvious" Indian-market patterns are dead at daily resolution and retail cost levels.** This is consistent with the 89% retail F&O loss rate.
- **The harness is sensitive enough to catch all three of these as failures, *and* correctly identified S2 specifically as overfit (PBO) versus S1/S3 as noise-around-zero (DSR/CPCV).** Different failure modes get different gate signatures. That diagnostic capability is worth the build cost.
- **The trial_log discipline mattered.** A naive analyst would have reported "S2 has Sharpe 0.07, looks marginal!" — the harness, with n_trials=24, said "no, that's below pure-luck threshold."

## Decisions

1. **All three strategies are CLOSED. Not paused, not "to revisit" — closed. Any future variant on the same data is a new trial counting against DSR.**
2. **CONCRETE_PLAN advances to W5-6 (allocator) as planned.** Having no surviving strategies at W4 does not change the W5-6 build — the allocator is a meta-layer with value independent of strategy survival.
3. **W7-8 disclosure channel proceeds as planned.** It's a fundamentally different LLM role.
4. **If by W12 no strategy has survived any channel, the honest action is to stop and write the project-level postmortem.** Stand by the kill criteria in CONCRETE_PLAN §7.

## What we did NOT spend

- ₹0 capital (free yfinance data)
- ~3 hours of human time
- Negligible compute
- Zero live trading

vs. the counterfactual where we deployed any of these to paper or live: we would be in the middle of a 60-day paper-trading cycle right now, watching them lose, with significantly higher resentment toward the process. The harness saved that.

## N_trials accounting (running total)

| Strategy | Variants tried | Cumulative trials | Status |
|---|---|---|---|
| s1_thursday_reversion | 12 | 12 | CLOSED |
| s2_vix_regime | 24 | 36 | CLOSED |
| s3_dow_dispersion | 20 | 56 | CLOSED |

Future strategies on NIFTY daily data should be aware that this dataset has been touched. New hypotheses on the same dataset will need to count *some* deflation against these 56 prior trials, even on a different parameterisation — that's the honest application of the Bailey/LdP framework.
