# agent-trader

LLM-as-analyst + rules-as-trader for NSE/BSE. India, low capital, SEBI-compliant.

**Status:** scaffold (Stage G0). No live calls. No real broker keys. No backtest results yet.

Full charter, evidence base, decisions, and gate criteria live in [`research/SYNTHESIS.md`](research/SYNTHESIS.md). Read that first.

## Architecture (one paragraph)

The LLM is an *analyst*, not a *trader*. It produces regime tags + event flags into a signal store on a slow loop (15-min+). A deterministic strategy layer reads the signal store plus price features and decides entry/sizing/exit. A risk module enforces hard kill-switch criteria. Execution goes through openalgo / Kite Connect on AWS ap-south-1 (SEBI 2026-04-01 mandates Indian-server hosting).

## Layout

```
agent_trader/
├── core/         strategy interface, signal store, risk, types
├── data/         qlib + Kite history adapters
├── analyst/      LLM analyst (graph, memory, prompts) — stub
├── execution/    broker abstraction (openalgo + Kite adapters) — stub
├── backtest/     nautilus runner — stub
└── ops/          audit logging (SEBI 5-yr), kill-switch
strategies/
└── nifty_weekly_otm_v0/   first hypothesis
tests/            smoke + interface tests
```

## Setup

```bash
uv sync --all-extras   # or `uv sync` for core only
make test
```

Optional extras: `llm` (anthropic, google-genai), `backtest` (vectorbt), `prod` (nautilus-trader), `data` (pyqlib, kiteconnect). Heavy deps are opt-in to keep CI fast and avoid pin conflicts during research.

## Gate status

See `research/tracker.md`. Current stage: **G0 — backtest not yet wired**. Do not attempt live trading.

## Reminders

- Revoke the GitHub PAT in `.env` once research/scaffold is locked.
- No code may call a broker live until the V-9 contamination probes have run on the chosen LLM and Stage G1 paper criteria are met.
