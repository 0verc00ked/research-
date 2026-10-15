"""W5-6 demo — show the allocator behaving on three contrived worlds.

This is integration-sanity, not a unit test. Read alongside
tests/test_allocator_g0c.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_trader.portfolio import Allocator, AllocatorConfig  # noqa: E402


def _print_snapshot(label: str, a: Allocator, capital: float) -> None:
    snap = a.allocate(capital)
    print(f"\n  {label}  (steps={a.steps})")
    print(f"    posterior μ_n = {snap.posterior.mu_n:.6f}  "
          f"E[σ²] = {snap.posterior.expected_sigma_sq:.6f}  "
          f"shrinkage = {snap.posterior.shrinkage_factor:.3f}")
    print(f"    total exposure = {snap.total_exposure:.4f}")
    for name, cap in snap.per_strategy_capital.items():
        i = a.cfg.strategy_names.index(name)
        print(f"    {name}: weight={snap.weights[i]:.3f}  capital=₹{cap:,.0f}")


def world_one_edge():
    print("=== World A: one strategy with real edge, four pure noise ===")
    rng = np.random.default_rng(2026)
    cfg = AllocatorConfig(
        strategy_names=["edge", "n1", "n2", "n3", "n4"],
        bound_b=0.05, t_hint=252,
        kelly_frac=0.1, max_total_exposure=0.5,
    )
    a = Allocator(cfg)
    capital = 100_000.0
    pnl_total = 0.0

    for t in range(252):
        snap = a.allocate(capital)
        r = rng.normal(0, 0.01, size=5).clip(-0.05, 0.05)
        r[0] += 0.003
        pnl = float(np.dot(snap.per_strategy_fraction, r)) * capital
        capital += pnl
        pnl_total += pnl
        a.observe({n: float(r[i]) for i, n in enumerate(cfg.strategy_names)})

    _print_snapshot("after T=252", a, capital)
    print(f"    final capital = ₹{capital:,.0f}  (P&L ₹{pnl_total:,.0f})")
    print(f"    empirical regret (raw return units): {a.exp.empirical_regret():.4f}")
    print(f"    theoretical regret bound: {a.exp.theoretical_regret_bound():.4f}")


def world_all_noise():
    print("\n=== World B: every strategy is pure noise (no edge) ===")
    rng = np.random.default_rng(7)
    cfg = AllocatorConfig(
        strategy_names=[f"s{i}" for i in range(4)],
        bound_b=0.05, t_hint=252,
        kelly_frac=0.1, max_total_exposure=0.5,
    )
    a = Allocator(cfg)
    capital = 100_000.0

    for _ in range(252):
        snap = a.allocate(capital)
        r = rng.normal(0, 0.01, size=4).clip(-0.05, 0.05)
        pnl = float(np.dot(snap.per_strategy_fraction, r)) * capital
        capital += pnl
        a.observe({f"s{i}": float(r[i]) for i in range(4)})

    _print_snapshot("after T=252", a, capital)
    print(f"    final capital = ₹{capital:,.0f}")
    print("    expectation: total exposure stays small; no ruin")


def world_one_clear_loser():
    print("\n=== World C: 1 small-edge strategy + 1 clear loser ===")
    rng = np.random.default_rng(13)
    cfg = AllocatorConfig(
        strategy_names=["edge", "loser"],
        bound_b=0.05, t_hint=252,
        kelly_frac=0.1, max_total_exposure=0.5,
    )
    a = Allocator(cfg)
    capital = 100_000.0

    for _ in range(252):
        snap = a.allocate(capital)
        r_e = float(np.clip(rng.normal(0.0015, 0.01), -0.05, 0.05))
        r_l = float(np.clip(rng.normal(-0.002, 0.01), -0.05, 0.05))
        pnl = float(snap.per_strategy_fraction[0] * r_e + snap.per_strategy_fraction[1] * r_l) * capital
        capital += pnl
        a.observe({"edge": r_e, "loser": r_l})

    _print_snapshot("after T=252", a, capital)
    print(f"    final capital = ₹{capital:,.0f}")
    print("    expectation: loser → near-zero weight, edge → dominant")


if __name__ == "__main__":
    world_one_edge()
    world_all_noise()
    world_one_clear_loser()
