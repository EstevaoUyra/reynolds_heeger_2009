"""Stage: suppressive_kernel.

Contract (model_spec.yaml stages.suppressive_kernel):
  consumes:
    x_grid        : (n_x,)  float   units: arbitrary spatial units
    theta_grid    : (n_th,) float   units: degrees
  produces:
    s_x           : (n_x,)  float   units: 1/spatial (integrates to 1 in x)
    s_theta       : (n_th,) float   units: 1/deg     (integrates to 1 in θ)
  params (ledger):
    model.suppressive_field_size      (C-010, paper-derived ledger)
    model.suppressive_tuning_width    (C-011, paper-derived ledger)
    figure_4C.suppressive_tuning_width (SQ-004, impl ledger — per-protocol)
  citation: C-002, C-009, C-011 (EQ-suppressive_kernel)
  assumption: A-004 (sigma convention), A-011 (periodic in θ)

Pure. Constant per simulation (does not depend on stimulus or attention).
Holds no tunable literals — the effective spatial/tuning widths are passed
in by the caller from the resolved ledger. Wraps the unchanged kernel
``rh_model.model.build_suppressive_kernel``.
"""

from __future__ import annotations

import numpy as np

from ..model import DEFAULT_THETA_PERIOD, build_suppressive_kernel


def run(
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    suppressive_field_size: float,
    suppressive_tuning_width: float,
    theta_period: float = DEFAULT_THETA_PERIOD,
) -> tuple[np.ndarray, np.ndarray]:
    """Build the separable suppressive kernel (s_x, s_theta).

    Citation: C-002, C-009, C-011 ; Assumption: A-004, A-011
    """
    return build_suppressive_kernel(
        x_grid, theta_grid, suppressive_field_size, suppressive_tuning_width,
        theta_period,
    )


__all__ = ["run"]
