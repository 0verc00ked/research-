# D3 + D1 + D5 — Consolidated Postmortem

**Date:** 2026-05-21
**What we built:** A real research engine — HMM regime classifier + cross-asset lead-lag scanner + conjunctive setup discovery — and ran it end-to-end on NIFTY.
**What we found:** Zero surviving strategies. The harness did its job.

## What worked (the engine itself)

| Component | Status | Evidence |
|---|---|---|
| D3 HMM regime model | ✅ well-calibrated | 5/6 known events correctly classified; dwell times sensible (64/36/34 bars across calm/range/bear) |
| D1 lead-lag scanner | ✅ statistically sound | Found 424 FDR-significant relationships; the strongest (SP500/NASDAQ → NIFTY @ 1d) match well-known time-zone effects |
| D5 conjunctive search | ✅ honest accounting | 377 total trials, 3 survived BH-FDR on train, 1 on val, 0 on OOS |

The research engine itself is the real artifact. ~600 LoC across `agent_trader/regime/`, `agent_trader/scanner/`, `agent_trader/setups/`. Reusable for any future hypothesis on any Indian instrument.

## What didn't work (the strategies)

Of 377 conjunctive setups searched across 13 features:
- 3 survived train-window BH-FDR
- 1 survived val-window sign + t≥1.0 (`regime_calm`)
- **0 survived 2024-2026 OOS sign consistency**

The single train+val survivor was `regime_calm`:
- 2015-2022: +0.25% mean 5d return in calm regimes
- 2022-2024: +0.34% (consistent)
- **2024-2026: -0.05% (sign flipped)**

This is textbook overfitting that survives one out-of-sample period but not a second. The reason the harness uses a *post-LLM-cutoff* OOS window is to catch exactly this.

## Cumulative evidence across the whole project

| Experiment | Strategies tested | Survived harness |
|---|---:|---:|
| W3-4 (boring deterministic) | 3 | 0 |
| W7-8 (disclosure text, headline-only) | classification methodology | 0 (G0d failed) |
| D3+D1+D5 (regime + lead-lag + conjunctions) | 377 | 0 |
| **Total** | **383 setups** | **0** |

The Bayesian update at this point is strong: **retail-tradable edge on NIFTY at daily-bar resolution with these features does not exist, or is too small to extract with our methods**. This is not a failure of the research methodology — it's a finding of the research methodology.

## Three honest reasons this could still be wrong

1. **Wrong horizon.** 5-day forward might be too long. Intraday (which we can't trade well anyway given LLM latency) or longer (1-month positional) might harbor edge.
2. **Wrong features.** 13 binary conditions are coarse. Continuous features + more sophisticated models (gradient boosting, deep nets) might find subtler patterns. But more model complexity also expands the overfit surface.
3. **Regime non-stationarity.** 2024-2026 may be a genuinely different market (SEBI algo framework, post-COVID dynamics). The harness rightly killed setups that don't survive this shift — but a setup that *would have worked* in 2025+ could exist with different conditioning.

## What the harness ALSO catches

A subtle and valuable point: D5 found `regime_calm` had t=+3.53 in val. Without OOS, this would have looked like a discovered edge. **The OOS gate is what saved us from deploying it.** This is the entire point of the post-LLM-cutoff window mandated by the harness — and we just saw it earn its keep.

## Recommended next steps

Three options, ranked by my honest preference:

### Option α: Package the research engine and stop (recommended)
Treat what we've built as the final product:
- `agent_trader/validation/` (López de Prado-grade harness)
- `agent_trader/portfolio/` (bounded-ruin allocator with regret proof)
- `agent_trader/regime/` (HMM regime classifier)
- `agent_trader/scanner/` (lead-lag scanner with FDR)
- `agent_trader/setups/` (conjunctive setup discovery)

Polish docs, write a README, MIT-license it, publish to GitHub. Even with zero P&L, this is a real contribution to Indian-retail-quant tooling. Most retail traders don't have any of this; you'd be in the top 1% of methodological discipline.

### Option β: Try one more high-conviction angle
Specifically, options-volatility relative-value on NIFTY weekly options. This is **D4 from the earlier menu** and requires capital >₹2L for SPAN margin, so it's not immediately tradable for you — but the analytics could be built and shelved for later. ~6 hours of work to build, no immediate P&L path.

### Option γ: Stop the project entirely
Take the cumulative negative evidence seriously and walk away. ₹0 spent on trading, ~₹14k spent on infra. Useful tools built. No edge found. This is a clean exit and honestly the most honest reading of the cumulative evidence.

## My personal recommendation

**Option α.** The research engine is real and valuable; packaging it as an artifact is concrete output. Continuing to hunt for alpha after 383 honest tests with zero survivors is increasingly hard to justify on prior probability. But α gives you a defensible artifact to point to, future-proofs the work for if you return to this later, and respects the time already spent.

Option β only makes sense if you genuinely have capital scaling on the horizon. Option γ is the cleanest emotional exit but throws away a real asset.
