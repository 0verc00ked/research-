"""Fetch NIFTY MIDCAP 100 constituent list. Stand-alone probe."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.data.nse_midcap import fetch  # noqa: E402


def main():
    stocks = fetch()
    print(f"fetched {len(stocks)} mid-cap stocks")
    for s in stocks[:10]:
        print(f"  {s.symbol:14s} | {s.company_name[:40]:40s} | {s.industry}")
    print(f"  ... ({len(stocks) - 10} more)")


if __name__ == "__main__":
    main()
