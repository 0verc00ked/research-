"""G0c — allocator self-test.

Per CONCRETE_PLAN.md §4 (Weeks 5-6):
  - Cumulative regret ≤ theoretical bound at T=252, K=5
  - Bayesian posterior shrunken to ≤30% of MLE at n=30
  - No allocation can exceed max_exposure regardless of posterior mean

Plus integration sanity:
  - On a 5-strategy world with one true-edge variant + 4 noise, the true
    edge ends with the highest Hedge weight
  - Total exposure ramps up only as the ensemble accumulates evidence
  - Losing strategies get vanishing allocation
"""
import numpy as np

from agent_trader.portfolio import (
    Allocator,
    AllocatorConfig,
    NIGPrior,
    update_posterior,
)


def test_g0c_regret_bound_t252_k5():
    rng = np.random.default_rng(123)
    cfg = AllocatorConfig(
        strategy_names=[f"s{i}" for i in range(5)],
        t_hint=252,
        bound_b=0.05,
    )
    a = Allocator(cfg)
    for _ in range(252):
        r = rng.normal(0, 0.01, size=5).clip(-0.05, 0.05)
        a.allocate(capital=100_000.0)
        a.observe({f"s{i}": float(r[i]) for i in range(5)})
    reg = a.exp.empirical_regret()
    bound = a.exp.theoretical_regret_bound()
    assert reg <= bound + 1e-9, f"regret {reg:.4f} exceeds bound {bound:.4f}"


def test_g0c_bayes_shrinkage_at_30():
    rng = np.random.default_rng(0)
    r = rng.normal(0.01, 0.01, size=30)
    post = update_posterior(NIGPrior(), r)
    assert post.shrinkage_factor < 0.3, (
        f"posterior should be shrunk >70% at n=30; got shrinkage={post.shrinkage_factor}"
    )


def test_g0c_exposure_cap_holds_under_extreme_mu():
    """Even if every ensemble return is +5%, total exposure cannot exceed
    max_total_exposure."""
    cfg = AllocatorConfig(
        strategy_names=["a", "b"],
        max_total_exposure=0.5,
        kelly_frac=0.1,
    )
    a = Allocator(cfg)
    for _ in range(300):
        a.allocate(capital=100_000.0)
        a.observe({"a": 0.05, "b": 0.05})
    snap = a.allocate(capital=100_000.0)
    assert snap.total_exposure <= 0.5 + 1e-9


def test_g0c_winner_wins_weight_at_t252():
    rng = np.random.default_rng(7)
    cfg = AllocatorConfig(
        strategy_names=["edge", "noise1", "noise2", "noise3", "noise4"],
        t_hint=252,
        bound_b=0.05,
    )
    a = Allocator(cfg)
    for _ in range(252):
        r = rng.normal(0, 0.01, size=5).clip(-0.05, 0.05)
        r[0] += 0.003
        a.allocate(capital=100_000.0)
        a.observe({n: float(r[i]) for i, n in enumerate(cfg.strategy_names)})
    snap = a.allocate(capital=100_000.0)
    assert snap.weights[0] == snap.weights.max(), (
        f"edge variant should be heaviest at t=252; got {snap.weights}"
    )
    assert snap.weights[0] > 0.25, "winner should clearly exceed uniform 0.20"


def test_g0c_loser_allocation_vanishes():
    rng = np.random.default_rng(9)
    cfg = AllocatorConfig(
        strategy_names=["edge", "loser"],
        t_hint=252,
        bound_b=0.05,
        kelly_frac=0.1,
        max_total_exposure=0.5,
    )
    a = Allocator(cfg)
    for _ in range(252):
        r_edge = float(rng.normal(0.003, 0.01))
        r_loser = float(rng.normal(-0.002, 0.01))
        a.allocate(capital=100_000.0)
        a.observe({"edge": r_edge, "loser": r_loser})
    snap = a.allocate(capital=100_000.0)
    assert snap.per_strategy_capital["loser"] < snap.per_strategy_capital["edge"]
    assert snap.per_strategy_capital["loser"] / max(snap.per_strategy_capital["edge"], 1e-9) < 0.5


def test_g0c_no_deployment_without_data():
    """With zero observations the posterior is the prior; μ_n = 0; Kelly
    long-only returns 0; total exposure should be 0."""
    cfg = AllocatorConfig(strategy_names=["a", "b", "c"])
    a = Allocator(cfg)
    snap = a.allocate(capital=100_000.0)
    assert snap.total_exposure == 0.0
    for v in snap.per_strategy_capital.values():
        assert v == 0.0


def test_g0c_no_ruin_in_1000_days():
    """Run the full allocator with iid noise for 1000 days. Capital should
    never go to zero or negative (sanity for the bounded-ruin property)."""
    rng = np.random.default_rng(2026)
    cfg = AllocatorConfig(
        strategy_names=[f"s{i}" for i in range(4)],
        kelly_frac=0.1,
        max_total_exposure=0.5,
    )
    a = Allocator(cfg)
    capital = 100_000.0
    min_capital = capital
    for _ in range(1000):
        snap = a.allocate(capital=capital)
        # realise next-day returns
        r = rng.normal(0, 0.01, size=4).clip(-0.05, 0.05)
        # P&L = Σ per_strategy_capital_i * r_i
        pnl = float(np.dot(snap.per_strategy_fraction, r)) * capital
        capital += pnl
        min_capital = min(min_capital, capital)
        a.observe({f"s{i}": float(r[i]) for i in range(4)})
    assert capital > 0, f"ruin: capital={capital}"
    assert min_capital > 50_000, f"draw-down breached 50% floor: min={min_capital}"
