# V4 — Real-Data Application

Date: 2026-05-22

NIFTY (^NSEI) daily closes, 2010-01-04..2026-05-21, 4022 bars. Random null strategies + buy-and-hold + adaptive simulation.

## R1 — Type-I on real NIFTY data (null strategies)

K=50 random signal strategies per window of τ=500 bars; 1000 windows tested.

| Method | Empirical Type-I |
|---|---:|
| Naive DSR | 0.4110 |
| Grid DSR  | 0.0000 |
| **SVC**   | **0.0000** |

## R2 — Known-edge: buy-and-hold NIFTY

- Observed Sharpe (annual): **0.570** over 4021 bars (~16 years)
- Naive DSR: 0.9873
- SVC (single hypothesis, no branching): 0.9873

## R3 — Adaptive researcher on real NIFTY

Researcher 'searched' 3 × 5 × 50 = 750 candidates, picks best.

- Grid DSR (counts ν=K_grid only) Type-I:  **0.0000**
- SVC (counts full tree) Type-I:           **0.0000**
- Wedge (Grid - SVC):                       +0.0000

## Interpretation

**R1** validates that SVC's Type-I control extends from synthetic iid data to *real* market data with all its empirical features (heavy tails, volatility clustering, autocorrelation). If SVC Type-I ≤ α on real NIFTY null strategies, the framework transfers to practice.

**R2** verifies that SVC does *not* mistake buy-and-hold NIFTY for noise. A single honest hypothesis with no branching should be evaluated on its merits.

**R3** is the operationally most relevant test: an adaptive researcher reports a Grid DSR of  α nominal but the *actual* Type-I on real data is the larger number above. SVC closes the gap — its empirical Type-I should stay near α.