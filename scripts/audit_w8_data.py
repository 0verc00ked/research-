"""W7-8 data-quality audit.

Procedure:
  1. For each of the 94 mid-cap tickers used in W7-8, fetch DAILY bars twice
     — once with auto_adjust=False (raw) and once with auto_adjust=True
     (split/bonus/dividend-adjusted).
  2. Identify corporate-action dates as days where the two diverge by >1%
     in close-to-close return.
  3. Cross-reference each W7-8 disclosure reaction against this calendar.
     Flag any disclosure within ±2 trading days of a corp-action date.
  4. Re-compute the W7.4 disclosure-vs-baseline statistics on the *clean*
     subset (no corp-action contamination).
  5. Compare clean vs raw numbers. If clean ratios > raw ratios, the W7-8
     verdict was biased by data quality and needs revisiting.

This is a daily-bar audit, not intraday. yfinance's intraday adjustment is
unreliable, so we use the daily disagreement as the corp-action signal.
"""
from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

REACTIONS = ROOT / "data_cache" / "disclosures" / "reactions.csv"
CORP_ACTIONS_CSV = ROOT / "data_cache" / "audit" / "corp_actions.csv"
CLEAN_REACTIONS = ROOT / "data_cache" / "audit" / "reactions_clean.csv"
REPORT = ROOT / "research" / "phase8_disclosure" / "data_quality_audit.md"

DIVERGENCE_THRESHOLD = 0.01   # 1% close-to-close divergence = likely corp action
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6)",
}


def find_corp_action_dates(ticker: str, start: str, end: str) -> set[pd.Timestamp]:
    """Compare auto_adjust=False vs True at daily resolution; flag days where
    the close-to-close return diverges by > DIVERGENCE_THRESHOLD.
    """
    try:
        raw = yf.download(ticker, start=start, end=end, interval="1d",
                          auto_adjust=False, progress=False)
        adj = yf.download(ticker, start=start, end=end, interval="1d",
                          auto_adjust=True, progress=False)
    except Exception as e:
        print(f"  WARN {ticker}: {e}")
        return set()
    if raw is None or raw.empty or adj is None or adj.empty:
        return set()
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    if isinstance(adj.columns, pd.MultiIndex):
        adj.columns = adj.columns.get_level_values(0)

    common = raw.index.intersection(adj.index)
    raw_c = raw.loc[common, "Close"]
    adj_c = adj.loc[common, "Close"]
    raw_ret = raw_c.pct_change()
    adj_ret = adj_c.pct_change()
    div = (raw_ret - adj_ret).abs()
    dates = set(common[div > DIVERGENCE_THRESHOLD])
    return dates


def main():
    df = pd.read_csv(REACTIONS)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True, format="ISO8601")
    tickers = sorted(df["yf_ticker"].unique())
    print(f"auditing {len(tickers)} tickers ...")

    start = (df["timestamp_utc"].min() - pd.Timedelta(days=10)).date().isoformat()
    end = (df["timestamp_utc"].max() + pd.Timedelta(days=10)).date().isoformat()
    print(f"window: {start} → {end}")

    all_corp_action_rows = []
    ticker_actions: dict[str, set] = {}
    for i, ticker in enumerate(tickers, 1):
        dates = find_corp_action_dates(ticker, start, end)
        ticker_actions[ticker] = dates
        for d in dates:
            all_corp_action_rows.append({"ticker": ticker, "date": d.date().isoformat()})
        if i % 10 == 0:
            print(f"  [{i}/{len(tickers)}] flagged {sum(len(v) for v in ticker_actions.values())} CA dates so far")

    CORP_ACTIONS_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(all_corp_action_rows).to_csv(CORP_ACTIONS_CSV, index=False)
    total_ca = sum(len(v) for v in ticker_actions.values())
    n_tickers_with_ca = sum(1 for v in ticker_actions.values() if v)
    print(f"\ncorp actions: {total_ca} across {n_tickers_with_ca}/{len(tickers)} tickers")

    # Flag disclosures near corp actions
    df["near_corp_action"] = False
    for _, row in df.iterrows():
        ticker = row["yf_ticker"]
        ts_date = row["timestamp_utc"].normalize().tz_localize(None)
        actions = ticker_actions.get(ticker, set())
        for ca in actions:
            ca_naive = ca.tz_localize(None) if ca.tz else ca
            if abs((ts_date - ca_naive).days) <= 2:
                df.loc[row.name, "near_corp_action"] = True
                break

    n_contaminated = int(df["near_corp_action"].sum())
    print(f"\ndisclosures within ±2d of corp actions: {n_contaminated}/{len(df)} "
          f"({n_contaminated/len(df):.1%})")

    clean = df[~df["near_corp_action"]].copy()
    contaminated = df[df["near_corp_action"]].copy()
    clean.to_csv(CLEAN_REACTIONS, index=False)

    # Recompute statistics
    def stats(s: pd.DataFrame) -> dict:
        d = {
            "n": len(s),
            "med_abs_eod": float(s["abs_eod_next"].median()) if len(s) else float("nan"),
            "p75_abs_eod": float(np.nanpercentile(s["abs_eod_next"], 75)) if len(s) else float("nan"),
            "p90_abs_eod": float(np.nanpercentile(s["abs_eod_next"], 90)) if len(s) else float("nan"),
            "p95_abs_eod": float(np.nanpercentile(s["abs_eod_next"], 95)) if len(s) else float("nan"),
            "share_above_0_5pct": float((s["abs_eod_next"] > 0.005).mean()) if len(s) else float("nan"),
        }
        return d

    raw_stats = stats(df)
    clean_stats = stats(clean)
    contam_stats = stats(contaminated)

    # Top movers — which are corp actions?
    top_movers = df.sort_values("abs_eod_next", ascending=False).head(20)
    top_clean = top_movers["near_corp_action"].sum()

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# W7-8 Data Quality Audit",
        f"\nDate: 2026-05-21",
        f"\nAudit window: {start} → {end}",
        f"\nTickers audited: {len(tickers)}",
        f"\nDivergence threshold: |unadj_ret − adj_ret| > {DIVERGENCE_THRESHOLD:.1%} per day → corp action\n",
        "## Corporate-action incidence\n",
        f"- total corp-action days flagged: **{total_ca}**",
        f"- tickers with at least one CA: **{n_tickers_with_ca}/{len(tickers)}**",
        f"- disclosures within ±2d of CA: **{n_contaminated}/{len(df)} ({n_contaminated/len(df):.1%})**",
        "",
        "## Statistics: raw vs clean vs contaminated\n",
        "| metric | RAW (W7-8 original) | CLEAN | CONTAMINATED only |",
        "|---|---:|---:|---:|",
        f"| n | {raw_stats['n']} | {clean_stats['n']} | {contam_stats['n']} |",
        f"| median |ret_eod_next| | {raw_stats['med_abs_eod']:.4f} | "
        f"{clean_stats['med_abs_eod']:.4f} | {contam_stats['med_abs_eod']:.4f} |",
        f"| p75 | {raw_stats['p75_abs_eod']:.4f} | {clean_stats['p75_abs_eod']:.4f} | "
        f"{contam_stats['p75_abs_eod']:.4f} |",
        f"| p90 | {raw_stats['p90_abs_eod']:.4f} | {clean_stats['p90_abs_eod']:.4f} | "
        f"{contam_stats['p90_abs_eod']:.4f} |",
        f"| p95 | {raw_stats['p95_abs_eod']:.4f} | {clean_stats['p95_abs_eod']:.4f} | "
        f"{contam_stats['p95_abs_eod']:.4f} |",
        f"| share with |ret|>0.5% | {raw_stats['share_above_0_5pct']:.1%} | "
        f"{clean_stats['share_above_0_5pct']:.1%} | "
        f"{contam_stats['share_above_0_5pct']:.1%} |",
        "",
        "## Top-20 movers from W7-8 — how many were corp-action contaminated?\n",
        f"- of the top 20 largest |ret_eod_next| disclosures in W7-8, **{top_clean}** were within ±2d of a corp action",
        f"- the remaining {20 - top_clean} were genuine moves",
        "",
        "## Interpretation\n",
    ]

    if clean_stats["med_abs_eod"] < raw_stats["med_abs_eod"] * 0.9:
        lines.append("**The raw W7-8 numbers were inflated by corp-action contamination.** ")
        lines.append("Cleaning shrinks the disclosure-bar magnitude meaningfully. This means our ")
        lines.append("'big move on routine disclosure' pattern was partly fake — actual reactions to ")
        lines.append("real disclosure content are smaller than we measured, making the channel even ")
        lines.append("less viable than the G0d failure suggested.")
    elif top_clean >= 5:
        lines.append(f"**{top_clean}/20 top movers were corp-action artifacts.** The 'movers' stratum ")
        lines.append("in our W8 classification was therefore partially mis-labelled — some 'movers' ")
        lines.append("weren't reacting to disclosures, they were displaying corporate-action distortions. ")
        lines.append("This would have made the LLM look even worse than it actually is at the task. ")
        lines.append("A re-run on clean data might push direction accuracy up modestly but unlikely to ")
        lines.append("change the fundamental verdict.")
    else:
        lines.append("**Corp-action contamination is real but limited (<5/20 top movers affected).** ")
        lines.append("The W7-8 G0d failure cannot be explained away by data quality. The negative ")
        lines.append("finding stands.")

    lines.append("")
    lines.append("## Recommendation\n")
    if clean_stats["med_abs_eod"] != raw_stats["med_abs_eod"]:
        lines.append("- Update the W7.4 discovery report to use the cleaned dataset")
        lines.append("- The G0d gate evaluation should be re-run on the cleaned sample")
        lines.append("- For W8 stratification, re-sample 'movers' from clean data only")
    else:
        lines.append("- No re-run needed; the original W7-8 numbers reflect the underlying signal honestly.")

    REPORT.write_text("\n".join(lines))
    print(f"\nreport: {REPORT}")
    print(f"clean reactions: {CLEAN_REACTIONS}")
    print()
    for l in lines[-15:]:
        print(l)


if __name__ == "__main__":
    main()
