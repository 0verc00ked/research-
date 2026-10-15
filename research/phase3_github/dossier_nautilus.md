# Dossier — nautechsystems/nautilus_trader

- **URL:** https://github.com/nautechsystems/nautilus_trader
- **Stars / Forks:** 22,861 / 2,847
- **Last push:** 2026-05-21 (daily)
- **Created:** 2018-06
- **License:** LGPL-3.0
- **Maintainer:** Nautech Systems Pty (registered AU company), commercial backing, paid support email. Multi-year, hundreds of contributors. T3.

## Stack
Rust-native engine (`rust 1.95.0`) with Python control plane (3.12–3.14). PyO3 bindings. Built for **deterministic event-driven backtest = live** parity.

## Architecture
- **Cython/Rust core**: order book, matching engine, time bus, message bus.
- **Adapters**: Binance, Bybit, OKX, dYdX, Hyperliquid, Polymarket, Interactive Brokers, Databento, Tardis. **No Indian broker adapter** (T3: `nautilus_trader/adapters/`).
- **Backtest engine** uses identical execution semantics as live — strategies port without code changes.
- **Risk engine** baked in (pre-trade checks, position limits).
- **Persistence**: Parquet + Postgres optional.

## Backtest quality
Best-in-class for OSS: full microstructure-level event simulation, configurable latency, fees, slippage. Walk-forward via external orchestration. Codspeed CI tracks perf regressions.

## India relevance
**Indirect but promising.** IBKR adapter exists; IBKR has GIFT-IFSC presence. No NSE direct adapter, but the adapter ABI is clean — writing a Zerodha/Dhan adapter is feasible (~1–2 KLoC).

## Red flags
- LGPL-3.0 means linking is permissive but modifications-to-core must be open.
- Documentation lags code in places.
- Steep learning curve (Rust+Cython internals).
- No grift markers.

## Trust score: **T3**

## Verdict: **Use as base** for serious execution infra (post-research). The research-to-live parity property is exactly what `trust_rubric.md` would want before sizing real capital. For a low-capital solo it is overkill at week 1, but is the right destination if any strategy survives Phase 5 walk-forward.
