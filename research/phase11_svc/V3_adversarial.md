# V3 — Adversarial Researcher Battery

Date: 2026-05-22

**Setup:** τ=500, α=0.05, 1500 sims per scenario.

Each scenario simulates a researcher behavior that may violate SVC's assumptions (A1 honest data-splitting, A4 honest branching report). All underlying strategies are null. SVC's empirical Type-I tells us whether the framework is **robust** (controls Type-I despite violation) or **vulnerable** (Type-I exceeds α — researcher fooled SVC).

## Results

| Scenario | True K | Reported ν | Peeks | SVC Type-I | Verdict |
|---|---:|---:|---:|---:|---|
| A1 Honest (true K=50, reports 50) | 50 | 50 | 1 | 0.0000 | ✅ ROBUST |
| A2 Under-reporter ×2 (true 50, reports 25) | 50 | 25 | 1 | 0.0000 | ✅ ROBUST |
| A3 Under-reporter ×10 (true 50, reports 5) | 50 | 5 | 1 | 0.0193 | ✅ ROBUST |
| A4 Lone-strategy lie (true 50, reports 1) | 50 | 1 | 1 | 0.9227 | ❌ VULNERABLE |
| A5 HARK (true 100, reports 1) | 100 | 1 | 1 | 0.9927 | ❌ VULNERABLE |
| A6 Repeated peeking (true 50 × 5 peeks) | 50 | 50 | 5 | 0.0000 | ✅ ROBUST |
| A7 Pruning (true 200, reports 50 'kept') | 200 | 50 | 1 | 0.0000 | ✅ ROBUST |
| A8 Smart adversary (under-report + peek) | 50 | 10 | 5 | 0.0173 | ✅ ROBUST |

## Interpretation

- **ROBUST** verdicts mean SVC's Type-I held below α + 2% even though the researcher violated assumptions. This is *unexpectedly good* behavior — the framework happens to self-correct in these cases.
- **VULNERABLE** verdicts mean SVC was *fooled* by the violation. This is the honest limit: the framework provably works only under (A1)–(A4). It cannot survive every dishonest researcher — no statistical framework can.

**Implications for users:**
1. SVC requires honest reporting of ν. Under-reporting of branching factors *will* inflate Type-I beyond α. There's no automatic fix.
2. SVC requires train/test isolation. Repeated peeking *will* inflate Type-I.
3. The framework should be paired with research-process safeguards (pre-registration, version-controlled research logs, audit trails) to mitigate adversarial behavior.