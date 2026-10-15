# Classical-but-Under-Deployed Strategy Classes — Honest Review

**Date:** 2026-05-21
**Author context:** Solo Indian retail; ₹15–25k live capital ceiling for G2/G3; no SPAN-margin tier yet; harness (CPCV + PBO + DSR + N_trials log) already built; 383 setups have already been killed by the OOS gate.
**Scope:** Four well-established strategy primitives we have NOT yet tried. For each — published OOS Sharpe with citation, implementation effort, capital floor, Indian viability, and an honest probability that *we* can extract usable edge.
**Trust grades** (consistent with `trust_rubric.md`): T0 = peer-reviewed top journal, T1 = peer-reviewed second tier, T2 = working paper / preprint with credible authors, T3 = secondary / blog with primary citations, T4 = practitioner blog only.

---

## 1. Cointegration-based pairs trading (Engle-Granger 1987, Johansen 1988)

### What it is
Find two (or k) instruments whose linear combination is stationary. Trade the spread's z-score: short the rich leg, long the cheap leg, exit on mean reversion. Modern refinement (Avellaneda-Lee 2010): model residuals as Ornstein-Uhlenbeck, derive entry/exit thresholds from the OU half-life and noise variance.

### Published OOS Sharpe (and the "edge is gone" question)

| Study | Window | Reported Sharpe | Trust |
|---|---|---|---|
| Gatev, Goetzmann, Rouwenhorst, *RFS* 2006 (NBER w7032) | 1962–1997 US | ~11% annualised excess; Sharpe ~1.2 on top-20 pairs portfolio | T0 |
| Do & Faff (2010, 2012) extending GGR | 1989–2009 US | Profitability halves; gross Sharpe drops to ~0.4–0.6 post-2002, near zero net of frictions by 2008 | T1 |
| Zhu (Yale WP 2024) "Examining Pairs Trading Profitability" | through 2023 US | Edge effectively gone; raw Sharpe < 0.3 post-2010 net of costs | T2 |
| Avellaneda & Lee, *Quant. Finance* 2010 | 1997–2007 US (ETF + PCA, OU spreads) | Sharpe 1.1 ETF-based; 1.51 with volume info 2003–07; **author-acknowledged degradation since 2002** | T0 |

**Honest reading:** The classical equity pairs edge has materially decayed in US markets since ~2002–2008. Crowding is *not* the main explanation per Zhu (2024); the underlying co-substitution structure has weakened. Avellaneda-Lee's OU/PCA generalisation is a real upgrade but its own paper documents post-2002 decay.

### Indian-market specific evidence

| Study | Window | Reported | Trust |
|---|---|---|---|
| Sarkar, Sen et al., arXiv 2211.07080 (2022) "Designing Efficient Pair-Trading Strategies … for Indian Stock Market" | 2018-01 → 2020-12 train, 2021 test | Cointegrated pairs in auto/realty/IT yielded annualised returns 16% on best sector; Sharpe ~1.34 in-sample | T2 |
| Sarkar et al. companion paper "Cointegration and Clustering-based Approach" (2023) | similar | leveraged variant 3.5× → 59% over 3 yrs, Sharpe ~2.28 (leverage-inflated; SE not reported) | T2 |
| Stochastic-Spread Pairs in Indian Commodities (arXiv 1907.08397) | MCX 2014–2018 | Sharpe > 1.4 *in-sample* on cointegrated pairs; no clean OOS | T2 |

**Caveats specific to these Indian papers:**
- All are in-sample or single-year holdout; none use CPCV or PBO. Selection bias from sector cherry-picking is severe (they pick "top sectors that worked").
- N_trials uncounted. By our harness standards, none of these have cleared a real OOS bar.
- Realised SEBI fees, STT (esp. post-2026-04-01 hikes), and the F&O lot-size mismatch are not modelled.

### Implementation complexity
- **Code:** ~400 LoC if reusing `statsmodels` (Engle-Granger ADF, Johansen), `pykalman` for Kalman-filtered hedge ratio.
- **Data:** Daily adjusted closes for ~50-200 NSE stocks; expired-future-clean only matters if pairs are F&O legs.
- **Estimation:** Rolling cointegration is fragile — hedge ratio drift is the #1 production killer.

### Capital floor
- **Cash equity pairs (long-short on stocks):** Long leg is free of margin; short leg in India is overnight-restricted (must use SLB or F&O). For overnight shorts you effectively need stock futures = lot sizes ₹5-15L notional ⇒ **capital floor ~₹2-3L per pair**.
- **Intraday-only cash pairs:** Possible with ₹15-25k but reversion timescale (days-weeks per Avellaneda-Lee OU half-lives of 5-30 days) is incompatible with intraday close. **Mismatch kills it.**
- **ETF pairs** (e.g., NIFTYBEES vs JUNIORBEES): Long-only basket-vs-basket reversion is feasible with ₹20-25k but the spread is small; per-trade ₹40 round-trip + STT + slippage probably exceeds expected reversion edge.

### Honest probability for us
- The published edge has decayed globally; Indian "evidence" is in-sample only and has not been validated post-2024.
- Capital floor for the *real* version (overnight stock-futures spread) is 10× our ceiling.
- The ETF-pair variant that fits our capital is the most fee-eaten variant.
- **P(we extract Sharpe > 0.5 net OOS in 6 months) ≈ 0.10.**

---

## 2. End-of-day index-rebalancing front-running

### What it is
Index reconstitutions are calendar-scheduled and the inclusion/exclusion list is announced ~4 weeks before the effective date. Index funds and ETFs must trade at the closing auction on the effective date. The aggregate buy/sell pressure is computable from float-adjusted weights and tracked AUM.

### Published evidence

| Study | Window | Finding | Trust |
|---|---|---|---|
| Petajisto, *J. Empirical Finance* 2011 | 1990-2005 US | S&P 500 inclusion: +8.8% announcement-to-effective; Russell 2000: +4.4%. Hidden cost to indexers 21-28 bp/yr (S&P), 38-77 bp/yr (Russell 2k). | T0 |
| Greenwood, *JFE* 2005 | Nikkei 225 redefinition 2000 | Massive demand-curve dislocation; arb dynamics documented. | T0 |
| **Greenwood & Sammon, NBER w30748 / HBS WP 23-025 (2023)** | 1980s → 2020s S&P 500 | **Inclusion abnormal return collapsed from +3.4% (1980s) → +7.6% (1990s) → +0.8% (2010-2020). Deletion effect from -large → -0.6%.** | T0 |
| Klug, EFMA 2023 WP "Trading on Index Constituent Changes" | recent US/EU | Confirms decay; arbs anticipated; counterparties pre-position. | T2 |

**The killer finding:** Greenwood-Sammon (2023) explicitly title their paper *The Disappearing Index Effect*. The edge that existed in the 1990s is ~90% gone in the US despite *more* index AUM. Reason: counterparties (active mgrs, alternative liquidity providers) now stand ready to sell into inclusions and buy on deletions. The asymmetry got arbed out.

### Indian evidence

| Study | Window | Finding | Trust |
|---|---|---|---|
| Selvam, Indhumathi, Lydia, *Asia-Pacific JMR* 2012 | CNX Nifty 2000s | Inclusion announcement → modest positive, reverses by effective date; deletions stronger initial drop with partial recovery. Conclusion: **no excess returns extractable.** | T1 |
| IJAR 2025 study, 44 inclusions + 43 exits 2010–2024 | three sub-periods | Asymmetric; effects are short-lived; no permanent valuation effect. | T3 |
| NSE/AMFI ad-hoc commentary | recent | NIFTY rebalances are semi-annual (Mar/Sep); thematic indices quarterly. Inclusion lists pre-announced ~4 weeks. | T4 |

### Implementation complexity
- **Code:** Easy. ~200 LoC: scrape NSE rebalance announcements, compute passive AUM × target weight × float, generate trade list, fade or front-run with limit orders into close.
- **Hard part:** Estimating *which* passive funds rebalance on T vs T-1 vs T+1, and the active "shadow" liquidity that has already eaten the trade.

### Capital floor
- Tradable on stock futures of inclusion/deletion candidate. **₹1.5-3L per single name** (typical stock-futures margin).
- Cash-equity-only variant (just buy/short a few of the announced inclusion candidates) is technically possible at ₹15-25k for 1-2 names, but you can hold only the long side (short overnight needs F&O).

### Is it still tradable in 2026?
- **US: largely no** (Greenwood-Sammon 2023, T0).
- **India: empirical evidence (Selvam 2012, IJAR 2025) already showed effects are short-lived and not exploitable for retail.**
- Plus: post-2026-04-01 SEBI algo framework adds disclosure / latency requirements; institutional flow has hours of head-start.

### Honest probability for us
- Direct front-running is gone in US per T0 evidence; Indian T1 evidence says it never persisted.
- The only residual play is *fading* the inclusion pop (selling strength on T+1/T+2) — but that's an asymmetric short with overnight margin needs.
- **P(net Sharpe > 0.5 OOS) ≈ 0.08.**

---

## 3. FII / DII flow signal (India-specific)

### What it is
NSE and BSE publish daily net-buy/net-sell numbers for Foreign Institutional Investors (FIIs) and Domestic Institutional Investors (DIIs) in cash equity and F&O segments, typically by 6 PM IST same day. Treat as a leading or coincident sentiment signal for next-day NIFTY return.

### Published evidence

| Study | Window | Finding | Trust |
|---|---|---|---|
| Jain, Nair, Jain (SSRN 2707461, 2015) | monthly | Granger causality between FII flow and Nifty — bidirectional in some sub-periods, **not robustly predictive at monthly frequency**. | T2 |
| Shah (SSRN 2013, 3353659) | older monthly | FII flows correlate but causality is weak / direction-ambiguous. | T2 |
| PMC9145119 "Trading Behaviour of FIIs in Indian Stock Markets" | daily | Bidirectional causality Nifty ↔ FII equity flow at lag 1; **FII flow follows past Nifty returns more than it leads.** | T1 |
| IJMRT 2025 "Indian Equity Flows: FII Withdrawals vs DII" | 2020-2024 | DII flows have begun to *offset* FII withdrawals; the simple "FII sells → market drops" relation has weakened. | T3 |

**Honest reading:** The FII number is largely *coincident*, not leading. The intra-day NIFTY move and the EOD FII print are correlated because FIIs *are* a chunk of the day's tape — by the time the 6 PM print is public, the price has already moved. The literature does not support a clean next-day predictive signal robust to costs.

### Lead-lag / pricing-in latency
- FII data is released ~6 PM IST same day; futures and Gift Nifty trade past 11:30 PM, so any predictive content is absorbed by next morning's open.
- Multi-day FII selling *streaks* correlate with drawdowns (3+ weeks of net selling → 3-8% Nifty drawdown) but this is observation after the fact, not an entry signal.

### Implementation complexity
- **Code:** Trivial. ~100 LoC: scrape NSE/BSE EOD CSVs, compute z-score of net flow, signal generation.
- **Data:** Free and public from NSE.

### Capital floor
- Tradable as NIFTY futures (≈₹1.2-1.5L margin/lot) or NIFTYBEES ETF (any size). NIFTYBEES at ₹15-25k → buy/sell 50-80 units; per-trade ₹40 round-trip + STT is manageable.
- **This is one of the few primitives that physically fits our capital.**

### Honest probability for us
- Edge is coincident, not leading, per PMC9145119 (T1).
- Streak-based signals are correlated but the harness will likely kill them in CPCV.
- The one angle with possible residual: *DII counter-flow* as a regime tag (when DIIs absorb FII selling, mean-reversion regime). This is feature-engineering, not a standalone strategy.
- **P(net Sharpe > 0.5 OOS) ≈ 0.12 standalone; ≈ 0.20 as a regime feature combined with other signals.**

---

## 4. Volatility-risk-premium (VRP) harvesting

### What it is
Implied vol persistently exceeds realised vol because option buyers pay for tail insurance. Short volatility (short straddle, short strangle, iron condor, short variance swap) has positive average return as compensation for negative skew / large drawdowns in crisis.

### Published evidence (US/global, T0)
- Bondarenko (2014), *Review of Financial Studies* — variance risk premium documented robust, large, negative-skewed payoff.
- Ilmanen (2011) *Expected Returns* — chapters on vol selling: Sharpe ~0.7-1.0 in calm decades, but with crisis-period drawdowns of 30-60%.
- CBOE PUT/BXM indices: Sharpe ~0.6-0.9 over 30 years; max drawdown ~30% in 2008.

### Indian-market specific evidence

| Study | Window | Finding | Trust |
|---|---|---|---|
| "Does VRP from NIFTY options drive excess returns" — *Economic Sciences* 2024 | 5 yrs NIFTY 50 + India VIX | VRP positive ~74% of months; statistically significant. Vol-selling strategies (ATM short straddles delta-hedged) produce excess returns. **Drawdowns severe during stress.** | T2 |
| Kannan (Medium, T4) "Harvest VRP in Nifty" | 2010-2018 | Selling 30-delta puts on NIFTY: ~0.70% average yield/trade. Not net of margin opportunity cost, no Sharpe published. | T4 |
| CCIL WP ER/016 (T2) | USD/INR options | Documents VRP in INR options too; positive but smaller. | T2 |
| Indian academic on NIFTY straddles | 2024-2025 working papers | Implied-realised gap averages 3-5 vol points; Sharpe ~0.8-1.0 *before* tail events; 2020-Mar wiped >12 months of premium in 6 trading days. | T2 |

### Capital requirement
- **SPAN + Exposure margin for NIFTY weekly short straddle:** ~₹1.5-2L per lot (lot size 75 from Apr-2024 revision; one straddle = 1 call + 1 put short).
- Far-OTM iron condor (defined-risk, 4-leg) reduces margin to ~₹40-70k per lot — *theoretically* fits our ₹15-25k ceiling if we do micro-size on BANKNIFTY weekly (smaller lot) but it would be 1 lot only.
- **Margin requirement is the #1 reason we currently can't trade this. This was already flagged in `D3_D1_D5_postmortem.md` as Option β (D4 angle, shelved).**

### The "why does anyone hold long vol" question
Three real answers, not just irrationality:
1. **Insurance demand.** Pension funds, OPMs, family offices buy puts as portfolio hedge — they have a liability-side reason to overpay.
2. **Negative skew is genuinely costly to leveraged players.** Sharpe ignores skew; a Sharpe-1.0 strategy that loses 60% in a tail is rationally avoided by margin-constrained traders.
3. **Crash years are concentrated.** Mar 2020, Feb 2018 (Volmageddon), Aug 2015 — single events erase years of premium. If your career timeline is <5 years, you have meaningful odds of meeting one.

So VRP is *real edge as compensation for real risk*, not a free lunch. Selling it without an explicit tail hedge is selling insurance without reinsurance.

### Implementation complexity
- **Code:** Moderate. ~600 LoC: option chain pull, delta/vega computation, position sizing by 1σ tail loss, daily delta-hedge with futures.
- **Operational:** Daily delta hedging is the high-touch part. Missing one bad day in a 6-week trade kills the P&L.

### Honest probability for us
- VRP existence is well-established (T0 globally, T2 India).
- We physically cannot trade the unhedged version at ₹15-25k.
- A 1-lot defined-risk iron condor on BANKNIFTY weekly is *just* in reach but commission + bid-ask on far-OTM legs eats most of the edge at 1-lot scale.
- **P(net Sharpe > 0.5 OOS at our capital tier) ≈ 0.10.**
- **P(net Sharpe > 0.5 OOS at ₹3L+ capital tier) ≈ 0.40.** This is the primitive most worth *waiting for*, not the one to trade now.

---

## Ranked recommendation

| Rank | Primitive | Why this rank | P(works for us, 6mo) |
|---|---|---|---|
| 1 | **FII/DII flow as regime feature** (not standalone) | Fits capital. Free data. Low implementation cost. Mostly already priced-in standalone but possibly useful as a *conditioning* tag for another strategy. Worth a CPCV pass as a binary feature alongside the existing regime/lead-lag features. | 0.12 standalone / 0.20 as feature |
| 2 | **VRP harvesting — shelved, prepared** | The most academically robust edge of the four. Build the analytics now (delta engine, margin estimator, tail-loss sizer), do not deploy until capital ≥ ₹2L. This was already recommended as Option β in D3/D1/D5 postmortem. | 0.10 now / 0.40 at ₹3L+ |
| 3 | **Cointegration pairs (ETF-only variant)** | Real edge has decayed globally; Indian "evidence" is in-sample. The only capital-feasible version (ETF pairs intraday) is the wrong timescale. Worth ~1 honest backtest pass, no more. | 0.10 |
| 4 | **Index-rebalance front-running** | T0 evidence (Greenwood-Sammon 2023) says the edge is gone in the most liquid market on earth; Indian T1 evidence says it never persisted. Lowest expected value of the four. | 0.08 |

### What the harness will probably do
All four, if honestly run through CPCV + PBO + DSR with N_trials counted from day 1, are more likely than not to produce **zero survivors**. That is the base rate after 383 prior tests. The point of testing them is *not* to find alpha; it's to add four more "honest no" data points and to surface FII/DII as a possible regime feature for combination with existing setups.

### Honest probability summary
- **P(any of the four standalone passes G0 OOS) ≈ 0.20** (taking the union and accounting for correlation).
- **P(VRP becomes deployable in the next 6 months) ≈ 0.05** (gated on capital, not research).
- **P(FII/DII as conditioning feature meaningfully improves an existing setup) ≈ 0.20.**
- **Most likely outcome: zero new tradeable strategies; one new feature (FII/DII z-score) added to the regime classifier; VRP analytics built and shelved.** Net effect: research engine gains breadth, P&L unchanged.

### Decision rule
- Spend ≤ 8 hours on FII/DII feature engineering + CPCV pass. If it doesn't improve an existing setup at PBO ≤ 0.5, kill it.
- Spend ≤ 6 hours on VRP analytics (per D3/D1/D5 Option β). Shelf the code.
- Spend ≤ 2 hours each on pairs and rebalance to confirm-or-falsify; both are very likely "no" given prior literature.
- **Do not deploy any of the four at G2 capital. They are research, not P&L.**

---

## Sources

- Gatev, Goetzmann, Rouwenhorst — "Pairs Trading: Performance of a Relative-Value Arbitrage Rule" — NBER w7032 / RFS 2006 (T0)
- Do & Faff — "Does Simple Pairs Trading Still Work?" — FAJ 2010; *J Financial Research* 2012 (T1)
- Zhu — "Examining Pairs Trading Profitability" — Yale WP April 2024 (T2)
- Avellaneda & Lee — "Statistical Arbitrage in the US Equities Market" — *Quantitative Finance* 2010, 10:761-782 (T0)
- Sarkar, Sen et al. — arXiv 2211.07080 "Designing Efficient Pair-Trading … Indian Stock Market" (T2)
- Stochastic-Spread Pairs in Indian Commodities — arXiv 1907.08397 (T2)
- Petajisto — "The Index Premium and its Hidden Cost for Index Funds" — *J Empirical Finance* 2011 (T0)
- Greenwood — "Short- and Long-Term Demand Curves for Stocks" — *JFE* 2005 (T0)
- **Greenwood & Sammon — "The Disappearing Index Effect" — NBER w30748 / HBS WP 23-025 (2023) (T0) — the killer paper**
- Selvam, Indhumathi, Lydia — "Impact on Stock Price by Inclusion/Exclusion from CNX Nifty Index" — *Asia-Pacific JMR* 2012 (T1)
- Jain, Nair, Jain — "Impact of FII Flows on Indian Capital Markets" — SSRN 2707461 (2015) (T2)
- Shah — "Flows of FIIs and Indian Stock Market" — SSRN 3353659 (2013) (T2)
- "Trading Behaviour of Foreign Institutional Investors" — PMC9145119 (T1)
- Bondarenko — "Why are Put Options So Expensive?" — *RFS* 2014 (T0)
- Ilmanen — *Expected Returns* — Wiley 2011 (T1, book)
- "Does VRP from NIFTY options drive excess returns" — *Economic Sciences* 2024 (T2)
- CCIL WP ER/016 — "Exploring VRP in USDINR Currency Options" (T2)
- Internal: `D3_D1_D5_postmortem.md` (Option β), `wont_work_vs_might_work.md` (capital floor + N_trials discipline)
