"""Stage: readout.

Contract (model_spec.yaml stages.readout):
  consumes:
    R          : (n_th, n_x) float  units: arbitrary response (≥ 0)
    x_grid     : (n_x,)  float      units: arbitrary spatial units
    theta_grid : (n_th,) float      units: degrees
    recorded_x : float              units: arbitrary spatial units
    recorded_theta : float          units: degrees
  produces:
    response   : float              units: arbitrary response (≥ 0)
  params (ledger):
    figure_1.recorded_x  (A-006, impl ledger — Figure-1 readout position)
  citation: C-005, C-012
  assumption: A-006 (1D reduction; recorded-neuron coordinates)

Pure. Reads R at the recorded neuron's coordinates (nearest grid sample).
No tunable literals — the recorded coordinates come from the protocol /
ledger. Mirrors the readout step inside ``rh_model.model.simulate``.
"""

from __future__ import annotations

import numpy as np


def run(
    R: np.ndarray,
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    recorded_x: float,
    recorded_theta: float,
) -> float:
    """Read R(x, θ) at the recorded neuron's coordinates.

    Citation: C-005, C-012 ; Assumption: A-006
    """
    i = int(np.argmin(np.abs(x_grid - recorded_x)))
    j = int(np.argmin(np.abs(theta_grid - recorded_theta)))
    return float(R[j, i])


__all__ = ["run"]
