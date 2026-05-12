from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import half_max_contrast
from rh_model import protocols


def _validated_outputs(out: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Figure 4C outputs after checking the declared curve contract.

    Assumption: A-006
    """
    expected = {"attended_CRF", "unattended_CRF", "percent_modulation", "c_pref"}
    assert expected.issubset(out.keys())

    attended = np.asarray(out["attended_CRF"], dtype=float)
    unattended = np.asarray(out["unattended_CRF"], dtype=float)
    percent_modulation = np.asarray(out["percent_modulation"], dtype=float)
    c_pref = np.asarray(out["c_pref"], dtype=float)

    assert attended.ndim == unattended.ndim == percent_modulation.ndim == c_pref.ndim == 1
    assert attended.shape == unattended.shape == percent_modulation.shape == c_pref.shape
    assert attended.size >= 8
    assert np.all(np.isfinite(attended))
    assert np.all(np.isfinite(unattended))
    assert np.all(np.isfinite(percent_modulation))
    assert np.all(np.isfinite(c_pref))
    assert np.all(c_pref > 0.0)
    assert np.all(np.diff(c_pref) > 0.0)
    assert np.allclose(np.diff(np.log(c_pref)), np.diff(np.log(c_pref))[0], rtol=0.15)
    assert np.all(attended >= 0.0)
    assert np.all(unattended > 0.0)

    expected_percent = 100.0 * (attended - unattended) / unattended
    assert np.allclose(percent_modulation, expected_percent, rtol=1e-6, atol=1e-8)
    return attended, unattended, percent_modulation, c_pref


def _max_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the largest finite CRF slope on a log-contrast axis.

    Assumption: A-006
    """
    return float(np.max(np.diff(curve) / np.diff(np.log(contrast))))


def _final_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the final finite CRF slope on a log-contrast axis.

    Assumption: A-006
    """
    return float(np.diff(curve)[-1] / np.diff(np.log(contrast))[-1])


@deterministic_test(spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="Q-025")
def test_figure_4C_output_contract_and_percent_modulation():
    """Figure 4C returns finite CRFs and a consistent percent-modulation curve.

    Citation: C-015
    """
    _validated_outputs(protocols.run_figure_4C())


@deterministic_test(spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="Q-026")
def test_attending_nonpreferred_decreases_response():
    """Attending nonpreferred-in-RF decreases the preferred-stimulus response.

    Citation: C-021
    """
    attended, unattended, percent_modulation, _ = _validated_outputs(protocols.run_figure_4C())

    assert np.all(attended <= unattended + 1e-10)
    assert np.mean(attended <= unattended + 1e-10) >= 0.875
    assert np.all(percent_modulation <= 1e-8)
    assert percent_modulation.min() < -1.0


@deterministic_test(spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="Q-027")
def test_attended_crf_is_right_shifted():
    """Attend-nonpreferred CRF has larger half-max contrast.

    Citation: C-015, C-019, C-021
    """
    attended, unattended, _, c_pref = _validated_outputs(protocols.run_figure_4C())

    attended_half = half_max_contrast(attended, c_pref)
    unattended_half = half_max_contrast(unattended, c_pref)
    assert attended_half > 1.05 * unattended_half
    assert attended[-1] >= 0.80 * unattended[-1]


@deterministic_test(spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="Q-028")
def test_absolute_percent_modulation_does_not_peak_at_highest_contrast():
    """Suppression is largest before the high-contrast endpoint.

    Citation: C-019
    """
    _, _, percent_modulation, _ = _validated_outputs(protocols.run_figure_4C())

    absolute_modulation = np.abs(percent_modulation)
    peak = int(np.argmax(absolute_modulation))
    assert 0 <= peak < len(absolute_modulation) - 1
    assert absolute_modulation[-1] < 0.95 * absolute_modulation[peak]
    assert absolute_modulation[: len(absolute_modulation) // 2].max() >= absolute_modulation[-1]


@deterministic_test(spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="Q-029")
def test_crfs_saturate_and_suppression_weakens_at_high_contrast():
    """Figure 4C CRFs level off and the high-contrast suppressive gap weakens.

    Citation: C-019, C-020
    """
    attended, unattended, _, c_pref = _validated_outputs(protocols.run_figure_4C())

    for curve in (attended, unattended):
        assert curve[-1] > curve[0]
        assert _final_log_slope(curve, c_pref) < 0.95 * _max_log_slope(curve, c_pref)

    normalized_gap = (unattended - attended) / unattended
    assert normalized_gap[-1] < normalized_gap.max()
    assert normalized_gap[-1] <= 1.10 * normalized_gap[-2]
