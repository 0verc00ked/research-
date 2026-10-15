# Dossier — HKUDS/Vibe-Trading

- **URL:** https://github.com/HKUDS/Vibe-Trading
- **Stars / Forks:** 7,768 / 1,568
- **Last push:** 2026-05-20
- **Created:** 2026-04-01 (≈7 weeks old at time of review — extraordinary star velocity ⇒ campaign suspicion)
- **License:** MIT
- **Maintainer:** Same HKUDS group as AI-Trader.

## Stack
Python 3.11+ FastAPI backend, React 19 frontend, PyPI `vibe-trading-ai`. CLI tools (`vibe-trading hypothesis`, `vibe-trading alpha bench`, `vibe-trading memory`).

## Architecture (per README, T1)
More substantive than AI-Trader:
- **Alpha Zoo v1**: 452 factor formulas across 4 banks (qlib158, alpha101, gtja191, academic).
- **Hypothesis Registry**: persistent hypotheses linked to backtest runs.
- **Run cards** (`run_card.json`/`md`) for reproducibility.
- **Shadow Account** scanning on OHLCV.
- **Lookahead-guard test + AST purity gate** for alphas (explicitly addresses overfitting/leakage — rare and good).
- **Swarm runs** with isolated workers.

## What's missing
- Same group as AI-Trader; commercial leaning visible (vibetrading.wiki).
- No published track record of live performance.
- Heavy LLM dependency for the agent surface.
- Very young — no public failure analysis yet.

## India relevance
None direct. Could ingest NSE data via custom MCP server.

## Red flags
- Star velocity (~1k★/week) — suggests coordinated promotion (Trendshift badges, Feishu/WeChat group ladders).
- Shares the AI-Trader marketing playbook.
- Mitigating: actual engineering features (AST gate, lookahead guard, run cards) are real-quant good practice, not pure grift.

## Trust score: **T1**
Better engineering signals than AI-Trader, but unverified and too young to score higher.

## Verdict: **Skim and watch.** Steal the `run_card.json` + `Hypothesis Registry` patterns explicitly. Do not adopt as base until 6+ months of merged community PRs.
