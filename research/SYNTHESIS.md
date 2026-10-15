# Synthesis — Agentic Trading Viability for a Solo Indian Operator

**Date:** 2026-05-21
**Status:** Strategic decision document. Operational verifications still pending (see §7).

This is built from five parallel research phases. Every load-bearing claim links to the phase file that carries the citations + trust scores. I am not smoothing over disagreements between phases — they are flagged.

---

## 1. The honest top-line

**A *fully* autonomous LLM trading system is not supported by current evidence.** Both rigorous 2025 evaluations (FinSABER 20-yr / 100+ symbols, StockBench contamination-free Mar–Jul 2025) found LLM agents **fail to reliably beat buy-and-hold after fees, out-of-sample**. No located paper as of May 2026 shows statistically significant fee-adjusted multi-year live OOS alpha. *(`phase1_foundations/agentic_primer.md`)*

The defensible build is **"LLM as analyst, rules as trader"**:
- LLM does what LLMs are actually good at: news/filings synthesis, earnings-call nuance, regime classification, cross-asset narrative.
- Deterministic rules do entry, sizing, risk, and exit. No LLM call in the order path.
- Horizon: **days to weeks** (5-min bars at the absolute fastest, given Phase 4 latency budget).

This is not your original idea ("fully autonomous"), but it is the version that survives the evidence bar.

---

## 2. Market pick

Two finalists from Phase 1a; recommendation between them is conditional on capital.

| Market | Min ticket | Why it survives | Why an LLM agent fits |
|---|---|---|---|
| **NIFTY/SENSEX weekly OTM options BUY** (NSE/BSE, Kite Connect) | ₹150–400 ticket; **₹15k floor for edge-detect** | Best liquidity-to-capital ratio post-Oct-2025 lot reform (NIFTY lot=65). Mature official API. ~1–1.2% round-trip fee forces positional horizon — matches LLM timescale, not a constraint. | News-, macro-, and event-driven; LLM can synthesize budget/earnings/global cues |
| **MCX commodity futures** (crude mini, natgas mini, gold mini) | ₹15–45k per lot | Cheapest derivative round-trip in India (~1.5–2 bps). News-driven during 5 PM–11:55 PM IST US-overlap window. | Globally headline-driven during evening session = natural LLM informational edge |

**Hard rule-outs** (Phase 1a + V-4, V-5): offshore crypto (FEMA/IT Act), Polymarket / prediction markets (PROGA 2025 + MeitY block), tokenized stocks, spot FX with offshore brokers, US options via LRS (RBI bars derivatives), **US options via IBKR India** (closed for resident Indians, T3), **US derivatives via NSE IX Global Access** (equities/ETFs only, no derivatives, T3), HFT (LLM latency floor). FIU-registered Indian crypto is legal but the 30% flat + 1% TDS + no-loss-offset regime mathematically rules out any high-turnover strategy — only buy-and-hold survives, so it does not earn an LLM-agent slot. **NSE F&O via IBKR India is open** for resident Indians (V-4, T3) — alternative broker route to Kite if needed.

**Pick for *this* operator (very low capital): NIFTY weekly OTM option BUY.** Lower min capital, same broker stack, cleanest tax. MCX is the planned second venue once Stage-3 gates clear.

**Disagreement resolved (V-3):** SEBI circular 2024/181 dated **2024-12-30** is the methodology mandate; NSE FAOP70616 (eff Jan 2026) is its operational implementation. Phase 5's "Oct 28 2025" date was wrong. **Current lot sizes:** NIFTY 65, BANKNIFTY 30, FINNIFTY 60, MIDCPNIFTY 120, NIFTYNXT50 25. *(T3, phase2_evidence/verification_pass.md V-3)*

---

## 3. The economics — read this twice

From `phase4_infra/infra_cost_model.md` and `phase5_capital/min_capital.md`:

- **Infra + LLM burn floor: ~₹3,500/month** (AWS t4g.small Mumbai RI $5.18/mo + Kite Connect data + Haiku/Flash at 5-min cadence). Mumbai pricing runs ~10–22% above us-east-1, which corrects Phase 4's earlier ₹2.5–3k estimate. Theoretical ₹190/mo on Oracle Always Free Mumbai is real but A1-capacity-constrained and Oracle's terms allow reclamation — not durable enough to bet capital on. *(Verified: phase2_evidence/verification_pass.md V-6, V-7)*
- **SEBI 2026-04-01 framework mandates Indian-server hosting.** ap-south-1 is mandatory. US/EU regions are out.
- **Live-capital hard floor: ₹15,000.** Below that, per-trade frictions (~₹70–120 round trip on options + ₹15.93 DP/equity sell) drown any plausible per-trade edge — you cannot statistically separate skill from luck, defeating the point of going live.

**The break-even bar (updated post-V-6):** At ₹15k capital + ₹3.5k/mo infra, the strategy must net **~23% per month** just to pay the infra rent. At ₹25k capital, ~14%/month. At ₹50k, ~7%/month. **These are heroic numbers.** Any backtest that hits them on first try should be treated as overfit until proven otherwise (Phase 1b §6, Phase 5 validation_framework.md).

This is the honest economic picture. It is not impossible, but the margin for error is essentially zero.

---

## 4. The stack

Lifted from Phase 3 GitHub mining — these are the components that survived the trust filter:

| Layer | Component | License | Trust | Why |
|---|---|---|---|---|
| Broker abstraction (India) | **openalgo** (marketcalls) | AGPL-3.0 | T3 | Only credible OSS unified abstraction over 30+ Indian brokers + Sandbox paper mode |
| Backtest engine (research) | **vectorbt** / **backtrader** | various | T3 | Fast iteration; well-known traps documented |
| Backtest engine (production parity) | **nautilus_trader** | LGPL | T3 | Event-driven, backtest-live parity, the eventual production target |
| Data/factor substrate | **microsoft/qlib** | MIT | T3 | Gold-standard point-in-time data + factor research |
| Agent cognitive loop (pattern only) | **TauricResearch/TradingAgents** | Apache-2.0 | T2 | Borrow the LangGraph multi-agent debate graph; **do not use as a system** — it has no execution/backtest/fee layer (verified in local clone, `default_config.py:6` shows hardcoded researcher path) |
| Memory pattern | **FinMem** (paper) | — | T2 | Layered episodic/semantic memory for the LLM analyst |
| Validation discipline | Vibe-Trading patterns (run cards, hypothesis registry, AST purity, lookahead guards) | — | T1→useful | Star-velocity anomaly noted; engineering ideas legit, treat as patterns not as a system |

**Repos to ignore on sight** (Phase 3): HKUDS/AI-Trader (18.3k★ stars-as-marketing, no license, SaaS funnel), nof1.ai (affiliate links), AutoHedge ("hedge fund in minutes"), the `polymarket-*-arbitrage-bot` SEO cluster, and the genre of "fully-automated-nifty-options-trading" repos.

**Paper-trading venues** (Phase 5):
- **Strategy R&D:** Alpaca paper (free, full API parity, accessible to Indians)
- **Indian plumbing:** Upstox Sandbox (best free India sandbox); openalgo's Sandbox mode
- **Highest fidelity (if account opened):** IBKR Paper
- **Avoid as paper venues:** Zerodha (no real sandbox, confirmed in own docs), AngelOne (same), Dhan (₹100 flat fills make it useless for P&L)

---

## 5. Architecture (concrete)

```
                ┌─────────────────────────────────────────────┐
                │  Data layer (qlib-style, PIT-correct)        │
                │  - NSE/BSE EOD + intraday (Kite history API) │
                │  - News (RSS + LLM summarization)            │
                │  - Macro calendar, earnings calendar         │
                └────────────────┬────────────────────────────┘
                                 │
                                 ▼
                ┌─────────────────────────────────────────────┐
                │  Analyst layer (LLM, slow loop, 15-min+)     │
                │  - Multi-agent debate (TradingAgents-style)  │
                │  - Outputs: regime tag, bias, conviction,    │
                │             news-event flags                 │
                │  - Layered memory (FinMem-style)             │
                └────────────────┬────────────────────────────┘
                                 │  (writes to a signal store)
                                 ▼
                ┌─────────────────────────────────────────────┐
                │  Strategy layer (DETERMINISTIC, no LLM)      │
                │  - Reads LLM signals + price features        │
                │  - Rules: entry, position sizing, stops      │
                │  - Risk caps: per-trade DD, daily DD, kill   │
                └────────────────┬────────────────────────────┘
                                 │
                                 ▼
                ┌─────────────────────────────────────────────┐
                │  Execution layer (openalgo on ap-south-1)    │
                │  - Kite Connect for NSE/BSE/MCX              │
                │  - 5-yr audit logs (SEBI mandate)            │
                │  - Static IP + 2FA                           │
                └─────────────────────────────────────────────┘
```

Key principle from Phase 3 patterns: **single `Strategy` interface used identically by backtest, paper, and live.** Backtest-to-live parity is non-negotiable. The LLM analyst is intentionally *out* of the order path — it produces signals that the strategy layer is free to ignore.

---

## 6. The ramp (gated, not optimistic)

Lifted from `phase5_capital/validation_framework.md`:

| Stage | Capital | Duration | Gate to next |
|---|---|---|---|
| **G0 Backtest** | — | until validation harness passes | **PBO ≤ 0.5 (hard) / ≤ 0.2 (soft) via CSCV S=16; Deflated Sharpe ≥ 0.95 with honestly-counted N_trials; CPCV N=8, k=2, purge ±label-horizon, embargo 2% of T; ≥1 post-LLM-cutoff window (2025-01+); ≥50 trades; includes 1 bear + 1 calm + 1 shock period; fees worst-plausible-case.** (Tightened per Phase 7 / López de Prado citations) |
| **G1 Paper** | ₹0 (Alpaca + Upstox Sandbox) | **60 days / ≥30 trades** | Live paper Sharpe within 1σ of backtest; no behavioral anomalies |
| **G2 Plumbing live** | **₹5,000** (BSE SENSEX deep-OTM buy, smallest tickets) | 30 days | Order plumbing, audit logs, kill-switch, broker session resilience all verified end-to-end |
| **G3 Edge-detect live** | **₹15,000–25,000** (NIFTY weekly OTM buy, lot 65) | 3 months / ≥50 trades | Net P&L > **₹3,500/mo** (clears infra, V-6 updated) AND statistically distinguishable from luck (t-stat > 2) |
| **G4 Scale** | 2× steps | indefinite | Re-verify each step; halt if any gate-3 metric drops |

**Kill-switch criteria (any one triggers full stop):** max DD > 15% of capital, 5 consecutive losses, broker session failure cascade, model anomaly (LLM hallucination flagged in signal log), exchange / regulator action, monthly burn > ₹4,000 without P&L cover, **OPS > 10/sec/exchange** (SEBI threshold, V-2 T3 — would trigger per-strategy registration requirement).

**Honest expectation: G3 is the most likely failure point.** Most strategies that pass G0+G1 die at G3. Plan emotionally for that.

---

## 7. What's still T0/T1 — Phase 2 verification list

These do not change the strategic call, but they must be resolved before Stage G2:

- **V-1** Latency ap-south-1 → Kite Connect REST/WS (currently T1 community lore — need a T4 measurement)
- ~~V-2~~ ✅ **10 OPS / exchange / client, placements only, static IP + Algo ID mandatory** (T3, SEBI Feb 4 2025 + broker portals)
- ~~V-3~~ ✅ **Lot sizes:** NIFTY 65, BANKNIFTY 30, FINNIFTY 60, MIDCPNIFTY 120, NIFTYNXT50 25 (T3)
- ~~V-4~~ ✅ **IBKR India:** NSE F&O open for residents; US options closed (T3, RBI LRS bars derivatives)
- ~~V-5~~ ✅ **NSE IX Global Access:** equities/ETFs only, no derivatives (T3)
- ~~V-6~~ ✅ **AWS Mumbai:** t4g.small RI $5.18/mo, t4g.medium RI $10.37/mo, gp3 $0.0912/GB-mo, egress $0.1093/GB (T3)
- ~~V-7~~ ✅ **Oracle Always Free Mumbai:** still offered, A1 capacity-constrained, reclamation clause confirms non-durability (T3)
- ~~V-8~~ ✅ **LLM TTFT:** Haiku 4.5 0.80s, Flash 0.67s, Flash-Lite 1.25–1.66s, GPT-5.4-mini 0.76s; no vendor SLA exists (T3, artificialanalysis.ai)
- 🟡 **V-1 partial** ✅ from Kochi Jio FTTH: Kite REST TTFB p50/p99 = **320.9 / 740.0 ms** (T4, n=30). WS subscribe TTFB p50 = 482.9 ms. Kite WS confirmed on AWS ap-south-1 (reverse-DNS T4). ap-south-1 → Kite still T1 (defensible bounds: REST cold 30–80 ms, WS subscribe→first tick 100–400 ms) until EC2 runbook in v1_latency_v9_contamination.md §A.5 is executed. **Phase 4 budget unchanged** — LLM call dominates network by 10×+.
- ~~V-9~~ ✅ **Contamination probe design done** with quantitative thresholds (T3 methodology, borrows arXiv:2512.23847). Executable harness scaffolded and smoke-tested (`contamination_probe.py`, 376 prompts ready, no network calls). Gate matrix in v1_latency_v9_contamination.md. **Combined gate:** any "disqualified" probe → no LLM in signal path; default architecture posture is Role-2 (regime tags + event flags only, no price forecasts) which matches §5.
- 🟡 **V-10 — Validation harness is a hard G0 prerequisite.** No strategy (LLM-derived or hand-written) is allowed to reach G1 paper without clearing PBO + DSR + CPCV per the tightened §6 thresholds. *Added 2026-05-21 per Phase 7 verdict.* Implementation lands in `agent_trader/validation/` (cpcv.py, pbo.py, dsr.py, mtrl.py, trial_log.py).
- **V-9** Lookahead bias from LLM training-data contamination on Indian tickers — design a contamination test before any backtest is allowed to count

---

## 7a. Built artifacts (as of 2026-05-21)

- `agent_trader/validation/` — CPCV + PBO + DSR + trial_log + regime_splits + harness. **G0a gate live and passing.**
- `agent_trader/portfolio/` — ExpWeights (Hedge) + NIG Bayesian sizing + fractional Kelly + Allocator. **G0c gate live and passing.** Mathematical claims: Hedge regret ≤ B·√(2T·ln K) (verified empirically), posterior μ shrunk >70% at n=30, total exposure hard-capped, zero-deployment-without-edge.
- `agent_trader/data/yfinance_loader.py` — free Indian-data adapter for development.
- `agent_trader/backtest/runner.py` — minimal daily-bar backtester (single + pair).
- W3-4 strategies S1/S2/S3 all CLOSED after failing the harness. 56 trials logged honestly.

## 7b. Architecture choices ruled out by Phase 7 (2026-05-21)

- ❌ **LLM-as-offline-strategy-generator ("strategy foundry")** — evaluated and rejected. Zero peer-reviewed work shows LLM-generated strategies clearing PBO+DSR+CPCV on contamination-free OOS; three independent rigorous negative results (Profit Mirage arXiv:2510.07920, MemGuard-Alpha, FinSABER KDD-2026). Honest probability vs buy-and-hold NIFTY 5–10% (vs 8–15% for analyst architecture). Full reasoning: `phase7_strategy_foundry/verdict.md`.
- ❌ **Autonomous LLM-driven strategy iteration in production.** Drift detection is fine; LLM-rewriting-strategy-while-live is not. Any strategy change is a new trial; new trials require re-running G0 and incrementing the N_trials counter against the Deflated Sharpe critical value.
- ✅ **Permitted foundry-like use:** *LLM proposes hypotheses for human review → human implements as hand-written rules → harness gates promotion.* This is "LLM as research analyst for a human quant" — productivity tool, not autonomous generator. Does not change the runtime architecture.

## 8. The honest go/no-go

**Conditional GO** on the following:

1. You commit to **"LLM as analyst, rules as trader"** — not fully autonomous in the order path.
2. You accept the **G0 → G4 ramp** with real gates, not aspirational ones. G0 alone is months of work.
3. You can sustain **~₹3,000/month** in infra+LLM burn during paper trading with no P&L, for at least 6 months.
4. You accept that ~70%+ probability is that the strategy dies at G3 and you walk away with ₹15k spent + learnings (not riches).
5. You revoke the leaked GitHub PAT.

If any of those are not true, **no-go**. The honest read of the evidence does not support staking real capital on a higher-confidence story.

**If you proceed, the next actions are:**
- Resolve V-1 through V-9 (Phase 2). Roughly 1–2 days of focused verification.
- Stand up the repo skeleton (qlib data + openalgo execution + deterministic strategy interface + LLM analyst stub). No live calls.
- Pick **one** strategy hypothesis to test first (recommend: NIFTY weekly OTM buy gated by an LLM regime+event signal, daily decision cadence). Run G0 end-to-end on it.

---

## Appendix — file map

- `README.md` — charter
- `trust_rubric.md` — T0–T4 rules
- `tracker.md` — phase status + open questions + decisions log
- `phase1_foundations/market_matrix.md` — 11 markets scored, finalists + rule-outs
- `phase1_foundations/agentic_primer.md` — taxonomy, evidence review, honest limits
- `phase3_github/index.md` — 25+ repo dossier index
- `phase3_github/patterns.md` — 12 patterns + 10 anti-patterns
- `phase3_github/dossier_*.md` — 23 per-repo dossiers
- `phase4_infra/infra_cost_model.md` — hosting + latency + cost
- `phase5_capital/min_capital.md` — min ticket + min edge-detect capital per market
- `phase5_capital/paper_testing.md` — Indian + global paper venue audit
- `phase5_capital/validation_framework.md` — walk-forward, OOS, regime tests, kill-switch
- `sources/raw/` — cached primary sources (date-prefixed)
