# Phase 7 raw source index

Captured 2026-05-21. Full text of fetches lives in tool call logs; key URLs and quoted numbers cached here.

## Load-bearing papers
- arXiv:2510.07920 (Profit Mirage) — Sharpe decay 51.48-62.23%, return decay 50.18-71.85%, FinLake-Bench 85.4-92.9% memorization accuracy
- arXiv:2603.26797 (MemGuard-Alpha) — 40-60% LLM alphas flagged contaminated; unfiltered 15-25% ARR -> filtered 5-12%
- arXiv:2505.07078 (FinSABER, KDD 2026) — FinMem composite Sharpe -0.228, FinAgent 0.241, B&H 0.703 across 20-yr / 100+ symbols
- arXiv:2510.02209 (StockBench) — Mar-Jun 2025 post-cutoff; 10/14 LLMs marginal beat (0.5-2.5pp); Sortino 0.024-0.042
- arXiv:2512.23847 (Lookahead Bias) — Lookahead Propensity statistic; news->returns alpha is partly leakage
- arXiv:2511.18850 (CogAlpha) — leakage unit test integrated; train 2011-2019/val 2020/test 2021-2024 on CSI-300
- arXiv:2502.16789 (AlphaAgent, KDD 2025) — AST-similarity novelty filter, CSI-500 ~45%, S&P-500 ~37% over 2021-2024

## Negative-precedent / methodology
- Allen & Karjalainen 1999 JFE — GP rules underperform B&H OOS
- Sullivan/Timmermann/White 1999 J. Finance — ~7,800 technical rules; ~zero survive White's Reality Check
- McLean & Pontiff 2016 J. Finance — 26% lower OOS, 58% lower post-publication on 97 anomalies
- Harvey/Liu/Zhu 2016 RFS — most factors false discoveries given multiple-testing burden
- Bailey/Borwein/LdP/Zhu 2017 J. Comp. Finance — PBO via CSCV; threshold ≤0.5
- Bailey/LdP 2014 J. Portfolio Mgmt — DSR formula; threshold ≥0.95
- LdP X post 2021-07 — "as few as 3 trials → likely-false strategy on 10-yr backtest"
- LdP AFML 2018 Ch.12 — CPCV: N groups, k test groups, purge, embargo

## Practitioner
- Ernest Chan epchan.blogspot.com 2025-10 — conditional/cautious on LLMs; copilots not autonomous
- Robert Carver — "designed not fitted"; hostile to parameter search
- ml-quants Substack #7 — LLM alpha as narrative-driven, not backtestable in conventional sense

## GitHub repos surveyed (full list in /research/phase7_strategy_foundry/github_landscape.md)
- Y-Research-SBU/QuantAgent 2681* MIT (no validation harness)
- imbue-bit/AlphaGPT 2016* Apache-2.0 (actually RL, mislabeled)
- DulyHao/AlphaForge 370* no-license (AAAI2025 code, stale)
- RndmVariableQ/AlphaAgent 299* MIT (AST novelty filter; no DSR/PBO)
- waylonli/FINSABER (KDD2026 official harness — steal directly)
- esvhd/pypbo (PBO library; use directly)
- skfolio (CombinatorialPurgedCV; use directly)
