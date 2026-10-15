# Dossier — microsoft/qlib

- **URL:** https://github.com/microsoft/qlib
- **Stars / Forks:** 43,287 / 6,813
- **Last push:** 2026-04-22
- **License:** MIT
- **Maintainer:** Microsoft Research Asia (T3). Multi-author, peer-reviewed papers; companion `microsoft/RD-Agent` (LLM-driven factor mining, arXiv:2505.15155).

## Stack
Python. Pandas-heavy. Stores OHLCV in custom binary format under `~/.qlib/qlib_data/`. Ships A-share + US datasets.

## Architecture
Quant-research-centric, not trade-execution-centric. Layers:
1. **Data layer** — efficient point-in-time, survivorship-correct loaders.
2. **Expression engine** — factor formulas, Alpha158/Alpha360 banks.
3. **Model zoo** — LightGBM, GRU, Transformer, TabNet, etc.
4. **Workflow / `qlib.workflow.recorder`** — MLflow-style experiment tracking.
5. **Portfolio strategy + backtester** — TopK-Dropout, basic execution with cost.
6. **Online serving** — paper-style daily inference, no broker integration.

## Backtest quality
Strong: point-in-time data, transaction cost configurable, supports walk-forward `RollingEnsemble`. Built-in metrics include max-drawdown, Calmar, IC, Rank-IC. Published benchmarks in repo `examples/benchmarks/` (T2: reproducible numbers in README, but on CSI300 — China A-shares).

## India relevance
Indirect. Pipeline is reusable for NSE if you supply the data (yfinance-to-qlib converter exists in `scripts/`). No Indian broker glue. **Best fit for an Indian user as the research/factor engine sitting upstream of an openalgo execution layer.**

## Red flags
Almost none. Caveats:
- Heavy footprint, opinionated data format.
- A-share benchmarks may not transfer (different microstructure, T+1 settlement).
- Maintenance has slowed slightly; many tasks now in `RD-Agent`.

## Trust score: **T3**
Microsoft Research-backed, peer-reviewed, code matches papers, well-known in quant community.

## Verdict: **Study and steal patterns**
Specifically: point-in-time data loader pattern, Alpha158 feature factory, walk-forward `RollingEnsemble`. If building a slow-horizon NSE system, qlib is the most credible OSS research substrate.
