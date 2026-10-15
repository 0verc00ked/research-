# V1 — Distribution Robustness Battery

Date: 2026-05-22

**Setup:** K=50 null alternatives, τ=500, α=0.05, 1500 simulations per distribution. Tests whether SVC's Type-I control survives when the regularity assumption (A3) — finite fourth moment, weak dependence — is *violated* in ways common in real financial returns.

## Results

| Distribution | SVC Type-I | median skew | median excess kurt | median ACF(1) | Verdict |
|---|---:|---:|---:|---:|---|
| D1 Gaussian iid | 0.0000 | -0.003 | -0.037 | -0.001 | ✅ PASS |
| D2 Student-t df=3 | 0.0000 | 0.947 | 8.364 | -0.003 | ✅ PASS |
| D3 Student-t df=5 | 0.0000 | 0.268 | 2.404 | -0.002 | ✅ PASS |
| D4 Skew-normal | 0.0000 | 0.440 | 0.182 | -0.003 | ✅ PASS |
| D5 GARCH(1,1) | 0.0000 | 0.040 | 0.352 | 0.002 | ✅ PASS |
| D6 AR(1) phi=0.2 | 0.0007 | 0.003 | -0.049 | 0.196 | ✅ PASS |
| D7 Jump-diffusion | 0.0000 | 0.812 | 7.735 | -0.005 | ✅ PASS |
| D8 Regime-switching | 0.0000 | 0.319 | 3.036 | 0.003 | ✅ PASS |

## Interpretation

Of the 8 distributions tested, 8 produced SVC Type-I ≤ α+0.02 = 0.07.

**Specific distributions to watch:**
- **D2 Student-t df=3:** infinite kurtosis under the t(3) law. The Sharpe estimator loses its CLT in the limit; we expect Type-I inflation here if anywhere.
- **D5 GARCH(1,1):** persistent volatility violates the weak-dependence assumption.
- **D6 AR(1):** persistent return autocorrelation violates A3's iid-like assumption.

If SVC controls Type-I across all 8 distributions (within MC error), the framework is robust to the dependence and tail-thickness patterns typical of real financial returns. If it fails on D2/D5/D6, those are honest documented failure modes.