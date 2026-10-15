# Patterns Extracted Across Phase 3 Repos

Cross-cutting architectural patterns observed. Each is tagged with where it's well-implemented and whether it's worth stealing.

## 1. Multi-agent debate (analyst → debate → judge)
**Seen in:** TradingAgents, AutoHedge (claimed), FinRobot, LangAlpha subagents.
**Best implementation:** TradingAgents (`tradingagents/agents/risk_mgmt/{aggresive,neutral,conservative}_debator.py` → `managers/risk_manager.py`). Three risk persona debators feed a judge node that produces Buy/Sell/Hold.
**Why it works (theoretically):** Forces LLM to articulate counter-arguments; reduces single-prompt overconfidence.
**Why it can fail:** LLMs in debate often converge on the loudest persona; no calibration mechanism for which debator was right historically. Reflection module addresses this partially.
**Worth stealing:** Yes — the structure. Pair with calibration (track each persona's hit rate over time).

## 2. Reflection / memory-aware decisions
**Seen in:** TradingAgents (`graph/reflection.py`, `FinancialSituationMemory`), FinMem (layered memory paper-grade).
**Pattern:** After a trade resolves, the system writes a "lesson" (vector-indexed). Future similar situations retrieve past lessons before deciding.
**FinMem extension:** Short / mid / long memory tiers with decay.
**Worth stealing:** Yes. Critical for any LLM-driven trader that runs >1 day.

## 3. Signal / portfolio / execution / risk separation
**Seen in:** QuantConnect Lean (Algorithm Framework), nautilus_trader (clean module boundaries), AutoHedge (claimed).
**Pattern:** Alpha model → Portfolio construction → Execution model → Risk model, each a swappable component.
**Worth stealing:** Yes — this is the canonical architecture. Bolt the multi-agent debate on top of this skeleton as the Alpha model output.

## 4. Backtest-to-live parity (single Strategy interface)
**Seen in:** freqtrade, jesse, nautilus_trader, Lean.
**Pattern:** One `Strategy` class runs identically in `backtest` / `hyperopt` / `dry-run` / `live`. Eliminates the most common cause of "looked great in backtest, crashed in live."
**Worth stealing:** Mandatory. Any framework lacking this should be disqualified.

## 5. Vectorized parameter sweep + walk-forward
**Seen in:** vectorbt, qlib (`RollingEnsemble`), freqtrade (`hyperopt`).
**Pattern:** Vectorize entries/exits, simulate millions of param combos in seconds, then walk-forward to detect overfitting.
**Caveat:** Lookahead is the user's responsibility. qlib's PIT loader prevents it; vectorbt does not.
**Worth stealing:** Yes for early research; combine with PIT guard before any sizing.

## 6. Broker abstraction layer
**Seen in:** OpenAlgo (30+ Indian brokers under one API), CCXT (crypto), nautilus adapters.
**Pattern:** Strategy emits broker-agnostic orders; adapter translates per venue.
**India-specific value:** OpenAlgo is currently the only credible OSS unified layer for Indian retail brokers.
**Worth stealing:** Use it directly.

## 7. Sandbox / paper mode that exercises the real adapter
**Seen in:** OpenAlgo Sandbox (₹1 Cr fake, exchange-aligned auto-square-off), freqtrade dry-run, Dhan Sandbox (vendor-side).
**Pattern:** Paper mode uses the same adapter code path as live, only the final order send is intercepted.
**Worth stealing:** Yes. Any paper mode that doesn't exercise the live code path is not paper trading.

## 8. Run-card / reproducibility manifest
**Seen in:** Vibe-Trading (`run_card.json` / `run_card.md`), qlib (`recorder`/MLflow), TradingAgents (`results_dir/{ticker}/{date}/`).
**Pattern:** Every backtest emits an immutable manifest: data window, params, code hash, seed, metrics, equity curve. Linked to a hypothesis registry.
**Worth stealing:** Yes — this is the trust-rubric-compatible primitive. Should be required before any T4 score.

## 9. Trading-as-Git (audit-by-commit)
**Seen in:** OpenAlice (TS).
**Pattern:** Orders are staged → committed with message → pushed to execute. Full history reviewable, blame by commit hash, revert via git operations.
**Worth stealing:** Yes — particularly for explainability and incident post-mortems on autonomous systems.

## 10. Programmatic Tool Calling (PTC)
**Seen in:** LangAlpha.
**Pattern:** Instead of LLM writing JSON tool calls that dump raw data into its context, LLM writes Python that calls MCP tools and processes data in a sandbox. Only summaries return to context.
**Why it matters:** Token cost of "LLM-as-trader" is dominated by data dumps. PTC cuts this dramatically.
**Worth stealing:** Yes for any multi-step analysis (factor screens, multi-year aggregations).

## 11. Hypothesis registry + invalidation
**Seen in:** Vibe-Trading (`vibe-trading hypothesis create/invalidate`).
**Pattern:** Each strategy is a hypothesis with explicit status (`active` / `rejected`) and invalidation note. Backtests link to hypotheses.
**Worth stealing:** Yes — combats sunk-cost-fallacy on dead strategies.

## 12. AST purity gate + lookahead guard for factor formulas
**Seen in:** Vibe-Trading Alpha Zoo.
**Pattern:** Factor expressions are parsed, AST-checked for forbidden operations (e.g. future-window references), and run through a synthetic-data lookahead test before being allowed in the zoo.
**Worth stealing:** Yes — directly prevents the #1 backtest fraud cause (look-ahead bias).

---

## Anti-patterns observed (do NOT replicate)
1. **"100% Fully Automated"** language (AI-Trader, AutoHedge).
2. **No license** with high stars (AI-Trader, AM1403x/financial-agent-india).
3. **Affiliate-link funnels in README** (nof1.ai → Gate.io/OKX; jesse → Binance).
4. **Star velocity >> code velocity** (Vibe-Trading: 7.8k★ in 7 weeks for a 2-month-old repo).
5. **Cherry-picked ticker backtests** (FinMem, FinRL) without out-of-sample partition.
6. **"Hedge fund in minutes"** marketing (AutoHedge).
7. **Single Solana / single chain venue** dressed as "universal market access" (AutoHedge).
8. **LLM autonomy without hard guards** (nof1.ai "minimal human intervention").
9. **No paper-mode parity with live adapter** (most "AI trading bot" repos).
10. **SEO-spam keyword-stuffed READMEs** (cluster of Polymarket arbitrage repos).
