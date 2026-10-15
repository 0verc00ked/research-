# validation/

**Hard G0 prerequisite.** No strategy reaches G1 paper without clearing the gates below.

Source of truth: `research/SYNTHESIS.md` §6 + `research/CONCRETE_PLAN.md` Weeks 1–2.

## Modules (landed 2026-05-21)

| Module | Purpose | Reference |
|---|---|---|
| `trial_log.py` | Append-only SQLite registry. `n_trials_for(name)` is the load-bearing count for DSR. | LdP AFML §11 |
| `cpcv.py` | Combinatorial Purged Cross-Validation. Default N=8, k=2, purge=label_horizon, embargo=2% T. | LdP 2018 |
| `pbo.py` | Probability of Backtest Overfitting via CSCV. Default S=16 → 12,870 splits. | Bailey/Borwein/LdP/Zhu 2014 |
| `dsr.py` | Deflated Sharpe Ratio with skew + kurtosis + n_trials adjustment. | Bailey & LdP 2014, SSRN 2460551 |
| `regime_splits.py` | Bear / calm / shock window partitioning. Forces ≥1 post-2025-01-01 window. | CONCRETE_PLAN §4 |
| `harness.py` | `validate()` entrypoint composing all gates. Returns structured `GateResult`. | this repo |

## Gate thresholds (CONCRETE_PLAN.md + SYNTHESIS §6)

| Gate | Threshold |
|---|---|
| `pbo` | ≤ 0.5 hard, ≤ 0.2 soft |
| `dsr` | ≥ 0.95 |
| `cpcv.folds_positive_ratio` | ≥ 0.6 |
| `n_trades` | ≥ 50 |
| post-cutoff window | ≥ 1 profitable window after 2025-01-01 (enforced separately on regime-partitioned runs) |

## Hard rules

1. **N_trials is honestly counted.** Every parameter sweep, every prompt re-roll, every code tweak that materially changes the strategy increments it via `TrialLog.record()`. Lying defeats DSR.
2. **The registry is append-only.** No deletions. No "this trial doesn't count." If you ran it, it counts.
3. **No LLM call inside the validation loop.** LLM cannot grade its own homework.
4. **Failed trials are recorded too.** Survivorship bias on your own work is real.
5. **Post-LLM-cutoff window is non-negotiable.** Profit Mirage (arXiv:2510.07920) showed 50–72% return decay across the cutoff boundary. At least one validation window must be 2025-01 or later.

## Quick use

```python
from agent_trader.validation import TrialLog, TrialRecord, validate, hash_code

log = TrialLog("trials.db")
n_trials = log.n_trials_for("nifty_weekly_otm_v0") + 1   # honestly counted

result = validate(
    strategy_returns=per_bar_returns,        # shape (T,)
    n_trades=n_trades,
    n_trials=n_trials,
    variants_matrix=variants_returns,        # shape (T, M) — all variants you tried
    label_horizon=5,                         # bars
)
print(result.verdict, result.reasons)

log.record(TrialRecord(
    strategy_name="nifty_weekly_otm_v0",
    code_hash=hash_code(open("strategies/nifty_weekly_otm_v0/strategy.py").read()),
    params={"min_conviction": 0.6},
    dataset_hash="...",
    metrics=result.metrics,
    gates=result.gates,
    verdict=result.verdict,
))
```

## G0a — the harness self-test

`tests/test_harness_g0a.py` constructs a *known-overfit* synthetic strategy
(best-of-100 random walks selected by Sharpe). A correct harness must flag
this with PBO ≥ 0.5 *and* refuse a PASS verdict. If that test fails, fix the
harness before anything else.
