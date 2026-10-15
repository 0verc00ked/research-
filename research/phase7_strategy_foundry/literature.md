# Phase 7 — Literature: LLM-as-Strategy-Generator / Automated Alpha Discovery

**Date:** 2026-05-21
**Scope:** Peer-reviewed and arXiv work 2023–2026 on LLM-driven alpha/strategy generation, the genetic-programming precedent, López de Prado's overfitting toolkit, negative results, and named-practitioner commentary. Every entry carries a T-score per `/research/trust_rubric.md`.

> **Reading order for the impatient:** §C (Negative results & contamination) and §D (López de Prado's protocol numbers) are the load-bearing sections. The "positive" LLM-alpha papers in §A are almost universally evaluated with weak baselines and short windows — read §C before believing any of them.

---

## A. LLM-driven alpha / factor mining (the "positive" literature)

### A1. Alpha-GPT (Wang et al., arXiv:2308.00016, 2023)
- **Venue:** arXiv; multiple v2 revisions through 2024. Not peer-reviewed to top venue at submission.
- **Method (2 lines):** LLM as interactive mediator between researcher idea and formulaic alpha search; AlphaBot translates natural language to symbolic expressions; GP-style search runs underneath.
- **Results / contamination handling:** Reports improved Sharpe over GP-only baselines on Chinese A-shares; **no walk-forward, no PBO, no DSR, no contamination test**. The LLM has read public Chinese-market alpha literature.
- **Trust score:** **T2** for the framework; **T1** for the alpha-generation claim (no de Prado-grade validation).
- **Takeaway:** Interesting human-AI loop concept; performance evidence is in-sample-flavored.
- URL: https://arxiv.org/abs/2308.00016

### A2. AlphaForge (Cui et al., AAAI-2025; arXiv:2406.18394)
- **Venue:** AAAI 2025 (peer-reviewed, **T3 venue**); repo `DulyHao/AlphaForge` 370★ (last push 2024-09).
- **Method:** Generative-predictive architecture for formulaic factor mining; dynamic combination ("mega-alpha") rather than static set.
- **Results:** Reports IC/RankIC gains over GP and DSO baselines on CSI-300/500. Standard train/valid/test split; no PBO; no DSR; survivorship discussion absent.
- **Trust score:** **T3** for the paper; **T1–T2** for "this would survive López de Prado's protocol" — *they never ran that protocol*.
- **Takeaway:** Among the more rigorous AAAI-published works; but its evaluation is IC/IR-driven, not statistically-overfit-aware.
- URL: https://arxiv.org/abs/2406.18394

### A3. AlphaAgent (Tang et al., KDD 2025; arXiv:2502.16789)
- **Venue:** ACM SIGKDD 2025 (**T3 venue**); repo `RndmVariableQ/AlphaAgent` 299★.
- **Method:** LLM agent with three regularizers — AST-similarity originality, hypothesis-factor alignment, AST complexity bound. Attempts to *counter* alpha decay.
- **Results:** CSI-500 and S&P-500 over 4 years (2021–2024). ~45% cumulative excess (CSI-500), ~37% (S&P-500). **No PBO, no DSR.** The S&P-500 window overlaps GPT-4/Claude-3 training data (well-known contamination zone — see §C1).
- **Trust score:** **T3** paper, **T1** for OOS edge claim (contamination & no DSR).
- **Takeaway:** The originality regularizer is a useful pattern; the headline returns are not credible until re-run on post-training-cutoff data with DSR.
- URL: https://arxiv.org/abs/2502.16789

### A4. Navigating the Alpha Jungle (LLM-MCTS, arXiv:2505.11122, May 2025)
- **Method:** LLM generates symbolic alpha formulas; MCTS prunes/explores using backtest feedback; frequent-subtree avoidance for diversity.
- **Results:** "Superior predictive accuracy and trading performance" on real stock data — *no DSR, no PBO, no clean post-cutoff OOS*. Specifics of fee model not visible in abstract.
- **Trust score:** **T2** (arXiv preprint, weak baselines).
- **Takeaway:** Mechanism (MCTS over LLM proposals) is interesting; evidence is standard-issue weak.
- URL: https://arxiv.org/abs/2505.11122

### A5. Chain-of-Alpha (arXiv:2508.06312, Aug 2025)
- **Method:** Chain-of-thought decomposition for alpha mining.
- **Results:** Marginal improvement over LLM single-shot baselines on Chinese markets; **no DSR/PBO**; no Indian or US large-cap clean test.
- **Trust score:** **T2** preprint.
- **Takeaway:** Incremental; nothing addresses the core overfitting/contamination issue.
- URL: https://arxiv.org/abs/2508.06312

### A6. AlphaEval (arXiv:2508.13174, Aug 2025) — **evaluation framework, not an alpha generator**
- **Method:** Five-dimensional "backtest-free" evaluation: Predictive Power (IC/RankIC), Temporal Stability (Relative Rank Entropy), Robustness (Perturbation Fidelity), Financial Logic (LLM judge), Diversity.
- **Important caveat:** Explicitly *excludes* PBO, DSR, and walk-forward — argues these are too computationally heavy. **This is a significant epistemological choice that López de Prado would disagree with.**
- **Results on LLM alphas:** AlphaAgent ranks highest on IC (0.041) and logic, but **lowest on robustness (0.415)** vs perturbations. Confirms that LLM-generated alphas are perturbation-fragile.
- **Trust score:** **T2** preprint; framework itself is **T2**.
- **Takeaway:** Useful diagnostic; do not use it *in lieu of* PBO/DSR.
- URL: https://arxiv.org/abs/2508.13174

### A7. Cognitive Alpha Mining / CogAlpha (arXiv:2511.18850, late 2025)
- **Method:** 7-level, 21-agent LLM hierarchy; code-based alpha representation (not formula stacking); evolutionary loop with a Multi-Agent Quality Checker that includes a **static leakage unit-test**.
- **OOS protocol:** CSI-300, train 2011–2019, validate 2020, test 2021/01 → 2024/12. Fees: 0.05% open / 0.15% close, min 5 CNY. **Chronological split; explicit leakage check.**
- **Results:** IC=0.0591, RankIC=0.0814, RankICIR=0.4350. Honest note from paper: traditional ML (LightGBM IC=0.0269) is comparable to *prior* LLM methods — meaning the gain attributed to LLMs in the older literature is largely artifact; only CogAlpha's evolutionary scaffold lifts it.
- **Trust score:** **T2** preprint, but **methodologically the most honest of the LLM-alpha papers**.
- **Takeaway:** The leakage-test integration is the right direction. Still no DSR/PBO.
- URL: https://arxiv.org/abs/2511.18850

### A8. QuantaAlpha (arXiv:2602.07085, Feb 2026)
- Evolutionary LLM-alpha framework; **not yet credibly evaluated** in literature.
- **Trust score:** **T1** preprint. URL: https://arxiv.org/abs/2602.07085

### A9. Alpha-R1 (arXiv:2512.23515, Dec 2025)
- **Method:** 8B RL-trained reasoner for context-aware **alpha screening** (not generation). Evaluates *when* a known alpha is economically relevant given news/regime.
- **Trust score:** **T2** preprint.
- **Takeaway:** Pattern is interesting and aligns with our §SYNTHESIS Role-2 stance (regime/news conditioning), not a generator.
- URL: https://arxiv.org/abs/2512.23515

### A10. FinAgent (cited in QuantAgents 2025 work)
- **Reported results (per QuantAgents paper):** ARR 45.31%, Sharpe 2.25, beating RL baselines (AlphaMix+ ARR 32.51%, SR 1.49). *No DSR, no PBO; small ticker basket; window overlaps LLM training data.* Same caveats as FinMem.
- **Trust score:** **T1–T2** for the P&L claim.

### A11. QuantAgents (arXiv:2510.04643, Oct 2025)
- **Reported:** ARR 58.68%, Sharpe 3.11 — extraordinary numbers on a small ticker basket and short window. Treat as **T1** for the P&L claim until externally replicated on contamination-free data.

### A12. AlphaEvolve (Cui et al., SIGMOD 2021, arXiv:2103.16196) — *not* the DeepMind 2025 system
- **Method:** Evolutionary search over operator DAGs (RelationOps, ExtractionOps) for novel alphas; *pre-LLM* but cited as the precedent everyone copies.
- **Trust score:** **T3** (SIGMOD).
- **Takeaway:** This is the work the LLM-alpha papers are mostly reinventing with LLMs in the proposer slot. Useful baseline.
- URL: https://dl.acm.org/doi/10.1145/3448016.3457324

### A13. AlphaEvolve (DeepMind, May 2025) — **not finance-specific**
- **Method:** Gemini-powered coding agent + evolutionary loop; solved matrix-multiplication speedup, datacentre scheduling, chip design.
- **Trust score:** **T3** for the algorithmic-discovery claim; **N/A** for finance.
- **Takeaway:** Often invoked as "AlphaEvolve for trading would work" — that is **not what DeepMind shows**. The validator quality (formal correctness of an algorithm) does not transfer to finance, where the validator is a noisy backtest. Do not infer financial viability from this work.
- URL: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/

---

## B. The classical precedent — genetic programming for alpha

### B1. Allen & Karjalainen, *Using genetic algorithms to find technical trading rules*, JFE 1999
- **Venue:** *Journal of Financial Economics* (**T3**, peer-reviewed).
- **Result:** Discovered rules were "profitable in-sample but **outperformed by simple buy-and-hold** out-of-sample" on S&P 500. Foundational negative result.
- **Trust score:** **T3.**
- **Takeaway:** This is the historical floor of expectation: 25+ years of GP alpha mining and the headline result is "did not beat buy-and-hold OOS." LLMs ride on the same conveyor belt and have not yet shown they break this pattern.

### B2. Sullivan, Timmermann, White, *Data-Snooping, Technical Trading Rule Performance, and the Bootstrap*, J. Finance 1999
- **Method:** White's Reality Check applied to ~7,846 technical trading rules.
- **Result:** After data-snooping correction, **no rule** had statistically significant superior predictive ability OOS post-1986. (T3, J. Finance.)
- **Takeaway:** The reason DSR/PBO exist. Auto-discovery without multiple-testing correction = noise dressed as alpha.

### B3. WorldQuant *101 Formulaic Alphas* (Kakushadze, 2016)
- **Important context for §C:** These 101 alpha expressions are public, widely cited, and almost certainly in the training corpus of every modern LLM. Any LLM that "discovers" alphas formally similar to Alpha101 entries is **retrieving, not exploring.**

### B4. Alpha Mining via Warm-Start GP (arXiv:2412.00896, 2024)
- Modern GP-alpha paper that explicitly acknowledges rapid alpha decay from overfitting and uses a warm-start to mitigate.
- **Trust score:** **T2.**

---

## C. Negative results, contamination, and replication failure

### C1. **Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents** (arXiv:2510.07920, Oct 2025) — **load-bearing paper**
- **Method:** Four-pronged empirical leakage audit: (1) pre- vs post-training-cutoff backtests, (2) counterfactual perturbation, (3) memorization audit on FinLake-Bench (2,000 Q&A, Jan 2022–Jun 2023), (4) fine-tuning generalization.
- **Numerical results (THE numbers to remember):**
  - **Sharpe ratio decay 51.48% → 62.23% post-training-cutoff** across tested LLM agents.
  - **Total return decay 50.18% → 71.85%** post-cutoff.
  - LLMs achieve **85.4%–92.9%** accuracy on memorization-style FinLake-Bench questions; **90.2%** on historical trend prediction.
  - Prediction Consistency (PC) > 0.69 across all tested agents = strong memorization signal.
- **Their proposed mitigation (FactFin):** Strategy-code generation + RAG over real-time factors + MCTS + counterfactual simulator. Reduces PC by 57–64%; recovers 22.74% Sharpe vs baselines on July 2024–June 2025 OOS.
- **Trust score:** **T3** — methodology is the most rigorous in the field; FactFin gain claim is **T2** until replicated.
- **Takeaway:** **At least half of every published LLM trading-agent alpha is contamination.** This is the strongest single piece of evidence in the entire phase.
- URL: https://arxiv.org/abs/2510.07920

### C2. **MemGuard-Alpha** (arXiv:2603.26797, 2026)
- **Method:** Membership-inference + cross-model disagreement to flag memorization-contaminated LLM-generated alphas.
- **Results:** **40–60% of LLM-generated alphas flagged as memorization-contaminated.** Filtered alpha annualized return drops from ~15–25% (unfiltered) to ~5–12% (filtered).
- **Trust score:** **T2** preprint; corroborates C1 from a different angle.
- **Takeaway:** Independent confirmation that the contamination tax on LLM-generated alpha is large.
- URL: https://arxiv.org/abs/2603.26797

### C3. **FinSABER — "Can LLM-based Financial Investing Strategies Outperform the Market in Long Run?"** (Li et al., KDD 2026; arXiv:2505.07078)
- **Venue:** KDD 2026 (**T3**); code at github.com/waylonli/FINSABER.
- **Method:** Backtests **FinMem, FinAgent**, and 12+ baselines (B&H, SMA, ATR, Bollinger, ARIMA, XGBoost, A2C, PPO, DDPG, SAC, TD3) over **20 years, 100+ symbols**. Mitigates survivorship, lookahead, and data-snooping.
- **Numerical results:**
  - **FinMem composite Sharpe = −0.228; FinAgent = 0.241; Buy-and-Hold = 0.703.**
  - On AMZN: FinMem 5.7% vs B&H 16.0%. On MSFT: FinMem 4.6% vs B&H 11.2%. On NFLX: FinMem 12.6% vs B&H 23.9%. Beats B&H only on TSLA (cherry).
  - Bull markets: FinAgent Sharpe 0.12 vs B&H 0.61 ("excessive conservatism").
  - Bear markets: FinAgent −0.38 vs B&H −0.28 ("inadequate risk control").
- **Fees:** Moomoo standard $0.0049/share, min $0.99/order; rf = 3%.
- **Trust score:** **T3** — most rigorous negative result on LLM agents.
- **Takeaway:** When the universe broadens and the window lengthens, the alpha disappears. Period.
- URL: https://arxiv.org/abs/2505.07078

### C4. **StockBench** (Chen et al., arXiv:2510.02209, Oct 2025)
- **Method:** Contamination-free benchmark, March 3 – June 30 2025 (post-training-cutoff for most models, 82 trading days), 14 LLMs (GPT-5, Claude-4, Qwen3-235B, Kimi-K2, GLM-4.5, etc.), top-DJIA names.
- **Results:**
  - 10 / 14 LLMs beat the 0.4% B&H cumulative return — but only by **0.5–2.5 percentage points** over 4 months on a strongly trending universe.
  - **Sortino ratios** mostly 0.024–0.042 (top: Kimi-K2 0.042 vs B&H 0.0155). These are **absolute** Sortinos for 4 months; annualized comparables are weak.
  - **Strong financial-QA performance does *not* translate to trading.**
- **Trust score:** **T3.**
- **Takeaway:** "Beats B&H on a 4-month bull window" is a low bar; the more durable finding is that QA prowess ≠ trading skill.
- URL: https://arxiv.org/abs/2510.02209

### C5. **DRL Crypto Backtest-Overfitting** (arXiv:2209.05559, 2022)
- PBO-style probabilistic check shows most "winning" DRL trading agents are overfit. (**T3.**) Pre-LLM but applies identically.

### C6. **Lookahead Bias in LLM Forecasts** (Gao/Jiang/Yan, arXiv:2512.23847, 2025)
- Develops a "Lookahead Propensity" statistic; shows LLM news→returns "alpha" is partly training-data lookahead. (**T3.**) Methodology directly applicable to strategy generation.

### C7. **McLean & Pontiff** (J. Finance 2016)
- 97 published cross-sectional anomalies: returns **26% lower OOS, 58% lower post-publication.** (**T3.**)
- **Implication for LLMs:** Any factor an LLM "discovers" that is similar to a published anomaly is starting on the wrong side of that 58% haircut.

### C8. **Harvey, Liu, Zhu**, *…and the Cross-Section of Expected Returns*, RFS 2016
- ~316 factors published; argue most are false discoveries given multiple-testing burden. (**T3.**) Same caution applies even more harshly to LLM-generated factors where N_trials is unbounded.

---

## D. López de Prado's protocol — the actual numbers

This is the load-bearing methodology section. Cite exact thresholds.

### D1. **The Probability of Backtest Overfitting (PBO)** — Bailey, Borwein, López de Prado, Zhu, J. Computational Finance 2017
- **Definition:** Probability that the *in-sample optimal* strategy underperforms the *median* OOS.
- **Method:** Combinatorially Symmetric Cross-Validation (CSCV) — partition returns into **S** even sub-periods (typically S=16), enumerate all C(S, S/2) combinations of train/test halves, compute the rank-of-IS-optimum in OOS distribution, summarize as PBO.
- **Threshold López de Prado uses in practice: PBO ≤ 0.5 is the absolute minimum (50/50 better than coin-flip); credible strategies usually target PBO ≤ 0.2.** Anything above 0.5 is overfit.
- **Trust score:** **T3.** Paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253

### D2. **Deflated Sharpe Ratio (DSR)** — Bailey & López de Prado, J. Portfolio Management 2014
- **Formula:** DSR = Φ( ( (SR − SR*) · √(T−1) ) / √(1 − γ₃·SR + (γ₄−1)/4 · SR²) ), where SR* is the multiple-testing-adjusted threshold:
  SR* = √(Var(SR_trials)) · [ (1 − γ) · Φ⁻¹(1 − 1/N) + γ · Φ⁻¹(1 − 1/N · e⁻¹) ], γ ≈ Euler-Mascheroni 0.5772, N = effective number of independent trials.
- **Threshold:** DSR ≥ 0.95 (probability the true SR > 0) for a "discovered" strategy.
- **López de Prado's empirical pronouncement (X post, July 2021):** *"On a 10-year backtest with reported Sharpe 1.5, 1.0, or 0.5, **as few as 3 trials are enough to produce a strategy that is likely false.**"*
- **Implication for LLM-as-generator:** Every LLM proposal is a *trial*. A foundry that runs 50 candidates and picks the best one has burned **≥50 effective trials**; the SR threshold to clear DSR ≥ 0.95 then is much higher than the naive Sharpe a researcher reports.
- **Trust score:** **T3.** Paper: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2460551

### D3. **Combinatorial Purged Cross-Validation (CPCV)** — *Advances in Financial Machine Learning* (2018), Ch. 12
- **Protocol:**
  - Partition the time series into **N** sequential non-overlapping groups (López de Prado recommends N=6 to N=10 for typical returns horizons).
  - For each combination of **k** test groups (typical k=2), build train/test split.
  - **Purge:** any training label whose horizon overlaps the test window is dropped.
  - **Embargo:** an additional fraction (typical 1%–2% of T) after each test window is removed from training to prevent serial correlation leakage.
  - Run all C(N, k) backtests, take distribution of OOS metrics.
- **Output:** Distribution of OOS Sharpes — not a point estimate. Use this distribution as input to DSR.
- **Trust score:** **T3.**

### D4. *Advances in Financial Machine Learning* (2018) — full book is the canonical reference
- **T3 textbook.** Chapters 11, 12, 14, 16 cover all of the above plus triple-barrier labeling and the importance of *meta-labeling* (which is, ironically, a structurally good fit for "LLM as regime-tagger, rules as trader").

### D5. *Machine Learning for Asset Managers* (López de Prado, 2020)
- Compresses the protocol; the recommended pipeline is: **PBO < 0.5 AND DSR > 0.95 AND CPCV distribution mean Sharpe > 1.0 AND minimum-track-record-length satisfied.** All four must hold.

---

## E. Named-practitioner commentary (T2-class — opinion, but informed)

### E1. **Ernest Chan** (epchan.blogspot.com, 2025; "Generative AI for Trading & Asset Management" book/workshop)
- **Position:** *Conditional, pragmatic.* LLMs are useful for **(a) translating strategy code between languages, (b) summarizing research and turning ideas into code, (c) assisting feature engineering.** He **explicitly rejects** "ChatGPT, give me a strategy that makes me millions" as not currently delivered by GenAI.
- **Stance on autonomous LLM generation:** Skeptical; emphasizes that domain expertise is the binding ingredient.
- **Trust score:** **T2** (informed opinion, not empirical proof).

### E2. **Robert Carver** (*Systematic Trading*, 2015; ongoing blog) — pre-LLM but directly applicable
- **Position:** *"Strategies should be designed, not fitted."* Anti-parameter-search ethos. The fewer parameters, the better; rules should work across markets and regimes by construction, not by tuning.
- **Implication for LLM-as-generator:** Carver's worldview is hostile to the foundry concept. The honest path is hypotheses-first, not generate-and-filter.
- **Trust score:** **T2** (informed practitioner; pre-LLM).

### E3. **Quantocracy aggregator + ML-Quants Substack #7** ("LLM Alpha and the Limits of Backtesting", 2025)
- **Argument:** LLMs generate "second-/third-order narrative alpha" that is fundamentally **not backtestable** because each narrative event is unique. Belongs in the discretionary toolkit, **not the systematic arsenal**. Sharpe ratios on "lucky headlines" are meaningless.
- **Trust score:** **T1** (single Substack, but consistent with FinSABER/StockBench evidence).
- **Takeaway:** This is the honest framing if you insist on LLMs in the loop: treat them as analyst/decision aids, not generators of validated edge.

### E4. **DeepCap.ai interview with Ernest Chan, 2025**
- Reiterates conditional view; emphasizes LLMs are weak at numerical reasoning and that the binding constraint is **the validator, not the generator**.
- **Trust score:** **T1–T2.**

---

## F. Summary scoring

| Claim | Best evidence | T-score |
|---|---|---|
| LLM-generated alphas reported to beat baselines on standard backtests | A1–A11 | T2 (consensus, weak baselines) |
| LLM-generated alphas survive contamination-free OOS without major decay | None published | **No T3 positive evidence exists** |
| Contamination causes 50–72% return decay in LLM trading agents | C1 (Profit Mirage) | **T3** |
| 40–60% of LLM-generated alphas are memorization | C2 (MemGuard-Alpha) | T2 |
| LLM agents fail to beat B&H on 20-yr / 100+ symbol clean evaluation | C3 (FinSABER) | **T3** |
| Most LLM agents marginally beat B&H on 82-day post-cutoff window | C4 (StockBench) | **T3** — but a low bar in a trending window |
| Genetic-programming auto-discovery does not beat B&H OOS | B1 (Allen & Karjalainen) | **T3** |
| Published cross-sectional anomalies decay 58% post-publication | C7 (McLean & Pontiff) | **T3** |
| López de Prado: 3 trials enough to produce likely-false strategy | D2 (Bailey & LdP 2014; X post 2021) | **T3** |
| PBO ≤ 0.5 absolute minimum, ≤ 0.2 credible; DSR ≥ 0.95 | D1, D2 | **T3** |
| Carver/Chan: LLMs as copilots, not autonomous alpha generators | E1, E2 | T2 |

---

## G. Notable absences

- **No peer-reviewed paper** as of May 2026 reports LLM-generated trading strategies that pass López-de-Prado-grade validation (PBO + DSR + CPCV) on contamination-free OOS. I searched arXiv, ACM DL, IEEE, J. Finance, RFS, JFE, JFQA, Quant Finance, Journal of Portfolio Management. **Zero hits.**
- **No paper** evaluates LLM-generated strategies on **Indian markets specifically** with proper survivorship/lookahead control. NIFTY/BANKNIFTY are completely untested in this literature.
- **No published evidence** that LLM-generated *options* strategies (the user's target market) work — the entire LLM-alpha literature is equity-cross-sectional.

This last point is critical: even if the literature were positive (it isn't), it would not transfer to the user's intended venue.
