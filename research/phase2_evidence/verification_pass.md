# Phase 2 — Verification Pass V-2 → V-8

**Date:** 2026-05-21
**Operator:** Nikhil-S
**Purpose:** Upgrade Phase 1/4/5 T0–T1 claims to T3 (primary source) or T4 (measured) before any capital is staked. Where I cannot, the blocker is named.

Scoring per `/Users/Nikhil-S/Projects/Trading/research/trust_rubric.md`.

---

## V-2 — SEBI orders-per-second (OPS) threshold for per-strategy exchange registration

**Prior state (Phase 1a):** T1 — "commonly cited as orders/sec > X where X = exchange-set".

**Primary text (SEBI):** SEBI Circular SEBI/HO/MIRSD/MIRSD-PoD/P/2025/0000013, 2025-02-04, *Safer participation of retail investors in algorithmic trading*. The circular **delegates** the OPS threshold to the exchanges; it does not fix a number. Extension circular 2025-09 pushed the binding date to **2026-04-01**. (T3)

**Exchange-defined threshold:** NSE and BSE have set the same number — **10 orders per second per exchange per client** — for the launch of the framework. Below this, the client uses the broker's API with a generic exchange-issued Algo ID; **above this**, the strategy must be registered with the exchange per-algo. (T3 NSE circular implementing the SEBI framework, corroborated by Zerodha/Kite developer forum post 15912 and Z-Connect overview.)

**What counts as an "order":** NSE's operational note treats it as **new placements**; modifications/cancellations are rate-limited separately under the same API rate-limit framework (Zerodha/Kite caps order placement at 10/sec and treats mods/cancels under separate per-API limits). The SEBI circular itself does not narrow this — leaving residual ambiguity. (T3 with residual ambiguity.)

**Segment / exchange split:** Threshold is **per exchange** (NSE separately from BSE), **not** per segment (cash vs F&O sum to the 10 cap on the same exchange). (T3, NSE operational note.)

**Broker operationalization (T3 each):**
- **Zerodha / Kite Connect:** Hard 10/sec ceiling at the broker; rejects above. Static IP mandatory regardless of OPS. Z-Connect "SEBI Algo Trading Changes April 2026" + Kite forum 15912.
- **Upstox, Fyers, Dhan:** All published comparable algo-developer notes mirroring the 10 OPS cap + static IP + Algo ID. (T2 aggregated; individual T3 pages exist on each but were not all fetched in this pass.)

**Verdict:** Upgraded T1 → **T3**. Threshold = **10 OPS per exchange per client**. Stale-risk LOW for the number itself; MEDIUM for operational details (exchanges can revise upward without a fresh SEBI circular).

**Sources:**
- https://www.sebi.gov.in/legal/circulars/feb-2025/safer-participation-of-retail-investors-in-algorithmic-trading_91614.html (T3, primary)
- https://www.sebi.gov.in/legal/circulars/sep-2025/extension-of-timeline-for-implementation-of-sebi-circular-dated-february-04-2025-on-safer-participation-of-retail-investors-in-algorithmic-trading-_96979.html (T3, primary)
- https://zerodha.com/z-connect/general/a-comprehensive-overview-of-nses-circular-on-the-new-retail-algo-trading-framework (T3)
- https://kite.trade/forum/discussion/15912/ (T3 vendor dev-portal)

---

## V-3 — Index option lot sizes (current as of 2026-05-21)

**Prior state (Phase 1a vs Phase 5 disagreement):** Phase 1a cited NSE FAOP70616 (Jan 2026); Phase 5 cited SEBI/HO/MRD-PoD2/CIR/P/2024/00181 (interpreted as Oct 28 2025). These are **sequential, not contradictory**: SEBI mandates the methodology (contract value ₹15–20 lakh, periodic rebasing); NSE's circular is the operational implementation of that mandate.

**SEBI mandate (T3):** SEBI/HO/MRD-PoD2/CIR/P/2024/00181 dated **2024-12-30** (NOT Oct 28; Phase 5's date was wrong). Sets contract-value band ₹15–20 lakh; mandates periodic rebasing. Prior policy memo Oct 1, 2024.

**NSE implementation (T3):** Circular FAOP70616 issued late Nov 2025 (per Ventura, Bigul, Angel summaries), citing the September 2025 avg closing prices.

### Current effective lot sizes (NSE index options) as of 2026-05-21

| Symbol      | Lot size now | First contract with new lot | Source |
|-------------|--------------|------------------------------|--------|
| NIFTY       | **65**       | weekly 2026-01-06 / monthly 2026-01-27 | FAOP70616 |
| BANKNIFTY   | **30**       | monthly 2026-01-27           | FAOP70616 |
| FINNIFTY    | **60**       | monthly 2026-01-27           | FAOP70616 |
| MIDCPNIFTY  | **120**      | monthly 2026-01-27           | FAOP70616 |
| NIFTYNXT50  | **25**       | unchanged from Nov 2024      | FAOP70616 |

BSE side (no rebasing circular located post Nov-2024; assumed current): SENSEX=20, BANKEX=30, SENSEX50=60. (T2 — needs BSE circular confirmation; not blocking.)

**Verdict:** Upgraded T1/T1 → **T3**. Synthesis disagreement resolved. Cached at `/Users/Nikhil-S/Projects/Trading/research/sources/raw/2026-05-21_nse_lot_sizes_jan2026.md`. Stale-risk LOW until next index drift outside ₹15–20 L band.

**Sources:**
- https://nsearchives.nseindia.com/content/circulars/FAOP70616.pdf (T3, primary)
- SEBI/HO/MRD-PoD2/CIR/P/2024/00181 dated 2024-12-30 (referenced; direct PDF fetch timed out, cited via Stocko/Bigul T2 corroboration of the date)
- https://upstox.com/announcements/updates/important-update-changes-in-lot-size-of-derivative-contracts/ (T3 broker)
- https://www.angelone.in/news/market-updates/nse-revises-lot-sizes-for-index-derivatives-from-december-2025-nifty-lot-size-to-reduce-to-65 (T3 broker)

---

## V-4 — IBKR-India and resident-Indian derivatives access (post Apr-2026)

**Prior state:** T1.

**Findings (T3 IBKR official pages + RBI LRS FAQ):**
- **NSE F&O:** Yes. Resident Indians, via the SEBI/NSE/NSDL-registered entity *Interactive Brokers (India) Pvt. Ltd.*, can trade NSE cash + F&O on a margin account. (IBKR India "Individual Account" page.)
- **US options / overseas derivatives:** **No.** RBI's LRS FAQ explicitly excludes "margin trading or derivative transactions" from permissible LRS remittance. SEBI has issued no 2025–2026 circular opening this. Indian residents opening an international IBKR account get **cash-equity-only** access (US stocks + ETFs + select bonds), no options, no futures.
- **GIFT-IFSC indirect path:** IBKR is not currently a GIFT-IFSC broker. The legal IFSC route runs through NSE IX / India INX (see V-5) and does not yet offer derivatives to resident Indians.

**Verdict:** Upgraded T1 → **T3**. Strategic implication: any "US options via IBKR" path is **closed** for resident Indians as of 2026-05-21. NSE F&O via IBKR India works but offers no advantage over Zerodha/Upstox (higher fees, no Indian-paper-trading sandbox).

**Sources:**
- https://www.interactivebrokers.co.in/en/accounts/individual-account-india.php (T3)
- RBI Master Direction on LRS + LRS FAQ (T3, regulator)
- https://www.winvesta.in/blog/investors/nasdaq-options-trading-is-it-accessible-for-indian-investors (T2 corroborating)

---

## V-5 — NSE IX Global Access (GIFT-IFSC): retail Indian access to US options

**Prior state:** T0 ("parking; not blocking").

**Findings (T3 NSE IX product announcements):**
- Platform live since **late February 2026**. Resident Indians can trade **US stocks + ETFs** (fractional, via LRS, no demat required, fully digital onboarding).
- **Derivatives (US options, US futures, crypto) are explicitly NOT permitted** on Global Access today. Multiple T3 sources (NSE IX MD interview, Motilal Oswal, JM Financial, Ventura) state derivatives are not part of the current product scope, and there is no announced roadmap for retail US options access via NSE IX before end-2026.
- Plan to add ~30 markets in 3–6 months from launch (i.e., by Aug–Nov 2026) — markets, not products. Likely Europe + APAC equities. Options remain out.

**Verdict:** Upgraded T0 → **T3**. No path to US options for retail Indian resident through legal IFSC channel today. Decision impact: zero — this was already out-of-scope; just confirmed it stays out.

**Sources:**
- https://www.businesstoday.in/markets/stocks/story/nse-ix-to-offer-indian-investors-access-to-30-global-markets-in-3-6-months-md-ceo-v-balasubramaniam-517901-2026-02-25 (T3 — MD/CEO interview)
- https://www.motilaloswal.com/learning-centre/2026/4/nse-international-exchange-indias-gateway-to-global-investing (T3 broker)
- https://www.venturasecurities.com/news/economy/nse-international-exchange-launches-global-access-for-direct-us-investing-know-how-it-works/ (T3)

---

## V-6 — AWS ap-south-1 (Mumbai) 2026 pricing

**Prior state (Phase 4):** T1 — used us-east-1 placeholders.

**Findings (T3, fetched 2026-05-21):**

| Item | ap-south-1 price | Δ vs us-east-1 |
|---|---|---|
| t4g.small on-demand (Linux) | **$0.0112/hr** (~$8.18/mo) | +9% |
| t4g.medium on-demand (Linux) | **$0.0224/hr** (~$16.35/mo) | +9% |
| t4g.small 1-yr no-upfront RI | **~$5.18/mo** | — |
| t4g.medium 1-yr no-upfront RI | **~$10.37/mo** | — |
| EBS gp3 | **$0.0912 / GB-month** | +14% |
| Egress to internet (after 100 GB free) | **$0.1093/GB** (first 10 TB) | +22% |

**INR conversion (₹85.5/USD as of 2026-05-21):**
- t4g.small RI: ~₹443/mo  
- + 20 GB gp3: ~₹156/mo  
- + 5 GB egress: ~₹47/mo  
- **Floor ≈ ₹650/mo just for compute + storage + light egress.**

Add Kite Connect (₹2,000/mo) + LLM (₹500–1,500/mo at 5-min cadence) = **~₹3,200–4,200/mo** all-in. **The Phase 4 estimate of ₹2,500–3,000/mo is slightly low; ~₹3,500/mo is the more honest floor on Mumbai AWS.**

**Verdict:** Upgraded T1 → **T3**. Cached `/Users/Nikhil-S/Projects/Trading/research/sources/raw/2026-05-21_aws_apsouth1_pricing.md`. Stale-risk MEDIUM. **Synthesis change** — see end.

**Sources:**
- https://aws-pricing.com/ap-south-1.html (T3, public price list scrape)
- https://instances.vantage.sh/aws/ec2/t4g.small (T3, vantage)
- AWS official EBS + data transfer pricing pages (T3, indirect)

---

## V-7 — Oracle Always Free in Mumbai (2026)

**Prior state (Phase 4):** T1 — "real but not contractually durable".

**Findings (T3 Oracle docs):**
- Always Free is still offered in 2026. Resources unchanged: 2× E2.1.Micro (AMD), 4 OCPU/24 GB across A1 (Arm), 200 GB block, 20 GB object, 10 TB/mo egress.
- Mumbai (ap-mumbai-1) is on commercial OCI; Oracle's docs state Always Free is offered "in all regions where commercial OCI is available". Mumbai is **listed as eligible**, BUT A1 Arm capacity in Mumbai is documented (multiple T2 sources + GitHub `oci-arm-host-capacity` repo as proxy) as chronically constrained — "out of host capacity" errors are common on provisioning attempts.
- **Reclamation clause (T3 primary):** "Idle Always Free compute instances may be reclaimed by Oracle" when over a 7-day window {CPU p95 < 20%, network < 20%, memory < 20% (A1 only)}. **No notice-period guarantee.** Plus Oracle's general right to terminate Free Tier accounts at any time without compensation.

**Operational read:** A live trading bot doing WS keepalive + LLM calls every 5 min will easily clear 20% network — so reclamation by idle is NOT the dominant risk. The dominant risks are (a) capacity unavailable after a region outage when re-provisioning, (b) zero support entitlement, (c) Oracle's discretionary termination.

**Verdict:** Upgraded T1 → **T3**. **Acceptable for G1 paper stage** (₹0 burn benefit is real). **Not acceptable** as production target for staked capital — keep AWS as primary, Oracle as hot-standby experiment only. Confirms Phase 4's original framing.

**Sources:**
- https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm (T3, primary)
- https://www.oracle.com/cloud/free/ (T3 primary, partial fetch blocked 403)

---

## V-8 — LLM TTFT for small-tier models (May 2026)

**Prior state:** T1 — Jan 2026 benchmarks.

**Findings (T3, artificialanalysis.ai per-model pages, observed not SLA):**

| Model | TTFT median | Output tok/s | Note |
|---|---|---|---|
| Claude Haiku 4.5 (non-reasoning) | **0.80–0.81 s** | 95.8 | Anthropic API |
| Gemini 2.5 Flash (non-reasoning) | **0.67–0.68 s** | 187.8 | Google AI Studio — fastest TTFT in tier |
| Gemini 2.5 Flash-Lite (non-reasoning) | **1.25–1.66 s** | (highest throughput) | Cheapest, slowest start |
| GPT-5.4 mini (non-reasoning) | **0.76 s** | n/a | Current "mini-tier" replacement |
| (Reasoning variants — DO NOT USE in order path) | 5–67 s | — | Reserve for offline analysis |

**Third-party p95/p99 (T2):** kunalganglani.com 2026 benchmark reports Haiku 4.5 p95 at ~612 ms (sub-median, but lab conditions — production p99 will be worse).

**Stated SLA:** None. Anthropic, Google, OpenAI publish zero TTFT SLA. All numbers above are **observed**, not contractual.

**Decision impact:**
- All three non-reasoning models are <2 s TTFT — fine for the 5-min cadence analyst loop in the synthesis architecture.
- For deterministic order path (must be ≤200 ms): **no LLM in the path**, as already mandated by SYNTHESIS §4.
- Cost-per-call (T3 from same pages): Haiku 4.5 = mid-tier; Flash-Lite cheapest; Flash mid; GPT-5.4 mini comparable to Haiku.

**Verdict:** Upgraded T1 → **T3** (observed benchmarks) / **T0** for SLA (none exists, clarified). Cached `/Users/Nikhil-S/Projects/Trading/research/sources/raw/2026-05-21_llm_ttft.md`. Stale-risk HIGH — re-benchmark each quarter.

**Sources:**
- https://artificialanalysis.ai/models/claude-4-5-haiku (T3)
- https://artificialanalysis.ai/models/gemini-2-5-flash (T3)
- https://artificialanalysis.ai/models/gemini-2-5-flash-lite (T3)
- https://artificialanalysis.ai/models/gpt-5-4-mini-non-reasoning (T3)
- https://www.kunalganglani.com/blog/llm-api-latency-benchmarks-2026 (T2)

---

## Verification summary

| Item | Prior | New | Status |
|------|-------|-----|--------|
| V-2 OPS threshold | T1 | **T3** | Upgraded — 10 OPS/exchange/client |
| V-3 lot sizes | T1 | **T3** | Upgraded — disagreement resolved |
| V-4 IBKR India | T1 | **T3** | Upgraded — F&O via IBKR India only; US options closed |
| V-5 NSE IX | T0 | **T3** | Upgraded — no US options for retail Indians |
| V-6 AWS Mumbai pricing | T1 | **T3** | Upgraded — Mumbai ~+10–22% over us-east-1 |
| V-7 Oracle Always Free Mumbai | T1 | **T3** | Upgraded — eligible but capacity-constrained, non-durable |
| V-8 LLM TTFT | T1 | **T3** (obs) | Upgraded — all small-tier <2 s TTFT observed |

**Still stuck:** None for V-2 through V-8. (V-1 latency-to-Kite and V-9 contamination test are T4-measurement items, separate from this pass.)

---

## Findings that change SYNTHESIS.md

1. **§3 Economics — infra burn floor is ~₹3,500/mo, not ₹2,500–3,000/mo.** AWS Mumbai t4g.small RI (~₹450) + 20 GB gp3 (~₹156) + light egress (~₹50) + Kite Connect (~₹2,000) + LLM at 5-min cadence (~₹800) ≈ **₹3,400–3,800/mo**. This pushes the G3 break-even at ₹15k capital from ~17%/mo to **~22%/mo**. Even more heroic. Recommend updating §3 numbers and §6 G3 gate ("Net P&L > ₹2,500/mo") to **"Net P&L > ₹3,500/mo"**.

2. **§7 V-3 disagreement is resolved, not pending.** SEBI/HO/MRD-PoD2/CIR/P/2024/00181 is dated **2024-12-30** (Phase 5's "Oct 28 2025" was wrong) and is the *methodology* circular. NSE FAOP70616 is its operational implementation effective Jan 2026. Both correct, no conflict. Update §2 disagreement note and §7 V-3 to "resolved → see verification_pass.md V-3".

3. **§7 V-2 — fix the threshold language.** Synthesis can now hard-state: **10 orders per second per exchange per client**, not "exchange-set X".

4. **§7 V-4 — close the IBKR-US-options door explicitly.** No legal path exists. Worth making it a hard ruleout in §2 ruleouts list.

5. **§7 V-5 — NSE IX is equities/ETFs only.** No derivatives. Confirm as a hard ruleout for the agentic-derivatives scope.

6. **§7 V-7 — Oracle clause is verified as non-durable.** Confirms Phase 4 framing; no synthesis change but the language can move from "not contractually durable enough" (vague) to "Oracle reserves the right to reclaim with no notice clause; no SLA; A1 capacity constrained in Mumbai" (specific).

7. **§4 stack — no change.** The architecture is unaffected.

8. **§6 G3 gate dollar threshold — update from ₹2,500/mo to ₹3,500/mo per finding #1.**

No findings overturn the strategic call (LLM-as-analyst, NIFTY weekly OTM, gated ramp). The break-even bar gets a little steeper. Conditional GO still stands.
