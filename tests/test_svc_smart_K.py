"""Tests for the smart (decision-rule-only) K extractor.

The key invariants:
  - K invariant to imports (decoration of strategy modules)
  - K invariant to docstrings
  - K invariant to variable renaming (alpha-equivalence)
  - K invariant to helper functions not used by the signal
  - K monotone in the actual decision-rule complexity
"""
import textwrap

from agent_trader.validation import compute_K, compute_K_decision_only


# Two strategies with the SAME decision logic but different surface forms

_STRATEGY_PLAIN = textwrap.dedent("""
def signal(price, threshold):
    if price[-1] > threshold:
        return 1
    return -1
""")

_STRATEGY_DECORATED = textwrap.dedent("""
'''A trading strategy module.

This module implements a threshold-crossing signal. Used by the project
since 2025. See docs/strategy_notes.md for the underlying mechanism.
'''
import numpy as np
import pandas as pd
from typing import Sequence


# A bunch of unused helper code that should NOT affect K
def helper_unused_1(x):
    '''An unused helper.'''
    return x ** 2 + 2 * x + 1


def helper_unused_2(a, b, c):
    '''Another unused helper.'''
    return (a + b) * c - sum([1, 2, 3])


class _UnusedConfig:
    '''Unused dataclass-style config.'''
    field_a: int = 0
    field_b: float = 1.0


def signal(price, threshold):
    '''Threshold-crossing signal: +1 above, -1 below.

    Parameters
    ----------
    price : Sequence[float]
    threshold : float

    Returns
    -------
    int : +1 or -1
    '''
    if price[-1] > threshold:
        return 1
    return -1
""")

_STRATEGY_RENAMED = textwrap.dedent("""
def signal(p, t):
    if p[-1] > t:
        return 1
    return -1
""")

# A genuinely different decision rule
_STRATEGY_DIFFERENT = textwrap.dedent("""
def signal(price, threshold):
    if price[-1] > threshold and price[-2] > price[-3]:
        return 1
    if price[-1] < threshold * 0.95:
        return -1
    return 0
""")


def test_naive_K_inflated_by_boilerplate():
    K_plain = compute_K(_STRATEGY_PLAIN)
    K_decorated = compute_K(_STRATEGY_DECORATED)
    assert K_decorated > K_plain * 2, (
        f"naive K should be inflated by imports/docstrings/helpers; "
        f"got plain={K_plain}, decorated={K_decorated}"
    )


def test_smart_K_invariant_to_boilerplate():
    K_plain = compute_K_decision_only(_STRATEGY_PLAIN)
    K_decorated = compute_K_decision_only(_STRATEGY_DECORATED)
    # Smart K should be roughly equal (within a small tolerance for AST diffs)
    ratio = K_decorated / max(K_plain, 1)
    assert 0.85 <= ratio <= 1.15, (
        f"smart K should be invariant to boilerplate; "
        f"got plain={K_plain}, decorated={K_decorated}, ratio={ratio:.2f}"
    )


def test_smart_K_invariant_to_renaming():
    K_full = compute_K_decision_only(_STRATEGY_PLAIN, alpha_equiv=True)
    K_short = compute_K_decision_only(_STRATEGY_RENAMED, alpha_equiv=True)
    assert K_full == K_short, (
        f"alpha-equivalent strategies should have equal K under alpha_equiv=True; "
        f"got {K_full} vs {K_short}"
    )


def test_smart_K_distinguishes_decision_complexity():
    K_simple = compute_K_decision_only(_STRATEGY_PLAIN)
    K_complex = compute_K_decision_only(_STRATEGY_DIFFERENT)
    assert K_complex > K_simple, (
        f"more complex decision rule should have larger smart K; "
        f"got simple={K_simple}, complex={K_complex}"
    )


def test_smart_K_with_real_project_strategy():
    """Run smart K on the project's actual s1 strategy file.

    The naive K reported in the case study was 5120 bits (excess over a
    trivial baseline). Smart K should be FAR smaller because it ignores
    the imports, dataclass boilerplate, and grid generator.
    """
    from pathlib import Path
    src = Path("strategies/s1_thursday_reversion/signal.py").read_text()
    K_naive = compute_K(src)
    K_smart = compute_K_decision_only(src)
    print(f"\n  s1 naive K = {K_naive}, smart K = {K_smart}")
    # Smart K should be smaller — exact ratio depends on how much of the
    # file is boilerplate (imports, dataclass for params, grid generator)
    # vs core decision logic. For s1 the signal function itself is
    # substantial (stateful closure with held_remaining), so we expect
    # a moderate reduction (~30-50%), not extreme.
    assert K_smart < K_naive, (
        f"smart K should be smaller than naive K; got naive={K_naive}, smart={K_smart}"
    )
    reduction = 1 - K_smart / K_naive
    assert reduction >= 0.25, (
        f"smart K should reduce by at least 25%; got {reduction:.1%}"
    )
