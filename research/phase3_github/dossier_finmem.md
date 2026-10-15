# Dossier — pipiku915/FinMem-LLM-StockTrading

- **URL:** https://github.com/pipiku915/FinMem-LLM-StockTrading
- **Stars / Forks:** 897 / 193
- **Last push:** 2024-08-18 (stale)
- **License:** MIT
- **Maintainer:** Authors of arXiv:2311.13743 (Yu et al., Stevens Institute). Accepted at AAAI Spring Symposium 2024 + ICLR Workshop. T3 paper-wise.

## Stack
Python 3.10, Docker. OpenAI + local-LLM-compatible.

## Architecture (the only reason this repo matters)
Three-module agent design:
1. **Profiling** — character/risk persona.
2. **Layered Memory** — **short / mid / long memory tiers**, each with decay + retrieval. Closest OSS implementation of the cognitive-memory-trader pattern.
3. **Decision-making** — converts retrieved memories → trade.

## Backtest evidence
Paper claims outperformance on selected US tickers (TSLA, MSFT, NIO, COIN, etc.). Cherry-picked tickers + arguably in-sample. Without an out-of-sample partition publicly verifiable → claims T0; method T3.

## India relevance
None.

## Red flags
- Stale (~9 months no commit). Replaced in the authors' research agenda.
- Performance numbers cherry-pick winners.

## Trust score: **T2** (paper credible; performance claims T0)

## Verdict: **Study and steal patterns.** The layered-memory + character-profile design is directly portable to a TradingAgents-style graph. Specifically the memory-decay and retrieval-by-relevance machinery.
