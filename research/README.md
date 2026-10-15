# Agentic Trading Research — Charter

**Owner:** Nikhil-S (Product Security Engineer, India-based)
**Started:** 2026-05-21
**Goal:** Decide whether a fully autonomous AI agentic trading system is viable for a solo operator in India with **very low starting capital**, and if so, on which market(s) and with what stack.

## Hard constraints
1. **Jurisdiction:** India-resident. Markets must be legally accessible (NSE/BSE/MCX directly; US/global via LRS or GIFT-IFSC; crypto via FIU-registered exchanges; tax must be modelable).
2. **Capital:** Live testing budget is minimal. Research covers all accessible markets, but the live recommendation must be runnable on the smallest practical account.
3. **Practical, not theoretical:** Every recommendation must point to a real broker, real API, real fee schedule, real reproducible test plan.
4. **Honest skepticism:** Most public "AI trading" results are overfit, cherry-picked, or outright fake. Default stance is disbelief until evidence clears the trust bar (see `trust_rubric.md`).

## Phases
- **Phase 1 — Foundations:** Market landscape (India-accessible), agentic trading primer, baseline economics. Output: scored market matrix → pick 2 finalists.
- **Phase 2 — Evidence:** Deep dive on finalists. Real spreads, fills, broker APIs, published agent results + failure analysis.
- **Phase 3 — GitHub mining:** Systematic survey of open-source agentic + algorithmic trading repos. Per-repo dossiers, trust scores, extractable patterns.
- **Phase 4 — Infrastructure:** Hosting, latency budget, LLM inference cost, end-to-end cost model. Honest on what LLM-agents *cannot* do (HFT).
- **Phase 5 — Capital & paper testing:** Minimum-capital paths, paper-trading venues, walk-forward backtesting, overfitting/survivorship/lookahead traps.
- **Phase 6 — Synthesis:** A single decision document with go/no-go, picked market, stack, capital plan, kill-switch criteria.

## Working rules
- Every claim that drives a decision must carry a **trust score** (`trust_rubric.md`).
- Raw fetches are cached under `sources/raw/` with date + URL.
- Phase outputs are markdown, citation-heavy, scored.
- `tracker.md` is the single source of truth for status, open questions, decisions.
- I (the assistant) will flag uncertainty explicitly rather than smoothing it over.

## Two priors carried into the research
1. Most agentic-trading repos lose money after fees; most backtests are overfit. Skeptical by default.
2. LLM-agent edge is on **slow horizons** (news, earnings, sentiment, multi-day positioning), not microstructure. Bias accordingly unless evidence overturns it.

## Out of scope (for now)
- HFT / co-location strategies (incompatible with LLM latency and solo-operator cost).
- Strategies requiring institutional data feeds (CME/NSE colocation, Refinitiv, Bloomberg).
- Anything requiring a SEBI Research Analyst / PMS license.
