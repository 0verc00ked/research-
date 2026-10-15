# Phase 10 — Novel Primitives Review: Transfer Entropy, TDA, Hawkes, Optimal Stopping

**Date:** 2026-05-21
**Author:** Claude Opus 4.7 (research agent)
**Audience:** Nikhil, post D3+D1+D5 zero-survivor finding
**Question:** After correlation lead-lag and conjunctive setup discovery both produced zero surviving strategies, are any of these four less-conventional mathematical primitives worth implementing?

**TL;DR — honest one-line on each:**
1. **Transfer Entropy** — strictly more general than what we already tried; same family of failure modes; **NOT worth implementing.**
2. **Persistent Homology / TDA** — has T2 published evidence for *crash detection* (a regime label, not a strategy); zero T3+ evidence of post-fee OOS strategy edge; **NOT worth as a strategy primitive, MAYBE 6h as a regime feature.**
3. **Hawkes Processes** — real published edge but **only at intraday / LOB tick resolution** which our latency budget cannot trade; **NOT worth implementing for our daily-bar harness.**
4. **Optimal Stopping (OU pairs-trading exit, SPRT)** — the **one genuinely under-explored primitive for us**; mathematically clean; complements (does not replace) the allocator; **worth a 10-14h build IF and only if a mean-reverting candidate survives the harness first.**

**Ranked recommendation at end of document.**

---

## 0. Frame: what "worth implementing" means here

After 383 setups tested and 0 survivors (`postmortem`), the prior on "novel math finds edge where old math didn't" is low. The base rate for retail-accessible novel-quant claims is dominated by:
- Methods that work in-sample, fail OOS (the same failure we already saw on `regime_calm`)
- Methods that work at frequencies retail cannot trade (HFT/LOB tick data)
- Methods that work on capital scales retail cannot deploy (>₹2L SPAN, institutional execution venues)
- Methods that work but the edge is the *data*, not the math (alt-data shops)

A primitive earns implementation budget only if:
(a) It's a primitive we **haven't already implicitly subsumed** (correlation lead-lag already covers linear-Gaussian Granger and a chunk of TE),
(b) Published OOS evidence exists at a frequency and capital scale we can actually trade,
(c) It either *generates* candidate strategies or *improves the harness/allocator* — not just adds a new feature column to D5's overfit surface.

---

## 1. Transfer Entropy (Schreiber 2000)

### 1.1 What it is
Non-parametric, non-linear measure of information flow X→Y: `TE(X→Y) = H(Y_t | Y_past) - H(Y_t | Y_past, X_past)`. Equals Granger causality exactly when variables are jointly Gaussian (Barnett, Barrett, Seth 2009 — T3). Beyond Gaussian, it captures non-linear coupling Granger cannot.

### 1.2 Libraries
- **IDTxl** (Wollstadt, Lizier — JOSS 2019): multivariate TE with conditional/redundancy correction, GPU/CPU parallel, Kraskov KSG estimator. Active maintenance, used in neuroscience primarily. **T3.**
- **PyIF** (Ikegwu et al., IEEE 2020): bivariate-only, KD-tree + GPU, ~1000× faster than naïve. Less feature-rich than IDTxl but faster for bivariate sweeps. **T3.**
- **`copent`, `transferentropy`** (R/Python ports): minor, T1.

### 1.3 Published financial results — honest read

| Paper | Finding | Trust | OOS-after-fees? |
|---|---|---|---|
| Marschinski & Kantz 2002 (`physics/0509014`) — DJIA vs DAX | Detects info flow; **no trading strategy, no P&L** | T3 (peer-reviewed methodology) | **No** |
| Korean equity TE networks (`2603.20271`, 2025) | "Cross-investor information is **redundant, not synergistic**; mutual information between TE signals and returns is **zero at daily horizon**" | T3 | **Negative — author concedes no daily edge** |
| Wang et al., *IJFE* 2025 — TE-determined HAR-RV model switching | Improves volatility prediction RMSE; **does NOT report a tradable directional strategy** | T2 | Volatility forecast, not returns |
| AEDL framework with TE + meta-learning (MDPI 2025) | Sharpe **0.48** OOS, 25y on 16 assets | T2 (peer-reviewed but young) | Sharpe 0.48 is below our harness DSR ≥ 0.95 bar; almost certainly below post-fee bar for retail |

### 1.4 Why TE doesn't escape what we already learned

- The Korean 2025 paper is the most rigorous recent attempt and its **headline negative finding** is exactly the result we already have: at daily horizon there is no extractable information once you condition on what's already in the price history.
- The "TE > Granger" advantage is non-linearity. But our D1 lead-lag scanner found 424 FDR-significant linear relations and **none generated a surviving strategy after OOS**. The bottleneck was not "linearity assumption was wrong"; it was "the relations don't persist and/or don't pay after costs."
- TE adds a multiplier on the multiple-comparisons surface (D5 already had 377 trials → 0 survivors). More features × more bandwidth choices × more lag choices = bigger overfit surface, same harness, predictably 0 OOS survivors.

### 1.5 Scorecard

| Dimension | Value |
|---|---|
| Trust score on the published edge | **T2 at best** (no T3+ evidence of post-fee retail-tradable TE strategy) |
| OOS performance after fees | Best reported: Sharpe ~0.48 gross on long history; retail-net would be ~0.1-0.3, **below our DSR bar** |
| Implementation effort in our codebase | 12-20h (IDTxl install + Kraskov tuning + integrate as D1 alternative + re-run D5 with TE features) |
| Compatibility with harness/allocator | Drops in as a new lead-lag scanner; allocator is unchanged |
| Capital sensitivity | None — same daily-bar problem as D1 |
| **Verdict** | **DO NOT implement.** TE is a non-linear generalization of what we already ran, and the most rigorous recent paper says daily TE→return MI is **zero**. |

---

## 2. Persistent Homology / Topological Data Analysis (Carlsson 2009)

### 2.1 What it is
Embed a sliding window of multivariate returns into ℝ^d (time-delay embedding), build a Vietoris-Rips filtration on the point cloud, compute persistence diagrams. The L^p norm of the persistence landscape (Bubenik 2015) is a real-valued time series that **spikes near regime changes / crashes** before they fully manifest.

### 2.2 Libraries
- **Ripser / ripser.py** — fast Vietoris-Rips. **T3.**
- **GUDHI** — INRIA, mature, broad. **T3.**
- **giotto-tda** — sklearn-style API, includes financial examples (crash detection on DJIA, S&P, NASDAQ, Russell 2000). **T3.**

### 2.3 Published financial results — honest read

| Paper | Finding | Trust | OOS-after-fees? |
|---|---|---|---|
| **Gidea & Katz 2018**, *Physica A* — landscapes of crashes | L^p norm of persistence landscape rises **prior to** dot-com 2000 and GFC 2008 crashes on 4 US indices | T3 (peer-reviewed primary) | **No strategy, no P&L** — it's a crash *indicator*, not a return-generating model |
| Gidea 2017, networks (T3) | Similar finding on cross-correlation networks | T3 | No strategy |
| Change Point Detection in Financial Markets (MDPI 2025) | TDA flags 2011 EU debt, Brexit, COVID-2020, Russia-Ukraine | T2 | **Lagging/coincident in several cases**, not predictive; no strategy |
| FX persistent homology (arXiv 2510.19306, Oct 2025) | Clusters currencies; comparative study vs PCA | T2 | Clustering, not trading |
| giotto-tda blog on "detecting crashes" | Same Gidea methodology, post-hoc fits | T1 (blog) | **In-sample only** |

### 2.4 The honest read
- TDA's *real* contribution is **as a regime-change detector**, comparable in role to our existing HMM. It is **not** a strategy generator.
- The most-cited paper (Gidea & Katz 2018) shows the signal rises near crashes but offers **no out-of-sample trading rule** and no calibration of a usable threshold.
- The 2018 result has been "replicated" in spirit by multiple follow-ups but always as "we see the signal go up around event X." This is the classic post-selection visualization problem: you pick a known crash window, you compute the indicator, you point at the rise. There is **no published T3 paper where TDA generates a pre-registered trade and earns a Sharpe > 1 after fees on OOS.**
- We already have an HMM regime classifier (D3) that did its job. Adding TDA as a second regime detector probably adds noise, not signal, unless the two disagree in interesting ways — which is a research project of its own.

### 2.5 Scorecard

| Dimension | Value |
|---|---|
| Trust score on the published edge | **T3 for "crash indicator rises near crashes"** — but **T1 at best for "trade this and make money after fees"** |
| OOS performance after fees | **No published number.** Every claim is either in-sample or change-point detection, not return |
| Implementation effort | 6-10h (giotto-tda one-time install; rolling Takens embedding + L^p landscape on existing NIFTY data; emit as a `regime_tda` feature) |
| Compatibility | Drops in as a feature in D5; OR as a second regime label alongside HMM |
| Capital sensitivity | None |
| **Verdict** | **DO NOT implement as a strategy primitive.** **MAYBE 6h** as a regime feature alongside HMM — but only if you have time after Option α (package the engine). The honest expectation is it correlates ~0.7 with HMM regime label and adds no information. |

---

## 3. Hawkes Processes (Bacry, Mastromatteo, Muzy 2015)

### 3.1 What it is
Self-exciting point process: λ(t) = μ + ∫_{-∞}^t φ(t-s) dN(s). Past events raise the intensity of future events. Captures volatility clustering and order-arrival clustering without ARCH-family parametric assumptions.

### 3.2 Libraries
- **tick** (X-DataInitiative, JMLR 2017) — multivariate Hawkes, exponential / sum-of-exponentials / non-parametric kernels, MLE + EM. **T3.** Last meaningful release ~2021; some Python 3.12 friction reported but installable.
- **hawkeslib** — simpler, well-maintained, T2.
- **PyHawkes** (Linderman) — Bayesian variant, T2, slower.

### 3.3 Published financial results — honest read

| Paper | Finding | Trust | OOS-after-fees? Retail? |
|---|---|---|---|
| Bacry, Mastromatteo, Muzy 2015 (`1502.04592`) — survey | Hawkes captures price/trade dynamics at **microsecond–second** resolution; superior fit to ARCH at high frequency | T3 (review) | High-freq only; no retail OOS |
| Bacry et al. 2013 (`1301.1135`) — 4D Hawkes for mid-price/trades | Excellent in-sample fit on EUR/USD futures **tick-by-tick** | T3 | Tick-by-tick, no retail strategy |
| Deep Hawkes for HFT Market Making (Kumar 2021, `2109.15110`) | Improves market-making P&L vs baseline | T2 | **HFT market making — colocation, not retail** |
| Hawkes Volatility tick filter (Lee, *ASMB* 2024) | Volatility estimation at 0.1s resolution | T3 | Volatility model, not strategy |
| Energy market optimal execution Hawkes (`2504.10282`, 2025) | Improves execution cost | T2 | Institutional execution problem, not signal generation |

### 3.4 The honest read
- Hawkes is **legitimately useful and has T3 evidence of edge** — but **the edge is at LOB tick resolution where retail cannot compete** (latency, colocation, exchange membership fees, market-maker rebates).
- At daily-bar resolution the self-excitation kernel collapses to "volatility clusters and there's positive autocorrelation in |returns|", which is already captured by trivial GARCH and HMM features. We don't need Hawkes for that.
- Retail-tradable Hawkes use case would require: (a) sub-second tick data subscription (Kite WebSocket → Zerodha's depth is OK but not full LOB), (b) sub-100ms execution latency, (c) co-location-adjacent infra. None of these are in our budget (CONCRETE_PLAN §5).
- Even the recent "intraday" Hawkes papers (`2503.14814`) explicitly assume HFT venue access.

### 3.5 Scorecard

| Dimension | Value |
|---|---|
| Trust score on edge | **T3 — but only at sub-second / LOB resolution** |
| OOS performance after fees at our resolution | **No published positive evidence at daily bars retail-net**. Hawkes at daily bars ≈ GARCH+autocorr, redundant with what we have |
| Implementation effort | 8-12h to fit, but **not the bottleneck** — the bottleneck is the infrastructure required to *trade* what Hawkes models, which we don't have |
| Compatibility | tick installs; would need a new event-time data pipeline (currently we have OHLCV bars) |
| Capital sensitivity | **High** — meaningful Hawkes strategies are market-making, which needs ≥₹5L margin + venue infra |
| **Verdict** | **DO NOT implement.** Hawkes' edge lives at a frequency and venue we cannot trade. Implementing it is academic LARP for our setup. |

---

## 4. Optimal Stopping / SPRT for Trade Exit

### 4.1 What it is
Instead of fixed-time exit (e.g., "close after 5 days") or fixed-percent stop ("stop at −1%"), derive the **mathematically optimal stopping rule** for a given assumed return process.

Two flavors:
- **OU optimal stopping** (Leung & Li 2015, Song et al. 2013) — assume the spread / log-price residual follows Ornstein-Uhlenbeck, solve the free-boundary problem for entry/exit thresholds that maximize expected discounted P&L net of transaction costs. Closed-form-ish.
- **SPRT (Wald 1947)** — sequentially update likelihood ratio of "thesis still alive" vs "thesis dead"; exit when the ratio crosses pre-committed bounds A, B chosen to control Type-I/II error.

### 4.2 Libraries
- **Hudson & Thames `arbitragelab`** — OU optimal-stopping module, well-documented (note: parts went paid in 2023; the OU code is in the free `arbitragelab` pre-fork). **T2.**
- **scipy.optimize** + custom ~150 LoC for OU free-boundary (Leung & Li 2015 algorithm is short).
- **`sequential`** R package (Kulldorff) — SPRT, T2.
- SPRT is so simple (~30 LoC) that "library" is overkill.

### 4.3 Published results — honest read

| Paper | Finding | Trust | OOS-after-fees? Retail? |
|---|---|---|---|
| Song, Yin, Zhang 2013, *Automatica* — optimal pairs-trading rule | Three-threshold rule maximizes expected return under OU; **proven optimal** | T3 | Theoretical; backtests on simulated and real US pairs show improvement over naive z-score thresholds |
| Leung & Li 2015 (`1411.5062`) — OU with TC and stop-loss | Closed-form characterization of entry/exit; **demonstrates 15-40% P&L improvement vs fixed-z exit** on backtested pairs after costs | T3 | Yes, modest but positive; pairs trading specifically |
| Bertsimas & Lo 1998 — optimal execution | Different problem (execution), but same family; T3 | T3 | Institutional |
| Hudson & Thames blog on OU optimal stopping | Walks through implementation on real pairs | T2 | Demonstrates improvement |
| Wald SPRT — financial application (sparse) | SPRT widely used in A/B testing, **rare in trading literature**; this is **genuinely under-explored** | — | — |

### 4.4 The honest read — **this is the interesting one**

- Optimal stopping is **not a strategy generator** — it does not give you a new edge. It is an **exit-rule improver** that takes an existing thesis ("the spread will revert", "the disclosure-driven move will decay") and replaces ad-hoc time/percent stops with a mathematically optimal rule under stated assumptions.
- **The OU-pairs-trading literature has T3 evidence that this improves P&L net of fees** — modestly (15-40% improvement over fixed-z), not heroically, and only when the underlying OU assumption is empirically validated (which is itself a testable hypothesis: AR(1) coefficient < 1, half-life within tradable horizon, residual stationarity).
- **SPRT as an exit rule is genuinely under-explored** in the published literature. The intuition: while a trade is open, you have a running likelihood of "this trade has the edge I thought" vs "it doesn't." SPRT gives you the **minimum-expected-sample-size** rule to make the kill/hold decision at any controllable error rate. This is a real mathematical artifact, simple to implement, and has no equivalent in our current codebase.
- Critically: **optimal stopping does not require finding a new edge first.** It requires only that *some* edge exists somewhere (which we currently don't have). So implementing it speculatively before we have a survivor is putting the cart before the horse. **It earns its keep only if a candidate strategy passes the harness first.**

### 4.5 Scorecard

| Dimension | Value |
|---|---|
| Trust score on edge | **T3 on OU optimal stopping for pairs trading** (Song-Yin-Zhang 2013, Leung-Li 2015 are peer-reviewed primary). **T2 on SPRT as trade exit** (theoretically clean, financially under-applied) |
| OOS performance | OU stopping: **+15-40% over fixed-z exit net of TC** in published pairs backtests. SPRT: no published financial OOS, but the math guarantees minimum expected sample size at the chosen error rate |
| Implementation effort | OU free-boundary exit module: **8h** (Leung-Li algorithm, ~150 LoC, unit tests). SPRT exit module: **4h** (30 LoC + unit tests + harness integration). Total: **~12h** |
| Compatibility | Slots into `portfolio/` as a per-strategy exit-policy module; allocator unchanged; harness unchanged (it evaluates whatever exit rule the strategy uses) |
| Capital sensitivity | **None** — works at any capital scale where the underlying strategy works |
| **Verdict** | **Worth ~12h IF AND ONLY IF a candidate strategy (likely a future mean-reverting one) passes the harness. Build it speculatively only at low priority — it's a multiplier on edge that doesn't yet exist.** |

---

## 5. Cross-cutting honest observations

### 5.1 What the literature pattern actually shows
Across all four primitives, the same pattern recurs in the credible papers:
- The math is real and the in-sample fit is real.
- The OOS evidence at our (daily-bar, retail, after-fees) operating point is **either absent or modest** (Sharpe ≤ 0.5 gross).
- The strongest OOS results live in venues we cannot trade (LOB HFT, institutional execution, pairs spreads on US assets with US fee structures).
- The same paper-class that produced our D5 0/377 result would produce a similar 0-survivor outcome if we re-ran D5 with TE features instead of correlation features. We would be re-running the same harness against a richer feature space, on the same daily-bar NIFTY data, with the same multiple-testing surface. **The harness would correctly kill the new survivors too.**

### 5.2 What's genuinely new for us
Only optimal stopping is a *categorically* new primitive — it's not a strategy generator, it's an **execution / exit-rule** improvement. The other three are all in the family of "find better signal in price history," which we've now run hard on and the harness says: no.

### 5.3 What this analysis does NOT tell you
- We did not test these on real data. This is a *literature survey* with trust-scored claims, not a T4 reproduction. To upgrade any T2/T3 claim above to T4, you'd need ~1-2 days of code per primitive.
- It's possible (low probability, but not zero) that one of these on Indian-specific data produces a result that's absent from the global literature because nobody has bothered. The Indian-mid-cap-equity TE problem, specifically, doesn't appear in any T3 paper I found. **This is the only honest "X has not been tried on our specific data" loophole**, and it is thin.

---

## 6. Ranked recommendation

### Build order, with concrete costs:

#### **Rank 1 — Optimal Stopping (OU + SPRT exit module), ~12h, conditional**
- **When to build:** ONLY after at least one strategy passes the harness AND that strategy has a mean-reverting or thesis-decay structure (pairs, disclosure-driven mid-cap move, VIX-regime trade)
- **Why:** real T3 OOS evidence of incremental P&L improvement post-fees; clean mathematical artifact; no overfit-surface expansion; no new venue/data requirement
- **What you get:** `portfolio/exit_policies/ou_optimal_stop.py` (~150 LoC) + `portfolio/exit_policies/sprt_exit.py` (~30 LoC) + tests + harness adapter
- **Failure mode:** if you never get a survivor, you never build it. That's fine.

#### **Rank 2 — TDA as a regime feature (NOT as a strategy), ~6h, optional**
- **When to build:** only if you go with Option α (package the engine) and want one more regime label to compare against HMM
- **Why:** T3 evidence that the indicator rises near crashes; cheap to add via giotto-tda; modest information-additive value
- **What you get:** `regime/tda_landscape.py` — rolling Takens embedding + L^1 persistence landscape on existing NIFTY data; emits a continuous-valued "topological stress" feature
- **Honest expected outcome:** ~0.6-0.8 correlation with HMM regime probability; possibly catches one regime change HMM misses or vice versa. Not a strategy. Don't expect a survivor from it.

#### **Rank 3 — Transfer Entropy: DO NOT BUILD**
- The most rigorous recent paper (Korean equities 2025) finds **MI(TE-signal, daily return) = 0**. Believing TE on NIFTY will be different is wishful.
- If you still want it as a research curiosity: ~16h with IDTxl. **Do not budget this against the 12-week plan.**

#### **Rank 4 — Hawkes Processes: DO NOT BUILD**
- Real edge, wrong venue. Retail cannot trade what Hawkes models well.
- Reconsider only if you ever scale to ≥₹5L SPAN + colocation. Not in the next 12 weeks.

---

## 7. Final honest synthesis (one paragraph)

Three of these four primitives (TE, TDA, Hawkes) are interesting math but each has a structural reason it won't escape the negative result we already have: TE is a generalization of what we already ran on the same data with the same harness; TDA is a regime indicator not a strategy and we already have one; Hawkes lives at a frequency we cannot trade. The fourth (optimal stopping) is the only genuinely under-utilized primitive for our codebase, but it is **multiplicative on edge** — it improves the exit rule of an *existing* good strategy, it does not produce one. So the most honest recommendation, combined with the postmortem's Option α, is: **package the engine, do not implement TE/TDA/Hawkes, and keep an optimal-stopping module on the "build when first strategy passes" shelf** — perhaps as a ~half-day project bundled into the eventual Option β (vol-RV) work since OU stopping has a particularly natural fit with vol-spread or pairs-style strategies.

The expected value of implementing any of these four *speculatively, before having a strategy that passes the harness*, is approximately zero. The expected value of having designed the optimal-stopping module on paper so it can be built in a day when needed is genuinely positive. This document is that paper design.

---

## Sources cited (trust-scored)

- Schreiber 2000, *Measuring Information Transfer*, PRL — T3 (founding paper)
- Barnett, Barrett, Seth 2009, `0910.4514` — TE = GC for Gaussian — T3
- Marschinski & Kantz 2002, `physics/0509014` — T3
- Korean equity TE networks, `arxiv:2603.20271` (2025) — T3 — **negative finding at daily horizon**
- Wang et al. 2025, IJFE — TE model switching for HAR-RV — T2
- AEDL framework MDPI 2025, Sharpe 0.48 — T2
- Wollstadt et al., *IDTxl* JOSS 2019 — T3 (library)
- Ikegwu et al., *PyIF* IEEE 2020 — T3 (library)
- Gidea & Katz 2018, *Physica A* 491:820 — T3 — **crash indicator, no strategy**
- giotto-tda OpenReview 2021 — T3 (library)
- Change Point Detection MDPI 2025 — T2
- FX TDA, `arxiv:2510.19306` Oct 2025 — T2
- Bacry, Mastromatteo, Muzy 2015, `1502.04592` — T3 (review)
- Bacry et al. 2013, `1301.1135` — T3 (tick-level)
- Bacry et al., *tick* JMLR 2017 — T3 (library)
- Deep Hawkes HFT, `2109.15110` — T2
- Lee 2024, *ASMB*, Hawkes volatility filter — T3
- Song, Yin, Zhang 2013, *Automatica* — optimal pairs rule — T3
- Leung & Li 2015, `1411.5062` — OU optimal stopping with TC — T3
- Wald 1947, *Sequential Analysis* — T3 (foundational)
- Hudson & Thames OU optimal stopping write-up — T2

**Not cited / deliberately excluded:** TradingView indicators, Medium posts that claim P&L without trade logs, "AI trading" repos, finfluencer content. All auto-cap at T0 per `trust_rubric.md`.
