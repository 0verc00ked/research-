# Dossier — mementum/backtrader

- **URL:** https://github.com/mementum/backtrader
- **Stars / Forks:** 21,627 / 5,083
- **Last push:** **2024-08-19** (≈21 months stale)
- **License:** GPL-3.0
- **Maintainer:** Daniel Rodriguez (`mementum`); maintenance has effectively stopped.

## Stack
Pure Python. Classic OOP design.

## Architecture
- Cerebro engine + Strategy class + Indicators + Analyzers + Brokers.
- Live trading via IBKR, Oanda, VC, ccxt-style brokers (community-maintained).
- Walk-forward via custom orchestration.

## Backtest quality
Slippage and commission modeling supported. Multiple data feeds. Slower than vectorbt for large parameter sweeps.

## India relevance
Indirect. `alpaca-backtrader-api` (alpacahq, 690★, last activity 2024-12) is the most-used adapter. No direct NSE adapter; some community wrappers for Zerodha exist but unmaintained.

## Red flags
- Effective abandonment. No PR merges in ~2 years.
- Still works for the basic case but expect to fork.

## Trust score: **T2**

## Verdict: **Study only.** Use vectorbt or qlib for new work; reference backtrader source for the canonical "Cerebro" engine design and `Analyzer` separation.
