"""D5 — Bayesian/conjunctive setup discovery on NIFTY using D3 regime + D1
lead-lag features + classical features.

Methodology:
  Train (2015-2022): discover all conjunctions of ≤3 conditions with
                     mean forward return significantly ≠ 0 after BH-FDR
  Val   (2022-2024): re-test surviving setups; setups that *also* clear val
                     advance
  OOS   (2024+):     final unbiased test on setups that survived train+val

Forward return: 5-day log return on NIFTY (^NSEI).
N_trials is reported honestly so DSR is honestly computed downstream.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.data.yfinance_loader import load  # noqa: E402
from agent_trader.setups import search, split_train_val_test  # noqa: E402

REPORT = ROOT / "research" / "phase9_research_engine" / "d5_setups_report.md"
SETUPS_CSV = ROOT / "data_cache" / "setups" / "surviving_setups.csv"


def build_feature_matrix(start: str = "2015-01-01") -> tuple[pd.DataFrame, pd.Series]:
    nifty = load("NIFTY", start=start)
    vix = load("INDIAVIX", start=start)
    usdinr = load("INR=X", start=start)
    gold = load("GC=F", start=start)
    brent = load("BZ=F", start=start)

    # Align on common dates. US indices (SP500/NASDAQ) intentionally excluded:
    # D1 confirmed their lead is priced in at NIFTY pre-open auction, so
    # retail can't trade them post-9:15 open. Including them would inflate
    # in-sample edge that isn't realisable.
    df = pd.DataFrame({
        "nifty": nifty.df["Close"],
        "vix": vix.df["Close"],
        "usdinr": usdinr.df["Close"],
        "gold": gold.df["Close"],
        "brent": brent.df["Close"],
    }).dropna()

    ret = np.log(df / df.shift(1))

    # Load D3 regime
    regime_path = ROOT / "data_cache" / "regime" / "nifty_regime_path.csv"
    if not regime_path.exists():
        raise FileNotFoundError("run scripts/d3_train_regime.py first")
    regime = pd.read_csv(regime_path, index_col=0, parse_dates=True)
    regime.index = regime.index.tz_localize(None)
    df.index = df.index.tz_localize(None)
    ret.index = ret.index.tz_localize(None)

    # Compute features
    f = pd.DataFrame(index=df.index)
    # D3 regime indicators (state 0=bear, 1=range, 2=bull per train report)
    regime_aligned = regime.reindex(df.index, method="ffill")
    f["regime_bear"] = (regime_aligned["state"] == 0)
    f["regime_calm"] = (regime_aligned["state"] == 2)
    # Currency / commodity (retail-tradable; not pre-priced like US overnight)
    f["usdinr_up_yday"] = ret["usdinr"].shift(1) > 0.003
    f["usdinr_down_yday"] = ret["usdinr"].shift(1) < -0.003
    f["brent_up_yday"] = ret["brent"].shift(1) > 0.01
    f["gold_up_yday"] = ret["gold"].shift(1) > 0.005
    # Classical
    f["nifty_5d_neg"] = ret["nifty"].rolling(5).sum().shift(1) < -0.02
    f["nifty_5d_pos"] = ret["nifty"].rolling(5).sum().shift(1) > 0.02
    f["nifty_20d_neg"] = ret["nifty"].rolling(20).sum().shift(1) < 0
    f["vix_p80"] = df["vix"].shift(1) > df["vix"].rolling(252).quantile(0.80).shift(1)
    f["vix_p20"] = df["vix"].shift(1) < df["vix"].rolling(252).quantile(0.20).shift(1)
    # Calendar
    f["monday"] = df.index.dayofweek == 0
    f["friday"] = df.index.dayofweek == 4

    # Forward 5-day return on NIFTY
    fwd5 = ret["nifty"].rolling(5).sum().shift(-5)

    aligned = pd.concat([f, fwd5.rename("fwd5")], axis=1).dropna()
    feats = aligned[f.columns].astype(bool)
    label = aligned["fwd5"]
    return feats, label


def main():
    print("building feature matrix ...")
    feats, label = build_feature_matrix()
    print(f"  features: {feats.shape}  ({feats.index[0].date()} → {feats.index[-1].date()})")
    print(f"  features cols: {list(feats.columns)}")

    (X_tr, y_tr), (X_val, y_val), (X_te, y_te) = split_train_val_test(
        feats, label, train_end="2022-01-01", val_end="2024-01-01"
    )
    print(f"  train: {len(X_tr)}  val: {len(X_val)}  test: {len(X_te)}")

    print("\nstage 1 — search on train ...")
    train_results, total_trials = search(
        X_tr, y_tr, max_order=3, min_n=50, fdr_level=0.05
    )
    train_survivors = [r for r in train_results if r.pass_fdr]
    print(f"  total trials: {total_trials:,}")
    print(f"  train survivors (BH-FDR): {len(train_survivors)}")

    if not train_survivors:
        print("\n** no setups survived train stage **")
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(
            "# D5 — Setup Discovery Report\n\n"
            f"N_trials (honest): {total_trials:,}\n"
            f"Train survivors: 0 — no conjunctive setups significant on 2015-2022 NIFTY.\n"
            "Conclusion: NIFTY 5-day forward return is not predictable by these binary feature conjunctions.\n"
        )
        return

    # stage 2: validate on 2022-2024
    print("\nstage 2 — re-test survivors on val ...")
    val_pass = []
    for setup in train_survivors:
        cols = list(setup.conditions)
        mask = X_val[cols].all(axis=1)
        n = int(mask.sum())
        if n < 20:
            continue
        sub = y_val[mask]
        mean = float(sub.mean())
        std = float(sub.std(ddof=1))
        if std <= 0:
            continue
        import math
        t = mean / (std / math.sqrt(n))
        same_sign = np.sign(mean) == np.sign(setup.mean_ret)
        if same_sign and abs(t) >= 1.0:
            val_pass.append((setup, n, mean, t))
    print(f"  val survivors: {len(val_pass)}")

    # stage 3: final OOS test
    print("\nstage 3 — final OOS test on 2024+ ...")
    test_pass = []
    for (setup, vn, vm, vt) in val_pass:
        cols = list(setup.conditions)
        mask = X_te[cols].all(axis=1)
        n = int(mask.sum())
        if n < 10:
            continue
        sub = y_te[mask]
        mean = float(sub.mean())
        std = float(sub.std(ddof=1))
        if std <= 0:
            continue
        import math
        t = mean / (std / math.sqrt(n))
        same_sign = np.sign(mean) == np.sign(setup.mean_ret)
        test_pass.append((setup, vn, vm, vt, n, mean, t, same_sign))

    # write report
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    SETUPS_CSV.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# D5 — Setup Discovery Report\n",
        f"Date: 2026-05-21\n",
        f"Universe: NIFTY 5-day forward return\n",
        f"N_trials (honest, across orders 1-3): **{total_trials:,}**\n",
        f"Train window: 2015 → 2022 ({len(X_tr)} bars)",
        f"Val window:   2022 → 2024 ({len(X_val)} bars)",
        f"Test window:  2024 → 2026 ({len(X_te)} bars) ← required post-cutoff OOS\n",
        "## Survivor count per stage\n",
        f"| stage | criterion | survivors |",
        f"|---|---|---:|",
        f"| 1 train (BH-FDR @ 0.05) | p_corrected ≤ 0.05 | {len(train_survivors)} |",
        f"| 2 val | same sign & |t|≥1.0 | {len(val_pass)} |",
        f"| 3 OOS | same sign (best-effort) | {sum(1 for x in test_pass if x[-1])} |",
        "",
    ]

    if test_pass:
        lines.append("## Setups surviving train + val + OOS sign-consistency\n")
        lines.append("| setup | train mean_ret | val n / mean / t | OOS n / mean / t / sign |")
        lines.append("|---|---:|---|---|")
        for (s, vn, vm, vt, tn, tm, tt, same) in sorted(test_pass, key=lambda x: -x[3]):
            sign = "✓" if same else "✗"
            lines.append(
                f"| {s.name} | {s.mean_ret:+.4f} | {vn} / {vm:+.4f} / {vt:+.2f} | "
                f"{tn} / {tm:+.4f} / {tt:+.2f} / {sign} |"
            )
        # Persist
        pd.DataFrame([{
            "conditions": s.name,
            "train_mean": s.mean_ret, "train_n": s.n, "train_t": s.t_stat,
            "val_mean": vm, "val_n": vn, "val_t": vt,
            "oos_mean": tm, "oos_n": tn, "oos_t": tt, "oos_same_sign": same,
        } for (s, vn, vm, vt, tn, tm, tt, same) in test_pass]).to_csv(SETUPS_CSV, index=False)

    lines.append("\n## Honest read\n")
    final = [x for x in test_pass if x[-1]]
    if not final:
        lines.append("**No setups cleared all three gates.** This is the most likely outcome given the base rate. ")
        lines.append("The conjunction space was exhaustively searched with honest N_trials accounting. Nothing survives.")
        lines.append("\nNext: feed the surviving train+val candidates (if any) through the validation harness ")
        lines.append("with full DSR/PBO/CPCV, treating N_trials = " + f"{total_trials:,}. With that many trials, ")
        lines.append("DSR will require extraordinary Sharpe to pass — likely none will.")
    else:
        lines.append(f"**{len(final)} setups cleared all three stages including OOS sign consistency.**\n")
        lines.append("These are *candidates* — they still need to pass the full harness (PBO, DSR with ")
        lines.append(f"N_trials={total_trials:,}, CPCV). If any survive that, they advance to W11-12 paper trade.\n")
        lines.append("**Honest caveat:** small OOS sample. Sign consistency on n<30 is weak evidence.")

    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")
    if test_pass:
        print(f"\nTop OOS-surviving candidates:")
        for (s, vn, vm, vt, tn, tm, tt, same) in sorted([x for x in test_pass if x[-1]], key=lambda x: -x[3])[:10]:
            print(f"  {s.name}")
            print(f"    train mean={s.mean_ret:+.4f}  val n={vn} mean={vm:+.4f} t={vt:+.2f}  "
                  f"OOS n={tn} mean={tm:+.4f} t={tt:+.2f}")


if __name__ == "__main__":
    main()
