"""Tests encoding the 2026-06-10 INDEPENDENT RE-RENDER audit findings (author-tests skill).

This module is the machine-checkable form of the 2026-06-10 independent re-render +
author-code reproduction audit (HEAD commit 37bba4e; report
logs/faithfulness_audit/2026-06-10-independent-rerender.md). That audit RE-ROOT-CAUSED
and PARTLY RE-TAGGED the earlier same-day audit (commit 8540de0, whose tests this file
previously held). This rewrite carries the CORRECTED findings, not the superseded ones.

WHAT CHANGED VS THE EARLIER 2026-06-10 AUDIT (and the prior version of this file):

  - Figure 7C (CODE_BUG, model scope): the var-attend / fixation peak ratio renders
    1.413 vs author code 1.323 and digitized panel 1.325. The earlier audit blamed the
    suppressive circular-θ CONVOLUTION OPERATOR (FFT wrap/centre vs MATLAB upConv). The
    re-render audit REFUTES that: it proved impl ``_separable_conv`` is bit-identical to
    the author ``conv2sepYcirc`` on an identical 361 grid + identical input + kernels
    (max-abs-diff = 0). The real cause is TWO θ-STIMULUS CONVENTION mismatches:
      (1) ``build_stimulus_drive`` (model.py:213) builds the per-stimulus θ profile with
          ``gaussian_periodic_1d`` (WRAPS at ±180), whereas the author uses a NON-periodic
          ``makeGaussian``/normpdf over ``theta=[-180:180]'``. For the NULL stimulus at
          θ=180 (the +180 edge) the periodic form wraps the off-grid tail back, inflating
          that stimulus's θ-column mass by +43% (1.7533 -> 2.5066). The null contributes
          ONLY to suppression S, so S inflates (S(0,100)=0.001186 vs author 0.001012, +17%),
          depressing the fixation/away baseline and inflating the ratio.
      (2) The θ grid is ``arange(-180,180)`` = 360 samples (drops the +180 endpoint) while
          the author grid is the 361-sample ``arange(-180,181)``; model.py:24 docstring
          even claims "361 samples", contradicting the code.
    FIX (from the finding): adopt the 361-sample θ buffer and a NON-periodic Gaussian for
    the per-stimulus θ profile (the suppressive/stimulation/attention KERNELS stay
    circular — that operator is already correct). Acceptance: S(0,100)=0.001012 (±0.5%)
    and the 7C var/fixation ratio = 1.32 (±0.03).

  - Figure 6C (RE-TAGGED CODE_BUG -> GENUINE_DIVERGENCE): the earlier audit claimed the
    committed flat-x feature field OVER-sharpens to σ-ratio 0.79 (a "major CODE_BUG") and
    made it a MUST-PASS in [0.85,0.90]. The re-render audit measured the CURRENTLY
    committed render at FWHM-ratio 0.875, which MATCHES the author 'cross' build (0.886)
    and the digitized panel (~0.87): the figure OUTPUT is faithful. The mechanism is still
    a flat-x proxy, not the author 'cross', so the audit keeps it a GENUINE_DIVERGENCE with
    NO FIX REQUIRED while the output stays at ~0.87. Per skills/author-tests/SKILL.md this
    means a RED TRIPWIRE, NOT a must-pass — a must-pass [0.85,0.90] would be a fit target
    the implementer could only "hit" by tuning the proxy width (the exact laundering the
    pipeline exists to prevent). The prior MUST-PASS form is therefore REMOVED.

Tag -> test kind (skills/author-tests/SKILL.md):

  - CODE_BUG -> MUST-PASS (Finding 1 / Figure 7C; and the CONTRACT_BUG calibration pin).
    The faithful mechanism reaches the AUTHOR value once the θ-stimulus convention (361
    grid + non-periodic profile) is corrected. Targets are AUTHOR-CODE reruns cross-checked
    against the digitized panels — not a re-derivation from the record the protocol draws
    from, and not a figure fit.
  - GENUINE_DIVERGENCE -> RED TRIPWIRE (soft) (Finding 2 / Figure 6C mechanism; Finding 3 /
    Figure 1). Flips green only if the model genuinely improves; never a fit target.

ALREADY-DISPOSITIONED, NOT DUPLICATED HERE:
  - Figure 4C (PAPER_ISSUE — published panel draws attend-RF above) is faithful to the
    author Figure4C.m with NO change required; fully encoded by
    test_dr_4c_sign_resolution.py (DR-4C-sign). Re-confirmed by the re-render audit.
  - Figs 2A/2B/3C/3F/4E/5C single-stimulus forward model + Eqs 1-2/5-6 + ledger (FAITHFUL)
    record no divergence; no test.

RELATIONSHIP TO test_audit_2026_06_04.py (left in place, not silently re-resolved):
  - AUD-D-7C-ratio asserts ``abs(ratio - ~1.33) < 0.35``; the impl's 1.41 PASSES that loose
    band. T-A610-7C-ratio below is a STRICTER must-pass on the SAME quantity (1.32 ± 0.03)
    that 1.41 FAILS. Both go green together once the θ-stimulus convention is fixed.

CONFLICT FLAGGED FOR THE 6C TRIPWIRE (read test_6C_feature_attention_field_is_author_cross):
  The finding's "committed render = 0.875 (faithful)" was measured by the auditor with a
  GAUSSIAN-σ FIT to the rendered curve. The repo's ``rh_claim_helpers.fwhm`` (raw half-max
  crossing, grid-quantized) gives ~0.79 on the SAME ``run_figure_6C`` record at every
  ``n_directions`` (0.778 @25, 0.790 @49, 0.813 @121). The two estimators disagree on the
  SAME committed output (σ-fit 0.875 vs half-max-crossing 0.79). I therefore key the 6C
  tripwire to the MECHANISM (flat-x proxy ≠ author 'cross'), which is the unambiguous,
  estimator-independent content of the GENUINE_DIVERGENCE — NOT to a numeric FWHM-ratio
  band, which would read RED under ``fwhm`` even though the auditor calls the output
  faithful, and would mis-signal "improvement needed" where the finding says none is. See
  that test's docstring for the full rationale.
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
# Finding 1 (CODE_BUG, model scope; visible in Fig 7C) — θ-stimulus convention
#   mismatch (periodic-wrap stimulus profile + 360-vs-361 θ grid), NOT the
#   convolution operator. On the no-attention two-stimulus pair (x=93 θ=0,
#   x=107 θ=180, contrast 1) at the recorded neuron (x=100, θ=0):
#       impl  : S(0,100) = 0.001186 (+17%), E(0,100) = 0.00730
#       author: S(0,100) = 0.001012,        E(0,100) = 0.00728
#   The +17% S comes from the NULL stimulus at the +180 edge: the periodic θ
#   profile wraps its off-grid tail back (θ-column mass +43%), and the 360-sample
#   grid drops the +180 endpoint. The null feeds suppression ONLY, so S inflates,
#   the fixation/away baseline drops, and R = A·E/(S+σ) carries it into the Fig 7C
#   var/fixation ratio: 1.41 vs author/digitized 1.32.
#   FIX: 361-sample θ buffer arange(-180,181) + NON-periodic per-stimulus θ profile
#        (kernels stay circular). model.py:24 docstring also wrongly says 360->361.
# ===========================================================================

# The author no-attention two-stimulus pair (Finding 1 / Figure7C.m geometry).
_PAIR_STIMULI = [
    {"x": 93.0, "theta": 0.0, "contrast": 1.0},     # variable grating, preferred dir
    {"x": 107.0, "theta": 180.0, "contrast": 1.0},  # fixed null grating (the +180 edge)
]
_RECORDED_X, _RECORDED_THETA = 100.0, 0.0

# Author-code targets (Finding 1): S from the non-periodic θ profile on the 361 grid,
# E unchanged (already matches — the stimulus θ profile change leaves the recorded
# preferred-direction column essentially untouched; only the edge null moves).
_AUTHOR_S_AT_RF = 0.001012     # impl currently 0.001186 (~17% too large)
_AUTHOR_E_AT_RF = 0.00728      # impl currently 0.00730 (already matches)


def _no_attention_pair_fields():
    """Run the no-attention 7C-geometry pair and return (S, E) at the recorded RF.

    Uses the SAME ``simulate`` and the SAME 7C calibration the protocol uses, with
    attention OFF (A == 1 everywhere), isolating the θ-stimulus drive + suppressive
    pool from the attention field. Evaluated on the model's own S/E fields; the
    EXPECTED value is the AUTHOR CODE result (makeGaussian non-periodic θ profile on
    the 361 grid, then conv2sepYcirc), not a re-derivation from this record.

    Citation: Finding 1 ; Figure7C.m:9 (theta=[-180:180]') ; makeGaussian.m (normpdf,
    non-periodic) ; build_stimulus_drive model.py:210-217 (gaussian_periodic_1d).
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
    spec_ref="pipeline.build_stimulus_drive", figure=7,
    claim_id="T-A610-7C-theta-grid-361",
)
def test_theta_grid_is_author_361_samples():
    """MUST-PASS (CODE_BUG, fix part b): the θ grid is the author's 361-sample buffer
    ``arange(-180, 181)`` spanning the CLOSED interval [-180, 180]. The committed grid
    is ``arange(-180, 180)`` = 360 samples and DROPS the +180 endpoint, while
    model.py:24's docstring falsely claims "361 samples". The dropped endpoint is where
    the Fig-7C null stimulus sits (θ=180), so the missing column is part of the
    suppressive-mass inflation Finding 1 root-causes.

    Satisfiable by the correct mechanism alone: adopting the author's closed-interval
    θ buffer is a grid-definition change with no free parameter. EXPECTED RED today
    (360 samples, max θ = 179).

    Citation: Finding 1 fix (b) ; Figure7C.m:9 theta=[-180:180]' (361) ;
    model.py:65-67 (arange(-180,180)=360) ; model.py:24 docstring ('361 samples').
    """
    params = default_params(
        stimulus_size=5.0, attention_field_size=5.0,
        peak_attention_gain_gamma=5.0, tuning_width=45.0,
        recorded_x=_RECORDED_X, recorded_theta=_RECORDED_THETA,
    )
    theta = np.asarray(params.theta_grid, dtype=float)
    assert theta.size == 361, (
        f"θ grid must be the author's 361-sample closed buffer arange(-180,181); got "
        f"{theta.size} samples (the committed arange(-180,180)=360 drops the +180 "
        "endpoint where the 7C null stimulus sits). Fix the grid in model.py:65-67 and "
        "the model.py:24 docstring (it wrongly says '361 samples')."
    )
    assert theta[0] == -180.0 and theta[-1] == 180.0, (
        f"θ grid must span the CLOSED [-180, 180] (endpoints {theta[0]}..{theta[-1]}); "
        "the +180 endpoint must be present (it carries the null-stimulus θ column)."
    )


@deterministic_test(
    spec_ref="pipeline.compute_suppressive_drive", figure=7,
    claim_id="T-A610-7C-suppressive-drive",
)
def test_no_attention_suppressive_drive_matches_author_nonperiodic_theta():
    """MUST-PASS (CODE_BUG, Finding 1): on the no-attention two-stimulus pair
    (x=93 θ=0, x=107 θ=180, contrast 1) the suppressive drive at the recorded neuron
    (x=100, θ=0) equals the author value S(0,100)=0.001012 (±0.5%). The committed model
    gives 0.001186 — ~17% too large — because the per-stimulus θ profile is built with
    ``gaussian_periodic_1d`` (WRAPS the +180-edge null's off-grid tail back, inflating
    its θ-column mass +43%) on a 360-sample grid that also drops the +180 endpoint.

    NOTE — this REVISES the prior root cause: the convolution operator is NOT to blame.
    The re-render audit proved ``_separable_conv`` is bit-identical to the author
    ``conv2sepYcirc`` (max-abs-diff = 0). Do NOT touch the convolution; fix the
    θ-STIMULUS profile (non-periodic Gaussian) and the θ grid (361).

    Satisfiable by the correct mechanism alone: replacing the per-stimulus θ profile
    with a non-periodic Gaussian on the 361 grid lands S at the author value with no
    free parameter. E is asserted unchanged (already matches), pinning the failure to
    the θ-stimulus drive, NOT a suppression gain (there is none; A-013 / SQ-005).
    EXPECTED RED today (0.001186).

    Citation: Finding 1 ; build_stimulus_drive model.py:210-217 (gaussian_periodic_1d)
    vs makeGaussian.m (normpdf, non-periodic) ; Figure7C.m:9 theta=[-180:180]'.
    """
    S_rf, E_rf = _no_attention_pair_fields()

    # Guard: E must already match the author drive (Finding 1: E faithful). This pins
    # the failure to the θ-STIMULUS / suppressive mass, not the preferred-column drive.
    assert abs(E_rf - _AUTHOR_E_AT_RF) <= 0.02 * _AUTHOR_E_AT_RF, (
        f"stimulus drive E(0,100)={E_rf:.6f} should already match the author "
        f"{_AUTHOR_E_AT_RF:.6f} (Finding 1); a mismatch here means the recorded-column "
        "drive regressed, not the edge-null θ profile under test."
    )

    rel_err = abs(S_rf - _AUTHOR_S_AT_RF) / _AUTHOR_S_AT_RF
    assert rel_err <= 0.005, (
        f"suppressive drive S(0,100)={S_rf:.6f} must equal the author non-periodic-θ "
        f"value {_AUTHOR_S_AT_RF:.6f} (±0.5%); got {S_rf:.6f} (rel err {rel_err:.1%}; "
        "the committed ~0.001186 is ~17% too large). Build the per-stimulus θ profile "
        "with a NON-periodic Gaussian on the 361-sample grid (model.py:213) — do NOT "
        "touch the bit-identical convolution and do NOT add a suppression gain "
        "(SQ-005/A-013)."
    )


@deterministic_test(
    spec_ref="simulation_protocols.figure_7C", figure=7,
    claim_id="T-A610-7C-ratio",
)
def test_7C_variable_over_fixation_ratio_matches_author_code_tight():
    """MUST-PASS (CODE_BUG, Finding 1): the Fig 7C attend-variable / fixation peak ratio
    equals the AUTHOR CODE / digitized-panel value 1.32 (±0.03). The committed model
    renders 1.41 because the θ-stimulus convention bug (T-A610-7C-suppressive-drive)
    inflates S by ~17%, propagating through R = A·E/(S+σ) into the cross-condition ratio.

    This is a STRICTER must-pass on the SAME quantity AUD-D-7C-ratio measures with a
    loose ±0.35 band (which 1.41 passes); the re-render audit re-derives the author
    target as 1.323 and the digitized panel as 1.325 (the digitization audit explicitly
    refutes the old 1.4). Satisfiable by the correct mechanism alone — fixing the
    θ-stimulus convention drops the ratio from 1.41 to ~1.32 with no tuning; the ±0.03
    band brackets author (1.323) and digitized (1.325) and excludes the committed 1.41.
    EXPECTED RED today. Do NOT loosen the band or tune.

    Citation: Finding 1 ; Figure7C.m ; figures/figure_7/panel_C (digitized 1.325).
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
        f"7C attend-variable/fixation peak ratio must equal the author/digitized 1.32 "
        f"(±0.03); got {model_ratio:.3f} (the committed ~1.41 carries the ~17% "
        "suppressive-drive inflation from the periodic-θ stimulus profile). Fix the "
        "θ-stimulus convention (T-A610-7C-suppressive-drive / -theta-grid-361); do NOT "
        "tune."
    )


# ===========================================================================
# Finding 2 (GENUINE_DIVERGENCE, Fig 6C) — the feature-attention field is a
#   flat-in-x proxy (run_figure_6C: spatial_center=None, invented geometry
#   x_opposite=-50, x_fixation=50), not the author Ashape='cross'
#   (attentionModel.m:146-162; Figure6C.m Ax=-100, AxWidth=30, attend-fixation
#   Ax=0). On the CURRENTLY committed render the audit measured the 6C FWHM ratio
#   (σ-fit) at 0.875, matching the author 'cross' (0.886) and the digitized panel
#   (~0.87): the figure OUTPUT is faithful. So per the finding NO FIX is required
#   while the output stays at ~0.87 — this is a RED TRIPWIRE on the MECHANISM, not
#   a must-pass on a number (a numeric band here would be a tune-to-fit target).
# ===========================================================================

@tier_test(
    tier="soft", spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="T-A610-6C-cross-mechanism-tripwire",
    paper_issue="Figure 6C attend-feature condition is built as a FLAT-IN-X proxy "
    "(run_figure_6C: spatial_center=None, invented x_opposite=-50/x_fixation=50), not "
    "the author Ashape='cross' (attentionModel.m:146-162; Figure6C.m Ax=-100, "
    "AxWidth=30, attend-fixation Ax=0). GENUINE_DIVERGENCE: the committed OUTPUT is "
    "faithful (re-render FWHM σ-ratio 0.875 vs author 'cross' 0.886, digitized ~0.87), "
    "but the MECHANISM is a proxy. No fix required while the output stays at ~0.87. "
    "Flips green only if 6C is genuinely routed through the author 'cross' field; never "
    "a tune-to-fit target.",
)
def test_6C_feature_attention_field_is_author_cross():
    """RED TRIPWIRE (GENUINE_DIVERGENCE, Finding 2): the Fig 6C attend-feature condition
    is produced by the author 'cross' attention field, not the flat-in-x proxy. We probe
    the MECHANISM directly: the proxy sets ``spatial_center=None`` and invents geometry
    (x_opposite=-50, x_fixation=50), whereas the author 'cross' build is spatially
    structured (Ax=-100, AxWidth=30; attend-fixation Ax=0). This test xfails while the
    proxy is in place and flips green only when 6C is routed through the author 'cross'
    field — a progress signal, NEVER a fit target. Soft tier: measured & reported, never
    gates.

    WHY THIS IS A MECHANISM TRIPWIRE, NOT A NUMERIC FWHM-RATIO MUST-PASS
    -------------------------------------------------------------------
    The finding tags 6C GENUINE_DIVERGENCE and says NO FIX is required while the output
    stays at ~0.87 — so by skills/author-tests/SKILL.md it must be a tripwire, never a
    must-pass (a must-pass band would hand the implementer a tune-to-fit target on the
    proxy width). I additionally do NOT key the tripwire to a numeric FWHM-ratio band
    because the two estimators disagree on the SAME committed output: the auditor's
    Gaussian-σ fit reads 0.875 (faithful), while the repo's ``rh_claim_helpers.fwhm``
    (raw half-max crossing) reads ~0.79 on the same ``run_figure_6C`` record at every
    n_directions. A band keyed to ``fwhm`` would read RED today even though the auditor
    calls the output faithful, mis-signalling "improvement needed". The unambiguous,
    estimator-independent content of the divergence is the MECHANISM (proxy ≠ 'cross'),
    so that is what flips this tripwire.

    (For reference only, the σ-ratio is REPORTED below via ``fwhm`` — its value does not
    gate this test.)

    Citation: Finding 2 ; protocols.py:388-441 (flat-x proxy) vs Figure6C.m:3-7
    (Ashape='cross', Ax=-100, AxWidth=30) + attentionModel.m:146-162 ; A-014 / SQ-006.
    """
    # Report the σ-ratio (does not gate — see docstring on the estimator conflict).
    out = protocols.run_figure_6C(n_directions=49)
    theta = np.asarray(out["theta_stim_grid"], dtype=float)
    fixation = np.asarray(out["attend_fixation_tuning"], dtype=float)
    attend_feature = np.asarray(out["attend_opposite_stimulus_tuning"], dtype=float)
    fwhm_fix = fwhm(fixation, theta)
    sigma_ratio = (fwhm(attend_feature, theta) / fwhm_fix) if fwhm_fix > 0 else float("nan")

    # The MECHANISM gate: is 6C routed through the author 'cross' field?
    # The flat-x proxy is detectable by its signature default geometry; the author
    # 'cross' build replaces it with the spatially-structured Ax=-100/AxWidth=30 field.
    src = __import__("inspect").getsource(protocols.run_figure_6C)
    is_flat_x_proxy = ("x_opposite" in src) and ("x_fixation" in src) and (
        "spatial_center" in src and "None" in src
    ) and ("cross" not in src.lower())

    assert not is_flat_x_proxy, (
        "Fig 6C attend-feature is still built by the FLAT-IN-X proxy (signature: "
        "x_opposite/x_fixation + spatial_center=None, no 'cross'); the author "
        "Ashape='cross' field (attentionModel.m:146-162; Figure6C.m Ax=-100, AxWidth=30, "
        "AthetaWidth=60, attend-fixation Ax=0) is not yet wired in. The output happens to "
        f"be faithful today (reported σ-ratio via fwhm = {sigma_ratio:.3f}; auditor "
        "σ-fit 0.875), so NO fix is required while it stays at ~0.87 — this tripwire "
        "flips green only when 6C genuinely routes through the author 'cross' field. Do "
        "NOT tune the proxy width to silence it."
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
    """RED TRIPWIRE (GENUINE_DIVERGENCE, Finding 3): the Fig-1 output-rate panel enhances
    the attended (right) band over the unattended (left) band by a VISIBLE margin —
    require R_attended/R_unattended >= 1.10 (a band a viewer would read as "clearly
    brighter"). The faithful equations give ~1.0098 (the γ gain nearly cancels between
    numerator and the locally-pooled denominator for broad spatial attention on one
    isolated stimulus), so this is EXPECTED to xfail.

    It flips green ONLY if the model genuinely produces the enhancement the paper's panel
    illustrates — a progress signal, never a fit target. Figure 1 is a mechanism
    schematic with NO Figure1.m to pin its contrast/γ, so do NOT tune γ or the contrast
    to force the band brighter. Soft tier: measured & reported, never gates.

    Citation: Finding 3 ; paper Fig 1 caption ('white indicates a value greater than 1 …
    output firing rates') ; protocols.run_figure_1 (R_at_attended / R_at_unattended).
    """
    out = protocols.run_figure_1()
    r_att = float(out["R_at_attended"])
    r_unatt = float(out["R_at_unattended"])
    ratio = r_att / max(r_unatt, 1e-12)
    assert ratio >= 1.10, (
        f"Fig-1 output band attended/unattended ratio {ratio:.4f} must be a visible "
        "enhancement (>=1.10) to match the paper's panel; the faithful equations give "
        "~1.0098 (the γ gain nearly cancels). This is a progress tripwire — flips green "
        "only on a genuine improvement; do NOT tune γ/contrast to force it."
    )


# ===========================================================================
# CONTRACT_BUG (Figs 2/3/4 figure_*.md docs) — the human-facing figure_3.md still
#   documents the RETIRED A-007 baselines (0.05/0.05), contradicting the BINDING
#   calibration CODE-017 (baseline_modulated=5e-7; baseline_unmodulated=5.0 for 3C /
#   0.0 for 3F). The figure PNG OUTPUTS are faithful; this is doc-vs-contract drift.
#   The doc REWRITE (figure_3.md / figure_4.md Panel-C) is owned by the spec audit
#   (logs/spec_audit/contract_audit_2026-06-10.md) and is out of test-authoring scope.
#   What IS machine-checkable here: PIN the binding calibration to CODE-017 so the
#   contract the docs must be rewritten to match cannot silently drift back. This is a
#   MUST-PASS guard (it is GREEN today — the code already holds CODE-017 — and serves
#   as the regression tripwire that keeps it that way).
# ===========================================================================

@deterministic_test(
    spec_ref="calibration.figure_3_baselines", figure=3,
    claim_id="T-A610-3-baseline-code017-pin",
)
def test_figure_3_baselines_are_code017_not_retired_a007():
    """MUST-PASS GUARD (CONTRACT_BUG): the binding Fig-3 baselines are CODE-017
    (baseline_modulated=5e-7; baseline_unmodulated=5.0 for 3C, 0.0 for 3F), NOT the
    retired A-007 0.05/0.05 that figure_3.md still teaches. This pins the contract the
    figure_3.md rewrite must match (the doc edit itself is owned by the spec audit,
    logs/spec_audit/contract_audit_2026-06-10.md; out of test-authoring scope). GREEN
    today — the code already holds CODE-017 — and stays green as a regression tripwire
    against drifting back to the retired baselines.

    Citation: Finding CONTRACT_BUG ; calibration.yaml CODE-017 ; Figure3C/F.m:5-6
    (baselineMod, baselineUnmod) ; logs/spec_audit/contract_audit_2026-06-10.md (F3).
    """
    c = resolve_namespace("figure_3C")
    f = resolve_namespace("figure_3F")

    assert abs(c["baseline_modulated"] - 5e-7) <= 1e-12, (
        f"3C baseline_modulated must be CODE-017 5e-7; got {c['baseline_modulated']!r} "
        "(the retired A-007 value was 0.05 — figure_3.md still teaches it; rewrite the "
        "doc to CODE-017 per the spec audit)."
    )
    assert c["baseline_unmodulated"] == 5.0, (
        f"3C baseline_unmodulated must be CODE-017 5.0; got {c['baseline_unmodulated']!r} "
        "(retired A-007 was 0.05)."
    )
    assert abs(f["baseline_modulated"] - 5e-7) <= 1e-12, (
        f"3F baseline_modulated must be CODE-017 5e-7; got {f['baseline_modulated']!r}."
    )
    assert f["baseline_unmodulated"] == 0.0, (
        f"3F baseline_unmodulated must be CODE-017 0.0; got {f['baseline_unmodulated']!r} "
        "(retired A-007 was 0.05)."
    )
