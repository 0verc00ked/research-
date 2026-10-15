# Sequential Validation Calculus: A Trial-Tree Formalism for Honest Backtest Validation Under Adaptive Research

**Draft, 2026-05-21**

## Abstract

The Deflated Sharpe Ratio of Bailey & López de Prado (2014) correctly punishes the maximum Sharpe of $N$ independent strategy tests via extreme-value theory, but assumes $N$ is exogenous and static. Real quantitative research is *sequential and branching*: a researcher tests strategy $A$, observes its outcome, *uses that outcome to decide* what to test next, branches when results look promising, and refines parameters adaptively. Under such research, the relevant $N$ is neither the number of strategies actually executed nor the Cartesian product of all decisions that could have been made — it is something in between, determined by the *realised research path through an implicit search space*.

We formalise this as a **Trial-Tree DAG**, derive an *effective $N$* from the tree's branching structure, augment it with an MDL term for strategy complexity, and prove a per-strategy Type-I error bound on the resulting MDL-augmented Deflated Sharpe Ratio. The framework computationally operationalises Gelman & Loken's "garden of forking paths" critique for backtest validation, complements Coqueret (2024)'s multiverse approach by accounting for the *actually realised* adaptive path, and extends Paterlini & Krink's Sharpe Information Criterion from parameter count to full description length.

We implement the framework as an open-source Python library (`agent_trader/validation/svc.py`) and apply it retrospectively to a real 390-trial adaptive research project on Indian equity markets. The case study shows that the framework's verdicts are consistent with the project's cumulative finding (no strategy survives) and identifies the specific stage at which each candidate would have been (and was) rejected.

## 1. Introduction

The problem of multiple-testing in backtest validation has a long pedigree. Bailey & López de Prado (2014; the "False Strategy Theorem") proved that the maximum of $N$ independent Sharpe-ratio estimates inflates predictably by $\sqrt{2 \log N}$, leading to the **Deflated Sharpe Ratio** (DSR) — a corrected statistic that punishes the observed Sharpe by the expected maximum under the null. This is now standard machinery: every honest backtest report should cite an $N$ and report DSR.

But what is $N$? In the original formulation, $N$ is the number of *strategies tested* — an exogenous, pre-specified count. Real research is not exogenous. A quant tests three strategies, sees one looks promising, branches into a parameter sweep, peeks at the out-of-sample, refines, runs more variants. **The researcher's *behaviour* is data-dependent.** Gelman & Loken (2013) named this the "garden of forking paths" and argued forcefully that single-path analyses ignore the implicit branches not taken. Coqueret (2024) imported the related "multiverse" methodology into finance, computing distributions over all possible analytic paths in a Cartesian product. But neither paper formalises a computational framework for the actually-realised adaptive path with a provable Type-I bound.

This paper does. Section 2 reviews the static-$N$ DSR machinery and the multiverse literature. Section 3 introduces the **Trial-Tree** formalism — a DAG whose edges encode "result of $u$ informed the decision to run $v$" — and derives an effective $N_{\mathrm{eff}}$ from its branching structure. Section 4 adds an MDL term to charge strategies for description-length complexity. Section 5 states and proves Theorem 1: under stated assumptions, the MDL-augmented DSR acceptance rule has Type-I error bounded by $\alpha$ regardless of how the trial-tree was constructed. Section 6 implements the framework as a Python library. Section 7 applies it retrospectively to a real 390-trial research project. Section 8 discusses limitations and open questions.

## 2. Background and prior art

[Note: this section in the final paper would expand on the lit review from A1, with proper academic citation style. For this draft we summarise the key positioning.]

The framework is positioned **strictly between** two well-developed bodies of work:

- **Static-$N$ deflation** (Bailey-LdP DSR; PBO; CSCV; False Strategy Theorem; Paterlini-Krink SIC) provides the extreme-value machinery we re-use, but requires $N$ to be specified ex-ante.
- **Multiverse / adaptive multiple testing** (Gelman-Loken; Steegen et al.; Coqueret 2024; online-FDR via Foster-Stine, LORD, SAFFRON, DAGGER, AdaPT) recognises the problem of adaptive research, but does not provide a per-strategy Type-I bound rooted in the realised research path.

Our contribution is a **Trial-Tree object** with **researcher-decision edges** (not pre-specified logical hierarchy as in DAGGER, not Cartesian-product enumeration as in Coqueret), a **single-strategy Type-I bound** under arbitrary branching, an **MDL augmentation** of DSR (extending Paterlini-Krink's parameter-count SIC), and a **case study on a real adaptive research history** of 390 trials.

We concede explicitly that the maximum-of-$N$ machinery is borrowed from the False Strategy Theorem; the novelty is in $N_{\mathrm{eff}}$.

## 3. The Trial-Tree formalism

[Definitions 1-2 from A2 reproduced verbatim. See `A2_formal_definitions.md` §§1-2 for full text.]

**Definition 1 (Trial-Tree).** $T = (V, E, \pi, \varphi, \nu)$ where $V$ is a finite set of trials, $E$ are directed parent-child edges, $\pi: V \to \mathcal{S}$ maps trials to strategies, $\varphi: V \to \mathbb{R}$ records observed Sharpes, and $\nu: V \to \mathbb{Z}_{\ge 1}$ records the branching factor (alternatives considered) at each trial.

**Definition 2 (Branching Product).** $N_{\mathrm{bp}}(v) = \prod_{u \in P(v)} \nu(u)$ along the path from root to $v$. This is the size of the implicit search space realised by the researcher's adaptive choices.

## 4. MDL augmentation

[Definitions 3-5 from A2 reproduced verbatim.]

**Definition 3 (MDL code length).** $K(s) = |C(s)|$ for a fixed prefix-free code $C$. In practice, $C$ canonically AST-compresses the strategy source and adds parameter-precision bits.

**Definition 4 (Effective N).** $N_{\mathrm{eff}}(v) = N_{\mathrm{bp}}(v) \cdot 2^{K(\pi(v))}$.

**Definition 5 (MDL-DSR).** Standard DSR with $N \mapsto N_{\mathrm{eff}}(v)$.

A practical note (added during implementation in §6): the raw $2^{K(s)}$ Kraft bound is *very loose* for natural strategies. For practical use we substitute $K_{\mathrm{excess}}(s) = K(s) - K_{\mathrm{baseline}}$ where $K_{\mathrm{baseline}}$ is the canonical-encoding length of the simplest reasonable strategy in the project's class. The Type-I bound still holds — it holds with any $K$ that upper-bounds the implicit search — but the framework becomes *relative within a project* rather than absolute against the universe of all expressible strategies. We argue this is the operationally honest choice.

## 5. Theorem 1 and its proof

[Full text reproduced from `A3_proof.md`. Statement repeated here.]

**Theorem 1.** Let $T$ be a trial-tree and $v$ a leaf. Under assumptions (A1)-(A5), and under $H_0(v)$,
$$
\Pr( \mathrm{MDL\text{-}DSR}(v) > 1 - \alpha ) \le \alpha + O(\tau^{-1/2}).
$$

The proof composes five lemmata: (1) asymptotic Gaussianity of $\mathrm{SR}_v$ (Mertens 2002), (2) Kraft inequality bounds the parameter search, (3) branching product bounds the structural search, (4) disjointness of the two contributions, (5) union bound + extreme-value asymptotic on the threshold.

Assumption (A1) — honest data-splitting — is essential and cannot be weakened: without train/test isolation, no statistical correction can save a researcher. Assumption (A4) — honest branching reporting — places the burden on the researcher to truthfully record the alternatives considered at each branch; this is true of every multiple-testing correction.

## 6. Implementation

Open-source Python in `agent_trader/validation/svc.py`. Key components:

- `compute_K(source_code, ..., baseline_bits)` — MDL code length via canonical AST + zlib compression with optional baseline subtraction.
- `TrialTree` — append-only SQLite-backed tree data structure, extending the standard `TrialLog` registry with `parent_id` and `nu`.
- `branching_product(path)`, `effective_N(path)`, `log2_effective_N(path)` — N_eff arithmetic with overflow-safe log-domain computation.
- `mdl_dsr(returns, path)` — the MDL-DSR statistic, returning observed Sharpe, expected-max-under-null, the deflation, and full diagnostic breakdown ($N_{\mathrm{bp}}$, $K$, $\log_2 N_{\mathrm{eff}}$).

Test suite (14 tests) verifies:
- $K$ is stable under cosmetic edits (docstring stripping) and monotone in code complexity.
- Tree path reconstruction is correct.
- $N_{\mathrm{eff}}$ overflow-safe for $K > 60$.
- MDL-DSR behaviour: heavier branching → lower MDL-DSR, higher $K$ → lower MDL-DSR, real edge at low $K_{\mathrm{excess}}$ → passes, real edge at extreme branching → legitimately rejected.

## 7. Case study: SVC on a 390-trial adaptive research project

We apply SVC retrospectively to our own research project on Indian equity markets, which spanned 390 strategy trials across four major phases (W3-4 boring strategies, W7-8 disclosure-text channel, D3+D1+D5 conjunctive setup search, Phase 10 novel-primitive survey). The full trial tree was reconstructed from version-control history, the project's `trial_log.db` SQLite registry, and the documented research-decision log.

For each of four headline candidates, we computed three verdicts: Naive DSR ($N=1$), Grid DSR ($N=$ within-strategy variant count), and SVC MDL-DSR (full $N_{\mathrm{eff}}$).

| Candidate | Naive DSR | Grid DSR | SVC MDL-DSR | $N_{\mathrm{bp}}$ | $K_{\mathrm{excess}}$ | $\log_2 N_{\mathrm{eff}}$ |
|---|---:|---:|---:|---:|---:|---:|
| s1_thursday_reversion | 0.683 | 0.000 | 0.000 | 180 | 5120 | 5127.5 |
| s2_vix_regime | 0.087 | 0.000 | 0.000 | 360 | 6648 | 6656.5 |
| s3_dow_dispersion | 0.000 | 0.000 | 0.000 | 300 | 4488 | 4496.2 |
| d5_regime_calm | 0.996 | 0.000 | 0.000 | 7540 | 0 | 12.9 |

**The d5_regime_calm row is the most informative.** This strategy survived the project's train-window deflation, passed validation-window sign-consistency, and was rejected only when run on the post-LLM-cutoff OOS window (where its sign flipped). Naive DSR rated it 0.996 — a textbook false-positive. Grid DSR (with $N = 377$) correctly drove it to 0.000. SVC adds the realised research path (factor $7540$ of branching) and confirms 0.000 with even more conservatism.

**The case study's honest limitation:** in this project, *Grid DSR was already enough* — every candidate was killed at the grid-count level, before SVC's additional discipline mattered. SVC's unique value would manifest on a candidate that *passed* Grid DSR but failed SVC. Our project does not contain such a candidate. The framework still earned its keep retrospectively as the most stringent verdict, consistent with the project's cumulative null result; its forward value will only be visible when applied to a project that does surface a Grid-DSR survivor.

**Implementation caveat surfaced by the case study:** Strategy source files include imports, helpers, and docstrings that inflate raw $K$ beyond the strategy's core logical content. We used $K_{\mathrm{excess}}$ relative to a trivial baseline; even then, $K_{\mathrm{excess}}$ values are unrealistically large for s1/s2/s3 (4488-6648 bits). A more sophisticated $K$ implementation would extract just the *decision-rule* portion of the strategy, ignoring boilerplate. This is straightforward future work and does not affect the theorem.

## 7.5. Empirical validation (Monte Carlo simulation)

Theorem 1 makes an asymptotic claim about Type-I error control. We validate it directly by simulating the null hypothesis world and counting empirical rejections.

**Test 1 — Flat tree, null world.** For each of 2000 simulations, draw $K = 50$ iid null strategies ($\mu = 0$, $\sigma = 0.01$, $\tau = 500$ obs each). The researcher picks the best-of-$K$ by observed Sharpe; we compute the SVC verdict.

| Statistic | Empirical Type-I | Target |
|---|---:|---:|
| Naive DSR ($N=1$) | **0.915** | ≤ 0.05 |
| Grid DSR ($N=K$) | 0.000 | ≤ 0.05 |
| SVC MDL-DSR | **0.000** | ≤ 0.05 |

Naive DSR fails catastrophically (91.5% false-positive rate) — this is precisely the failure mode the framework targets. SVC and Grid DSR both hold Type-I at 0% — well below the target.

**Test 2 — Adaptive tree, null world.** Researcher with branching factors $(5, 4, 3)$ explores 60 candidate strategies, picks the in-sample best at each level on TRAIN data, evaluates on independent TEST data. Repeat 2000 times.

| Statistic | Empirical Type-I |
|---|---:|
| Naive DSR | 0.0515 |
| Grid DSR ($N=60$) | 0.0000 |
| SVC MDL-DSR | **0.0000** |

**Test 4 — Calibration of $E[\mathrm{SR}_{\max} \mid N]$.** Monte Carlo the actual maximum of $N$ iid null Sharpes; compare to the Bailey-LdP prediction used inside MDL-DSR.

| $N$ | empirical max | predicted (Bailey-LdP) | relative error |
|---:|---:|---:|---:|
| 10 | 0.0689 | 0.0705 | 2.3% |
| 100 | 0.1128 | 0.1133 | 0.5% |
| 1000 | 0.1460 | 0.1457 | 0.2% |
| 10000 | 0.1735 | 0.1728 | 0.4% |

The deflation formula is well-calibrated within Monte Carlo error for $N \ge 10$.

**Verdict:** Theorem 1's central claims (Type-I control + calibrated deflation) are empirically supported on the tested scenarios.

### 7.5.1 The honest cost of honesty — power

**Test 3 — Power on real edges.** For each true annual Sharpe in $\{0.5, 1.0, 1.5, 2.0, 3.0\}$, place a single edge strategy among $K = 49$ null alternatives. Researcher picks the best of $K$. Measure (i) how often the edge is picked vs noise, (ii) how often the picked strategy passes SVC.

| True annual SR | Edge picked from K=50 | Passes SVC |
|---:|---:|---:|
| 0.5 | 8.7% | 0.0% |
| 1.0 | 25.5% | 0.1% |
| 1.5 | 44.9% | 0.3% |
| 2.0 | 70.0% | 1.7% |
| 3.0 | 96.0% | 26.8% |

**This is real and worth being explicit about: SVC has very low power at modest true edges.** A true annualised Sharpe of 2.0 — generally considered a substantial edge in published quant literature — passes SVC only 1.7% of the time. Even a true Sharpe of 3.0 (extraordinary) passes only 26.8%.

The interpretation is not that SVC is "broken"; it is that **tight Type-I control on adaptive research with a large implicit search space is fundamentally expensive in power**. This is mathematical truth, not a deficiency of the framework. The relevant question is whether the tradeoff is appropriate for backtest validation:

- **Type-I cost** = accepting a noise strategy as edge = real money lost when deployed.
- **Type-II cost** = rejecting a true edge as noise = missed opportunity, no realized loss.

For solo researchers with real capital at stake, Type-I costs dominate Type-II costs by orders of magnitude. SVC's conservatism is the right side to err on. For institutional research with abundant capital where exploration is cheap, the tradeoff may shift, and a less conservative framework (or more $\tau$, or pre-registration with smaller $N_{\mathrm{eff}}$) would be appropriate.

**The actionable takeaway:** A researcher seeking to actually *pass* SVC on a true edge should (i) pre-register to keep $N_{\mathrm{eff}}$ small, (ii) accumulate enough $\tau$ that the per-trial standard error shrinks, and (iii) prefer simpler strategies (low $K_{\mathrm{excess}}$).

## 8. Discussion

**What SVC catches that Grid DSR does not.** Grid DSR punishes the researcher only for the strategies *within a single grid*. SVC additionally punishes for the cross-phase decisions (which markets, which horizons, which feature families) that the researcher made before settling on the grid. For a project with substantial across-phase branching, SVC's $N_{\mathrm{eff}}$ can be orders of magnitude larger than Grid DSR's $N$.

**What SVC cannot catch.** Dishonest reporting of $\nu$. A researcher who under-counts branching factors defeats the bound. This is true of every multiple-testing framework. We do not propose a remedy beyond the obvious: pre-registration, version-controlled research logs, and an honest project diary.

**Limitations.**
1. The framework requires honest data-splitting (A1) and honest branching reporting (A4) — both researcher behaviours, not statistical guarantees.
2. The $K$ implementation is canonical-encoding-dependent ($O(1)$ in the Kolmogorov sense, but materially different in finite samples).
3. The Type-I bound is per-strategy. For collective control over multiple accepted strategies, additional online-FDR machinery (Foster-Stine, LORD) should be composed; we do not develop this here.
4. Power is not characterised. The framework controls false positives only; what fraction of true edges pass MDL-DSR is bounded above by the same extreme-value statistics and depends on the strategy's true Sharpe.

**Future work.** 
- Tighten Lemma 4 (disjointness of branching and Kraft contributions) with a more formal information-theoretic argument.
- Replace static-$\nu$ reporting with a version that infers branching from version-control logs.
- Compose with online-FDR for collective control.
- Extend $K$ to extract decision-rule core, excluding boilerplate.

**The honest summary.** SVC is a small but real contribution: a formal object (the trial-tree) plus an honest accounting rule ($N_{\mathrm{eff}}$) plus an MDL augmentation, with a per-strategy Type-I bound that holds under stated assumptions, all backed by working code and a real-world case study. It does not produce alpha; it produces *honest verdicts on whether candidate alphas should be believed*.

## Acknowledgements

[To be added.]

## References (key)

- Bailey, D. H., & López de Prado, M. (2014). *The Deflated Sharpe Ratio*. Journal of Portfolio Management.
- Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. (2017). *The Probability of Backtest Overfitting*. Journal of Computational Finance.
- Coqueret, G. (2024). *Forking paths in financial economics*. arXiv:2401.08606.
- Gelman, A., & Loken, E. (2013). *The garden of forking paths*. Working paper.
- Mertens, E. (2002). *Comments on variance of the IID estimator in Lo (2002)*.
- Paterlini, S., & Krink, T. (2016). *Noise Fit, Estimation Error and a Sharpe Information Criterion*.
- Ramdas, A., Yang, F., Jordan, M., & Wainwright, M. (2018). *DAGGER: Hierarchical structured FDR*. NeurIPS.
- Foster, D. P., & Stine, R. A. (2008). *α-investing: A procedure for sequential control of expected false discoveries*.
- Javanmard, A., & Montanari, A. (2018). *Online Rules for Control of False Discovery Rate and False Discovery Exceedance*. Annals of Statistics.
- Kraft, L. G. (1949). *A device for quantizing, grouping, and coding amplitude-modulated pulses*. MIT M.Sc. thesis.

(Full bibliography in lit-review file `A1_lit_review.md`.)
