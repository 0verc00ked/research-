"""W7.1 probe — verify BSE API endpoint works before doing 6-month scrape."""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import httpx

from agent_trader.data.bse_disclosures import fetch_page, _HEADERS, _BASE


def main():
    # Probe: yesterday only
    yday = date.today() - timedelta(days=1)
    print(f"probing BSE for {yday} ..")
    with httpx.Client() as client:
        rows, meta = fetch_page(client, yday, yday, page=1)
        print(f"  HTTP ok, page 1 rows: {len(rows)}")
        if rows:
            print("  first row keys:", sorted(rows[0].keys()))
            print("  sample row (truncated):")
            for k, v in rows[0].items():
                s = str(v)
                if len(s) > 100:
                    s = s[:100] + "..."
                print(f"    {k}: {s}")
        print("  meta:", json.dumps(meta, indent=2)[:300])


if __name__ == "__main__":
    main()
