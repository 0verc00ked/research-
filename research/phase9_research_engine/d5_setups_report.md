# D5 — Setup Discovery Report

Date: 2026-05-21

Universe: NIFTY 5-day forward return

N_trials (honest, across orders 1-3): **377**

Train window: 2015 → 2022 (1663 bars)
Val window:   2022 → 2024 (477 bars)
Test window:  2024 → 2026 (563 bars) ← required post-cutoff OOS

## Survivor count per stage

| stage | criterion | survivors |
|---|---|---:|
| 1 train (BH-FDR @ 0.05) | p_corrected ≤ 0.05 | 3 |
| 2 val | same sign & |t|≥1.0 | 1 |
| 3 OOS | same sign (best-effort) | 0 |

## Setups surviving train + val + OOS sign-consistency

| setup | train mean_ret | val n / mean / t | OOS n / mean / t / sign |
|---|---:|---|---|
| regime_calm | +0.0025 | 311 / +0.0034 / +3.53 | 312 / -0.0005 / -0.48 / ✗ |

## Honest read

**No setups cleared all three gates.** This is the most likely outcome given the base rate. 
The conjunction space was exhaustively searched with honest N_trials accounting. Nothing survives.

Next: feed the surviving train+val candidates (if any) through the validation harness 
with full DSR/PBO/CPCV, treating N_trials = 377. With that many trials, 
DSR will require extraordinary Sharpe to pass — likely none will.