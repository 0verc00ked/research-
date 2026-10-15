"""W7.5 — category + time-of-day discrimination before bringing the LLM in.

If a free attribute already discriminates (e.g., 'Financial Results' announcements
have 3× the median |move| of 'Postal Ballot' announcements), that's the
baseline the LLM has to BEAT to add value.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REACTIONS = ROOT / "data_cache" / "disclosures" / "reactions.csv"
REPORT = ROOT / "research" / "phase8_disclosure" / "discovery_v2.md"


def main():
    df = pd.read_csv(REACTIONS)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True, format="ISO8601")
    # IST timestamps for time-of-day analysis
    df["ts_ist"] = df["timestamp_utc"].dt.tz_convert("Asia/Kolkata")
    df["hour_ist"] = df["ts_ist"].dt.hour
    df["abs_eod"] = df["ret_eod_next"].abs()

    lines = ["# W7.5 — Free-attribute discrimination analysis\n",
             "Date: 2026-05-21\n",
             f"Sample: {len(df):,} mid-cap disclosures.\n"]

    # ===== Category =====
    cat_stats = (
        df.groupby("category")
        .agg(n=("abs_eod", "size"),
             med_abs=("abs_eod", "median"),
             p75_abs=("abs_eod", lambda s: float(np.nanpercentile(s, 75))),
             p95_abs=("abs_eod", lambda s: float(np.nanpercentile(s, 95))))
        .sort_values("n", ascending=False)
    )
    overall_med = float(df["abs_eod"].median())

    lines.append("## Category discrimination (does category alone separate movers from non-movers?)\n")
    lines.append(f"Overall median |ret_eod_next|: **{overall_med:.4f}**\n")
    lines.append("| category | n | median |ret| | p75 | p95 | vs overall |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for cat, row in cat_stats.head(20).iterrows():
        ratio = row["med_abs"] / overall_med if overall_med else float("nan")
        lines.append(
            f"| {cat[:42]} | {int(row['n'])} | {row['med_abs']:.4f} | "
            f"{row['p75_abs']:.4f} | {row['p95_abs']:.4f} | {ratio:.2f}x |"
        )
    lines.append("")
    top_cat = cat_stats["med_abs"].max() / overall_med
    bot_cat = cat_stats[cat_stats["n"] >= 50]["med_abs"].min() / overall_med
    lines.append(f"**Spread:** top-vs-bottom category ratio (n≥50): "
                 f"{top_cat:.2f}x vs {bot_cat:.2f}x → category alone discriminates by "
                 f"**{top_cat/bot_cat:.2f}x** between extremes.\n")

    # ===== Time of day =====
    lines.append("## Time-of-day (IST)\n")
    hour_stats = (
        df.groupby("hour_ist")
        .agg(n=("abs_eod", "size"), med=("abs_eod", "median"))
    )
    market_hours = hour_stats.loc[9:15]  # 9–15 IST roughly
    after_hours = hour_stats.drop(market_hours.index, errors="ignore")
    lines.append(f"- disclosures during market hours (9–15 IST): "
                 f"**{int(market_hours['n'].sum())}** ({market_hours['n'].sum()/len(df):.0%})")
    lines.append(f"- disclosures after market hours: "
                 f"**{int(after_hours['n'].sum())}** ({after_hours['n'].sum()/len(df):.0%})")
    lines.append("")
    lines.append("| hour IST | n | median |ret| |")
    lines.append("|---:|---:|---:|")
    for h, row in hour_stats.iterrows():
        if row["n"] > 50:
            lines.append(f"| {int(h):02d} | {int(row['n'])} | {row['med']:.4f} |")
    lines.append("")

    # ===== Filter to a "high-signal candidate" subset =====
    # Define: categories with median |ret| > 1.5x overall, n >= 50
    sig_cats = cat_stats[(cat_stats["n"] >= 50) & (cat_stats["med_abs"] > 1.5 * overall_med)]
    lines.append("## Pre-LLM filter: high-signal categories (n≥50, median |ret| > 1.5x overall)\n")
    if len(sig_cats) == 0:
        lines.append("(none — category alone cannot identify high-signal disclosures)\n")
    else:
        lines.append("| category | n | median |ret| | p95 |")
        lines.append("|---|---:|---:|---:|")
        for cat, row in sig_cats.iterrows():
            lines.append(f"| {cat[:42]} | {int(row['n'])} | {row['med_abs']:.4f} | {row['p95_abs']:.4f} |")
        sig_subset = df[df["category"].isin(sig_cats.index)]
        lines.append("")
        lines.append(f"**Subset (free pre-LLM filter):** {len(sig_subset):,} disclosures "
                     f"({len(sig_subset)/len(df):.1%} of sample), median |ret_eod| "
                     f"**{sig_subset['abs_eod'].median():.4f}** "
                     f"(vs overall {overall_med:.4f} = {sig_subset['abs_eod'].median()/overall_med:.2f}x)")
        lines.append("")

    lines.append("## What this means for W8\n")
    lines.append("- If category alone gives a 3x+ separation, the LLM has to beat that to justify itself.")
    lines.append("- If category gives ~1x (no separation), the LLM is the only path to filtering.")
    lines.append("- In the time-of-day breakdown, after-hours disclosures publish during a closed market,")
    lines.append("  so the 'ret_1h' is effectively 'first hour of next session' — much more reaction time")
    lines.append("  for an LLM than the raw number suggests.")

    REPORT.write_text("\n".join(lines))
    print(f"\nReport written: {REPORT}")
    print("\n" + "\n".join(lines))


if __name__ == "__main__":
    main()
