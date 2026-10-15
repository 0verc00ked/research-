# SVC A8c — Power-improvement variants

Date: 2026-05-22

Setup: K=50 alternatives, tau=500, alpha=0.05, 1500 sims per cell.

## Variants

- **V1 — Adaptive variance:** use empirical cross-trial Sharpe variance instead of the iid lower bound σ² = 1/τ.
- **V3 — Half-Kraft:** use K/2 instead of K. Kraft's bound is very loose for natural strategies; halving acknowledges this.

## Type-I results (null worlds)

| Scenario | Baseline | V1 adaptive var | V3 half-Kraft |
|---|---:|---:|---:|
| S1 iid null | 0.0000 | 0.0027 | 0.0000 |
| S2 correlated null (ρ=0.5) | 0.0000 | 0.0027 | 0.0000 |

## Power results (real edge)

| true SR | Baseline | V1 adaptive var | V3 half-Kraft |
|---:|---:|---:|---:|
| 1.0 | 0.0007 | 0.0053 | 0.0007 |
| 1.5 | 0.0047 | 0.0207 | 0.0047 |
| 2.0 | 0.0267 | 0.0747 | 0.0267 |
| 3.0 | 0.2500 | 0.4767 | 0.2500 |

## Verdict

- **V1 adaptive variance:** IMPROVEMENT (Type-I 0.003/0.003, avg power 0.144 vs 0.071)
- **V3 half-Kraft:**         safe but no power gain (Type-I 0.000/0.000, avg power 0.071 vs 0.071)

## Interpretation

An 'IMPROVEMENT' verdict means the variant preserves Type-I control on both null scenarios AND beats baseline average power on the real-edge scenarios.

If no variant produces an IMPROVEMENT verdict, the conclusion is that SVC's baseline tradeoff is near-Pareto-optimal: you can buy power only by relaxing Type-I, and the existing calibration is on the right side of the frontier for the retail-validation use case.