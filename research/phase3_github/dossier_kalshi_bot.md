# Dossier — ryanfrigo/kalshi-ai-trading-bot

- **URL:** https://github.com/ryanfrigo/kalshi-ai-trading-bot
- **Stars / Forks:** 414 / 160
- **Last push:** 2026-04-27
- **License:** MIT
- **Maintainer:** Individual (@ryanfrigo). T1 identity.

## Stack
Python 3.12+. Kalshi REST + key-signing, SQLite, Streamlit dashboard. OpenRouter for any LLM.

## Architecture
- Signed API client + market-data ingestion + position tracking.
- Three example strategies (one LLM-driven directional, one "safe-compounder" edge-based, one other).
- Strict separation of paper vs live (`--paper`).

## Backtest evidence
Disclaimer (verbatim, T3 of-author honesty): *"No strategy in this repo is guaranteed to make money. The examples lose money on certain markets."* This is rare and signals adult ownership.

## India relevance
**Kalshi is US-only** (KYC requires US ID). Inaccessible to Indian residents.

## Red flags
None. Modest tone, honest disclaimer, no signal-selling.

## Trust score: **T2**

## Verdict: **Reference for pattern.** The toolkit-not-turnkey framing + explicit "examples lose money" is the model honest open-source trading projects should follow. The Kalshi venue is closed to the user, but the structure is reusable for any prediction-market integration.
