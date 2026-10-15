# SVC A8a — Grid-DSR-vs-SVC Wedge Experiment

Date: 2026-05-22

Demonstrates SVC's unique value by constructing scenarios where Grid DSR is fooled but SVC catches the inflation.

**Setup:** 1000 simulations per N_bp value. Within-phase grid = 20. K_excess = 30 bits. tau = 500. alpha = 0.05.

All strategies are null (true Sharpe = 0). The researcher 'searches' across N_bp phases, in each running a 20-cell grid. Reports the best Sharpe across all phases.

Naive DSR uses N=1 (the indefensible default).
Grid DSR uses N=20 (the grid the researcher acknowledges).
SVC MDL-DSR uses N_eff = N_bp × 20 × 2^K (honest accounting).

## Results

| N_bp | Naive Type-I | Grid Type-I | SVC Type-I | Wedge (Grid − SVC) |
|---:|---:|---:|---:|---:|
| 1 | 0.6220 | 0.0000 | 0.0000 | +0.0000 |
| 5 | 0.9950 | 0.0010 | 0.0000 | +0.0010 |
| 25 | 1.0000 | 0.0000 | 0.0000 | +0.0000 |
| 100 | 1.0000 | 0.0230 | 0.0000 | +0.0230 |
| 500 | 1.0000 | 0.0810 | 0.0000 | +0.0810 |

## Interpretation

**Grid DSR Type-I should stay around its design level (≤ 0.05) regardless of N_bp**, because Grid DSR only knows about the within-phase grid (size 20) and not the across-phase exploration. This is by construction.

**SVC Type-I should also stay around its design level (≤ 0.05) at all N_bp values**, because SVC accounts for the across-phase branching.

**The wedge appears when:** the researcher's reported Sharpe happens to clear Grid DSR's threshold (which is ignorant of the cross-phase search) but is correctly rejected by SVC. Each row of Grid_Type-I above α represents false positives Grid DSR would allow.

## What this proves

If Grid DSR Type-I exceeds SVC Type-I, that excess is the empirical demonstration of SVC's unique contribution beyond Grid DSR. Specifically, Grid DSR is *guaranteed* to leak Type-I at level α (its design), but for any N_bp > 1 the *true* selection is much larger than the grid, so Grid DSR's nominal α understates the actual false-positive risk. SVC closes that gap.