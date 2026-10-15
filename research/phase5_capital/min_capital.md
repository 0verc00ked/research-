# Minimum Capital Landscape — India-Accessible Markets

**Scope:** Smallest rupee ticket required to place ONE legal, smallest-permissible live trade per market, plus a "soft" floor where fees stop dominating P&L. All figures are as of May 2026.

**Trust scoring:** see `../trust_rubric.md`. Citations inline. Prices fluctuate daily — re-verify before live deployment.

---

## 1. NSE F&O — Index Options (post-2024 lot reform)

### Current lot sizes (effective Oct 28, 2025; locked-in for monthly contracts from Jan 27, 2026)

| Index | New lot | Old lot | Source |
|-------|---------|---------|--------|
| NIFTY 50 | **65** | 75 | T3: SEBI circular SEBI/HO/MRD-PoD2/CIR/P/2024/00181 (Dec 30, 2024); NSE FAOP70616; Zerodha support page |
| BANKNIFTY | **30** | 35 | T3: same |
| FINNIFTY | **60** | 65 | T3: same |
| MIDCPNIFTY | **120** | 140 | T3: same |
| NIFTYNXT50 | **25** | unchanged | T3: same |
| BSE SENSEX | **20** | 10 (increased earlier round) | T3: BSE circular; Paytm Money blog (T2 corroborator) |
| BSE BANKEX | **30** | 15 | T3: same |
| BSE SENSEX50 | **75** | — | T3: Zerodha support (T2 on date; T3 on number) |

**Rationale:** SEBI's periodic-review mandate that notional contract value sit in the ₹15 lakh band (revised from earlier ₹5–10 lakh) (T3: SEBI Dec 2024 circular). Note: the Oct 2025 *reduction* is the second swing — SEBI first hiked lots in Nov 2024, then partially walked it back when notionals overshot.

### Hard minimum ticket — BUYING one option (cheapest live trade)

To **buy** a single OTM weekly call/put, you pay full premium upfront, no margin overhead.

| Instrument | Lot | Typical OTM premium (May 2026) | Hard minimum (premium × lot) |
|---|---|---|---|
| NIFTY weekly OTM | 65 | ₹5–20 (deep OTM, last day) | **₹325–1,300** |
| NIFTY weekly ATM | 65 | ₹100–200 | ₹6,500–13,000 |
| BANKNIFTY (monthly only now) ATM | 30 | ₹150–400 | ₹4,500–12,000 (T2: option-chain snapshots) |
| FINNIFTY ATM weekly | 60 | ₹80–150 | ₹4,800–9,000 |
| SENSEX weekly OTM | 20 | ₹5–20 | **₹100–400** ← lowest hard floor on Indian options |
| BANKEX | 30 | ₹100–300 | ₹3,000–9,000 |

**Lowest absolute hard minimum on Indian index options ≈ ₹150–400** (one deep-OTM SENSEX weekly call near expiry) (T2: BSE option-chain inspection; lot size T3).

⚠ Weekly contracts for SENSEX50 and BANKEX were *discontinued* (last expiries Nov 14 & Nov 18, 2024) per BSE/SEBI rationalisation (T2: 5paisa, Groww). Only **NIFTY** and **SENSEX** retain weekly expiries on a per-exchange basis (one each per week, post-SEBI Oct 2024 limit).

### Hard minimum — SELLING one option (requires margin)

Selling = SPAN + Exposure margin posted up front. For NIFTY at ~25,000 spot:
- Notional ≈ 25,000 × 65 = ₹16.25 L
- Initial margin ≈ 12–15% of notional ≈ **₹1.95–2.45 L per lot** (T2: Zerodha margin calculator; T3 on formula)

→ Option selling is **not** in the "very low capital" budget. Skip.

### Soft minimum (fees ≤ 5% of expected P&L)

Round-trip fixed cost on one option lot (Zerodha, T3 — `zerodha.com/charges`):
- Brokerage: ₹20 buy + ₹20 sell = ₹40
- STT (sell side, 0.05% of premium on options buy; 0.0625% on sell — verify post-Apr 2026 budget rates)
- Exchange txn + SEBI + stamp + 18% GST on brokerage/txn/SEBI ≈ ₹15–40 depending on premium

**All-in round trip ≈ ₹70–120 per option lot.**

For a strategy targeting say 20% return on premium paid, you need premium × lot ≥ **₹2,000–3,000** for fees to be <5% of P&L → soft minimum ≈ **₹3,000 deployed per trade**, capital ≈ **₹15,000–25,000** to allow position sizing and drawdown buffer.

---

## 2. NSE F&O — Index Futures (SPAN + Exposure)

| Contract | Lot | Spot (May 2026) | Notional | Initial margin (~12–15%) |
|---|---|---|---|---|
| NIFTY FUT | 65 | ~25,000 | ₹16.25 L | **₹1.95–2.45 L** |
| BANKNIFTY FUT | 30 | ~53,500 (T1: MunafaSutra May 2026 snapshot) | ₹16.05 L | ₹1.9–2.4 L |
| FINNIFTY FUT | 60 | ~24,500 | ₹14.7 L | ₹1.75–2.2 L |
| SENSEX FUT | 20 | ~83,000 | ₹16.6 L | ₹2.0–2.5 L |

**Hard minimum index-futures ticket ≈ ₹2 lakh.** Out of scope for very low capital. (T3: Zerodha SPAN calculator methodology; T2: live margin values fluctuate daily.)

Note: Zerodha varsity / older blogs that quote "₹1.2 L for NIFTY intraday" pre-date the SEBI Peak-Margin / Phase-IV upfront-margin regime; intraday MIS leverage on index futures is **gone** for retail since Sep 2021 — full NRML margin is required upfront (T3: SEBI Nov 2020 circular CIR/MRD/DP/45/2020).

---

## 3. NSE Cash Equity

- **No regulatory minimum lot.** 1 share = 1 trade.
- **Fee floor:** Zerodha equity delivery brokerage = ₹0; STT 0.1% buy + 0.1% sell; exchange txn ~0.00297%; SEBI ₹10/crore; stamp 0.015% buy; DP charge ₹13.5+GST per scrip on sell-side (CDSL) (T3: zerodha.com/charges).
- Intraday MIS: ₹20 or 0.03% (lower), plus STT 0.025% sell side.
- **Practical floor:** DP charge of ~₹15.93 on each sell makes any delivery sell <₹3,000 unviable (fee > 0.5%). For intraday, fixed ₹40 brokerage round-trip → trade size should be ≥ ₹5,000 to keep brokerage <1%.
- **Hard minimum:** ₹100 (price of cheapest liquid stock × 1).
- **Soft minimum capital:** ₹10,000–25,000 for any diversification + fee headroom.
- (T3: Zerodha charges page; SEBI circular on STT)

---

## 4. MCX — Mini Commodity Contracts

| Contract | Lot | Approx. price (May 2026) | Contract notional | Initial margin (~10%) | Hard minimum |
|---|---|---|---|---|---|
| **Gold Mini** | 100 g | ₹95,000 / 10g | ₹9.5 L | ₹85k–₹1.0 L | **~₹85,000** |
| **Silver Mini** | 5 kg | ₹95,000 / kg | ₹4.75 L | ₹40k–₹55k | **~₹45,000** |
| Gold Petal | 1 g | ₹95,000 / 10g | ₹9,500 | ₹900–1,200 | **~₹1,000** ← cheapest MCX entry |
| ~~Crude Oil Mini~~ | DISCONTINUED — Crude Oil Mini removed by SEBI/MCX (T2: Zerodha varsity / Aliceblue). Only standard Crude Oil (100 bbl, notional ~₹6 L, margin ~₹65k) remains. | | | | |

**Cheapest legal MCX live ticket:** **Gold Petal** — ~₹1,000 margin (T2: broker margin calculators; T3: MCX contract spec). Liquidity is OK but spreads wider than mini.

(T2 overall — figures move daily; T3 on lot specs from MCX contract circulars.)

---

## 5. Crypto (FIU-registered exchanges, India)

### CoinDCX (T2/T3)
- Spot trading: **no minimum deposit**; minimum withdrawal ₹500 (T3: CoinDCX docs).
- Per-trade minimum order: typically **₹100–₹500 INR-quoted** for major pairs (T2: corroborated by Mudrex/CoinDCX FAQ pages; not crisply documented).
- Futures (CoinDCX Futures): margin-based, minimum notional varies per contract.
- API: REST + websocket, JSON-bodied POST auth (T3: docs.coindcx.com).
- **Tax overhead:** 30% flat on gains + 1% TDS per trade (Indian Finance Act 2022) (T3) — this is the real killer for high-frequency crypto strategies; TDS alone eats 1% per round trip.

### Mudrex (T2)
- Same FIU-PMLA regime. Min order ~₹100 INR-quoted on most pairs.
- API less mature than CoinDCX.

### Delta Exchange India (T3)
- Crypto **derivatives** (perp futures, options) FIU-registered Indian entity.
- Margin-based; smallest contracts are ~$10 notional (well under ₹1,000).
- Has a **testnet** (see paper_testing.md).

**Hard minimum live crypto ticket:** **~₹100** (one INR-quoted spot buy on CoinDCX/Mudrex) (T2).
**Soft minimum capital:** ~₹5,000–10,000 (to absorb 1% TDS + 30% tax + spread).

⚠ The 1% TDS on every sell makes crypto **structurally unfit for any strategy doing >50 round trips/year** — TDS alone burns 50% of capital before tax, even if every trade is breakeven. Slow-horizon only.

---

## 6. US Equities (LRS route)

### INDmoney (T3: IFSCA GAP at GIFT-IFSC)
- Fractional shares from **$1** (~₹85).
- Zero account fee, FX spread + GIFT-IFSC fees apply (~50–80 bps round trip).
- LRS ceiling: $250,000/FY per resident; TCS 20% above ₹10 L remitted in a FY (T3: RBI LRS circular; Finance Act 2023).

### Vested (T3: SEBI registered, IFSCA partner)
- Fractional from **$1**.
- Similar fee structure; FX spread is the dominant cost.

**Hard minimum:** **~₹85 ($1)** (T3: INDmoney/Vested product pages).
**Soft minimum capital:** ₹10,000+ to make FX spread tolerable. **API access for retail is essentially zero** — both are app-only with no public algo-trading API. → Not actionable for an agentic system.

### IBKR India (T3)
- ₹6–20/order Indian markets; for US markets, commissions in USD.
- **Has TWS API + Client Portal API**, fully usable from India for global products.
- Account opening: requires ~$0 minimum (was $10k, dropped), but funding for US trading via LRS.
- This is the only **API-accessible** US/global route from India for retail.

**Hard minimum ticket:** $1 (fractional via IBKR Pro for US stocks) (T3).
**Soft minimum capital:** ₹50,000+ to amortize FX/wire costs.

---

## Summary Table — Hard & Soft Minimums

| Market / instrument | Hard min ticket | Soft min capital | API? | Worth it for "very low capital"? |
|---|---|---|---|---|
| SENSEX weekly OTM option (buy) | ₹150–400 | ₹15k | Yes (Zerodha/Upstox/Dhan etc.) | ✅ cheapest live entry on Indian options |
| NIFTY weekly OTM option (buy) | ₹325–1,300 | ₹20k | Yes | ✅ deepest liquidity |
| NSE cash equity | ₹100 (1 share) | ₹15k | Yes | ✅ but no leverage; slow |
| MCX Gold Petal future | ~₹1,000 margin | ₹15k | Yes | ✅ underrated, low capital |
| MCX Silver Mini | ~₹45k margin | ₹75k | Yes | ❌ too large |
| Crypto spot (CoinDCX) | ₹100 | ₹10k | Yes | ⚠ killed by 1% TDS unless slow |
| Delta India crypto perps | ~₹500 margin | ₹10k | Yes | ⚠ same TDS issue, plus 30% on gains |
| US fractional (INDmoney/Vested) | ₹85 ($1) | ₹10k+ | ❌ no retail API | ❌ not actionable |
| US/global via IBKR | $1 | ₹50k | ✅ TWS API | ⚠ overkill for ₹small capital |
| Index futures (any) | ₹1.9–2.5 L | ₹5 L | Yes | ❌ way over budget |
| Option selling (any) | ₹1.9–2.5 L | ₹5 L | Yes | ❌ same |

---

## Concrete recommendation — cheapest viable LIVE start

**Tier-0 (sub-₹5k experimentation):**
- **SENSEX weekly deep-OTM option BUY** on Zerodha/Upstox/Dhan. ~₹200–500 per ticket. Fees ≈ ₹70 round trip → fees swallow 15–35% of any move; statistical noise dominates. Useful only as plumbing test, NOT for measuring edge.

**Tier-1 (₹15,000–25,000 — recommended floor for measurable edge):**
- **NIFTY weekly options BUY** (₹500–2,000 per ticket) + 1–2 lots position sizing. Fee burden drops to ~3–5% of ticket. This is where a strategy can actually show statistical signal vs. noise.
- Alternative: **MCX Gold Petal** (₹1,000–1,500 per lot) for slower-horizon trend/macro plays.

**Tier-2 (₹50,000+ — real edge measurement):**
- Multi-leg options (defined-risk spreads), Gold Mini, equity swing trading with diversification.

---

## Rupee-floor opinion (load-bearing)

**Do NOT recommend live deployment below ₹15,000.**
Below this, per-trade fees + STT + slippage are so large vs. ticket size that even a genuinely edge-positive strategy will look like noise — the user cannot tell skill from luck, which defeats the entire purpose of the live test. Paper trade until at least ₹15k of risk capital is set aside; treat anything below as "plumbing-only" runs.

Justification: a typical buy-side option ticket of ₹2,000 with ₹80 round-trip fee = 4% fee drag. At ₹15k capital with ~5–7 simultaneous positions of ₹2k each, fee drag is bearable and position sizing is meaningful. Below that, fee drag exceeds plausible per-trade edge.

---

## Source citations

- SEBI circular SEBI/HO/MRD-PoD2/CIR/P/2024/00181, Dec 30, 2024 (lot-size revision) — T3
- NSE circular FAOP70616 (lot-size implementation) — T3
- BSE circulars on SENSEX/BANKEX lot revision — T3
- Zerodha charges page (zerodha.com/charges) — T3
- Zerodha margin calculator (zerodha.com/margin-calculator/) — T3 methodology, T2 daily numbers
- Zerodha support — lot sizes article (support.zerodha.com) — T3
- RBI LRS circular + Finance Act 2023 (TCS) — T3
- CoinDCX API docs (docs.coindcx.com) — T3
- Delta Exchange API docs (docs.delta.exchange) — T3
- MunafaSutra option-chain snapshots (May 2026) — T1 corroborative only
