"""Stage: attention_field.

Contract (model_spec.yaml stages.attention_field):
  consumes:
    attention_condition : {spatial_center: float|None,
                           feature_center: float|None}
    x_grid        : (n_x,)  float   units: arbitrary spatial units
    theta_grid    : (n_th,) float   units: degrees
  produces:
    A             : (n_th, n_x) float   units: dimensionless gain (≥ 1)
  params (ledger):
    <protocol>.attention_field_size       (paper-derived ledger)
    <protocol>.peak_attention_gain_gamma  (C-007/C-012.., paper-derived)
    <protocol>.tuning_width               (feature selectivity, paper-derived)
  citation: C-005, C-009 (EQ-attention)
  assumption: A-004 (sigma convention)

Pure. A = 1 + (γ−1)·G_x·G_θ; flat dimension → Gaussian replaced by 1.
No tunable literals. Wraps the unchanged kernel
``rh_model.model.build_attention_field``.
"""

from __future__ import annotations

import numpy as np

from ..model import DEFAULT_THETA_PERIOD, build_attention_field


def run(
    attention_condition: dict,
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    attention_field_size: float,
    peak_attention_gain_gamma: float,
    feature_tuning_width: float | None = None,
    theta_period: float = DEFAULT_THETA_PERIOD,
) -> np.ndarray:
    """Construct A(x, θ) = 1 + (γ-1) · G_x · G_θ.

    Citation: C-005, C-009 ; Assumption: A-004
    """
    return build_attention_field(
        attention_condition, x_grid, theta_grid, attention_field_size,
        peak_attention_gain_gamma, feature_tuning_width, theta_period,
    )


__all__ = ["run"]
