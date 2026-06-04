"""Stage: suppression.

Contract (model_spec.yaml stages.suppression):
  consumes:
    s_x       : (n_x,)  float    units: 1/spatial (unit-volume kernel)
    s_theta   : (n_th,) float    units: 1/deg     (unit-volume kernel)
    A         : (n_th, n_x) float  units: dimensionless gain (≥ 1)
    E         : (n_th, n_x) float  units: arbitrary drive (≥ 0)
  produces:
    S         : (n_th, n_x) float  units: arbitrary drive (≥ 0)
  params (ledger):
    model.suppressive_field_size    (C-010/CODE-010, paper-derived ledger)
    model.suppressive_tuning_width  (CODE-011, near-flat θ pool)
  citation: C-002, C-006 (EQ-6)
  code: CODE-001, CODE-002, CODE-003 (conv2sepYcirc; no per-panel gain)
  assumption: A-011 (boundary conditions: zero-padded x, circular θ)

S = conv2sepYcirc(A·E, s_x, s_theta), separable. Pure. Plain discrete
convolution with the unit-volume suppressive kernels — NO per-panel
``suppressive_drive_gain`` (retired, SQ-005/A-013) and no integral ·dx/·dθ
factor. Wraps ``rh_model.model.compute_suppressive_drive``.
"""

from __future__ import annotations

import numpy as np

from ..model import compute_suppressive_drive


def run(
    s_x: np.ndarray,
    s_theta: np.ndarray,
    A: np.ndarray,
    E: np.ndarray,
) -> np.ndarray:
    """S(x,θ) = conv2sepYcirc(A · E, s_x, s_theta). Zero-padded in x; circular in θ.

    Citation: C-002, C-006 ; Code: CODE-001, CODE-002 ; Assumption: A-011
    """
    return compute_suppressive_drive(s_x, s_theta, A, E)


__all__ = ["run"]
