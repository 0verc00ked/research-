# SVC — A2: Formal Definitions and Theorem Statement

**Status:** v1.0 (post lit-review, 2026-05-21). Supersedes `A2_formal_definitions_DRAFT.md`.

## 0. Notation and prior art

We retain the Bailey & López de Prado (2014) extreme-value machinery for the maximum of $N$ Sharpe ratio estimates and the Paterlini-Krink (2016) intuition that strategy complexity should debit reported performance. The novel object is the **trial-tree** $T$ and the construction of an *effective* $N$, denoted $N_{\text{eff}}$, from $T$ that honestly reflects an adaptive researcher's implicit search space.

Throughout: $D$ is a fixed dataset of length $\tau$ periods (we use $\tau$ instead of $T$ for sample length to avoid clash with the tree symbol). $\mathcal{S}$ is the strategy space. Each strategy $s \in \mathcal{S}$ produces a return stream $R(s) \in \mathbb{R}^\tau$ when applied to $D$. Annualised Sharpe is $\mathrm{SR}(s) = \bar{R}(s) / \hat{\sigma}(R(s)) \cdot \sqrt{m}$ where $m$ is periods per year.

## 1. Trial-Tree (Definition 1)

A **trial-tree** is a tuple $T = (V, E, \pi, \varphi, \nu)$ where:

- $V$: finite set of *trial nodes* (experiments actually executed).
- $E \subseteq V \times V$: directed edges where $(u, v) \in E$ means "the choice to execute trial $v$ was informed by the outcome of trial $u$." Constraint: $T$ is a rooted tree (each non-root node has exactly one parent).
- $\pi: V \to \mathcal{S}$: maps each trial to the strategy that was tested.
- $\varphi: V \to \mathbb{R}$: records observed Sharpe $\mathrm{SR}(\pi(v))$ on the *evaluation portion* of $D$ used for this trial.
- $\nu: V \to \mathbb{Z}_{\ge 1}$: the **branching factor** at $v$ — the honest count of alternative trials that the researcher was choosing between when $v$ was selected, *including $v$ itself*.

**Edge semantics.** $(u, v) \in E$ does **not** mean "$u$ logically implies $v$" (as in DAGGER) nor "$v$ is one path of a pre-specified multiverse" (as in Coqueret 2024). It means: had $u$'s observed Sharpe been different, the researcher might have chosen a different child to explore — i.e., the *realisation* of $u$'s evaluation is the parent of the *decision* to construct $v$.

**Branching-factor semantics.** $\nu(v)$ requires honest researcher reporting. If at the decision point preceding $v$ the researcher had a discrete set $\{v, v_2, \ldots, v_{\nu(v)}\}$ in mind and chose $v$ based on parent's outcome, $\nu(v)$ is the size of that set. If the researcher genuinely had no alternatives in mind (a forced single path), $\nu(v) = 1$.

This is the framework's main practical demand and main vulnerability: a dishonest researcher who under-reports $\nu$ defeats the bound, just as they defeat any multiple-testing correction.

## 2. Path and Branching Product (Definition 2)

For $v \in V$, the **path** $P(v) = (v_0, v_1, \ldots, v_d)$ is the unique sequence from root $v_0$ to $v_d = v$, with $d = \mathrm{depth}(v)$.

The **branching product** is

$$
N_{\text{bp}}(v) \;=\; \prod_{u \in P(v)} \nu(u).
$$

This is the size of the implicit search space *realised by the researcher's decision path*: at each step, $\nu(u)$ alternatives were considered, multiplicatively yielding $N_{\text{bp}}(v)$ candidate end-states.

**Connection to multiverse.** Coqueret (2024) defines a multiverse $P = \prod_j r_j$ as the *Cartesian product* of all analytic decisions, with $r_j$ the number of options for decision $j$. SVC's $N_{\text{bp}}(v)$ collapses Coqueret's Cartesian product onto a single observed path. The two coincide only when the researcher's decisions are *symmetric and pre-specified*, which is the multiverse assumption Coqueret makes explicitly and SVC relaxes.

## 3. MDL Code Length (Definition 3)

Fix a prefix-free code $C: \mathcal{S} \to \{0,1\}^*$. The **MDL code length** of $s$ is

$$
K(s) \;:=\; |C(s)| \quad \text{(bits)}.
$$

In practice we use a *canonical encoding*: $C(s)$ is the concatenation of (a) a serialisation of the strategy's abstract syntax tree (passed through a fixed compressor, e.g. zlib at level 9, applied to a normalised AST), and (b) the precision-adjusted encoding of each continuous parameter (typically $\lceil \log_2(1/\varepsilon) \rceil$ bits per parameter for precision $\varepsilon$).

This is "$K$ up to a constant" in the Kolmogorov sense: a different canonical encoding $C'$ would give $K_{C'}(s) = K_C(s) + O(1)$ for the encoding overhead, which is bounded over $\mathcal{S}$.

**Kraft's inequality** ensures that at most $2^{K(s)}$ strategies can be assigned prefix-free codewords of length $\le K(s)$. Thus a strategy $s$ of code length $K(s)$ is implicitly selected from a pool of at most $2^{K(s)}$ strategies of equal-or-lesser complexity.

**Caveat (overlap with branching).** If a parameter of $s$ was selected via branching (e.g., "tested $\nu = 4$ thresholds, picked $\theta^*$"), the branching contributes a factor of 4 to $N_{\text{bp}}$ and the chosen $\theta^*$ contributes its precision-bits to $K(s)$. To avoid double-counting, **$K(s)$ should be computed against the realised strategy with its branched parameters already fixed**. In that case the precision-bits of $\theta^*$ encode a *single* value, not the set of values considered; the search across $\nu$ alternatives is in $N_{\text{bp}}$, not in $K(s)$. The two terms are therefore disjoint contributions.

## 4. Effective N (Definition 4)

$$
N_{\text{eff}}(v) \;=\; N_{\text{bp}}(v) \cdot 2^{K(\pi(v))}.
$$

This combines (a) the researcher's adaptive search across the trial-tree (the $N_{\text{bp}}$ factor) with (b) the strategy's own internal parameter-space search (the $2^{K(\pi(v))}$ factor) into a single honest count of the implicit hypothesis space from which $\pi(v)$ was selected.

## 5. MDL-augmented Deflated Sharpe Ratio (Definition 5)

Adopt the Bailey & López de Prado (2014) deflation: for observed Sharpe $\mathrm{SR}_v$, return-stream skewness $\hat{\gamma}_3$, excess kurtosis $\hat{\gamma}_4 - 3$, sample length $\tau$, and observed cross-trial Sharpe variance $\hat{\sigma}^2_{\mathrm{SR}}$,

$$
E[\mathrm{SR}_{\max} \mid N] \;=\; \sqrt{\hat{\sigma}^2_{\mathrm{SR}}} \cdot \left((1 - \gamma_{\mathrm{em}}) \Phi^{-1}\!\left(1 - \tfrac{1}{N}\right) + \gamma_{\mathrm{em}} \Phi^{-1}\!\left(1 - \tfrac{1}{N \cdot e}\right)\right),
$$

(where $\gamma_{\mathrm{em}} \approx 0.5772$ is Euler-Mascheroni) and

$$
\hat{\sigma}_{\mathrm{SR}_v} \;=\; \sqrt{\frac{1 - \hat{\gamma}_3 \mathrm{SR}_v + \frac{\hat{\gamma}_4 - 1}{4} \mathrm{SR}_v^2}{\tau - 1}}.
$$

The **MDL-DSR** at trial $v$ is

$$
\mathrm{MDL\text{-}DSR}(v) \;=\; \Phi\!\left(\frac{\mathrm{SR}_v - E[\mathrm{SR}_{\max} \mid N_{\text{eff}}(v)]}{\hat{\sigma}_{\mathrm{SR}_v}}\right).
$$

This is identical to standard DSR with the substitution $N \mapsto N_{\text{eff}}(v)$. The novelty is in the construction of $N_{\text{eff}}(v)$ from $T$, not in the deflation formula itself.

## 6. Theorem 1 — Type-I Bound (Statement)

**Assumptions:**

(A1) *Honest data-splitting.* For every $u \in P(v)$, the data used to compute $\varphi(u)$ (the Sharpe driving the branching decision at $u$) is disjoint from the data used to compute $\mathrm{SR}_v$.

(A2) *Prefix encoding.* $C$ is a fixed prefix-free code on $\mathcal{S}$ and $K(\pi(v)) = |C(\pi(v))|$.

(A3) *Regularity.* The per-period returns of $\pi(v)$ on the evaluation data are stationary with finite fourth moment and weak (mixing) temporal dependence sufficient for a Berry-Esseen-type CLT to apply with rate $O(\tau^{-1/2})$.

(A4) *Honest branching count.* $\nu(u)$ at every $u \in V$ is reported correctly: it equals the actual number of distinct strategies the researcher was choosing between at that decision point.

(A5) *Calibrated cross-trial variance.* $\hat{\sigma}^2_{\mathrm{SR}}$ is computed as the empirical variance of $\mathrm{SR}_w$ across $w \in V$ and is consistent for the population variance of the (correlated) Sharpe estimates over the implicit search space.

**Claim.** Under (A1)-(A5), for any $\alpha \in (0, 1)$ and any leaf $v \in V$, under the null hypothesis $H_0(v): \mathbb{E}[R(\pi(v))] \le 0$:

$$
\Pr\bigl( \mathrm{MDL\text{-}DSR}(v) > 1 - \alpha \,\bigm|\, H_0(v) \bigr) \;\le\; \alpha + O(\tau^{-1/2}).
$$

**Interpretation.** The acceptance rule "accept $v$ iff $\mathrm{MDL\text{-}DSR}(v) > 1 - \alpha$" has Type-I error bounded by $\alpha$ up to a finite-sample correction that vanishes as $\tau \to \infty$, **regardless of how the trial-tree $T$ was constructed**.

## 7. What the theorem does and does not say

**The theorem says:** Given honest reporting of $\nu$ and honest data-splitting, the MDL-DSR acceptance rule controls Type-I error per single strategy at level $\alpha$, asymptotically in sample length $\tau$.

**The theorem does not say:**
- *Type-I across multiple accepted strategies.* The bound is per-trial. For collective control over a set of accepted strategies, additional adjustments (e.g., FDR control via online machinery from Foster-Stine / LORD / SAFFRON) would be needed. This is an extension we flag but do not develop here.
- *Power.* Nothing in the theorem guarantees that good strategies clear the bar. The bound is one-sided (controls false positives only). Power depends on the strategy's true Sharpe and is bounded above by the same extreme-value statistics.
- *Robustness to dishonest reporting.* (A4) is essential. A researcher who under-counts $\nu$ defeats the bound (this is true of every multiple-testing correction; we make no special claim here).
- *Independence of trials.* (A5) handles correlation via the empirical cross-trial Sharpe variance, but does so approximately. Highly correlated trial families may need a more conservative variance estimate.

## 7.5. Calibration note on $K$ (discovered during A4 implementation)

The raw Kraft bound $2^{K(s)}$ from Lemma 2 is provably correct but extremely loose in practice. For a typical AST-compressed strategy of even moderate complexity (e.g., 50-byte canonical AST → 400 bits), $2^{400}$ candidates dwarfs any plausible implicit search and the deflation threshold becomes unreachable. The Type-I bound in Theorem 1 holds, but the framework rejects everything.

For practical use, we measure $K(s)$ as **excess complexity over a project-class baseline**:
$$
K_{\text{excess}}(s) \;=\; \max(0, K_{\text{raw}}(s) - K_{\text{baseline}})
$$
where $K_{\text{baseline}}$ is the canonical-encoding length of the simplest reasonable strategy in the researcher's project class (e.g., a buy-and-hold or a single-indicator threshold rule).

This is a calibration choice, not a weakening of the theorem: the proof goes through with any $K$ that upper-bounds the implicit search, and $K_{\text{excess}}$ does so *over the project's strategy class*. The cost is that the framework is now *relative* (within a project, more complex strategies are penalised more) rather than *absolute* (a strategy is penalised against the universe of all expressible strategies). For methodological honesty in a project, relative is more useful.

The `compute_K()` function in `agent_trader/validation/svc.py` accepts a `baseline_bits` parameter to support this calibration.

## 8. Positioning vs prior art (one-paragraph summary)

> **We extend Bailey & López de Prado's Deflated Sharpe Ratio from the static-$N$ regime to the adaptive-research regime by formalising research history as a Trial-Tree DAG and introducing an MDL-augmented acceptance rule with a provable Type-I bound. Our framework computationally operationalises Gelman & Loken's garden-of-forking-paths critique, complementing Coqueret (2024)'s multiverse-enumeration approach with an honest accounting of the *actually-realised* adaptive path. The MDL term extends Paterlini & Krink's Sharpe Information Criterion from parameter-count to full-description-length complexity. We borrow the maximum-of-$N$ extreme-value machinery from the False Strategy Theorem and the proof technique for adaptive DAGs from the DAGGER (Ramdas et al. 2018) family, both of which we re-purpose for backtest validation.**

## 9. Roadmap to A3 (proof)

The proof of Theorem 1 will be structured as:

1. **Lemma 1.** Under (A1)-(A3), $\mathrm{SR}_v$ is asymptotically Gaussian with variance $\hat{\sigma}_{\mathrm{SR}_v}^2$ (Bailey-LdP standard).

2. **Lemma 2 (Kraft-implicit search).** Under (A2), the strategy $\pi(v)$ belongs to a set of size at most $2^{K(\pi(v))}$ — the strategies of equal-or-lesser description length under $C$.

3. **Lemma 3 (Branching-implicit search).** Under (A4), the path $P(v)$ implicitly realises a search of size at most $N_{\text{bp}}(v)$ over the strategy space.

4. **Lemma 4 (Disjointness).** Under the Caveat in Definition 3, the Kraft-implicit and Branching-implicit search spaces are *disjoint sources of selection* — the multiplication $N_{\text{bp}} \cdot 2^K$ does not double-count.

5. **Lemma 5 (Union-bound extreme value).** Under (A1), (A5), and Lemmata 2–4, the probability that any of the $N_{\text{eff}}(v)$ candidates exceeds threshold $\tau_\alpha = E[\mathrm{SR}_{\max} \mid N_{\text{eff}}(v)] + \hat{\sigma}_{\mathrm{SR}_v} \Phi^{-1}(1 - \alpha)$ is at most $\alpha + O(\tau^{-1/2})$.

6. **Theorem 1.** Combine Lemmata 1–5.

The substantive mathematical work is in Lemma 4 (disjointness) and Lemma 5 (extreme value rate). The other lemmata are largely bookkeeping.
