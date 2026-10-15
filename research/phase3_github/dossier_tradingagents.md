# Dossier — TauricResearch/TradingAgents

- **URL:** https://github.com/TauricResearch/TradingAgents
- **Stars / Forks:** 77,915 / 15,175 (T3: GitHub API, fetched 2026-05-21)
- **Last commit on `main`:** `13b826a` 2025-10-09 — `Merge PR #245 feat/tooloptim` (T4: `git log` on local clone)
- **License:** Apache-2.0
- **Maintainer:** Tauric Research (academic group; arXiv 2412.20138). Discord + WeChat + X. Org-owned, multi-contributor. No sock-puppet smell.

## Stack
Python 3.13. **LangGraph + langchain-openai / langchain-anthropic / langchain-google-genai** (T4: `tradingagents/graph/trading_graph.py:8-13`). Data: Yahoo Finance, Alpha Vantage, Google News, Reddit, OpenAI tool-fetched (`tradingagents/dataflows/`). Default LLMs `o4-mini` + `gpt-4o-mini` (T4: `default_config.py`).

## Architecture (what the code actually does)
- **Analyst team** (4 LangGraph nodes): `market_analyst`, `social_media_analyst`, `news_analyst`, `fundamentals_analyst` (T4: `tradingagents/agents/analysts/`).
- **Researcher debate:** bull vs bear, `max_debate_rounds` default 1 (T4: `default_config.py:24`, `agents/researchers/`).
- **Research manager** consolidates debate.
- **Trader** node composes plan (T4: `agents/trader/trader.py`).
- **Risk debate:** aggressive / neutral / conservative debators → **risk_manager** picks Buy/Sell/Hold (T4: `agents/risk_mgmt/`, `agents/managers/risk_manager.py`).
- **Reflection module** writes "lessons" into `FinancialSituationMemory` (vector store) for next run (T4: `graph/reflection.py`, `utils/memory.py`).

## What is MISSING
- **No execution layer.** No broker API. No order router. No paper-trading harness beyond simulated "decision" output. (T4: `grep -ri "order\|broker\|paper" tradingagents` finds only prompt strings.)
- **No backtester.** It produces a single decision per `(ticker, date)` invocation; sequential evaluation is by external scripts.
- **No fee / slippage modeling.**
- **`data_dir` hardcoded** to `/Users/yluo/Documents/...` (T4: `default_config.py:6`) — clear sign code was published for paper reproduction, not production.

## Backtest evidence
Paper (arXiv 2412.20138, T2) reports beating buy-and-hold on selected US tickers. **No out-of-sample disclosure, no fee inclusion in repo code, no losing-period breakdown in README** → auto-cap at **T0** per `trust_rubric.md`.

## India relevance
Zero. Yahoo Finance + Alpha Vantage cover NSE tickers (`RELIANCE.NS`), but no broker integration. Two Chinese A-share forks exist (`hsliuping/TradingAgents-CN` 27k★, `KylinMountain/TradingAgents-AShare` 406★) — neither is India-localized.

## Red flags
None grift-level. Disclaimer present. Caveat: hyped 77k stars vs. very thin execution surface ⇒ many forkers will mistake it for a trader. It is a **research scaffold**.

## Trust score: **T2**
Code is real, peer-reviewed paper exists, code matches paper structure. Performance claims remain T0.

## Verdict: **Study and steal patterns**
Specifically the multi-agent debate graph, the bull/bear+risk-debator structure, and the reflection-into-memory loop. Do **not** treat it as a trading system; bolt it onto a real engine (nautilus / freqtrade / openalgo).
