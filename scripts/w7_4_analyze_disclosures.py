"""W7.4 — discovery analysis #1 + #2.

Critical question #1: Do mid-cap disclosures cluster around larger price
moves than random bars?
Critical question #2: Of disclosures that preceded a big move, what's the
median absorption half-life?

Inputs:
  data_cache/disclosures/bse_6mo.csv  (from W7.2 scrape)
  NIFTY MIDCAP 100 list  (from W7.3 fetcher)

Outputs:
  research/phase8_disclosure/discovery_v1.md
  data_cache/disclosures/midcap_matched.csv
  data_cache/disclosures/reactions.csv
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.data.intraday_prices import (  # noqa: E402
    compute_reaction,
    fetch_intraday_history,
)
from agent_trader.data.nse_midcap import (  # noqa: E402
    aggressive_norm,
    fetch as fetch_midcaps,
    name_match_index,
)

DISCLOSURES_CSV = ROOT / "data_cache" / "disclosures" / "bse_6mo.csv"
MIDCAP_CSV = ROOT / "data_cache" / "disclosures" / "midcap_matched.csv"
REACTIONS_CSV = ROOT / "data_cache" / "disclosures" / "reactions.csv"
REPORT_MD = ROOT / "research" / "phase8_disclosure" / "discovery_v1.md"


def match_midcaps(disc: pd.DataFrame, midcaps: list) -> pd.DataFrame:
    name_idx = name_match_index(midcaps)
    disc = disc.copy()
    disc["bse_norm"] = disc["scrip_name"].astype(str).map(aggressive_norm)
    midcap_lookup = {k: (v.symbol, v.yf_ticker) for k, v in name_idx.items()}
    rows = []
    for _, r in disc.iterrows():
        m = midcap_lookup.get(r["bse_norm"])
        if m:
            rows.append({**r.to_dict(), "nse_symbol": m[0], "yf_ticker": m[1]})
    matched = pd.DataFrame(rows)
    if not matched.empty:
        matched["timestamp_utc"] = pd.to_datetime(
            matched["timestamp_utc"], utc=True, format="ISO8601"
        )
    return matched


def compute_all_reactions(matched: pd.DataFrame) -> pd.DataFrame:
    if matched.empty:
        return pd.DataFrame()
    start = matched["timestamp_utc"].min() - pd.Timedelta(days=3)
    end = matched["timestamp_utc"].max() + pd.Timedelta(days=3)
    out_rows = []
    tickers = sorted(matched["yf_ticker"].unique())
    print(f"  fetching intraday history for {len(tickers)} tickers ...")
    for i, ticker in enumerate(tickers, 1):
        try:
            bars = fetch_intraday_history(
                ticker, start.to_pydatetime(), end.to_pydatetime(), interval="60m"
            )
        except Exception as e:
            print(f"  WARN {ticker}: {e}")
            continue
        if bars.empty:
            continue
        bars.attrs["ticker"] = ticker
        sub = matched[matched["yf_ticker"] == ticker]
        for _, r in sub.iterrows():
            rxn = compute_reaction(bars, r["timestamp_utc"].to_pydatetime())
            if rxn is None:
                continue
            out_rows.append({
                "scrip_name": r["scrip_name"],
                "nse_symbol": r["nse_symbol"],
                "yf_ticker": ticker,
                "timestamp_utc": r["timestamp_utc"].isoformat(),
                "category": r["category"],
                "subcategory": r["subcategory"],
                "news_subject": r["news_subject"],
                "price_at_disclosure": rxn.price_at_disclosure,
                "ret_1h": rxn.ret_1h,
                "ret_2h": rxn.ret_2h,
                "ret_4h": rxn.ret_4h,
                "ret_eod_next": rxn.ret_eod_next,
                "abs_eod_next": rxn.abs_eod_next,
                "n_bars_after": rxn.n_bars_available_after,
            })
        if i % 10 == 0:
            print(f"    [{i}/{len(tickers)}] processed, accumulated rows: {len(out_rows)}")
    return pd.DataFrame(out_rows)


def discovery_summary(reactions: pd.DataFrame, baseline: pd.DataFrame) -> str:
    if reactions.empty:
        return "(no reactions computed)"

    def _q(s: pd.Series, q: float) -> float:
        return float(np.nanpercentile(s.dropna(), q))

    lines = ["# W7.4 — Discovery Analysis v1\n"]
    lines.append(f"Date: 2026-05-21\n")
    lines.append(f"## Sample\n")
    lines.append(f"- mid-cap disclosures with intraday data: **{len(reactions)}**")
    lines.append(f"- unique tickers: {reactions['nse_symbol'].nunique()}")
    lines.append(f"- date range: {reactions['timestamp_utc'].min()} → {reactions['timestamp_utc'].max()}\n")

    lines.append("## Critical question #1 — do disclosures cluster around moves?\n")
    lines.append("### |ret_eod_next| distribution: disclosure bars vs random baseline\n")
    lines.append("| pct | disclosure | random | ratio |")
    lines.append("|-----|-----------:|-------:|------:|")
    for q in (50, 75, 90, 95, 99):
        d = _q(reactions["abs_eod_next"], q)
        b = _q(baseline["abs_eod_next"], q) if not baseline.empty else float("nan")
        ratio = d / b if b and np.isfinite(b) else float("nan")
        lines.append(f"| p{q} | {d:.4f} | {b:.4f} | {ratio:.2f}x |")
    lines.append("")

    lines.append("### |ret_1h| distribution: disclosure bar vs baseline\n")
    lines.append("| pct | disclosure | random | ratio |")
    lines.append("|-----|-----------:|-------:|------:|")
    for q in (50, 75, 90, 95, 99):
        d = _q(reactions["ret_1h"].abs(), q)
        b = _q(baseline["ret_1h"].abs(), q) if not baseline.empty else float("nan")
        ratio = d / b if b and np.isfinite(b) else float("nan")
        lines.append(f"| p{q} | {d:.4f} | {b:.4f} | {ratio:.2f}x |")
    lines.append("")

    lines.append("**Interpretation:** ratios well above 1.0 mean disclosures cluster around bigger moves than random bars — signal exists. Ratios near 1.0 mean disclosures look like any other bar — channel is likely dead.\n")

    lines.append("## Critical question #2 — absorption half-life (only on disclosures with |ret_eod_next| > 0.5%)\n")
    sig = reactions[reactions["abs_eod_next"] > 0.005].copy()
    lines.append(f"- materially-reacted disclosures: **{len(sig)}** ({len(sig)/max(len(reactions),1):.1%} of total)")
    if len(sig) > 0:
        # Fraction of total EOD move realised at 1h / 2h / 4h
        sig["frac_1h"] = (sig["ret_1h"] / sig["ret_eod_next"]).clip(lower=-2, upper=2)
        sig["frac_2h"] = (sig["ret_2h"] / sig["ret_eod_next"]).clip(lower=-2, upper=2)
        sig["frac_4h"] = (sig["ret_4h"] / sig["ret_eod_next"]).clip(lower=-2, upper=2)
        lines.append(f"- median fraction of EOD move realised at +1h: **{sig['frac_1h'].median():.2f}**")
        lines.append(f"- median fraction of EOD move realised at +2h: **{sig['frac_2h'].median():.2f}**")
        lines.append(f"- median fraction of EOD move realised at +4h: **{sig['frac_4h'].median():.2f}**")
        lines.append("")
        lines.append("**Interpretation:** if median frac_1h is already > 0.7, half the move is in <1h — too fast for LLM analysis to be useful. If frac_1h < 0.5 and frac_4h > 0.7, the absorption window is in the LLM strike zone.\n")
    return "\n".join(lines)


def main() -> None:
    if not DISCLOSURES_CSV.exists():
        print(f"ERROR: {DISCLOSURES_CSV} not found. Run scripts/w7_2_scrape_bse.py first.")
        return

    print(f"loading disclosures from {DISCLOSURES_CSV}")
    disc = pd.read_csv(DISCLOSURES_CSV)
    print(f"  {len(disc):,} disclosures loaded")

    print("fetching NIFTY MIDCAP 100 list ...")
    midcaps = fetch_midcaps()

    print("matching disclosures to mid-cap names ...")
    matched = match_midcaps(disc, midcaps)
    print(f"  {len(matched):,} matched to mid-cap tickers")
    matched.to_csv(MIDCAP_CSV, index=False)

    if matched.empty:
        print("no matches; aborting")
        return

    print("computing per-disclosure price reactions ...")
    reactions = compute_all_reactions(matched)
    print(f"  {len(reactions):,} reactions computed")
    reactions.to_csv(REACTIONS_CSV, index=False)

    # Baseline: random bars on the same tickers (for clustering test)
    print("building random-baseline distribution ...")
    baseline = _build_baseline(matched)

    report = discovery_summary(reactions, baseline)
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(report)
    print(f"\nReport written: {REPORT_MD}")
    print(report)


def _build_baseline(matched: pd.DataFrame, samples_per_ticker: int = 100) -> pd.DataFrame:
    """For each ticker, sample random non-disclosure bars to compute baseline
    move distribution. Useful as the null for the clustering test."""
    if matched.empty:
        return pd.DataFrame()
    start = matched["timestamp_utc"].min() - pd.Timedelta(days=3)
    end = matched["timestamp_utc"].max() + pd.Timedelta(days=3)
    rng = np.random.default_rng(0)
    out_rows: list[dict] = []
    for ticker in sorted(matched["yf_ticker"].unique()):
        try:
            bars = fetch_intraday_history(ticker, start.to_pydatetime(), end.to_pydatetime(), interval="60m")
        except Exception:
            continue
        if bars.empty or len(bars) < 20:
            continue
        bars.attrs["ticker"] = ticker
        idxs = rng.choice(len(bars) - 8, size=min(samples_per_ticker, len(bars) - 8), replace=False)
        for i in idxs:
            ts = bars.index[i].to_pydatetime()
            rxn = compute_reaction(bars, ts)
            if rxn is None:
                continue
            out_rows.append({
                "yf_ticker": ticker,
                "timestamp_utc": ts.isoformat(),
                "ret_1h": rxn.ret_1h,
                "ret_2h": rxn.ret_2h,
                "ret_4h": rxn.ret_4h,
                "ret_eod_next": rxn.ret_eod_next,
                "abs_eod_next": rxn.abs_eod_next,
            })
    return pd.DataFrame(out_rows)


if __name__ == "__main__":
    main()
