#!/usr/bin/env python3
"""Parse curl timing logs and compute percentiles per host."""
import re, statistics, glob, os, json

LOG_DIR = os.path.dirname(os.path.abspath(__file__))
PAT = re.compile(
    r"(\d+) dns=(\S+) connect=(\S+) tls=(\S+) pretransfer=(\S+) ttfb=(\S+) total=(\S+) size=(\S+)"
)

def pct(xs, p):
    if not xs:
        return None
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100
    f, c = int(k), min(int(k) + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def parse_file(path):
    rows = []
    with open(path) as f:
        for line in f:
            m = PAT.search(line)
            if not m:
                continue
            code, dns, conn, tls, pre, ttfb, total, size = m.groups()
            rows.append({
                "code": int(code),
                "dns_ms": float(dns) * 1000,
                "connect_ms": float(conn) * 1000,
                "tls_ms": float(tls) * 1000,
                "ttfb_ms": float(ttfb) * 1000,
                "total_ms": float(total) * 1000,
                # Derived: tcp handshake only = connect - dns; tls handshake only = tls - connect
                "tcp_only_ms": (float(conn) - float(dns)) * 1000,
                "tls_only_ms": (float(tls) - float(conn)) * 1000 if float(tls) > 0 else 0,
                "server_ms": (float(ttfb) - float(tls)) * 1000 if float(tls) > 0 else (float(ttfb) - float(conn)) * 1000,
            })
    return rows

summary = {}
for path in sorted(glob.glob(os.path.join(LOG_DIR, "rest_*.log")) +
                   glob.glob(os.path.join(LOG_DIR, "wsrest_*.log"))):
    host = os.path.basename(path).replace("rest_", "").replace("wsrest_", "").replace(".log", "")
    rows = parse_file(path)
    if not rows:
        continue
    metrics = {}
    for k in ["tcp_only_ms", "tls_only_ms", "ttfb_ms", "total_ms", "server_ms"]:
        vals = [r[k] for r in rows]
        metrics[k] = {
            "n": len(vals),
            "p50": round(pct(vals, 50), 2),
            "p95": round(pct(vals, 95), 2),
            "p99": round(pct(vals, 99), 2),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
            "mean": round(statistics.mean(vals), 2),
        }
    metrics["http_codes"] = sorted(set(r["code"] for r in rows))
    summary[host] = metrics

print(json.dumps(summary, indent=2))

# Also print a compact markdown table
print("\n\n## Per-host summary (ms)\n")
print("| host | tcp p50 | tcp p99 | tls p50 | tls p99 | ttfb p50 | ttfb p99 | total p50 | total p99 |")
print("|---|---|---|---|---|---|---|---|---|")
for h, m in summary.items():
    print(f"| {h} | "
          f"{m['tcp_only_ms']['p50']} | {m['tcp_only_ms']['p99']} | "
          f"{m['tls_only_ms']['p50']} | {m['tls_only_ms']['p99']} | "
          f"{m['ttfb_ms']['p50']} | {m['ttfb_ms']['p99']} | "
          f"{m['total_ms']['p50']} | {m['total_ms']['p99']} |")
