# D1 — Lead-Lag Scan Report

Date: 2026-05-21

Universe: 22 instruments

Window: 2015-01-02 .. 2024-12-31  (2378 bars)

Lags scanned: 1, 2, 3, 5, 10 days

FDR target: 0.05 (Benjamini-Hochberg)

Total pair-lag tests: 424

**Significant lead-lag relationships after FDR: 424**

## Top 30 by |z|

| lead | lagger | lag (d) | corr | z | p | q |
|---|---|---:|---:|---:|---:|---:|
| SP500 | USDINR | 1 | -0.304 | -15.30 | 1.00e-300 | 1.843e-299 |
| NASDAQ | NIFTYIT | 1 | +0.281 | +14.06 | 1.00e-300 | 1.843e-299 |
| NASDAQ | USDINR | 1 | -0.278 | -13.89 | 1.00e-300 | 1.843e-299 |
| SP500 | NIFTYIT | 1 | +0.271 | +13.56 | 1.00e-300 | 1.843e-299 |
| SP500 | NIFTY | 1 | +0.246 | +12.23 | 1.00e-300 | 1.843e-299 |
| NASDAQ | NIFTY | 1 | +0.244 | +12.11 | 1.00e-300 | 1.843e-299 |
| NASDAQ | INFY | 1 | +0.240 | +11.92 | 1.00e-300 | 1.843e-299 |
| SP500 | INFY | 1 | +0.233 | +11.59 | 1.00e-300 | 1.843e-299 |
| NIFTY | USDINR | 1 | -0.231 | -11.47 | 1.00e-300 | 1.843e-299 |
| BANKNIFTY | USDINR | 1 | -0.231 | -11.45 | 1.00e-300 | 1.843e-299 |
| SP500 | NIFTYMETAL | 1 | +0.207 | +10.22 | 1.00e-300 | 1.843e-299 |
| NASDAQ | TCS | 1 | +0.206 | +10.18 | 1.00e-300 | 1.843e-299 |
| NASDAQ | NIFTYAUTO | 1 | +0.205 | +10.13 | 1.00e-300 | 1.843e-299 |
| NIFTYAUTO | USDINR | 1 | -0.203 | -10.05 | 1.00e-300 | 1.843e-299 |
| NASDAQ | NIFTYMETAL | 1 | +0.202 | +10.00 | 1.00e-300 | 1.843e-299 |
| SP500 | NIFTYAUTO | 1 | +0.201 | +9.94 | 1.00e-300 | 1.843e-299 |
| SP500 | TCS | 1 | +0.199 | +9.81 | 1.00e-300 | 1.843e-299 |
| HDFCBANK | USDINR | 1 | -0.192 | -9.47 | 1.00e-300 | 1.843e-299 |
| SP500 | BANKNIFTY | 1 | +0.191 | +9.44 | 1.00e-300 | 1.843e-299 |
| LT | USDINR | 1 | -0.188 | -9.28 | 1.00e-300 | 1.843e-299 |
| SBIN | USDINR | 1 | -0.185 | -9.12 | 1.00e-300 | 1.843e-299 |
| NASDAQ | BANKNIFTY | 1 | +0.177 | +8.70 | 1.00e-300 | 1.843e-299 |
| SP500 | ICICIBANK | 1 | +0.169 | +8.32 | 1.00e-300 | 1.843e-299 |
| SP500 | LT | 1 | +0.166 | +8.18 | 2.22e-16 | 3.923e-15 |
| NIFTYFMCG | USDINR | 1 | -0.158 | -7.77 | 7.55e-15 | 1.280e-13 |
| ICICIBANK | USDINR | 1 | -0.155 | -7.63 | 2.40e-14 | 3.911e-13 |
| NASDAQ | ICICIBANK | 1 | +0.155 | +7.62 | 2.53e-14 | 3.975e-13 |
| RELIANCE | USDINR | 1 | -0.154 | -7.56 | 3.95e-14 | 5.985e-13 |
| SP500 | HDFCBANK | 1 | +0.153 | +7.50 | 6.24e-14 | 9.123e-13 |
| NASDAQ | RELIANCE | 1 | +0.152 | +7.44 | 9.77e-14 | 1.381e-12 |

## Honest interpretation

- The correlations are *small* — typical r in [0.05, 0.20]. That's expected: 
  large lead-lag effects would already be arbitraged.
- FDR-significance ≠ economic significance. A relationship with r=0.08 means 
  the lagger's variance explained by the lead is ~0.6%. Need to think hard 
  about how to extract tradable edge from this.
- The lead direction matters: 'GOLD leads HDFCBANK' is plausible (global risk appetite). 'TCS leads BRENT' is suspect — could be artifact / spurious.
- Stability check: would need to verify these relationships persist in the 2025+ OOS window before any strategy uses them.