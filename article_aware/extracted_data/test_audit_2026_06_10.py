"""Tests encoding the 2026-06-10 faithfulness-audit findings (author-tests skill).

This module is the machine-checkable form of the 2026-06-10 re-render + author-code
faithfulness audit (README "Current exit", commit 8540de0 PARTIAL). It SHARPENS two
findings the 2026-06-04 audit (test_audit_2026_06_04.py) had left under-resolved:

  - the 7C attend-variable / fixation ratio is NOT merely "1.41, in the loose
    paper band" — author code reproduces 1.32 and the impl's 1.41 is a CODE_BUG in
    the suppressive circular-θ convolution (FFT wrap/centre convention vs MATLAB
    upConv), independent of the ~17%-too-large suppressive drive it produces; and
  - the 6C feature-attention field is NOT a GENUINE_DIVERGENCE of an "oval
    approximation that mildly overshoots" — the committed flat-in-x build
    OVER-sharpens (σ-ratio 0.79) relative to the author Ashape='cross' (0.89) and
    the digitized panel (0.87); the 'cross' field is the correct mechanism, so this
    is a CODE_BUG, not a divergence.

Tag -> test kind (skills/author-tests/SKILL.md):

  - CODE_BUG -> MUST-PASS. The faithful mechanism reproduces the paper/author value
    once the convolution convention (Finding 1) / the 'cross' attention field
    (Finding 2) is corrected. The expected values are the AUTHOR CODE reruns
    (conv2sepYcirc/upConv; Ashape='cross') cross-checked against the digitized
    panels — NOT a re-derivation from the record the protocol draws from, and NOT a
    figure fit. Satisfiable by the correct mechanism alone (see each test).
  - GENUINE_DIVERGENCE -> RED TRIPWIRE (soft/xfail). A faithful mechanism still
    misses it; it flips green only if the model genuinely improves (Finding 3,
    Figure 1).

Finding 4 (Figure 4C, PAPER_ISSUE — published panel draws attend-RF above) is
ALREADY-DISPOSITIONED and re-confirmed faithful to the author code with NO change
required; it is fully encoded by test_dr_4c_sign_resolution.py (DR-4C-sign) and is
NOT duplicated here.

Finding 5 (Figs 2A/2B/3C/3F/4E/5C single-stimulus forward model, FAITHFUL) records
no divergence and needs no test.

------------------------------------------------------------------------------
RELATIONSHIP TO test_audit_2026_06_04.py (do not silently resolve here):

  - AUD-D-7C-ratio (MUST-PASS) asserts ``abs(ratio - ~1.33) < 0.35``; the impl's
    1.41 PASSES that loose band. The 2026-06-10 audit re-derives the AUTHOR value
    as 1.32 and attributes the impl's 1.41 to the suppressive-convolution
    convention CODE_BUG. The new T-A610-7C-ratio test below asserts the TIGHT
    author target (1.32 +/- 0.03), which 1.41 FAILS — it is a STRICTER must-pass on
    the SAME quantity, encoding the convolution fix. AUD-D is left in place; the
    implementer drives BOTH green together by fixing the convolution.
  - AUD-E-6C-cross-tripwire was filed as a GENUINE_DIVERGENCE soft tripwire on the
    6C PEAK RATIO (~1.11) for the missing 'cross' field. The 2026-06-10 audit
    RE-TAGS the 'cross'-field gap as a CODE_BUG and pins the discriminating
    measurement as the direction-tuning σ-RATIO (FWHM ratio), for which the author
    'cross' field gives 0.89 and the committed flat-x build over-sharpens to 0.79.
    The new T-A610-6C-cross-sigma-ratio test below is the MUST-PASS form. AUD-E
    (peak ratio, soft) is left in place and flips green alongside it when 'cross'
    lands; this module adds the sharper, gating σ-ratio target the new audit
    verified. (The pre-existing test_figure_6C_code_bug.py encodes the EARLIER,
    coarser flat-x-vs-confined fix the committed model already satisfies; its
    targets are weaker than — and not in conflict with — the σ-ratio band here.)
------------------------------------------------------------------------------
"""

from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import fwhm
from rh_model import protocols
from rh_model.calibration import resolve_namespace
from rh_model.model import default_params, simulate
from rh_tier_helpers import ref_peak, tier_test


# ===========================================================================
# Finding 1 (CODE_BUG, model scope; visible in Fig 7C) — the suppressive
#   circular-θ convolution does not reproduce conv2sepYcirc/upConv.
#
#   On an IDENTICAL no-attention two-stimulus pair (x=93 θ=0, x=107 θ=180,
#   contrast 1) at the recorded neuron (x=100, θ=0) the impl suppressive drive is
#   S(0,100) = 0.001186 vs the author code 0.001012 — ~17% too large — even though
#   E matches exactly (0.00730 vs 0.00728). Because R = A·E/(S+σ), the inflated S
#   changes the RATIO across attention conditions: the Fig 7C attend-variable /
#   fixation peak ratio renders 1.41 vs author code 1.32 and the digitized panel
#   1.32. The residual after matching the 361-sample θ grid is the FFT wrap/centre
#   convention (np.roll(-argmax) in model.py:_separable_conv) vs MATLAB upConv's
#   odd-filter centre tap. FIX: bit-match conv2sepYcirc/upConv's circular centre
#   convention on the author's 361-sample [-180,180] θ grid.
# ===========================================================================

# The author no-attention two-stimulus pair (Finding 1 / Figure7C.m geometry).
_PAIR_STIMULI = [
    {"x": 93.0, "theta": 0.0, "contrast": 1.0},   # variable grating, preferred dir
    {"x": 107.0, "theta": 180.0, "contrast": 1.0},  # fixed null grating
]
_RECORDED_X, _RECORDED_THETA = 100.0, 0.0

# Author-code targets (Finding 1): S from conv2sepYcirc/upConv, E unchanged.
_AUTHOR_S_AT_RF = 0.001012     # impl currently 0.001186 (~17% too large)
_AUTHOR_E_AT_RF = 0.00728      # impl currently 0.00730 (already matches)


def _no_attention_pair_fields():
    """Run the no-attention 7C-geometry pair and return (S, E) at the recorded RF.

    Uses the SAME ``simulate`` and the SAME 7C calibration (field sizes, γ, widths)
    the protocol uses, with attention OFF (A == 1 everywhere), so this isolates the
    suppressive convolution operator from the attention field. Evaluated on the
    model's own S/E fields; the EXPECTED value is the AUTHOR CODE's
    conv2sepYcirc/upConv result (Finding 1), not a re-derivation from this record.

    Citation: C-018 / attentionModel.m:171 (conv2sepYcirc), conv2sepYcirc.m:18-19
    (upConv circular).
    """
    s = resolve_namespace("figure_7C")
    params = default_params(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        recorded_x=_RECORDED_X,
        recorded_theta=_RECORDED_THETA,
    )
    out = simulate(_PAIR_STIMULI, {"spatial_center": None, "feature_center": None}, params)
    i = int(np.argmin(np.abs(params.x_grid - _RECORDED_X)))
    j = int(np.argmin(np.abs(params.theta_grid - _RECORDED_THETA)))
    return float(out["S"][j, i]), float(out["E"][j, i])


@deterministic_test(
    spec_ref="pipeline.compute_suppressive_drive", figure=7,
    claim_id="T-A610-7C-suppressive-drive",
)
def test_no_attention_suppressive_drive_matches_author_conv2sepYcirc():
    """MUST-PASS (CODE_BUG): on the no-attention two-stimulus pair (x=93 θ=0,
    x=107 θ=180, contrast 1) the suppressive drive at the recorded neuron
    (x=100, θ=0) equals the author conv2sepYcirc/upConv value S(0,100)=0.001012
    (+/-0.5%). The committed model gives 0.001186 — ~17% too large — because its
    circular-θ convolution (np.roll(-argmax) + FFT) does not reproduce MATLAB
    upConv's odd-filter centre tap on the author's 361-sample [-180,180] θ grid.

    Satisfiable by the correct mechanism alone: bit-matching the author's circular
    convolution convention (and θ grid) lands S at the author value with no free
    parameter. The stimulus drive E is asserted unchanged (already matches), so the
    only way to move S onto target is the convolution convention — NOT tuning a
    suppression gain (there is none; A-013 / SQ-005). EXPECTED RED today (0.001186).

    Citation: attentionModel.m:171 ; conv2sepYcirc.m:18-19 (upConv circular) ;
    model.py:_separable_conv (130-151) ; θ grid model.py:65-67.
    """
    S_rf, E_rf = _no_attention_pair_fields()

    # Guard: E must already match the author drive (Finding 1: E faithful). This
    # pins the failure to the SUPPRESSIVE convolution, not the stimulus drive.
    assert abs(E_rf - _AUTHOR_E_AT_RF) <= 0.02 * _AUTHOR_E_AT_RF, (
        f"stimulus drive E(0,100)={E_rf:.6f} should already match the author "
        f"{_AUTHOR_E_AT_RF:.6f} (Finding 1); a mismatch here means the stimulus "
        "drive regressed, not the suppressive convolution under test."
    )

    rel_err = abs(S_rf - _AUTHOR_S_AT_RF) / _AUTHOR_S_AT_RF
    assert rel_err <= 0.005, (
        f"suppressive drive S(0,100)={S_rf:.6f} must equal the author "
        f"conv2sepYcirc/upConv value {_AUTHOR_S_AT_RF:.6f} (+/-0.5%); got "
        f"{S_rf:.6f} (rel err {rel_err:.1%}; the committed ~0.001186 is ~17% too "
        "large). Bit-match upConv's circular centre tap on the 361-sample "
        "[-180,180] θ grid in model.py:_separable_conv — do NOT introduce a "
        "suppression gain (none exists; SQ-005/A-013)."
    )


@deterministic_test(
    spec_ref="simulation_protocols.figure_7C", figure=7,
    claim_id="T-A610-7C-ratio",
)
def test_7C_variable_over_fixation_ratio_matches_author_code_tight():
    """MUST-PASS (CODE_BUG): the Fig 7C attend-variable / fixation peak ratio equals
    the AUTHOR CODE / digitized-panel value 1.32 (+/-0.03). The committed model
    renders 1.41 because the suppressive-convolution CODE_BUG (T-A610-7C-suppressive
    -drive) inflates S by ~17%, which propagates through R = A·E/(S+σ) into the
    cross-condition ratio.

    This is a STRICTER must-pass on the SAME quantity AUD-D-7C-ratio measures with a
    loose +/-0.35 band (which 1.41 passes); the 2026-06-10 audit re-derives the
    author target as 1.32 and the digitization audit explicitly refutes the old 1.4.
    Satisfiable by the correct mechanism alone — fixing the convolution convention
    (T-A610-7C-suppressive-drive) drops the ratio from 1.41 to 1.32 with no tuning;
    the +/-0.03 band brackets the author code (1.32) and digitized panel (1.32) and
    excludes the committed 1.41. EXPECTED RED today. Do NOT loosen the band or tune.

    Citation: C-018 / Figure7C.m ; figures/figure_7/panel_C (digitized 1.32).
    """
    out = protocols.run_figure_7C()
    var = np.asarray(out["attend_variable_tuning"], dtype=float)
    base = np.asarray(out["fixation_tuning"], dtype=float)
    model_ratio = float(var.max() / base.max())

    # Anchor on the digitized reference too (a fidelity check, not self-consistency):
    # the digitized attend_variable/fixation peak ratio must itself be ~1.32.
    ref_ratio = ref_peak(7, "C", "attend_variable") / ref_peak(7, "C", "fixation")
    assert abs(ref_ratio - 1.32) < 0.10, (
        f"digitized 7C attend_variable/fixation ratio {ref_ratio:.3f} should be "
        "~1.32 (the audit's refuted-old-1.4 reference); flag the reference if not."
    )

    assert abs(model_ratio - 1.32) <= 0.03, (
        f"7C attend-variable/fixation peak ratio must equal the author/digitized "
        f"1.32 (+/-0.03); got {model_ratio:.3f} (the committed ~1.41 carries the "
        "~17% suppressive-drive inflation). Fix the suppressive circular-θ "
        "convolution convention (T-A610-7C-suppressive-drive); do NOT tune."
    )


# ===========================================================================
# Finding 2 (CODE_BUG, Fig 6C) — the feature-attention field is flat-in-x, which
#   OVER-sharpens vs the author Ashape='cross' (additive-separable plus-shaped
#   field, attentionModel.m:146-162). Measured σ-ratio of the direction tuning
#   (fixation -> attend-feature):
#       impl flat-x : 143 -> 113   (σ-ratio 0.79)   -- over-sharpens
#       author cross: 142 -> 126   (σ-ratio 0.89)
#       digitized C :  61 ->  53   (σ-ratio 0.87)
#   Author code and digitized panel agree (~0.87-0.89); the committed flat-x
#   over-sharpens to 0.79. A-014 correctly rejects the confined G_x·G_θ product
#   (which zeroes the gain at the RF) but its flat-x remedy overshoots the other
#   way. FIX: implement Ashape='cross' (config-selectable, default 'oval') and route
#   6C through it with Figure6C.m params (AxWidth=30, AthetaWidth=60, Apeak=2).
#   Acceptance: σ-ratio in [0.85, 0.90].
# ===========================================================================

# σ-ratio is measured as the FWHM ratio (FWHM = 2.3548·σ for a Gaussian, so the
# ratio is identical). The committed flat-x build gives ~0.79; the author 'cross'
# field and the digitized panel both land in [0.85, 0.90].
_CROSS_SIGMA_RATIO_LO, _CROSS_SIGMA_RATIO_HI = 0.85, 0.90


@deterministic_test(
    spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="T-A610-6C-cross-sigma-ratio",
)
def test_6C_feature_attention_sharpening_matches_author_cross_field():
    """MUST-PASS (CODE_BUG): the Fig 6C direction-tuning σ-ratio (attend-feature
    FWHM / attend-fixation FWHM) lands in [0.85, 0.90] — the value the author
    Ashape='cross' field (0.89) and the digitized panel C (0.87) produce. The
    committed flat-in-x feature field OVER-sharpens to 0.79 (FWHM ~140 -> ~111),
    sharper than either the author code or the digitized panel.

    The flat-x build (A-014) is a partial fix: it correctly avoids the confined
    G_x·G_θ product that zeroes the feature gain at the RF, but it overshoots the
    other way. Satisfiable by the correct mechanism alone: implementing the author
    'cross' Ashape (attentionModel.m:146-162; Figure6C.m AxWidth=30, AthetaWidth=60,
    Apeak=2) reproduces the 0.89 σ-ratio by construction — it is the author's own
    attention-field geometry, not a tuned width. EXPECTED RED today (0.79, below the
    band). Do NOT widen the flat-x field to land in the band — implement 'cross'.

    The band [0.85, 0.90] brackets BOTH the author code (0.89) and the digitized
    panel (0.87) and excludes the committed 0.79; it is a fidelity target read from
    the author script + digitized reference, not from this record.

    Citation: attentionModel.m:146-162 (Ashape=='cross') ; Figure6C.m:5-7 ;
    figures/figure_6/panel_C (digitized σ-ratio ~0.87).
    """
    out = protocols.run_figure_6C(n_directions=49)
    theta = np.asarray(out["theta_stim_grid"], dtype=float)
    fixation = np.asarray(out["attend_fixation_tuning"], dtype=float)
    attend_feature = np.asarray(out["attend_opposite_stimulus_tuning"], dtype=float)

    fwhm_fix = fwhm(fixation, theta)
    fwhm_att = fwhm(attend_feature, theta)
    assert fwhm_fix > 0.0, "degenerate fixation tuning curve (zero FWHM)"
    sigma_ratio = fwhm_att / fwhm_fix

    assert _CROSS_SIGMA_RATIO_LO <= sigma_ratio <= _CROSS_SIGMA_RATIO_HI, (
        f"6C feature-attention σ-ratio (FWHM {fwhm_att:.1f} / {fwhm_fix:.1f} = "
        f"{sigma_ratio:.3f}) must land in [{_CROSS_SIGMA_RATIO_LO}, "
        f"{_CROSS_SIGMA_RATIO_HI}] — the author Ashape='cross' (0.89) / digitized "
        f"(0.87) value. The committed flat-in-x build over-sharpens to ~0.79. "
        "Implement the author 'cross' attention field (attentionModel.m:146-162; "
        "Figure6C.m AxWidth=30, AthetaWidth=60, Apeak=2); do NOT tune the flat-x "
        "width to fit the band."
    )


# ===========================================================================
# Finding 3 (GENUINE_DIVERGENCE, Figure 1) — the rendered "Output firing rate"
#   panel shows attended (right) and unattended (left) bands at essentially equal
#   brightness: R_attended/R_unattended = 1.0098. The paper's Fig-1 population
#   panel draws the attended band clearly brighter. This is the FAITHFUL behaviour
#   of the equations for broad spatial attention on a single isolated stimulus (γ
#   multiplies E in the numerator AND the locally-pooled S in the denominator, so
#   the gain nearly cancels). Fig 1 is a mechanism schematic with no Figure1.m to
#   pin its exact contrast/γ. RED TRIPWIRE: flips green only if the model genuinely
#   produces a visible attended-band enhancement; never a fit target.
# ===========================================================================

@tier_test(
    tier="soft", spec_ref="simulation_protocols.figure_1", figure=1,
    claim_id="T-A610-1-output-enhancement-tripwire",
    paper_issue="Figure 1 rendered 'Output firing rate' panel shows attended/"
    "unattended bands at ~equal brightness (R ratio 1.0098) while the paper draws "
    "the attended band clearly brighter. GENUINE_DIVERGENCE: faithful behaviour of "
    "the equations for broad spatial attention on a single isolated stimulus (γ "
    "multiplies both numerator E and the locally-pooled denominator S, nearly "
    "cancelling). No Figure1.m pins the schematic's contrast/γ. Flips green only if "
    "the model genuinely renders a visible enhancement; do NOT tune γ to force it.",
)
def test_figure_1_output_band_shows_attended_enhancement():
    """RED TRIPWIRE (GENUINE_DIVERGENCE): the Fig-1 output-rate panel enhances the
    attended (right) band over the unattended (left) band by a VISIBLE margin —
    require R_attended/R_unattended >= 1.10 (a band a viewer would read as
    "clearly brighter"). The faithful equations give ~1.0098 (the γ gain nearly
    cancels between numerator and the locally-pooled denominator for broad spatial
    attention on one isolated stimulus), so this is EXPECTED to xfail.

    It flips green ONLY if the model genuinely produces the enhancement the paper's
    panel illustrates — a progress signal, never a fit target. Figure 1 is a
    mechanism schematic with NO Figure1.m to pin its contrast/γ, so do NOT tune γ or
    the contrast to force the band brighter. Soft tier: measured & reported, never
    gates.

    Citation: paper Fig 1 caption ('white indicates a value greater than 1 … output
    firing rates') ; protocols.run_figure_1 (R_at_attended / R_at_unattended).
    """
    out = protocols.run_figure_1()
    r_att = float(out["R_at_attended"])
    r_unatt = float(out["R_at_unattended"])
    ratio = r_att / max(r_unatt, 1e-12)
    assert ratio >= 1.10, (
        f"Fig-1 output band attended/unattended ratio {ratio:.4f} must be a "
        "visible enhancement (>=1.10) to match the paper's panel; the faithful "
        "equations give ~1.0098 (the γ gain nearly cancels). This is a progress "
        "tripwire — flips green only on a genuine improvement; do NOT tune γ/"
        "contrast to force it."
    )
