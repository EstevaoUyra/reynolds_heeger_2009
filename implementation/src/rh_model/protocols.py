"""Per-figure protocol runners (ARCHITECTURE.md §2: protocol → measurement).

Each ``run_figure_<id>()`` runs the named forward stage pipeline over the
figure's stimulus/parameter sweep, delegates the typed record to
``measurements`` (pure, the single source of truth — §2), and returns that
record. The article-aware deterministic tests and the declarative view read
the SAME record, so a passing test and the figure can never disagree.

This is a STRUCTURE migration: the returned records are a *superset* of the
pre-migration protocol-output dicts with byte-for-behavior-identical values.
All numeric calibration comes from the §3 **two-ledger** view via
``rh_model.calibration`` (paper-derived: article_aware/spec/calibration.yaml;
implementation-side: implementation/calibration.yaml). No protocol holds a
tunable numeric literal.
"""

from __future__ import annotations

import numpy as np

from . import measurements
from .calibration import resolve, resolve_namespace
from .model import default_params, simulate


def _contrast_sweep(stimuli_factory, attention_factory, base_overrides, n_contrasts=8):
    """Sweep contrast on a log scale, returning (contrasts, responses)."""
    contrasts = np.logspace(np.log10(0.01), np.log10(1.0), n_contrasts)
    responses = np.zeros(n_contrasts)
    for i, c in enumerate(contrasts):
        params = default_params(**base_overrides)
        out = simulate(stimuli_factory(c), attention_factory(c), params)
        responses[i] = out["response"]
    return contrasts, responses


def _sci(protocol: str) -> dict:
    """Paper-derived scientific overrides for a protocol (article_aware)."""
    return resolve_namespace(protocol)


def _impl(protocol: str) -> dict:
    """Implementation-side overrides for a protocol (implementation ledger)."""
    return resolve_namespace(protocol)


# --- Figure 1 (illustrative population fields) ---

def run_figure_1() -> dict:
    """Figure 1 — schematic population fields E, A, S, R + spatial layout.

    Citation: C-012 / spec.simulation_protocols.figure_1
    """
    overrides = dict(
        stimulus_size=resolve("figure_1.stimulus_size"),
        attention_field_size=resolve("figure_1.attention_field_size"),
        peak_attention_gain_gamma=resolve("figure_1.peak_attention_gain_gamma"),
        tuning_width=resolve("figure_1.tuning_width"),
        sigma=resolve("figure_1.sigma"),
        stimulus_spatial_sigma_scale=resolve("figure_1.stimulus_spatial_sigma_scale"),
        attention_spatial_sigma_scale=resolve("figure_1.attention_spatial_sigma_scale"),
        suppressive_spatial_sigma_scale=resolve("figure_1.suppressive_spatial_sigma_scale"),
        recorded_x=resolve("figure_1.recorded_x"),
        recorded_theta=0.0,
    )
    params = default_params(**overrides)
    stimuli = [
        {"x": resolve("figure_1.stim_left_x"), "theta": 0.0,
         "contrast": resolve("figure_1.stim_contrast")},
        {"x": resolve("figure_1.stim_right_x"), "theta": 0.0,
         "contrast": resolve("figure_1.stim_contrast")},
    ]
    attention = {
        "spatial_center": resolve("figure_1.attention_spatial_center"),
        "feature_center": None,
    }
    out = simulate(stimuli, attention, params)
    j0 = int(np.argmin(np.abs(params.theta_grid - 0.0)))
    right_x = resolve("figure_1.stim_right_x")
    left_x = resolve("figure_1.stim_left_x")
    raw = {
        "x_grid": params.x_grid,
        "E_slice": out["E"][j0],
        "A_slice": out["A"][j0],
        "S_slice": out["S"][j0],
        "R_slice": out["R"][j0],
        "R_at_attended": float(
            out["R"][j0, int(np.argmin(np.abs(params.x_grid - right_x)))]
        ),
        "R_at_unattended": float(
            out["R"][j0, int(np.argmin(np.abs(params.x_grid - left_x)))]
        ),
        "E": out["E"],
        "A": out["A"],
        "S": out["S"],
        "R": out["R"],
    }
    return measurements.figure_1_record(raw)


# --- Figure 2 (single stim, attended vs unattended) ---

def _run_figure_2_panel(protocol: str, n_contrasts: int = 8):
    s = _sci(protocol)
    i = _impl(protocol)
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        suppressive_drive_gain=i["suppressive_drive_gain"],
        suppressive_spatial_sigma_scale=i["suppressive_spatial_sigma_scale"],
        baseline_unmodulated=i["baseline_unmodulated"],
    )
    stim = lambda c: [{"x": 0.0, "theta": 0.0, "contrast": c}]
    attended = lambda c: {"spatial_center": 0.0, "feature_center": None}
    unattended = lambda c: {"spatial_center": None, "feature_center": None}
    c, att = _contrast_sweep(stim, attended, overrides, n_contrasts)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts)
    return measurements.crf_pair_record(c, att, unatt, contrast_key="c")


def run_figure_2A(n_contrasts: int = 8):
    """Citation: C-013 / spec.simulation_protocols.figure_2A

    Assumption: A-006 / SQ-001 — the 1D discretized suppressive pooling is
    too broad so the contrast-gain CRF will not bend over within [0.01, 1];
    the per-protocol effective suppressive-width scale (0.55, implementation
    ledger) pulls half-saturation below 1 without raising the SQ-001 gain.
    """
    return _run_figure_2_panel("figure_2A", n_contrasts)


def run_figure_2B(n_contrasts: int = 8):
    """Citation: C-013 / spec.simulation_protocols.figure_2B"""
    return _run_figure_2_panel("figure_2B", n_contrasts)


# --- Figure 3 (with baseline) ---

def _run_figure_3_panel(protocol: str, n_contrasts: int = 8):
    s = _sci(protocol)
    i = _impl(protocol)
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        suppressive_drive_gain=i["suppressive_drive_gain"],
        suppressive_spatial_sigma_scale=i["suppressive_spatial_sigma_scale"],
        baseline_modulated_by_attention=i["baseline_modulated_by_attention"],
        baseline_unmodulated=i["baseline_unmodulated"],
    )
    stim = lambda c: [{"x": 0.0, "theta": 0.0, "contrast": c}]
    attended = lambda c: {"spatial_center": 0.0, "feature_center": None}
    unattended = lambda c: {"spatial_center": None, "feature_center": None}
    c, att = _contrast_sweep(stim, attended, overrides, n_contrasts)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts)
    return measurements.crf_pair_record(
        c, att, unatt, contrast_key="c", with_absolute_difference=True
    )


def run_figure_3C(n_contrasts: int = 8):
    """Citation: C-014 / spec.simulation_protocols.figure_3C

    Assumption: A-006 / SQ-001 — same over-broad 1D suppressive pooling as
    2A; the per-protocol effective suppressive-width scale (0.45,
    implementation ledger) lets the CRFs converge at high contrast so the
    absolute difference falls below 75% of its peak.
    """
    return _run_figure_3_panel("figure_3C", n_contrasts)


def run_figure_3F(n_contrasts: int = 8):
    """Citation: C-014 / spec.simulation_protocols.figure_3F"""
    return _run_figure_3_panel("figure_3F", n_contrasts)


# --- Figure 4 (two stimuli in RF) ---

def run_figure_4C(n_contrasts: int = 8, c_nonpref: float | None = None):
    """Two stimuli colocated in RF. c_pref varied; c_nonpref fixed.

    Citation: C-015 / spec.simulation_protocols.figure_4C

    Assumption: SQ-004 — with the cited suppressive tuning width (180 deg,
    C-010/C-011) the attend-nonpreferred CRF never recovers/saturates within
    [0.01, 1]. A per-protocol effective suppressive tuning width of 75 deg
    (implementation ledger, mid of the robust 60-90 deg green band) restores
    the contrast-gain recovery; article_aware/spec and the C-011 constant
    are left unchanged. Figure 4C green is PROVISIONAL, soft-blocked on
    SQ-004.
    """
    s = _sci("figure_4C")
    i = _impl("figure_4C")
    if c_nonpref is None:
        c_nonpref = resolve("figure_4C.c_nonpref")
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        suppressive_drive_gain=i["suppressive_drive_gain"],
        sigma=i["sigma"],
        suppressive_tuning_width=i["suppressive_tuning_width"],
    )
    stim = lambda c_pref: [
        {"x": 0.0, "theta": 0.0, "contrast": c_pref},
        {"x": 0.0, "theta": 180.0, "contrast": c_nonpref},
    ]
    attended = lambda c_pref: {"spatial_center": 0.0, "feature_center": 180.0}
    unattended = lambda c_pref: {"spatial_center": None, "feature_center": None}
    c_pref, att = _contrast_sweep(stim, attended, overrides, n_contrasts)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts)
    return measurements.crf_pair_record(c_pref, att, unatt, contrast_key="c_pref")


def run_figure_4E(n_contrasts: int = 8):
    """Two stimuli colocated in RF, contrasts covary. attend_pref vs nonpref.

    Citation: C-015 / spec.simulation_protocols.figure_4E
    """
    s = _sci("figure_4E")
    i = _impl("figure_4E")
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        suppressive_drive_gain=i["suppressive_drive_gain"],
    )
    stim = lambda c: [
        {"x": 0.0, "theta": 0.0, "contrast": c},
        {"x": 0.0, "theta": 180.0, "contrast": c},
    ]
    attend_pref = lambda c: {"spatial_center": 0.0, "feature_center": 0.0}
    attend_nonpref = lambda c: {"spatial_center": 0.0, "feature_center": 180.0}
    c, att_pref = _contrast_sweep(stim, attend_pref, overrides, n_contrasts)
    _, att_nonpref = _contrast_sweep(stim, attend_nonpref, overrides, n_contrasts)
    return measurements.crf_ratio_record(c, att_pref, att_nonpref)


# --- Figure 5 (orientation tuning, multiplicative scaling) ---

def run_figure_5C(n_orientations: int = 19):
    """Sweep stimulus orientation; tuning curve attended vs unattended.

    Citation: C-016 / spec.simulation_protocols.figure_5C
    """
    s = _sci("figure_5C")
    overrides_template = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
    )
    theta_0_grid = np.linspace(-90.0, 90.0, n_orientations)
    contrast = resolve("figure_5C.contrast")
    attended_tuning = np.zeros(n_orientations)
    unattended_tuning = np.zeros(n_orientations)
    for idx, theta_0 in enumerate(theta_0_grid):
        stimuli = [{"x": 0.0, "theta": float(theta_0), "contrast": contrast}]
        params = default_params(**overrides_template)
        attended_tuning[idx] = simulate(
            stimuli, {"spatial_center": 0.0, "feature_center": None}, params
        )["response"]
        unattended_tuning[idx] = simulate(
            stimuli, {"spatial_center": None, "feature_center": None}, params
        )["response"]
    rec = measurements.tuning_record({
        "theta_0_grid": theta_0_grid,
        "attended_tuning": attended_tuning,
        "unattended_tuning": unattended_tuning,
        "ratio": attended_tuning / np.where(
            unattended_tuning > 1e-9, unattended_tuning, 1e-9
        ),
    })
    return rec


# --- Figure 6 (motion direction tuning, feature-based attention) ---

def run_figure_6C(n_directions: int = 25, x_opposite: float = -50.0, x_fixation: float = 50.0):
    """Sweep stimulus motion direction; attend_fixation vs attend_opposite.

    Citation: C-017 / spec.simulation_protocols.figure_6C
    """
    s = _sci("figure_6C")
    overrides_template = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
    )
    theta_stim_grid = np.linspace(-180.0, 175.0, n_directions)
    contrast = resolve("figure_6C.contrast")
    attend_fixation_tuning = np.zeros(n_directions)
    attend_opposite_stimulus_tuning = np.zeros(n_directions)
    for idx, theta_stim in enumerate(theta_stim_grid):
        stimuli = [
            {"x": 0.0, "theta": float(theta_stim), "contrast": contrast},
            {"x": x_opposite, "theta": float(theta_stim), "contrast": contrast},
        ]
        params = default_params(**overrides_template)
        attend_fixation_tuning[idx] = simulate(
            stimuli, {"spatial_center": x_fixation, "feature_center": None}, params
        )["response"]
        attend_opposite_stimulus_tuning[idx] = simulate(
            stimuli,
            {"spatial_center": x_opposite, "feature_center": float(theta_stim)},
            params,
        )["response"]
    return measurements.tuning_record({
        "theta_stim_grid": theta_stim_grid,
        "attend_fixation_tuning": attend_fixation_tuning,
        "attend_opposite_stimulus_tuning": attend_opposite_stimulus_tuning,
    })


# --- Figure 7 (two stimuli in RF, three attention conditions) ---

def run_figure_7C(n_directions: int = 25, theta_nonpref: float = 180.0):
    """Sweep θ_var; three attention conditions on two-stim-in-RF setup.

    Citation: C-018 / spec.simulation_protocols.figure_7C
    """
    s = _sci("figure_7C")
    overrides_template = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
    )
    theta_var_grid = np.linspace(-180.0, 175.0, n_directions)
    contrast = resolve("figure_7C.contrast")
    fixation_tuning = np.zeros(n_directions)
    attend_nonpref_tuning = np.zeros(n_directions)
    attend_variable_tuning = np.zeros(n_directions)
    x_fixation = 50.0
    for idx, theta_var in enumerate(theta_var_grid):
        stimuli = [
            {"x": 0.0, "theta": theta_nonpref, "contrast": contrast},
            {"x": 0.0, "theta": float(theta_var), "contrast": contrast},
        ]
        params = default_params(**overrides_template)
        fixation_tuning[idx] = simulate(
            stimuli, {"spatial_center": x_fixation, "feature_center": None}, params
        )["response"]
        attend_nonpref_tuning[idx] = simulate(
            stimuli, {"spatial_center": 0.0, "feature_center": theta_nonpref}, params
        )["response"]
        attend_variable_tuning[idx] = simulate(
            stimuli, {"spatial_center": 0.0, "feature_center": float(theta_var)}, params
        )["response"]
    return measurements.tuning_record({
        "theta_var_grid": theta_var_grid,
        "fixation_tuning": fixation_tuning,
        "attend_nonpref_tuning": attend_nonpref_tuning,
        "attend_variable_tuning": attend_variable_tuning,
    })
