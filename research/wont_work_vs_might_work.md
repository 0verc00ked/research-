# What Will NOT Work vs What Has a Chance

**Date:** 2026-05-21
**Purpose:** A single page consolidating every failure mode and every plausible edge surfaced across Phases 1–7. Decision aid, not aspirational.

The base rate is brutal: SEBI 2024 study — **89% of retail F&O traders lose money**. López de Prado: **<5 of 100 backtested strategies deliver live edge**. Default expectation = failure. Read everything below against that floor.

---

## Part A — What will NOT work (do not waste time)

Each item carries the evidence + trust score. If you find yourself drifting toward one of these, this page is the reason to stop.

### A.1 Architectural dead ends

| # | Approach | Why it dies | Evidence |
|---|---|---|---|
| 1 | **LLM in the order path** (LLM directly says "buy NIFTY 25000 CE") | Fee-adjusted OOS Sharpe < 0; LLM trades on retrieved narratives, not edge | FinSABER (KDD-2026, T3), StockBench (T3) |
| 2 | **LLM generates the strategy code** (foundry / Alpha-GPT pattern) | Retrieval, not exploration; 40–60% memorization rate; 50–72% return decay after training cutoff | Profit Mirage (arXiv:2510.07920, T3), MemGuard-Alpha (T2), Phase 7 verdict |
| 3 | **Autonomous LLM iteration / fine-tuning in production** | Every change is a new trial; N_trials inflation kills DSR; drift becomes overfit not adaptation | LdP DSR methodology (T3) |
| 4 | **HFT, market making, sub-second** | LLM latency floor 0.5–2 s; Kite REST TTFB ~320 ms; structurally locked out | Phase 4 + V-1 measurements (T4) |
| 5 | **"Always-on" strategies that promise to work in all regimes** | Mathematically implies negative skew somewhere — usually catastrophic tail | classical quant lit |
| 6 | **Backtest-driven decisions without PBO/DSR/CPCV** | Default false-positive rate >>50% on retail-grade backtests | LdP 2014 (T3) |

### A.2 Market / venue dead ends for *this* user

| # | Venue | Why ruled out |
|---|---|---|
| 7 | **Offshore crypto exchanges** (Binance, Bybit ex-VPN) | FEMA + IT Act violation (T3) |
| 8 | **Polymarket / prediction markets** | PROGA 2025 + MeitY block (T3) |
| 9 | **Tokenized stocks** | No legal on-ramp from India (T3) |
| 10 | **Spot FX with offshore brokers** | FEMA (T3) |
| 11 | **US options via LRS / IBKR / NSE IX** | RBI bars derivatives under LRS; IBKR India closed for resident options; NSE IX equities-only (T3) |
| 12 | **High-turnover Indian crypto strategies** | 30% flat tax + 1% TDS + no loss offset = mathematical kill (T3) |
| 13 | **Sub-₹15k live capital** | Per-trade fees + STT + slippage drown any plausible edge — cannot statistically separate skill from luck (Phase 5, T3) |

### A.3 Methodological dead ends

| # | Mistake | Why it kills you |
|---|---|---|
| 14 | **Random train/test split on time-series** | Trivially leaks future into past |
| 15 | **Survivorship-biased data** (only currently-listed tickers / undelisted contracts) | Inflates Sharpe by 30–60% |
| 16 | **Optimistic fees & slippage in backtest** | Real fills are worse than mid; always use worst-plausible-case |
| 17 | **Forgetting how many strategies you tried** (N_trials inflation) | DSR critical value rises with N_trials; "I only have 5 backtests" → after 500 tweaks DSR threshold is much higher |
| 18 | **Cherry-picked time window** ("started just after the 2020 crash") | Any equity strategy looks great from a local bottom |
| 19 | **Strategy that doesn't include at least 1 bear + 1 calm + 1 shock** | Untested for the regime that will eventually arrive |
| 20 | **Backtest entirely inside LLM training cutoff** | Contamination: LLM "knows" what happened. Mandatory ≥1 post-2025-01 window |
| 21 | **Using LLM to grade its own outputs** | Self-confirming loop |
| 22 | **Trusting a backtest Sharpe without confidence interval** | Sharpe SE is large at low N; "Sharpe 1.4 over 80 trades" may have CI [0.3, 2.5] |
| 23 | **Strategies discovered by mass parameter sweep** without correction | The Bonferroni / Benjamini-Hochberg / PBO machinery exists *because* this is the #1 false-positive engine in quant |

### A.4 Operational dead ends

| # | Mistake | Why it kills you |
|---|---|---|
| 24 | **No kill-switch** | One model anomaly → blown account |
| 25 | **Skipping paper trading** | Plumbing bugs always exist; live discovery = live loss |
| 26 | **Increasing capital after a winning streak** without re-running gates | You're scaling noise |
| 27 | **Manual override of the strategy mid-trade** | Behavioral leak that backtest doesn't capture; if you do this once, the whole audit trail is poisoned |
| 28 | **Hosting outside India for retail algo** (post-2026-04-01) | SEBI framework violation |
| 29 | **No audit log** | Regulatory non-compliance + you can't diagnose what went wrong |

---

## Part B — What has a *chance* to work

"Chance" ≠ "will work." Even these, base rate is hostile. Each item lists what would have to be true.

### B.1 Architectural patterns with surviving evidence

| # | Pattern | What must be true | Trust |
|---|---|---|---|
| 1 | **LLM-as-analyst (regime/event tags only) + hand-written rules + hard kill-switch** | V-9 contamination probe at "regime_only" or cleaner; strategy clears G0 | T2 (FinMem partial + Phase 1b reasoning) |
| 2 | **Boring proven patterns where execution is the edge** (calendar effects, expiry-day mean reversion, dispersion, vol-skew) | You execute cleaner / cheaper than the median retail trader, not "find new alpha" | T2 (decades of literature; e.g. Bouchaud et al.) |
| 3 | **Slow horizon — days to weeks** | Strategy is profitable at >5-min bar resolution; fee budget doesn't cap edge | T3 (Phase 4 latency + fee math) |
| 4 | **Event-driven on macro-scheduled events** (RBI policy, earnings, expiry, budget) | Statistical regularities in volatility around these are well documented | T2 (Indian-market specific literature limited but exists) |
| 5 | **LLM as research analyst** (offline brainstorm → human implements → harness validates) | You honestly count it in N_trials; you don't let it self-grade | T2 (Phase 7 §7b permitted use) |

### B.2 Edges that *plausibly* exist for a solo Indian retail operator

| # | Plausible edge | Why it's plausible | What it requires |
|---|---|---|---|
| 6 | **Cost discipline + tax-efficient construction** | Most retail loses to fees not to direction; cost-aware sizing is a real edge | Mastery of the brokerage / STT / GST / stamp matrix |
| 7 | **Behavioral edge** (no revenge trading, no FOMO entries, no over-leverage) | Kill-switch + deterministic rules enforce this in code | Discipline + audit log review |
| 8 | **Time-of-day / day-of-week patterns on Indian indices** | Documented intraday seasonality (open volatility, last-hour drift, weekly expiry dynamics) | Walk-forward across years, not just curve-fit |
| 9 | **Volatility-regime classification** beating naive HV-percentile | India VIX + skew term-structure are informative; whether LLM adds info beyond classical regime models is an open question — must be ablated | Ablation test: LLM-tagged regime vs HMM/threshold regime on same strategy |
| 10 | **News-event filter** (avoid trading into a known-unknown like RBI policy day) | Pure risk-off filter; doesn't need positive alpha, just avoids one losing class | Macro calendar API + event-day blocklist |
| 11 | **Tail-risk-aware sizing** | Most blowups are from oversizing into a fat tail; Kelly fraction << 1 is a real edge | Realized-vol scaling + hard max position |

### B.3 What the *combination* must look like

A passing G0 strategy will probably have ALL of these properties:
- **Simple.** Three or fewer parameters that aren't curve-fit. If it has 20 knobs, it's overfit.
- **Defensible mechanism.** A one-paragraph explanation of *why* it should work that doesn't invoke "patterns" or "AI." If you can't write that paragraph for a friend, it's not a strategy.
- **Robust to the LLM going dark.** Drops to a sane fallback (e.g., "regime unknown → no trade") if the analyst returns `disabled`.
- **Profitable on classical regime classifier alone.** If the strategy needs the LLM to be profitable, the LLM is a confound, not a feature.
- **Has at least one out-of-cutoff OOS window.** 2025-01 or later, contamination-clean.
- **Loses money during one of the validation regimes.** A strategy that wins everywhere is overfit. Real edge has a regime it skips.

---

## Part C — The honest ordering for time spent

If you only have N hours, spend them in this order:

1. **Build `agent_trader/validation/`** (CPCV + PBO + DSR + trial log). Without this, nothing below means anything. — *highest leverage activity in the entire project*
2. **Collect clean Indian data** (qlib-format, point-in-time, survivorship-clean, including delisted contracts and expired options). Most strategy failure is bad data, not bad strategy.
3. **Pick ONE hypothesis from B.2** (recommend #8 or #4 — both have classical evidence, neither requires LLM to be profitable). Hand-write it. Run it through the harness. It will probably fail. That's data.
4. **Paper-trade the surviving strategy** for 60 days. Compare live paper Sharpe to backtest Sharpe. If they diverge by > 1σ, the backtest lied — back to step 3.
5. **Only then** wire the LLM analyst, and only if you can show ablation that it adds OOS information beyond a classical regime classifier.
6. **Only then** consider G2 live plumbing with ₹5k.

If steps 1–4 take 6 months and produce nothing tradeable, **that is a successful outcome.** You spent ₹20k on infra and learned the architecture instead of ₹2L on a bad strategy.

---

## Part D — One-paragraph self-check before any live trade

> *"This strategy passed PBO ≤ 0.5, DSR ≥ 0.95 at honestly-counted N_trials = ___, CPCV with N=8 / k=2 / purge / embargo, and was profitable on at least one window after 2025-01. It is profitable without the LLM analyst (LLM is additive, not load-bearing). It has a one-paragraph mechanism explanation. The kill-switch and audit log are wired. The capital at risk is within G3 limits. I have not modified the strategy parameters in the last 30 days. I am ready for it to lose money for the next 3 months."*

If you can't sign every clause, do not press go.
