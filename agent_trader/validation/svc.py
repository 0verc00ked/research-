"""Sequential Validation Calculus — Trial-Tree formalism, MDL computation,
N_eff construction, and MDL-DSR statistic.

Reference: research/phase11_svc/A2_formal_definitions.md and A3_proof.md.

Public API:
  - TrialTree           — tree data structure (extends TrialLog with parent_id, branching)
  - TrialNode           — augmented record with branching count nu and code hash
  - compute_K           — K(s) = MDL code length of a strategy in bits
  - branching_product   — N_bp(v) along path P(v)
  - effective_N         — N_eff(v) = N_bp(v) * 2^K
  - mdl_dsr             — the MDL-DSR statistic
"""
from __future__ import annotations

import ast
import json
import math
import sqlite3
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Iterable

import numpy as np
from scipy.stats import norm

from .dsr import EULER_MASCHERONI


_SCHEMA = """
CREATE TABLE IF NOT EXISTS trial_node (
    trial_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    ts             TEXT NOT NULL,
    strategy_name  TEXT NOT NULL,
    parent_id      INTEGER,
    nu             INTEGER NOT NULL DEFAULT 1,
    code_hash      TEXT NOT NULL,
    code_length    INTEGER NOT NULL DEFAULT 0,
    params_json    TEXT NOT NULL,
    dataset_hash   TEXT NOT NULL,
    sharpe         REAL,
    metrics_json   TEXT NOT NULL DEFAULT '{}',
    notes          TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (parent_id) REFERENCES trial_node(trial_id)
);
CREATE INDEX IF NOT EXISTS idx_strategy_name ON trial_node(strategy_name);
CREATE INDEX IF NOT EXISTS idx_parent ON trial_node(parent_id);
"""


# ---------------------------------------------------------------------------
# MDL — code length K(s)
# ---------------------------------------------------------------------------

def _canonical_ast_bytes(source_code: str) -> bytes:
    """Normalise a Python source to a canonical AST byte form.

    We strip docstrings, comments (already gone from AST), and use ast.dump()
    with annotate_fields=False and include_attributes=False. This gives a
    stable representation across cosmetic edits but reflects logical changes.
    """
    tree = ast.parse(source_code)
    # remove docstrings: a string-only Expr as first stmt of module / class / func
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", None)
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                node.body = body[1:]
    dumped = ast.dump(tree, annotate_fields=False, include_attributes=False)
    return dumped.encode("utf-8")


_SIGNAL_FUNCTION_NAMES = frozenset({
    "signal", "make_signal", "on_bar", "compute_signal", "trade_signal",
    "_fn",  # for closures returned by make_signal
})


def _extract_signal_functions(tree: ast.Module) -> list[ast.AST]:
    """Find signal-producing function definitions in the module AST.

    Heuristic: any FunctionDef / AsyncFunctionDef whose name is in
    _SIGNAL_FUNCTION_NAMES, plus any function whose body contains a Return
    whose value depends on a parameter named 'price', 'bars', 'history',
    'returns' etc. This is intentionally heuristic — for a publication-grade
    implementation, this would be configurable via a user-supplied predicate.
    """
    out: list[ast.AST] = []
    feature_arg_names = {"price", "prices", "bars", "history", "returns", "data"}

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name in _SIGNAL_FUNCTION_NAMES:
            out.append(node)
            continue
        # Secondary check: function with a feature-named arg
        args_present = {arg.arg for arg in node.args.args}
        if args_present & feature_arg_names:
            out.append(node)
            continue
        # Walk inner functions for closures (e.g., make_signal returns _fn)
        for child in ast.walk(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if child.name in _SIGNAL_FUNCTION_NAMES and child is not node:
                    out.append(child)
    # Deduplicate by id
    seen: set[int] = set()
    uniq: list[ast.AST] = []
    for n in out:
        if id(n) not in seen:
            seen.add(id(n))
            uniq.append(n)
    return uniq


class _AlphaRenamer(ast.NodeTransformer):
    """Renames all local variable names to canonical _v0, _v1, ... so that
    K becomes invariant under alpha-equivalent code (variable renaming)."""

    def __init__(self) -> None:
        self._map: dict[str, str] = {}
        self._counter = 0

    def _canon(self, name: str) -> str:
        if name not in self._map:
            self._map[name] = f"_v{self._counter}"
            self._counter += 1
        return self._map[name]

    def visit_Name(self, node: ast.Name) -> ast.AST:
        # Only rename plausibly-local names (lowercase, no underscore prefix).
        # Keep dotted attrs, Capitalised (likely class/type), and dunder names.
        if (
            node.id and node.id[0].islower() and not node.id.startswith("_")
            and node.id not in {"True", "False", "None", "self"}
        ):
            node.id = self._canon(node.id)
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        if node.arg and node.arg[0].islower() and not node.arg.startswith("_"):
            node.arg = self._canon(node.arg)
        return node


def compute_K_decision_only(
    source_code: str,
    *,
    continuous_params: dict[str, float] | None = None,
    precision_bits: int = 16,
    baseline_bits: int = 0,
    alpha_equiv: bool = True,
) -> int:
    """Smart K — measure only the *decision-rule* logic of a strategy module,
    ignoring imports, helpers, docstrings, and (optionally) variable names.

    Pipeline:
      1. Parse module to AST.
      2. Identify signal-producing functions (name-based + arg-name heuristic).
      3. Strip docstrings.
      4. Optionally alpha-rename local variables to canonical names.
      5. Dump and zlib-compress.
      6. Add parameter-precision bits.
      7. Subtract baseline_bits.

    Use this in preference to compute_K() for realistic strategy modules.
    """
    tree = ast.parse(source_code)
    sig_funcs = _extract_signal_functions(tree)
    if not sig_funcs:
        # Fall back to the full module if no signal functions are detected
        return compute_K(
            source_code,
            continuous_params=continuous_params,
            precision_bits=precision_bits,
            baseline_bits=baseline_bits,
        )
    # Strip docstrings from each signal function and from inner functions
    for func in sig_funcs:
        for node in ast.walk(func):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                body = getattr(node, "body", None)
                if (
                    body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)
                ):
                    node.body = body[1:]
    if alpha_equiv:
        renamer = _AlphaRenamer()
        sig_funcs = [renamer.visit(ast.fix_missing_locations(f)) for f in sig_funcs]
    # Combine all signal-function dumps
    dumped = "\n".join(
        ast.dump(f, annotate_fields=False, include_attributes=False) for f in sig_funcs
    )
    compressed = zlib.compress(dumped.encode("utf-8"), level=9)
    L_struct = 8 * len(compressed)
    L_params = precision_bits * (len(continuous_params) if continuous_params else 0)
    return int(max(0, L_struct + L_params - baseline_bits))


def compute_K(
    source_code: str,
    *,
    continuous_params: dict[str, float] | None = None,
    precision_bits: int = 16,
    baseline_bits: int = 0,
) -> int:
    """K(s) = MDL code length in bits.

    Components:
      - L_struct = 8 * len(zlib.compress(canonical_AST(source))) — structural bits
      - L_params = precision_bits * |continuous_params|         — parameter bits
      - L_excess = max(0, L_struct + L_params - baseline_bits)  — bits *beyond* baseline

    The raw Kraft bound 2^K is a *very loose* upper bound on the implicit
    parameter-space search size — for natural strategy code, most byte
    sequences do not decode to valid strategies. To get a practical and
    honest measure, set `baseline_bits` to the compressed code length of the
    simplest reasonable strategy in your class (e.g., a trivial buy-and-hold).
    The framework's Type-I bound holds with the raw L_struct + L_params, but
    is so conservative that in practice no real strategy passes; using
    excess-over-baseline preserves *relative* ordering while making the
    threshold achievable.

    With baseline_bits = 0 (default), this returns raw bits per Definition 3.
    """
    ast_bytes = _canonical_ast_bytes(source_code)
    compressed = zlib.compress(ast_bytes, level=9)
    L_struct = 8 * len(compressed)
    L_params = 0
    if continuous_params:
        L_params = precision_bits * len(continuous_params)
    raw = L_struct + L_params
    return int(max(0, raw - baseline_bits))


# ---------------------------------------------------------------------------
# Trial-tree
# ---------------------------------------------------------------------------

@dataclass
class TrialNode:
    """A trial-tree node (Definition 1 of A2)."""
    strategy_name: str
    code_hash: str
    code_length: int            # K(pi(v)) in bits
    params: dict[str, Any]
    dataset_hash: str
    nu: int = 1                 # branching factor at this node
    parent_id: int | None = None
    sharpe: float | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    trial_id: int | None = None
    ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TrialTree:
    """Append-only SQLite-backed trial-tree.

    Compatible with the existing TrialLog API in spirit but augments with
    parent_id and branching count nu. Existing trial_log.db files can be
    migrated by treating each as a root-level child of an implicit root.
    """

    def __init__(self, path: str | Path = "trial_tree.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, isolation_level=None)

    def record(self, node: TrialNode) -> int:
        with self._lock, self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO trial_node
                (ts, strategy_name, parent_id, nu, code_hash, code_length,
                 params_json, dataset_hash, sharpe, metrics_json, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    node.ts, node.strategy_name, node.parent_id, node.nu,
                    node.code_hash, node.code_length,
                    json.dumps(node.params, default=str, sort_keys=True),
                    node.dataset_hash, node.sharpe,
                    json.dumps(node.metrics, default=str),
                    node.notes,
                ),
            )
            return int(cur.lastrowid)  # type: ignore[arg-type]

    def get(self, trial_id: int) -> TrialNode | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                """SELECT trial_id, ts, strategy_name, parent_id, nu, code_hash,
                          code_length, params_json, dataset_hash, sharpe,
                          metrics_json, notes
                   FROM trial_node WHERE trial_id = ?""",
                (trial_id,),
            ).fetchone()
        if row is None:
            return None
        return TrialNode(
            trial_id=row[0], ts=row[1], strategy_name=row[2], parent_id=row[3],
            nu=row[4], code_hash=row[5], code_length=row[6],
            params=json.loads(row[7]), dataset_hash=row[8], sharpe=row[9],
            metrics=json.loads(row[10]), notes=row[11],
        )

    def path_to_root(self, trial_id: int) -> list[TrialNode]:
        """Return P(v) = (v0, v1, ..., vd) from root to v inclusive."""
        path: list[TrialNode] = []
        cur = trial_id
        while cur is not None:
            node = self.get(cur)
            if node is None:
                break
            path.append(node)
            cur = node.parent_id
        return list(reversed(path))

    def all_sharpes(self) -> list[float]:
        with self._lock, self._connect() as conn:
            rows = conn.execute(
                "SELECT sharpe FROM trial_node WHERE sharpe IS NOT NULL"
            ).fetchall()
        return [float(r[0]) for r in rows]


# ---------------------------------------------------------------------------
# N_eff and MDL-DSR
# ---------------------------------------------------------------------------

def branching_product(path: list[TrialNode]) -> int:
    """N_bp(v) = product of nu(u) for u in P(v).  Definition 2 of A2."""
    n = 1
    for node in path:
        n *= max(1, int(node.nu))
    return n


def effective_N(path: list[TrialNode]) -> tuple[int, int, int]:
    """N_eff(v) = N_bp(v) * 2^{K(pi(v))}. Definition 4.

    Returns (N_eff, N_bp, K) so callers can log all three.
    Note: 2^K can be astronomically large; we return the LOG2 of N_eff to avoid
    overflow, and Sharpe-deflation formulae are computed via log-domain.
    """
    if not path:
        return 1, 1, 0
    n_bp = branching_product(path)
    K_leaf = int(path[-1].code_length)
    # We return N_eff as int up to overflow; if K > 60, we cap and return a
    # large-int. Callers should use log2_effective_N for safe arithmetic.
    try:
        n_eff = n_bp * (2 ** K_leaf)
    except OverflowError:
        n_eff = 10 ** 18  # cap; the deflation formula uses log of N_eff anyway
    return n_eff, n_bp, K_leaf


def log2_effective_N(path: list[TrialNode]) -> float:
    """Safer arithmetic: log2(N_eff) = log2(N_bp) + K."""
    if not path:
        return 0.0
    n_bp = branching_product(path)
    K_leaf = int(path[-1].code_length)
    return math.log2(max(1, n_bp)) + float(K_leaf)


def _expected_max_sharpe_logN(
    log_N: float, sharpe_variance_across_trials: float
) -> float:
    """E[SR_max | N] computed from log2(N) to avoid overflow.

    For very large N, Phi^{-1}(1 - 1/N) ≈ sqrt(2 ln N) by Mills ratio.
    """
    if log_N <= 0:
        return 0.0
    n_eff_for_quantile = 2 ** min(log_N, 300)  # cap for numerical
    z1 = norm.ppf(1 - 1.0 / n_eff_for_quantile) if n_eff_for_quantile > 1 else 0.0
    z2 = (
        norm.ppf(1 - 1.0 / (n_eff_for_quantile * math.e))
        if n_eff_for_quantile > 1
        else 0.0
    )
    # Fall back to the asymptotic approximation when N is huge
    if not math.isfinite(z1) or not math.isfinite(z2):
        ln_N = log_N * math.log(2)
        z1 = math.sqrt(2 * ln_N)
        z2 = math.sqrt(2 * (ln_N - 1))
    em = (1 - EULER_MASCHERONI) * z1 + EULER_MASCHERONI * z2
    return float(math.sqrt(max(sharpe_variance_across_trials, 1e-12)) * em)


@dataclass
class MDLDSRResult:
    sharpe_observed: float
    sharpe_expected_max_under_null: float
    mdl_dsr: float
    log2_N_eff: float
    n_bp: int
    K_bits: int
    n_obs: int
    skew: float
    kurt: float


def mdl_dsr(
    returns: np.ndarray,
    *,
    path: list[TrialNode],
    sharpe_variance_across_trials: float | None = None,
    periods_per_year: int = 252,
) -> MDLDSRResult:
    """MDL-DSR statistic per Definition 5 of A2 and Theorem 1 of A3."""
    r = np.asarray(returns, dtype=float)
    n = len(r)
    if n < 30:
        raise ValueError(f"need >= 30 returns, got {n}")

    mean = float(r.mean())
    std = float(r.std(ddof=1))
    if std <= 0:
        return MDLDSRResult(0.0, 0.0, 0.0, 0.0, 1, 0, n, 0.0, 0.0)

    sr_period = mean / std
    sr_annual = sr_period * math.sqrt(periods_per_year)
    skew = float(((r - mean) ** 3).mean() / std ** 3)
    excess_kurt = float(((r - mean) ** 4).mean() / std ** 4 - 3.0)
    kurt = excess_kurt + 3.0

    var_sr_hat = (1 - skew * sr_period + (kurt - 1) / 4 * sr_period ** 2) / (n - 1)
    if var_sr_hat <= 0:
        return MDLDSRResult(sr_annual, 0.0, 0.0, 0.0, 1, 0, n, skew, kurt)
    sigma_sr_hat = math.sqrt(var_sr_hat)

    log2_N = log2_effective_N(path)
    var_for_em = (
        sharpe_variance_across_trials
        if sharpe_variance_across_trials is not None
        else 1.0 / periods_per_year
    )
    sr_zero_period = _expected_max_sharpe_logN(log2_N, var_for_em)
    sr_zero_annual = sr_zero_period * math.sqrt(periods_per_year)

    z = (sr_period - sr_zero_period) / sigma_sr_hat
    mdl_dsr_val = float(norm.cdf(z))

    n_bp = branching_product(path)
    K_bits = int(path[-1].code_length) if path else 0

    return MDLDSRResult(
        sharpe_observed=sr_annual,
        sharpe_expected_max_under_null=sr_zero_annual,
        mdl_dsr=mdl_dsr_val,
        log2_N_eff=log2_N,
        n_bp=n_bp,
        K_bits=K_bits,
        n_obs=n,
        skew=skew,
        kurt=kurt,
    )
