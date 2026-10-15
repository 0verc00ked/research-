"""Gaussian HMM regime classifier (hmmlearn wrapper).

Train on in-sample window; produce posterior state probabilities for any
window using *frozen* parameters (no refit). Adds:
  - deterministic state-label ordering by mean log-return: 0=bear, K-1=bull
  - persistence stat (avg dwell time) for sanity
  - Viterbi most-likely path
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from hmmlearn.hmm import GaussianHMM

from .features import FeatureScaler


@dataclass
class RegimeModel:
    hmm: GaussianHMM
    scaler: FeatureScaler
    label_order: np.ndarray   # permutation that puts states in increasing mean-return order
    n_states: int

    def transform(self, X_raw: np.ndarray) -> np.ndarray:
        return self.scaler.transform(X_raw)

    def posterior(self, X_raw: np.ndarray) -> np.ndarray:
        """Posterior P(state | data) — shape (T, K), labels reordered."""
        X = self.transform(X_raw)
        _, post = self.hmm.score_samples(X)
        return post[:, self.label_order]

    def predict_path(self, X_raw: np.ndarray) -> np.ndarray:
        """Viterbi most-likely state sequence — labels reordered."""
        X = self.transform(X_raw)
        states = self.hmm.predict(X)
        # remap to label_order
        inv = np.argsort(self.label_order)
        return inv[states]

    def dwell_times(self, states: np.ndarray) -> dict[int, float]:
        """Average run length per state — large dwell = persistent regime."""
        out: dict[int, list[int]] = {k: [] for k in range(self.n_states)}
        run = 1
        for i in range(1, len(states)):
            if states[i] == states[i - 1]:
                run += 1
            else:
                out[int(states[i - 1])].append(run)
                run = 1
        out[int(states[-1])].append(run)
        return {k: float(np.mean(v)) if v else 0.0 for k, v in out.items()}


def train(
    X_raw: np.ndarray,
    *,
    n_states: int = 3,
    n_iter: int = 100,
    random_state: int = 42,
) -> RegimeModel:
    """Train HMM on a feature matrix (T, D). Standardises in-sample."""
    from .features import fit_scaler

    scaler = fit_scaler(X_raw)
    X = scaler.transform(X_raw)
    hmm = GaussianHMM(
        n_components=n_states,
        covariance_type="diag",
        n_iter=n_iter,
        random_state=random_state,
        tol=1e-4,
    )
    hmm.fit(X)
    # Order states by mean log_ret (column 0 of features by convention)
    # Lower mean_log_ret = bearish state -> label 0
    mean_ret = hmm.means_[:, 0]
    label_order = np.argsort(mean_ret)
    return RegimeModel(hmm=hmm, scaler=scaler, label_order=label_order, n_states=n_states)
