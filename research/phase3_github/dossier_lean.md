# Dossier — QuantConnect/Lean

- **URL:** https://github.com/QuantConnect/Lean
- **Stars / Forks:** 19,067 / 4,783
- **Last push:** 2026-05-20
- **License:** Apache-2.0
- **Maintainer:** QuantConnect Inc (commercial, US/Ireland). T3.

## Stack
**C# core**, Python strategies via PythonNet. Event-driven. Multi-asset (equity, options, futures, FX, crypto, CFD).

## Architecture
- Data → universe selection → alpha model → portfolio construction → execution → risk model. Each is a swappable component (the "Algorithm Framework").
- Backtest = live identical interface.
- Brokerages: IBKR, Tradier, Coinbase, Binance, Bitfinex, Kraken, Bybit, Charles Schwab, OANDA, TradeStation. **No Indian broker.**
- Cloud (QuantConnect.com) provides Indian equities data, but execution still through above brokerages.

## Backtest quality
Institutional. Survivorship-correct data (paid), corporate-action handling, fill models, multiple slippage models. Open-source LEAN backtests locally without cloud.

## India relevance
**Weak.** You can backtest NSE on QuantConnect cloud (paid data), but cannot execute on NSE through Lean. IBKR-route is via US/GIFT, not domestic NSE.

## Red flags
- C# adds significant operational overhead vs Python options.
- Cloud is the upsell — local OSS works but is the harder path.
- No grift.

## Trust score: **T3**

## Verdict: **Study** for architecture (alpha/portfolio/execution/risk separation). **Ignore as base** for India-direct trading.
