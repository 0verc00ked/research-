# Dossier — ginlix-ai/LangAlpha

- **URL:** https://github.com/ginlix-ai/LangAlpha
- **Stars / Forks:** 1,151 / 166
- **Last push:** 2026-05-20
- **Created:** 2026-01-18 (~4 months)
- **License:** Apache-2.0
- **Maintainer:** ginlix.ai (commercial entity, website live). T1.

## Stack
Python 3.12+, LangChain, PostgreSQL, Redis, Slack/Discord integrations, MCP servers, sandboxed Python execution. React web UI with TradingView embed.

## Architecture — patterns worth stealing
- **Programmatic Tool Calling (PTC)**: agent writes Python that calls MCP tools instead of dumping raw data into LLM context — substantial token efficiency gain.
- **Progressive tool discovery**: tools loaded as summaries; full docs dumped into workspace on demand.
- **Persistent per-workspace research**: `.agents/user/memo/`, `.agents/workspace/memory/`, `agent.md` — research compounds over weeks/months. Echoes Claude Code / OpenCode model.
- **Skills**: pre-built workflows (DCF, initiating-coverage reports, earnings, morning notes).
- **Subagent swarm** with isolated context windows, checkpoint/resume, live steering, middleware stack (25 layers).
- **Encrypted secrets vault** (pgcrypto), credential leak detection.

## What it is NOT
A trader. No order routing, no broker connectors. It is a **vibe-investing research harness**.

## India relevance
Symbol-agnostic; could ingest NSE via TradingView or custom MCP. No execution.

## Red flags
- Commercial-leaning, branded heavily.
- 4-month-old repo with paid SaaS ahead.
- No published track record.

## Trust score: **T1**

## Verdict: **Study patterns.** Specifically (1) PTC for token efficiency, (2) persistent workspace memory, (3) middleware stack design. Do not adopt as base.
