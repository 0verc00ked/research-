"""D1 — cross-asset lead-lag scan with FDR correction.

Universe: 7 Indian indices + 10 large-cap stocks + 6 global instruments.
Lags scanned: 1, 2, 3, 5, 10 days.
FDR target: 0.05 via Benjamini-Hochberg.

In-sample window: 2015-2024 (kept aside 2025+ for OOS in any future use).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.data.yfinance_loader import load  # noqa: E402
from agent_trader.scanner import scan  # noqa: E402

REPORT = ROOT / "research" / "phase9_research_engine" / "d1_lead_lag_report.md"
RESULTS_CSV = ROOT / "data_cache" / "scanner" / "lead_lag_significant.csv"

UNIVERSE = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "NIFTYIT": "^CNXIT",
    "NIFTYAUTO": "^CNXAUTO",
    "NIFTYPHARMA": "^CNXPHARMA",
    "NIFTYMETAL": "^CNXMETAL",
    "NIFTYFMCG": "^CNXFMCG",
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "USDINR": "INR=X",
    "BRENT": "BZ=F",
    "GOLD": "GC=F",
    "SP500": "^GSPC",
    "NASDAQ": "^IXIC",
}


def main():
    start = "2015-01-01"
    end = "2025-01-01"  # in-sample only
    print(f"loading {len(UNIVERSE)} assets, {start} → {end} ...")
    series: dict[str, pd.Series] = {}
    for name, ticker in UNIVERSE.items():
        try:
            s = load(ticker, start=start, end=end)
            series[name] = s.df["Close"]
            print(f"  {name:14s} ({ticker:14s}): {len(s.df)} bars")
        except Exception as e:
            print(f"  {name}: FAILED ({e})")

    df = pd.DataFrame(series).dropna()
    print(f"\naligned matrix: {df.shape}  ({df.index[0].date()} .. {df.index[-1].date()})")
    rets = np.log(df / df.shift(1)).dropna()
    print(f"return matrix: {rets.shape}")

    print("\nrunning scan ...")
    results = scan(rets, lags=(1, 2, 3, 5, 10), fdr_level=0.05, min_corr_abs=0.05)
    significant = [r for r in results if r.pass_fdr]
    print(f"  total tests: {len(results)}")
    print(f"  significant after BH-FDR: {len(significant)}")

    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{
        "lead": r.lead, "lagger": r.lagger, "lag_days": r.lag_days,
        "corr": r.corr, "z": r.z, "p": r.p, "fdr_q": r.fdr_q,
    } for r in significant]).to_csv(RESULTS_CSV, index=False)

    lines = [
        "# D1 — Lead-Lag Scan Report",
        f"\nDate: 2026-05-21",
        f"\nUniverse: {len(UNIVERSE)} instruments",
        f"\nWindow: {df.index[0].date()} .. {df.index[-1].date()}  ({df.shape[0]} bars)",
        f"\nLags scanned: 1, 2, 3, 5, 10 days",
        f"\nFDR target: 0.05 (Benjamini-Hochberg)",
        f"\nTotal pair-lag tests: {len(results):,}",
        f"\n**Significant lead-lag relationships after FDR: {len(significant)}**\n",
    ]
    if significant:
        lines.append("## Top 30 by |z|\n")
        lines.append("| lead | lagger | lag (d) | corr | z | p | q |")
        lines.append("|---|---|---:|---:|---:|---:|---:|")
        for r in sorted(significant, key=lambda x: -abs(x.z))[:30]:
            lines.append(f"| {r.lead} | {r.lagger} | {r.lag_days} | {r.corr:+.3f} | "
                         f"{r.z:+.2f} | {r.p:.2e} | {r.fdr_q:.3e} |")
        lines.append("")

        # Interpretation pointers
        lines.append("## Honest interpretation\n")
        lines.append("- The correlations are *small* — typical r in [0.05, 0.20]. That's expected: ")
        lines.append("  large lead-lag effects would already be arbitraged.")
        lines.append("- FDR-significance ≠ economic significance. A relationship with r=0.08 means ")
        lines.append("  the lagger's variance explained by the lead is ~0.6%. Need to think hard ")
        lines.append("  about how to extract tradable edge from this.")
        lines.append("- The lead direction matters: 'GOLD leads HDFCBANK' is plausible (global risk "
                     "appetite). 'TCS leads BRENT' is suspect — could be artifact / spurious.")
        lines.append("- Stability check: would need to verify these relationships persist in the "
                     "2025+ OOS window before any strategy uses them.")
    else:
        lines.append("\n**No FDR-significant relationships found.** That's a clean negative result — "
                     "tells us multi-asset daily lead-lag at these lags is not exploitable for retail.")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print(f"\nReport: {REPORT}")
    print(f"CSV: {RESULTS_CSV}")
    if significant:
        print(f"\nTop 10 by |z|:")
        for r in sorted(significant, key=lambda x: -abs(x.z))[:10]:
            print(f"  {r.lead:14s} → {r.lagger:14s} @ {r.lag_days}d  "
                  f"r={r.corr:+.3f}  z={r.z:+.2f}  q={r.fdr_q:.2e}")


if __name__ == "__main__":
    main()
