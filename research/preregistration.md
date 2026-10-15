# Pre-registration — Week 3-4 Hypotheses

**Date locked:** 2026-05-21 (committed to git BEFORE any backtest run on these strategies)
**Discipline:** López de Prado pre-registration. Modifying hypothesis after seeing results = new trial, increments N_trials.

This file freezes three hypotheses *before* a single backtest runs. If a hypothesis is changed after looking at results, it counts as a new trial against DSR, *not* as the same hypothesis "refined."

---

## S1 — Thursday (NIFTY weekly expiry) reversion

**Mechanism (one paragraph):** Indian retail flow concentrates in NIFTY weekly options expiring every Thursday. Forced unwinding of in-the-money positions, panic-buying of cheap OTM hopes, and gamma-driven hedging by market-makers near close create predictable directional pressure on the index. The hypothesis: a strong directional move into Thursday tends to *partially reverse* by the following Tuesday because retail positioning unwinds and dealer hedges normalize. This is a "post-expiry mean-reversion" effect.

**Entry rule:** At Thursday close, compute prior_window-day cumulative return on NIFTY (^NSEI). If return > +reversion_threshold%, take SHORT NIFTY. If return < -reversion_threshold%, take LONG NIFTY. Else flat.

**Exit rule:** Next Tuesday close (≈ 2.5 trading days hold).

**Position size:** Constant 1 unit per trade (returns reported per-unit).

**Parameter grid (variants for PBO):**
- prior_window ∈ {3, 5, 10, 15} days
- reversion_threshold ∈ {0.5, 1.0, 2.0}% (cumulative)
Total variants: 12.

**Universe:** ^NSEI only.
**Data window:** 2010-01-01 → 2026-05-21 (in-sample 2010–2024, OOS 2025+).
**Cost model:** 0.05% per side round trip (worst plausible retail).

---

## S2 — India-VIX regime conditional momentum

**Mechanism (one paragraph):** India VIX measures 30-day expected volatility of NIFTY options. Empirically, periods of *low* VIX (below historical 20th percentile) correspond to calm/trending markets where short-term momentum tends to persist; periods of *high* VIX (above 80th percentile) correspond to panic/crash conditions where mean-reversion or capitulation dominates. The hypothesis: trade momentum *only when VIX is low*, and *fade momentum* when VIX is high.

**Entry rule:** Daily, at close, compute:
- VIX percentile within trailing 252 trading days
- Prior `mom_lookback`-day return on NIFTY (^NSEI)

If VIX_pct < vix_low_pct AND prior_return > 0 → LONG NIFTY next day
If VIX_pct > vix_high_pct AND prior_return > 0 → SHORT NIFTY next day
Else flat.

**Exit rule:** Hold `hold_days` then exit.

**Position size:** Constant 1 unit per trade.

**Parameter grid:**
- mom_lookback ∈ {5, 10, 20} days
- hold_days ∈ {3, 5}
- vix_low_pct ∈ {20, 30}
- vix_high_pct ∈ {70, 80}
Total variants: 24.

**Universe:** ^NSEI, ^INDIAVIX.
**Data window:** same as S1.
**Cost model:** 0.05% per side.

---

## S3 — Day-of-week dispersion (NIFTY vs BANKNIFTY)

**Mechanism (one paragraph):** Documented day-of-week anomalies exist on Indian indices (Patel 2008; multiple subsequent studies). Specifically, the *spread* between NIFTY (broad large-cap) and BANKNIFTY (concentrated financials) tends to behave differently on Mondays (post-weekend information catch-up favours banks via opening flow) vs Fridays (positioning into weekend tends to defensive large-cap). The hypothesis: a long-short pair trade triggered on specific weekdays captures this dispersion.

**Entry rule:** At market open on `entry_day` (one of Mon..Fri):
- LONG ^NSEI / SHORT ^NSEBANK with `weight` capital each side (dollar-neutral)
OR test the inverse:
- SHORT ^NSEI / LONG ^NSEBANK

**Exit rule:** Close both legs at the close of `entry_day + hold_days`.

**Position size:** Each leg = 1 unit (dollar-neutral pair).

**Parameter grid:**
- entry_day ∈ {Mon, Tue, Wed, Thu, Fri} (5)
- direction ∈ {long_nifty, short_nifty} (2)
- hold_days ∈ {1, 2} (2)
Total variants: 20.

**Universe:** ^NSEI, ^NSEBANK.
**Data window:** same as S1.
**Cost model:** 0.05% per side (×2 legs = 0.1% total per round trip).

---

## Honest N_trials accounting

Total hypotheses pre-registered: 3 (S1, S2, S3).
Total variants across all three: 12 + 24 + 20 = **56**.

For each individual strategy run through `validate()`, n_trials passed = number of variants in that strategy's grid (because all are tested simultaneously on the same data).

The `trial_log` will record one row per variant per strategy = 56 rows after W3-4.

**Any post-hoc parameter exploration adds to n_trials**. If we look at results and "try one more thing," that one more thing is trial #57, not a refinement of trial #56.

## Expected outcome

Honest prior:
- P(at least one of S1/S2/S3 passes G0): ~30%
- P(all three fail): ~70%

If all three fail: W3-4 is a *success* — we learned the obvious patterns are insufficiently exploitable for retail capital, *without* spending live capital to discover it.

If one or two pass: those advance to W9-10 deep validation + W11-12 paper.

If all three pass: extremely suspicious; re-audit harness + data for leakage.
