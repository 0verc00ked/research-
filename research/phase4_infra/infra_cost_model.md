# Phase 4 — Infrastructure, Latency & Cost Model

**Author:** Research analyst (skeptical default)
**Date:** 2026-05-21
**FX placeholder:** USD 1 = INR 84 (rate-sensitive; see §6)
**Scope:** Solo India operator, very low capital, India-targeted bot (NSE/BSE cash + F&O via retail broker API). HFT/colo explicitly out of scope per `README.md`.

> TL;DR — Minimum defensible monthly burn for a *live* LLM-agent bot on Indian equities/F&O is **~₹3,000–₹4,500/month** with a free-tier broker, a Hetzner/Oracle Always-Free VM, and Gemini Flash / Claude Haiku on a 15-minute decision cadence. At a 5-minute cadence with Sonnet-class models, expect **₹8,000–₹15,000/month**. Realistic reachable horizons: **1-minute bars and slower**. Tick / sub-second is unreachable for LLM-in-the-loop.

---

## 1. Hosting options for an India-targeted bot

### 1.1 What "good enough" means here
Trade decisions happen on candle closes (1-min, 5-min, 15-min). We need:
- **Stable outbound HTTPS** to broker (`api.kite.trade`, `api.upstox.com`, etc.) — Mumbai-region endpoints
- **<200 ms** round-trip to broker REST/WebSocket (broker, not exchange, is our latency frontier — retail orders go through broker risk gates regardless)
- **24×7 uptime during market hours 09:15–15:30 IST** with auto-restart
- **No need** to be NSE-colo-adjacent. Retail broker APIs are nowhere near the colo fast path; sub-ms-to-NSE is irrelevant when the order traverses Zerodha's stack first.

### 1.2 Option table

| Option | Region | Spec | Monthly cost | Latency to broker (Mumbai) | Reliability | Trust |
|---|---|---|---|---|---|---|
| Home machine + residential ISP (Jio/Airtel FTTH) | Anywhere India | Existing hardware | ₹0 marginal (₹999 ISP shared) | 10–40 ms RTT to Mumbai | **Bad**: power cuts, router reboots, ISP NAT/CGNAT, IP churn, no SLA | T2 |
| AWS EC2 `t4g.small` (2 vCPU ARM, 2 GB) ap-south-1 | Mumbai | Burstable | ~$15–17 / **₹1,260–1,430** | 1–5 ms intra-region to broker | 99.99% region SLA | T3 (see source) |
| AWS EC2 `t4g.medium` (2 vCPU, 4 GB) ap-south-1 | Mumbai | Burstable | ~$30–34 / **₹2,520–2,860** | same | same | T3 |
| AWS `t4g.small` ap-south-2 (Hyderabad) | Hyderabad | Burstable | ~$15–17 / **₹1,260–1,430** (parity expected; **needs verification**) | +8–15 ms vs Mumbai to broker | 99.99% | T1 — needs verification |
| Oracle Cloud Mumbai — **Always Free** (2× AMD VM.Standard.E2.1.Micro or 1× Ampere A1 4 vCPU/24 GB) | Mumbai | ARM | **₹0** | 1–10 ms to broker | "Always free" but Oracle has reclaimed idle Ampere VMs; not contractually durable | T2 — needs verification of current Mumbai availability |
| GCP `e2-small` Mumbai (asia-south1) | Mumbai | 2 vCPU shared, 2 GB | ~$13–15 / **₹1,090–1,260** | 1–5 ms intra-region | 99.95% | T1 — needs verification |
| Azure B2s Central India | Pune | 2 vCPU, 4 GB | ~$30 / **₹2,520** | 5–15 ms to Mumbai broker endpoints | 99.95% | T1 — needs verification |
| Hetzner CX22 (Falkenstein/Helsinki) | EU | 2 vCPU ARM, 4 GB | €4.49 + VAT / **~₹430** | **120–180 ms RTT to Mumbai broker** | Excellent uptime, but EU egress | T3 |
| DigitalOcean Bangalore `s-1vcpu-2gb` | Bangalore | 1 vCPU, 2 GB | $12 / **₹1,008** | 15–30 ms to Mumbai | 99.99% | T1 — needs verification |
| Contabo / Linode | Various | Various | $5–10 / **₹420–840** | Region-dependent, usually >100 ms to Mumbai | Mixed | T1 |

**AWS Mumbai t4g pricing reality check:** US-east-1 list is $0.0168/h (t4g.small) and $0.0336/h (t4g.medium) (T3: economize/vantage). ap-south-1 typically runs ~10–20% above us-east-1 on burstable ARM. Plug ~$0.020/h × 730 h = **~$14.6/mo for t4g.small**, ~**$29/mo for t4g.medium**, + EBS (~$0.10/GB-mo gp3 → ~$1 for 10 GB) + data transfer (negligible if logs stay <10 GB/mo). **Needs verification on the official AWS Mumbai pricing page** (T1 right now, the calculator pages searched returned us-east-1 numbers).

### 1.3 Pros / cons summary

**Home + residential:** Looks free, isn't. One power cut during a position = a fill at the wrong side. CGNAT means inbound webhooks need tunneling. **Disqualified for live trading** beyond paper.

**AWS / GCP / Azure Mumbai:** Best latency-to-broker, best reliability, highest cost. Free tier (1 yr) makes AWS effectively ₹0 for year-1 on t3.micro/t4g.small if you're a new account. **Default pick if Oracle Always Free is unavailable.**

**Oracle Always Free Mumbai (Ampere A1):** If you can grab it and hold it, this is the floor. 4 vCPU/24 GB ARM is overkill for our workload. Risk: capacity-claimed reboots, ToS changes. **Recommended as primary with AWS Mumbai as warm standby.**

**Hetzner EU:** Cheapest reliable VM in the world, but +150 ms RTT kills 1-minute-bar reactivity. **Fine for research/backtest box, not for execution.**

**DigitalOcean Bangalore:** Solid mid-tier. Bangalore→Mumbai adds ~20 ms but acceptable for ≥1-min cadence.

---

## 2. Latency budget realism

### 2.1 LLM inference latency (2k input / 500 output)

| Model | TTFT p50 | TTFT p99 | Throughput | End-of-stream p50 (≈ TTFT + 500/tps) | Source |
|---|---|---|---|---|---|
| Claude Sonnet 4.6 | 500 ms | 1,400 ms | 90 tok/s | **~6.0 s** | T3 (TokenMix Apr 2026, 10k requests, 2k in / 500 out) |
| Claude Haiku 4.5 | ~300 ms (est) | ~800 ms (est) | 150+ tok/s (est) | **~3.5 s** | T1 — needs verification on artificialanalysis.ai |
| GPT-4o | ~450 ms | ~1,200 ms | ~80 tok/s | **~6.7 s** | T1 — needs verification |
| GPT-4o-mini | ~350 ms | ~900 ms | ~100 tok/s | **~5.4 s** | T1 — needs verification |
| Gemini 2.5 Flash | ~400 ms | ~1,100 ms | ~200 tok/s | **~2.9 s** | T1 — needs verification |
| Gemini 2.5 Flash-Lite | ~250 ms | ~700 ms | ~250 tok/s | **~2.3 s** | T1 — needs verification |
| Local Llama-3.1-8B Q4 on M2/M3 Mac | n/a | n/a | 30–60 tok/s | **8–17 s** | T2 (community llama.cpp benchmarks) |
| Local Llama-3.3-70B on rented H100 80GB | ~200 ms | ~600 ms | 40–80 tok/s | **6–13 s** | T2 |

Anthropic note: P95/P50 ratio of **1.8×** for Sonnet 4.6 — most consistent of the frontier providers (T3: TokenMix). OpenAI's ratio is ~2.7×, meaning tail blowouts are worse.

### 2.2 End-to-end agent loop (1-minute candle close trigger)

| Stage | p50 | p99 | Notes |
|---|---|---|---|
| Market-data ingest (broker WS → bar close) | 50 ms | 300 ms | KiteTicker pushes; bar built locally |
| Feature compute (indicators, regime, news fetch) | 100 ms | 1,500 ms | News API call dominates p99 |
| Prompt assembly + cache | 20 ms | 80 ms | Use prompt caching aggressively |
| LLM call (Haiku/Flash) | 3,000 ms | 5,000 ms | Streaming optional but doesn't help — we need full JSON |
| LLM call (Sonnet/GPT-4o) | 6,000 ms | 12,000 ms | Same |
| Risk check (position size, exposure, kill-switch flags) | 5 ms | 20 ms | Local |
| Broker order placement (REST `place_order`) | 150 ms | 800 ms | KiteConnect typical; T2 — needs verification with own tests |
| **Total e2e — Haiku/Flash** | **~3.3 s** | **~7.7 s** | |
| **Total e2e — Sonnet/GPT-4o** | **~6.3 s** | **~14.7 s** | |

### 2.3 Reachable horizons

| Horizon | LLM-agent viable? | Why |
|---|---|---|
| Tick / sub-100 ms | **No** | Even Haiku's TTFT eats the budget alone |
| 1-second bars | **No** | p99 e2e > 1 s for any model worth using |
| 1-minute bars | **Yes**, with Haiku/Flash/Lite | 7.7 s p99 leaves 52 s of the next bar for retries / hedging |
| 5-minute bars | **Yes, comfortable** | Any model |
| 15-min / hourly / daily | **Yes, ideal** | Use the strongest model you can afford |
| Overnight / multi-day | **Yes, ideal** | Cost dominates, latency irrelevant |

**Conclusion:** LLM-agent edge sits at 5-minute and slower. 1-min is the floor and only with small-model + ruthless prompt discipline. Anything faster needs traditional algo code, not an LLM in the hot path.

---

## 3. End-to-end monthly cost model (minimum viable)

### 3.1 Assumptions
- 21 trading days/month, 6.25 h/day cash session = **131 h/month live**
- Bot calls LLM only during market hours
- 2,000 input tokens / 500 output tokens per decision (T1 — depends heavily on prompt design)
- Prompt caching saves ~70% on input reads (90% headline rate × cache hit rate ~80%)
- INR/USD = 84

### 3.2 LLM cost per decision

| Model | $ / decision (raw) | $ / decision (with caching) |
|---|---|---|
| Claude Haiku 4.5 ($1 in / $5 out per M) | 2000×$1/M + 500×$5/M = **$0.0045** | **~$0.0017** |
| Claude Sonnet 4.6 ($3 / $15) | **$0.0135** | **~$0.0051** |
| GPT-4o-mini ($0.15 / $0.60) | **$0.00060** | **~$0.00023** |
| GPT-4o ($2.50 / $10) | **$0.0100** | **~$0.0038** |
| Gemini 2.5 Flash ($0.30 / $2.50) | **$0.00185** | **~$0.00070** |
| Gemini 2.5 Flash-Lite (~$0.10 / $0.40, T1 needs verification) | **$0.00040** | **~$0.00015** |

### 3.3 Decision-frequency cost grid (cached)

Decisions/month = 131 h × (60/cadence_min) calls.

| Cadence | Calls/mo | Haiku | Sonnet | GPT-4o-mini | GPT-4o | Flash | Flash-Lite |
|---|---|---|---|---|---|---|---|
| Every 5 min | 1,572 | $2.67 / **₹224** | $8.02 / **₹674** | $0.36 / **₹30** | $5.97 / **₹502** | $1.10 / **₹92** | $0.24 / **₹20** |
| Every 15 min | 524 | $0.89 / **₹75** | $2.67 / **₹224** | $0.12 / **₹10** | $1.99 / **₹167** | $0.37 / **₹31** | $0.08 / **₹7** |
| Every 1 hour | 131 | $0.22 / **₹19** | $0.67 / **₹56** | $0.03 / **₹3** | $0.50 / **₹42** | $0.09 / **₹8** | $0.02 / **₹2** |

LLM spend is **not** the binding constraint at any reasonable cadence. Compute + market-data is.

### 3.4 Full monthly burn (minimum viable, three tiers)

| Line | Floor (Oracle Free + Free broker + Flash-Lite @ 15min) | Mid (AWS t4g.small + Kite Connect + Haiku @ 5min) | Comfortable (t4g.medium + Kite Connect + Sonnet @ 5min) |
|---|---|---|---|
| Compute (VPS/cloud) | ₹0 (Oracle Always Free) | ₹1,400 (AWS t4g.small Mumbai) | ₹2,800 (AWS t4g.medium Mumbai) |
| EBS / storage | ₹0 | ₹100 (10 GB gp3) | ₹200 (20 GB gp3) |
| Broker API | ₹0 (Kite personal free for orders; **no live/historical data**) | ₹500 (KiteConnect data plan, T3) | ₹500 |
| Market-data backup / news (Marketaux/Newsdata free tiers, EOD scrape) | ₹0 | ₹0 | ₹500 (paid news API) |
| LLM API | ₹7 (Flash-Lite, 15-min) | ₹224 (Haiku, 5-min) | ₹674 (Sonnet, 5-min) |
| Storage off-box (S3 backups, R2) | ₹0 (local) | ₹50 (5 GB S3 ap-south-1) | ₹100 |
| Domain (.in / .dev) | ₹80 (₹950/yr amortized) | ₹80 | ₹80 |
| Monitoring (UptimeRobot free; BetterStack free) | ₹0 | ₹0 | ₹840 ($10 BetterStack) |
| SMS / Telegram alerts | ₹0 (Telegram Bot API free) | ₹0 | ₹0 |
| Buffer (egress, surprise) | ₹100 | ₹200 | ₹500 |
| **TOTAL FLOOR / MO** | **~₹190** | **~₹2,560** | **~₹6,200** |

**Realistic recommended floor for a *live* setup that won't lose money to ops glitches: the Mid tier at ~₹2,500–3,000/month** — Oracle Always Free is real but not contractually durable enough for live capital. Use it; just don't trust it.

### 3.5 The break-even number

At ₹2,560/month, with ~₹50,000 starting capital (low-capital realistic floor), the bot must clear **≥5.1% gross monthly return** just to pay rent — before taxes (STT, GST, stamp, exchange, SEBI), before slippage, before drawdown. At ₹25,000 capital, **≥10.2%/month**. This is the number that should haunt every backtest.

---

## 4. Self-hosted vs API LLM economics

### 4.1 Local on existing hardware (M-series Mac)
- **Marginal cost: ₹0** (electricity ~₹50/mo for 6 h × 21 d at 30 W)
- **Capability ceiling: Llama-3.1-8B / Qwen-2.5-7B Q4_K_M** — markedly weaker than Haiku for structured reasoning over financial text (T2)
- **Latency: 8–17 s e2e** — pushes you off 1-min bars
- **Verdict:** Use for backtesting, research, and offline feature engineering. Don't put it in the live decision loop unless you've benchmarked the *same* prompt vs Haiku on your *own* eval set.

### 4.2 Rented GPU for a real local model
- **Single H100 80GB on demand**: ~$2.50–3.50/h spot, ~$3.50–5/h on-demand (T1 — needs verification on Lambda/Runpod/Vast 2026 sheets)
- 131 market-hours/mo × $3 = **$393 / ~₹33,000/mo** for a single H100
- Llama-3.3-70B Instruct delivers ~Haiku-level quality at best, often worse on instruction-following (T2)
- **Break-even vs Haiku (cached):** at $0.0017/decision, you'd need ~230,000 decisions/month to match $393. We do 1,572/month at 5-min cadence. **Local rented GPU is 146× more expensive for our load.**
- **Break-even vs Sonnet (cached):** ~77,000 decisions/month. Still 49× over.

**Conclusion:** API LLMs win decisively at our decision rate. Local rented inference only pencils out for batch workloads (overnight backtests, embeddings, training-data labeling) — and even there, batch APIs at 50% off (T3: Anthropic batch) often beat it.

### 4.3 When does local stop losing?
| Decisions/month | Cheaper option |
|---|---|
| <10,000 | API every time (Haiku/Flash) |
| 10k–100k | API; consider on-demand H100 only if latency-bounded and you have engineering time |
| 100k–500k | Borderline; serious infra work to make local viable |
| >500k | Local rented GPU may win, but at this rate you're not running an LLM-in-the-loop bot, you're running a feature extractor — use a small distilled model |

---

## 5. Reliability & ops

### 5.1 Failure modes (ranked by expected damage)
1. **Broker session expiry mid-trade** — Kite access tokens expire daily ~06:00 IST. If your refresh logic fails, your bot stops *and* you don't notice. **Highest-impact silent failure.** (T2 — KiteConnect docs)
2. **Broker API throttle / 429** — Kite limits ~3 req/s order endpoints, 10 req/s general (T1 — needs verification on current docs). A retry storm = ban window during the very minutes you need to exit.
3. **LLM API outage / 5xx** — Anthropic, OpenAI, Google all have incidents. p99 unavailability ~0.5–1% (T1). Always have a **deterministic fallback policy** (e.g., "if LLM unreachable for >60 s, flatten and stop").
4. **Exchange / NSE outage** — happens (Feb 2021 NSE outage). Orders queue at broker; positions can't be exited. Out of your control; document in runbook.
5. **Network drop / VM reboot** — AWS maintenance, Oracle Ampere reclaim. Need cron-on-boot restart and state recovery from broker-side positions, never from local memory.
6. **Clock drift** — bar boundaries miscount. Run `chrony` / `systemd-timesyncd`. Trivial fix, common omission.
7. **Disk-full from logs** — kills the daemon. Logrotate + alert at 70%.
8. **Cost runaway** — runaway LLM loop on retry burns ₹thousands. Hard daily token budget per API key.
9. **Code deploy mid-session** — git pull while open positions exist. **Lock deploys to outside market hours** by policy.
10. **Personal failure mode** — operator panics, manually intervenes, undoes the bot. Pre-commit your kill-switch criteria.

### 5.2 Watchdog / kill-switch principles (no implementation yet)
- **Two-process design:** the trading agent and a separate watchdog. Watchdog does not share a Python interpreter with the agent. Different VM if budget allows.
- **Heartbeat:** agent writes timestamp to file/Redis every 5 s. Watchdog checks every 10 s. Two misses → flatten via independent broker session.
- **Independent kill path:** the watchdog must be able to square off positions *without* the agent's code path. It needs its own broker token and its own `place_order` (market-IOC, exit-only).
- **Hard limits the watchdog enforces (not the agent, the watchdog):**
  - Daily loss cap (e.g., -2% of NAV) → flatten + halt for the day
  - Per-trade loss cap → cancel and re-evaluate
  - Position count cap
  - Open exposure cap (gross, not net)
  - Order-rate cap (e.g., >10 orders/min = halt; assume bug)
- **External kill switch:** a Telegram command `/halt` that the watchdog reads, independent of the agent. So you can stop it from your phone in 5 seconds.
- **Cold-start invariant:** on boot, before placing any order, reconcile local intended state with broker-reported positions. Mismatch → halt, alert, human review.
- **No silent retries on order rejections:** every rejection logged + alerted. Two consecutive rejections on the same instrument → halt that instrument.
- **Time-of-day gates:** no new entries in last 15 min of session; force exits before close for intraday products. MIS auto-squareoff is the broker's safety net, not yours.
- **Paper-first invariant:** every code path must be runnable against a paper broker (or `--dry-run`) producing identical logs. CI enforces.

---

## 6. Sensitivities & caveats

- **FX:** At ₹90/USD the Mid tier moves from ₹2,560 to ₹2,720. At ₹80/USD, ₹2,430. Not a major lever.
- **Prompt size:** If your prompt drifts to 8k input / 1k output (common with sloppy context engineering), LLM cost rises **~4×**. Sonnet @ 5-min jumps from ₹674 to ~₹2,700. Prompt discipline is a cost control, not just a quality control.
- **Cache hit rate:** I assumed 80%. If you redesign prompts daily, you'll see <20% and costs will roughly double the "raw" column above.
- **Oracle Always Free:** Anecdotally reclaimed if idle. **Needs verification** that Mumbai region currently offers it and that a continuously-running trading process counts as "active." Treat as bonus, not baseline.
- **AWS Mumbai t4g pricing:** I used a US→Mumbai uplift of ~10–20% on top of public us-east-1 numbers. **Needs verification on https://aws.amazon.com/ec2/pricing/on-demand/ region selector** — the calculator pages I hit returned us-east-1.
- **Broker fee schedule (STT/exchange/GST/stamp) not included here** — those are per-trade, modeled in Phase 5. Infra is the *fixed* floor; trading frictions are the *variable* floor.
- **News/sentiment data:** Free tiers (Marketaux 100 req/day, Newsdata 200 req/day) are sufficient for low-cadence bots. If you need real-time Indian-language news, expect ₹1,000–5,000/mo more.

---

## 7. Recommendation

1. **Compute:** Start on Oracle Always Free Mumbai (Ampere A1) **with** an AWS t4g.small Mumbai as warm standby (~₹1,400/mo budgeted but not always spent). Deploy via Terraform/Ansible so flipping VMs is a 5-minute exercise.
2. **Broker:** Zerodha Kite — free trading API + ₹500/mo for live & historical data once you go past paper.
3. **LLM:** **Gemini 2.5 Flash-Lite** or **Claude Haiku 4.5** at **15-minute cadence** for v1. Sonnet/GPT-4o reserved for "should we even take this trade" gate, called <5×/day.
4. **Cadence ladder:** Paper for 60 days at 15-min → if Sharpe > 1.5 walk-forward, drop to 5-min → only then consider 1-min and only with smaller-model + tighter prompts.
5. **Floor to clear:** Bot needs to clear **~₹2,500/month** in net P&L *after* trading frictions just to break even on infra. On ₹50k starting capital that's a 5%/mo bar. **Assume any backtest claiming this is overfit until proven otherwise** (carry trust rubric forward).

---

## Sources (cited in body)

- AWS EC2 t4g pricing references (T3 for us-east-1; ap-south-1 needs verification on AWS region page): https://www.economize.cloud/resources/aws/pricing/ec2/t4g.medium/ , https://instances.vantage.sh/aws/ec2/t4g.medium , https://aws.amazon.com/ec2/pricing/on-demand/
- Anthropic Claude pricing 2026 (T3): https://platform.claude.com/docs/en/about-claude/pricing , https://www.anthropic.com/news/claude-haiku-4-5 , https://benchlm.ai/blog/posts/claude-api-pricing
- OpenAI pricing 2026 (T3): https://openai.com/api/pricing/ , https://developers.openai.com/api/docs/pricing
- Gemini pricing 2026 (T3): https://ai.google.dev/gemini-api/docs/pricing
- Hetzner Cloud pricing post Apr 2026 increase (T3): https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/ , https://www.hetzner.com/cloud/regular-performance
- Zerodha KiteConnect pricing (T3): https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/what-are-the-charges-for-kite-apis , https://zerodha.com/z-connect/updates/free-personal-apis-from-kite-connect
- Claude Sonnet 4.6 latency benchmark, Apr 2026, 10k requests, 2k in / 500 out (T3): https://tokenmix.ai/blog/ai-api-latency-benchmark , https://artificialanalysis.ai/models/claude-sonnet-4-6/providers
- AWS Mumbai region general perf (T2): https://awsspeedtest.com/regions/ap-south-1 , https://www.cloudping.co/

## Items explicitly marked "needs verification" (T0/T1) — do not let drive a decision
- AWS ap-south-1 *exact* t4g.small / t4g.medium hourly (re-fetch from AWS region selector)
- GCP Mumbai, Azure Central India current 2026 list prices
- Oracle Always Free Mumbai availability + Ampere reclaim policy 2026
- Haiku 4.5 / GPT-4o-mini / Gemini Flash specific TTFT/TPS numbers (artificialanalysis.ai per-model pages)
- Kite REST rate limits exact values 2026
- H100 rental spot pricing 2026 (Lambda, Runpod, Vast)
