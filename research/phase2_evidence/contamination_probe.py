"""
V-9 contamination probe scaffold for the LLM analyst.

Status: PROMPTS + SCORING ONLY. No network calls. Plug in your own model client.

Usage sketch (after you pick a model and add a client):

    from contamination_probe import (
        build_probe_a_prompts, build_probe_b_prompts, build_probe_c_prompts,
        score_probe_a, score_probe_b, score_probe_c, combined_gate,
    )
    client = YourClient(model="claude-haiku-4-5-20251015")
    a = run(build_probe_a_prompts(), client)
    b = run(build_probe_b_prompts(), client)
    c = run(build_probe_c_prompts(), client)
    verdict = combined_gate(score_probe_a(a), score_probe_b(b), score_probe_c(c))

Reference: Gao, Jiang, Yan, "A Test of Lookahead Bias in LLM Forecasts", arXiv:2512.23847.
Methodology adapted; thresholds set by this project.
"""
from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass, asdict, field
from typing import Callable, Iterable


# -------------------------------------------------------------------- A: events

# Each entry: (ticker, event_date, kind, realized_5d_sign, realized_20d_sign, notes)
# `realized_*_sign` is +1/-1/0; fill in from official close data when you wire this up.
PROBE_A_EVENTS = [
    ("ADANIENT",  "2023-01-20", "sharp_move", -1, -1, "Hindenburg report Jan 24"),
    ("ADANIPORTS","2023-01-30", "sharp_move", -1, -1, "Adani group follow-on collapse"),
    ("PAYTM",     "2024-01-29", "sharp_move", -1, -1, "RBI ban on PPB Jan 31"),
    ("ZEEL",      "2024-01-19", "sharp_move", -1, -1, "Sony merger called off Jan 22"),
    ("YESBANK",   "2020-03-02", "sharp_move", -1,  0, "RBI moratorium Mar 5"),
    ("IRFC",      "2024-01-08", "sharp_move",  1,  1, "Budget-led pop"),
    ("RELIANCE",  "2024-10-21", "sharp_move",  1,  1, "1:1 bonus Oct 28"),
    ("VEDL",      "2023-09-25", "sharp_move", -1,  0, "demerger plan"),
    ("SUZLON",    "2023-11-12", "sharp_move",  1,  1, "QIP placement"),
    ("IDEA",      "2024-04-15", "sharp_move",  1,  0, "FPO sub close"),
    # Earnings (fill realized signs from actual data later)
    ("TCS",       "2024-04-09", "earnings", None, None, "Q4FY24"),
    ("INFY",      "2024-04-15", "earnings", None, None, "Q4FY24"),
    ("HDFCBANK",  "2024-04-17", "earnings", None, None, "Q4FY24"),
    ("RELIANCE",  "2024-04-19", "earnings", None, None, "Q4FY24"),
    ("ICICIBANK", "2024-04-23", "earnings", None, None, "Q4FY24"),
    ("MARUTI",    "2024-04-26", "earnings", None, None, "Q4FY24"),
    ("LT",        "2024-05-08", "earnings", None, None, "Q4FY24"),
    ("ITC",       "2024-05-23", "earnings", None, None, "Q4FY24"),
    ("BAJFINANCE","2024-04-25", "earnings", None, None, "Q4FY24"),
    ("ASIANPAINT","2024-05-09", "earnings", None, None, "Q4FY24"),
    # Uneventful controls (no >5% move in next 20d) — to be confirmed
    ("HINDUNILVR","2023-08-14", "uneventful", 0, 0, ""),
    ("NESTLEIND", "2023-07-10", "uneventful", 0, 0, ""),
    ("BRITANNIA", "2023-06-12", "uneventful", 0, 0, ""),
    ("DABUR",     "2023-09-04", "uneventful", 0, 0, ""),
    ("MARICO",    "2023-10-09", "uneventful", 0, 0, ""),
    ("PIDILITIND","2023-11-06", "uneventful", 0, 0, ""),
    ("BERGEPAINT","2023-12-04", "uneventful", 0, 0, ""),
    ("COLPAL",    "2024-01-08", "uneventful", 0, 0, ""),
    ("GODREJCP",  "2024-02-05", "uneventful", 0, 0, ""),
    ("TATACONSUM","2024-03-04", "uneventful", 0, 0, ""),
]


def _shift_business_days(date_str: str, days: int) -> str:
    """Naive ±N day shift for null baseline. Replace with NSE-calendar-aware shift later."""
    import datetime as dt
    d = dt.date.fromisoformat(date_str) + dt.timedelta(days=days)
    while d.weekday() >= 5:  # skip Sat/Sun, ignores Indian holidays
        d += dt.timedelta(days=1)
    return d.isoformat()


PROBE_A_TEMPLATE = """Assume today is {date}. You know only what was publicly available on or before this date.

The stock {ticker} (NSE) has been on your radar.

Without inventing facts you cannot verify from your training data:
1. Estimate the probability that {ticker}'s close 5 trading days from now is higher than today's close. State as a number in [0,1].
2. Estimate the probability that {ticker}'s close 20 trading days from now is higher than today's close. State as a number in [0,1].
3. List up to two specific catalysts you anticipate in the next 20 trading days. If none, say "none".
4. State your confidence in your answers as low/medium/high.

Reply ONLY in JSON:
{{
  "p_up_5d": <float>,
  "p_up_20d": <float>,
  "catalysts": [<string>, ...],
  "confidence": "<low|medium|high>"
}}
"""


@dataclass
class ProbePrompt:
    probe: str               # "A", "B", "C"
    case_id: str             # event index or ticker
    arm: str                 # "event", "null", "pre", "post", "neutral_t={i}", etc.
    prompt: str
    meta: dict = field(default_factory=dict)


def build_probe_a_prompts() -> list[ProbePrompt]:
    """For each event: one 'event' arm at D-5, one 'null' arm at D-95 (same ticker)."""
    out = []
    for i, (tk, date, kind, r5, r20, note) in enumerate(PROBE_A_EVENTS):
        d_event = _shift_business_days(date, -5)
        d_null  = _shift_business_days(date, -95)
        out.append(ProbePrompt(
            "A", f"a{i:02d}", "event",
            PROBE_A_TEMPLATE.format(ticker=tk, date=d_event),
            {"ticker": tk, "event_date": date, "kind": kind,
             "realized_5d": r5, "realized_20d": r20, "note": note},
        ))
        out.append(ProbePrompt(
            "A", f"a{i:02d}", "null",
            PROBE_A_TEMPLATE.format(ticker=tk, date=d_null),
            {"ticker": tk, "event_date": date, "kind": kind,
             "realized_5d": r5, "realized_20d": r20, "note": note},
        ))
    return out


# -------------------------------------------------------------------- B: events

PROBE_B_EVENTS = [
    # ticker, event_date, pre_date, post_date, pre_price, post_price, event_kw_regex
    ("ADANIENT",  "2023-01-24", "2023-01-23", "2023-02-10", 3442, 1404,
     r"(hindenburg|short[- ]?seller|governance|fraud allegations)"),
    ("ADANIPORTS","2023-02-02", "2023-01-30", "2023-02-15", 760,  395,
     r"(adani|hindenburg|group sell[- ]?off)"),
    ("RELIANCE",  "2024-10-28", "2024-10-21", "2024-11-04", 2750, 1330,
     r"(bonus|1:1|split)"),
    ("PAYTM",     "2024-02-01", "2024-01-29", "2024-02-15", 761,  342,
     r"(rbi|payments bank|ppbl ban|kyc)"),
    ("ZEEL",      "2024-01-22", "2024-01-19", "2024-02-05", 261,  160,
     r"(sony|merger (called off|collapse))"),
    ("YESBANK",   "2020-03-05", "2020-03-02", "2020-03-12", 36.85, 21.25,
     r"(moratorium|reconstruction|rbi takeover)"),
    ("NIFTY",     "2020-03-23", "2020-03-19", "2020-04-09", 8263, 8748,
     r"(covid|pandemic|lockdown)"),
    ("NIFTY",     "2024-06-04", "2024-06-03", "2024-06-10", 23264,22530,
     r"(election|exit poll|verdict|coalition)"),
]


PROBE_B_TEMPLATE = """Assume today is {date}. The Indian listed entity {ticker} last traded near ₹{price}.

Give a one-paragraph (3-5 sentences) outlook for the next 5 trading days, based ONLY on what was publicly known on or before this date.

Then provide a sentiment score in [-1.0 (very bearish), +1.0 (very bullish)] for the same 5-day window.

Reply ONLY in JSON:
{{
  "outlook": "<string>",
  "sentiment": <float>
}}
"""


def build_probe_b_prompts() -> list[ProbePrompt]:
    out = []
    for i, (tk, ed, pre_d, post_d, pre_p, post_p, kw) in enumerate(PROBE_B_EVENTS):
        out.append(ProbePrompt(
            "B", f"b{i:02d}", "pre",
            PROBE_B_TEMPLATE.format(ticker=tk, date=pre_d, price=pre_p),
            {"event": ed, "kw_regex": kw},
        ))
        out.append(ProbePrompt(
            "B", f"b{i:02d}", "post",
            PROBE_B_TEMPLATE.format(ticker=tk, date=post_d, price=post_p),
            {"event": ed, "kw_regex": kw},
        ))
    return out


# -------------------------------------------------------------------- C: tickers

PROBE_C_TICKERS = {
    "narrative_loaded": ["ADANIENT","ADANIGREEN","YESBANK","PAYTM","ZEEL","VEDL","RELIANCE",
                         "IRFC","SUZLON","IDEA"],
    "neutral":           ["TCS","INFY","HDFCBANK","ITC","ASIANPAINT"],
}

PROBE_C_TEMPLATE = """Give a one-paragraph (3-5 sentence) 12-month outlook on the Indian listed stock {ticker}.
Then provide a numerical bull/bear score from -1.0 (very bearish) to +1.0 (very bullish).

Reply ONLY in JSON:
{{
  "outlook": "<string>",
  "score": <float>
}}
"""

PROBE_C_SAMPLES_PER_TICKER = 20  # at temperature 0.7


def build_probe_c_prompts() -> list[ProbePrompt]:
    out = []
    for bucket, tks in PROBE_C_TICKERS.items():
        for tk in tks:
            for s in range(PROBE_C_SAMPLES_PER_TICKER):
                out.append(ProbePrompt(
                    "C", f"c_{tk}_{s:02d}", bucket,
                    PROBE_C_TEMPLATE.format(ticker=tk),
                    {"ticker": tk, "bucket": bucket, "sample": s},
                ))
    return out


# ----------------------------------------------------- scoring helpers


def _safe_json(text: str) -> dict | None:
    try:
        return json.loads(text)
    except Exception:
        # tolerant: find first { ... } block
        i, j = text.find("{"), text.rfind("}")
        if i >= 0 and j > i:
            try:
                return json.loads(text[i:j+1])
            except Exception:
                return None
        return None


def _binomial_p(k: int, n: int, p0: float = 0.5) -> float:
    """Two-sided binomial p-value vs p0. Tiny implementation, no scipy."""
    if n == 0:
        return 1.0
    def C(n, k):
        return math.comb(n, k)
    def pmf(i):
        return C(n, i) * (p0 ** i) * ((1 - p0) ** (n - i))
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n + 1) if pmf(i) <= obs + 1e-12))


def score_probe_a(responses: list[dict]) -> dict:
    """
    responses: list of {"prompt": ProbePrompt, "raw": str_from_model}
    Compute hit rate of model's p_up_5d > 0.5 prediction vs realized_5d sign,
    on EVENT arm vs NULL arm. Returns dict with hit rates, spread, p-value.
    """
    event_hits, event_n = 0, 0
    null_hits, null_n = 0, 0
    for r in responses:
        p = r["prompt"]
        m = _safe_json(r["raw"]) or {}
        prob = m.get("p_up_5d")
        if prob is None:
            continue
        pred_up = prob > 0.5
        realized = p.meta.get("realized_5d")
        if realized is None or realized == 0:
            continue
        hit = (pred_up and realized > 0) or ((not pred_up) and realized < 0)
        if p.arm == "event":
            event_n += 1
            event_hits += int(hit)
        elif p.arm == "null":
            null_n += 1
            null_hits += int(hit)
    er = event_hits / event_n if event_n else float("nan")
    nr = null_hits  / null_n  if null_n  else float("nan")
    spread = er - nr if event_n and null_n else float("nan")
    # McNemar-ish proxy: binomial on event hits vs null base rate
    p_value = _binomial_p(event_hits, event_n, p0=max(0.05, min(0.95, nr or 0.5))) if event_n else 1.0
    if not (spread == spread):  # NaN
        verdict = "insufficient_data"
    elif spread <= 0.05 and p_value > 0.05:
        verdict = "clean"
    elif spread > 0.15 or p_value < 0.01:
        verdict = "disqualified"
    else:
        verdict = "mild"
    return {"event_n": event_n, "event_hit_rate": er, "null_hit_rate": nr,
            "spread": spread, "p_value": p_value, "verdict": verdict}


def score_probe_b(responses: list[dict]) -> dict:
    """
    Compute event-mention rate (regex on outlook) and sentiment skew between pre/post pairs.
    """
    import re
    mention = 0
    total = 0
    per_event = {}
    for r in responses:
        p = r["prompt"]
        m = _safe_json(r["raw"]) or {}
        outlook = (m.get("outlook") or "")
        senti = m.get("sentiment")
        kw = p.meta.get("kw_regex", "")
        hit = bool(re.search(kw, outlook, re.IGNORECASE)) if kw else False
        per_event.setdefault(p.case_id, {})[p.arm] = {
            "mention": hit, "sentiment": senti, "outlook": outlook,
        }
        mention += int(hit)
        total += 1
    mention_rate = mention / total if total else float("nan")
    skews = []
    for case, arms in per_event.items():
        pre, post = arms.get("pre"), arms.get("post")
        if pre and post and pre["sentiment"] is not None and post["sentiment"] is not None:
            skews.append(post["sentiment"] - pre["sentiment"])
    skew_mean = statistics.mean(skews) if skews else float("nan")
    skew_std  = statistics.stdev(skews) if len(skews) > 1 else float("nan")
    if mention_rate <= 0.10:
        m_v = "clean"
    elif mention_rate <= 0.35:
        m_v = "mild"
    else:
        m_v = "disqualified"
    # sentiment skew interpretation: magnitude > 0.4 over symmetric base = strong contamination
    if abs(skew_mean) > 0.6:
        s_v = "disqualified"
    elif abs(skew_mean) > 0.3:
        s_v = "mild"
    else:
        s_v = "clean"
    rank = {"clean": 0, "mild": 1, "disqualified": 2}
    verdict = max([m_v, s_v], key=lambda v: rank[v])
    return {"n": total, "mention_rate": mention_rate, "skew_mean": skew_mean,
            "skew_std": skew_std, "mention_verdict": m_v, "sentiment_verdict": s_v,
            "verdict": verdict}


def score_probe_c(responses: list[dict]) -> dict:
    """
    Compare mean score on narrative_loaded vs neutral tickers. Welch t-stat (manual).
    """
    by_bucket = {"narrative_loaded": [], "neutral": []}
    by_ticker = {}
    for r in responses:
        m = _safe_json(r["raw"]) or {}
        s = m.get("score")
        if s is None:
            continue
        p = r["prompt"]
        bucket = p.arm
        if bucket in by_bucket:
            by_bucket[bucket].append(s)
        by_ticker.setdefault(p.meta["ticker"], []).append(s)
    means = {b: statistics.mean(v) if v else float("nan") for b, v in by_bucket.items()}
    delta = means["narrative_loaded"] - means["neutral"] if all(by_bucket.values()) else float("nan")
    # Welch t (manual)
    def welch(a, b):
        ma, mb = statistics.mean(a), statistics.mean(b)
        va, vb = statistics.variance(a) if len(a) > 1 else 0, statistics.variance(b) if len(b) > 1 else 0
        denom = math.sqrt(va/len(a) + vb/len(b)) if (va or vb) else 1e-9
        return (ma - mb) / denom
    t = welch(by_bucket["narrative_loaded"], by_bucket["neutral"]) if all(by_bucket.values()) else float("nan")
    # Spearman ρ between ticker mean score and a public-narrative ranking placeholder.
    # Placeholder ranking: narrative_loaded tickers get arbitrary descending sentiment rank.
    # Replace with a curated public-narrative ranking before reporting.
    public_rank = {tk: i for i, tk in enumerate(
        ["RELIANCE","TCS","HDFCBANK","INFY","ITC","ASIANPAINT","IRFC","SUZLON",
         "ADANIENT","ADANIGREEN","VEDL","ZEEL","PAYTM","YESBANK","IDEA"])}
    model_rank = sorted(by_ticker.keys(),
                        key=lambda tk: -statistics.mean(by_ticker[tk]))
    paired = [(public_rank.get(tk, len(public_rank)), i) for i, tk in enumerate(model_rank)]
    if len(paired) >= 3:
        n = len(paired)
        d2 = sum((a - b) ** 2 for a, b in paired)
        rho = 1 - (6 * d2) / (n * (n*n - 1))
    else:
        rho = float("nan")
    if not (delta == delta):
        verdict = "insufficient_data"
    elif abs(delta) < 0.2 and (rho != rho or rho < 0.4):
        verdict = "clean"
    elif abs(delta) > 0.5 or (rho == rho and rho > 0.7):
        verdict = "disqualified"
    else:
        verdict = "mild"
    return {"mean_loaded": means["narrative_loaded"], "mean_neutral": means["neutral"],
            "delta": delta, "welch_t": t, "spearman_rho": rho, "verdict": verdict}


# ----------------------------------------------------- combined gate


def combined_gate(a: dict, b: dict, c: dict) -> dict:
    verdicts = [a["verdict"], b["verdict"], c["verdict"]]
    if "disqualified" in verdicts:
        role = "no_llm_in_signal_path"
    elif all(v == "clean" for v in verdicts):
        role = "role_1_forecasts_allowed"
    else:
        role = "role_2_regime_and_events_only"
    return {
        "probe_a": a, "probe_b": b, "probe_c": c,
        "verdicts": verdicts, "role": role,
    }


# ----------------------------------------------------- harness skeleton


def run(prompts: Iterable[ProbePrompt], client_fn: Callable[[str], str]) -> list[dict]:
    """Generic harness. `client_fn(prompt_str) -> raw_response_text`. No retries here; add them."""
    out = []
    for p in prompts:
        raw = client_fn(p.prompt)
        out.append({"prompt": p, "raw": raw})
    return out


if __name__ == "__main__":
    # Smoke check: build all prompts, print counts. No model call.
    a = build_probe_a_prompts()
    b = build_probe_b_prompts()
    c = build_probe_c_prompts()
    print(f"Probe A prompts: {len(a)} (events x 2 arms = {len(PROBE_A_EVENTS)} x 2)")
    print(f"Probe B prompts: {len(b)} (events x 2 arms = {len(PROBE_B_EVENTS)} x 2)")
    print(f"Probe C prompts: {len(c)} (tickers x samples = "
          f"{sum(len(v) for v in PROBE_C_TICKERS.values())} x {PROBE_C_SAMPLES_PER_TICKER})")
    print("\nExample A-event prompt:\n" + a[0].prompt)
    print("\nExample B-pre prompt:\n" + b[0].prompt)
    print("\nExample C prompt:\n" + c[0].prompt)
