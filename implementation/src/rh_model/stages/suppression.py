"""Stage: suppression.

Contract (model_spec.yaml stages.suppression):
  consumes:
    s_x       : (n_x,)  float    units: 1/spatial
    s_theta   : (n_th,) float    units: 1/deg
    A         : (n_th, n_x) float  units: dimensionless gain (≥ 1)
    E         : (n_th, n_x) float  units: arbitrary drive (≥ 0)
    dx        : float            units: arbitrary spatial units
    dtheta    : float            units: degrees
  produces:
    S         : (n_th, n_x) float  units: arbitrary drive (≥ 0)
  params (ledger):
    <protocol>.suppressive_drive_gain   (SQ-001, impl ledger — 1D scale)
  citation: C-002, C-006 (EQ-6)
  assumption: A-011 (boundary conditions: zero-padded x, circular θ)

S = s ∗ (A·E), separable. Pure. The 1D-discretization
``suppressive_drive_gain`` is applied by the caller (protocols / the
formalized crf entry point) from the resolved ledger — this stage holds
no tunable literal. Wraps the unchanged kernel
``rh_model.model.compute_suppressive_drive``.
"""

from __future__ import annotations

import numpy as np

from ..model import compute_suppressive_drive


def run(
    s_x: np.ndarray,
    s_theta: np.ndarray,
    A: np.ndarray,
    E: np.ndarray,
    dx: float,
    dtheta: float,
) -> np.ndarray:
    """S(x,θ) = s ∗ (A · E). Zero-padded in x; circular in θ.

    Citation: C-002, C-006 ; Assumption: A-011
    """
    return compute_suppressive_drive(s_x, s_theta, A, E, dx, dtheta)


__all__ = ["run"]
