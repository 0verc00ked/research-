# Trust Scoring Rubric

Every factual claim in this research carries a score. **No T0/T1 claim is allowed to drive a decision.**

| Score | Meaning | Examples |
|-------|---------|----------|
| **T0** | Unverified / marketing / anecdote | Blog post, Twitter thread, YouTube "I made $X with AI", repo README screenshots |
| **T1** | Single plausible source, not verified | One Medium article, one Reddit comment with reasoning, one StackOverflow answer |
| **T2** | Multiple independent sources agree | 2+ unrelated reputable sources, or vendor docs + independent corroboration |
| **T3** | Primary source / regulator / peer-reviewed | Exchange rulebook, SEBI/RBI circular, broker official fee page, audited research paper, official API docs |
| **T4** | Reproduced by me in this repo | Ran the code, fetched the API, computed the math, saved evidence in `sources/raw/` |

## How to apply
- Cite each fact: `(T3: NSE circular NSE/CMTR/49387, 2024-08)` or `(T1: medium article, weak evidence)`.
- If a fact is load-bearing for a decision and only T0/T1, either upgrade it or hold the decision.
- Conflicting sources → record both, score each, prefer the higher-scored or more recent primary one.
- Re-score on review; trust can decay (stale APIs, expired regulations).

## Red flags that auto-cap at T0
- Backtest with no out-of-sample window.
- P&L screenshots without trade-by-trade logs.
- "AI" repos that don't show losing periods.
- Strategies that "always" work in volatile *and* calm markets.
- Repos with paid Discord / signal-selling funnels attached.
- Anything endorsed by a finfluencer with affiliate links.
