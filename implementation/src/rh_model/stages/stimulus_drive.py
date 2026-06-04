"""Stage: stimulus_drive.

Contract (model_spec.yaml stages.stimulus_drive):
  consumes:
    stimuli       : list[{x: float, theta: float, contrast: float}]
                    units: x arbitrary spatial; theta deg; contrast [0,1]
    x_grid        : (n_x,)  float   units: arbitrary spatial units
    theta_grid    : (n_th,) float   units: degrees
  produces:
    E             : (n_th, n_x) float   units: arbitrary drive (≥ 0)
  params (ledger):
    <protocol>.stimulus_size   (C-013..C-018, paper-derived ledger)
    <protocol>.tuning_width    (C-011/C-015/C-017/C-018, paper-derived)
  citation: C-009 (EQ-stim)
  assumption: A-009 (form of stimulus drive)

Pure. Sum of per-stimulus Gaussian contributions. No tunable literals —
the spatial/feature widths come from the resolved ledger. Wraps the
unchanged kernel ``rh_model.model.build_stimulus_drive``.
"""

from __future__ import annotations

import numpy as np

from ..model import DEFAULT_THETA_PERIOD, build_stimulus_drive


def run(
    stimuli: list[dict],
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    stimulus_size: float,
    tuning_width: float,
    theta_period: float = DEFAULT_THETA_PERIOD,
    stimulation_field_size: float = 5.0,
    stimulation_tuning_width: float = 60.0,
) -> np.ndarray:
    """Construct Eraw = conv2sepYcirc(stim, ExKernel, EthetaKernel).

    Citation: C-009 ; Code: CODE-012, CODE-013, CODE-019 ; Assumption: A-009
    """
    return build_stimulus_drive(
        stimuli, x_grid, theta_grid, stimulus_size, tuning_width, theta_period,
        stimulation_field_size, stimulation_tuning_width,
    )


__all__ = ["run"]
