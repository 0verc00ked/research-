# Dossier — 195440/nof1.ai (open-nof1.ai)

- **URL:** https://github.com/195440/nof1.ai
- **Stars / Forks:** 669 / 196
- **Last push:** 2026-05-15
- **Created:** 2025-10-27
- **License:** AGPL-3.0
- **Maintainer:** Pseudonymous (`195440`). Chinese-language README primary. T0 identity.

## Stack
TypeScript / Node 20, VoltAgent framework, OpenAI-compatible LLM (DeepSeek V3.2 / "Gork4" [sic, Grok-4] / Claude), Gate.io + OKX exchanges.

## Architecture
Single Trading Agent (LLM) → VoltAgent → tools (market data, news, account, trade exec) → Gate.io / OKX clients. **Minimal hard rules — LLM has near-full decision autonomy.**

## Red flags (many)
- README links to Gate.io and OKX with referral parameters (`?ref_type=103`, `nofiaioo`) — monetization via signups, classic affiliate funnel.
- "Minimal human intervention" + "let AI decide autonomously" — anti-pattern explicit in rubric.
- Pseudonymous author.
- Zero open issues (suspiciously clean for 669★).
- No backtest evidence.
- Typo "Gork4" suggests low rigor.

## India relevance
Gate.io and OKX are not FIU-registered; Indian use is non-compliant.

## Trust score: **T0**

## Verdict: **Ignore.** Textbook affiliate-funnel "AI trader."
