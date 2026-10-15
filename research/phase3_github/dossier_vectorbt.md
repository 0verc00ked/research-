# Dossier — polakowo/vectorbt

- **URL:** https://github.com/polakowo/vectorbt
- **Stars / Forks:** 7,635 / 980
- **Last push:** 2026-04-25
- **License:** NOASSERTION (custom, non-standard; ships with caveats)
- **Maintainer:** Oleg Polakov (commercial product `vectorbtpro` is the paid follow-on).

## Stack
Python, NumPy + Numba JIT, Pandas. Built for vectorized parameter sweeps.

## Architecture
- Convert OHLCV → entries/exits arrays → simulate Portfolio → metrics.
- Fast enough to evaluate millions of parameter combinations.
- Supports SL/TP, position sizing, fees, slippage.

## Backtest quality
Excellent for parameter exploration; lookahead risk is the responsibility of the user (no built-in PIT guard). Pair with cross-validation manually.

## India relevance
Symbol-agnostic; eats any OHLCV. The most accessible backtester for NSE on a low-spec laptop.

## Red flags
- Free OSS is feature-frozen relative to paid vectorbtpro.
- License is "all rights reserved with usage permissions" — read carefully before commercial deployment.

## Trust score: **T3**

## Verdict: **Use as base** for backtest layer in the early phases. If parameter sweeps get heavy, evaluate vectorbtpro vs nautilus.
