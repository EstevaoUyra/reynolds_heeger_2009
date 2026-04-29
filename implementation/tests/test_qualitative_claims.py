from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols


def half_max_contrast(response: np.ndarray, contrast: np.ndarray) -> float:
    response = np.asarray(response, dtype=float)
    contrast = np.asarray(contrast, dtype=float)
    target = 0.5 * response.max()
    above = np.flatnonzero(response >= target)
    if len(above) == 0:
        return float("nan")
    idx = int(above[0])
    if idx == 0:
        return float(contrast[0])
    c0, c1 = np.log(contrast[idx - 1]), np.log(contrast[idx])
    r0, r1 = response[idx - 1], response[idx]
    if r1 == r0:
        return float(contrast[idx])
    t = (target - r0) / (r1 - r0)
    return float(np.exp(c0 + t * (c1 - c0)))


def value_at(x_grid: np.ndarray, values: np.ndarray, target: float) -> float:
    return float(np.interp(target, np.asarray(x_grid, dtype=float), np.asarray(values, dtype=float)))


def fwhm(response: np.ndarray, theta: np.ndarray) -> float:
    response = np.asarray(response, dtype=float)
    theta = np.asarray(theta, dtype=float)
    above = np.flatnonzero(response >= 0.5 * response.max())
    if len(above) == 0:
        return 0.0
    return float(theta[int(above[-1])] - theta[int(above[0])])


def assert_all_at_least(left: np.ndarray, right: np.ndarray) -> None:
    assert np.all(np.asarray(left) >= np.asarray(right))


def assert_all_at_most(left: np.ndarray, right: np.ndarray) -> None:
    assert np.all(np.asarray(left) <= np.asarray(right))


@deterministic_test(spec_ref="simulation_protocols.figure_1", claim_id="Q-001")
def test_figure_1_attended_location_response_exceeds_unattended():
    out = protocols.run_figure_1()
    assert out["R_at_attended"] > out["R_at_unattended"]


@deterministic_test(spec_ref="simulation_protocols.figure_1", claim_id="Q-002")
def test_figure_1_attention_field_baseline_and_peak():
    out = protocols.run_figure_1()
    assert np.all(out["A"] >= 1.0)
    assert abs(out["A"].max() - 2.0) < 0.1


@deterministic_test(spec_ref="simulation_protocols.figure_1", claim_id="Q-003")
def test_figure_1_population_fields_are_non_negative():
    out = protocols.run_figure_1()
    assert np.all(out["E"] >= 0.0)
    assert np.all(out["A"] >= 1.0)
    assert np.all(out["S"] >= 0.0)
    assert np.all(out["R"] >= 0.0)


@deterministic_test(spec_ref="simulation_protocols.figure_2A", claim_id="Q-004")
def test_figure_2a_attended_response_exceeds_unattended():
    out = protocols.run_figure_2A()
    assert_all_at_least(out["attended_CRF"], out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_2A", claim_id="Q-005")
def test_figure_2a_percent_modulation_peaks_at_intermediate_contrast():
    out = protocols.run_figure_2A()
    peak = int(np.argmax(out["percent_modulation"]))
    assert 0 < peak < len(out["percent_modulation"]) - 1


@deterministic_test(spec_ref="simulation_protocols.figure_2A", claim_id="Q-006")
def test_figure_2a_attended_crf_is_left_shifted():
    out = protocols.run_figure_2A()
    attended_half = half_max_contrast(out["attended_CRF"], out["c"])
    unattended_half = half_max_contrast(out["unattended_CRF"], out["c"])
    assert attended_half < unattended_half


@deterministic_test(spec_ref="simulation_protocols.figure_2A", claim_id="Q-007")
def test_figure_2a_attended_crf_saturates_at_high_contrast():
    out = protocols.run_figure_2A()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3


@deterministic_test(spec_ref="simulation_protocols.figure_2A", claim_id="Q-008")
def test_figure_2a_high_contrast_modulation_is_below_peak_modulation():
    out = protocols.run_figure_2A()
    assert out["percent_modulation"][-1] < out["percent_modulation"].max()


@deterministic_test(spec_ref="simulation_protocols.figure_2B", claim_id="Q-009")
def test_figure_2b_attended_response_exceeds_unattended():
    out = protocols.run_figure_2B()
    assert_all_at_least(out["attended_CRF"], out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_2B", claim_id="Q-010")
def test_figure_2b_high_contrast_modulation_remains_substantial():
    out = protocols.run_figure_2B()
    assert out["percent_modulation"][-1] >= 0.5 * out["percent_modulation"].max()


@deterministic_test(spec_ref="simulation_protocols.figure_2B", claim_id="Q-011")
def test_figure_2b_attended_crf_is_multiplicative_scaling():
    out = protocols.run_figure_2B()
    ratio = out["attended_CRF"] / out["unattended_CRF"]
    mask = out["unattended_CRF"] > 0.01 * out["unattended_CRF"].max()
    assert ratio[mask].max() / ratio[mask].min() < 1.5


@deterministic_test(spec_ref="simulation_protocols.figure_2B", claim_id="Q-012")
def test_figure_2b_peak_attended_response_exceeds_peak_unattended():
    out = protocols.run_figure_2B()
    assert out["attended_CRF"].max() > out["unattended_CRF"].max()


@deterministic_test(spec_ref="simulation_protocols.figure_2B", claim_id="Q-013")
def test_figure_2b_attended_crf_saturates_at_high_contrast():
    out = protocols.run_figure_2B()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-014")
def test_figure_3c_attended_response_exceeds_unattended():
    out = protocols.run_figure_3C()
    assert_all_at_least(out["attended_CRF"], out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-015")
def test_figure_3c_percent_modulation_peaks_in_lower_half():
    out = protocols.run_figure_3C()
    assert int(np.argmax(out["percent_modulation"])) < len(out["percent_modulation"]) / 2


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-016")
def test_figure_3c_attended_crf_is_left_shifted():
    out = protocols.run_figure_3C()
    attended_half = half_max_contrast(out["attended_CRF"], out["c"])
    unattended_half = half_max_contrast(out["unattended_CRF"], out["c"])
    assert attended_half < unattended_half


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-017")
def test_figure_3c_lowest_contrast_response_is_positive():
    out = protocols.run_figure_3C()
    assert out["attended_CRF"][0] > 0.0
    assert out["unattended_CRF"][0] > 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-018")
def test_figure_3c_attended_crf_saturates_at_high_contrast():
    out = protocols.run_figure_3C()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3


@deterministic_test(spec_ref="simulation_protocols.figure_3F", claim_id="Q-019")
def test_figure_3f_attended_response_exceeds_unattended():
    out = protocols.run_figure_3F()
    assert_all_at_least(out["attended_CRF"], out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_3F", claim_id="Q-020")
def test_figure_3f_percent_modulation_peaks_in_lower_half():
    out = protocols.run_figure_3F()
    assert int(np.argmax(out["percent_modulation"])) < len(out["percent_modulation"]) / 2


@deterministic_test(spec_ref="simulation_protocols.figure_3F", claim_id="Q-021")
def test_figure_3f_absolute_difference_peaks_in_upper_half():
    out = protocols.run_figure_3F()
    assert int(np.argmax(out["absolute_difference"])) >= len(out["absolute_difference"]) / 2


@deterministic_test(spec_ref="simulation_protocols.figure_3F", claim_id="Q-022")
def test_figure_3f_percent_and_absolute_difference_peak_apart():
    out = protocols.run_figure_3F()
    percent_peak = int(np.argmax(out["percent_modulation"]))
    difference_peak = int(np.argmax(out["absolute_difference"]))
    assert abs(percent_peak - difference_peak) > len(out["percent_modulation"]) / 3


@deterministic_test(spec_ref="simulation_protocols.figure_3F", claim_id="Q-023")
def test_figure_3f_lowest_contrast_response_is_positive():
    out = protocols.run_figure_3F()
    assert out["attended_CRF"][0] > 0.0
    assert out["unattended_CRF"][0] > 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_3F", claim_id="Q-024")
def test_figure_3f_attended_crf_saturates_at_high_contrast():
    out = protocols.run_figure_3F()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-025")
def test_figure_4c_attending_nonpreferred_decreases_response():
    out = protocols.run_figure_4C()
    assert_all_at_most(out["attended_CRF"], out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-026")
def test_figure_4c_attended_crf_is_right_shifted():
    out = protocols.run_figure_4C()
    attended_half = half_max_contrast(out["attended_CRF"], out["c_pref"])
    unattended_half = half_max_contrast(out["unattended_CRF"], out["c_pref"])
    assert attended_half > unattended_half


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-027")
def test_figure_4c_absolute_percent_modulation_does_not_peak_at_highest_contrast():
    out = protocols.run_figure_4C()
    assert int(np.argmax(np.abs(out["percent_modulation"]))) < len(out["percent_modulation"]) - 1


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-028")
def test_figure_4c_crfs_converge_at_high_contrast():
    out = protocols.run_figure_4C()
    high_contrast_gap = abs(out["attended_CRF"][-1] - out["unattended_CRF"][-1]) / out["unattended_CRF"][-1]
    max_gap = abs(out["attended_CRF"] - out["unattended_CRF"]).max() / out["unattended_CRF"].max()
    assert high_contrast_gap < max_gap


@deterministic_test(spec_ref="simulation_protocols.figure_4E", claim_id="Q-029")
def test_figure_4e_attending_preferred_exceeds_attending_nonpreferred():
    out = protocols.run_figure_4E()
    assert np.all(out["attend_pref_CRF"] > out["attend_nonpref_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_4E", claim_id="Q-030")
def test_figure_4e_crfs_are_multiplicative_scaling():
    out = protocols.run_figure_4E()
    mask = out["attend_nonpref_CRF"] > 0.01 * out["attend_nonpref_CRF"].max()
    ratio = out["ratio"]
    assert ratio[mask].max() / ratio[mask].min() < 1.5


@deterministic_test(spec_ref="simulation_protocols.figure_4E", claim_id="Q-031")
def test_figure_4e_attend_pref_crf_saturates_at_high_contrast():
    out = protocols.run_figure_4E()
    attend_pref_at_half = value_at(out["c"], out["attend_pref_CRF"], 0.5)
    assert (out["attend_pref_CRF"][-1] - attend_pref_at_half) / attend_pref_at_half < 0.3


@deterministic_test(spec_ref="simulation_protocols.figure_4E", claim_id="Q-032")
def test_figure_4e_peak_attend_pref_exceeds_peak_attend_nonpreferred():
    out = protocols.run_figure_4E()
    assert out["attend_pref_CRF"].max() > out["attend_nonpref_CRF"].max()


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-033")
def test_figure_5c_attended_tuning_exceeds_unattended():
    out = protocols.run_figure_5C()
    assert_all_at_least(out["attended_tuning"], out["unattended_tuning"])


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-034")
def test_figure_5c_tuning_ratio_is_approximately_constant():
    out = protocols.run_figure_5C()
    mask = out["unattended_tuning"] > 0.05 * out["unattended_tuning"].max()
    ratio = out["ratio"]
    assert ratio[mask].max() / ratio[mask].min() < 1.3


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-035")
def test_figure_5c_both_tuning_curves_peak_at_same_orientation():
    out = protocols.run_figure_5C()
    attended_peak = out["theta_0_grid"][int(np.argmax(out["attended_tuning"]))]
    unattended_peak = out["theta_0_grid"][int(np.argmax(out["unattended_tuning"]))]
    assert abs(attended_peak - unattended_peak) < 5.0


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-036")
def test_figure_5c_fwhm_is_approximately_equal():
    out = protocols.run_figure_5C()
    attended_width = fwhm(out["attended_tuning"], out["theta_0_grid"])
    unattended_width = fwhm(out["unattended_tuning"], out["theta_0_grid"])
    assert abs(attended_width - unattended_width) / unattended_width < 0.2


@deterministic_test(spec_ref="simulation_protocols.figure_6C", claim_id="Q-037")
def test_figure_6c_feature_attention_narrows_tuning():
    out = protocols.run_figure_6C()
    attended_width = fwhm(out["attend_opposite_stimulus_tuning"], out["theta_stim_grid"])
    fixation_width = fwhm(out["attend_fixation_tuning"], out["theta_stim_grid"])
    assert attended_width < fixation_width


@deterministic_test(spec_ref="simulation_protocols.figure_6C", claim_id="Q-038")
def test_figure_6c_tuning_curves_peak_at_preferred_direction():
    out = protocols.run_figure_6C()
    fixation_peak = out["theta_stim_grid"][int(np.argmax(out["attend_fixation_tuning"]))]
    opposite_peak = out["theta_stim_grid"][int(np.argmax(out["attend_opposite_stimulus_tuning"]))]
    assert abs(fixation_peak) < 15.0
    assert abs(opposite_peak) < 15.0


@deterministic_test(spec_ref="simulation_protocols.figure_6C", claim_id="Q-039")
def test_figure_6c_tuning_curves_are_non_negative():
    out = protocols.run_figure_6C()
    assert np.all(out["attend_fixation_tuning"] >= 0.0)
    assert np.all(out["attend_opposite_stimulus_tuning"] >= 0.0)


@deterministic_test(spec_ref="simulation_protocols.figure_6C", claim_id="Q-040")
def test_figure_6c_feature_attention_boosts_preferred_response():
    out = protocols.run_figure_6C()
    assert out["attend_opposite_stimulus_tuning"].max() > out["attend_fixation_tuning"].max()


@deterministic_test(spec_ref="simulation_protocols.figure_7C", claim_id="Q-041")
def test_figure_7c_attending_variable_boosts_preferred_response():
    out = protocols.run_figure_7C()
    idx_pref = int(np.argmin(np.abs(out["theta_var_grid"])))
    assert out["attend_variable_tuning"][idx_pref] > out["fixation_tuning"][idx_pref]


@deterministic_test(spec_ref="simulation_protocols.figure_7C", claim_id="Q-042")
def test_figure_7c_attending_nonpreferred_suppresses_preferred_response():
    out = protocols.run_figure_7C()
    idx_pref = int(np.argmin(np.abs(out["theta_var_grid"])))
    assert out["attend_nonpref_tuning"][idx_pref] < out["fixation_tuning"][idx_pref]


@deterministic_test(spec_ref="simulation_protocols.figure_7C", claim_id="Q-043")
def test_figure_7c_variable_and_nonpreferred_shift_in_opposite_directions():
    out = protocols.run_figure_7C()
    idx_pref = int(np.argmin(np.abs(out["theta_var_grid"])))
    variable_delta = out["attend_variable_tuning"][idx_pref] - out["fixation_tuning"][idx_pref]
    nonpreferred_delta = out["attend_nonpref_tuning"][idx_pref] - out["fixation_tuning"][idx_pref]
    assert variable_delta * nonpreferred_delta < 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_7C", claim_id="Q-044")
def test_figure_7c_tuning_curves_are_non_negative():
    out = protocols.run_figure_7C()
    assert np.all(out["fixation_tuning"] >= 0.0)
    assert np.all(out["attend_nonpref_tuning"] >= 0.0)
    assert np.all(out["attend_variable_tuning"] >= 0.0)
