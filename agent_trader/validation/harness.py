"""Single `validate()` entrypoint that runs every G0 gate and returns a
structured pass/fail.

Gate thresholds tracked in `research/SYNTHESIS.md` §6:
  - PBO   ≤ 0.5  (hard);  ≤ 0.2 (soft)
  - DSR   ≥ 0.95
  - CPCV  ≥ 0.6 folds positive (soft floor)
  - Regime: profitable in ≥1 post-LLM-cutoff window
  - N_trades ≥ 50
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .cpcv import CPCVResult, combinatorial_purged_cv
from .dsr import DSRResult, deflated_sharpe_ratio
from .pbo import PBOResult, cscv_pbo


@dataclass
class GateResult:
    verdict: str  # "PASS" | "FAIL" | "INCONCLUSIVE"
    reasons: list[str] = field(default_factory=list)
    pbo: PBOResult | None = None
    dsr: DSRResult | None = None
    cpcv: CPCVResult | None = None
    n_trades: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def metrics(self) -> dict[str, Any]:
        out: dict[str, Any] = {"n_trades": self.n_trades}
        if self.dsr is not None:
            out["sharpe_observed"] = self.dsr.sharpe_observed
        return out

    @property
    def gates(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if self.pbo is not None:
            out["pbo"] = self.pbo.pbo
        if self.dsr is not None:
            out["dsr"] = self.dsr.dsr
        if self.cpcv is not None:
            out["cpcv_folds_positive"] = self.cpcv.folds_positive_ratio
        return out


def validate(
    *,
    strategy_returns: np.ndarray,
    n_trades: int,
    n_trials: int,
    variants_matrix: np.ndarray | None = None,
    label_horizon: int = 1,
    pbo_hard_max: float = 0.5,
    dsr_min: float = 0.95,
    cpcv_folds_positive_min: float = 0.6,
    n_trades_min: int = 50,
) -> GateResult:
    """Run all gates.

    Args:
        strategy_returns: shape (T,) of the candidate strategy's per-bar returns
        n_trades: actual number of round-trip trades
        n_trials: honestly-counted trial number for this strategy family
                  (from TrialLog.n_trials_for(...))
        variants_matrix: shape (T, M) — per-bar returns of every parameter
                         variant tested. Required for PBO. If None, PBO is
                         skipped and the result is INCONCLUSIVE.
    """
    reasons: list[str] = []
    pbo_res = None
    dsr_res = None
    cpcv_res = None

    if n_trades < n_trades_min:
        reasons.append(f"n_trades {n_trades} < min {n_trades_min}")

    try:
        dsr_res = deflated_sharpe_ratio(strategy_returns, n_trials=n_trials)
        if dsr_res.dsr < dsr_min:
            reasons.append(f"DSR {dsr_res.dsr:.3f} < {dsr_min}")
    except ValueError as e:
        reasons.append(f"DSR error: {e}")

    try:
        cpcv_res = combinatorial_purged_cv(
            strategy_returns, label_horizon=label_horizon
        )
        if cpcv_res.folds_positive_ratio < cpcv_folds_positive_min:
            reasons.append(
                f"CPCV folds positive {cpcv_res.folds_positive_ratio:.2f} "
                f"< {cpcv_folds_positive_min}"
            )
    except ValueError as e:
        reasons.append(f"CPCV error: {e}")

    if variants_matrix is None:
        reasons.append("PBO skipped: no variants_matrix provided")
        verdict = "INCONCLUSIVE"
    else:
        try:
            pbo_res = cscv_pbo(variants_matrix)
            if pbo_res.pbo > pbo_hard_max:
                reasons.append(f"PBO {pbo_res.pbo:.3f} > hard max {pbo_hard_max}")
        except ValueError as e:
            reasons.append(f"PBO error: {e}")
        verdict = "PASS" if not reasons else "FAIL"

    return GateResult(
        verdict=verdict,
        reasons=reasons,
        pbo=pbo_res,
        dsr=dsr_res,
        cpcv=cpcv_res,
        n_trades=n_trades,
    )
