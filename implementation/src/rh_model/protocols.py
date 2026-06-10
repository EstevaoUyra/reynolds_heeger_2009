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


def _contrast_sweep(
    stimuli_factory, attention_factory, base_overrides, n_contrasts=8,
    c_range=(0.01, 1.0),
):
    """Sweep contrast on a log scale, returning (contrasts, responses).

    ``c_range`` is the (low, high) swept-contrast endpoints. Each CRF panel
    passes its OWN author-script window (the Figure*.m ``cRange``, CODE-020),
    resolved from the calibration ledger: 2A/2B/3C/3F use [1e-5, 1], 4C/4E use
    [1e-4, 0.1]. The default [0.01, 1.0] is retained only as a backstop for
    callers that do not pass a range; no figure protocol relies on it.
    """
    contrasts = np.logspace(np.log10(c_range[0]), np.log10(c_range[1]), n_contrasts)
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
    # Contrast window from the author Figure2A.m/Figure2B.m cRange (CODE-020):
    # [1e-5, 1], not the prior guessed [0.01, 1]. The model half-saturates at
    # c≈0.002-0.005, so [0.01,1] clips the rising limb + contrast-gain left-shift.
    c_range = (s["c_range_lo"], s["c_range_hi"])
    stim = lambda c: [{"x": 0.0, "theta": 0.0, "contrast": c}]
    attended = lambda c: {"spatial_center": 0.0, "feature_center": None}
    unattended = lambda c: {"spatial_center": None, "feature_center": None}
    c, att = _contrast_sweep(stim, attended, overrides, n_contrasts, c_range=c_range)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts, c_range=c_range)
    return measurements.crf_pair_record(c, att, unatt, contrast_key="c")


def run_figure_2A(n_contrasts: int = 8):
    """Citation: C-013, CODE-020 / spec.simulation_protocols.figure_2A

    Single suppression normalization (SQ-005, A-013): NO per-panel suppression
    gain or width scale — the prior SQ-001/SQ-002 knobs are deleted. The CRF
    bends over inside its window because the contrast sweep uses the author
    Figure2A.m cRange [1e-5, 1] (CODE-020), resolved from the ledger; the model
    half-saturates at c≈0.002-0.005, which the prior guessed [0.01,1] floor
    clipped off (rendering a flat plateau and hiding the contrast-gain left-shift).
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
    # Contrast window from the author Figure3C.m/Figure3F.m cRange (CODE-020):
    # [1e-5, 1], not the prior guessed [0.01, 1] (same clipped-window bug as Fig 2).
    c_range = (s["c_range_lo"], s["c_range_hi"])
    stim = lambda c: [{"x": 0.0, "theta": 0.0, "contrast": c}]
    attended = lambda c: {"spatial_center": 0.0, "feature_center": None}
    unattended = lambda c: {"spatial_center": None, "feature_center": None}
    c, att = _contrast_sweep(stim, attended, overrides, n_contrasts, c_range=c_range)
    _, unatt = _contrast_sweep(stim, unattended, overrides, n_contrasts, c_range=c_range)
    return measurements.crf_pair_record(
        c, att, unatt, contrast_key="c", with_absolute_difference=True
    )


def run_figure_3C(n_contrasts: int = 8):
    """Citation: C-014, CODE-017, CODE-020 / spec.simulation_protocols.figure_3C

    Single suppression normalization (SQ-005, A-013): NO per-panel suppression
    gain or width scale (the SQ-001 knobs are deleted). Baselines are the author
    Figure3C.m values (CODE-017: baselineMod=5e-7, baselineUnmod=5). The CRFs
    converge at high contrast inside the author Figure3C.m cRange [1e-5, 1]
    (CODE-020), resolved from the ledger — not the prior guessed [0.01, 1].
    """
    return _run_figure_3_panel("figure_3C", n_contrasts)


def run_figure_3F(n_contrasts: int = 8):
    """Citation: C-014 / spec.simulation_protocols.figure_3F"""
    return _run_figure_3_panel("figure_3F", n_contrasts)


# --- Figure 4 (two stimuli in RF) ---

def run_figure_4C(n_contrasts: int = 8, c_nonpref: float | None = None):
    """Figure 4C — exact authors' ``Figure4C.m`` protocol (CODE-018).

    Martinez-Trujillo & Treue (2002), as the authors actually simulated it:
    FOUR separated stimuli, the recorded neuron PREFERRING θ = 0 with its RF
    centred at x = 100 (the midpoint of the two RF stimuli):

      - x = 90,  θ = 0   — PREFERRED stimulus in RF, contrast c_pref (swept)
      - x = 110, θ = 180 — NULL/nonpreferred stimulus in RF, contrast 0.01 (fixed)
      - x = -90, θ = 0   — preferred stimulus in the opposite hemifield (swept)
      - x = -110,θ = 180 — null stimulus in the opposite hemifield (fixed 0.01)

    Two conditions, BOTH attending the NULL stimulus (an *oval* attention field,
    spatial Gaussian × a θ = 180° feature Gaussian of width 20° — the Fig-4C
    ``AthetaWidth`` — not flat in θ):

      - ``attended_CRF``   = attend the null stimulus IN the RF   (Ax = 110)
      - ``unattended_CRF`` = attend the null stimulus CONTRALATERAL (Ax = -110)

    Mechanism (C-021): attending the null boosts the θ = 180° population, which
    feeds ONLY the recorded θ = 0 neuron's SUPPRESSIVE pool, so attend-null-in-RF
    *lowers* its response → ``attended_CRF`` sits BELOW ``unattended_CRF``. The
    authors' reported attentional modulation is the SUPPRESSION
    ``%-mod = 100·(unattended-attended)/unattended`` (positive, peaking ~36% at
    low contrast and declining), which the record's ``percent_modulation`` field
    carries with that sign convention (``with_suppression_sign=True``). Verified:
    this exact configuration through ``rh_model.simulate`` reproduces the authors'
    Figure4C.m CRFs and a %-mod peak ~38% — matching the digitized panel_C
    %-modulation (~36%); see logs/.../verify_model_4c.

    cRange = [1e-4, 0.1] and c_nonpref = 0.01 are the authors' Figure4C.m values.

    PAPER/CODE INCONSISTENCY (tripwire DR-4C-sign): the *published* Figure 4C
    panel DRAWS the attend-nonpref-in-RF curve ABOVE attend-away and labels the
    dashed curve a "percentage increase" (caption B/C, C-015) — i.e. facilitation
    — which is the OPPOSITE curve order to the authors' released Figure4C.m (where
    attend-RF is the LOWER curve) and to C-021's suppression prose. We follow the
    released CODE (ladder rung 1) + C-021; the figure-panel sign/order discrepancy
    is dispositioned as a documented paper defect (see assumptions A-012 /
    decision-request DR-4C-sign).

    Citation: C-015, C-021 ; Code: CODE-018 (Figure4C.m) ; Assumption: A-012
    """
    s = _sci("figure_4C")
    if c_nonpref is None:
        c_nonpref = resolve("figure_4C.c_nonpref")
    rf_center = resolve("figure_4C.rf_center")
    stim_pref_rf = resolve("figure_4C.stim_pref_rf_x")
    stim_null_rf = resolve("figure_4C.stim_null_rf_x")
    stim_pref_contra = resolve("figure_4C.stim_pref_contra_x")
    stim_null_contra = resolve("figure_4C.stim_null_contra_x")
    theta_null = resolve("figure_4C.theta_nonpref")
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        recorded_x=rf_center,
        recorded_theta=0.0,
    )
    stim = lambda c_pref: [
        {"x": stim_pref_rf, "theta": 0.0, "contrast": c_pref},
        {"x": stim_null_rf, "theta": theta_null, "contrast": c_nonpref},
        {"x": stim_pref_contra, "theta": 0.0, "contrast": c_pref},
        {"x": stim_null_contra, "theta": theta_null, "contrast": c_nonpref},
    ]
    # Both conditions attend the NULL (θ=180) stimulus; spatial centre differs.
    attended = lambda c_pref: {
        "spatial_center": stim_null_rf, "feature_center": theta_null
    }
    unattended = lambda c_pref: {
        "spatial_center": stim_null_contra, "feature_center": theta_null
    }
    c_pref, att = _contrast_sweep(
        stim, attended, overrides, n_contrasts, c_range=(1e-4, 0.1)
    )
    _, unatt = _contrast_sweep(
        stim, unattended, overrides, n_contrasts, c_range=(1e-4, 0.1)
    )
    return measurements.crf_pair_record(
        c_pref, att, unatt, contrast_key="c_pref", with_suppression_sign=True
    )


def run_figure_4E(n_contrasts: int = 8):
    """Figure 4E — exact authors' ``Figure4E.m`` protocol (CODE-018).

    The "yoked contrast" Martinez-Trujillo & Treue panel. IDENTICAL
    four-separated-stimulus layout to 4C — preferred (θ = 0) and null (θ = 180)
    in the RF and contralateral — with the recorded neuron's RF centred at the
    midpoint of the two RF stimuli (x = 100):

      - x = 90,  θ = 0   — PREFERRED stimulus in RF
      - x = 110, θ = 180 — NULL/nonpreferred stimulus in RF
      - x = -90, θ = 0   — preferred stimulus in the opposite hemifield
      - x = -110,θ = 180 — null stimulus in the opposite hemifield

    UNLIKE 4C (which fixes the null at low contrast), ALL FOUR contrasts COVARY
    over the swept window — the yoked-contrast experiment. Two conditions:

      - ``attend_pref_CRF``    = attend the PREFERRED stimulus in RF (Ax = 90, Aθ = 0)
      - ``attend_nonpref_CRF`` = attend the NULL stimulus in RF (Ax = 110, Aθ = 180)

    The record's ``ratio`` = attend_pref / attend_nonpref; the %-modulation is
    ``(ratio - 1)·100``. This author geometry (vs the prior two-co-located-stimuli
    -at-x=0 layout, which let feature competition crush the nonpreferred response
    and overflow the %-modulation to ~386%) yields a peak %-modulation ~50–54%,
    matching the digitized panel-E ~54% — the faithful mechanism reaches the paper
    value once the geometry is the authors' (CODE-018), with NO tuning (A-013).

    Contrast window = author Figure4E.m cRange [1e-4, 0.1] (CODE-020).

    Citation: C-015 / spec.simulation_protocols.figure_4E ; Code: CODE-018 (Figure4E.m)
    """
    s = _sci("figure_4E")
    rf_center = resolve("figure_4E.rf_center")
    stim_pref_rf = resolve("figure_4E.stim_pref_rf_x")
    stim_null_rf = resolve("figure_4E.stim_null_rf_x")
    stim_pref_contra = resolve("figure_4E.stim_pref_contra_x")
    stim_null_contra = resolve("figure_4E.stim_null_contra_x")
    theta_null = resolve("figure_4E.theta_nonpref")
    overrides = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        recorded_x=rf_center,
        recorded_theta=0.0,
    )
    c_range = (s["c_range_lo"], s["c_range_hi"])
    # All four stimuli covary in contrast (the yoked-contrast experiment).
    stim = lambda c: [
        {"x": stim_pref_rf, "theta": 0.0, "contrast": c},
        {"x": stim_null_rf, "theta": theta_null, "contrast": c},
        {"x": stim_pref_contra, "theta": 0.0, "contrast": c},
        {"x": stim_null_contra, "theta": theta_null, "contrast": c},
    ]
    attend_pref = lambda c: {"spatial_center": stim_pref_rf, "feature_center": 0.0}
    attend_nonpref = lambda c: {
        "spatial_center": stim_null_rf, "feature_center": theta_null
    }
    c, att_pref = _contrast_sweep(stim, attend_pref, overrides, n_contrasts, c_range=c_range)
    _, att_nonpref = _contrast_sweep(stim, attend_nonpref, overrides, n_contrasts, c_range=c_range)
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

def run_figure_6C(n_directions: int = 25):
    """Authors' ``Figure6C.m`` protocol (CODE-018) — feature-based attention.

    Citation: C-017, C-021, C-023 / spec.simulation_protocols.figure_6C
    Code: CODE-018 (Figure6C.m + attentionModel.m:146-162, Ashape='cross')

    Geometry comes from the BINDING ledger keys (calibration.yaml figure_6C.*),
    transcribed verbatim from ``Figure6C.m``:

      - figure_6C.stim_rf_x        = 100  : RF stimulus (θ=0) AND the recorded
                                            column (i = find(x==stimCenter1))
      - figure_6C.stim_contra_x    = -100 : contralateral stimulus (θ=0); also the
                                            attend-opposite spatial centre (Ax) and
                                            its feature centre (Atheta = θ of stim2)
      - figure_6C.attend_fixation_x = 0   : attend-fixation flat-θ baseline centre

    Two SEPARATED stimuli, both at the swept direction θ_stim (the authors sweep a
    single direction and read off the recorded neuron's tuning), each θ-impulse
    gratings. Two attention conditions, both at AxWidth = AthetaWidth-driven sizes
    from the ledger (attention_field_size = 30, tuning_width = 60):

      - attend_fixation : oval field at Ax = attend_fixation_x (= 0), flat in θ
                          (Atheta NaN). The 'Att Away' baseline (R1 in Figure6C.m).
      - attend_opposite : author 'cross' field at Ax = stim_contra_x (= -100),
                          Atheta = θ_stim. The additive separable spatial×feature
                          field (attentionModel.m:146-162). Because AxWidth=30 places
                          attnGainX≈Abase at the recorded RF column (x=100), the
                          directional gain reaches the RF only through the θ-conv —
                          NOT at full γ — so it scales + sharpens the tuning by the
                          digitized amount (peak ratio 1.108, FWHM ratio ~0.88,
                          CODE-018) rather than the over-scaled ~1.167 a flat-x
                          full-γ proxy produced (the retired SQ-006 framing).
    """
    s = _sci("figure_6C")
    overrides_template = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        # Record from the RF-stimulus column (Figure6C.m: i = find(x==stimCenter1)).
        recorded_x=resolve("figure_6C.stim_rf_x"),
    )
    # Binding ledger geometry (calibration.yaml figure_6C.*, CODE-018).
    x_rf = resolve("figure_6C.stim_rf_x")
    x_contra = resolve("figure_6C.stim_contra_x")
    x_fixation = resolve("figure_6C.attend_fixation_x")

    theta_stim_grid = np.linspace(-180.0, 175.0, n_directions)
    contrast = resolve("figure_6C.contrast")
    attend_fixation_tuning = np.zeros(n_directions)
    attend_opposite_stimulus_tuning = np.zeros(n_directions)
    for idx, theta_stim in enumerate(theta_stim_grid):
        stimuli = [
            {"x": x_rf, "theta": float(theta_stim), "contrast": contrast},
            {"x": x_contra, "theta": float(theta_stim), "contrast": contrast},
        ]
        params = default_params(**overrides_template)
        attend_fixation_tuning[idx] = simulate(
            stimuli,
            {"spatial_center": x_fixation, "feature_center": None, "shape": "oval"},
            params,
        )["response"]
        attend_opposite_stimulus_tuning[idx] = simulate(
            stimuli,
            # Author 'cross' field: spatial centre at the contralateral stimulus
            # (Ax = stim_contra_x), feature centre at the swept direction (Atheta).
            {
                "spatial_center": x_contra,
                "feature_center": float(theta_stim),
                "shape": "cross",
            },
            params,
        )["response"]
    return measurements.tuning_record({
        "theta_stim_grid": theta_stim_grid,
        "attend_fixation_tuning": attend_fixation_tuning,
        "attend_opposite_stimulus_tuning": attend_opposite_stimulus_tuning,
    })


# --- Figure 7 (two stimuli in RF, three attention conditions) ---

def run_figure_7C(n_directions: int = 25, theta_nonpref: float | None = None):
    """Figure 7C — exact authors' ``Figure7C.m`` protocol (CODE-018).

    Two SEPARATED stimuli in the RF (NOT co-located at x = 0): a
    variable-direction grating at x = 93 and a fixed null (θ = 180) grating at
    x = 107, with the recorded neuron's RF centred at their midpoint (x = 100).
    There is NO contralateral stimulus; spatial attention "away" is directed to
    x = -100. The sweep is over the variable stimulus's motion direction θ_var,
    at fixed contrast 1.0 (CODE-021). Three conditions:

      - ``fixation_tuning``        = attend AWAY (Ax = -100, feature-flat) — baseline
      - ``attend_nonpref_tuning``  = attend the NULL stimulus (Ax = 107, Aθ = 180)
      - ``attend_variable_tuning`` = attend the VARIABLE stimulus (Ax = 93, Aθ = θ_var)

    Co-locating the two stimuli at x = 0 inflated the attend-variable / attend-away
    peak ratio to ~2.73 (the prior "intended failure"); the authors' separated
    x = 93/107 geometry yields ~1.41, matching the digitized ~1.33–1.4 — the
    faithful mechanism reaches the paper ratio once the geometry is restored, with
    NO tuning (A-013). AthetaWidth = 45 (Table 1, CODE-018).

    Citation: C-018 / spec.simulation_protocols.figure_7C ; Code: CODE-018 (Figure7C.m)
    """
    s = _sci("figure_7C")
    if theta_nonpref is None:
        theta_nonpref = resolve("figure_7C.theta_nonpref")
    rf_center = resolve("figure_7C.rf_center")
    stim_var_x = resolve("figure_7C.stim_var_x")
    stim_null_x = resolve("figure_7C.stim_null_x")
    att_away_x = resolve("figure_7C.att_away_x")
    overrides_template = dict(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        recorded_x=rf_center,
        recorded_theta=0.0,
    )
    theta_var_grid = np.linspace(-180.0, 175.0, n_directions)
    contrast = resolve("figure_7C.contrast")
    fixation_tuning = np.zeros(n_directions)
    attend_nonpref_tuning = np.zeros(n_directions)
    attend_variable_tuning = np.zeros(n_directions)
    for idx, theta_var in enumerate(theta_var_grid):
        stimuli = [
            {"x": stim_null_x, "theta": theta_nonpref, "contrast": contrast},
            {"x": stim_var_x, "theta": float(theta_var), "contrast": contrast},
        ]
        params = default_params(**overrides_template)
        fixation_tuning[idx] = simulate(
            stimuli, {"spatial_center": att_away_x, "feature_center": None}, params
        )["response"]
        attend_nonpref_tuning[idx] = simulate(
            stimuli,
            {"spatial_center": stim_null_x, "feature_center": theta_nonpref},
            params,
        )["response"]
        attend_variable_tuning[idx] = simulate(
            stimuli,
            {"spatial_center": stim_var_x, "feature_center": float(theta_var)},
            params,
        )["response"]
    return measurements.tuning_record({
        "theta_var_grid": theta_var_grid,
        "fixation_tuning": fixation_tuning,
        "attend_nonpref_tuning": attend_nonpref_tuning,
        "attend_variable_tuning": attend_variable_tuning,
    })
