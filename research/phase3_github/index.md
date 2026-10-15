# Phase 3 — GitHub Mining Index

**Generated:** 2026-05-21
**Method:** GitHub Search API (`api.github.com/search/repositories?sort=stars`) across 32 query strings (agentic trading, LLM-trading, FinGPT/FinRL/FinRobot/FinMem, qlib, freqtrade, nautilus, backtrader, vectorbt, zipline, Lean, hummingbot, jesse, OctoBot, openalgo, kiteconnect, upstox, dhan, angelone smartapi, icici breeze, polymarket, kalshi, autonomous trading, etc.). Raw JSON cached in `/Users/Nikhil-S/Projects/Trading/research/sources/raw/phase3/`.
**Trust scoring:** Stars and README claims are T0. License + commit history + actual code inspection upgrades to T2/T3. Where I cloned/read code locally it is noted as T4.

## Master table

| Repo | ★ | Forks | Last push | License | Lang | Indian broker? | Trust | One-line verdict |
|---|---:|---:|---|---|---|---|---|---|
| [TauricResearch/TradingAgents](dossier_tradingagents.md) | 77.9k | 15.2k | 2026-05-17 | Apache-2.0 | Python | No | **T2** | Study patterns; arXiv paper + clean LangGraph code, but **no execution layer** — research-only. |
| [freqtrade/freqtrade](dossier_freqtrade.md) | 50.6k | 10.6k | 2026-05-21 | GPL-3.0 | Python | No (crypto CEX/DEX) | **T3** | Use as base for any crypto-leg; mature backtester, dry-run, hyperopt, JOSS-published. |
| [microsoft/qlib](dossier_qlib.md) | 43.3k | 6.8k | 2026-04-22 | MIT | Python | Indirect | **T3** | Study patterns; gold standard for factor/ML quant research, not turnkey execution. |
| [nautechsystems/nautilus_trader](dossier_nautilus.md) | 22.9k | 2.8k | 2026-05-21 | LGPL-3.0 | Rust + Python | No | **T3** | Study/Use-as-base for serious infra; event-driven Rust engine with research-live parity. |
| [mementum/backtrader](dossier_backtrader.md) | 21.6k | 5.1k | 2024-08-19 | GPL-3.0 | Python | Via alpaca-backtrader-api | **T2** | Study only; classic but **effectively abandoned** (~21 months no push). |
| [AI4Finance-Foundation/FinGPT](dossier_finrl_family.md) | 20.3k | 2.9k | 2026-05-11 | MIT | Notebooks | No | **T1** | Ignore for execution; mostly notebooks + model checkpoints, not a trading system. |
| [QuantConnect/Lean](dossier_lean.md) | 19.1k | 4.8k | 2026-05-20 | Apache-2.0 | C# | No direct India | **T3** | Study; institutional engine, but Indian-data path goes through QuantConnect cloud. |
| [hummingbot/hummingbot](dossier_hummingbot.md) | 18.6k | 4.7k | 2026-05-20 | Apache-2.0 | Python | No (crypto only) | **T3** | Study market-making layer; reputable, but its edge is for MMs with rebate deals. |
| [HKUDS/AI-Trader](dossier_ai_trader.md) | 18.3k | 2.8k | 2026-05-20 | NONE | Python | No | **T0** | Ignore — SaaS funnel + unlicensed code + "100% automated" marketing = grift signal. |
| [UFund-Me/Qbot](dossier_qbot.md) | 17.4k | 2.5k | 2026-03-11 | MIT | Python | A-share, not IN | **T1** | Skim only; bundles existing libs, heavy CN marketing. |
| [AI4Finance-Foundation/FinRL](dossier_finrl_family.md) | 15.2k | 3.3k | 2026-05-18 | MIT | Notebooks | No | **T2** | Study RL framing only; legacy repo, points users to FinRL-X. |
| [jesse-ai/jesse](dossier_jesse.md) | 7.9k | 1.1k | 2026-05-20 | MIT | Python | No (crypto) | **T2** | Study; clean DSL, but business model funnels to paid "Jesse+". |
| [HKUDS/Vibe-Trading](dossier_vibe_trading.md) | 7.8k | 1.6k | 2026-05-20 | MIT | Python | No | **T1** | Skim — same HKUDS group; better engineering than AI-Trader but still early (created 2026-04). |
| [polakowo/vectorbt](dossier_vectorbt.md) | 7.6k | 980 | 2026-04-25 | NOASSERTION | Python | No | **T3** | Use as backtester; fast vectorized; PRO is paid, OSS still useful. |
| [AI4Finance-Foundation/FinRobot](dossier_finrl_family.md) | 7.0k | 1.2k | 2026-05-10 | Apache-2.0 | Notebooks | No | **T1** | Skim; report-generator more than trader; FinRobot.ai is a paid SaaS funnel. |
| [Drakkar-Software/OctoBot](dossier_octobot.md) | 5.9k | 1.2k | 2026-05-20 | GPL-3.0 | Python | No (crypto) | **T2** | Study; healthy maintenance, but cloud-SaaS pivot, AI features superficial. |
| [TraderAlice/OpenAlice](dossier_openalice.md) | 4.2k | 636 | 2026-05-21 | AGPL-3.0 | TS | Via IBKR/CCXT | **T1** | Watch; thoughtful "Trading-as-Git" pattern but 3-month-old repo, no track record. |
| [Polymarket/agents](dossier_polymarket_agents.md) | 3.5k | 787 | 2024-11-05 | MIT | Python | No | **T1** | Reference only — archived, but useful for prediction-market patterns. |
| [The-Swarm-Corporation/AutoHedge](dossier_autohedge.md) | 2.7k | 452 | 2026-05-11 | MIT | Python | No | **T0** | Ignore — "enterprise hedge fund" buzzword stack, Solana-only, swarms.xyz funnel. |
| [marketcalls/openalgo](dossier_openalgo.md) | 1.9k | 906 | 2026-05-20 | AGPL-3.0 | Python | **YES — 30+ Indian brokers** | **T3** | **Use as base** for any India deployment — by far the most credible Indian-broker abstraction layer. |
| [ginlix-ai/LangAlpha](dossier_langalpha.md) | 1.2k | 166 | 2026-05-20 | Apache-2.0 | Python | No | **T1** | Study patterns (PTC, workspaces); commercial-leaning, 4-month-old repo. |
| [pipiku915/FinMem-LLM-StockTrading](dossier_finmem.md) | 897 | 193 | 2024-08-18 | MIT | Python | No | **T2** | Study memory pattern (ICLR'24 workshop paper); stale code. |
| [195440/nof1.ai](dossier_nof1.md) | 669 | 196 | 2026-05-15 | AGPL-3.0 | TS | No (Gate.io/OKX) | **T0** | Ignore — referral-link laden, "minimal human intervention" marketing. |
| [51bitquant/ai-hedge-fund-crypto](dossier_misc_minor.md) | 584 | 152 | 2025-09-05 | MIT | Python | No | **T1** | Skim; small derivative work. |
| [ryanfrigo/kalshi-ai-trading-bot](dossier_kalshi_bot.md) | 414 | 160 | 2026-04-27 | MIT | Python | No | **T2** | Reference for prediction markets; disclaimer states examples lose money — refreshing honesty. |
| [marketcalls/openalgo](dossier_openalgo.md) (repeated for emphasis) | 1.9k | — | — | AGPL-3.0 | — | YES | T3 | — |
| **India broker shims (low-star, low-trust)** | | | | | | | | |
| Idirect-Tech/Breeze-Python-SDK | 86 | — | 2026-04-13 | MIT | Python | YES (ICICI) | T3 | Vendor official SDK; use if going ICICI route. |
| zerodha/kiteconnectjs | 388 | — | 2026-04-23 | MIT | TS | YES (Zerodha) | T3 | Vendor official SDK; use if going Zerodha route. |
| AM1403x/financial-agent-india | 105 | — | 2026-02-12 | NONE | Python | YES (AngelOne) | T1 | Skim; AI-agent over SmartAPI, unverified. |
| srikar-kodakandla/fully-automated-nifty-options-trading | 230 | — | 2024-10-10 | MIT | Python | YES (Kite) | T1 | Red flag: "fully automated nifty options"; classic overfit pattern. |

## Files
- Dossiers: `dossier_*.md` in this directory.
- Cross-cutting patterns: [`patterns.md`](patterns.md).
- Raw API responses: `/Users/Nikhil-S/Projects/Trading/research/sources/raw/phase3/`.
