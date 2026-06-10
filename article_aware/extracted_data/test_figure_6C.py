from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import fwhm
from rh_model import protocols


EXPECTED_OUTPUTS = {
    "theta_stim_grid",
    "attend_fixation_tuning",
    "attend_opposite_stimulus_tuning",
}


def _figure_6_arrays() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Authors' native ~1° sweep grid (theta = [-180:180], Figure6C.m). The FWHM /
    # half-height-width helpers below are simple grid-crossing measures (no
    # interpolation), so they are quantized to the sweep spacing: the old default
    # n_directions=25 (~14.8° steps) snaps both curves' half-max crossings to the
    # SAME sample and reports equal widths even though the attend-feature curve is
    # genuinely narrower (peak ratio 1.108, author 'cross' sharpening). The 1° grid
    # resolves the ~13° sharpening. The model curve is resolution-independent; only
    # the width MEASUREMENT needs the authors' native resolution.
    out = protocols.run_figure_6C(n_directions=356)
    assert EXPECTED_OUTPUTS.issubset(out.keys())
    theta = np.asarray(out["theta_stim_grid"], dtype=float)
    fixation = np.asarray(out["attend_fixation_tuning"], dtype=float)
    opposite = np.asarray(out["attend_opposite_stimulus_tuning"], dtype=float)
    return theta, fixation, opposite


def _normalize_shape(curve: np.ndarray) -> np.ndarray:
    curve = np.asarray(curve, dtype=float)
    span = float(curve.max() - curve.min())
    if span <= 0.0:
        return np.zeros_like(curve, dtype=float)
    return (curve - float(curve.min())) / span


def _normalized_half_height_width(curve: np.ndarray, theta: np.ndarray) -> float:
    normalized = _normalize_shape(curve)
    above = np.flatnonzero(normalized >= 0.5)
    if len(above) == 0:
        return 0.0
    return float(theta[int(above[-1])] - theta[int(above[0])])


def _value_near(theta: np.ndarray, curve: np.ndarray, target: float) -> float:
    return float(curve[int(np.argmin(np.abs(theta - float(target))))])


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-037")
def test_protocol_returns_expected_finite_1d_tuning_arrays():
    """Figure 6C returns same-shaped finite 1D direction tuning arrays.

    Citation: C-017
    """
    theta, fixation, opposite = _figure_6_arrays()

    assert theta.ndim == 1
    assert fixation.ndim == 1
    assert opposite.ndim == 1
    assert theta.shape == fixation.shape == opposite.shape
    assert theta.size >= 9
    assert np.all(np.isfinite(theta))
    assert np.all(np.isfinite(fixation))
    assert np.all(np.isfinite(opposite))
    assert np.all(np.diff(theta) > 0.0)
    assert theta[0] < 0.0 < theta[-1]
    assert np.min(np.abs(theta)) <= 15.0
    assert np.all(fixation >= 0.0)
    assert np.all(opposite >= 0.0)


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-038")
def test_tuning_curves_peak_near_preferred_direction_and_drop_at_flanks():
    """Both Figure 6C curves peak near the preferred direction and decline far away.

    Citation: C-017, C-023
    """
    theta, fixation, opposite = _figure_6_arrays()

    fixation_peak_theta = theta[int(np.argmax(fixation))]
    opposite_peak_theta = theta[int(np.argmax(opposite))]
    assert abs(fixation_peak_theta) <= 15.0
    assert abs(opposite_peak_theta) <= 15.0

    center_fixation = _value_near(theta, fixation, 0.0)
    center_opposite = _value_near(theta, opposite, 0.0)
    far_fixation = max(
        _value_near(theta, fixation, -180.0),
        _value_near(theta, fixation, 180.0),
    )
    far_opposite = max(
        _value_near(theta, opposite, -180.0),
        _value_near(theta, opposite, 180.0),
    )
    assert center_fixation > far_fixation
    assert center_opposite > far_opposite


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-039")
def test_attend_opposite_stimulus_tuning_is_narrower_than_fixation_tuning():
    """Feature-based attention narrows the Figure 6C motion-direction tuning curve.

    Citation: C-023
    """
    theta, fixation, opposite = _figure_6_arrays()

    assert fwhm(opposite, theta) < fwhm(fixation, theta)
    assert _normalized_half_height_width(opposite, theta) < _normalized_half_height_width(
        fixation, theta
    )


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-040")
def test_feature_attention_increases_center_to_flank_selectivity():
    """Feature attention increases preferred-direction selectivity over flank responses.

    Citation: C-021, C-023
    """
    theta, fixation, opposite = _figure_6_arrays()

    center_fixation = _value_near(theta, fixation, 0.0)
    center_opposite = _value_near(theta, opposite, 0.0)
    flank_fixation = max(
        _value_near(theta, fixation, -90.0),
        _value_near(theta, fixation, 90.0),
    )
    flank_opposite = max(
        _value_near(theta, opposite, -90.0),
        _value_near(theta, opposite, 90.0),
    )

    assert center_opposite >= center_fixation
    assert flank_opposite <= center_opposite
    assert (center_opposite / max(flank_opposite, 1e-12)) > (
        center_fixation / max(flank_fixation, 1e-12)
    )


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-041")
def test_normalized_attend_opposite_curve_falls_off_more_steeply_near_preferred():
    """Normalized attend-opposite tuning has a steeper near-preferred falloff.

    Citation: C-023
    """
    theta, fixation, opposite = _figure_6_arrays()
    fixation_norm = _normalize_shape(fixation)
    opposite_norm = _normalize_shape(opposite)

    near_offset = 60.0
    fixation_near = max(
        _value_near(theta, fixation_norm, -near_offset),
        _value_near(theta, fixation_norm, near_offset),
    )
    opposite_near = max(
        _value_near(theta, opposite_norm, -near_offset),
        _value_near(theta, opposite_norm, near_offset),
    )

    assert opposite_near < fixation_near
