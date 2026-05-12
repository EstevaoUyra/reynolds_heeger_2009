from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import half_max_contrast, value_at
from rh_model import protocols


def _validated_outputs(out: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Figure 2 outputs after checking the shared curve contract.

    Assumption: A-006
    """
    expected = {"attended_CRF", "unattended_CRF", "percent_modulation", "c"}
    assert expected.issubset(out.keys())

    attended = np.asarray(out["attended_CRF"], dtype=float)
    unattended = np.asarray(out["unattended_CRF"], dtype=float)
    percent_modulation = np.asarray(out["percent_modulation"], dtype=float)
    contrast = np.asarray(out["c"], dtype=float)

    assert attended.ndim == unattended.ndim == percent_modulation.ndim == contrast.ndim == 1
    assert attended.shape == unattended.shape == percent_modulation.shape == contrast.shape
    assert attended.size >= 8
    assert np.all(np.isfinite(attended))
    assert np.all(np.isfinite(unattended))
    assert np.all(np.isfinite(percent_modulation))
    assert np.all(np.isfinite(contrast))
    assert np.all(contrast > 0.0)
    assert np.all(np.diff(contrast) > 0.0)
    assert np.all(np.diff(np.log(contrast)) > 0.0)
    assert np.allclose(np.diff(np.log(contrast)), np.diff(np.log(contrast))[0], rtol=0.15)
    assert np.all(unattended > 0.0)
    expected_pm = 100.0 * (attended - unattended) / unattended
    assert np.allclose(percent_modulation, expected_pm, rtol=1e-6, atol=1e-8)
    return attended, unattended, percent_modulation, contrast


def _response_scale(*curves: np.ndarray) -> float:
    """Return a robust shared vertical scale for CRF comparisons.

    Assumption: A-006
    """
    stacked = np.concatenate([np.asarray(curve, dtype=float) for curve in curves])
    return float(stacked.max() - stacked.min())


def _max_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the largest finite slope on the log-contrast axis.

    Assumption: A-006
    """
    return float(np.max(np.diff(curve) / np.diff(np.log(contrast))))


def _final_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the final finite slope on the log-contrast axis.

    Assumption: A-006
    """
    return float(np.diff(curve)[-1] / np.diff(np.log(contrast))[-1])


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-004")
def test_figure_2A_output_contract_and_percent_modulation():
    """Figure 2A returns finite CRF arrays on a log-contrast grid.

    Citation: C-013
    """
    _validated_outputs(protocols.run_figure_2A())


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-005")
def test_figure_2A_crfs_are_monotonic_and_saturating():
    """Both Figure 2A contrast-response functions rise monotonically and level off.

    Citation: C-003, C-020
    """
    attended, unattended, _, contrast = _validated_outputs(protocols.run_figure_2A())

    for curve in (attended, unattended):
        assert np.all(np.diff(curve) >= -1e-10)
        assert curve[-1] > curve[0]
        assert _final_log_slope(curve, contrast) < 0.95 * _max_log_slope(curve, contrast)
        at_half_contrast = value_at(contrast, curve, 0.5)
        assert (curve[-1] - at_half_contrast) / at_half_contrast < 0.35


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-006")
def test_figure_2A_attended_curve_is_left_shifted_without_response_gain():
    """The attended Figure 2A CRF reaches half-max at lower contrast.

    Citation: C-007, C-019, C-021
    """
    attended, unattended, _, contrast = _validated_outputs(protocols.run_figure_2A())

    assert np.all(attended >= unattended - 1e-10)
    attended_half = half_max_contrast(attended, contrast)
    unattended_half = half_max_contrast(unattended, contrast)
    assert attended_half < 0.80 * unattended_half

    scale = _response_scale(attended, unattended)
    final_separation = attended[-1] - unattended[-1]
    peak_separation = np.max(attended - unattended)
    assert final_separation < 0.25 * scale
    assert final_separation < 0.95 * peak_separation
    assert attended[-1] < 1.35 * unattended[-1]


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-007")
def test_figure_2A_percent_modulation_peaks_then_falls_at_high_contrast():
    """Figure 2A percent modulation peaks before the high-contrast endpoint and declines.

    Citation: C-019
    """
    attended, unattended, percent_modulation, contrast = _validated_outputs(protocols.run_figure_2A())

    peak = int(np.argmax(percent_modulation))
    attended_half = half_max_contrast(attended, contrast)
    assert 0 < peak < len(percent_modulation) - 2
    assert contrast[peak] <= 1.25 * attended_half
    assert percent_modulation[-1] < 0.40 * percent_modulation[peak]
    assert percent_modulation[-1] < percent_modulation[0]

    rising_mask = contrast <= half_max_contrast(unattended, contrast)
    assert percent_modulation[rising_mask].mean() > 1.6 * percent_modulation[-2:].mean()


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-014")
def test_figure_2A_has_stronger_left_shift_than_figure_2B():
    """The lateral attended-vs-unattended shift is larger in 2A than in 2B.

    Citation: C-007, C-008, C-019
    """
    attended_a, unattended_a, _, contrast_a = _validated_outputs(protocols.run_figure_2A())
    attended_b, unattended_b, _, contrast_b = _validated_outputs(protocols.run_figure_2B())

    shift_ratio_a = half_max_contrast(attended_a, contrast_a) / half_max_contrast(
        unattended_a, contrast_a
    )
    shift_ratio_b = half_max_contrast(attended_b, contrast_b) / half_max_contrast(
        unattended_b, contrast_b
    )
    assert shift_ratio_a < 0.90 * shift_ratio_b


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-016")
def test_figure_2A_modulation_falls_more_than_figure_2B():
    """Figure 2A modulation falls farther from peak to high contrast than 2B.

    Citation: C-019
    """
    _, _, percent_a, _ = _validated_outputs(protocols.run_figure_2A())
    _, _, percent_b, _ = _validated_outputs(protocols.run_figure_2B())

    final_fraction_a = percent_a[-1] / percent_a.max()
    final_fraction_b = percent_b[-1] / percent_b.max()
    absolute_drop_a = percent_a.max() - percent_a[-1]
    absolute_drop_b = percent_b.max() - percent_b[-1]

    assert final_fraction_a < 0.75 * final_fraction_b
    assert absolute_drop_a > absolute_drop_b
