# W7.4 — Discovery Analysis v1

Date: 2026-05-21

## Sample

- mid-cap disclosures with intraday data: **5234**
- unique tickers: 94
- date range: 2025-11-22T04:26:40.743000+00:00 → 2026-05-20T18:28:30.463000+00:00

## Critical question #1 — do disclosures cluster around moves?

### |ret_eod_next| distribution: disclosure bars vs random baseline

| pct | disclosure | random | ratio |
|-----|-----------:|-------:|------:|
| p50 | 0.0151 | 0.0131 | 1.15x |
| p75 | 0.0285 | 0.0242 | 1.18x |
| p90 | 0.0444 | 0.0380 | 1.17x |
| p95 | 0.0565 | 0.0484 | 1.17x |
| p99 | 0.0785 | 0.0749 | 1.05x |

### |ret_1h| distribution: disclosure bar vs baseline

| pct | disclosure | random | ratio |
|-----|-----------:|-------:|------:|
| p50 | 0.0040 | 0.0032 | 1.27x |
| p75 | 0.0078 | 0.0064 | 1.21x |
| p90 | 0.0138 | 0.0115 | 1.20x |
| p95 | 0.0177 | 0.0168 | 1.06x |
| p99 | 0.0412 | 0.0337 | 1.22x |

**Interpretation:** ratios well above 1.0 mean disclosures cluster around bigger moves than random bars — signal exists. Ratios near 1.0 mean disclosures look like any other bar — channel is likely dead.

## Critical question #2 — absorption half-life (only on disclosures with |ret_eod_next| > 0.5%)

- materially-reacted disclosures: **4209** (80.4% of total)
- median fraction of EOD move realised at +1h: **0.09**
- median fraction of EOD move realised at +2h: **0.18**
- median fraction of EOD move realised at +4h: **0.34**

**Interpretation:** if median frac_1h is already > 0.7, half the move is in <1h — too fast for LLM analysis to be useful. If frac_1h < 0.5 and frac_4h > 0.7, the absorption window is in the LLM strike zone.
