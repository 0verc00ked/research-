# Paper-Trading & Sandbox Venues — Indian Retail (2026)

**Scope:** Honest assessment of every paper / sandbox environment an Indian solo operator can use to test agentic trading strategies. "API parity" means: same auth, same endpoints, same payload as live. "Data realism" means: real or near-real market quotes flowing in. "Fill realism" means: simulated order matching using actual order book vs. naive last-traded-price fills.

**Trust scoring** per `../trust_rubric.md`.

---

## Indian equity / F&O brokers

### Zerodha Kite Connect — NO real sandbox
- **Claim:** Zerodha does NOT offer a sandbox or paper-trading API endpoint (T3: Zerodha official support article "Does Zerodha offer an API sandbox environment?" — answer is explicitly "no"; T3: Kite Connect forum threads from Zerodha staff).
- **Workarounds:**
  1. Run your strategy code against live Kite WebSocket ticks but route order calls to a **local mock order book** you write yourself (most common pattern).
  2. Use Kite's historical-data API for backtests (rate-limited; T3: kite.trade/docs/connect/v3).
  3. Place tiny live orders (1 share, smallest option) and treat them as paper trades, eating actual fees.
- **API parity / realism:** N/A — there is no sandbox.
- **Free?** Kite Connect is **₹2,000/month** per app (T3: kite.trade pricing). Historical-data add-on extra. This matters: Zerodha is not free for algo dev.
- **Verdict:** Use Kite **only** when you've committed to live trading on Zerodha; don't use it for paper exploration.

### Upstox Sandbox — REAL sandbox, free, recommended
- **Claim:** Upstox provides a documented sandbox environment with a "New Sandbox App" flow on their developer portal, supporting order placement, modify, cancel; orders stay alive for 24 hours; switchable in SDK via a toggle (T3: upstox.com/developer/api-documentation/sandbox/).
- **API parity:** Same endpoint shape, same auth flow; just a different base URL / app key. SDK has a single config toggle. (T3: official docs.)
- **Data realism:** Sandbox includes simulated market data; quality vs. live is **not fully documented** — likely synthetic or delayed (T1; needs reproduction in Phase 4 hands-on test).
- **Fill realism:** "Mock fills" — not order-book matched. Slippage and partial-fill behavior is unrealistic (T1).
- **Free?** Yes. (T3.)
- **Verdict:** ✅ **Best free Indian sandbox for plumbing tests** (auth flow, error handling, retry logic). Do NOT use it to estimate P&L — fills are too clean.

### Dhan Sandbox — REAL sandbox, free, but limited
- **Claim:** "Dhan Sandbox" is a fully simulated environment; sign up at developer.dhanhq.co; no live Dhan account required (T3: dhanhq.co developer portal; T2: marketcalls article confirms launch).
- **API parity:** Same API shape as live; toggle by base URL / token. (T3.)
- **Data realism:** ⚠ **Quotes and websockets are NOT available in sandbox** (T3: official Dhan docs). You can simulate order flow but not market data — strategy must be fed quotes from elsewhere.
- **Fill realism:** ❌ **All orders fill at price ₹100 regardless of market** (T3: official Dhan docs). This is purely a logic-test environment, NOT a P&L test.
- **Capital:** Resets to ₹10,00,000 every morning automatically (T3).
- **Free?** Yes, forever (T3).
- **Verdict:** ✅ for testing order-state machine, position tracking, error handling. ❌ for any P&L estimate, slippage modeling, or strategy validation.

### Fyers — "Paper trading" via API Bridge (NOT a true sandbox)
- **Claim:** Fyers offers a paper-trading mode inside its **API Bridge** desktop tool (T2: fyers.in community thread). The bridge runs on user's PC and intercepts orders.
- **API parity:** Indirect — you talk to the bridge, not Fyers servers directly. Live-mode parity is the bridge's responsibility. (T1.)
- **Data realism:** Uses live Fyers feed (good).
- **Fill realism:** Naive — last-traded-price fills, no order book simulation (T1).
- **Free?** API itself is free (T3: fyers.in/products/api); bridge is part of Fyers Automate, which may have separate cost.
- **Verdict:** ⚠ Workable but the bridge layer adds operational complexity. Prefer Upstox/Dhan for pure sandbox testing.

### AngelOne SmartAPI — NO real sandbox
- **Claim:** No formal sandbox advertised; SmartAPI forum has active user requests for one as of 2024–25 (T2: smartapi.angelbroking.com forum threads).
- **Workaround:** Same as Zerodha — mock locally, or place 1-quantity live trades.
- **Free?** SmartAPI is free to use (T3: smartapi.angelbroking.com).
- **Verdict:** ❌ Not viable for paper testing. Use only if you've chosen AngelOne for live.

---

## US / global brokers

### Alpaca Paper Trading — accessible, excellent
- **Claim:** Alpaca offers free paper trading; account creation effectively automatic on signup; paper API is offered by AlpacaDB Inc. and requires no real money (T3: alpaca.markets/support).
- **India access:** Paper trading: **fully accessible** from India (no KYC barrier for paper accounts) (T3: alpaca.markets docs/account-plans). Live trading for Indian residents: now available in beta for non-US tax residents (T3: alpaca.markets/blog/non-us-live-trading-beta), but go-live requires LRS-compliant funding which complicates the path.
- **API parity:** Same endpoints, just different base URL (`paper-api.alpaca.markets`) (T3).
- **Data realism:** Real-time IEX data free, full SIP feeds paid. Quote quality is real, not synthetic. (T3.)
- **Fill realism:** Naive fills against NBBO — not full order-book sim, but better than ₹100-flat. Reasonable for swing/positional strategies; bad for sub-minute. (T2.)
- **Free?** Paper trading is fully free (T3).
- **Verdict:** ✅✅ **Best free paper environment for developing agentic strategy logic**, regardless of where you ultimately deploy live. Treat as your primary strategy-development sandbox even if live target is India.

### Interactive Brokers Paper Account — accessible, gold standard
- **Claim:** All IBKR clients get a paper trading account with full trading-feature parity (T3: ibkrguides.com/clientportal/papertradingaccount.htm). New individual account holders auto-receive one.
- **India access:** IBKR India offers paper accounts to all account holders (T3: interactivebrokers.co.in). Account opening required (KYC + INR funding for India markets, USD via LRS for US markets), but paper itself is free once account exists.
- **API parity:** TWS API and Client Portal API both available against paper account (T3).
- **Data realism:** Same market data as your live entitlements. Highest among options listed. (T3.)
- **Fill realism:** Best-in-class — IBKR's paper engine simulates against real order book (T2: widely corroborated). Closest to real execution of any retail paper venue.
- **Free?** Paper trading is free once you have an account; data subscriptions cost extra ($1.5–10/month per exchange) (T3).
- **Verdict:** ✅✅✅ **Highest realism**, but account opening and minimum activity friction is real. Best if you plan to use IBKR live anyway.

---

## Crypto

### Binance Spot Testnet — accessible, free
- **Claim:** testnet.binance.vision provides full Spot API testnet; auto-funded with multiple test assets on registration (T3: testnet.binance.vision).
- **India access:** Testnet has no KYC, accessible globally (T3). NB: Binance live is no longer FIU-registered in India for residents → testnet OK for learning, but you can't directly graduate to Binance live as a resident.
- **API parity:** Same as live Spot API. (T3.)
- **Data realism:** Synthetic order book; not the live Binance book. (T2.)
- **Fill realism:** Order-book simulated, but liquidity is thin and prices drift from real BTC/USDT. (T2.)
- **Free?** Yes (T3).
- **Verdict:** ✅ for API/code testing. ⚠ Don't trust P&L numbers — testnet prices diverge from mainnet.

### Bybit Testnet — accessible, free
- **Claim:** testnet.bybit.com provides full perp/spot testnet (T3: bybit-exchange.github.io/docs).
- **India access:** Same as Binance — no resident-trading-friendly path for live. Testnet open.
- **Same caveats** as Binance testnet.

### Delta Exchange India Testnet — accessible, free, FIU-friendly
- **Claim:** testnet.delta.exchange (India variant at `cdn-ind.testnet.deltaex.org`) (T3: docs.delta.exchange).
- **India access:** Delta is FIU-registered; live → testnet path is clean for Indian residents. **This is the only crypto venue where testnet-to-live is straightforward for an India resident.**
- **API parity:** Full (T3).
- **Data realism / fill realism:** Synthetic, similar caveats. (T2.)
- **Verdict:** ✅ **Best crypto sandbox for an Indian who actually plans to go live on crypto.**

### CoinDCX — NO public testnet/sandbox
- **Claim:** No documented public sandbox (T2: docs.coindcx.com only documents live endpoints).
- **Workaround:** Use Binance/Delta testnet for code-level testing, then switch to live CoinDCX with tiny order sizes.
- **Verdict:** ❌ for paper.

---

## Prediction markets

### Kalshi — official demo API
- **Claim:** Kalshi has a developer demo environment with mock funds and demo API root URL (T2: third-party blog corroborates; not surfaced in primary docs in this pass — needs WebFetch confirmation).
- **India access:** Kalshi live is US-only. Demo accessible via VPN-free signup (T1 — needs verification).
- **Verdict:** ⚠ Demo useful for code; live not legally accessible to India residents.

### Polymarket — NO official paper
- No official paper mode. Two third-party simulators exist:
  - **PolySimulator** (polysimulator.com): $1,000 virtual balance, real odds, no KYC. T1.
  - **PaperPoly** (paperpoly.app): tracks Brier score, calibration, P&L. T1.
- **India access:** Polymarket live access restricted under US OFAC/CFTC rules; in India, on-chain access via wallet is technically possible but in regulatory grey zone (T1).
- **Verdict:** ⚠ Third-party simulators OK for learning; do not trust them for strategy validation due to unverifiable fill/odds logic. Not recommended.

---

## Summary table

| Venue | Real sandbox? | API parity | Data realism | Fill realism | Free | India access | Trust |
|---|---|---|---|---|---|---|---|
| Zerodha Kite | ❌ | n/a | n/a | n/a | ₹2k/mo | ✅ | T3 (negative) |
| **Upstox Sandbox** | ✅ | High | Medium | Low | ✅ | ✅ | T3 |
| **Dhan Sandbox** | ✅ | High | ❌ (no quotes) | ❌ (₹100 flat fill) | ✅ | ✅ | T3 |
| Fyers API Bridge | ⚠ (local proxy) | Medium | High (live feed) | Low | ✅ | ✅ | T2 |
| AngelOne SmartAPI | ❌ | n/a | n/a | n/a | ✅ | ✅ | T2 (negative) |
| **Alpaca Paper** | ✅ | High | High | Medium | ✅ | ✅ | T3 |
| **IBKR Paper** | ✅ | High | High | High | Acct req'd | ✅ | T3 |
| Binance Testnet | ✅ | High | Low | Low | ✅ | ✅ (testnet) | T3 |
| Bybit Testnet | ✅ | High | Low | Low | ✅ | ✅ (testnet) | T3 |
| **Delta India Testnet** | ✅ | High | Low | Low | ✅ | ✅ | T3 |
| CoinDCX | ❌ | n/a | n/a | n/a | ✅ | ✅ | T2 (negative) |
| Kalshi Demo | ⚠ | High | High | ? | ✅ | ✅ (demo) | T1 |
| Polymarket | ❌ official | n/a | n/a | n/a | — | ⚠ | T0–T1 |

---

## Recommended paper-testing stack (for this user)

**Strategy development & logic testing:**
**Alpaca Paper** — best realism among free, fully open to Indians, instant signup, full API parity. Use this even though final live target may be Indian markets — the strategy code is portable.

**Indian-market plumbing (auth, lot sizing, India fees, holiday calendar):**
**Upstox Sandbox** — for testing the broker-integration layer specifically for NSE/BSE/MCX.
**Dhan Sandbox** — secondary; useful for testing order-state-machine but useless for P&L.

**Highest-fidelity validation before live:**
**IBKR Paper** — if user opens IBKR India account anyway, this is the gold-standard final-stage sim.

**Crypto (only if user pursues crypto):**
**Delta India Testnet** for code; then graduate to tiny live on Delta India (FIU-registered, India-compliant).

**Do not use for P&L validation:**
- Dhan ₹100 flat-fill
- Any third-party Polymarket simulator
- Zerodha "live tiny order" approximation (eats real fees)

---

## Source citations

- Zerodha support — "Does Zerodha offer an API sandbox environment?" — T3
- Kite Connect docs (kite.trade/docs/connect/v3) — T3
- Upstox developer docs (upstox.com/developer/api-documentation/sandbox/) — T3
- Dhan developer portal (developer.dhanhq.co; dhanhq.co/trading-apis) — T3
- Fyers community (fyers.in/community) — T2
- AngelOne SmartAPI forum threads — T2
- Alpaca docs & support (alpaca.markets/support) — T3
- IBKR paper docs (ibkrguides.com) — T3
- Binance Spot Testnet (testnet.binance.vision) — T3
- Delta Exchange API docs (docs.delta.exchange) — T3
- PolySimulator / PaperPoly (third-party, unverified) — T1
