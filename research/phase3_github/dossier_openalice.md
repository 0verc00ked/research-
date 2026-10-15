# Dossier — TraderAlice/OpenAlice

- **URL:** https://github.com/TraderAlice/OpenAlice
- **Stars / Forks:** 4,189 / 636
- **Last push:** 2026-05-21
- **Created:** 2026-02-18 (3 months old)
- **License:** AGPL-3.0
- **Maintainer:** "TraderAlice" — unclear individual / small team. Website openalice.ai. T1 identity.

## Stack
TypeScript / Node. CCXT, Alpaca, IBKR.

## Architecture (notable patterns)
- **Unified Trading Account (UTA)**: AI interacts with abstractions, never directly with brokers.
- **Trading-as-Git**: orders staged → committed with message → pushed to execute. Full audit trail via commit hashes. **This pattern is worth stealing.**
- **Guard pipeline**: per-account pre-execution checks (position size, cooldown, whitelist).
- **Workspaces**: per-task git repo + persistent terminal session running `claude` / `codex` / `shell` CLI with MCP tools.
- **Evolution mode**: permissioned self-modification (red flag if used in live trading without sandbox).

## Backtest evidence
None disclosed.

## India relevance
Via CCXT (foreign crypto exchanges only) and IBKR (US/GIFT path). No NSE broker. Could be wrapped over openalgo's REST API as another connector.

## Red flags
- 3-month-old repo with 4k★ — campaign suspicion (Discord + QQ + X badges).
- AGPL-3.0 — same caveat as openalgo for network-exposed derivatives.
- "Evolution mode" with full Bash access — security nightmare unless tightly sandboxed.
- README explicitly says "experimental, do not use for live trading" — earns some honesty points.

## Trust score: **T1**

## Verdict: **Watch.** The "Trading-as-Git" pattern is genuinely novel and worth pinching for audit/explainability; the rest is too young to depend on.
