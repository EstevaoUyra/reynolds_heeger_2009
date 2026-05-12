from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import half_max_contrast
from rh_model import protocols


EXPECTED_KEYS = {
    "attended_CRF",
    "unattended_CRF",
    "percent_modulation",
    "absolute_difference",
    "c",
}


def _arrays(out: dict[str, np.ndarray]) -> tuple[np.ndarray, ...]:
    c = np.asarray(out["c"], dtype=float)
    attended = np.asarray(out["attended_CRF"], dtype=float)
    unattended = np.asarray(out["unattended_CRF"], dtype=float)
    percent = np.asarray(out["percent_modulation"], dtype=float)
    difference = np.asarray(out["absolute_difference"], dtype=float)
    return c, attended, unattended, percent, difference


def _assert_monotonic_and_saturating(curve: np.ndarray) -> None:
    increments = np.diff(curve)
    total_rise = float(curve[-1] - curve[0])
    assert np.all(increments >= -1e-10)
    assert total_rise > 0.0
    assert increments[-1] < 0.35 * total_rise


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-014")
def test_protocol_output_contract_and_curve_shapes():
    """Figure 3C returns finite same-shaped log-contrast protocol arrays.

    Citation: C-014
    """
    out = protocols.run_figure_3C()
    assert EXPECTED_KEYS.issubset(out.keys())
    c, attended, unattended, percent, difference = _arrays(out)
    assert c.ndim == 1
    assert attended.shape == unattended.shape == percent.shape == difference.shape == c.shape
    assert len(c) >= 6
    assert np.all(np.isfinite(c))
    assert np.all(np.isfinite(attended))
    assert np.all(np.isfinite(unattended))
    assert np.all(np.isfinite(percent))
    assert np.all(np.isfinite(difference))
    assert np.all(c > 0.0)
    assert np.all(np.diff(c) > 0.0)
    np.testing.assert_allclose(np.diff(np.log(c)), np.diff(np.log(c))[0], rtol=0.08)


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-015")
def test_reported_modulation_and_difference_match_crfs():
    """Figure 3C modulation outputs are derived from attended and unattended CRFs.

    Citation: C-014
    """
    out = protocols.run_figure_3C()
    _, attended, unattended, percent, difference = _arrays(out)
    expected_difference = attended - unattended
    np.testing.assert_allclose(difference, expected_difference, rtol=1e-7, atol=1e-9)
    np.testing.assert_allclose(
        percent,
        100.0 * expected_difference / unattended,
        rtol=1e-7,
        atol=1e-9,
    )


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-016")
def test_attended_and_unattended_crfs_have_baseline_and_saturate():
    """Figure 3C CRFs are positive, monotonic, saturating, and attention ordered.

    Citation: C-020 C-021
    """
    out = protocols.run_figure_3C()
    _, attended, unattended, _, _ = _arrays(out)
    assert attended[0] > 0.0
    assert unattended[0] > 0.0
    assert np.all(attended >= unattended)
    _assert_monotonic_and_saturating(attended)
    _assert_monotonic_and_saturating(unattended)


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-017")
def test_attended_crf_has_lower_half_max_contrast():
    """Figure 3C attended CRF is left-shifted relative to the unattended CRF.

    Citation: C-014
    """
    out = protocols.run_figure_3C()
    c, attended, unattended, _, _ = _arrays(out)
    assert half_max_contrast(attended, c) < half_max_contrast(unattended, c)


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-018")
def test_modulation_is_low_contrast_weighted_and_converges_high():
    """Figure 3C percent modulation peaks low and is small at high contrast.

    Citation: C-014 C-020
    """
    out = protocols.run_figure_3C()
    _, _, _, percent, difference = _arrays(out)
    n = len(percent)
    percent_peak = int(np.argmax(percent))
    difference_peak = int(np.argmax(difference))
    assert percent_peak < n // 2
    assert difference_peak < n - 1
    assert percent[-1] < 0.5 * float(percent[percent_peak])
    assert difference[-1] < 0.75 * float(difference[difference_peak])


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-025")
def test_figure_3c_has_stronger_left_shift_than_3f():
    """Figure 3C has stronger contrast-gain left shift than Figure 3F.

    Citation: C-014 C-019
    """
    out_c = protocols.run_figure_3C()
    out_f = protocols.run_figure_3F()
    c_c, attended_c, unattended_c, percent_c, _ = _arrays(out_c)
    c_f, attended_f, unattended_f, percent_f, _ = _arrays(out_f)
    shift_ratio_c = half_max_contrast(attended_c, c_c) / half_max_contrast(unattended_c, c_c)
    shift_ratio_f = half_max_contrast(attended_f, c_f) / half_max_contrast(unattended_f, c_f)
    assert shift_ratio_c < shift_ratio_f
    assert int(np.argmax(percent_c)) < len(percent_c) // 2
    assert int(np.argmax(percent_f)) < len(percent_f) // 2
