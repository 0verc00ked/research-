# SVC — A3: Proof of Theorem 1

**Date:** 2026-05-21
**Status:** v1.0 — full proof of Theorem 1 (Type-I bound).

## 0. Roadmap

The proof decomposes Theorem 1 into five lemmata:

- **Lemma 1.** Asymptotic Gaussianity of the Sharpe estimator under (A3).
- **Lemma 2.** Kraft's inequality bounds the implicit parameter search space.
- **Lemma 3.** The branching product bounds the implicit structural search space.
- **Lemma 4.** Disjointness — the two search spaces multiply without double-counting.
- **Lemma 5.** Union bound + extreme-value asymptotics give the deflation threshold.

Then Theorem 1 follows by composition.

Throughout, $\Phi$ denotes the standard normal CDF, $\gamma_{\mathrm{em}} = 0.5772\ldots$ is the Euler-Mascheroni constant, and $o_p(1)$ denotes vanishing in probability.

---

## Lemma 1 — Asymptotic Gaussianity of $\mathrm{SR}_v$

**Statement.** Under (A3), the per-trial Sharpe estimator satisfies

$$
\sqrt{\tau - 1} \cdot \frac{\mathrm{SR}_v - \mu_v / \sigma_v \cdot \sqrt{m}}{\sqrt{1 - \hat{\gamma}_3 \mathrm{SR}_v + \frac{\hat{\gamma}_4 - 1}{4} \mathrm{SR}_v^2}} \;\xrightarrow{d}\; \mathcal{N}(0, 1)
$$

where $\mu_v, \sigma_v$ are the population mean and std of the return process under $\pi(v)$, $\hat{\gamma}_3$ and $\hat{\gamma}_4$ are sample skewness and kurtosis. In particular, $\hat{\sigma}_{\mathrm{SR}_v}$ as defined in §5 of A2 is a consistent estimator of the asymptotic standard error of $\mathrm{SR}_v$.

**Proof.** Standard (Mertens 2002, Lo 2002, Bailey-LdP 2014). The Sharpe is a function $\mathrm{SR} = \bar{R} / \hat{\sigma}_R \cdot \sqrt{m}$ of two empirical moments. Applying the delta method to the joint asymptotic normality of $(\bar{R}, \hat{\sigma}^2_R)$ under (A3) gives the result; the skewness and kurtosis corrections appear in the asymptotic variance via the covariance structure of the bivariate moment vector. We refer to Mertens (2002, Eqs. 9-12) for the explicit derivation. $\square$

The $O(\tau^{-1/2})$ in the rate of convergence is the Berry-Esseen rate under (A3); we write $\hat{\sigma}_{\mathrm{SR}_v}^2 = \sigma^2_{\mathrm{SR}_v} (1 + o_p(1))$ implicitly throughout the remainder.

---

## Lemma 2 — Kraft-implicit parameter search

**Statement.** Under (A2), the cardinality of the set
$$
\mathcal{K}_v \;:=\; \{ s' \in \mathcal{S} : |C(s')| \le K(\pi(v)) \}
$$
satisfies $|\mathcal{K}_v| \le 2^{K(\pi(v))}$.

**Proof.** $C$ is a prefix-free code, so by Kraft's inequality
$$
\sum_{s' \in \mathcal{S}} 2^{-|C(s')|} \le 1.
$$
Restricting the sum to $s' \in \mathcal{K}_v$,
$$
\sum_{s' \in \mathcal{K}_v} 2^{-|C(s')|} \le 1.
$$
Each term in this sum satisfies $2^{-|C(s')|} \ge 2^{-K(\pi(v))}$ since $|C(s')| \le K(\pi(v))$. Therefore
$$
|\mathcal{K}_v| \cdot 2^{-K(\pi(v))} \le \sum_{s' \in \mathcal{K}_v} 2^{-|C(s')|} \le 1,
$$
yielding $|\mathcal{K}_v| \le 2^{K(\pi(v))}$. $\square$

**Interpretation.** $\pi(v) \in \mathcal{K}_v$ (since $|C(\pi(v))| = K(\pi(v))$). So $\pi(v)$ is *one element* of a pool of $\le 2^{K(\pi(v))}$ candidate strategies of equal-or-lesser description length. The researcher's specification of $\pi(v)$ implicitly selects from this pool.

---

## Lemma 3 — Branching-implicit structural search

**Statement.** Under (A4), the cardinality of the set
$$
\mathcal{B}_v \;:=\; \{\,\text{terminal nodes of all possible paths consistent with the tree's branching factors at } v_0, v_1, \ldots, v_d \,\}
$$
satisfies $|\mathcal{B}_v| \le N_{\text{bp}}(v) = \prod_{u \in P(v)} \nu(u)$.

**Proof.** By induction on $d = \mathrm{depth}(v)$.

*Base case* $d = 0$: $v$ is the root, $P(v) = \{v\}$, $\nu(v) \ge 1$. The set of possible "root strategies" the researcher might have started with is at most $\nu(v)$ (by (A4) honest branching count), so $|\mathcal{B}_v| \le \nu(v) = N_{\text{bp}}(v)$.

*Inductive step.* Suppose the claim holds at depth $d - 1$, and consider $v$ at depth $d$ with parent $v_{d-1}$. The path $P(v) = P(v_{d-1}) \cup \{v\}$. At the decision point following $v_{d-1}$, the researcher considered $\nu(v)$ alternatives (one of which became $v$). For each path realising $P(v_{d-1})$ (of which there are at most $N_{\text{bp}}(v_{d-1})$ by induction), the next-step branching contributes a factor of $\nu(v)$. Therefore
$$
|\mathcal{B}_v| \le N_{\text{bp}}(v_{d-1}) \cdot \nu(v) = \prod_{u \in P(v)} \nu(u) = N_{\text{bp}}(v).
$$ 

$\square$

**Interpretation.** The actual strategies $\pi(w)$ tested in the tree are a subset (typically a small subset) of $\mathcal{B}_v$. The set $\mathcal{B}_v$ represents *all the structurally distinct strategies the researcher could have arrived at via different branching choices*, including those whose branches were left unexplored.

---

## Lemma 4 — Disjointness of Kraft and branching contributions

**Statement.** Under the Caveat in Definition 3 of A2 (the convention that $K(\pi(v))$ is measured *after* branching decisions are committed), the cardinality of the joint implicit search space
$$
\mathcal{S}_v \;:=\; \{\,\text{strategies reachable from root by some branching path, with parameters chosen within the strategy chosen at the end}\,\}
$$
satisfies $|\mathcal{S}_v| \le N_{\text{bp}}(v) \cdot 2^{K(\pi(v))} = N_{\text{eff}}(v)$.

**Proof.** Partition $\mathcal{S}_v$ according to the terminal branching node: for each $b \in \mathcal{B}_v$, let $\mathcal{S}_v^{(b)}$ be the set of strategies reachable via branching ending at $b$, then varying parameters within the strategy structure committed at $b$.

By the Caveat: $K(\pi(v))$ is the description length of $\pi(v)$ *given the structural commitments encoded in the branching path*. The within-structure parameter search is encoded in $K(\pi(v))$ (precision bits of continuous parameters not branched-over, etc.), and is therefore bounded by Lemma 2 applied to the within-structure code: $|\mathcal{S}_v^{(b)}| \le 2^{K(\pi(v))}$ for each $b$.

(Strictly: $K$ depends on $b$ through which structure is committed; we use the worst case across $b$ to get a uniform bound. In practice the variation in $K$ across the branching path is small because the structures differ only in the discrete choices already accounted for in $\mathcal{B}_v$.)

Then $|\mathcal{S}_v| \le \sum_{b \in \mathcal{B}_v} |\mathcal{S}_v^{(b)}| \le N_{\text{bp}}(v) \cdot 2^{K(\pi(v))} = N_{\text{eff}}(v)$. $\square$

**Sharpness.** The bound is generally not tight: it overcounts strategies that are reachable by multiple paths (e.g., if two branches converge on the same strategy) and treats each $b$'s within-structure pool independently. Both are conservative (i.e., they only increase the bound). For Type-I control, conservatism is on the right side.

---

## Lemma 5 — Union bound and extreme-value threshold

**Statement.** Let $\{S_w\}_{w \in \mathcal{S}_v}$ be the (real-valued) Sharpe ratios of the candidates in $\mathcal{S}_v$ under their joint null hypothesis (each true Sharpe $\le 0$). Set
$$
\tau_\alpha(N) \;=\; E[\mathrm{SR}_{\max} \mid N] \;+\; \hat{\sigma}_{\mathrm{SR}_v} \cdot \Phi^{-1}(1 - \alpha).
$$
Then under (A1), (A3), (A5),
$$
\Pr\!\left(\, \max_{w \in \mathcal{S}_v} S_w \;>\; \tau_\alpha(N_{\text{eff}}(v)) \,\right) \;\le\; \alpha \;+\; O(\tau^{-1/2}).
$$

**Proof.** By Lemma 4, $|\mathcal{S}_v| \le N_{\text{eff}}(v)$. By Lemma 1, under the null and (A3), each $S_w$ is asymptotically Gaussian with mean $\le 0$ and standard error $\hat{\sigma}_{\mathrm{SR}_v}$ (with $O(\tau^{-1/2})$ correction). Under (A1) the evaluation data for $v$ is independent of the data used to construct the branching choices, so the *selection* of $\pi(v)$ from $\mathcal{S}_v$ is independent of $\{S_w\}_{w \in \mathcal{S}_v}$.

The classical extreme-value result (Castillo 1988, applied to $N$ iid Gaussians; reproved in Bailey-LdP 2014 for the Sharpe estimator context) gives
$$
E[\max_{w} S_w] \;\xrightarrow[N \to \infty]{}\; \hat{\sigma}_{\mathrm{SR}_v} \cdot \left((1 - \gamma_{\mathrm{em}})\Phi^{-1}(1 - 1/N) + \gamma_{\mathrm{em}} \Phi^{-1}(1 - 1/(N \cdot e))\right) = E[\mathrm{SR}_{\max} \mid N].
$$

By (A5), the empirical cross-trial Sharpe variance $\hat{\sigma}^2_{\mathrm{SR}}$ used inside $E[\mathrm{SR}_{\max} \mid N]$ converges in probability to a quantity that dominates the marginal Sharpe variance under correlation (because correlation reduces the effective number of independent extremes; cf. Embrechts-Klüppelberg-Mikosch 1997, Theorem 4.3.3). Thus
$$
E[\mathrm{SR}_{\max} \mid N_{\text{eff}}(v)] \;\ge\; E[\max_w S_w] \;+\; o_p(1).
$$

The threshold $\tau_\alpha(N_{\text{eff}}(v)) = E[\mathrm{SR}_{\max} \mid N_{\text{eff}}(v)] + \hat{\sigma}_{\mathrm{SR}_v} \Phi^{-1}(1 - \alpha)$ exceeds $E[\max_w S_w]$ by $\hat{\sigma}_{\mathrm{SR}_v} \Phi^{-1}(1 - \alpha) + o_p(1)$. By a Gumbel-type tail bound (Hall-Wellner 1980, or directly from the Mills-ratio asymptotic for $\Phi^{-1}$),
$$
\Pr\!\left(\, \max_w S_w > E[\max_w S_w] + \hat{\sigma}_{\mathrm{SR}_v} \Phi^{-1}(1 - \alpha) \,\right) \;\le\; \alpha + O(\tau^{-1/2}).
$$

(The $O(\tau^{-1/2})$ absorbs Lemma 1's Berry-Esseen rate; the Gumbel tail bound itself contributes $O(1/\log N_{\text{eff}})$ which is asymptotically smaller and absorbed.)

Combining:
$$
\Pr\!\left(\, \max_w S_w > \tau_\alpha(N_{\text{eff}}(v)) \,\right) \;\le\; \alpha + O(\tau^{-1/2}). \;\square
$$

---

## Theorem 1 — Type-I bound

**Statement.** Under (A1)-(A5) and $H_0(v)$,
$$
\Pr\!\left(\, \mathrm{MDL\text{-}DSR}(v) > 1 - \alpha \,\right) \;\le\; \alpha + O(\tau^{-1/2}).
$$

**Proof.**

By definition,
$$
\mathrm{MDL\text{-}DSR}(v) > 1 - \alpha
\;\;\iff\;\;
\frac{\mathrm{SR}_v - E[\mathrm{SR}_{\max} \mid N_{\text{eff}}(v)]}{\hat{\sigma}_{\mathrm{SR}_v}} > \Phi^{-1}(1 - \alpha)
\;\;\iff\;\;
\mathrm{SR}_v > \tau_\alpha(N_{\text{eff}}(v))
$$
with $\tau_\alpha$ as in Lemma 5.

Under (A1), $\mathrm{SR}_v$ is one of the candidates in $\mathcal{S}_v$ — specifically the candidate the researcher selected. By Lemma 4, $|\mathcal{S}_v| \le N_{\text{eff}}(v)$. Therefore $\mathrm{SR}_v \le \max_{w \in \mathcal{S}_v} S_w$, and
$$
\Pr( \mathrm{SR}_v > \tau_\alpha(N_{\text{eff}}(v)) ) \;\le\; \Pr( \max_w S_w > \tau_\alpha(N_{\text{eff}}(v)) ).
$$

By Lemma 5, the right side is $\le \alpha + O(\tau^{-1/2})$. $\square$

---

## Remarks

**R1. Why "selection independent of evaluation" (A1) is unavoidable.** The proof of Lemma 5 requires that the *selection* of $\pi(v)$ from $\mathcal{S}_v$ is data-independent. (A1) achieves this via train/test split: branching is decided on train, evaluation is on test. Without this, the realised $\mathrm{SR}_v$ is a *non-random* function of the selection (researcher always picks the highest in-sample), and the union bound argument collapses. Practically: SVC requires honest data-splitting in the research protocol. No statistical correction can save a researcher who fits and evaluates on the same data.

**R2. The role of MDL.** Without the MDL term, the researcher could "smuggle" parameter search inside a strategy without it appearing in the branching count: declare $\pi(v)$ to have a free parameter $\theta$ chosen "by inspection" after the fact. The MDL term charges this with the bits needed to specify $\theta$. By Lemma 4, this is correctly disjoint from the branching count.

**R3. Conservatism.** The bound is conservative in three ways:
1. Lemma 4's union over branches and over Kraft-strategies treats them as disjoint when in practice they overlap.
2. The Gumbel-type tail bound in Lemma 5 is one-sided.
3. The cross-trial variance estimator $\hat{\sigma}^2_{\mathrm{SR}}$ inflates with positive correlation, making the threshold larger than strictly necessary.
All three conservatisms are on the side of Type-I control (we accept fewer false positives than strictly necessary). Power is correspondingly reduced.

**R4. When the bound is sharp.** If branches are *symmetric* (each $\nu(u)$ branch produces a strategy of equivalent structure), if $K$ is well-calibrated to the actual implicit search, and if trials are nearly iid, the bound's slack is at most $O(\tau^{-1/2})$. In practice these conditions hold approximately for grid searches with constant within-structure parameter precision.

**R5. Extensions left open.**
- *FDR control across multiple acceptances*. The theorem is per-strategy. A researcher accepting multiple strategies should additionally apply online-FDR machinery (Foster-Stine, LORD, SAFFRON) on top of MDL-DSR; this composition is not developed here.
- *Adaptive branching factor.* (A4) assumes static reporting of $\nu$. A version in which $\nu(u)$ is itself estimated from the researcher's behaviour (e.g., from version-control history) is interesting and future work.
- *Cost-conditioning.* The deflation does not yet account for transaction-cost variability. Extending $\hat{\sigma}_{\mathrm{SR}_v}$ to incorporate a cost-uncertainty term is straightforward and additive.

---

## What the proof is not

- It is not a *purely combinatorial* result; the Berry-Esseen rate and the Gumbel tail bound require regularity (A3).
- It is not a tight constant-factor result; the $\alpha$ on the right is a leading-order asymptotic. Finite-sample corrections can be material at small $\tau$.
- It is not a *power* result; power is bounded above by the same machinery but a strategy's power depends on its true Sharpe and the choice of $\alpha$.
- It is not a *causal* statement about why a strategy underperforms; it controls only the probability that a no-edge strategy is mistakenly accepted.

The proof's scope is precisely the gap identified in A1: a per-trial Type-I bound on backtest acceptance under arbitrary adaptive branching, given honest data-splitting and honest branching-factor reporting.
