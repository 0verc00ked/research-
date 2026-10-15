"""BSE corporate-announcements scraper.

Hits the public `BseIndiaAPI/api/AnnGetData/w` endpoint that BSE's own
announcements page uses. No authentication needed but realistic browser
headers are required or BSE returns 403.

Caveats:
  - Rate-limited. We sleep between page fetches.
  - 'Time' is BSE timestamp string; we parse to UTC.
  - Some announcements have no PDF attachment; we keep them with attachment=None.
  - Schema observed empirically; verify against fresh fetch on schema drift.
"""
from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

_BASE = "https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.5 Safari/605.1.15"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.bseindia.com/",
    "Origin": "https://www.bseindia.com",
    "Connection": "keep-alive",
}


@dataclass
class Announcement:
    scrip_code: str
    scrip_name: str
    headline: str
    news_subject: str   # NEWSSUB — usually more substantive than HEADLINE
    category: str
    subcategory: str
    timestamp_utc: datetime
    attachment_url: str | None
    raw: dict[str, Any]


def _ddmmyyyy(d: date) -> str:
    return d.strftime("%Y%m%d")


def _parse_row(row: dict[str, Any]) -> Announcement | None:
    """Best-effort row parser. BSE schema has been observed to use field names
    like 'SCRIP_CD', 'SLONGNAME', 'HEADLINE', 'NEWS_DT', 'ATTACHMENTNAME',
    'CATEGORYNAME', 'SUBCATNAME'. We tolerate variants."""
    try:
        ts_raw = row.get("NEWS_DT") or row.get("News_submission_dt") or row.get("DT_TM")
        if not ts_raw:
            return None
        # BSE timestamps appear as "2026-05-01T14:32:00" (IST). Convert to UTC.
        ts = datetime.fromisoformat(ts_raw.replace("Z", "").split("+")[0])
        # IST = UTC + 5:30
        ts_utc = ts - timedelta(hours=5, minutes=30)
        attach = row.get("ATTACHMENTNAME") or row.get("ATTACHEDFILE")
        attach_url = f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{attach}" if attach else None
        return Announcement(
            scrip_code=str(row.get("SCRIP_CD", row.get("scripCode", ""))),
            scrip_name=str(row.get("SLONGNAME", row.get("scripName", ""))),
            headline=str(row.get("HEADLINE", row.get("NewsHeadline", ""))),
            news_subject=str(row.get("NEWSSUB", "")),
            category=str(row.get("CATEGORYNAME", row.get("CategoryName", ""))),
            subcategory=str(row.get("SUBCATNAME", row.get("SubCategoryName", "") or row.get("ANNOUNCEMENT_TYPE", ""))),
            timestamp_utc=ts_utc,
            attachment_url=attach_url,
            raw=row,
        )
    except Exception:
        return None


def fetch_page(
    client: httpx.Client,
    from_date: date,
    to_date: date,
    page: int = 1,
    timeout: float = 30.0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    params = {
        "pageno": str(page),
        "strCat": "-1",
        "strPrevDate": _ddmmyyyy(from_date),
        "strScrip": "",
        "strSearch": "P",
        "strToDate": _ddmmyyyy(to_date),
        "strType": "C",
    }
    resp = client.get(_BASE, params=params, headers=_HEADERS, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    table = data.get("Table") or []
    meta = (data.get("Table1") or [{}])[0] if data.get("Table1") else {}
    return table, meta


def fetch_range(
    from_date: date,
    to_date: date,
    *,
    out_csv: Path,
    sleep_s: float = 0.5,
    max_pages_per_window: int = 200,
    window_days: int = 7,
) -> int:
    """Walk the date range in `window_days`-day windows, page through each.

    Writes CSV with one row per announcement. Returns total rows written.
    """
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    fieldnames = [
        "scrip_code", "scrip_name", "headline", "news_subject", "category",
        "subcategory", "timestamp_utc", "attachment_url",
    ]
    with httpx.Client(http2=False) as client, out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        cursor = from_date
        while cursor < to_date:
            window_end = min(cursor + timedelta(days=window_days - 1), to_date)
            page = 1
            window_rows = 0
            while page <= max_pages_per_window:
                try:
                    table, meta = fetch_page(client, cursor, window_end, page=page)
                except (httpx.HTTPError, json.JSONDecodeError) as e:
                    print(f"  WARN {cursor}..{window_end} p{page}: {e}", flush=True)
                    break
                if not table:
                    break
                for row in table:
                    ann = _parse_row(row)
                    if ann is None:
                        continue
                    w.writerow({
                        "scrip_code": ann.scrip_code,
                        "scrip_name": ann.scrip_name,
                        "headline": ann.headline,
                        "news_subject": ann.news_subject,
                        "category": ann.category,
                        "subcategory": ann.subcategory,
                        "timestamp_utc": ann.timestamp_utc.isoformat(),
                        "attachment_url": ann.attachment_url or "",
                    })
                    window_rows += 1
                    written += 1
                page += 1
                time.sleep(sleep_s)
            print(f"  {cursor} .. {window_end}: {window_rows} rows (running total {written})", flush=True)
            cursor = window_end + timedelta(days=1)
    return written
