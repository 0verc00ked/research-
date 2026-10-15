"""Tests for Sequential Validation Calculus (SVC).

Reference: research/phase11_svc/A2_formal_definitions.md
"""
import math
from pathlib import Path

import numpy as np
import pytest

from agent_trader.validation.svc import (
    MDLDSRResult,
    TrialNode,
    TrialTree,
    branching_product,
    compute_K,
    effective_N,
    log2_effective_N,
    mdl_dsr,
)


# ---------------------------------------------------------------------------
# K(s) — MDL code length
# ---------------------------------------------------------------------------

def test_K_increases_with_code_size():
    short = "def f(): return 0"
    longer = "def f():\n    return sum(x*y for x in range(10) for y in range(10))"
    K_short = compute_K(short)
    K_long = compute_K(longer)
    assert K_long > K_short, "more complex code should compress to more bits"


def test_K_stable_under_docstrings():
    """K(s) should not change when only docstrings are added (we strip them)."""
    code_a = "def f():\n    return 42"
    code_b = "def f():\n    '''doc'''\n    return 42"
    assert compute_K(code_a) == compute_K(code_b)


def test_K_continuous_params_add_bits():
    code = "def f(): return 0"
    K_no_params = compute_K(code)
    K_with_params = compute_K(code, continuous_params={"theta": 0.5, "phi": 0.1})
    # precision_bits default = 16, two params → +32 bits
    assert K_with_params == K_no_params + 32


def test_K_baseline_excess():
    """With baseline_bits, K returns the excess over baseline."""
    code = "def f(): return 0"
    K_raw = compute_K(code, baseline_bits=0)
    K_excess = compute_K(code, baseline_bits=K_raw)
    assert K_excess == 0
    K_partial = compute_K(code, baseline_bits=K_raw - 5)
    assert K_partial == 5


# ---------------------------------------------------------------------------
# Trial-tree
# ---------------------------------------------------------------------------

def test_root_node_path(tmp_path: Path):
    tree = TrialTree(tmp_path / "tree.db")
    root_id = tree.record(TrialNode(
        strategy_name="root_hypothesis",
        code_hash="abc",
        code_length=100,
        params={},
        dataset_hash="d",
        nu=1,
    ))
    path = tree.path_to_root(root_id)
    assert len(path) == 1
    assert path[0].parent_id is None
    assert path[0].nu == 1


def test_branching_path(tmp_path: Path):
    tree = TrialTree(tmp_path / "tree.db")
    root_id = tree.record(TrialNode(
        strategy_name="root",
        code_hash="r", code_length=50, params={}, dataset_hash="d", nu=3,
    ))
    child_id = tree.record(TrialNode(
        strategy_name="child",
        code_hash="c", code_length=80, params={}, dataset_hash="d",
        nu=4, parent_id=root_id,
    ))
    grand_id = tree.record(TrialNode(
        strategy_name="grand",
        code_hash="g", code_length=120, params={}, dataset_hash="d",
        nu=2, parent_id=child_id,
    ))
    path = tree.path_to_root(grand_id)
    assert len(path) == 3
    assert [p.strategy_name for p in path] == ["root", "child", "grand"]
    # branching product = 3 * 4 * 2 = 24
    assert branching_product(path) == 24


# ---------------------------------------------------------------------------
# N_eff
# ---------------------------------------------------------------------------

def test_effective_N_simple():
    # Single root node, nu=1, K=10 → N_eff = 1 * 2^10 = 1024
    node = TrialNode(
        strategy_name="s",
        code_hash="h", code_length=10, params={}, dataset_hash="d", nu=1,
    )
    n_eff, n_bp, K = effective_N([node])
    assert n_bp == 1
    assert K == 10
    assert n_eff == 1024


def test_log2_effective_N():
    # Chain: nu=3, nu=4, K=12 → log2(N_eff) = log2(12) + 12
    nodes = [
        TrialNode("a", "h", 0, {}, "d", nu=3),
        TrialNode("b", "h", 12, {}, "d", nu=4),
    ]
    lg = log2_effective_N(nodes)
    assert abs(lg - (math.log2(12) + 12)) < 1e-9


def test_effective_N_overflow_safe():
    # Very large K shouldn't crash log2 path
    nodes = [TrialNode("a", "h", 200, {}, "d", nu=10)]
    lg = log2_effective_N(nodes)
    assert lg > 200  # finite


# ---------------------------------------------------------------------------
# MDL-DSR
# ---------------------------------------------------------------------------

def test_mdl_dsr_punishes_branching_inflation():
    """Same returns, more branching (higher N_bp) → lower MDL-DSR.

    This is the central behavioral test of the framework: at fixed observed
    Sharpe, an adaptive researcher with more branching gets less credit.
    """
    rng = np.random.default_rng(0)
    r = rng.normal(0.001, 0.01, size=500)
    # Light branching (1 root with nu=1)
    light = [TrialNode("s", "h", 30, {}, "d", nu=1)]
    # Heavy branching (root nu=10, then nu=10)
    heavy = [
        TrialNode("a", "h", 0, {}, "d", nu=10),
        TrialNode("b", "h", 30, {}, "d", nu=10),
    ]
    r_light = mdl_dsr(r, path=light)
    r_heavy = mdl_dsr(r, path=heavy)
    assert r_light.mdl_dsr > r_heavy.mdl_dsr, (
        f"heavier branching should reduce MDL-DSR; got light={r_light.mdl_dsr}, "
        f"heavy={r_heavy.mdl_dsr}"
    )


def test_mdl_dsr_punishes_complexity_inflation():
    """Same returns, higher K (more complex strategy) → lower MDL-DSR."""
    rng = np.random.default_rng(1)
    r = rng.normal(0.001, 0.01, size=500)
    simple = [TrialNode("s", "h", 30, {}, "d", nu=1)]
    complex_ = [TrialNode("s", "h", 200, {}, "d", nu=1)]
    r_simple = mdl_dsr(r, path=simple)
    r_complex = mdl_dsr(r, path=complex_)
    assert r_simple.mdl_dsr > r_complex.mdl_dsr


def test_mdl_dsr_accepts_real_edge_at_low_complexity():
    """Strong edge + simple strategy (low K_excess) + no branching → should pass.

    Note: code_length here is *excess bits over baseline*. Real-world
    `compute_K` would use baseline_bits to give the same effective value for
    the project's simplest strategy.
    """
    rng = np.random.default_rng(2)
    r = rng.normal(0.003, 0.01, size=1500)  # annual Sharpe ~4.7
    # K_excess = 5 bits → only ~32 implicit candidates from parameter search
    path = [TrialNode("s", "h", 5, {}, "d", nu=1)]
    result = mdl_dsr(r, path=path)
    assert result.mdl_dsr > 0.95, (
        f"real strong edge with low K_excess should pass; got {result.mdl_dsr}, "
        f"observed Sharpe {result.sharpe_observed}, "
        f"E[max under null] {result.sharpe_expected_max_under_null}"
    )


def test_mdl_dsr_rejects_real_edge_with_huge_implicit_search():
    """Real edge but with extreme branching → MDL-DSR may legitimately reject.

    This is the framework working as designed: even a real edge cannot clear
    the bar if the implicit search space dwarfs the observed evidence.
    """
    rng = np.random.default_rng(3)
    r = rng.normal(0.001, 0.01, size=500)  # Sharpe ~1.6 annual
    # Extreme branching to drive N_eff up
    extreme = [
        TrialNode("a", "h", 0, {}, "d", nu=100),
        TrialNode("b", "h", 100, {}, "d", nu=100),
    ]
    result = mdl_dsr(r, path=extreme)
    assert result.mdl_dsr < 0.95


def test_mdl_dsr_short_data_raises():
    with pytest.raises(ValueError):
        mdl_dsr(np.zeros(10), path=[TrialNode("s", "h", 10, {}, "d")])
