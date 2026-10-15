# portfolio/

Bounded-ruin online-learning allocator. Composes:

- **ExpWeights** (Hedge / exponentiated-weights) — produces convex weights p_t carrying a √(T·ln K) regret bound on the cumulative weighted return vs best-in-hindsight.
- **Bayesian Kelly** on ensemble returns — produces total fractional exposure with a skeptical Normal-Inverse-Gamma prior. At n=30 trades, the posterior μ is shrunk to ≤30% of MLE; overfit backtests cannot scale into capital.
- **Hard cap** at `max_total_exposure` (default 0.5) and Kelly fraction at `kelly_frac` (default 0.1 = Kelly/10) — multiple layers of ruin avoidance.

## Decomposition

```
per_strategy_capital_fraction_i  =  p_t^i  ·  total_exposure_t
                                    │         │
                                    │         └── Bayesian Kelly on ensemble
                                    │             (skeptical NIG, fractional Kelly,
                                    │              capped)
                                    │
                                    └── Hedge convex weights
                                        (regret ≤ B·√(2T·ln K))
```

## Mathematical guarantees (what we claim)

1. **Hedge:** Σ_t Σ_i p_t^i · r_t^i ≥ max_i Σ_t r_t^i − B·√(2T·ln K) for returns in [-B, B]. Verified empirically in `test_exp_weights.py::test_regret_bound_holds_empirically` and `test_allocator_g0c.py::test_g0c_regret_bound_t252_k5`.
2. **Shrinkage:** at n=30, posterior μ is at most 30% of the MLE (κ₀=100 prior). Verified in `test_bayesian_sizing.py::test_shrinkage_30_obs`.
3. **Exposure cap:** total deployed fraction ≤ `max_total_exposure`. Verified in `test_allocator_g0c.py::test_g0c_exposure_cap_holds_under_extreme_mu`.
4. **Bounded ruin:** zero deployment when posterior μ ≤ 0 (long-only). Verified in `test_allocator_g0c.py::test_g0c_no_deployment_without_data` and `test_g0c_no_ruin_in_1000_days`.

## Mathematical guarantees (what we do NOT claim)

- The Hedge regret bound does **not** transfer to `per_strategy_capital_fraction_i = p_t^i · total_exposure_t`. The Kelly multiplier breaks the clean guarantee. The bound is on the split (Hedge output), not on the total deployment.
- Per-strategy Bayesian sizing is **not** done. We size the *ensemble*, not individual strategies. Strategy quality is arbitrated by Hedge weights.
- No guarantee under non-stationary returns. Real markets shift regimes; the bound assumes the [-B, B] range holds.

## Usage

```python
from agent_trader.portfolio import Allocator, AllocatorConfig, NIGPrior

cfg = AllocatorConfig(
    strategy_names=["s1", "s2", "s3"],
    bound_b=0.05,         # max realistic |return| per period
    t_hint=252,           # for default Hedge eta
    kelly_frac=0.1,       # Kelly/10
    max_total_exposure=0.5,
    long_only=True,
)
a = Allocator(cfg)

# Each period:
snap = a.allocate(capital=15_000.0)
# snap.per_strategy_capital is dict[name -> rupee allocation]
# snap.weights, snap.total_exposure available for logging

# After observing realised returns:
a.observe({"s1": 0.012, "s2": -0.004, "s3": 0.001})
```

## Operational notes

- **Re-evaluate `bound_b` if your strategy has fat tails.** B=0.05 = 5% per day. NIFTY weekly options can be much fatter. If true range > B, Hedge gains saturate (loses adaptivity) but bound still holds.
- **`warmup_floor` in ExpWeights** keeps losing strategies at a minimum weight so a strategy that becomes good after a long bad streak is recoverable. Defaults to 1e-3.
- **Tuning κ₀:** smaller = more responsive to recent data, but more vulnerable to overfit. 100 is the project default; 50 is more aggressive, 200 is more conservative. Don't tune this on results — that's overfitting the harness too.

## G0c gate

`tests/test_allocator_g0c.py` is the G0c gate. If it fails after any change to this package, do not promote any code that depends on the allocator until it's fixed.
