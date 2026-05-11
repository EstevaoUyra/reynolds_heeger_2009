"""Per-figure protocol runners.

Each function corresponds to one entry in
article_aware/spec/model_spec.yaml/simulation_protocols, and returns a dict
of named outputs matching the qualitative claims for that figure.
"""

from __future__ import annotations

import numpy as np

from .model import default_params, simulate


def _safe_pm(attended: np.ndarray, unattended: np.ndarray) -> np.ndarray:
    """Percent modulation, guarded against div-by-near-zero."""
    denom = np.where(np.abs(unattended) > 1e-9, unattended, 1e-9)
    return 100.0 * (attended - unattended) / denom


def _contrast_sweep(stimuli_factory, attention_factory, base_overrides, n_contrasts=8):
    """Sweep contrast on a log scale, returning (contrasts, responses)."""
    contrasts = np.logspace(np.log10(0.01), np.log10(1.0), n_contrasts)
    responses = np.zeros(n_contrasts)
    for i, c in enumerate(contrasts):
        params = default_params(**base_overrides)
        out = simulate(stimuli_factory(c), attention_factory(c), params)
        responses[i] = out["response"]
    return contrasts, responses


# --- Figure 1 (illustrative) ---

def run_figure_1():
    """Figure 1 — schematic. Returns the population fields E, A, S, R for
    a two-grating stimulus with attention to the right stimulus.

    Citation: C-012 / spec.simulation_protocols.figure_1
    """
    overrides = dict(
        stimulus_size=3.0,
        attention_field_size=30.0,
        peak_attention_gain_gamma=2.0,
        tuning_width=30.0,
        sigma=1.5,
        stimulus_spatial_sigma_scale=0.5,
        attention_spatial_sigma_scale=21.5 / 30.0,
        suppressive_spatial_sigma_scale=0.2,
        recorded_x=10.0,
        recorded_theta=0.0,
    )
    params = default_params(**overrides)
    stimuli = [
        {"x": -10.0, "theta": 0.0, "contrast": 0.5},
        {"x": 10.0, "theta": 0.0, "contrast": 0.5},
    ]
    attention = {"spatial_center": 10.0, "feature_center": None}
    out = simulate(stimuli, attention, params)
    # Extract 1D slice at θ = 0 for the population fields
    j0 = int(np.argmin(np.abs(params.theta_grid - 0.0)))
    return {
        "x_grid": params.x_grid,
        "E_slice": out["E"][j0],
        "A_slice": out["A"][j0],
        "S_slice": out["S"][j0],
        "R_slice": out["R"][j0],
        "R_at_attended": float(out["R"][j0, int(np.argmin(np.abs(params.x_grid - 10.0)))]),
        "R_at_unattended": float(out["R"][j0, int(np.argmin(np.abs(params.x_grid + 10.0)))]),
        "E": out["E"],
        "A": out["A"],
        "S": out["S"],
        "R": out["R"],
    }


# --- Figure 2 (single stim, attended vs unattended) ---

def _run_figure_2_panel(stimulus_size: float, attention_field_size: float, n_contrasts: int = 8):
    overrides = dict(
        stimulus_size=stimulus_size,
        attention_field_size=attention_field_size,
        peak_attention_gain_gamma=2.0,
        tuning_width=30.0,
        suppressive_drive_gain=4.0,
        baseline_unmodulated=0.01,
    )
    stim = lambda c: [{"x": 0.0, "theta": 0.0, "contrast": c}]
    attended = lambda c: {"spatial_center": 0.0, "feature_center": None}
    unattended = lambda c: {"spatial_center": None, "feature_center": None}
    c, att = _contrast_sweep(stim, attended, overrides, n_contrasts)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts)
    return {
        "attended_CRF": att,
        "unattended_CRF": unatt,
        "percent_modulation": _safe_pm(att, unatt),
        "c": c,
    }


def run_figure_2A(n_contrasts: int = 8):
    """Citation: C-013 / spec.simulation_protocols.figure_2A"""
    return _run_figure_2_panel(3.0, 30.0, n_contrasts)


def run_figure_2B(n_contrasts: int = 8):
    """Citation: C-013 / spec.simulation_protocols.figure_2B"""
    return _run_figure_2_panel(5.0, 3.0, n_contrasts)


# --- Figure 3 (with baseline) ---

def _run_figure_3_panel(
    stimulus_size: float,
    attention_field_size: float,
    n_contrasts: int = 8,
    suppressive_drive_gain: float = 5.0,
    baseline_modulated_by_attention: float = 0.02,
    baseline_unmodulated: float = 0.1,
):
    overrides = dict(
        stimulus_size=stimulus_size,
        attention_field_size=attention_field_size,
        peak_attention_gain_gamma=2.0,
        tuning_width=30.0,
        suppressive_drive_gain=suppressive_drive_gain,
        baseline_modulated_by_attention=baseline_modulated_by_attention,
        baseline_unmodulated=baseline_unmodulated,
    )
    stim = lambda c: [{"x": 0.0, "theta": 0.0, "contrast": c}]
    attended = lambda c: {"spatial_center": 0.0, "feature_center": None}
    unattended = lambda c: {"spatial_center": None, "feature_center": None}
    c, att = _contrast_sweep(stim, attended, overrides, n_contrasts)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts)
    return {
        "attended_CRF": att,
        "unattended_CRF": unatt,
        "percent_modulation": _safe_pm(att, unatt),
        "absolute_difference": att - unatt,
        "c": c,
    }


def run_figure_3C(n_contrasts: int = 8):
    """Citation: C-014 / spec.simulation_protocols.figure_3C"""
    return _run_figure_3_panel(5.0, 30.0, n_contrasts)


def run_figure_3F(n_contrasts: int = 8):
    """Citation: C-014 / spec.simulation_protocols.figure_3F"""
    return _run_figure_3_panel(
        7.0,
        7.0,
        n_contrasts,
        suppressive_drive_gain=8.0,
        baseline_modulated_by_attention=0.05,
        baseline_unmodulated=0.05,
    )


# --- Figure 4 (two stimuli in RF) ---

def run_figure_4C(n_contrasts: int = 8, c_nonpref: float = 0.5):
    """Two stimuli colocated in RF. c_pref varied; c_nonpref fixed.
    Attended = attend nonpref-in-RF; unattended = attend opposite hemifield (A=1).

    Citation: C-015 / spec.simulation_protocols.figure_4C
    """
    overrides = dict(
        stimulus_size=5.0,
        attention_field_size=5.0,
        peak_attention_gain_gamma=5.0,
        tuning_width=20.0,
        suppressive_drive_gain=20.0,
    )
    stim = lambda c_pref: [
        {"x": 0.0, "theta": 0.0, "contrast": c_pref},
        {"x": 0.0, "theta": 180.0, "contrast": c_nonpref},
    ]
    attended = lambda c_pref: {"spatial_center": 0.0, "feature_center": 180.0}
    unattended = lambda c_pref: {"spatial_center": None, "feature_center": None}
    c_pref, att = _contrast_sweep(stim, attended, overrides, n_contrasts)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts)
    return {
        "attended_CRF": att,
        "unattended_CRF": unatt,
        "percent_modulation": _safe_pm(att, unatt),
        "c_pref": c_pref,
    }


def run_figure_4E(n_contrasts: int = 8):
    """Two stimuli colocated in RF, contrasts covary.
    attend_pref vs attend_nonpref.

    Citation: C-015 / spec.simulation_protocols.figure_4E
    """
    overrides = dict(
        stimulus_size=5.0,
        attention_field_size=5.0,
        peak_attention_gain_gamma=5.0,
        tuning_width=20.0,
        suppressive_drive_gain=4.0,
    )
    stim = lambda c: [
        {"x": 0.0, "theta": 0.0, "contrast": c},
        {"x": 0.0, "theta": 180.0, "contrast": c},
    ]
    attend_pref = lambda c: {"spatial_center": 0.0, "feature_center": 0.0}
    attend_nonpref = lambda c: {"spatial_center": 0.0, "feature_center": 180.0}
    c, att_pref = _contrast_sweep(stim, attend_pref, overrides, n_contrasts)
    _, att_nonpref = _contrast_sweep(stim, attend_nonpref, overrides, n_contrasts)
    return {
        "attend_pref_CRF": att_pref,
        "attend_nonpref_CRF": att_nonpref,
        "ratio": att_pref / np.where(att_nonpref > 1e-9, att_nonpref, 1e-9),
        "c": c,
    }


# --- Figure 5 (orientation tuning, multiplicative scaling) ---

def run_figure_5C(n_orientations: int = 19):
    """Sweep stimulus orientation; record tuning curve attended vs unattended.

    Citation: C-016 / spec.simulation_protocols.figure_5C
    """
    overrides_template = dict(
        stimulus_size=10.0,
        attention_field_size=10.0,
        peak_attention_gain_gamma=2.0,
        tuning_width=30.0,
    )
    theta_0_grid = np.linspace(-90.0, 90.0, n_orientations)
    contrast = 0.5
    attended_tuning = np.zeros(n_orientations)
    unattended_tuning = np.zeros(n_orientations)
    for i, theta_0 in enumerate(theta_0_grid):
        stimuli = [{"x": 0.0, "theta": float(theta_0), "contrast": contrast}]
        params = default_params(**overrides_template)
        attended_tuning[i] = simulate(
            stimuli, {"spatial_center": 0.0, "feature_center": None}, params
        )["response"]
        unattended_tuning[i] = simulate(
            stimuli, {"spatial_center": None, "feature_center": None}, params
        )["response"]
    return {
        "theta_0_grid": theta_0_grid,
        "attended_tuning": attended_tuning,
        "unattended_tuning": unattended_tuning,
        "ratio": attended_tuning / np.where(unattended_tuning > 1e-9, unattended_tuning, 1e-9),
    }


# --- Figure 6 (motion direction tuning, feature-based attention) ---

def run_figure_6C(n_directions: int = 25, x_opposite: float = -50.0, x_fixation: float = 50.0):
    """Sweep stimulus motion direction (yoked across two stimuli);
    record tuning curve attend_fixation vs attend_opposite_stimulus.

    Two stimuli, both at the same θ_stim:
      - In RF (x = 0)
      - In opposite hemifield (x = x_opposite)
    Spatial attention always away from RF (at fixation or at opposite stim).

    Citation: C-017 / spec.simulation_protocols.figure_6C
    """
    overrides_template = dict(
        stimulus_size=10.0,
        attention_field_size=30.0,
        peak_attention_gain_gamma=2.0,
        tuning_width=60.0,
    )
    theta_stim_grid = np.linspace(-180.0, 175.0, n_directions)
    attend_fixation_tuning = np.zeros(n_directions)
    attend_opposite_stimulus_tuning = np.zeros(n_directions)
    for i, theta_stim in enumerate(theta_stim_grid):
        stimuli = [
            {"x": 0.0, "theta": float(theta_stim), "contrast": 0.5},
            {"x": x_opposite, "theta": float(theta_stim), "contrast": 0.5},
        ]
        params = default_params(**overrides_template)
        # attend_fixation: spatial Gaussian at fixation, flat in θ
        attend_fixation_tuning[i] = simulate(
            stimuli,
            {"spatial_center": x_fixation, "feature_center": None},
            params,
        )["response"]
        # attend_opposite_stimulus: spatial at opposite, feature at θ_stim
        attend_opposite_stimulus_tuning[i] = simulate(
            stimuli,
            {"spatial_center": x_opposite, "feature_center": float(theta_stim)},
            params,
        )["response"]
    return {
        "theta_stim_grid": theta_stim_grid,
        "attend_fixation_tuning": attend_fixation_tuning,
        "attend_opposite_stimulus_tuning": attend_opposite_stimulus_tuning,
    }


# --- Figure 7 (two stimuli in RF, three attention conditions) ---

def run_figure_7C(n_directions: int = 25, theta_nonpref: float = 180.0):
    """Sweep θ_var; three attention conditions on two-stim-in-RF setup.

    Citation: C-018 / spec.simulation_protocols.figure_7C
    """
    overrides_template = dict(
        stimulus_size=5.0,
        attention_field_size=5.0,
        peak_attention_gain_gamma=5.0,
        tuning_width=45.0,
    )
    theta_var_grid = np.linspace(-180.0, 175.0, n_directions)
    fixation_tuning = np.zeros(n_directions)
    attend_nonpref_tuning = np.zeros(n_directions)
    attend_variable_tuning = np.zeros(n_directions)
    x_fixation = 50.0
    for i, theta_var in enumerate(theta_var_grid):
        stimuli = [
            {"x": 0.0, "theta": theta_nonpref, "contrast": 0.5},
            {"x": 0.0, "theta": float(theta_var), "contrast": 0.5},
        ]
        params = default_params(**overrides_template)
        # fixation: spatial away, flat
        fixation_tuning[i] = simulate(
            stimuli,
            {"spatial_center": x_fixation, "feature_center": None},
            params,
        )["response"]
        # attend nonpref: spatial in RF, feature at nonpref direction
        attend_nonpref_tuning[i] = simulate(
            stimuli,
            {"spatial_center": 0.0, "feature_center": theta_nonpref},
            params,
        )["response"]
        # attend variable: spatial in RF, feature at variable direction
        attend_variable_tuning[i] = simulate(
            stimuli,
            {"spatial_center": 0.0, "feature_center": float(theta_var)},
            params,
        )["response"]
    return {
        "theta_var_grid": theta_var_grid,
        "fixation_tuning": fixation_tuning,
        "attend_nonpref_tuning": attend_nonpref_tuning,
        "attend_variable_tuning": attend_variable_tuning,
    }
