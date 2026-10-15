"""G0a — the harness self-test.

A known-overfit synthetic strategy (best of M random walks selected by Sharpe)
must be caught by PBO and refused PASS by the harness. If this test fails,
the harness itself is broken — do not trust any downstream result until fixed.
"""
import numpy as np

from agent_trader.validation import cscv_pbo, validate


def test_g0a_catches_synthetic_overfit():
    rng = np.random.default_rng(42)
    t, m = 1000, 200
    variants = rng.normal(0, 0.01, size=(t, m))

    # Mimic naive backtest selection: pick variant with highest in-sample Sharpe
    # over the full sample. This is the canonical overfit move.
    in_sample_sharpe = variants.mean(axis=0) / variants.std(axis=0, ddof=1)
    best_idx = int(np.argmax(in_sample_sharpe))
    best_returns = variants[:, best_idx]

    # Honest accounting: we tried m variants. DSR must punish this.
    result = validate(
        strategy_returns=best_returns,
        n_trades=80,
        n_trials=m,
        variants_matrix=variants,
    )
    # The harness must NOT pass a best-of-M noise selection at this n_trials.
    # The dominant rejection channel is DSR (multiple-testing correction).
    assert result.verdict == "FAIL", (
        f"harness wrongly PASSed best-of-{m} noise selection: "
        f"reasons={result.reasons} "
        f"dsr={result.dsr.dsr if result.dsr else 'NA'} "
        f"pbo={result.pbo.pbo if result.pbo else 'NA'}"
    )
    assert result.dsr is not None and result.dsr.dsr < 0.95, (
        "DSR should refuse this with high n_trials"
    )


def test_g0a_passes_genuine_edge():
    """Inverse sanity: a strategy with strong, stable edge — tested at honest
    n_trials=3 — should clear all gates. (A small edge tested across many
    trials is correctly rejected; that is *not* a harness bug.)"""
    rng = np.random.default_rng(7)
    t, m = 1500, 3
    variants = rng.normal(0, 0.01, size=(t, m))
    variants[:, 0] += 0.003  # ~0.3% per period, annualised SR ~4.5

    result = validate(
        strategy_returns=variants[:, 0],
        n_trades=120,
        n_trials=m,
        variants_matrix=variants,
    )
    assert result.verdict == "PASS", (
        f"harness wrongly rejected real edge: {result.reasons} "
        f"(dsr={result.dsr.dsr if result.dsr else 'NA'}, "
        f"pbo={result.pbo.pbo if result.pbo else 'NA'})"
    )
