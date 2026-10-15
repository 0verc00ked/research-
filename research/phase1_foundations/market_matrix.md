# Phase 1 — Market Matrix (India-accessible, API-tradable)

**Date:** 2026-05-21
**Author:** research assistant for Nikhil-S
**Scoring:** 1 (worst) — 5 (best) per cell. Score is the assistant's judgment given the user's constraints (solo, low capital, LLM-agent making minute-to-day decisions, ap-south-1 hosted, India tax-resident).
**Trust scores (T0–T4) refer to `trust_rubric.md`.**
**Staleness flag:** SEBI retail-algo framework hit full enforcement on 2026-04-01, and exchange-side operational modalities are still being shaken out. Several numbers below need re-verification before any live deployment (call them out as such).

---

## 0. Cross-cutting context

### SEBI retail algo framework (Feb 4, 2025 circular; full enforcement Apr 1, 2026)
- Broker = principal, vendor = agent; broker liable for all API orders.
- Self-developed "white-box" algos for own use: permitted via broker API with static-IP whitelist + 2FA + 5-yr log retention.
- Any algo crossing per-second order thresholds, or any algo *offered* to others, requires per-strategy exchange registration via the broker.
- **All retail algos must be hosted on Indian servers** — kills US/EU cloud regions for the order-routing layer.
- Source: SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013 (T3) — https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html ; extension circular Sep 30, 2025 (T3) — https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html
- Staleness: HIGH. Confirm threshold values and registration mechanics with the chosen broker before going live.

### Fee schedule baseline (Zerodha 2026, T3)
- Source: https://zerodha.com/charges/ — primary broker fee page, fetched 2026-05-21, saved at `sources/raw/2026-05-21_zerodha_charges.md`.
- Used as the reference; Dhan/Fyers/Upstox are within ~10–20% of these.

### Tax baseline (T3 — Income Tax Act 2025, in force from 2026-04-01; carries forward old Section 43(5) treatment)
- Equity delivery: capital gains (STCG 20% if <12mo, LTCG 12.5% > Rs 1.25L if ≥12mo — *needs re-verification post Budget 2026*).
- Equity intraday: **speculative business income**, taxed at slab, loss set-off limited to speculative income, 4-yr carry-forward (Section 43(5)).
- F&O (index/stock futures, options, currency, commodity): **non-speculative business income**, slab rate, 8-yr loss carry-forward, ITR-3.
- Crypto VDAs: 30% flat under Section 115BBH + 4% cess; 1% TDS under Section 194S; only cost of acquisition deductible; losses *not* set-offable against any other income.
- US stocks via LRS: dividends taxed at slab (with US 25% withholding creditable via DTAA); capital gains taxed in India.
- Sources: ClearTax / Sahi / Lemonn guides (T2 — multiple independent corroboration); Section 115BBH and 194S of the Act (T3).

### Latency floor for solo cloud bot in ap-south-1
- AWS Mumbai → broker REST endpoint (Zerodha/Dhan): typically **40–120 ms** order round-trip end-to-end (T1 — common community-reported figure, no primary measurement saved; treat as needs verification).
- Co-located NSE leased-line: <1 ms — irrelevant here, retail can't get it for solo budgets.
- LLM inference adds 300 ms – 3 s per decision (Claude/GPT API class).
- **Net floor for an LLM-driven agent: ~1–5 seconds end-to-end** (worse than the broker latency by an order of magnitude). This rules out anything sub-minute-edge.

---

## 1. NSE / BSE cash equities

| Dim | Score | Note |
|---|---|---|
| Liquidity | 5 | Top 100 names: tens-of-crores per day; <5 bps spreads on Nifty 50. (T2: NSE daily bhavcopy + Sensibull liquidity dashboards) |
| Round-trip fee | 4 (intraday) / 3 (delivery) | Intraday: Rs 20 brokerage + 0.025% STT sell + ~0.006% txn + 0.003% stamp + 18% GST → **~3.5–4 bps** all-in on a Rs 1L round-trip (T3: zerodha.com/charges). Delivery: STT 0.1% × 2 = **20 bps** + stamp 1.5 bps + GST → ~22 bps. |
| API quality | 5 | Kite Connect: REST + WebSocket, well-documented, 10 req/s, 3000 instruments per WS connection. Personal API free; vendor/connect Rs 500/mo (T3: https://kite.trade ; https://zerodha.com/products/api/). |
| Min capital (1 instrument) | 5 | One share of any large-cap; ~Rs 100 minimum. Margin not required for delivery. |
| Regulatory burden | 3 | Full SEBI algo framework applies. Static IP, exchange registration above order/sec thresholds. (T3: SEBI Feb 2025 circular) |
| Latency floor | 4 | 40–120 ms broker RTT from ap-south-1 (T1, needs verification). |
| Agent-friendliness | 4 (delivery) / 2 (intraday) | Delivery on multi-day horizon = great fit for slow LLM agent. Intraday is fee-eaten unless edge > ~8 bps/trade. |
| Tax | 3 | Delivery CG is clean. Intraday = speculative, slab rate, awkward loss treatment (T3: Section 43(5)). |
| Red flags | — | Circuit limits, T+1 settlement, illiquid mid/small-caps have huge spreads. |

---

## 2. NSE F&O

### 2a. Index options (NIFTY, BANKNIFTY, FINNIFTY, SENSEX)
| Dim | Score | Note |
|---|---|---|
| Liquidity | 5 | NIFTY weekly ATM: lakhs of contracts daily, 1-tick spreads. BANKNIFTY: deep but moved to monthly-only weekly schedule post-2024. SENSEX (BSE) weekly: now the second-most-liquid index option in India. (T2: NSE/BSE volume reports) |
| Round-trip fee | 3 | Rs 20 + Rs 20 brokerage + STT 0.15% on sell premium + NSE txn 0.03553% on premium × 2 + stamp 0.003% buy + GST. On a Rs 100 premium × 65-lot NIFTY = Rs 6500 turnover, all-in ≈ **Rs 65–80**, i.e. **~1.0–1.2% of premium round-trip** (T3: zerodha.com/charges, T4: computed). This is the biggest fee bite in Indian markets. |
| API quality | 5 | Same Kite Connect; full options chain over WS. |
| Min capital (1 instrument) | 4 | Lot sizes from Jan 1, 2026: NIFTY = 65, BANKNIFTY = 30, SENSEX = 20 (T3: NSE circular FAOP70616 — https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf). Buying a 1-lot OTM NIFTY weekly call: premium often Rs 20–50 → **Rs 1,300–3,250** min capital + Rs 5–10k buffer for slippage. Selling needs Rs 1.0–1.5 lakh SPAN+ELM margin. |
| Regulatory burden | 3 | Same SEBI algo framework. Plus index F&O lot-size hikes (Nov 2024) raised contract value to Rs 15L+ to push retail out; partially reversed Jan 2026 (T3: NSE circular). |
| Latency floor | 3 | 40–120 ms; tick speed in BANKNIFTY ATM can be sub-ms — your edge is gone at retail latency. |
| Agent-friendliness | 3 | Good for *positional* options (multi-day directional/IV plays). Bad for scalping — fees alone require >100 bps premium move per trade to break even. |
| Tax | 4 | F&O = non-speculative business, slab rate, 8-yr loss carry-forward (T3: Section 43(5)). Clean. |
| Red flags | — | Liquidity drops off rapidly away from ATM and beyond next-week expiry. STT-on-exercise trap (0.15% of *intrinsic*) blows up ITM-held-to-expiry. |

### 2b. Index futures
| Dim | Score | Note |
|---|---|---|
| Liquidity | 4 | NIFTY/BANKNIFTY futures liquid; mid-month/far month thin. |
| Round-trip fee | 4 | STT 0.05% sell only + Rs 20 + Rs 20 + txn 0.00183% × 2 + stamp 0.002% + GST. On NIFTY ~ Rs 16L notional/lot: ~**Rs 900–1000 round-trip = ~5–6 bps**. (T3) |
| API quality | 5 | Same as above. |
| Min capital | 2 | SPAN+ELM ~ Rs 1.5–2.5 lakh per NIFTY lot (T2: Zerodha margin calculator https://zerodha.com/margin-calculator/Futures/). Out of range for "very low capital." |
| Regulatory burden | 3 | Same. |
| Latency floor | 3 | Same. |
| Agent-friendliness | 3 | Cheap per trade but capital-heavy. |
| Tax | 4 | Non-speculative. |
| Red flags | — | Capital wall. |

### 2c. Stock options
| Dim | Score | Note |
|---|---|---|
| Liquidity | 2 | Concentrated in ~30 names; most stock options have wide spreads and bad fills. (T1) |
| Round-trip fee | 2 | Same option fee structure but premium % is higher → effective bp cost similar but slippage dominates. |
| API quality | 5 | Same Kite. |
| Min capital | 3 | Highly varies; e.g. RELIANCE option lot is small (~250) but premiums in hundreds → Rs 5–20k per buy. Selling = Rs 1–3L margin. |
| Regulatory burden | 3 | Same. |
| Latency floor | 3 | Same. |
| Agent-friendliness | 2 | Liquidity penalty makes algo execution risky. |
| Tax | 4 | Non-speculative. |
| Red flags | — | Thin books, expiry pinning risk. |

### 2d. Stock futures
| Dim | Score | Note |
|---|---|---|
| Liquidity | 3 | Top ~50 names liquid. |
| Round-trip fee | 4 | Similar to index futures, ~5–7 bps. |
| API quality | 5 | Same. |
| Min capital | 2 | Rs 80k–3L margin per name. |
| Regulatory burden | 3 | Same. |
| Latency floor | 3 | Same. |
| Agent-friendliness | 3 | Capital-heavy. |
| Tax | 4 | Non-speculative. |
| Red flags | — | Capital wall. |

---

## 3. MCX commodities (gold/silver/crude/natgas)

| Dim | Score | Note |
|---|---|---|
| Liquidity | 3 | Crude oil mini, gold mini, natgas: decent during US session overlap (5pm–11:55pm IST). Daytime thin. (T1) |
| Round-trip fee | 4 | CTT 0.01% sell + brokerage Rs 20 + MCX txn 0.0021% × 2 + stamp 0.002% + GST. On gold mini (~Rs 7–8L notional): ~**Rs 100–150 RT = ~1.5–2 bps**. (T3: zerodha.com/charges) |
| API quality | 5 | Kite Connect supports MCX same as NSE. |
| Min capital | 3 | Gold mini margin ~Rs 35–45k; crude mini ~Rs 20–30k; natgas mini ~Rs 15–25k (T2: Zerodha margin calculator). Crude mini is the cheapest serious commodity lot. |
| Regulatory burden | 3 | Same SEBI framework (commodity F&O covered). |
| Latency floor | 4 | Same; MCX is slower-paced than index options, so retail latency is less of a handicap. |
| Agent-friendliness | 4 | Globally-driven moves (crude, gold) lend themselves to news/macro LLM reasoning on minutes-to-hours timescale. |
| Tax | 4 | Non-speculative business (T3). |
| Red flags | — | Liquidity gaps in Indian morning hours, expiry physical-delivery for some contracts (avoid last week). |

---

## 4. NSE currency derivatives (INR pairs only)

| Dim | Score | Note |
|---|---|---|
| Liquidity | 2 | USDINR futures: still functional but volumes shrunk dramatically after April 2024 RBI rule on declared underlying exposure (T3: https://www.business-standard.com/economy/news/rbi-defers-implementing-currency-derivatives-regulations-till-may-3-124040401233_1.html). EURINR/GBPINR/JPYINR: very thin. |
| Round-trip fee | 5 | No STT, tiny txn charges. ~2 bps RT on futures, ~Rs 25–35 per option lot. (T3) |
| API quality | 5 | Same Kite. |
| Min capital | 4 | Lot = 1000 USD; margin ~Rs 1500–2500 per lot. Lowest entry of any derivative. |
| Regulatory burden | 2 | Post April 2024, retail must self-declare contracted underlying FX exposure for positions, with a USD-100M-equivalent grace cap (T3: NSE Clearing position limits — https://www.nseclearing.in/risk-management/currency-derivatives/position-limits). Many retail traders pulled out; brokers added attestation friction. Algo-trading is legal but the attestation overlay is annoying. |
| Latency floor | 3 | Same. |
| Agent-friendliness | 2 | INR pairs mostly track RBI's managed band → tiny realised moves, edges < fees. |
| Tax | 4 | Non-speculative. |
| Red flags | — | RBI heavy-hand on rupee. PnL distribution is fat-tailed-but-narrow. Vol crushed by managed float. |

---

## 5. Crypto on Indian FIU-registered exchanges (CoinDCX, Mudrex, Giottus, ZebPay, Delta Exchange India)

| Dim | Score | Note |
|---|---|---|
| Liquidity | 3 (spot) / 4 (Delta derivatives) | CoinDCX spot OK on BTC/ETH/SOL/XRP; alt depth thin. Delta India derivatives: ~$2.5B/day system-wide (T1: Delta press release; not independently audited). |
| Round-trip fee | 2 (spot) / 4 (Delta perps) | CoinDCX spot 0.20% maker + 0.20% taker → **40 bps RT** (T2: tradersunion, coindcx blog). Delta perps 0.025% maker / 0.075% taker → ~10 bps RT. **Plus 1% TDS on every sell**, plus 30% on net gain. Crypto TDS makes Indian-rail crypto trading the most fee-hostile market in this list for high-turnover strategies. |
| API quality | 4 | CoinDCX REST + WS, official, public docs (T3: https://coindcx.com/api/). Delta Exchange India has full REST/WS, FIX is institutional-only. |
| Min capital | 5 | Fractional BTC/ETH down to Rs 100. Delta perps: lowest margin ~Rs 200–500 to open a contract. |
| Regulatory burden | 3 | FIU registration + PMLA compliance is on the exchange, not the retail user. SEBI algo framework does NOT cover crypto (SEBI doesn't regulate VDAs; only PMLA + IT Act). But this means no formal algo-protection framework either — broker liability is murky. (T2) |
| Latency floor | 4 | Most Indian exchanges colo their matching engines in India or Singapore. ap-south-1 → CoinDCX/Delta typically <50 ms. (T1) |
| Agent-friendliness | 3 | 24/7 markets = great for LLM agent (no expiry pressure, news-driven). BUT 1% TDS + 30% flat + no loss set-off kills any strategy with churn > a few trades/month. **Only buy-and-hold-class strategies survive the tax math.** (T3: Section 194S, 115BBH) |
| Tax | 1 | Worst tax regime in this list. 30% on gain, no loss offset, no expense deduction, 1% TDS per sell (refundable but locks up working capital). (T3) |
| Red flags | — | WazirX hack 2024 and ongoing restructuring (treat WazirX as defunct for new deployments). Tax math broken for algo turnover. Stablecoin off-ramp scrutiny. |

---

## 6. Crypto on offshore exchanges (Binance, Bybit, OKX) via VPN / foreign account

| Dim | Score | Note |
|---|---|---|
| Legality | **1** | Offshore exchanges without FIU registration are blocked by MeitY since Dec 2023; using VPN to access them = violates IT Act + likely FEMA (sending INR via P2P/USDT off-ramp to fund offshore = unapproved capital account transaction). 30%+1% TDS still applies; non-reporting risks PMLA action. (T3: https://righttoinformation.wiki/cryptocurrency-legal-india-2026 ; T2) |
| All other dims | — | Not scored. Ruled out on legality. |

**Dealbreaker. Do not pursue.**

---

## 7. US equities/ETFs via LRS (Vested, INDmoney, IBKR-India)

| Dim | Score | Note |
|---|---|---|
| Liquidity | 5 | NYSE/NASDAQ. Best in the world. |
| Round-trip fee | 3 | Vested/INDmoney: 0–0.25% per trade + FX spread 50–100 bps + TCS 20% on remittances >Rs 7L (refundable as tax credit but lockup). IBKR: Rs 100–200 flat per US trade + ~30 bps FX. (T2: vendor pages) |
| API quality | 2 (Vested/INDmoney) / 5 (IBKR) | Vested/INDmoney: **no public retail API**. IBKR: full TWS API, IB Gateway, REST/Web API, official (T3: interactivebrokers.com). |
| Min capital | 4 | Fractional shares supported. $10 entry. |
| Regulatory burden | 3 | LRS USD 250k/yr per individual cap. Form A2 declaration on remittance. TCS handling. (T3: RBI LRS master direction) |
| Latency floor | 1 | Routing India→US adds 200–300 ms RTT on top of broker latency. (T2) |
| Agent-friendliness | 4 | Slow-horizon LLM agents on US equities = canonical fit. News, earnings, sentiment all in English. |
| Tax | 3 | CG taxed in India (LTCG 12.5% if >24mo, STCG slab); dividend slab with US 25% withholding creditable. (T3) |
| Red flags | — | **No retail options via LRS — RBI explicitly disallows derivatives under LRS (T3: RBI Master Direction on LRS).** TCS lockup on remittances. INR depreciation = silent tailwind/headwind. |

---

## 8. US equities/options via IBKR-direct or GIFT-IFSC (NSE IX Global Access)

| Dim | Score | Note |
|---|---|---|
| Legality | 3 | IBKR-direct (non-LRS, on foreign income): legal only if the funds are foreign-source (e.g. foreign salary, NRE proceeds). Using LRS funds for options at IBKR = grey/non-compliant per the LRS derivative bar. **NSE IX Global Access** launched Feb 2026 — direct US stock access from GIFT City IFSC under IFSCA, *not* SEBI; LRS-funded (T2: https://www.moneylife.in/article/nse-ix-opens-direct-us-stock-trading-for-indians-sparks-regulatory-debate/79796.html ; https://www.hindchakra.com/2026/03/01/nse-international-exchange-launches-global-access-platform-indian-investors-gain-direct-route-to-us-stocks/ ). Whether NSE IX permits *options* for Indian residents is **unclear as of May 2026 — needs verification with IFSCA**. |
| Liquidity | 3 | GIFT-IFSC US stock book is shallow (new product, single-broker routing). IBKR-direct: full liquidity. |
| Round-trip fee | 3 | IBKR US options: $0.65/contract + exchange fees. Cheap by Indian standards. GIFT IFSC fees published per-trade by NSE IX — verify. |
| API quality | 5 (IBKR) / 1 (NSE IX) | IBKR API = gold standard. NSE IX Global Access has no documented retail API as of May 2026 (T0 — needs verification). |
| Min capital | 4 | Single options contracts; $50–500. |
| Regulatory burden | 4 (IBKR with foreign funds) / 2 (NSE IX retail) | Tax reporting (Schedule FA, Schedule FSI) onerous either way. |
| Latency floor | 1 | India→US RTT. |
| Agent-friendliness | 5 | US options + LLM-driven slow-horizon strategies is arguably the strongest fit in the entire matrix — **if** legality and funding pathway hold. |
| Tax | 2 | Complex. Options PnL in India = business income (slab). Schedule FA disclosure. (T2) |
| Red flags | — | **Funding pathway is the entire question.** If LRS is the only way the user can fund, options are out per RBI. NSE IX needs verification on what instruments retail can access. |

---

## 9. Forex via INR-denominated pairs

Same as item 4 above. Genuine global FX (EURUSD spot etc.) is **not legal for retail Indian residents** under FEMA — only INR-pairs on NSE/BSE. Margin FX with offshore brokers = FEMA violation. (T3: RBI Master Direction on Margin Trading; T2: liquidityfinder.com)

---

## 10. Prediction markets (Polymarket, Kalshi, etc.)

| Dim | Score | Note |
|---|---|---|
| Legality | **1** | **Banned for Indian residents** under the Promotion and Regulation of Online Gaming Act, 2025 (PROGA). MeitY blocked Polymarket. Funding via USDT off-ramp violates FEMA + PMLA. ISP-level blocks active. (T2: https://evaakil.com/polymarket-legal-status-in-india/ ; https://www.tradetheoutcome.com/is-polymarket-legal-in-india/) |
| All other dims | — | Not scored. Ruled out on legality. |

Indian-domiciled "opinion trading" apps (Probo etc.) were also shut down under PROGA. **Dealbreaker. Do not pursue.**

---

## 11. Tokenized stocks / synthetic assets (xStocks, dYdX synths, mirrored equities)

| Dim | Score | Note |
|---|---|---|
| Legality | 1 | These live on offshore DEXes or unregistered CEX wrappers. No FIU-registered Indian exchange offers them. Acquiring requires unapproved off-ramp. SEBI has explicitly warned against synthetic "stock tokens" (no formal circular saved here — T1, needs verification of latest SEBI press release). |
| Red flags | — | Counterparty risk (no underlying delivery), smart-contract risk, off-ramp = FEMA risk. **Dealbreaker.** |

---

## Summary score table

| # | Market | Liq | Fee | API | Min K | Reg | Lat | Agent-fit | Tax | **Sum** |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Equity delivery (NSE/BSE) | 5 | 3 | 5 | 5 | 3 | 4 | 4 | 3 | **32** |
| 1' | Equity intraday | 5 | 4 | 5 | 5 | 3 | 4 | 2 | 3 | 31 |
| 2a | Index options | 5 | 3 | 5 | 4 | 3 | 3 | 3 | 4 | **30** |
| 2b | Index futures | 4 | 4 | 5 | 2 | 3 | 3 | 3 | 4 | 28 |
| 2c | Stock options | 2 | 2 | 5 | 3 | 3 | 3 | 2 | 4 | 24 |
| 2d | Stock futures | 3 | 4 | 5 | 2 | 3 | 3 | 3 | 4 | 27 |
| 3 | MCX commodities | 3 | 4 | 5 | 3 | 3 | 4 | 4 | 4 | **30** |
| 4 | Currency derivs (INR) | 2 | 5 | 5 | 4 | 2 | 3 | 2 | 4 | 27 |
| 5 | Crypto FIU-Indian | 3 | 2 | 4 | 5 | 3 | 4 | 3 | 1 | 25 |
| 6 | Crypto offshore | — | — | — | — | — | — | — | — | **RULE OUT** |
| 7 | US equities LRS | 5 | 3 | 2 (Vested) / 5 (IBKR) | 4 | 3 | 1 | 4 | 3 | 25 / 28 |
| 8 | US options IBKR/GIFT | 3 | 3 | 5/1 | 4 | 4/2 | 1 | 5 | 2 | **needs legal verification** |
| 9 | True FX | — | — | — | — | — | — | — | — | **RULE OUT (FEMA)** |
| 10 | Prediction markets | — | — | — | — | — | — | — | — | **RULE OUT (PROGA)** |
| 11 | Tokenized synths | — | — | — | — | — | — | — | — | **RULE OUT** |

---

## Finalist recommendations

### Finalist #1 — **NSE index options (NIFTY + SENSEX weeklies) via Kite Connect**

**Why:**
- Highest liquidity of any India-accessible derivative; tightest spreads; LLM-agent can operate on 5-min to multi-day horizons where the fee/edge ratio is workable.
- Min capital: ~Rs 5–10k for a buy-only strategy on 1-lot OTM weeklies. Fits "very low capital."
- Kite Connect API is mature, official, well-documented, Rs 500/mo. Personal-API tier free.
- Tax is clean (non-speculative business, 8-yr loss carry-forward).
- Indian-server hosting requirement is satisfied trivially via AWS ap-south-1 with Elastic IP.

**Conditions / risks:**
- Fee structure means per-trade gross edge must exceed ~1% of premium just to break even — pushes the agent toward *positional* (hours-to-days) plays, not scalping. This is *fine* for an LLM agent (matches its native timescale).
- SEBI algo framework: confirm with Zerodha that self-developed white-box use is permitted under its registered umbrella (it currently is, but operational details still evolving).
- STT-on-exercise trap: never hold ITM options to expiry — close before 3:25 PM.

### Finalist #2 — **MCX commodity futures (crude mini, natgas mini, gold mini) via Kite Connect**

**Why:**
- Globally-driven, news-and-macro-sensitive markets where an LLM reading EIA reports, FOMC statements, geopolitics has natural informational edge.
- All-in fees ~1.5–2 bps RT — the cheapest derivative round-trip available to Indian retail.
- Min capital Rs 15–45k per lot (crude/natgas mini at the lower end) — fits low-capital constraint.
- Trades during US session overlap (5 PM–11:55 PM IST) means liquidity coincides with the news cycle.
- Same Kite API, same tax (non-speculative), same hosting story.

**Conditions / risks:**
- Liquidity in Indian morning hours (9–5 PM IST) is thinner; the agent should be silent then or use the mini contracts only.
- Avoid the physical-delivery period for commodities that have it (last week before expiry).

### Honorable mention — **NSE/BSE equity delivery (positional, multi-day)**

The slowest, safest sandbox for the very first live deployment. Fee per round-trip is higher (~22 bps), but capital is fully flexible, no margin, no expiry, and the failure modes are gentlest. **Recommended as the paper-trading and first-live-capital venue before graduating to options/commodities.**

---

## Explicitly ruled out for this user

1. **Crypto on offshore exchanges (VPN/foreign account)** — illegal/grey, FEMA + IT Act risk.
2. **Prediction markets (Polymarket, Kalshi, etc.)** — banned under PROGA 2025.
3. **Tokenized stocks / synthetic assets** — no legal acquisition path from India.
4. **True spot FX with offshore brokers** — FEMA violation.
5. **US options via Vested/INDmoney** — not offered; via LRS-funded IBKR options = derivative remittance bar applies.
6. **NSE currency derivatives as a primary venue** — vol crushed by managed float, attestation friction post-April 2024, no real LLM edge.
7. **Stock options (single-name)** — liquidity penalty kills algo execution at retail size.
8. **Equity intraday as the *primary* venue** — STT + speculative-income tax treatment + need-edge-> 8 bps per trade math makes it inferior to options/commodities for the agent timescale.
9. **HFT in any market** — out of scope per charter; LLM latency floor of 1–5 s rules it out structurally.

---

## Open verification items (for Phase 2)

- [ ] Exact orders-per-second threshold in current exchange operational notes that triggers per-strategy registration (NSE/BSE). T0 right now.
- [ ] Confirm IBKR India (SEBI-registered subsidiary) policy on retail Indian-resident options trading post-Apr 2026. T0.
- [ ] Confirm whether NSE IX Global Access permits US *options* for Indian residents under IFSCA rules. T0.
- [ ] Re-verify Budget 2026 STT figures on equity options (any change post 1 Apr 2026) against the live zerodha.com/charges page on the trading-day before going live.
- [ ] Measure actual ap-south-1 → kite.zerodha.com order-RTT (T4 target).
- [ ] Re-verify equity LTCG/STCG rates under Income Tax Act 2025 (Budget 2026 may have moved them).
- [ ] Confirm physical-delivery vs cash-settled list on current MCX contracts (FY26 changes).

---

## Sources index (T-scores in parens)

- (T3) SEBI Circular Feb 4 2025 — Safer participation of retail investors in algo trading. https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html
- (T3) SEBI Sept 30 2025 extension circular. https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html
- (T3) Zerodha official charges page (fetched & saved). https://zerodha.com/charges/
- (T3) Kite Connect docs. https://kite.trade ; https://zerodha.com/products/api/
- (T3) Zerodha margin calculator. https://zerodha.com/margin-calculator/Futures/  ; /Commodity/
- (T3) NSE F&O lot-size circular FAOP70616 (Jan 2026 revision). https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf
- (T3) NSE Clearing currency derivatives position limits. https://www.nseclearing.in/risk-management/currency-derivatives/position-limits
- (T3) IFSCA NRI/resident page. https://ifsca.gov.in/Pages/Contents/NRIs%20section
- (T3) CoinDCX API portal. https://coindcx.com/api/
- (T2) Delta Exchange India fees & API. https://www.delta.exchange/  ; https://www.bitget.com/academy/what-is-delta-exchange-2026-guide-to-crypto-derivatives-trading-in-india
- (T2) Moneylife — NSE IX Global Access launch coverage. https://www.moneylife.in/article/nse-ix-opens-direct-us-stock-trading-for-indians-sparks-regulatory-debate/79796.html
- (T2) ClearTax F&O/intraday tax guides. https://cleartax.in/s/fo-trader-return-filing  ; https://cleartax.in/s/income-tax-on-intraday-trading
- (T2) Lemonn F&O tax guide. https://lemonn.co.in/blog/fno/f-and-o-trading-taxation-guide/
- (T2) Sahi F&O tax FY26 guide. https://www.sahi.com/blogs/income-tax-on-f-and-o-trading-in-india-complete-guide-for-fy-2025-26
- (T2) Koinly India crypto tax. https://koinly.io/guides/crypto-tax-india/
- (T2) Winvesta — NASDAQ options India access. https://www.winvesta.in/blog/investors/nasdaq-options-trading-is-it-accessible-for-indian-investors
- (T2) Polymarket legality India. https://evaakil.com/polymarket-legal-status-in-india/  ; https://www.tradetheoutcome.com/is-polymarket-legal-in-india/
- (T1) AWS ap-south-1 latency community refs — needs T4 measurement.
- (T1) Various broker fee comparison pages — used only as cross-check against Zerodha primary.

Raw caches in `/Users/Nikhil-S/Projects/Trading/research/sources/raw/`:
- `2026-05-21_zerodha_charges.md`
- `2026-05-21_sebi_retail_algo_framework.md`
