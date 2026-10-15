"""W3-W4 runner — backtests all three pre-registered strategies and logs to
trial_log. Read research/preregistration.md before running.

PBO is computed once per strategy (it's a property of the variant ensemble,
not the individual variant). Per-variant logging records Sharpe + n_trades.
Verdict is on the best-in-sample variant (the one that naive selection would
have picked) under honest n_trials.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.backtest.runner import run_daily, run_pair_daily  # noqa: E402
from agent_trader.data.yfinance_loader import load  # noqa: E402
from agent_trader.validation import (  # noqa: E402
    TrialLog,
    TrialRecord,
    hash_code,
    validate,
)
from strategies.s1_thursday_reversion.signal import S1Params, make_signal as s1_signal  # noqa: E402
from strategies.s2_vix_regime.signal import S2Params, make_signal as s2_signal  # noqa: E402
from strategies.s3_dow_dispersion.signal import S3Params, make_signal as s3_signal  # noqa: E402

DATA_DIR = ROOT / "data_cache"
LOG_DB = ROOT / "trial_log.db"
START = "2010-01-01"


def _backtest_grid(grid, runner) -> tuple[np.ndarray, list[float], list[int]]:
    """runner(params) -> BacktestResult. Returns (variants_matrix, sharpes, n_trades)."""
    returns_list = []
    sharpes = []
    n_trades = []
    for p in grid:
        res = runner(p)
        returns_list.append(res.returns)
        std = res.returns.std(ddof=1)
        sharpes.append(
            float(res.returns.mean() / std * np.sqrt(252)) if std > 0 else 0.0
        )
        n_trades.append(res.n_trades)
    variants = np.column_stack(returns_list)
    return variants, sharpes, n_trades


def _log_and_summarise(
    name: str,
    grid,
    variants: np.ndarray,
    sharpes: list[float],
    n_trades: list[int],
    code_hash: str,
    dataset_hash: str,
) -> dict:
    best = int(np.argmax(sharpes))
    best_returns = variants[:, best]

    # One harness run on the best variant; n_trials = honest variant count
    best_result = validate(
        strategy_returns=best_returns,
        n_trades=n_trades[best],
        n_trials=len(grid),
        variants_matrix=variants,
    )

    # Log every variant. Only the best carries the full gates from PBO/CPCV;
    # the rest get a partial record with their own Sharpe + n_trades.
    log = TrialLog(LOG_DB)
    for i, p in enumerate(grid):
        gates = best_result.gates if i == best else {}
        log.record(
            TrialRecord(
                strategy_name=name,
                code_hash=code_hash,
                params=p.__dict__,
                dataset_hash=dataset_hash,
                metrics={"sharpe": sharpes[i], "n_trades": n_trades[i]},
                gates=gates,
                verdict=(best_result.verdict if i == best else "VARIANT"),
                notes=("BEST" if i == best else ""),
            )
        )

    return {
        "name": name,
        "n_variants": len(grid),
        "best_params": grid[best].__dict__,
        "best_sharpe": sharpes[best],
        "best_n_trades": n_trades[best],
        "all_sharpes_summary": {
            "min": float(np.min(sharpes)),
            "median": float(np.median(sharpes)),
            "max": float(np.max(sharpes)),
        },
        "verdict": best_result,
    }


def run_s1(nifty) -> dict:
    grid = S1Params.grid()
    variants, sharpes, n_trades = _backtest_grid(
        grid, lambda p: run_daily(nifty.df, s1_signal(p), cost_per_side=0.0005, warmup=20)
    )
    code_hash = hash_code((ROOT / "strategies/s1_thursday_reversion/signal.py").read_text())
    return _log_and_summarise(
        "s1_thursday_reversion", grid, variants, sharpes, n_trades, code_hash, nifty.fingerprint
    )


def run_s2(nifty, vix) -> dict:
    grid = S2Params.grid()
    variants, sharpes, n_trades = _backtest_grid(
        grid, lambda p: run_daily(nifty.df, s2_signal(p, vix.df), cost_per_side=0.0005, warmup=260)
    )
    code_hash = hash_code((ROOT / "strategies/s2_vix_regime/signal.py").read_text())
    return _log_and_summarise(
        "s2_vix_regime", grid, variants, sharpes, n_trades, code_hash,
        f"{nifty.fingerprint}+{vix.fingerprint}",
    )


def run_s3(nifty, bnk) -> dict:
    grid = S3Params.grid()
    variants, sharpes, n_trades = _backtest_grid(
        grid,
        lambda p: run_pair_daily(nifty.df, bnk.df, s3_signal(p), cost_per_side=0.0005, warmup=20),
    )
    code_hash = hash_code((ROOT / "strategies/s3_dow_dispersion/signal.py").read_text())
    return _log_and_summarise(
        "s3_dow_dispersion", grid, variants, sharpes, n_trades, code_hash,
        f"{nifty.fingerprint}+{bnk.fingerprint}",
    )


def _print_summary(s: dict) -> None:
    v = s["verdict"]
    print(f"\n== {s['name']} ==")
    print(f"  n_variants: {s['n_variants']}")
    print(f"  best params: {s['best_params']}")
    print(f"  best in-sample Sharpe: {s['best_sharpe']:.3f} (n_trades={s['best_n_trades']})")
    print(f"  all variants sharpe: min={s['all_sharpes_summary']['min']:.2f} "
          f"med={s['all_sharpes_summary']['median']:.2f} max={s['all_sharpes_summary']['max']:.2f}")
    print(f"  VERDICT: {v.verdict}")
    if v.dsr is not None:
        print(f"    DSR: {v.dsr.dsr:.3f}  (observed annual Sharpe {v.dsr.sharpe_observed:.2f}, "
              f"E[max under null]={v.dsr.sharpe_expected_max_under_null:.2f})")
    if v.pbo is not None:
        print(f"    PBO: {v.pbo.pbo:.3f}  (in-sample SR mean={v.pbo.in_sample_sr_mean:.2f}, "
              f"oos SR mean={v.pbo.out_sample_sr_mean:.2f})")
    if v.cpcv is not None:
        print(f"    CPCV folds positive: {v.cpcv.folds_positive_ratio:.2f}  "
              f"(mean OOS Sharpe across folds: {v.cpcv.mean_oos_sharpe:.2f})")
    if v.reasons:
        print(f"    reasons: {v.reasons}")


def main() -> None:
    print("Loading data from yfinance (cache: data_cache/)...")
    nifty = load("NIFTY", start=START)
    bnk = load("BANKNIFTY", start=START)
    vix = load("INDIAVIX", start=START)
    for s in (nifty, bnk, vix):
        print(f"  {s.name}: {len(s.df)} bars [{s.df.index[0].date()} .. {s.df.index[-1].date()}]  hash={s.fingerprint}")

    _print_summary(run_s1(nifty))
    _print_summary(run_s2(nifty, vix))
    _print_summary(run_s3(nifty, bnk))


if __name__ == "__main__":
    main()
