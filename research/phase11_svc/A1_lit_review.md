# SVC — Phase A1 Literature Review

**Date:** 2026-05-21
**Author:** Nikhil S.
**Purpose:** Confirm or refute the novelty of Sequential Validation Calculus (SVC) — a Trial-Tree formalism with an MDL-augmented Deflated Sharpe Ratio and a Type-I bound under adaptive/branching research.

This review is deliberately ruthless. The cost of building a duplicate is 50-76 hours we can't repay, so the bar for "novel enough to build" is high.

---

## 1. The garden of forking paths in finance — has anyone computationally formalised it?

### 1.1 Gelman & Loken (2013/2014), "The Garden of Forking Paths"
- **URL:** http://www.stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf
- **Trust:** T3 (working paper, but the canonical reference; cited >2000 times).
- **What it does:** Names the problem philosophically. Argues that a single analysis path is implicitly one of many branches a researcher *would have* taken given different data. No formal mathematics; no tree object; no Type-I bound; no application to finance specifically.
- **What SVC adds:** A formal object (Trial-Tree DAG), a counting function (N_eff), a Type-I bound. Gelman & Loken is the *problem statement* SVC purports to solve.

### 1.2 Coqueret (2024), "Forking paths in financial economics"
- **URL:** https://arxiv.org/abs/2401.08606
- **Trust:** T3 (arXiv preprint by an established quant academic; cited but not yet peer-reviewed in a top finance journal as of search date).
- **What it does:** Imports multiverse analysis into finance. Models a study as a composition of J operators each with r_j options, so total paths P = prod r_j. Reports distribution of t-statistics across all P paths for three case studies (equity premium prediction, anomalies, risk premia). Uses AIC weights for averaging across paths. **No DAG, no adaptivity, no Type-I bound, no MDL.** Confirmed by direct read of arxiv HTML.
- **What SVC adds:**
  1. *Adaptivity*: Coqueret enumerates all paths as if symmetric and pre-specified. SVC models the researcher as adaptively choosing the next trial based on the current observed result, and tries to count this honestly.
  2. *Tree, not Cartesian product*: SVC's object is a DAG where edges encode "u informed v", which is strictly more general than P = prod r_j.
  3. *Formal Type-I guarantee*: Coqueret has none.
  4. *MDL penalty*: Coqueret uses AIC, not description length of strategy code.
- **Verdict:** Closely adjacent, not duplicative. This is the single closest piece of prior art and must be cited prominently. SVC's positioning is: *Coqueret answers "what if the researcher had explored all P paths?"; SVC answers "what should N_eff be given the actual adaptive path the researcher took, accounting for the implicit unexplored branches?"*

### 1.3 Steegen, Tuerlinckx, Gelman, Vanpaemel (2016), "Increasing Transparency Through a Multiverse Analysis"
- **URL:** https://journals.sagepub.com/doi/10.1177/1745691616658637
- **Trust:** T3 (peer-reviewed, Perspectives on Psychological Science).
- **What it does:** Originator of "multiverse analysis": enumerate all reasonable analytic decisions, run all of them, report distribution. Psychology context.
- **What SVC adds:** Same as Coqueret — multiverse is enumerative, not adaptive, and has no Type-I bound.

### 1.4 Bell, Kampman, Dodge, Lawrence (2022), "Modeling the Machine Learning Multiverse" (NeurIPS)
- **URL:** https://arxiv.org/abs/2206.05985
- **Trust:** T3 (NeurIPS-published).
- **What it does:** Multiverse over ML hyperparameters with Gaussian-Process surrogate + Bayesian experimental design. Focus is *efficient exploration* of the multiverse, not *honest accounting* for adaptive exploration.
- **What SVC adds:** Different question. Bell-et-al asks "how do I sample the multiverse efficiently?"; SVC asks "given that I already sampled adaptively, how do I penalise the resulting Sharpe?"

---

## 2. Sequential / adaptive multiple testing — is it imported to backtesting?

### 2.1 Foster & Stine (2008), "Alpha-investing"
- **URL:** https://deanfoster.net/research/edc.pdf
- **Trust:** T3 (JRSS-B).
- **What it does:** Sequential mFDR control via an alpha-wealth budget: each test costs alpha, each rejection earns wealth back. Hypothesis stream is exogenous.
- **What SVC adds:** Alpha-investing assumes hypotheses arrive *exogenously*. In backtesting, the researcher *generates* the next hypothesis based on the previous outcome — the hypothesis stream is endogenous to the realised path. SVC's contribution is to model this endogenous branching explicitly via the Trial-Tree. Also, alpha-investing controls mFDR, not Type-I on a single accepted strategy.

### 2.2 Javanmard & Montanari (2018), "Online rules for control of FDR" (LOND, LORD)
- **URL:** https://web.stanford.edu/~montanar/RESEARCH/FILEPAP/onlineFDR.pdf
- **Trust:** T3 (Annals of Statistics).
- **What it does:** Online FDR control where each hypothesis's significance threshold depends on time-of-last-discovery (LORD) or count-of-discoveries (LOND). Assumes independent (or weakly dependent) p-values from an exogenous stream.
- **What SVC adds:** Same gap as alpha-investing. Plus, LORD/LOND have not been applied to backtest validation in published work I can find (T2 confidence: extensive search returned no finance-specific application).

### 2.3 Ramdas et al. (2018), "SAFFRON"
- **URL:** https://arxiv.org/pdf/1802.09098
- **Trust:** T3 (ICML).
- **What it does:** Adaptive online FDR; estimates fraction of true nulls for power.
- **What SVC adds:** Same gap. Online-FDR is a *toolkit* SVC could borrow; it is not a finished framework for backtest validation.

### 2.4 Ramdas et al. (2018), "DAGGER: Sequential FDR control on DAGs"
- **URL:** https://arxiv.org/abs/1709.10250
- **Trust:** T3 (NeurIPS).
- **What it does:** Tests hypotheses on a DAG; rejection of child requires rejection of parent (logical hierarchy). The DAG is **fixed a priori**.
- **What SVC adds:** SVC's DAG is *constructed by the researcher's adaptive choices*, not given a priori. DAGGER's logical-implication semantics ("parent must reject before child") is entirely different from SVC's research-history semantics ("u's result informed the choice to run v"). DAGGER's FDR proof technique may, however, be a useful starting point for SVC's Type-I proof.

### 2.5 Lei & Fithian (2018), "AdaPT"
- **Trust:** T3 (JRSS-B).
- **What it does:** Adaptive FDR control using auxiliary covariates while preserving Type-I via masking. Not finance-specific.
- **What SVC adds:** AdaPT's masking trick could be relevant for SVC's proof, but no published application to backtest validation exists.

**Conclusion on Section 2:** A rich generic toolbox of online/adaptive FDR exists, and SVC will benefit from it (likely cite as machinery the proof rests on), but **none of this toolbox has been imported into backtest validation in a published paper**. That is a real gap.

---

## 3. MDL / Kolmogorov complexity in finance

### 3.1 Brandouy, Delahaye, Ma, Zenil (2015), "Estimating the Algorithmic Complexity of Stock Markets"
- **URL:** https://arxiv.org/abs/1504.04296
- **Trust:** T3.
- **What it does:** Estimates K-complexity of *price series* via lossless compression. Not of strategy code, not for overfitting penalisation.
- **What SVC adds:** Inverts the object — SVC's K(.) is description length of the *strategy*, not of the data. Distinct contribution.

### 3.2 Paterlini & Krink (2016), "Noise Fit, Estimation Error and a Sharpe Information Criterion"
- **URL:** https://arxiv.org/pdf/1602.06186
- **Trust:** T3.
- **What it does:** Defines an AIC-style penalty on the Sharpe ratio to account for noise fitting from K parameters. Penalty is proportional to K/T.
- **What SVC adds:** SIC penalises *parameter count*. MDL penalises *full description length* (in bits) of the strategy code, which dominates parameter count by also charging for structural choices (e.g., "use a rolling 20-day window" vs. "use an exponentially weighted variance"). SIC is the closest single penalty in finance to SVC's MDL term. The contribution of SVC's MDL term over SIC is qualitative: it counts choices that don't surface as free parameters.
- **Note:** This is a real overlap and the paper to cite explicitly. SVC's MDL term is an *extension*, not a novel idea ex nihilo.

### 3.3 Grunwald & Roos (2019), "Minimum Description Length Revisited"
- **URL:** https://arxiv.org/pdf/1908.08484
- **Trust:** T3.
- **What it does:** Modern MDL theory. Not finance-specific.
- **What SVC adds:** SVC's contribution is *applying* this machinery to backtest validation.

### 3.4 Miyaguchi & Yamanishi (2018), "High-dimensional Penalty Selection via MDL"
- **URL:** https://arxiv.org/abs/1804.09904
- **Trust:** T3.
- **What it does:** Use LNML/MDL to pick regularisation strength. Not finance.
- **What SVC adds:** SVC applies a similar idea to the strategy-acceptance threshold problem, not to regularisation.

**Conclusion on Section 3:** No published work combines MDL with Deflated Sharpe Ratio or with backtest validation specifically. Paterlini's SIC (AIC-style) is the closest neighbour. SVC's MDL term is a small but real novelty.

---

## 4. López de Prado et al. — recent extensions to DSR/PBO

### 4.1 Bailey & López de Prado, "False Strategy Theorem" (AMM 2021; SSRN revised through Nov 2025)
- **URL:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3221798 ; https://www.tandfonline.com/doi/abs/10.1080/00029890.2021.1965068
- **Trust:** T3 (peer-reviewed in American Mathematical Monthly).
- **What it does:** Proves that the max of N iid SR estimates grows like sqrt(2 log N), giving the deflation formula used by DSR. **N is exogenous and static.** No tree, no researcher decisions. SSRN revisions through 2025 do not (per public abstract and discussions) introduce a tree formalism — they refine constants, add IID-frequency arguments.
- **What SVC adds:** Replaces the static N with the tree-derived N_eff. The theorem's max-of-N machinery is the *engine* SVC's Type-I bound will likely reuse, but the *plumbing* — what N to plug in for an adaptive researcher — is what SVC contributes.

### 4.2 Bailey, Borwein, López de Prado, Zhu (2017), "The Probability of Backtest Overfitting" (CSCV)
- **URL:** https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- **Trust:** T3 (Journal of Computational Finance).
- **What it does:** PBO via combinatorially symmetric cross-validation across a fixed set of N strategies.
- **What SVC adds:** Same gap — N is static.

### 4.3 López de Prado, Lipton, Zoonekynd (2025), "A Protocol for Causal Factor Investing"
- **URL:** https://www.adialab.ae/research-series/a-protocol-for-causal-factor-investing ; SSRN 4774522 / 5131050
- **Trust:** T3.
- **What it does:** A 7-step research protocol grounded in causal inference (DAGs of *causal relations between economic variables*, not of research trials). Critiques associational factor zoo.
- **What SVC adds:** Different DAG object. LdP's DAG is over the *economic causal structure of returns*. SVC's DAG is over *the researcher's experimental history*. No overlap in object, though SVC should cite this as the broader programme it sits within.

### 4.4 López de Prado et al. — adaptive/sequential DSR extension?
- **Search result:** None found through 2026-05. The False Strategy Theorem revisions, the CPCV literature, and the Causal Factor Investing programme do not extend to adaptive/sequential research. (T2 confidence: extensive search of SSRN, arXiv, Google Scholar through 2026-05.)
- **What SVC adds:** This is the actual gap.

---

## 5. Adaptive designs from clinical trials — imported to backtesting?

### 5.1 Lan-DeMets alpha spending, O'Brien-Fleming boundaries, group sequential design
- **Trust:** T3 (canonical clinical-trials literature).
- **What it does:** Allocate a Type-I budget across interim looks at accumulating data.
- **What SVC adds:** Not directly applied to backtesting in published work I can find (T2 confidence). However, alpha-spending is *one valid candidate* for SVC's N_eff function — i.e., we could treat each tree node as an interim look and spend alpha across the path. This is a useful machinery to borrow, and it does not constitute prior art that pre-empts SVC.

---

## 6. Recent quant arXiv (2023-2026)

### 6.1 Sequential Cauchy Combination Test (2303.13406)
- **What it does:** Sequential multiple-testing for alpha discovery / drift bursts.
- **What SVC adds:** Different problem — about *combining* p-values sequentially, not about counting researcher branching.

### 6.2 "Backtest overfitting in the machine learning era" (Science Direct 2024)
- **What it does:** Compares OOS testing methods (CPCV vs. walk-forward etc.) on synthetic data. No new formalism.
- **What SVC adds:** Not competing.

### 6.3 No paper found matching: "trial accounting", "sequential research validation in finance", "adaptive backtest validation" as a *framework* (T2 confidence: searched arXiv q-fin, SSRN, Google Scholar 2023-2026).

---

## Novelty verdict: **partial-overlap, leaning novel**

SVC is **not pre-empted**. The closest pieces of prior art are:

1. **Coqueret 2024** (forking paths in financial economics) — multiverse, enumerative, no DAG of adaptive choices, no Type-I bound. SVC's adaptive-DAG framing is distinct.
2. **Bailey & López de Prado (False Strategy Theorem + DSR + PBO)** — static N. SVC replaces the static N with a tree-derived N_eff.
3. **Paterlini & Krink Sharpe Information Criterion** — AIC-style penalty on SR. SVC's MDL term is a strict extension (counts non-parameter description length).
4. **Online-FDR literature (Foster-Stine, LORD, SAFFRON, DAGGER, AdaPT)** — generic machinery, not applied to backtesting in published work. SVC can (and probably should) build its Type-I proof on this machinery rather than from scratch.

**What SVC adds that no published work has done:**
- A formal **Trial-Tree DAG with edges encoding researcher-decision dependence** (not pre-specified logical hierarchy as in DAGGER, not Cartesian-product multiverse as in Coqueret/Steegen).
- A **Type-I bound on a single-strategy acceptance rule** under arbitrary adaptive branching (rather than FDR over a stream as in online-FDR work, or static deflation as in DSR).
- An **MDL term added to DSR** (vs. SIC's AIC term and DSR's no-complexity term).
- A **case study on a real adaptive research history** (our 390-trial registry), which is methodologically novel — published work uses synthetic or cross-sectional data.

**What SVC must concede in the paper:**
- The False Strategy Theorem provides the max-of-N machinery that SVC's bound will likely reuse. SVC's contribution is the N_eff construction, not the max-order-statistic theorem.
- Coqueret 2024 is close enough that SVC must explicitly differentiate "multiverse enumeration over all paths" (Coqueret) from "honest accounting of the realised adaptive path with implicit unexplored branches" (SVC) in the paper's intro.
- The MDL term is a small extension of Paterlini's SIC, not a wholly novel idea.

**Kill-criterion check:** None of the kill criteria from `00_plan.md` triggered. No published work computationally formalises adaptive backtest validation with a Type-I bound. We proceed to A2.

**Recommended positioning of the paper:**
*"We extend Bailey & López de Prado's Deflated Sharpe Ratio from the static-N regime to the adaptive-research regime by formalising research history as a Trial-Tree DAG and introducing an MDL-augmented acceptance rule with a provable Type-I bound. Our framework operationalises Gelman & Loken's garden-of-forking-paths critique computationally, complementing Coqueret (2024)'s multiverse-enumeration approach with an honest accounting of the actually-realised adaptive path."*

That positioning is defensible. Proceed to A2.

---

## Sources (all consulted via WebSearch / WebFetch on 2026-05-21; cached index at `/Users/Nikhil-S/Projects/Trading/research/sources/raw/phase11/sources_index.md`)

- [Coqueret 2024 — Forking paths in financial economics](https://arxiv.org/abs/2401.08606)
- [Bailey & LdP — False Strategy Theorem (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3221798) and [AMM 2021](https://www.tandfonline.com/doi/abs/10.1080/00029890.2021.1965068)
- [Bailey, Borwein, LdP, Zhu — Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)
- [Bailey & LdP — Deflated Sharpe Ratio](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- [LdP & Zoonekynd — A Protocol for Causal Factor Investing](https://www.adialab.ae/research-series/a-protocol-for-causal-factor-investing)
- [Gelman & Loken — Garden of Forking Paths](http://www.stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf)
- [Steegen et al. — Multiverse Analysis](https://journals.sagepub.com/doi/10.1177/1745691616658637)
- [Bell et al. — Modeling the ML Multiverse (NeurIPS 2022)](https://arxiv.org/abs/2206.05985)
- [Foster & Stine — Alpha-investing](https://deanfoster.net/research/edc.pdf)
- [Javanmard & Montanari — Online FDR (LORD)](https://web.stanford.edu/~montanar/RESEARCH/FILEPAP/onlineFDR.pdf)
- [Ramdas et al. — SAFFRON](https://arxiv.org/pdf/1802.09098)
- [Ramdas et al. — DAGGER](https://arxiv.org/abs/1709.10250)
- [Paterlini & Krink — Sharpe Information Criterion](https://arxiv.org/pdf/1602.06186)
- [Brandouy et al. — Algorithmic Complexity of Stock Markets](https://arxiv.org/abs/1504.04296)
- [Grunwald & Roos — MDL Revisited](https://arxiv.org/pdf/1908.08484)
- [Miyaguchi & Yamanishi — MDL Penalty Selection](https://arxiv.org/abs/1804.09904)
- [Harvey, Liu, Zhu — ...and the Cross-Section of Expected Returns](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2249314)
- [Sequential Cauchy Combination Test](https://arxiv.org/pdf/2303.13406)
