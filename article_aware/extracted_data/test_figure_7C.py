from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols


EXPECTED_OUTPUTS = {
    "theta_var_grid",
    "fixation_tuning",
    "attend_nonpref_tuning",
    "attend_variable_tuning",
}


def _figure_7c_arrays() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Figure 7C protocol arrays after checking the output contract.

    Citation: C-018
    """
    out = protocols.run_figure_7C()
    assert EXPECTED_OUTPUTS.issubset(out.keys())
    theta = np.asarray(out["theta_var_grid"], dtype=float)
    fixation = np.asarray(out["fixation_tuning"], dtype=float)
    attend_nonpref = np.asarray(out["attend_nonpref_tuning"], dtype=float)
    attend_variable = np.asarray(out["attend_variable_tuning"], dtype=float)
    return theta, fixation, attend_nonpref, attend_variable


def _nearest_value(theta: np.ndarray, curve: np.ndarray, target: float) -> float:
    """Return the curve value at the grid sample nearest a target direction.

    Assumption: A-006
    """
    return float(curve[int(np.argmin(np.abs(theta - float(target))))])


def _window_mean(theta: np.ndarray, curve: np.ndarray, center: float, radius: float) -> float:
    """Mean response in a direction window on the protocol grid.

    Assumption: A-006
    """
    mask = np.abs(theta - float(center)) <= float(radius)
    assert np.any(mask)
    return float(np.mean(curve[mask]))


def _nonpreferred_mean(theta: np.ndarray, curve: np.ndarray, radius: float = 45.0) -> float:
    """Mean response near the two nonpreferred ends of the direction sweep.

    Citation: C-018
    """
    mask = np.abs(np.abs(theta) - 180.0) <= float(radius)
    assert np.any(mask)
    return float(np.mean(curve[mask]))


def _preferred_bias(theta: np.ndarray, curve: np.ndarray) -> float:
    """Preferred-center response relative to nonpreferred-side response.

    Citation: C-018
    """
    return _window_mean(theta, curve, 0.0, 30.0) - _nonpreferred_mean(theta, curve)


def _direction_changes(curve: np.ndarray) -> int:
    """Count substantial sign changes in the discrete slope of a tuning curve.

    Assumption: A-006
    """
    dynamic_range = float(np.ptp(curve))
    if dynamic_range == 0.0:
        return 0
    slope = np.diff(curve)
    substantial = np.abs(slope) > 0.02 * dynamic_range
    signs = np.sign(slope[substantial])
    if len(signs) < 2:
        return 0
    return int(np.count_nonzero(signs[1:] != signs[:-1]))


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-041")
def test_protocol_outputs_are_finite_direction_tuning_curves():
    """Figure 7C returns finite, non-negative tuning curves over direction.

    Citation: C-001, C-018
    """
    theta, fixation, attend_nonpref, attend_variable = _figure_7c_arrays()
    curves = (fixation, attend_nonpref, attend_variable)

    assert theta.ndim == 1
    assert len(theta) >= 17
    assert np.all(np.diff(theta) > 0.0)
    assert float(theta[0]) <= -150.0
    assert float(theta[-1]) >= 150.0
    assert np.min(np.abs(theta)) <= 15.0

    for curve in curves:
        assert curve.ndim == 1
        assert curve.shape == theta.shape
        assert np.all(np.isfinite(curve))
        assert np.all(curve >= 0.0)


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-042")
def test_preferred_direction_ordering_matches_attention_target():
    """Near the preferred direction, variable attention exceeds fixation and nonpreferred attention suppresses it.

    Citation: C-018, C-021
    """
    theta, fixation, attend_nonpref, attend_variable = _figure_7c_arrays()
    fixation_pref = _nearest_value(theta, fixation, 0.0)
    nonpref_pref = _nearest_value(theta, attend_nonpref, 0.0)
    variable_pref = _nearest_value(theta, attend_variable, 0.0)

    assert variable_pref > fixation_pref > nonpref_pref
    assert variable_pref > nonpref_pref


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-043")
def test_attention_effects_have_opposite_signs_around_preferred_flanks():
    """Variable attention raises, and nonpreferred attention lowers, most central-flank responses.

    Citation: C-018, C-021
    """
    theta, fixation, attend_nonpref, attend_variable = _figure_7c_arrays()
    central_flank = (np.abs(theta) <= 60.0) & (np.abs(theta) >= 15.0)
    assert np.count_nonzero(central_flank) >= 4

    variable_delta = attend_variable[central_flank] - fixation[central_flank]
    nonpref_delta = attend_nonpref[central_flank] - fixation[central_flank]
    assert np.mean(variable_delta > 0.0) >= 0.75
    assert np.mean(nonpref_delta < 0.0) >= 0.75
    assert float(np.mean(variable_delta)) > 0.0
    assert float(np.mean(nonpref_delta)) < 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-044")
def test_attention_conditions_shift_preferred_bias_oppositely():
    """Attending the variable stimulus increases preferred bias, while attending nonpreferred decreases it.

    Citation: C-018, C-021
    """
    theta, fixation, attend_nonpref, attend_variable = _figure_7c_arrays()
    fixation_bias = _preferred_bias(theta, fixation)
    nonpref_bias = _preferred_bias(theta, attend_nonpref)
    variable_bias = _preferred_bias(theta, attend_variable)

    assert variable_bias > fixation_bias > nonpref_bias
    assert (variable_bias - fixation_bias) > 0.0
    assert (nonpref_bias - fixation_bias) < 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-045")
def test_attend_variable_has_larger_peak_than_attend_nonpreferred():
    """The attend-variable curve has the largest preferred-direction peak and the nonpreferred curve the smallest.

    Citation: C-018, C-021
    """
    theta, fixation, attend_nonpref, attend_variable = _figure_7c_arrays()
    for curve in (fixation, attend_nonpref, attend_variable):
        peak_theta = float(theta[int(np.argmax(curve))])
        assert abs(peak_theta) <= 45.0

    assert float(np.max(attend_variable)) > float(np.max(fixation))
    assert float(np.max(fixation)) > float(np.max(attend_nonpref))
    assert _nearest_value(theta, attend_nonpref, 0.0) < _nearest_value(theta, fixation, 0.0)


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-046")
def test_tuning_curves_are_single_peaked_and_not_pathologically_jagged():
    """All three Figure 7C curves rise to a central peak and remain smooth on the sampled grid.

    Citation: C-018
    """
    theta, fixation, attend_nonpref, attend_variable = _figure_7c_arrays()
    for curve in (fixation, attend_nonpref, attend_variable):
        preferred = _window_mean(theta, curve, 0.0, 30.0)
        nonpreferred = _nonpreferred_mean(theta, curve)
        assert preferred > nonpreferred
        assert float(np.ptp(curve)) > 0.0
        assert _direction_changes(curve) <= 2
