# Dossier — AI4Finance-Foundation (FinGPT / FinRL / FinRobot / FinRL-X)

Grouped because they share maintainers, Discord, and marketing patterns.

| Repo | ★ | License | Status |
|---|---:|---|---|
| FinGPT | 20.3k | MIT | Notebooks + HF model checkpoints (sentiment, forecaster) — **not a trading system** |
| FinRL | 15.2k | MIT | Original RL framework; legacy, redirects users to FinRL-X |
| FinRobot | 7.0k | Apache-2.0 | LLM-agent platform; funnels to finrobot.ai (paid SaaS) |
| FinRL-X / FinRL-Trading | 3.2k | Apache-2.0 | New "production-oriented" target |
| FinRL-Meta | 1.9k | MIT | Gym-style market environments |
| FinRL-Tutorials | 1.2k | MIT | Notebooks |

- **Maintainer:** AI4Finance Foundation. Loosely affiliated with Columbia (Xiao-Yang Liu). Multi-paper publishing group.
- **Last activity:** All actively maintained (2026-05).

## Pattern across the family
README hyperbole, prolific paper publication, **Discord-and-website funnel to commercial offerings** (finrobot.ai, finrl.ai). Code is real but assembly-required; performance numbers come from selected episodes in `FinRL-Meta` Gym envs.

## Architecture
- **FinGPT**: LoRA fine-tunes of Llama for sentiment / forecasting. Useful as a sentiment **component**, not a trader.
- **FinRL**: PPO/DDPG/SAC stable-baselines wrappers over a custom Gym env that uses OHLCV. Reward = log-return − cost. Famously hard to make out-of-sample profitable (T2: independent replication papers report poor OOS).
- **FinRobot**: LangChain + Autogen multi-agent that produces equity-research PDFs. Less a trader, more a report generator.

## Backtest evidence
FinRL papers show training-set Sharpe; out-of-sample disclosure is partial. Multiple independent reviewers note results are sensitive to seed and dataset window → **performance claims auto-cap T0** per rubric.

## India relevance
- FinGPT sentiment models work on English news — usable for NSE-listed mega-caps (RELIANCE, TCS, INFY).
- FinRL Gym envs accept any OHLCV CSV — NSE data feasible.
- No broker integration anywhere in the family.

## Red flags
- "Revolutionize" / fire emojis in README — marketing tone.
- Commercial SaaS funnel.
- Performance numbers selectively presented across many papers.

## Trust score: **T1** (T2 for FinRL framework as code).

## Verdict: **Skim.** Borrow FinGPT for a sentiment component only. Don't use FinRL as a strategy generator without extensive your-own walk-forward validation.
