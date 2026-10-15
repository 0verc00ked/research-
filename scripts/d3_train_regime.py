"""D3 — Train HMM regime model on NIFTY+VIX and validate against known events.

Train window: 2010-2024 in-sample.
Test window: 2025-01-01 → present (post-LLM-cutoff window required by harness).

Sanity checks:
  - State persistence (dwell times) > 1 bar
  - High-vol state captures known crash dates (2020-03, 2022-Feb-24, 2023-01-25)
  - Calm state captures known calm periods (2017 H1, 2019 H2)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.data.yfinance_loader import load  # noqa: E402
from agent_trader.regime import RegimeModel, build_features, train  # noqa: E402

REPORT = ROOT / "research" / "phase9_research_engine" / "d3_regime_report.md"
REGIME_CSV = ROOT / "data_cache" / "regime" / "nifty_regime_path.csv"
KNOWN_EVENTS = {
    "covid_2020-03-23": pd.Timestamp("2020-03-23"),
    "russia_war_2022-02-24": pd.Timestamp("2022-02-24"),
    "adani_2023-01-25": pd.Timestamp("2023-01-25"),
    "modi_mandate_2024-06-04": pd.Timestamp("2024-06-04"),
    "calm_2017-06-01": pd.Timestamp("2017-06-01"),
    "calm_2019-08-01": pd.Timestamp("2019-08-01"),
}


def main() -> None:
    print("loading NIFTY + India VIX ...")
    nifty = load("NIFTY", start="2010-01-01")
    vix = load("INDIAVIX", start="2010-01-01")
    feats, idx = build_features(nifty.df["Close"], vix.df["Close"])
    print(f"  feature matrix: {feats.shape}  ({idx[0].date()} .. {idx[-1].date()})")

    is_mask = idx < pd.Timestamp("2025-01-01")
    X_is = feats.iloc[is_mask].to_numpy()
    X_full = feats.to_numpy()
    print(f"  in-sample: {X_is.shape[0]}  oos: {X_full.shape[0] - X_is.shape[0]}")

    model = train(X_is, n_states=3, n_iter=200, random_state=42)
    posterior = model.posterior(X_full)
    path = model.predict_path(X_full)
    dwell = model.dwell_times(path)

    df = pd.DataFrame({
        "state": path,
        "p_state0": posterior[:, 0],
        "p_state1": posterior[:, 1],
        "p_state2": posterior[:, 2],
    }, index=idx)
    REGIME_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(REGIME_CSV)

    # State characterisation (in-sample only — no peeking at OOS)
    is_path = path[is_mask]
    state_returns = {}
    state_rv = {}
    for k in range(3):
        mask = is_path == k
        state_returns[k] = float(feats.iloc[is_mask]["log_ret"].to_numpy()[mask].mean())
        state_rv[k] = float(feats.iloc[is_mask]["rv20"].to_numpy()[mask].mean())
    print("  in-sample state characterisation:")
    for k in range(3):
        print(f"    state {k}: mean log_ret/d = {state_returns[k]:+.4f}, "
              f"mean rv20 = {state_rv[k]:.4f}, dwell = {dwell[k]:.1f} bars")

    # Validate vs known events
    print("\n  state at known events:")
    near_state: dict[str, int] = {}
    for label, date in KNOWN_EVENTS.items():
        if date < idx[0] or date > idx[-1]:
            continue
        nearest_idx = idx.get_indexer([date], method="nearest")[0]
        near_state[label] = int(path[nearest_idx])
        print(f"    {label} → state {near_state[label]}  "
              f"(p={posterior[nearest_idx]})")

    # Write report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D3 — HMM Regime Report",
        f"\nDate: 2026-05-21",
        f"\nTraining window: 2010-01 → 2025-01",
        f"OOS window: 2025-01 → 2026-05  ({X_full.shape[0] - X_is.shape[0]} bars)",
        "\n## State characterisation (in-sample)\n",
        "| state | mean log_ret/d | mean rv20 (ann) | dwell (bars) | interpretation |",
        "|---|---:|---:|---:|---|",
    ]
    interp = {}
    sorted_by_return = sorted(range(3), key=lambda k: state_returns[k])
    interp[sorted_by_return[0]] = "bear / drawdown"
    interp[sorted_by_return[1]] = "range / calm"
    interp[sorted_by_return[2]] = "bull / trend"
    for k in range(3):
        lines.append(f"| {k} | {state_returns[k]:+.4f} | {state_rv[k]:.4f} | "
                     f"{dwell[k]:.1f} | {interp[k]} |")
    lines.append("")
    lines.append("## Known events — sanity check\n")
    lines.append("| event | date | inferred state | interpretation |")
    lines.append("|---|---|---:|---|")
    for label, date in KNOWN_EVENTS.items():
        if label in near_state:
            s = near_state[label]
            lines.append(f"| {label} | {date.date()} | {s} | {interp[s]} |")
    lines.append("")

    # OOS regime distribution
    oos_path = path[~is_mask]
    if len(oos_path) > 0:
        lines.append("## OOS regime distribution (2025-01+)\n")
        counts = pd.Series(oos_path).value_counts().sort_index()
        for k, n in counts.items():
            lines.append(f"- state {k} ({interp[int(k)]}): {n} bars "
                         f"({n/len(oos_path):.1%})")
        lines.append("")

    lines.append("## Output artifact\n")
    lines.append(f"Per-day state + posterior saved to: `{REGIME_CSV.relative_to(ROOT)}`")
    lines.append("This file is consumed by D5 (setup discovery) as a feature.")

    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")


if __name__ == "__main__":
    main()
