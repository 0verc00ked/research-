# Dossier — marketcalls/openalgo  ⭐ India-critical

- **URL:** https://github.com/marketcalls/openalgo
- **Stars / Forks:** 1,902 / 906
- **Last push:** 2026-05-20 (very active)
- **Created:** 2024-02
- **License:** AGPL-3.0
- **Maintainer:** Rajandran R / Marketcalls (well-known Indian algo-trading educator, YouTube channel, docs.openalgo.in). Multi-contributor. T3 identity-wise.

## Stack
Python Flask + React 19. SQLite. PyPI package (`openalgo`). Python 3.11–3.14.

## Broker coverage (**30+ Indian brokers**, T3: README enumerated list)
5paisa, AliceBlue, AngelOne, Compositedge, Definedge, Delta Exchange (crypto), Dhan (+Sandbox), Firstock, Flattrade, Fyers, Groww, IBulls, IIFL, Iiflcapital, Indmoney, JainamXTS, Kotak Neo, Motilal Oswal, Mstock, Nubra, Paytm Money, Pocketful, RMoney, Samco, Shoonya (Finvasia), Tradejini, Upstox, Wisdom Capital, Zebu, Zerodha.

This is **the only OSS abstraction layer with broad Indian broker coverage** I found in the search.

## Architecture
Four product surfaces over one broker session (T3: README table):
1. **Unified Broker API** (`/api/v1/`) — TradingView/Amibroker/Excel/N8N webhooks.
2. **Python Strategy Host** (`/python`) — in-browser scheduler.
3. **Flow** — no-code drag-drop.
4. **Options Trading Suite** (`/tools`) — Strategy Builder, Option Chain, IV smile, Max Pain, Vol Surface, GEX, OI tools.

**Sandbox engine** with ₹1 Cr simulated capital and exchange-aligned auto square-off — closest thing to a paper-mode in Indian-broker land.

## Backtest evidence
Not the primary surface. Sandbox is forward-paper, not historical backtest. Pair it with qlib/backtrader/vectorbt upstream.

## Red flags
- 174 open issues (active project gravity, not abandonment).
- Marketcalls runs paid courses — vendor model is courses+free-tool, not signal-selling. Acceptable.
- AGPL-3.0: if you ever expose the API to others over network, you must open-source your derivative. **For solo use this is fine.**
- No P&L screenshots, no "guaranteed returns" language — clean.

## Trust score: **T3**
Real maintainer with public identity, real broker integrations (each broker module is testable independently), large community.

## Verdict: **Use as base** for Indian-broker execution leg.
This is the leading candidate for the execution/risk layer in any India-focused stack. Pair with:
- qlib or vectorbt for backtest/research
- TradingAgents-style multi-agent layer above as the signal generator
- openalgo Sandbox for paper-forward before going live.
