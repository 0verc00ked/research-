# Dossier — freqtrade/freqtrade

- **URL:** https://github.com/freqtrade/freqtrade
- **Stars / Forks:** 50,573 / 10,557
- **Last push:** 2026-05-21 (active daily)
- **Created:** 2017-05
- **License:** GPL-3.0
- **Maintainer:** Org `freqtrade`, lead maintainer @xmatthias, multi-contributor, JOSS publication (10.21105/joss.04864). T3 credibility.

## Stack
Python. CCXT for exchange access. SQLite for state. FreqAI sub-module for ML. Telegram + Web UI control plane (`frequi`, 991★).

## Exchange coverage (crypto only)
Binance, Bybit, Kraken, Gate, Bitget, Bitmart, HTX, Hyperliquid (DEX), KuCoin, OKX, BingX (T3: README). **None of these are FIU-registered Indian crypto exchanges** — Indian residents using them sit in regulatory grey zone; CoinDCX/WazirX/Mudrex are NOT integrated.

## Architecture
Full pipeline: **data download → strategy class (`IStrategy`) → backtest → hyperopt (Optuna-based) → dry-run (paper) → live**. Same `IStrategy` runs in all four modes — the key property that makes it production-credible.

## Backtest quality
- Walk-forward via `backtesting --timerange`.
- Hyperopt explicitly warns about overfitting in docs.
- Slippage & fees modeled (per-pair, configurable).
- `NostalgiaForInfinity` (3.2k★ strategy repo) shows real long-term performance with losing periods — rare honesty.

## Red flags
- Telegram-controllable from any source: many forks attach paid signal funnels. Core repo is clean.
- README disclaimer is strong ("USE AT YOUR OWN RISK").
- No P&L screenshots in README — good sign.

## India relevance
**Low.** Crypto-only and no Indian-exchange adapter. Could be wired to Delta India (open issue, not merged last I checked) for INR-margined futures, but that requires custom CCXT extension. Indian crypto tax (30% flat + 1% TDS) makes this brutal for a low-capital solo.

## Trust score: **T3**
JOSS-peer-reviewed, large org, code matches docs, no grift attached to the core.

## Verdict: **Use as base** if going crypto. **Ignore** otherwise.
The strategy DSL + dry-run-to-live parity is the model to copy. Even for a non-crypto stack, study `freqtrade/optimize/backtesting.py` for canonical fee/slippage handling.
