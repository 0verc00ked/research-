# V2 — Head-to-Head Comparison Battery

Date: 2026-05-22

**Setup:** K=50, τ=500, α=0.05, 500 null sims / 500 edge sims, bootstrap & permutation use 200 resamples each.

## Type-I (should be ≤ α=0.05)

| Method | iid null | correlated null (ρ=0.5) |
|---|---:|---:|
| naive | 0.9400 | 0.4960 |
| bonferroni | 0.0420 | 0.0360 |
| bailey_ldp | 0.0000 | 0.0000 |
| svc | 0.0000 | 0.0000 |
| bootstrap | 0.0540 | 0.0560 |
| permutation | 0.0420 | 0.0360 |

## Power (higher is better, given Type-I controlled)

| Method | true SR=1.5 | true SR=2.0 | true SR=3.0 |
|---|---:|---:|---:|
| naive | 0.9740 | 0.9920 | 1.0000 |
| bonferroni | 0.1940 | 0.4680 | 0.8840 |
| bailey_ldp | 0.0320 | 0.1480 | 0.6500 |
| svc | 0.0320 | 0.1440 | 0.6460 |
| bootstrap | 0.2000 | 0.4740 | 0.8900 |
| permutation | 0.2080 | 0.4640 | 0.8880 |

## Per-method verdict

| Method | Controls Type-I? | Power at SR=2.0 | Notes |
|---|---|---:|---|
| naive | ❌ | 0.9920 | Should fail Type-I dramatically — the bar everyone else has to beat |
| bonferroni | ✅ | 0.4680 | Conservative parametric — usually controls Type-I but loses power |
| bailey_ldp | ✅ | 0.1480 | Static-N parametric extreme value — should match SVC for flat trees |
| svc | ✅ | 0.1440 | **Our framework** — should match bailey_ldp here (same N for flat tree) |
| bootstrap | ✅ | 0.4740 | Non-parametric, captures correlation — may have higher power on S2 |
| permutation | ✅ | 0.4640 | Non-parametric exact — gold-standard but computationally heavy |

## Interpretation

For a *flat trial-tree* (the scenario tested here), SVC reduces to Bailey-LdP DSR; they should produce identical verdicts. SVC's *unique* value over Bailey-LdP appears when the tree is non-trivial — see the V1.5 wedge experiment (A8a). What V2 tests is whether SVC is at least as good as the established alternatives in the baseline (flat) case.

Bootstrap and permutation, being non-parametric, may show different behavior under correlation (S2). If they reject substantially more often than SVC on S2, that suggests SVC's parametric extreme-value formula is over-conservative when trials are positively correlated.