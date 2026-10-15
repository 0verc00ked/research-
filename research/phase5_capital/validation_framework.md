# Honest Validation Framework — From Backtest to Live

**Premise (carried from `../README.md`):** Most agentic-trading repos lose money after fees. Most backtests are overfit. The default stance is disbelief. This document defines the protocol that any candidate strategy must clear before risking real capital.

**Trust scoring** per `../trust_rubric.md`.

---

## 1. Walk-Forward Analysis (WFA) — protocol

Walk-forward is the **only** acceptable backtest methodology for this project. Static train/test split with one holdout is insufficient: a strategy that works once may not have been re-optimized as the regime changed.

**Anchored walk-forward (recommended):**
1. Choose an **in-sample (IS)** window length L_is and an **out-of-sample (OOS)** window length L_oos. Typical ratio 4:1 (e.g. 12 months IS, 3 months OOS).
2. Train / optimize strategy parameters on `[t₀, t₀ + L_is)`.
3. Apply frozen parameters to `[t₀ + L_is, t₀ + L_is + L_oos)`. Record OOS performance.
4. Step forward by L_oos (rolling) or extend IS window (anchored).
5. Concatenate all OOS segments — **this** is the honest equity curve.
6. Report:
   - OOS Sharpe with confidence interval
   - OOS max drawdown
   - **Degradation ratio** = IS Sharpe / OOS Sharpe (red flag if >2)
   - Parameter stability across windows (if optimal params jump wildly each window → overfit signal)

(T3: Pardo, *The Evaluation and Optimization of Trading Strategies* (Wiley); López de Prado, *Advances in Financial Machine Learning*, Ch. 7 — Cross-validation in finance.)

---

## 2. Time-series splits — NO random shuffling

Standard k-fold CV is **forbidden**. Random shuffling leaks future info into the training set (lookahead). Use:

- **Purged k-fold CV with embargo** (López de Prado, AFML ch. 7) — T3.
  - Purge: remove training samples whose labels overlap the validation set's time range.
  - Embargo: drop a buffer of `h` bars after each validation segment from the next training set to prevent serial-correlation leakage.
- **Combinatorial Purged CV (CPCV)** for hyperparameter tuning — multiple paths, gives a distribution of Sharpe rather than a point estimate. T3 (López de Prado).
- If using train/val/test: **chronological** only. Train: oldest 60%. Val: next 20% (hyperparam selection). Test: most recent 20%, looked at exactly **once** at the very end.

---

## 3. Out-of-sample holdout — minimum length

Minimum recommendations:
- **Daily-bar strategies:** ≥ 2 years of OOS, **including at least one bear market** (else regime untested).
- **Intraday strategies (≥5-min bars):** ≥ 6 months OOS, ≥ 200 trading days, ≥ 200 trades.
- **Sub-minute strategies:** out of scope for this project (LLM-agent latency floor).

Why: Bailey & López de Prado's *Minimum Backtest Length* formula (T3: SSRN 2308659) — for k trial strategies tested, the expected maximum Sharpe under the null (no edge) grows as `~√(2 log k)`. Even 10 strategies tested → expected null Sharpe ≈ 2.1 over a 1-year sample. You need enough OOS length that random outperformance becomes implausible.

---

## 4. Slippage & fee modeling — use worst-plausible

**Default modeling stance:** assume execution is worse than the historical median, not better.

**Slippage estimates (conservative, India retail):**
- NIFTY/BANKNIFTY index options (ATM, liquid): **0.5–1 tick spread** + **1 tick adverse slippage on market orders** = ~₹0.10–₹0.50 per unit.
- Index options (OTM, far-week): wider spreads, model 2–3 ticks slippage.
- Index futures: ~0.5 tick.
- Equity cash (liquid Nifty-50 stocks): 1 tick (₹0.05) + impact.
- Equity cash (small-cap, midcap): 0.1–0.5% impact — backtest must include this.
- MCX commodities: variable, 0.05–0.2% on minis.
- Crypto INR pairs: 0.2–0.5% spread + 1% TDS (this is fixed regulatory).

**Fee modeling:** use **actual Zerodha/Upstox charges page values** (T3) — not zero, not estimates. Include:
- Brokerage (₹20 or 0.03% F&O)
- STT (sell side primarily; post-Apr-2026 budget rates per the brokerage charges page)
- Exchange transaction charges
- SEBI turnover fees (₹10/crore)
- Stamp duty (buy side, 0.003%–0.015% varies)
- DP charges on equity delivery sell (~₹15.93 per scrip, fixed — kills small tickets)
- 18% GST on brokerage/txn/SEBI components

**Rule of thumb floor:** if your backtest shows positive returns after subtracting **1.5× the official fee schedule + 1 tick slippage per fill**, only then is it interesting.

---

## 5. Survivorship bias

Failure mode: backtest on today's Nifty-50 constituents and extrapolate back 10 years → you've ignored the companies that got delisted, merged, or fell out of the index.

**Mitigations:**
- Use **point-in-time** index constituents (NSE provides historical constituent lists; T3) — match each backtest date to that date's actual index members.
- Include **delisted stocks** in equity universe — sources: NSE delisting circulars, Norgate Data (paid), Eodhd (paid).
- For F&O: don't assume contracts that no longer exist were always equally liquid (e.g. Crude Oil Mini was discontinued — backtests using it post-2022 are invalid).
- For crypto: include coins that delisted from CoinDCX/Binance (many memecoin booms+busts disappear from "current" datasets).

If you cannot obtain point-in-time universe, **constrain backtest to the most liquid top-5 instruments** (NIFTY, BANKNIFTY, SENSEX, FINNIFTY, Gold) — these have continuous existence and are immune to survivorship.

---

## 6. Lookahead bias — explicit checks

Common leaks:
1. **Future-fill prices** — using close price of bar `t` for a signal computed at close of bar `t`. Fix: simulate fill at open of bar `t+1` or VWAP of `t+1`.
2. **Future indicator values** — talib indicators that internally use future windows (uncommon but possible in custom code).
3. **Earnings / corporate-action adjusted prices** retroactively applied — using a today-adjusted price series instead of the unadjusted price-as-known-then.
4. **Survivorship** (see above) — also a form of lookahead.
5. **Crypto-specific:** funding rate forward-fill, exchange-listing date assumptions.

**Mandatory check:** shift all features by one bar. If Sharpe collapses, you had lookahead.

**Mandatory check #2:** Replace your signal with `signal.shift(1)`. P&L should drop only modestly (one bar of opportunity lost). If P&L collapses to zero, your strategy was forecasting `t` using info from `t` — leak.

---

## 7. Regime testing — mandatory historical shocks

Backtest must include **all** of the following Indian-market regimes. If any is missing, the strategy is undertested:

| Regime | Period | Why |
|---|---|---|
| COVID crash | Feb 24 – Apr 7, 2020 | Volatility shock, circuit breakers, options vol explosion |
| COVID recovery | Apr 2020 – Dec 2020 | Trending bull, low realized vol mid-period |
| 2022 macro tightening | Jan – Jun 2022 | RBI rate hikes, FII outflow |
| Adani crisis | Jan 24 – Feb 3, 2023 | Sector-specific shock, Hindenburg report |
| 2023–24 bull | Apr 2023 – Sep 2024 | Sustained uptrend (vulnerable to bull-bias overfitting) |
| 2024 election | Jun 3–4, 2024 | Gap-up/gap-down regime ("BJP majority shortfall" Monday) |
| Oct 2024 SEBI options reform | post Oct 1, 2024 | Lot-size hike, weekly-expiry rationalization — changes microstructure |
| 2025 correction | Oct 2024 – Mar 2025 | Sustained drawdown phase |

For each regime, report Sharpe, max DD, hit rate **separately**. A strategy that's positive overall but bleeds 50% in any single regime is unsafe for live.

---

## 8. Statistical significance bar

**Minimum trades:**
- For Sharpe estimation with reasonable CI: ≥ **100 trades** absolute floor; ≥ **300 trades** for confidence.
- For trade-edge t-statistic ≥ 2.0 at 5% significance: depends on edge size. Rule of thumb: if mean edge per trade is `μ` and std `σ`, need `n ≥ (2σ/μ)²`. For typical retail edges (μ/σ ≈ 0.1), n ≈ 400.

**Sharpe ratio CI:** annualized Sharpe has standard error roughly `√((1 + 0.5·SR²)/T)` for T return observations (T3: Lo 2002, *The Statistics of Sharpe Ratios*).
- Sharpe = 1.5 on 250 daily obs → SE ≈ 0.07; 95% CI = [1.36, 1.64]. OK.
- Sharpe = 1.5 on 60 daily obs → SE ≈ 0.15; 95% CI = [1.20, 1.80]. Marginal.

**Deflated Sharpe Ratio (DSR)** — mandatory if more than ~3 strategy variants were tested:
- Formula in Bailey & López de Prado (2014), *The Deflated Sharpe Ratio* (Journal of Portfolio Management 40(5)) — T3.
- DSR adjusts observed SR for (i) number of trials, (ii) skew/kurtosis of returns, (iii) sample length.
- **Decision rule:** DSR < 0.95 (i.e. <95% probability the SR is non-zero after correction) → reject the strategy. Do not deploy.
- Implementation references: `quantstrat/R/deflated.Sharpe.R` (T3 — open-source reference impl); stefan-jansen ML4T notebook (T3 — pedagogical impl).

---

## 9. Paper → tiny live → small live → scale — gated ramp

Each gate has objective go/no-go criteria. **Do not skip gates. Do not cherry-pick the gate's evaluation window.**

### Gate 0 — Backtest (offline)
- ≥ 2 years OOS via walk-forward
- ≥ 300 trades
- DSR ≥ 0.95 after multiple-testing correction
- Positive in all required regimes (Section 7)
- Slippage modeled at 1.5× official spread + 1 tick
- Survivorship and lookahead checks passed
- **Pass → Gate 1.**

### Gate 1 — Paper trading (live data, simulated fills)
- Run on **Alpaca Paper** (best fidelity free) or **IBKR Paper** for ≥ **60 trading days** continuous.
- ≥ 30 simulated trades.
- OOS-paper Sharpe within ±30% of backtest OOS Sharpe.
- No software incidents (uncaught exceptions, API timeouts handled, reconnection works).
- **Pass → Gate 2.**

### Gate 2 — Tiny live ("plumbing live")
- **Capital: ≤ ₹5,000.** Smallest legal ticket per trade (SENSEX weekly OTM, MCX gold petal, one-share equity, or one $1 fractional US stock).
- Duration: ≥ **30 trading days**.
- Goal here is NOT to make money — fees will dominate. Goal is to verify:
  - Real fills happen at real prices, slippage within model
  - Real broker rejects/exceptions are handled
  - Real corporate-action / expiry / settlement events are handled
  - Real tax/STT accounting matches expectation
- **Go criterion:** zero unhandled exceptions, slippage within 1.5× modeled, fills within 1 tick of expected ≥ 95% of the time.
- **Pass → Gate 3.**

### Gate 3 — Small live ("edge-detect live")
- **Capital: ₹15,000 – ₹25,000** (the soft minimum from `min_capital.md`).
- Duration: ≥ **3 months / ≥ 50 trades**.
- **Go criterion:** live Sharpe within ±40% of paper Sharpe; max DD ≤ 1.3× backtest max DD; no drift in trade-edge mean.
- If live edge is clearly negative for 2 consecutive months → **kill the strategy**, return to backtest.
- **Pass → Gate 4.**

### Gate 4 — Scale
- Increase capital in **2× steps**, not 10×. Re-evaluate after each step for ≥ 30 trades.
- Watch for **capacity decay**: as size grows, slippage grows. If live Sharpe drops monotonically with size → you've hit capacity, stop scaling.
- Cap personal-deployment ceiling at ₹5–10 L regardless of edge — beyond that, regulatory scrutiny (SEBI Research Analyst / PMS thresholds) and tax complexity make it a different project.

---

## 10. Kill-switch criteria

The agent must self-halt (no human override required) if **any** of:

1. **Drawdown limits:**
   - Daily DD > 3% of capital → flatten + halt 24h.
   - Weekly DD > 7% → halt + manual review.
   - All-time DD > 15% → kill strategy entirely, return to backtest.

2. **Consecutive losses:**
   - ≥ 7 consecutive losing trades → halt + review (rule-of-thumb: even a 60%-hit strategy has <1% probability of 7-in-a-row by chance).

3. **Behavioral anomalies (agentic-specific):**
   - LLM output unparseable (JSON malformed) more than 2× in 10 calls → halt.
   - LLM produces a trade-size value outside `[min_lot, max_position]` bounds → halt (don't clip silently — halt and review).
   - LLM rationale contains hallucinated tickers or dates → halt.
   - Two LLM calls within 5 min produce contradictory directional signals on same instrument → halt.

4. **Market-state anomalies:**
   - Spread > 3× normal for entry instrument → skip the trade, log it.
   - Realized vol > 2× rolling 30d → reduce position size to 50%; if >3×, halt new entries.
   - Exchange circuit breaker triggered → halt.

5. **Infrastructure anomalies:**
   - Broker API latency > 2s for 3 consecutive requests → halt new entries until normal.
   - Websocket disconnect > 60s during market hours → flatten positions; halt for the session.
   - Clock skew > 1s → halt (timestamp-based rules become unreliable).

6. **PnL plausibility:**
   - Reported PnL for a closed trade differs from independently computed PnL (entry/exit × qty − fees) by > 0.5% → halt, force reconciliation.

**All kill-switch trips must log to a tamper-evident audit log** (append-only file or signed log) so post-mortems can reconstruct what the agent saw and decided.

---

## 11. What this framework explicitly REJECTS

- "I made X% in 6 months on paper" without walk-forward → T0, rejected.
- Single-regime backtests (e.g. only 2023–24 bull) → rejected.
- Backtests with zero slippage/fee assumption → rejected.
- Strategies tuned on the validation set → rejected (test set looked at once, at the end).
- "AI strategy" repos with no losing months → near-certainly cherry-picked, rejected.
- Sharpe > 3 on retail timeframes → near-certainly overfit; demand DSR ≥ 0.95.
- Strategy authored by a person also selling signals / running a paid Discord → conflict of interest, T0 cap.

---

## Source citations

- Bailey & López de Prado, *The Deflated Sharpe Ratio* (2014), J. Portfolio Mgmt 40(5) — T3
- Bailey, Borwein, López de Prado, Zhu — *The Probability of Backtest Overfitting* — T3
- López de Prado, *Advances in Financial Machine Learning* (2018) — T3
- Pardo, *The Evaluation and Optimization of Trading Strategies* (Wiley, 2008) — T3
- Lo, *The Statistics of Sharpe Ratios* (FAJ, 2002) — T3
- SEBI Peak-Margin circular CIR/MRD/DP/45/2020 (T3) — for upfront-margin reality
- Zerodha charges page (T3) — for fee floors
