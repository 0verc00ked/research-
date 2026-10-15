# RMT + PCA Statistical Arbitrage — Honest Viability Review

**Date:** 2026-05-21
**Author:** Claude Opus 4.7 (1M ctx), in research mode for Nikhil
**Question:** Does Random Matrix Theory + PCA-residual mean-reversion (Avellaneda-Lee 2010 class) yield tradable edge for a ₹15–25k Indian retail operator?
**TL;DR:** **No. Do not build.** Capital floor is at least 1–2 orders of magnitude above what we have; the canonical strategy's published OOS Sharpe has decayed from 1.44 (1997-2007) → 0.9 (2003-2007) → no peer-reviewed positive evidence post-2010 net of realistic costs at retail scale; zero published Indian-market evidence on this strategy class at retail capital; build cost competes against E1/E3 work that has a higher probability of yielding usable artifacts.

Cumulative project context: **N_trials=383 honest, 0 survivors.** This review is to decide whether to spend the *next* trial-budget on RMT/PCA. Conclusion below is "no" with quantified reasoning.

---

## §1 The mathematical core (what RMT actually tells us)

### 1.1 Marchenko-Pastur (noise null distribution)

For an N×T return matrix of i.i.d. zero-mean unit-variance returns, the empirical correlation matrix's eigenvalues are asymptotically (N→∞, T→∞, Q=T/N fixed) distributed on the bulk:

```
λ_± = (1 ± 1/√Q)²    with density ρ(λ) = (Q / 2π λ) · √((λ_+ − λ)(λ − λ_−))
```

Eigenvalues **inside** [λ_−, λ_+] are statistically indistinguishable from noise. Eigenvalues **outside** (typically the top 1, then a sector-cluster cloud of ~10-30) carry signal. (T3: Marchenko & Pastur 1967, Plerou et al. 1999 Phys. Rev. Lett., Laloux et al. 1999 Phys. Rev. Lett.)

### 1.2 Canonical empirical results

- **Plerou et al. (1999, 2002)** — S&P 500: ~94% of eigenvalues fall inside the MP bulk; the top eigenvalue ≈ 25× λ_+ is "the market"; ~10-20 deviating eigenvalues correspond to sectors. (T3: Phys. Rev. Lett. 83, 1471; Phys. Rev. E 65, 066126.)
- **Laloux, Cizeau, Bouchaud, Potters (1999, 2000)** — Same conclusion on US data; introduced **eigenvalue clipping** (replace bulk eigenvalues with their mean, keep top-k eigenvalues unchanged) for Markowitz portfolio construction. Out-of-sample portfolio variance dropped ~30% vs raw sample covariance. (T3: Phys. Rev. Lett. 83, 1467; Int. J. Theor. Appl. Finance 3.)
- **Bouchaud & Potters textbook** — *A First Course in Random Matrix Theory* (Cambridge, 2021) and *Cleaning large correlation matrices: tools from RMT* (arXiv:1610.08104) — current state-of-the-art on optimal Rotationally Invariant Estimators (RIEs), including Ledoit-Péché optimal nonlinear shrinkage. (T3: textbook + peer-reviewed.)

**Key caveat I almost never see retail traders cite (T2/T3):** the 1999 MP fit on S&P held cleanly because returns were *approximately* stationary in that window. More recent multi-decade studies (e.g., arXiv:2507.14325, 2025) explicitly note **"Marchenko-Pastur fits reasonably well only for 1990s data; does not hold for more recent financial data"** — because non-stationarity, fat tails, and structural breaks inflate the bulk in ways MP cannot capture. This is a non-trivial degradation of the null model that the whole strategy class depends on.

---

## §2 Avellaneda-Lee 2010 — the canonical PCA stat-arb paper

### 2.1 Methodology (what you'd actually code)

1. Pick a universe of N≥100 liquid stocks. Use daily returns over a rolling window T (typically 60–252 days, so Q=T/N ≈ 0.5–2.5).
2. Compute correlation matrix R; do eigendecomposition.
3. Keep top-k eigenvectors (k chosen by MP threshold or fixed at 15). These are your **risk factors**.
4. For each stock i, regress its returns on the k factors → factor loadings (betas) + residual ε_i(t).
5. Model the cumulative residual X_i(t) = Σ ε_i(s) as an Ornstein-Uhlenbeck mean-reverting process: dX = κ(m − X)dt + σ dW.
6. Compute s-score: s_i = (X_i − m_i) / σ_eq,i.
7. Trade: enter long when s < −1.25, short when s > 1.25; exit when |s| < 0.5. Hedge with the factor exposure.
8. Rebalance daily; positions are dollar-neutral / beta-neutral.

(T3: Avellaneda & Lee, *Quantitative Finance* 10(7), 761–782, 2010. SSRN:1153505.)

### 2.2 Published OOS performance — the honest numbers

| Period | Strategy variant | Sharpe (net of costs) | Source / Trust |
|---|---|---|---|
| 1997–2002 | PCA, k=15, daily | ~1.9 | T3 Avellaneda-Lee 2010 |
| 2003–2007 | PCA, k=15, daily | **0.9** | T3 Avellaneda-Lee 2010 |
| 1997–2007 | PCA full sample | 1.44 | T3 Avellaneda-Lee 2010 |
| 2003–2007 | ETF-based variant with volume | 1.51 | T3 Avellaneda-Lee 2010 |
| 2007 liquidity crunch (Aug) | PCA daily | sharp drawdown documented | T3 Avellaneda-Lee 2010 §5 |
| Post-2010 retail-realistic | **No peer-reviewed positive OOS at retail scale** | — | T2 (absence of evidence) |
| 2016–2024 US, deep-learning factor residual (CNN/Transformer) | Out-of-sample Sharpe occasionally >10 (gross, large universe, institutional execution) | claims are real but T2 — replication paper, no transaction cost stress | arXiv:2412.11432 |
| ~2001–2025 US, Attention Factor model | OOS Sharpe ~4.0 gross, **2.3 net of TC** on large-cap | T2/T3 arXiv:2510.11616 |
| 2020–2025 Polish equities, LSTM + PCA pairs | Demonstrated edge over baseline (no production track record) | T2 arXiv:2512.02037 |

**Honest reading:** The canonical strategy's Sharpe decayed from ~1.9 to ~0.9 over 1997–2007 — i.e., **the edge was visibly disappearing inside the original paper's own sample**. Post-2010, the literature has shifted to deep-learning extensions because the linear PCA version no longer publishes net-of-cost Sharpe in defensible regimes. The "Sharpe>10" claims in recent ML papers are all *gross* and at institutional execution assumptions; the one paper that bothers to report *net of transaction cost* lands at ~2.3 on the largest-cap US universe with daily rebal — and that's the upper bound, not the median.

### 2.3 Why the strategy decays

- **Crowding.** Once PCA stat-arb became table stakes at every prop shop by ~2005, residuals mean-revert faster than the half-life implied by daily-bar data. Strategies that require >1-day holding to extract the s-score signal get arbitraged before you trade.
- **Structural break in correlation matrix.** Post-2008 the equity market shows persistent regime shifts (Bouchaud & Potters 2016 §5 — T3). The k=15 factor model's loadings need to be re-estimated faster than its statistical significance allows.
- **Transaction cost asymmetry.** As Mean Reversion Pays But Costs (arXiv:1103.4934, T2) shows analytically, in the presence of linear TC, a "buffer" of width ∝ TC^(1/3) is needed before each trade — and at retail cost (5–25 bps round-trip), that buffer eats the bulk of the signal at daily frequency.

---

## §3 Indian-market evidence (or lack of it)

**Bottom line: there is essentially zero peer-reviewed, OOS-clean published evidence of Avellaneda-Lee-style PCA stat-arb at retail capital on Indian equities.** (T2 — absence of evidence after targeted search; I cannot prove none exists, but it does not surface on Google Scholar, IDEAS/RePEc, arXiv with India-NSE-PCA-stat-arb queries.)

What *does* exist on Indian markets:
- **Cointegrated pairs trading (NOT the same as PCA residual)** — QuantInsti EPAT projects 2015–2025 on 25 NSE large-caps; ₹5L per pair capital; 5 bps/leg TC; reports walk-forward results but on a small handful of pairs, not the N≥100 PCA universe. (T1 — student projects, not peer-reviewed.)
- **Generic "stat-arb works in India" blog claims** — finfluencer-grade. T0.
- **Co-location at NSE** — institutional infrastructure required to extract intraday stat-arb. Retail explicitly priced out. (T3 NSE.)

What does **not** exist:
- Any peer-reviewed Indian-equity PCA-residual paper with net-of-cost OOS Sharpe.
- Any retail-capital backtest (< ₹1L total deployable) showing the strategy clears costs.
- Any documented case of an Indian retail operator running this profitably.

If you assume the strategy decays in proportion to information dissemination + TC inflation, the Indian-market analogue in 2026 is almost certainly worse than the US 2010 number (~0.9 Sharpe gross, ~0 net at retail cost): the Indian universe of liquid (top 200 NSE) stocks is smaller, sector concentration in financials is higher (less effective dimensionality after first eigenvector), STT + GST + stamp duty + slippage round-trip is ~15–25 bps on small caps, and SEBI's algo framework restricts retail intraday rebalancing dynamics. (T2/T3 mix.)

---

## §4 Implementation complexity into our harness

Realistic build estimate, integrating into existing `agent_trader/` scaffold:

| Component | LoC | Hours | Notes |
|---|---:|---:|---|
| Universe selection (top-N NSE liquid) + survivorship-clean point-in-time data | ~200 | 8–12 | Hardest single piece; we already have Kite→qlib adapter scaffold, but need delisting-aware membership history |
| Rolling correlation matrix + eigendecomposition + MP clipping | ~150 | 4 | numpy.linalg.eigh; well-understood |
| Residual extraction (factor regression, OU fitting via AR(1)) | ~200 | 6 | Per-stock OLS + Hurst/half-life estimation |
| S-score signal + dollar-neutral portfolio construction | ~250 | 8 | Constraint: integer share rounding crushes small-capital signal — see §5 |
| Cost model (STT, GST, stamp, slippage, impact) per-trade | ~150 | 4 | We have skeleton from W1-2 |
| CPCV / PBO / DSR plumbing through harness | ~50 | 4 | Reuses `validation/` |
| Walk-forward orchestrator + trial_log integration | ~150 | 6 | |
| **Total** | **~1150** | **40–50 hours** | Without an LLM helping; with LLM ~30 hours; plus 5–10 hours of debugging |

This is **2–3 weeks of focused work** to build and run once. Each parameter sweep is a new entry in `trial_log`. Realistically you'd test 5–10 hyperparameter configurations honestly → adds 5–10 to N_trials, pushing total to 388–393. DSR threshold rises accordingly.

---

## §5 Capital sensitivity — the killshot

This is where the strategy dies for our user, regardless of edge.

### 5.1 Universe and position sizing math

PCA stat-arb requires:
- N ≥ 100 stocks for the MP bulk vs signal split to even be meaningful (Q=T/N condition). With N=50 the noise bulk dominates and you can't separate signal eigenvectors cleanly. (T3 Bouchaud-Potters textbook.)
- At any given time, the strategy typically has positions in 20–50 stocks (those with |s| > threshold).
- Each position must be **roughly equal-dollar** to make the residual-extraction math work (otherwise you're long the largest stocks by default, which is just a beta bet).

### 5.2 Indian-retail capital reality

With ₹15–25k total capital, dollar-neutral across (say) 30 positions = ~₹500–800 *gross exposure per leg* (≈ ₹250–400 net long, ₹250–400 net short). But:

- **No legal short-selling of Indian equities for retail at this size.** Securities Lending and Borrowing (SLB) exists but has lot-size and margin requirements that exclude sub-lakh participation. The only practical "short" is intraday MIS — closed by 3:20 PM and so excludes overnight residual mean reversion which is the entire mechanism. (T3 SEBI/NSE.)
- **Fractional shares unavailable on Indian exchanges** for resident retail. Minimum is 1 share. A stock at ₹3,000 (e.g., RELIANCE) = ₹3,000 minimum position = 12–20% of total capital just to take one leg. Integer rounding error on 30 positions of ~₹500 each, where individual share prices range ₹50–₹5,000, makes the residual portfolio's beta-neutrality drift dominate the mean-reversion signal. (T3 NSE; T2 fractional-share absence.)
- **F&O futures alternative:** NIFTY-50 stock futures exist for ~190 names. Lot sizes designed for SPAN margin ≥ ₹1–3L per lot. Completely out of reach.
- **Daily rebalancing TC at retail:** ~15–25 bps round trip per leg on small caps × 30 legs × ~daily turnover = the signal needs to clear ~5–8% annualized just to break even, before paying us anything. Avellaneda's *net* 0.9 Sharpe was at institutional TC of ~3–5 bps round-trip.

### 5.3 Quantified verdict

**Capital floor to run this honestly:**
- Bare minimum to take 30 ~equal positions with 1-share rounding noise < 20%: **₹3–5 Lakh** (T2 estimate, my analysis from share-price distribution of NSE-100).
- Floor for shorts to work via SLB / single-stock futures: **₹5–10 Lakh** SPAN-friendly.
- Floor where TC drag drops below half the published gross Sharpe: **₹10 Lakh+** with broker fee tiering negotiated.

**Our capital: ₹15–25k = 1–2 orders of magnitude below the floor.** No clever rescaling fixes this. This is dispositive.

---

## §6 2023–2026 wrinkles — does the new literature change the verdict?

Recent developments in RMT-based portfolio construction:

1. **Optimal nonlinear shrinkage (Ledoit-Wolf, Ledoit-Péché, RIE)** — Bun, Bouchaud, Potters 2016/2017 (T3) — strictly better than MP clipping; ~5–15% additional OOS variance reduction. Helps **portfolio construction** (Markowitz inversion); does NOT add edge to the *signal* in stat-arb. Marginal to our question.
2. **Hierarchical clustering refinements (HRP / NCO)** — López de Prado 2016, Pantaleo et al. 2024 (T2/T3) — cluster-then-shrink two-step estimators. Used for risk parity / variance minimization, not directly for mean-reversion signal generation. Tangential.
3. **Autoencoder + deep-learning residual extraction (2021–2025)** — Guijarro-Ordonez et al. (arXiv:2106.04028, T2), Cartea et al. arXiv:2402.08233 (T2), arXiv:2412.11432 (T2), arXiv:2510.11616 (T2/T3) — claim Sharpe >2 net of TC on large-cap US. Reproduction-uncertain, training-cost-high, requires GPU + 20+ years clean data + ~500-stock universe. Even if real, lifts the *technique* not the *capital floor*. Doesn't rescue retail.
4. **End-to-end policy learning (2024)** — embed AE in trading policy, backprop risk-adjusted return. Cute but exacerbates overfit-by-trial-count problem we already understand from D5 postmortem. PBO will likely flag.
5. **Non-stationarity-aware MP / dynamic-spectrum models (arXiv:2507.14325, 2025, T2)** — confirms what we already suspected: vanilla MP doesn't fit modern data well. Sharpens the *diagnosis*, not the *strategy*.

**None of these wrinkles change the answer for retail at ₹15–25k.** They all assume an N≥200, institutional-cost, daily-rebal regime that is structurally inaccessible.

---

## §7 Comparison to project's existing options

| Path | Build hours | Capital floor | Prob. tradable edge | Artifact value |
|---|---:|---:|---:|---|
| RMT/PCA stat-arb (this review) | 40–50 | ₹3–10 L | <5% at our capital | Low (can't even paper-trade meaningfully) |
| E1 — microstructure seasonality (already in CONCRETE_PLAN) | 30–40 | ₹15k | 10–20% | Medium |
| E2 — disclosure NLP (already in plan) | 50–60 | ₹15–25k | 5–15% | High (reusable for security analyst day-job) |
| E3 — bounded-ruin allocator (already in plan) | 30–40 | N/A | ~80% as artifact | Very high |
| Option α from D3 postmortem (package + publish) | 15–20 | ₹0 | N/A | High (real OSS contribution) |

**RMT/PCA is dominated on every dimension by the items already in our plan.**

---

## §8 Trust-scored claim summary

| Claim | Trust |
|---|---|
| MP distribution describes noise eigenvalues of i.i.d. correlation matrices | T3 (Marchenko-Pastur 1967) |
| Plerou + Laloux 1999 found ~94% S&P eigenvalues in bulk | T3 (Phys. Rev. Lett.) |
| Avellaneda-Lee 2010 PCA strategy: gross Sharpe 1.44 (1997-2007), 0.9 (2003-2007) net of "modest" institutional costs | T3 (Quant. Finance 2010) |
| Post-2010 peer-reviewed net-of-cost OOS evidence for linear PCA stat-arb at retail scale | T0 (absent; could not find) |
| Indian-market PCA stat-arb peer-reviewed evidence | T0 (absent) |
| Recent deep-learning extensions claim Sharpe 2–10 gross, ~2.3 net of TC on large-cap US | T2 (arXiv preprints, no production track record) |
| Indian retail cannot short stocks at < ₹1L capital | T3 (SEBI/NSE) |
| Indian exchanges do not offer fractional shares to residents | T3 (NSE) |
| Capital floor for honest PCA stat-arb implementation ≥ ₹3L | T2 (my derived estimate from share-price distribution + cost model) |
| Strategy decays over time due to crowding | T2 (Avellaneda-Lee's own data + general quant lit) |
| MP fit degrades on post-2010 data | T2 (arXiv:2507.14325, 2025) |

No T0/T1 claim is load-bearing in this verdict. The verdict is load-bearing on the T3 capital-floor facts (no shorts, no fractionals, lot-size minimums on F&O) — those are the killshots.

---

## §9 Final verdict

**(a) Honest probability this approach yields tradable edge for our user (₹15–25k, Indian retail, daily-bar resolution):**
**< 3%.** The capital floor alone makes the strategy non-implementable in a form that resembles the published methodology. Even a heroic adaptation (e.g., 10-stock PCA on cash-only longs with broad-market hedge via NIFTYBEES ETF) would (i) violate the N≥100 statistical condition that makes the MP framework meaningful and (ii) collapse to "trade idiosyncratic residuals on ~10 stocks vs NIFTY" which is just a noisy long-only mean-reversion strategy already covered (and rejected) in our 383-trial precedent.

**(b) Build cost in hours:**
**40–50 hours** to implement honestly into the existing harness (universe + RMT + residual extraction + signal + cost-model + CPCV/PBO/DSR plumbing). Plus 5–10 hours per honest hyperparameter sweep. Realistic total to a "done, tested, postmortem-written" state: **60–70 hours = 2–3 focused weeks**.

**(c) Capital floor required (for the strategy to be implementable, not yet profitable):**
- **≥ ₹3–5 Lakh** for the cash-leg-only version with 30 long positions and reasonable rounding error.
- **≥ ₹5–10 Lakh** if dollar-neutral with SLB shorts or single-stock futures.
- **≥ ₹10 Lakh** to drop TC drag below half of historically published gross Sharpe.

This is 12–40× our current capital ceiling, and that's just to *run* the strategy honestly — not to expect profit.

**(d) Yes / No recommendation:**

**NO. Do not build.**

Rationale, ranked:
1. **Capital floor dispositive.** ₹15–25k cannot take the positions the strategy needs. No engineering elegance fixes this.
2. **Published evidence trajectory is hostile.** Canonical strategy's Sharpe halved within its own 1997-2007 sample; post-2010 the literature shifted to deep-learning variants that require GPU + institutional data + 500-stock universes — none accessible to us.
3. **Zero Indian-market evidence.** We'd be the first to publish either confirming or refuting, with all the false-positive risk that implies on our N_trials=383 baseline.
4. **Dominated by existing plan items.** E1 (microstructure), E2 (disclosure NLP), E3 (bounded-ruin allocator), and Option α (package and publish) all have higher artifact value or higher edge probability at our capital and roughly equal-to-lower build cost.
5. **Plan-integrity argument.** D3/D1/D5 postmortem already established (correctly) that we have no edge at daily-bar resolution on our existing feature set. PCA residual extraction is a *richer feature*, not a *different resolution* — and adds 100+ new trial-degrees-of-freedom that will inflate DSR thresholds without a corresponding edge story.

**Recommendation if you still want exposure to the RMT idea:** spend 4–6 hours reading Bouchaud & Potters (2021) Ch. 12 + Avellaneda-Lee (2010) + the Cartea 2024 AE paper, write a one-paragraph note in `phase10_novel/` summarizing what you learned, and move on. Total time: half a day, zero build, zero capital risk, full intellectual benefit. This is the right cost-benefit point.

---

## §10 Sources

Core (T3):
- Marchenko, V. A. & Pastur, L. A. (1967). Distribution of eigenvalues for some sets of random matrices.
- Plerou, V. et al. (1999). Universal and Nonuniversal Properties of Cross Correlations in Financial Time Series. *Phys. Rev. Lett.* 83, 1471.
- Laloux, L., Cizeau, P., Bouchaud, J.-P., Potters, M. (1999). Noise Dressing of Financial Correlation Matrices. *Phys. Rev. Lett.* 83, 1467.
- Avellaneda, M. & Lee, J.-H. (2010). Statistical Arbitrage in the U.S. Equities Market. *Quantitative Finance* 10(7), 761–782. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1153505
- Bouchaud, J.-P., Potters, M. (2021). *A First Course in Random Matrix Theory*. Cambridge University Press.
- Bun, J., Bouchaud, J.-P., Potters, M. (2016). Cleaning large correlation matrices: tools from RMT. arXiv:1610.08104.

Recent (T2):
- Guijarro-Ordonez, J., Pelger, M., Zanotti, G. (2021/2024). Deep Learning Statistical Arbitrage. arXiv:2106.04028.
- Cartea et al. (2024). End-to-End Policy Learning of a Statistical Arbitrage Autoencoder. arXiv:2402.08233.
- A Deep Learning Approach for Trading Factor Residuals (2024). arXiv:2412.11432.
- Attention Factors for Statistical Arbitrage (2025). arXiv:2510.11616.
- Statistical Arbitrage in Polish Equities Market (2025). arXiv:2512.02037.
- Eigenvalue Distribution of Empirical Correlation Matrices for Multiscale Complex Systems (2025). arXiv:2507.14325.
- Denoising Complex Covariance Matrices with Hybrid ResNet and RMT (2025). arXiv:2510.19130.

Indian-context (T1/T2):
- QuantInsti EPAT — Cointegrated Pairs Trading Strategy in Indian Equity Market (2015–2025). https://blog.quantinsti.com/cointegrated-pairs-trading-indian-equity-market-epat-project/
- NSE Clearing — Margins / SPAN requirements. https://www.nseclearing.in/risk-management/equity-derivatives/margins (T3)
- Hudson & Thames `arbitragelab` — PCA Approach documentation. https://hudson-and-thames-arbitragelab.readthedocs-hosted.com/en/latest/other_approaches/pca_approach.html (T1/T2 — open-source library docs)

Project-internal:
- `/Users/Nikhil-S/Projects/Trading/research/CONCRETE_PLAN.md`
- `/Users/Nikhil-S/Projects/Trading/research/wont_work_vs_might_work.md`
- `/Users/Nikhil-S/Projects/Trading/research/phase9_research_engine/D3_D1_D5_postmortem.md`
- `/Users/Nikhil-S/Projects/Trading/research/trust_rubric.md`
