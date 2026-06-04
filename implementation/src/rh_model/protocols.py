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
    """Resolved scientific overrides for a protocol (merged ledger view).

    Under the SQ-005 resolution every CRF/tuning protocol uses the SAME single
    suppression normalization (the cited/code field constants) — there are no
    per-panel suppression knobs to resolve here (A-013).
    """
    return resolve_namespace(protocol)


# --- Figure 1 (illustrative population fields) ---

def run_figure_1() -> dict:
    """Figure 1 — four rendered population fields E, A, S, R (CODE-019 config).

    Two equal vertical gratings at x = ±100; attention on the RIGHT (Ax = +100,
    AxWidth = 30, γ = 2). The rendered "Stimulus drive" box is Eraw (PRE-attention),
    so E is left/right symmetric; the attention asymmetry first appears in S and R
    (which use E = attnGain·Eraw). All field/σ sizes are the single cited/code
    constants (ExWidth=5, EthetaWidth=60, IxWidth=20, IthetaWidth=360, σ=1e-6) —
    no per-panel knob.

    Citation: C-009, C-012 / spec.simulation_protocols.figure_1
    Code: CODE-019, CODE-011, CODE-014
    """
    overrides = dict(
        stimulus_size=resolve("figure_1.stimulus_size"),
        attention_field_size=resolve("figure_1.attention_field_size"),
        peak_attention_gain_gamma=resolve("figure_1.peak_attention_gain_gamma"),
        tuning_width=resolve("figure_1.tuning_width"),
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
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
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
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        # Figure-3 baselines from the authors' code (CODE-017): baseline_modulated
        # added to E (attention-modulated path); baseline_unmodulated added to R
        # after normalization. 3C: mod=5e-7, unmod=5.0; 3F: mod=5e-7, unmod=0.0.
        baseline_modulated_by_attention=s["baseline_modulated"],
        baseline_unmodulated=s["baseline_unmodulated"],
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

    Citation: C-015, C-019 / spec.simulation_protocols.figure_4C

    Assumption: A-012 — the "attend nonpreferred-in-RF" condition is a SPATIAL
    (location) attention cue to the RF (Martinez-Trujillo & Treue 2002): a
    spatial Gaussian centered at x = 0, FLAT over θ (``feature_center=None``),
    so the gain γ boosts the drives of BOTH colocated stimuli — including the
    recorded θ = 0 neuron's preferred drive. This yields contrast-gain
    facilitation (attended CRF above attend-away, leftward shift, positive
    declining %-modulation). A narrow feature-tuned field on θ = 180° (the
    prior build) lands the gain on the suppressive pool only and produces the
    wrong (suppression) sign — that is the Fig-4E mechanism, not 4C. The cited
    180° suppressive tuning width (C-011) and the global σ are used as-is; the
    SQ-004 per-protocol overrides are RETIRED.
    """
    s = _sci("figure_4C")
    if c_nonpref is None:
        c_nonpref = resolve("figure_4C.c_nonpref")
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
    )
    stim = lambda c_pref: [
        {"x": 0.0, "theta": 0.0, "contrast": c_pref},
        {"x": 0.0, "theta": 180.0, "contrast": c_nonpref},
    ]
    attended = lambda c_pref: {"spatial_center": 0.0, "feature_center": None}
    unattended = lambda c_pref: {"spatial_center": None, "feature_center": None}
    c_pref, att = _contrast_sweep(stim, attended, overrides, n_contrasts)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts)
    return measurements.crf_pair_record(c_pref, att, unatt, contrast_key="c_pref")


def run_figure_4E(n_contrasts: int = 8):
    """Two stimuli colocated in RF, contrasts covary. attend_pref vs nonpref.

    Citation: C-015 / spec.simulation_protocols.figure_4E
    """
    s = _sci("figure_4E")
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
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

    Citation: C-017, C-021, C-023 / spec.simulation_protocols.figure_6C

    Feature-based attention is spatially GLOBAL (C-023: "the stimulus drive is
    multiplied by an attention field that is itself selective for motion
    direction" — the directional gain multiplies the recorded neuron's drive, so
    it must reach the RF). The attend-opposite-stimulus condition therefore
    selects the current motion direction (feature_center = θ_stim) but is FLAT in
    x (spatial_center = None), so the feature gain reaches the recorded neuron at
    x = 0 and sharpens / elevates its direction tuning (C-021, C-023). Confining
    the field to a spatial Gaussian at x_opposite = -50 (attention-field size 30)
    zeroes the feature gain at x = 0 (G_x ≈ 0), so the curves overlap (peak ratio
    ~1.01, no sharpening) regardless of suppression gain — that is the
    spatial-confinement bug, not the feature mechanism. Spatial attention being
    directed AWAY from the RF (to the fixation/opposite location) is captured by
    the attend-fixation baseline, not by stripping the feature component from the
    RF. x_opposite is retained only as the location of the second (yoked) stimulus
    in E. The spatial-globality of feature attention is not yet a named ledger
    assumption — logged as SQ-006 (underspecification) for Phase A to formalize.
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
            # Feature-based attention is spatially global (C-023): flat in x so
            # the θ_stim-selective gain reaches the recorded neuron at x = 0.
            {"spatial_center": None, "feature_center": float(theta_stim)},
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
