"""W7.2 — scrape 6 months of BSE corporate announcements.

Estimated runtime: ~40 min. Estimated output: ~200k rows, ~50MB CSV.
Re-run is idempotent (overwrites the CSV).
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.data.bse_disclosures import fetch_range  # noqa: E402

OUT = ROOT / "data_cache" / "disclosures" / "bse_6mo.csv"


def main() -> None:
    today = date.today()
    start = today - timedelta(days=180)
    print(f"scraping BSE announcements {start} -> {today}")
    print(f"output: {OUT}")
    n = fetch_range(start, today, out_csv=OUT, sleep_s=0.4, window_days=5)
    print(f"\nDONE. wrote {n} rows to {OUT}")
    print(f"  size: {OUT.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
