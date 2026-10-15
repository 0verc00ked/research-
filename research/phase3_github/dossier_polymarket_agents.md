# Dossier — Polymarket/agents

- **URL:** https://github.com/Polymarket/agents
- **Stars / Forks:** 3,533 / 787
- **Last push:** 2024-11-05
- **Status:** **Archived** (read-only on GitHub)
- **License:** MIT
- **Maintainer:** Polymarket (official org). T3 identity.

## Stack
Python 3.9. Local + remote RAG. LangChain. News + betting odds providers.

## Architecture
Reference scaffolding: market data fetch → RAG over news → LLM prompt → bet sizing → submit via Polymarket CLOB API. Not a complete system — explicitly "developer framework and utilities."

## Backtest evidence
None.

## India relevance
**Polymarket is geo-blocked for Indian users** (US/UK/AU/SG/Polish + many others restricted; Indian residents fall under the broad block). Even if accessible, INR-to-USDC ramps + LRS reporting are heavy for low-capital.

## Red flags
- Archived in 2024 — abandoned official path; community forks proliferate including grift ones (search results show many `polymarket-btc-5min-arbitrage-bot` repos with copy-paste descriptions and zero substance).

## Trust score: **T1** (T3 for org identity, T0 for any production-readiness).

## Verdict: **Reference only.** Prediction-markets are intellectually attractive for slow-horizon LLM agents but currently inaccessible for an Indian solo operator. Pattern to steal: the news-RAG-to-bet-sizing pipeline.
