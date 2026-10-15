# W7.5 — Free-attribute discrimination analysis

Date: 2026-05-21

Sample: 5,234 mid-cap disclosures.

## Category discrimination (does category alone separate movers from non-movers?)

Overall median |ret_eod_next|: **0.0151**

| category | n | median |ret| | p75 | p95 | vs overall |
|---|---:|---:|---:|---:|---:|
| Company Update | 4044 | 0.0146 | 0.0278 | 0.0563 | 0.96x |
| Board Meeting | 367 | 0.0171 | 0.0309 | 0.0582 | 1.13x |
| Insider Trading / SAST | 277 | 0.0144 | 0.0295 | 0.0550 | 0.95x |
| AGM/EGM | 155 | 0.0175 | 0.0268 | 0.0504 | 1.16x |
| Result | 146 | 0.0194 | 0.0356 | 0.0667 | 1.28x |
| Corp. Action | 115 | 0.0170 | 0.0336 | 0.0645 | 1.12x |
|  Corp Action | 25 | 0.0199 | 0.0369 | 0.0673 | 1.31x |
| Corp Action | 7 | 0.0123 | 0.0221 | 0.0323 | 0.81x |

**Spread:** top-vs-bottom category ratio (n≥50): 1.31x vs 0.95x → category alone discriminates by **1.38x** between extremes.

## Time-of-day (IST)

- disclosures during market hours (9–15 IST): **1823** (35%)
- disclosures after market hours: **3411** (65%)

| hour IST | n | median |ret| |
|---:|---:|---:|
| 08 | 53 | 0.0175 |
| 09 | 67 | 0.0140 |
| 10 | 151 | 0.0157 |
| 11 | 249 | 0.0144 |
| 12 | 274 | 0.0139 |
| 13 | 300 | 0.0114 |
| 14 | 312 | 0.0139 |
| 15 | 470 | 0.0160 |
| 16 | 641 | 0.0142 |
| 17 | 697 | 0.0152 |
| 18 | 642 | 0.0156 |
| 19 | 485 | 0.0185 |
| 20 | 327 | 0.0159 |
| 21 | 257 | 0.0153 |
| 22 | 131 | 0.0154 |
| 23 | 112 | 0.0169 |

## Pre-LLM filter: high-signal categories (n≥50, median |ret| > 1.5x overall)

(none — category alone cannot identify high-signal disclosures)

## What this means for W8

- If category alone gives a 3x+ separation, the LLM has to beat that to justify itself.
- If category gives ~1x (no separation), the LLM is the only path to filtering.
- In the time-of-day breakdown, after-hours disclosures publish during a closed market,
  so the 'ret_1h' is effectively 'first hour of next session' — much more reaction time
  for an LLM than the raw number suggests.