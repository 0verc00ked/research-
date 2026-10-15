# D3 — HMM Regime Report

Date: 2026-05-21

Training window: 2010-01 → 2025-01
OOS window: 2025-01 → 2026-05  (339 bars)

## State characterisation (in-sample)

| state | mean log_ret/d | mean rv20 (ann) | dwell (bars) | interpretation |
|---|---:|---:|---:|---|
| 0 | -0.0001 | 0.2347 | 33.8 | bear / drawdown |
| 1 | +0.0004 | 0.1643 | 36.2 | range / calm |
| 2 | +0.0006 | 0.1036 | 63.9 | bull / trend |

## Known events — sanity check

| event | date | inferred state | interpretation |
|---|---|---:|---|
| covid_2020-03-23 | 2020-03-23 | 0 | bear / drawdown |
| russia_war_2022-02-24 | 2022-02-24 | 0 | bear / drawdown |
| adani_2023-01-25 | 2023-01-25 | 2 | bull / trend |
| modi_mandate_2024-06-04 | 2024-06-04 | 0 | bear / drawdown |
| calm_2017-06-01 | 2017-06-01 | 2 | bull / trend |
| calm_2019-08-01 | 2019-08-01 | 2 | bull / trend |

## OOS regime distribution (2025-01+)

- state 0 (bear / drawdown): 76 bars (22.4%)
- state 1 (range / calm): 69 bars (20.4%)
- state 2 (bull / trend): 194 bars (57.2%)

## Output artifact

Per-day state + posterior saved to: `data_cache/regime/nifty_regime_path.csv`
This file is consumed by D5 (setup discovery) as a feature.