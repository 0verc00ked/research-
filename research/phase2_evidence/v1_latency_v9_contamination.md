# V-1 (Latency to Indian broker APIs) + V-9 (LLM contamination test design)

**Date:** 2026-05-21
**Author:** Research analyst (skeptical default)
**Scope:** Resolve two Phase-2 verification items from `SYNTHESIS.md §7`.
**Companion artifacts:**
- Raw curl timings & traceroutes: `sources/raw/2026-05-21_v1_latency/`
- Executable contamination probe scaffold: `phase2_evidence/contamination_probe.py`

---

## Part A — V-1: Latency to Kite Connect (and peer brokers)

### A.0 Honest scope statement

I do **not** have an AWS `ap-south-1` EC2 instance available. All numbers below are measured **from this Mac** in **Kochi, Kerala, on Reliance Jio FTTH** (public IP `152.58.217.209`, AS55836, Asia/Kolkata). They tell us:

- What a residential Jio India connection looks like to each broker today (useful as a **lower bound** for ops-from-home and as the **upper bound** that ap-south-1 must beat).
- The **DNS topology / hosting fabric** of each broker (Cloudflare anycast vs AWS ap-south-1 ELB vs CloudFront — see A.2). This is the *most useful* finding from a Mac run, because it survives the move to EC2.
- Variance and tail behavior at the application + ISP layer.

They **do not** tell us:
- The actual ap-south-1 → broker RTT a deployed bot would see (likely **substantially lower** for AWS-hosted endpoints, possibly **similar** for Cloudflare-edge endpoints).
- Order placement latency under exchange-hour load.
- Behavior under burst/throttle.

Trust scores below: **measured-from-Mac = T4**, **ap-south-1 extrapolation = T1** until the runbook in §A.5 is executed.

### A.1 Methodology used (Mac, 2026-05-21)

- Tool: `/usr/bin/curl 8.7.1` with `-w` timing breakdown (`time_namelookup`, `time_connect`, `time_appconnect` (TLS), `time_starttransfer` (TTFB), `time_total`).
- **30 iterations per host**, back-to-back, HTTPS GET to `https://<host>/`. Default behavior triggers full DNS → TCP → TLS → HTTP request each iteration (no keep-alive across iterations because curl exits).
- Output recorded one line per iteration to `sources/raw/2026-05-21_v1_latency/rest_<host>.log`.
- Parsing & percentiles via `parse.py` (linear interpolation between samples).
- Traceroutes: `traceroute -n -w 1 -m 20 -q 1` (single probe, named hops disabled to avoid PTR delay). Saved in `traceroutes.log`. ICMP is filtered past hop 7 on Jio's CGNAT — expected.

**Caveat about TLS timing on macOS curl:** Apple's bundled curl links against SecureTransport / LibreSSL. TLS 1.3 with 0-RTT may be reused for the same hostname within a curl session; here each iteration is a separate process so we get a fresh full handshake — apples-to-apples across hosts.

### A.2 DNS / hosting fabric (this is the load-bearing finding)

| Host | Resolves to | Edge fabric | Mumbai-region? |
|---|---|---|---|
| `api.kite.trade` | `104.16.33.50`, `104.16.34.50` | **Cloudflare anycast** (104.16.0.0/12) | Cloudflare BOM / DEL PoP, not AWS Mumbai |
| `ws.kite.trade` | `kite-prod-ticker-connect-1378672944.ap-south-1.elb.amazonaws.com` → `13.206.9.219`, `3.7.28.249` | **AWS ALB in ap-south-1** | **Yes** |
| `api.upstox.com` | `api.upstox.com.cdn.cloudflare.net` | **Cloudflare** | No (anycast) |
| `api.fyers.in` | `data-fy-in-lb-1496158902.ap-south-1.elb.amazonaws.com` | **AWS ALB in ap-south-1** | **Yes** |
| `api.dhan.co` | `d2xp57zo8omd3y.cloudfront.net` | **AWS CloudFront** (edge POPs) | No (edge) |
| `apiconnect.angelbroking.com` | `103.82.178.77` | Self-hosted (Sify / Mumbai DC, AS) | Likely Mumbai DC |

**Implication for ap-south-1 hosting decision:**

1. The Kite **REST** endpoint is Cloudflare-fronted. RTT from ap-south-1 → Cloudflare BOM is ~1–3 ms (well-known; T2: cloudping.co). RTT from a Jio FTTH home to Cloudflare BOM is **~30 ms minimum** (measured below). The TLS handshake is **3 RTTs for TLS 1.3 full handshake including TCP** (1 SYN + 1 ClientHello + 1 Finished + 1 GET ≈ 4× RTT to TTFB on a cold connection).
2. The Kite **WS** ticker endpoint is on an AWS ALB in `ap-south-1`. From `ap-south-1` itself, intra-region RTT is **<1 ms** (T3: AWS). From Jio FTTH today I measured **~43 ms minimum** TCP RTT.
3. **Therefore, the ap-south-1 → Kite latency picture is essentially "1 RTT to Cloudflare for REST, ~0 RTT to ws.kite.trade for WS"** — both extremely fast. The Phase 4 number of "1–5 ms intra-region to broker" survives this check for WS; for REST it's accurate only because Cloudflare has BOM presence.

### A.3 Measurements from this Mac (Kochi → Internet, n=30 per host)

All values **milliseconds**. `tcp_only` = `time_connect − time_namelookup` (pure TCP SYN/ACK), `tls_only` = `time_appconnect − time_connect` (TLS handshake), `ttfb` = `time_starttransfer` from start, `total` = full request including body.

| host | tcp p50 | tcp p95 | tcp p99 | tcp min | tls p50 | tls p99 | ttfb p50 | ttfb p99 | total p50 | total p99 |
|---|---|---|---|---|---|---|---|---|---|---|
| api.kite.trade (CF) | 61.5 | 350.7 | 368.3 | 30.3 | 67.1 | 290.6 | 320.9 | 740.0 | 321.3 | 740.8 |
| ws.kite.trade (AWS ap-south-1) | 72.8 | 201.1 | 496.2 | 43.0 | 287.5 | 1441.7 | 482.9 | 1952.7 | 484.7 | 1956.2 |
| api.upstox.com (CF) | 57.0 | 188.1 | 240.6 | 28.9 | 61.1 | 509.5 | 279.9 | 833.1 | 280.4 | 833.9 |
| api.fyers.in (AWS ap-south-1) | 69.5 | 174.7 | 387.4 | 47.1 | 81.8 | 496.4 | 313.3 | 825.4 | 315.7 | 833.2 |
| api.dhan.co (CloudFront) | 46.2 | 118.2 | 158.5 | 27.7 | 57.7 | 277.8 | 229.0 | 481.9 | 232.6 | 493.0 |
| apiconnect.angelbroking.com (Mumbai DC) | 76.0 | 1772.6 | 3072.5 | 53.2 | 101.7 | 302.3 | 340.3 | 3508.0 | 340.7 | 3508.9 |

Raw logs: `sources/raw/2026-05-21_v1_latency/rest_*.log`, `wsrest_ws.kite.trade.log`.

**Readings:**

- **TCP-min is the cleanest "physical RTT" signal**: ~28–47 ms minimum from Kochi-Jio to any major broker endpoint. That tracks the speed-of-light + Jio backbone reality (Kochi → Mumbai geodesic ≈ 1,300 km → ~13 ms fibre theoretical one-way → ~26 ms RTT theoretical floor; my 28 ms is consistent).
- **ws.kite.trade TLS p99 = 1,441 ms** is a real tail. The AWS ALB in ap-south-1 is fronted by no edge cache, so a Jio routing hiccup hits the user directly. From ap-south-1 itself this tail will **disappear**.
- **AngelOne TCP p99 = 3,072 ms** is wild — one or two outliers blew it up, likely a single ICMP/SYN retransmit on Jio. Re-running another day would smooth it. Flagged, not blocking.
- **Kite REST TTFB p50 ≈ 321 ms from a Jio home** is the number to keep in mind for "if my bot lives on my laptop": ~3× higher than what ap-south-1 will see.

### A.4 Traceroute summary

All routes leave Jio CGNAT (`192.0.0.1` hops 2–5), enter Jio backbone (`192.168.x.x` internal P/PE addresses, hops 6–7), then ICMP-filter from hop 8 onward — typical of cloud and CDN destinations. Visible final hops:

- `api.kite.trade` (CF 104.16.34.50): 13 hops, final ~84 ms.
- `ws.kite.trade` (AWS ap-south-1 13.206.9.219): ICMP-blackholed past hop 7 (AWS ALB drops ICMP).
- `api.fyers.in`: same — ICMP-blackholed past hop 7.
- `api.dhan.co` (CloudFront): blackholed past hop 7.
- `api.upstox.com` (CF 172.64.147.179): final at hop 11, ~99 ms.

Net: ~7 hops within Jio backbone, then 1–3 hops into peering / AWS / CF, total path is short. Nothing pathological. Full file: `traceroutes.log`.

### A.5 Runbook for the **real** ap-south-1 measurement (paste into EC2)

Run this on a freshly launched `t4g.small` in `ap-south-1` (Mumbai). Total runtime ~5 min. **Save the resulting tarball back to `sources/raw/<DATE>_v1_latency_aws/`**.

```bash
#!/usr/bin/env bash
# V-1 ap-south-1 latency runbook. Run on EC2 t4g.small in ap-south-1.
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
OUT=/tmp/v1_aws_${TS}
mkdir -p "$OUT"; cd "$OUT"

# 0) Provenance — what box are we on?
{
  curl -s http://169.254.169.254/latest/meta-data/instance-type
  echo
  curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone
  echo
  curl -s http://169.254.169.254/latest/meta-data/public-ipv4
  echo
  uname -a
  date -u
} > provenance.txt

# 1) Format string for curl timing
cat > curl-format.txt <<'EOF'
%{http_code} dns=%{time_namelookup} connect=%{time_connect} tls=%{time_appconnect} pretransfer=%{time_pretransfer} ttfb=%{time_starttransfer} total=%{time_total} size=%{size_download}
EOF

# 2) 30 cold-handshake iterations per host (no connection reuse)
HOSTS="api.kite.trade ws.kite.trade api.upstox.com api.fyers.in api.dhan.co apiconnect.angelbroking.com"
for h in $HOSTS; do
  for i in $(seq 1 30); do
    curl -sk -o /dev/null -w "$(cat curl-format.txt)" "https://${h}/" >> "rest_${h}.log"
    echo "" >> "rest_${h}.log"
  done
done

# 3) Warm-connection (HTTP/2 multiplex, keep-alive) — closer to bot reality.
#    Bots maintain pooled sessions; cold RTT overstates per-request latency.
for h in api.kite.trade api.fyers.in api.upstox.com api.dhan.co; do
  curl -sk -o /dev/null -w "$(cat curl-format.txt)\n" \
    $(for i in $(seq 1 30); do echo "https://${h}/"; done) \
    >> "warm_${h}.log"
done

# 4) Authenticated-endpoint TTFB (PUBLIC endpoint that returns small JSON; needs no key):
#    Kite has /quote and /margins behind auth. Use the OHLC public-ish endpoint
#    or simply /  which returns 400 — both exercise the broker app server.
#    REPLACE with a real auth-token-bearing GET if you have a session.

# 5) Traceroute (mtr if installed; install if not — sudo yum install -y mtr)
if ! command -v mtr >/dev/null; then sudo dnf install -y mtr || sudo apt-get install -y mtr; fi
for h in $HOSTS; do
  mtr -n -c 30 -r "$h" > "mtr_${h}.txt" 2>&1 || traceroute -n -w 1 -m 20 "$h" > "tr_${h}.txt" 2>&1
done

# 6) Sustained ping (1-min) to characterize jitter
for h in $HOSTS; do
  ping -c 60 -W 1 "$h" > "ping_${h}.txt" 2>&1 || true
done

# 7) WS open + first-tick latency (requires Kite API key + access_token):
#    See ws_probe.py below (omitted here; carry over from agent codebase).

# 8) Pack and ship
cd /tmp && tar czf "v1_aws_${TS}.tgz" "v1_aws_${TS}"
echo "Done. Copy /tmp/v1_aws_${TS}.tgz to sources/raw/<DATE>_v1_latency_aws/"
```

**What to record beyond the raw logs (a checklist for the future you):**

1. Instance type, AZ, public IP, kernel.
2. Time of day in IST (network differs 09:15–15:30 vs off-hours).
3. Whether the box is in the same AZ as `ws.kite.trade`'s ALB (use `dig` to see which IPs back the ALB and compare prefix to `aws-ip-ranges.json` for ap-south-1 AZs).
4. p50/p95/p99 for: TCP-only, TLS-only, TTFB, total — both **cold** and **warm** (kept-alive) modes.
5. WS-specific: TLS handshake p50/p99, time-to-first-tick after subscribe, gap stats.
6. Order-placement (if a sandbox session is open): place_order REST p50/p99 vs market-state.

### A.6 Defensible bound on ap-south-1 → Kite RTT

Given (a) the broker hostnames resolve to either Cloudflare anycast (with a known Mumbai PoP) or AWS ap-south-1 ALBs (b) ap-south-1 intra-region RTT < 1 ms (T3, AWS) and AWS → Cloudflare BOM is 1–3 ms (T2, cloudping):

| Metric (ap-south-1 → broker, cold full handshake) | Defensible bound | Trust |
|---|---|---|
| TCP-only RTT, REST (Cloudflare path) | 1–5 ms | T2 |
| TCP-only RTT, WS (AWS ALB intra-region) | <1 ms | T3 |
| TLS-1.3 full handshake (TCP + TLS, REST) | 5–20 ms | T2 |
| TTFB cold REST (GET / on `api.kite.trade`) | 30–80 ms | T1 — measured value pending §A.5 runbook |
| TTFB warm REST (HTTP/2 reuse) | 5–25 ms | T1 — pending |
| WS subscribe → first tick | 100–400 ms | T1 — heavily depends on instrument liquidity / Kite's broadcast bus |
| `place_order` REST round trip (market hours) | 80–250 ms p50, 400–800 ms p99 | T2 — matches Phase 4 Table 2.2 estimate; needs T4 measurement |

### A.7 Does this change the Phase 4 latency budget?

Phase 4 §2.2 e2e budget with Haiku/Flash: **p50 ~3.3 s, p99 ~7.7 s**, dominated by the LLM call (~3 s p50, ~5 s p99).

- Network RTT to broker is **5–25 ms p50** from ap-south-1 — already negligible vs LLM.
- Even if a Jio-home-style 320 ms TTFB applied (it won't, but as a worst case), LLM still dominates by **>10×**.
- **Conclusion: no change to the latency budget.** The "1–5 ms intra-region to broker" assumption in `phase4_infra/infra_cost_model.md §1.2` survives. The 5-minute decision cadence floor in §2.3 holds.

The one caveat I want to flag: **TLS handshake cost** (5–20 ms ap-south-1) applies *per cold connection*. If the agent makes a fresh REST connection for every order, that compounds at p99. Phase 4 §5.2 already implies a session pool; this measurement reinforces it as a hard requirement, not an optimisation.

### A.8 Items still open after this verification

- **V-1.a (real T4):** Execute §A.5 runbook on an actual ap-south-1 t4g.small. Estimated cost: ~₹3 of EC2 time if you spin and terminate within an hour. **Blocker before G2 (live plumbing) — not before G0/G1.**
- **V-1.b (order-placement latency under load):** Requires an authenticated Kite session. Defer to first paper-trade week.
- **V-1.c (WS reconnect storm behavior):** Kite's stated reconnect policy + how the SDK behaves on ALB drain. Defer to paper trading.

---

## Part B — V-9: Contamination test design for LLM analyst on Indian tickers

### B.0 Why this gate exists

If the LLM analyst "knows" the future of NIFTY/BANKNIFTY constituents from training-data leakage, every backtest that uses it produces phantom alpha. Gao/Jiang/Yan arXiv:2512.23847 (T3) showed this is a measurable and significant problem on US tickers with their "Lookahead Propensity" statistic. **No published equivalent for Indian tickers as of 2026-05-21.** The defensible move is to run our own probes before any LLM-in-the-loop backtest is allowed to "count."

The thesis of the test: **the LLM analyst pillar of the architecture only survives if its outputs are calibrated **after stripping any known-future signal**, OR if we restrict the LLM to *non-predictive* tasks (regime tagging, news summarization, narrative classification) where leakage is structurally less impactful.**

### B.1 Three probes

#### Probe A — Forward-event leakage (the StockBench-style probe)

**Hypothesis:** Given a prompt that explicitly anchors "today = D" for some D before the model's training cutoff, the model's "forecasts" or "expectations" for D+1 … D+N reflect knowledge of what actually happened, not its stated reasoning.

**Construction:** For each pair `(ticker, date D)` where D is at least 30 trading days before the model's stated cutoff, build a prompt that:
1. Sets the scene ("Assume today is 2024-01-22. You know only what was public before this date.").
2. Provides a stub of public-pre-D context (last earnings, sector commentary — without leaking the result).
3. Asks for: (i) direction probability for +5 / +20 / +60 trading days, (ii) the model's stated confidence, (iii) any specific catalyst it expects.

Compare predictions to:
- **A null baseline** = same prompt with `D` replaced by a fictitious date far in the model's pre-cutoff window for the *same* ticker (e.g., shifted by ±90 trading days). Bayesian: if the model is uncontaminated, prediction distributions should not differ meaningfully across nearby Ds. If contaminated, they will be sharper / more correct near actual-event Ds.
- **Realized returns** over those windows.

**Universe (initial run, n=30 events):**
- 10 "uneventful" dates across NIFTY-50 names with no large move in D+1..D+20.
- 10 dates that preceded **sharp moves** (>±5σ daily) — Adani Jan 24 2023 (-23% intraday on Hindenburg), Yes Bank Mar 5 2020 (moratorium), Paytm Feb 1 2024 (RBI ban on PPB), Vodafone Idea Mar 26 2025 (AGR), IRFC Jan 12 2024 (Budget pop), Zee Jan 22 2024 (Sony merger collapse), HDFC-HDFC Bank Jul 2023 merger close, Adani-Hindenburg follow-on Feb 2 2023, RIL bonus Oct 2024, Tata Motors demerger Aug 2024.
- 10 dates preceding **earnings beats/misses** of >10% vs consensus on liquid NIFTY-50 names.

**Null hypothesis ($H_0$):** Direction probability conditional on "D = actual event minus 5 trading days" is statistically indistinguishable from direction probability conditional on "D = nearby non-event date" for the same ticker.

**Contamination signal:** the model's stated direction probability at D matches the realized D+5/D+20 sign with hit rate `r > 0.65` across n=30 events, *and* its hit rate on the matched null dates is `≤ 0.55`. The difference is significance-tested with a paired binomial / McNemar's test, α = 0.05.

#### Probe B — Known-date confound

**Hypothesis:** For famous events the model "knows," analysis flips depending on whether the prompted date is before or after the event, *even if everything else in the prompt is identical*.

**Construction:** Same factual context, two prompts:
- *Pre:* "Today is 2023-01-23. Adani Enterprises (ADANIENT) at ₹3,442. Summarize one-week outlook."
- *Post:* "Today is 2023-02-10. Adani Enterprises (ADANIENT) at ₹1,404. Summarize one-week outlook."

…with **no Hindenburg context provided in either prompt**. A contamination-free model should produce two symmetric, momentum-blind outlooks. A contaminated model "remembers" the report and writes "given the recent governance allegations…" in the Post prompt, or "I would caution given upcoming risks…" in the Pre prompt. Both are leakage tells.

**Event roster (n=8, all T3-documented):**
1. ADANIENT, 2023-01-24 Hindenburg report
2. ADANIPORTS, 2023-02-02 follow-on collapse
3. RELIANCE, 2024-10-28 1:1 bonus
4. PAYTM, 2024-02-01 RBI PPB ban
5. ZEEL, 2024-01-22 Sony merger collapse
6. YESBANK, 2020-03-05 RBI moratorium
7. NIFTY, 2020-03-23 COVID low
8. NIFTY, 2024-06-04 election counting day (–5.9% intraday)

**Scoring:** For each event, compute two scores on the model's free-text output:
- **Event-mention rate:** does the output mention the actual event by name, by date, or by sufficiently specific paraphrase ("the recent short-seller allegations", "the merger fell through")? Binary per output. Annotated by the analyst (n=2 raters, Cohen's κ reported).
- **Sentiment skew:** sentiment score on the outlook text (a tiny LLM-as-judge call with a separate model, OR a lexicon-based VADER-style score). Sign should flip if the model is conditioning on date-vs-event.

**Null hypothesis:** event-mention rate is ≤ 1/n_dates random-base across pre and post prompts, and sentiment skew is symmetric.

**Contamination signal:** event-mention rate > 25% on either side, OR sentiment skew between pre/post pairs exceeds 1.5σ of the within-stable-date variance.

#### Probe C — Ticker prior

**Hypothesis:** Independent of features, the model carries a structural bull/bear bias on certain Indian tickers from training-data sentiment.

**Construction:** One prompt template, no date anchor, no recent context:

> "Give a one-paragraph 12-month outlook on the Indian listed stock {TICKER}. Provide a numerical bull/bear score from −1.0 (very bearish) to +1.0 (very bullish), then justify."

Tickers (n=14, mix of "narrative-loaded" and "neutral"):

| Narrative-loaded | Neutral / quiet |
|---|---|
| ADANIENT, ADANIGREEN | TCS |
| YESBANK, PAYTM | INFY |
| ZEEL, VEDL | HDFCBANK |
| RELIANCE, IRFC | ITC |
| SUZLON, IDEA | ASIANPAINT |

Run **n=20 samples per ticker at T=0.7** (use sampling temperature; cache prompts; rotate order to mitigate position bias).

**Null hypothesis:** Across the 14 tickers, the distribution of mean bull/bear scores is approximately symmetric around 0 and not correlated with the narrative-loaded vs neutral split.

**Contamination signal:** the narrative-loaded set's mean score is >0.4 away from the neutral set's mean (Welch's t-test, α = 0.05). Or, equivalently: ranking of tickers by mean score reproduces the public-narrative ranking with Spearman ρ > 0.7.

### B.2 Pass / fail thresholds (load-bearing — these gate the architecture)

The architecture has **two possible roles** for the LLM analyst:
- **Role 1 (strong):** Forecasts / direction probabilities feed the strategy layer (used for sizing or veto).
- **Role 2 (weak):** Regime tags / news-event flags / narrative classification only — never a forecast, never a probability, never a per-ticker bias. The deterministic strategy layer does the forecasting using price + structural features only.

| Probe | "Clean" (Role 1 OK) | "Mild contamination" (Role 2 only) | "Disqualified" (no LLM in signal path) |
|---|---|---|---|
| **A — Forward leakage** | hit-rate-on-event ≤ hit-rate-on-null + 0.05, p > 0.05 | spread 0.05–0.15 or p ∈ [0.01, 0.05] | spread > 0.15 OR p < 0.01 |
| **B — Known-date confound** | event-mention rate ≤ 10%, sentiment skew symmetric | mention rate 10–35%, sentiment skew 1.5–3σ | mention rate > 35% OR skew > 3σ |
| **C — Ticker prior** | |Δ mean| < 0.2, Spearman ρ < 0.4 | |Δ mean| 0.2–0.5 or ρ ∈ [0.4, 0.7] | |Δ mean| > 0.5 OR ρ > 0.7 |

**Combined gate:**
- **Role 1 unlocked** iff *all three probes* land in the "clean" column.
- **Role 2 (default)** iff at most one probe is in "mild," none in "disqualified."
- **No-LLM** if any probe is in "disqualified."

**Author's strong prior (T1, will be tested):** Every frontier model trained through ≥2024-12 will land **at least mild-contaminated** on Probe B. That's why the architecture in SYNTHESIS §5 already restricts the LLM to Role 2 (regime / event-flag outputs that the deterministic layer can selectively ignore). The probes are not for *whether* to allow Role 1 — they're for *quantifying how badly* a model would lie if you gave it Role 1, so we know how aggressively to discount its Role-2 outputs as well.

### B.3 Tie back to the trust rubric

- Probe results are **T4** (we ran them), subject to standard caveats about sample size.
- Decisions driven from probe results must cite the run date and the model+version pinned (e.g., `claude-haiku-4.5-20251015`). Re-run on every model upgrade. **No T0/T1 lookahead-cleanliness claim is allowed to drive a decision** (rubric line 4).
- Probe A inherits its methodology from Gao/Jiang/Yan 2025 (arXiv:2512.23847, T3). The application to Indian tickers is novel; reproducibility is essential — every prompt, seed, sample, and judge-rater pair must be checked into `phase2_evidence/contamination_runs/<date>_<model>/`.

### B.4 Executable harness

See `phase2_evidence/contamination_probe.py`. It builds all three probes' prompts in code, defines the scoring rubric, and includes a deterministic null-baseline shuffler — **no network calls yet**. The user picks a model, plugs in an API client, and runs. Output is a JSON+markdown report with the pass/fail verdict per probe and combined gate.

---

## Headlines (for SYNTHESIS §7 update)

- **V-1 (from-Mac T4):** Kite REST `api.kite.trade` from Kochi-Jio FTTH: TCP p50 = **61 ms**, TLS p50 = **67 ms**, **TTFB p50 = 321 ms**, **TTFB p99 = 740 ms**. Min TCP RTT 30 ms. `ws.kite.trade` lives on AWS ap-south-1 (T4); `api.kite.trade` lives on Cloudflare anycast (T4). Phase 4 latency budget is **unchanged** — LLM dominates network by >10× regardless. Real ap-south-1 measurement is a 5-minute runbook (§A.5), blocker only at Stage G2.
- **V-9 thresholds:** Role-1 (LLM forecasts feed strategy) unlocked **only if all three probes are clean**. Default expectation is Role-2 (regime/event flags only). Disqualification on any single probe in the "disqualified" column.
