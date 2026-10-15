# SVC A5 — Case Study on Our Own ~390 Trials

Date: 2026-05-21

Apply Sequential Validation Calculus *retrospectively* to the strategies we have already tested across W3-4, D3+D1+D5, and W7-8. For each candidate, we compute three verdicts:

1. **Naive DSR** — treats the candidate as if `N_trials = 1` (the indefensible default)
2. **Grid-DSR** — uses `N_trials = #variants in this strategy's grid`
3. **SVC MDL-DSR** — uses tree-derived `N_eff = N_bp × 2^{K_excess}`

## Verdicts

| Candidate | Naive DSR | Grid DSR | SVC MDL-DSR | Tree N_bp | K_excess | log₂ N_eff |
|---|---:|---:|---:|---:|---:|---:|
| s1_thursday_reversion (best of 12) | 0.683 | 0.000 | 0.000 | 180 | 5120 | 5127.5 |
| s2_vix_regime (best of 24) | 0.087 | 0.000 | 0.000 | 360 | 6648 | 6656.5 |
| s3_dow_dispersion (best of 20) | 0.000 | 0.000 | 0.000 | 300 | 4488 | 4496.2 |
| d5_regime_calm (best of 377) | 0.996 | 0.000 | 0.000 | 7540 | 0 | 12.9 |

## Interpretation

Three observations are pre-registered before we look at the table:

1. **Naive DSR** would have accepted any candidate whose annual Sharpe is high enough to look impressive in isolation. Of these four candidates, only d5 has a meaningfully positive Sharpe; the others fail even on naive DSR.
2. **Grid DSR** correctly punishes the within-grid search. We expect this to bring all four below 0.95.
3. **SVC MDL-DSR** further punishes the across-phase research path. The two compositional factors are (a) the **branching product** capturing alternative phases the researcher could have pursued (5 markets × 3 phases × grid size) and (b) **K_excess** charging for strategy code complexity beyond the project baseline.

The expected ordering across columns: Naive DSR ≥ Grid DSR ≥ SVC MDL-DSR.

## Implications

- For candidates that *fail Grid DSR*, SVC adds little — they were dead anyway. 
- For candidates that *pass Grid DSR but fail SVC* (e.g., a strategy with apparent good Sharpe whose grid was modest but whose research-tree branching was large), SVC catches the additional inflation that grid-counting misses.
- For candidates that *pass SVC*, they have survived honest accounting of the whole adaptive research path. In this project, **we expect zero such survivors**, consistent with the cumulative finding.

If d5_regime_calm passes Grid DSR but fails SVC, that is the framework working as designed: the train-window survivor was inflated by 4 levels of unaccounted adaptive search above the 377-variant grid.