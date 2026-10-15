# V5 — Edge Cases and Numerical Stability

Date: 2026-05-22

11 edge cases tested; 11 pass, 0 fail.

## Results

| Case | Verdict | Details |
|---|---|---|
| E1 K=0 (no parameter complexity) | ✅ PASS | log2_N=3.32, mdl_dsr=0.0000 |
| E2 K=10000 (extreme) | ✅ PASS | log2_N=10003, mdl_dsr=0.0 |
| E3 tau=30 (minimum allowed) | ✅ PASS | n_obs=30, mdl_dsr=0.3684 |
| E4 tau=100,000 (very long) | ✅ PASS | n_obs=100000, mdl_dsr=0.0000 |
| E5 Single-trial tree (no branching) | ✅ PASS | N_bp=1, log2_N=0.00 |
| E6 Very deep tree (depth 100) | ✅ PASS | depth=100, log2_N=100.00, N_bp=1267650600228229401496703205376 |
| E7 Very wide tree (ν=1000) | ✅ PASS | N_bp=1000, log2_N=9.97 |
| E8 Near-zero variance (1e-10 std) | ✅ PASS | std=1.03e-10, mdl_dsr=1.0000 |
| E9 Exact zero std (returns all equal) | ✅ PASS | std=0, mdl_dsr=0.0 |
| E10 Mixed deep+wide (5 levels × ν=10) | ✅ PASS | N_bp=100000, log2_N=16.61 |
| E11 Monotonicity: more branching → lower SVC | ✅ PASS | values for ν=1,10,100,1000: ['0.7987', '0.0840', '0.0032', '0.0001'] |

## Interpretation

All cases that produce finite, in-range mdl_dsr values are PASS. Cases that throw exceptions or produce out-of-range values are FAIL.

Of 11 edge cases tested, 11 pass. Failures (if any) document implementation bugs that need to be fixed before publication.