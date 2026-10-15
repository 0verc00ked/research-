"""NIFTY MIDCAP 100 constituent list loader.

niftyindices.com publishes the constituent CSV publicly. We cache it locally
because the URL occasionally requires session cookies on cold fetch.

Mid-cap classification (market-cap ₹2k–20k Cr) is approximated by membership
in NIFTY MIDCAP 100. Exact market-cap from a paid source would be cleaner;
this is good enough for W7-8 research.
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path

import httpx

URL = "https://niftyindices.com/IndexConstituent/ind_niftymidcap100list.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15",
    "Accept": "text/csv,*/*;q=0.9",
    "Referer": "https://www.niftyindices.com/",
}


@dataclass
class MidcapStock:
    symbol: str        # NSE ticker, e.g. "AUROPHARMA"
    company_name: str  # may differ slightly from BSE long name
    industry: str
    series: str
    isin: str

    @property
    def yf_ticker(self) -> str:
        return f"{self.symbol}.NS"


def fetch(cache_dir: str | Path = "data_cache") -> list[MidcapStock]:
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    cache_file = cache / "nifty_midcap100.csv"
    if not cache_file.exists():
        resp = httpx.get(URL, headers=HEADERS, timeout=30.0, follow_redirects=True)
        resp.raise_for_status()
        cache_file.write_bytes(resp.content)
    text = cache_file.read_text(encoding="utf-8-sig", errors="replace")
    rows: list[MidcapStock] = []
    reader = csv.DictReader(io.StringIO(text))
    for r in reader:
        rows.append(
            MidcapStock(
                symbol=(r.get("Symbol") or "").strip(),
                company_name=(r.get("Company Name") or "").strip(),
                industry=(r.get("Industry") or "").strip(),
                series=(r.get("Series") or "").strip(),
                isin=(r.get("ISIN Code") or "").strip(),
            )
        )
    return [r for r in rows if r.symbol]


def aggressive_norm(s: str) -> str:
    """Reduce a company name to alphabetic characters only, uppercased.

    Strips spaces, punctuation, '&', '(India)', 'Ltd' / 'Ltd.' / 'Limited' etc.
    "Persistent Systems Ltd" and "Persistent Systems Ltd." both →
    "PERSISTENTSYSTEMSLTD" — they now collide as intended.
    """
    return "".join(c for c in s.upper() if c.isalpha())


def name_match_index(stocks: list[MidcapStock]) -> dict[str, MidcapStock]:
    """Index by aggressive_norm(company_name) for robust BSE↔NSE matching."""
    return {aggressive_norm(s.company_name): s for s in stocks}
