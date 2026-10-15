# SVC A2 — Formal Definitions (Working Draft)

**Status:** Draft v0.1, 2026-05-21. Subject to revision once A1 lit review completes.

## Setting

Fix a historical price/return dataset D of length T. Let 𝒮 denote a (possibly large) space of trading strategies, each strategy s ∈ 𝒮 deterministically inducing a return stream R(s) ∈ ℝ^T when applied to D. The Sharpe ratio is

```
SR(s) = mean(R(s)) / sd(R(s)) · √m
```

where m is the per-period annualisation factor (m=252 for daily bars).

We test the per-strategy null hypothesis H₀(s): the true Sharpe ratio of s is ≤ 0, against H₁(s): true Sharpe > 0.

## Definition 1 — Trial-Tree

A **trial-tree** is a tuple T = (V, E, π, φ, ν) where:

- **V** — finite set of *trials* (research experiments actually run)
- **E ⊆ V × V** — directed edges (u, v) meaning "the decision to run v was informed by the outcome of u"
- **π: V → 𝒮** — maps each trial to the strategy that was tested
- **φ: V → ℝ** — records the observed Sharpe ratio SR(π(v))
- **ν: V → ℕ_{≥1}** — the **branching factor** at v: the *honest* count of alternatives the researcher was choosing among when v was selected as the child to explore

Constraint: T is a rooted tree (each non-root node has exactly one parent).

**Interpretation of ν.** When the researcher reaches a decision point — "I observed v's result; among {sibling alternatives I would have considered if v had been disappointing}, I picked v to continue" — ν(v) records the size of that *alternative set*, including v itself. This is the implicit search width at v.

## Definition 2 — Path and Branching Product

The **path** P(v) is the unique sequence (root = v₀, v₁, ..., v_d = v) connecting the root to v.

The **branching product** of v is

```
N_bp(v) = ∏_{u ∈ P(v)} ν(u).
```

**Interpretation.** N_bp(v) is the size of the implicit search space *traversed by the researcher's decision-making process* to land on strategy π(v). If the researcher's choices at each branch were responsive to data, the effective number of strategies considered is N_bp(v), even though only d = depth(v) trials were actually run.

This is the central claim of SVC: **for adaptive researchers, N_bp dominates the actual trial count as the honest multiple-testing denominator.**

## Definition 3 — MDL Code Length of a Strategy

Fix a prefix-free code C: 𝒮 → {0,1}* that encodes strategies. The **MDL code length** of strategy s is

```
K(s) = |C(s)|  (bits).
```

In practice, K(s) is computed as:
- length(gzip(ast(s))) where ast(s) is the abstract syntax tree of the strategy code, *plus*
- ⌈log₂(1/ε)⌉ bits per continuous parameter, where ε is the precision (e.g., 10⁻³ → 10 bits per parameter).

By Kraft's inequality, no more than 2^{K(s)} distinct strategies can be assigned codewords of length ≤ K(s) in any prefix-free code. Thus a strategy of code length K(s) is implicitly selected from a pool of at most 2^{K(s)} strategies.

## Definition 4 — Effective N (Combined)

For a trial v in tree T,

```
N_eff(v) = N_bp(v) · 2^{K(π(v))}.
```

The first factor captures the search performed by the *researcher* (branching). The second factor captures the search implicit in the *strategy structure itself* (parameter space). They are multiplicative because they correspond to disjoint sources of selection.

## Definition 5 — MDL-Augmented Deflated Sharpe Ratio (MDL-DSR)

Following Bailey & López de Prado (2014), for a strategy with observed Sharpe SR_v, return-stream skew γ₃ and excess kurtosis γ₄−3, sample length T, and observed Sharpe variance across trials σ²_SR, define

```
E[SR_max | N] = √(σ²_SR) · ((1−γ)Φ⁻¹(1 − 1/N) + γΦ⁻¹(1 − 1/(N·e)))
```

(γ = Euler-Mascheroni constant) and

```
σ̂_SR = √( (1 − γ₃·SR_v + (γ₄−1)/4 · SR_v²) / (T − 1) ).
```

The **MDL-DSR** of trial v is

```
MDL-DSR(v) = Φ( (SR_v − E[SR_max | N_eff(v)]) / σ̂_SR ).
```

Equivalent to standard DSR but with N = N_eff(v) substituted for the naive trial count.

## Theorem 1 (Target — to prove in A3)

Let T be a trial-tree and let v ∈ V be a specific leaf. Suppose:

(A1) For every u ∈ P(v), the decision to explore v's branch rather than a sibling was made on the basis of a strict training/validation split: the data used to compute the Sharpe driving the decision is disjoint from the data used to compute SR_v.

(A2) The K(π(v)) bound is achieved by an actual prefix-free encoding (so Kraft's inequality applies).

(A3) Under H₀(v), the strategy's per-period returns satisfy mild regularity (finite fourth moment, weak dependence).

**Claim.** Under H₀(v),

```
P( MDL-DSR(v) > 1 − α ) ≤ α + o(1)
```

as T → ∞, where o(1) → 0 with T.

**Sketch of proof technique.** By union bound over the implicit search space of size N_eff(v), each candidate has tail probability bounded by the standard normal approximation. The Bailey-LdP correction precisely computes the expected maximum under N alternatives via extreme value theory. The MDL factor 2^{K(π(v))} extends the union bound to cover the parameter-space search not accounted for by branching alone.

## Open questions for A3

1. **Tightness of N_bp:** Is the branching product the right honest count, or is there a tighter bound using conditional information?
2. **Correlation between trials:** Standard DSR assumes independence of trial Sharpes. Real backtest variants are correlated. The Bailey-LdP formula partially handles this via the σ²_SR term, but our tree-aware version needs careful re-derivation.
3. **Data-reuse:** A1 forbids data reuse across decisions, but real research reuses data. A weakened version of Theorem 1 under partial data reuse?
4. **Multiplicativity of N_bp and 2^K:** Is the product the right combination, or is one of them already counting the other?

## Open questions for A2 to resolve before A3

1. Is N_bp definition correct, or should we use a tighter information-theoretic measure (e.g., conditional entropy of branch choice given training data)?
2. Should K(s) include parameter precision or only structure? Both? Per-parameter precision is implementation-dependent.
3. Is there a cleaner formulation that doesn't require the strong A1 data-splitting assumption?

## Working examples (to develop further in A5)

**Example 1 — Pre-registered single test.** Tree: root → v. ν(root) = 1, ν(v) = 1. K(π(v)) = 10 bits (simple strategy). N_eff = 1 · 2^10 = 1024. Standard DSR with N=1 would be too lenient; MDL-DSR with N=1024 is properly skeptical of overfit-by-parameter-tuning.

**Example 2 — Three boring strategies (our W3-4).** Tree: root → {S1, S2, S3}. ν(root) = 3 (we explicitly chose 3). ν(S_i) = some grid count (S1 had 12 variants). K(S1) ≈ 200 bits. N_eff(S1) = 3 · 12 · 2^200 ≈ astronomical. **Even with the absurd MDL inflation, our S1 had Sharpe of 0.017, so this is moot — it failed by miles regardless.**

**Example 3 — D5 setup search.** Tree: root → 377 conjunctive setups. ν(root) = 377 by construction. K of a simple boolean conjunction ≈ 30 bits. N_eff ≈ 377 · 2^30 ≈ 4×10^11. MDL-DSR would require a Sharpe far beyond what `regime_calm` showed (DSR with N=377 already rejected it; MDL with N=4e11 even more so).

The retrospective interesting case: **what if we ever build a strategy that *passes* standard DSR? Does it also pass MDL-DSR?** That's the operationally important question for A5.
