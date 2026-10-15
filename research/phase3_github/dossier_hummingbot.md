# Dossier — hummingbot/hummingbot

- **URL:** https://github.com/hummingbot/hummingbot
- **Stars / Forks:** 18,616 / 4,681
- **Last push:** 2026-05-20
- **License:** Apache-2.0
- **Maintainer:** Hummingbot Foundation (post-CoinAlpha pivot, DAO-style). T2-T3.

## Stack
Python, Cython hot-path. Docker-first install. Strategy DSL ("Scripts" framework).

## Focus
**Market-making bots** for 140+ CEX/DEX. Originally incentivized via liquidity-mining campaigns with exchange partners (these have largely wound down).

## Architecture
Connectors (per exchange) → market-data feeds → strategy → order management → risk. Backtest support is weaker than freqtrade/nautilus; MM strategies are tuned via paper-mode and live.

## Backtest evidence
Limited historical backtest — market-making is order-book dependent, hard to backtest faithfully. Hummingbot publishes "reported volumes" dashboard (T1: self-reported).

## India relevance
None directly. Indian residents using foreign crypto exchanges face FEMA + 30% crypto tax + 1% TDS — MM economics evaporate. Hyperliquid/dYdX integrations exist but same regulatory issue.

## Red flags
- Heavy "earn rewards" / "Condor Telegram bot" marketing (Foundation revenue model).
- MM strategies need rebate-tier accounts to be profitable — solo low-capital traders typically pay maker fee, not earn rebate.

## Trust score: **T2**
Code is real and battle-tested. The *strategies* are not where a small Indian trader wins.

## Verdict: **Study** the connector abstraction. **Ignore** as a trading vehicle for this user's constraints.
