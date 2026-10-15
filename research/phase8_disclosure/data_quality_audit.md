# W7-8 Data Quality Audit

Date: 2026-05-21

Audit window: 2025-11-12 → 2026-05-30

Tickers audited: 94

Divergence threshold: |unadj_ret − adj_ret| > 1.0% per day → corp action

## Corporate-action incidence

- total corp-action days flagged: **5**
- tickers with at least one CA: **5/94**
- disclosures within ±2d of CA: **1/5234 (0.0%)**

## Statistics: raw vs clean vs contaminated

| metric | RAW (W7-8 original) | CLEAN | CONTAMINATED only |
|---|---:|---:|---:|
| n | 5234 | 5233 | 1 |
| median |ret_eod_next| | 0.0151 | 0.0151 | 0.0632 |
| p75 | 0.0285 | 0.0284 | 0.0632 |
| p90 | 0.0444 | 0.0444 | 0.0632 |
| p95 | 0.0565 | 0.0565 | 0.0632 |
| share with |ret|>0.5% | 80.4% | 80.4% | 100.0% |

## Top-20 movers from W7-8 — how many were corp-action contaminated?

- of the top 20 largest |ret_eod_next| disclosures in W7-8, **0** were within ±2d of a corp action
- the remaining 20 were genuine moves

## Interpretation

**Corp-action contamination is real but limited (<5/20 top movers affected).** 
The W7-8 G0d failure cannot be explained away by data quality. The negative 
finding stands.

## Recommendation

- Update the W7.4 discovery report to use the cleaned dataset
- The G0d gate evaluation should be re-run on the cleaned sample
- For W8 stratification, re-sample 'movers' from clean data only