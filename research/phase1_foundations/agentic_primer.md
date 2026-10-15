# Agentic Trading — An Honest Primer

**Phase:** 1 — Foundations
**Author:** research analyst (skeptical-by-default)
**Date:** 2026-05-21
**Question:** What *is* agentic trading, and where (if anywhere) does it actually have edge?

> TL;DR — "Agentic trading" today is mostly LLMs wrapped around a backtester. As of May 2026, **no published paper has demonstrated statistically significant, fee-adjusted, live, out-of-sample alpha from a fully agentic LLM system over a long horizon**. The interesting and defensible LLM edge is in *slow* information synthesis (news, earnings, filings, regime classification), not in price prediction or execution. For a solo Indian operator with tiny capital, the realistic play is LLM-as-analyst feeding a small, rules-bound execution engine — not a fully autonomous "AI trader."

---

## 1. Taxonomy — five distinct things people call "AI trading"

Each row below is a *different* technology with different evidence base and different latency profile. Conflating them is the single biggest source of hype.

| # | Class | One-line description | Primary citation | Year |
|---|-------|---------------------|------------------|------|
| 1 | **Classical rule-based algo** | Hand-coded signals (MA cross, mean reversion, pairs, MM quoting). Deterministic, fast. | Chan, *Quantitative Trading* (2008); industry standard. | pre-2010 |
| 2 | **Statistical / ML signal models** | Supervised learning on engineered features → expected return / classification. Gradient boosting, factor models, deep nets on tabular. | Lopez de Prado, *Advances in Financial Machine Learning* (2018) — T3 textbook | 2018 |
| 3 | **RL trading agents** | Agent learns a trading policy by interacting with a market simulator. PPO/SAC/DDPG over OHLCV+indicators. | Liu et al., *FinRL: A Deep Reinforcement Learning Library for Automated Stock Trading*, arXiv:2011.09607 — T3 (paper + open code) | 2020 |
| 4 | **LLM-assisted signal generation** | LLM ingests news/filings/earnings calls → sentiment, event tags, embeddings that feed a downstream model or rules engine. Human or simple policy makes the trade. | Yang et al., *FinGPT: Open-Source Financial Large Language Models*, arXiv:2306.06031 — T3 | 2023 |
| 5 | **Fully agentic LLM systems** | Multiple LLM "personas" (analyst, researcher, risk, trader) debate and produce a decision; agent loop runs end-to-end. | Xiao et al., *TradingAgents: Multi-Agents LLM Financial Trading Framework*, arXiv:2412.20138 — T3 (paper + repo) | 2024 |

Adjacent / supporting work cited in this primer:

- *Deep Reinforcement Learning for Automated Stock Trading: An Ensemble Strategy*, Yang/Liu/Zhong/Walid, SSRN 3690996 (2020) — foundation of FinRL benchmarks. **T3.**
- *FinMem: A Performance-Enhanced LLM Trading Agent with Layered Memory and Character Design*, arXiv:2311.13743 (2023) — AAAI-SS published. **T3.**
- *FinRobot: An Open-Source AI Agent Platform for Financial Applications*, arXiv:2405.14767 (2024). **T3 (paper)**, but mostly an analyst/equity-research framework, not a live trader.
- *Instruct-FinGPT*, arXiv:2306.12659 (2023). **T3.**

---

## 2. Time-horizon map — what can plausibly win at which speed

LLM inference latency is the binding constraint everything else fits around. A single GPT-4-class round trip is roughly **0.5–10 s** end-to-end; multi-agent debate loops in TradingAgents-style systems are **10–60 s** per decision (T2: TradingAgents paper §experiments; observed in repo runs). That instantly disqualifies LLM agents from anything faster than ~minute-bar trading.

| Horizon | Examples | Winning approach | Can LLM agents play? |
|---------|----------|-----------------|----------------------|
| **microseconds** (HFT) | Co-located market-taking, latency arb | FPGA, hand-tuned C++, kernel bypass | **No.** Off by 6–9 orders of magnitude. Out of scope by charter. |
| **milliseconds** | Electronic market making, queue position | Classical rule-based + statistical, in C++/Rust | **No.** LLM latency alone fails. |
| **seconds–minutes** | Intraday quant, scalping, momentum bursts | ML signal models + execution algos | **Marginal.** LLM can pre-compute features overnight; cannot be in the decision loop. |
| **minutes–hours** | Intraday swing, opening-range, news reaction | ML + rules; sometimes LLM-assisted news triggers | **Plausible**, but news is already priced in within seconds for liquid US names. India equities are slower. |
| **days–weeks** | Swing, event-driven, earnings drift | LLM-assisted signals; classical event studies | **Sweet spot for LLM agents.** Decision latency irrelevant; news synthesis matters. |
| **weeks+** | Positional, factor tilts, regime allocation | Factor models; LLM regime/macro reasoning | **Sweet spot.** Cost of LLM inference amortized across long holds. |

**Honest read:** LLM-agent edge, if it exists at all, lives between ~days and ~months. Anyone claiming an agentic LLM doing intraday alpha needs to explain how they beat both the latency floor and the fact that liquid-equity news is already in the price within ~5 minutes of release (T3: extensive event-study literature; PEAD shrinks rapidly post-millennium).

---

## 3. Published evidence — what has actually been shown

Scoring rubric: T0 (anecdote) → T4 (I reproduced it). The trust score here measures **the strength of the evidence that the strategy makes money**, not the quality of the engineering.

| Paper | Year | Real money? | Out-of-sample? | Fees/slippage modeled? | Reported result | Trust score (for "makes money" claim) |
|-------|------|-------------|----------------|------------------------|-----------------|----------------------------------------|
| **FinRL** (arXiv:2011.09607) | 2020 | No | Train/test split; not walk-forward | Transaction-cost parameter included; slippage simplistic | Beats DJIA in backtest with PPO/A2C ensemble | **T2** — solid framework, but reported alpha is in-sample-flavored; community reproductions are mixed |
| **FinRL ensemble** (SSRN 3690996) | 2020 | No | Train/test split | Yes (cost term) | Outperforms DJIA, Sharpe ~1.3 in backtest | **T2** |
| **FinGPT** (arXiv:2306.06031, 2307.10485) | 2023 | No | Sentiment task, not trading | N/A — it's a model, not a strategy | SOTA on financial sentiment benchmarks | **T3 for the model**, but does **not** itself demonstrate trading profit |
| **FinMem** (arXiv:2311.13743) | 2023 | No | Yes, on a small ticker set and short window | Partially | Beats buy-and-hold on selected tickers (TSLA, AAPL, MSFT, etc.) over ~10 months | **T1–T2** — narrow universe, short window, classic survivorship/cherry-pick risk |
| **FinRobot** (arXiv:2405.14767) | 2024 | No | Not a trading study | N/A | Equity-research / analyst tasks | **N/A for trading** — useful framework, not evidence of P&L |
| **TradingAgents** (arXiv:2412.20138) | 2024 | No | Yes — claims OOS in v6/v7 | Partially | "Notable improvements" in cumulative return, Sharpe, MDD vs baselines | **T1–T2** — small ticker set, short window, baselines are weak; multiple independent reproductions show inconsistent results (T1) |
| **FinSABER / "Can LLM-based Financial Investing Strategies Outperform the Market in Long Run?"** (arXiv:2505.07078) | 2025 | No | **Yes — 20 years, 100+ symbols** | Yes | **Previously reported LLM advantages disappear under broad cross-section and long horizon; LLMs are over-conservative in bull markets and over-aggressive in bear markets** | **T3** — most rigorous negative result so far |
| **StockBench** (arXiv:2510.02209) | 2025 | No (contamination-free paper trading) | Yes — Mar–Jul 2025, 82 days, top-20 DJIA, post-training-cutoff | Yes | **Most LLM agents fail to beat buy-and-hold**; a few proprietary models edge it | **T3** — best clean OOS evidence to date; conclusion is "mostly negative" |
| **LiveTradeBench** (UIUC, GitHub ulab-uiuc/live-trade-bench + tech report, Oct 2025) | 2025 | Paper trading, live, real-time | Yes — by construction | Yes | Models that win static benchmarks **do worse** in live conditions | **T2–T3** |
| **A Test of Lookahead Bias in LLM Forecasts** (Gao/Jiang/Yan, arXiv:2512.23847) | 2025 | N/A | N/A | N/A | Develops statistical test; shows LLM "alpha" on news→returns tasks is partly **lookahead** from training data | **T3** — important methodological warning |
| **DRL Crypto Backtest-Overfitting** (arXiv:2209.05559) | 2022 | No | PBO-style probabilistic check | Yes | Less-overfit agents beat more-overfit ones; many "winning" DRL agents are overfit | **T3** — meta-result, not a profitable strategy |

**Bottom line on published evidence:**
1. Every paper claiming positive LLM-agent alpha that I could find uses a **small ticker universe, short window, and weak baselines**.
2. The two most rigorous, recent, and skeptical evaluations — **FinSABER (arXiv:2505.07078)** and **StockBench (arXiv:2510.02209)** — both conclude **LLM agents do not reliably beat buy-and-hold** out-of-sample with fees.
3. No paper I located reports **real-money, multi-year, fee-adjusted, statistically significant** OOS alpha from a fully agentic LLM trader. If such evidence exists, it is not in the open literature as of May 2026.

That is the headline negative finding of this primer.

---

## 4. Failure modes — the standard ways AI-trading results dissolve

Every one of these has been documented in financial ML; LLM agents add new flavors.

1. **Lookahead bias / training-data leakage (LLM-specific).** LLMs trained through, say, 2024-04 cutoff already "know" how stocks moved through that date. Any backtest of an LLM on pre-cutoff news produces phantom alpha. Gao/Jiang/Yan (arXiv:2512.23847, T3) formalize this with a "Lookahead Propensity" statistic. StockBench's whole design point is that data must post-date model cutoffs.
2. **Survivorship bias.** Backtesting on today's S&P 500 or NIFTY 50 silently drops the companies that delisted. Most academic LLM-trading studies do this. FinSABER explicitly calls it out (T3).
3. **Narrow-universe / cherry-picking.** "FinMem made money on TSLA, AAPL, MSFT" — a basket that went up regardless. Pick the universe after seeing the outcome, get fake alpha.
4. **Overfitting hyperparameters to the test set.** DRL is especially prone; the crypto backtest-overfitting paper (arXiv:2209.05559, T3) shows that probability-of-backtest-overfitting (PBO) is high in published RL trading work.
5. **Fee/slippage neglect.** Backtests with frictionless fills look great; live, taker fees + spread + impact often erase the edge. For Indian retail, STT + brokerage + GST + exchange fee + SEBI charges + stamp duty on intraday is ~0.10–0.15% **round trip** on equities — that kills any strategy with edge below ~1%/trade.
6. **Regime shift.** A model trained 2010–2019 (long QE bull) typically fails in 2022 (rates shock). LLM agents trained on text up to a date inherit the regime priors of that text corpus.
7. **Narrative bias / already-priced-in news.** LLMs are excellent at telling you *why* something happened — *after* the move. For liquid US names, post-release news drift is consumed in seconds. PEAD-style edges have shrunk steadily for 30 years.
8. **"Always-bullish" priors.** LLMs trained on financial-media text are biased toward growth/optimism narratives — they buy dips and miss regime breaks. FinSABER quantifies this: LLM strategies are over-conservative in bull markets (miss upside via stop-outs) and over-aggressive in bear markets (catch falling knives).
9. **Self-confirming evaluation.** When the LLM both *generates* the news summary and *trades* on it, errors are not independent. A single mis-classification cascades.
10. **Cost of compute as part of P&L.** A multi-agent debate at 30 s and ~$0.05 of API tokens, run on 50 tickers daily, is **$2.50/day or ~$900/year** in inference alone — before infra. On a ₹50,000 starting account, that's ~3% drag.

---

## 5. What LLM agents *plausibly* can and cannot do

### Plausible edge (worth building around)
- **News and filing synthesis at scale.** Reading 200 8-Ks, 10-Qs, or annual reports in a night is a real human-time multiplier. (Edge depends on whether the reading produces a *non-consensus* read.)
- **Earnings-call nuance.** Tone, hedging language, analyst-question evasion — empirically predictive at the **multi-day** horizon. Multiple pre-LLM NLP studies (Loughran/McDonald dictionaries) found tradeable signal here; LLMs likely improve on this. **T2** — extension is plausible, not yet cleanly demonstrated in agentic form.
- **Cross-asset / cross-document reasoning.** "This central-bank statement + this oil inventory + this currency move" — narrative stitching no single quant signal captures.
- **Regime classification.** Coarse macro state (risk-on / risk-off / vol regime) from text is a useful conditioning variable for *other* models.
- **Idea generation and hypothesis enumeration.** LLM as a research analyst for the human is high-value even if its trades are not.

### Not plausible (do not build around)
- **Price prediction beyond what's already in features.** No magic. If a feature isn't predictive when fed to XGBoost, the LLM won't extract more.
- **Microstructure / order-book alpha.** Latency floor alone forbids it.
- **Execution alpha.** TWAP/VWAP/IS implementation is a solved engineering problem; LLM does not help.
- **Beating well-engineered factor models on long-horizon equity selection.** Fama-French, Q-factor, and modern statistical-factor models are very hard to beat with text alone.
- **HFT, market-making, latency arb.** Off the table.

---

## 6. Where this leaves a solo Indian operator with tiny capital

Working assumptions: ₹50k–₹2L starting capital, India tax residency, NSE/BSE/MCX direct access (Zerodha/Dhan-class broker), US/global via LRS with high friction and tax overhead, crypto via FIU-registered exchanges with 30% flat tax + 1% TDS (T3: Indian Finance Acts 2022/2023).

**Brutal constraints first:**
- **Brokerage + STT + GST + stamp + exchange + SEBI fees** on Indian equity intraday total ~₹40–60 per round trip on a ₹50k notional. Any strategy with sub-1% per-trade edge is eaten alive.
- **F&O lot sizes** mean NIFTY/BankNIFTY positional options need ~₹50k–₹1L margin per leg; one bad day is catastrophic on a ₹50k account.
- **LLM inference cost** at meaningful scale (50+ tickers, daily) is ₹3,000–7,000/month on hosted APIs — a serious % drag on small capital.
- **Crypto 30% flat tax + 1% TDS** makes high-turnover crypto strategies almost mathematically impossible to win net.
- **No PMS, no RA license** — you cannot manage other people's money or publish recommendations.

**What this means for strategy choice:**
1. **Sub-daily LLM-agent trading on Indian equities is structurally hard.** Fees dominate at small size. Skip.
2. **Multi-day to multi-week LLM-assisted swing on a small basket** (10–30 liquid NSE names, or a few global names via INDmoney/Vested) is the only LLM-agent shape that survives cost analysis. Even here, the published evidence is *negative*, so live deployment should be paper-only until walk-forward shows edge net of all costs.
3. **The honest first build is "LLM as analyst, rules as trader."** LLM produces ranked theses overnight; a small, transparent rules engine decides position size, entry, stop. This separates the parts that LLMs are good at (synthesis) from the parts they are demonstrably bad at (timing, sizing, discipline).
4. **Crypto agentic trading is a tax trap in India** unless held >12 months in spot — at which point it's not really agentic trading.
5. **US equities via LRS** widen the universe and have better LLM-relevant signal density (more analyst coverage, more news) but add tax-filing complexity (Form 67, Schedule FA), FX cost, and TCS on remittance.

**Default skeptical recommendation (to be tested in later phases):**
> Build a **slow, news-and-filing-driven, LLM-assisted swing system** on a curated Indian-equity universe (maybe ~25 liquid large/midcaps), with all trading decisions executed by an auditable rules engine on signals the LLM produces. Paper-trade for ≥6 months. Require walk-forward, cost-included, statistically-significant outperformance over a simple momentum + value baseline before any real capital. Assume failure; design for graceful kill.

---

## Open questions carried to later phases

- Does any reproducible Indian-market LLM-agent study exist? (Phase 2)
- Real fee schedules and effective taxes at ₹50k–₹2L scale across Zerodha, Dhan, Upstox, IBKR India? (Phase 1/2)
- Best paper-trading venue with realistic NSE fills? (Phase 5)
- How to design a leakage-free evaluation given that any popular LLM has seen years of financial news? (Phase 5)
- Inference-cost model: local Llama-class vs hosted Claude/GPT at our token volume. (Phase 4)

---

## Sources cited (with score)

- TradingAgents — [arXiv:2412.20138](https://arxiv.org/abs/2412.20138) — T3 paper, T1–T2 P&L claim
- FinRL library — [arXiv:2011.09607](https://arxiv.org/abs/2011.09607) — T3
- FinRL framework — [arXiv:2111.09395](https://arxiv.org/abs/2111.09395) — T3
- DRL ensemble — [SSRN 3690996](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3690996) — T3
- FinGPT (open source) — [arXiv:2306.06031](https://arxiv.org/abs/2306.06031) — T3
- FinGPT (data) — [arXiv:2307.10485](https://arxiv.org/abs/2307.10485) — T3
- Instruct-FinGPT — [arXiv:2306.12659](https://arxiv.org/abs/2306.12659) — T3
- FinMem — [arXiv:2311.13743](https://arxiv.org/abs/2311.13743) — T3 paper, T1–T2 P&L claim
- FinRobot — [arXiv:2405.14767](https://arxiv.org/abs/2405.14767) — T3 (analyst, not trader)
- FinSABER ("Can LLM-based Strategies Outperform…") — [arXiv:2505.07078](https://arxiv.org/abs/2505.07078) — T3, **negative result**
- StockBench — [arXiv:2510.02209](https://arxiv.org/abs/2510.02209) — T3, **mostly negative result**
- LiveTradeBench — [github.com/ulab-uiuc/live-trade-bench](https://github.com/ulab-uiuc/live-trade-bench) — T2–T3
- Lookahead in LLM forecasts — [arXiv:2512.23847](https://arxiv.org/abs/2512.23847) — T3
- DRL crypto backtest-overfitting — [arXiv:2209.05559](https://arxiv.org/abs/2209.05559) — T3
- López de Prado, *Advances in Financial Machine Learning* (2018) — T3 textbook
