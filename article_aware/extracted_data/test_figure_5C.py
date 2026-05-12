from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import fwhm
from rh_model import protocols


EXPECTED_OUTPUTS = {"theta_0_grid", "attended_tuning", "unattended_tuning", "ratio"}


def _figure_5c_outputs() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Figure 5C protocol arrays as float vectors.

    Citation: C-016, C-022
    """
    out = protocols.run_figure_5C()
    assert EXPECTED_OUTPUTS.issubset(out.keys())
    theta = np.asarray(out["theta_0_grid"], dtype=float)
    attended = np.asarray(out["attended_tuning"], dtype=float)
    unattended = np.asarray(out["unattended_tuning"], dtype=float)
    ratio = np.asarray(out["ratio"], dtype=float)
    return theta, attended, unattended, ratio


def _assert_single_peak_near_zero(theta: np.ndarray, curve: np.ndarray) -> int:
    """Assert broad qualitative geometry of an orientation tuning curve.

    Citation: C-016, C-022
    """
    peak_idx = int(np.argmax(curve))
    step = float(np.median(np.diff(theta)))
    assert abs(float(theta[peak_idx])) <= max(10.0, 1.5 * step)
    assert np.all(np.diff(curve[: peak_idx + 1]) >= -1e-9)
    assert np.all(np.diff(curve[peak_idx:]) <= 1e-9)
    return peak_idx


def _normalized(curve: np.ndarray) -> np.ndarray:
    """Normalize a positive tuning curve by its peak for shape comparison.

    Assumption: A-006
    """
    peak = float(np.max(curve))
    assert peak > 0.0
    return curve / peak


def _assert_approximately_symmetric(theta: np.ndarray, curve: np.ndarray) -> None:
    """Assert approximate left/right symmetry around preferred orientation.

    Citation: C-016, C-022
    """
    positive_theta = theta[theta >= 0.0]
    max_mirrored_theta = min(abs(float(theta[0])), abs(float(theta[-1])))
    positive_theta = positive_theta[positive_theta <= max_mirrored_theta]
    normalized = _normalized(curve)
    right = np.interp(positive_theta, theta, normalized)
    left = np.interp(-positive_theta, theta, normalized)
    response_bearing = np.maximum(left, right) > 0.02
    assert np.count_nonzero(response_bearing) >= 3
    np.testing.assert_allclose(
        left[response_bearing],
        right[response_bearing],
        rtol=0.1,
        atol=0.03,
    )


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-033")
def test_figure_5c_output_contract_and_ratio_consistency():
    """Figure 5C returns finite same-shaped arrays and a computed gain ratio.

    Citation: C-016, C-022
    """
    theta, attended, unattended, ratio = _figure_5c_outputs()
    assert theta.ndim == attended.ndim == unattended.ndim == ratio.ndim == 1
    assert theta.size >= 9
    assert theta.shape == attended.shape == unattended.shape == ratio.shape
    assert np.all(np.isfinite(theta))
    assert np.all(np.isfinite(attended))
    assert np.all(np.isfinite(unattended))
    assert np.all(np.isfinite(ratio))
    assert np.all(np.diff(theta) > 0.0)
    assert theta[0] < 0.0 < theta[-1]
    assert np.min(np.abs(theta)) <= max(5.0, 0.6 * float(np.median(np.diff(theta))))

    positive = unattended > 1e-12
    assert np.any(positive)
    np.testing.assert_allclose(ratio[positive], attended[positive] / unattended[positive])


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-034")
def test_attended_tuning_exceeds_unattended():
    """Attended tuning is at least unattended tuning at every orientation.

    Citation: C-021, C-022
    """
    _, attended, unattended, _ = _figure_5c_outputs()
    assert np.all(attended >= unattended - 1e-12)
    assert np.max(attended - unattended) > 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-035")
def test_tuning_curves_are_nonnegative_single_peaked_and_preferred_at_zero():
    """Both tuning curves are nonnegative and peak near preferred orientation.

    Citation: C-016, C-022
    """
    theta, attended, unattended, _ = _figure_5c_outputs()
    assert np.all(attended >= -1e-12)
    assert np.all(unattended >= -1e-12)
    attended_peak = _assert_single_peak_near_zero(theta, attended)
    unattended_peak = _assert_single_peak_near_zero(theta, unattended)
    assert attended_peak == unattended_peak
    _assert_approximately_symmetric(theta, attended)
    _assert_approximately_symmetric(theta, unattended)


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-036")
def test_tuning_ratio_is_approximately_constant():
    """Spatial attention scales tuning without changing shape.

    Citation: C-022
    """
    theta, attended, unattended, ratio = _figure_5c_outputs()
    response_bearing = unattended > 0.05 * float(np.max(unattended))
    assert np.count_nonzero(response_bearing) >= 3
    assert np.all(ratio[response_bearing] > 1.0)
    assert float(np.max(ratio[response_bearing]) / np.min(ratio[response_bearing])) < 1.25

    center_idx = int(np.argmin(np.abs(theta)))
    bearing_indices = np.flatnonzero(response_bearing)
    flank_ratios = ratio[[int(bearing_indices[0]), int(bearing_indices[-1])]]
    np.testing.assert_allclose(flank_ratios, ratio[center_idx], rtol=0.2, atol=0.0)
    np.testing.assert_allclose(
        ratio[response_bearing],
        attended[response_bearing] / unattended[response_bearing],
    )


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-037")
def test_normalized_tuning_shape_is_preserved():
    """Peak-normalized attended and unattended tuning curves have the same shape.

    Citation: C-022
    """
    _, attended, unattended, _ = _figure_5c_outputs()
    attended_norm = _normalized(attended)
    unattended_norm = _normalized(unattended)
    assert float(np.corrcoef(attended_norm, unattended_norm)[0, 1]) > 0.995
    np.testing.assert_allclose(attended_norm, unattended_norm, rtol=0.08, atol=0.04)


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-038")
def test_fwhm_is_approximately_equal():
    """Tuning width is approximately equal with and without attention.

    Citation: C-022
    """
    theta, attended, unattended, _ = _figure_5c_outputs()
    attended_width = fwhm(attended, theta)
    unattended_width = fwhm(unattended, theta)
    assert unattended_width > 0.0
    assert abs(attended_width - unattended_width) / unattended_width < 0.15
