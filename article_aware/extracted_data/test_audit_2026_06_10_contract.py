"""Tests encoding the 2026-06-10 CONTRACT-AUDIT findings (author-tests skill).

This module carries the 2026-06-10 contract-vs-code audit that RE-ROOT-CAUSED and
SHARPENED the same-day re-render findings. It supersedes the relevant parts of
``test_audit_2026_06_10.py`` (Finding 2 / Fig 6C) and ``test_figure_6C_code_bug.py``
(the 2026-06-03 spatial-confinement framing), which described an EARLIER model state
("curves overlap, peak ratio ~1.01, no sharpening") that the model has since moved
past. The committed model now OVER-corrects, and the binding ledger says the geometry
is wrong — that is the finding this file encodes.

WHAT THE NEW AUDIT FOUND (and why the prior 6C encoding is stale)
----------------------------------------------------------------
Figure 6C (CONTRACT_BUG -> MUST-PASS). ``run_figure_6C`` ignores the author geometry
it ALREADY records as BINDING ledger keys (calibration.yaml:638-702):

    figure_6C.stim_rf_x        = 100.0   (recorded column == RF stimulus)
    figure_6C.stim_contra_x    = -100.0  (contralateral / attend-opposite centre)
    figure_6C.attend_fixation_x = 0.0    (attend-fixation flat-θ baseline centre)

and the tuning_width note documents Ashape='cross' (CODE-018, the C-017 mechanism).
Instead the code hard-codes ``x_opposite=-50.0, x_fixation=50.0`` (protocols.py:388),
puts the RF stimulus at ``x=0`` (not 100), and builds the attend-feature field as a
FLAT-IN-X, full-γ θ-selective proxy (``spatial_center=None, feature_center=θ_stim``).
No 'cross' (additive separable spatial×feature) attention shape exists anywhere.

The DIRECTION is faithful (feature attention scales + sharpens the recorded tuning),
but the flat-x full-γ proxy applies the θ-gain at FULL strength everywhere in x, so it
OVER-scales and OVER-sharpens. Measured on the committed model:

                                impl       author 'cross'   digitized panel
    peak ratio (feat/fix)       1.167-1.168    1.109            1.108
    FWHM ratio (feat/fix)       0.79-0.823     0.886-0.889      ~0.87

The binding contract says one thing; the code does another. This is a CONTRACT_BUG,
not a genuine divergence: the FAITHFUL author 'cross' mechanism lands at the digitized
panel (peak 1.108, FWHM ratio ~0.87-0.89), so the targets below are reachable by the
CORRECT mechanism alone — they are NOT a fit target. The implementer drives them green
by (a) routing 6C through the ledger geometry (RF stimulus at stim_rf_x=100, contra at
stim_contra_x=-100, attend-fixation at attend_fixation_x=0) and (b) implementing the
author 'cross' attention shape (attentionModel.m:146-162; Figure6C.m AxWidth=30,
AthetaWidth=60), NOT by tuning the proxy's γ or width.

Acceptance (from the finding, anchored to the digitized panel + author code):
    6C peak ratio  = 1.108  (±0.01)   — EXCLUDES the committed 1.167
    6C FWHM ratio  = 0.87-0.89        — EXCLUDES the committed 0.79

Tag -> test kind (skills/author-tests/SKILL.md): CONTRACT_BUG -> MUST-PASS. The
faithful 'cross' mechanism reaches the digitized/author value once the geometry +
shape are corrected; the band is keyed to the DIGITIZED reference (a fidelity check,
not the record the protocol draws from), and brackets the author 'cross' reproduction.

RELATIONSHIP TO THE PRIOR-SAME-DAY 6C ENCODING (left in place where harmless, FIXED
where it now ASSERTS a stale state):
  - ``test_audit_2026_06_10.py``::test_6C_feature_attention_field_is_author_cross is a
    soft MECHANISM tripwire (proxy ≠ 'cross'). It stays valid (the proxy IS still in
    place) and is complementary: this file additionally pins the NUMERIC contract the
    'cross' fix must hit. The two go green together.
  - ``test_figure_6C_code_bug.py`` asserted peak ratio >= 1.08 and sharpening >= 18°,
    which the OVER-scaled committed state (1.167 / 30°) PASSES — i.e. those bounds are
    too loose and let the contract bug through; the >=18° bound would even REJECT the
    correct mechanism (author sharpening ~17°). Those stale bounds are RETIRED in that
    file and superseded by the tight, correct two-sided bands here. See the retirement
    note left in test_figure_6C_code_bug.py.
"""

from __future__ import annotations

import inspect

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import fwhm
from rh_model import protocols
from rh_tier_helpers import ref_peak

# Digitized-panel acceptance band (from the finding; verified: ref_peak ratio = 1.1074).
_DIGITIZED_PEAK_RATIO = 1.108
_PEAK_RATIO_TOL = 0.01
# FWHM-ratio band: author 'cross' 0.886-0.889, digitized ~0.87 -> accept [0.87, 0.89].
_FWHM_RATIO_LO, _FWHM_RATIO_HI = 0.87, 0.89


def _record(n_directions: int = 73):
    """Run 6C at a fine grid and return (theta, attend_fixation, attend_feature)."""
    out = protocols.run_figure_6C(n_directions=n_directions)
    theta = np.asarray(out["theta_stim_grid"], dtype=float)
    fixation = np.asarray(out["attend_fixation_tuning"], dtype=float)
    feature = np.asarray(out["attend_opposite_stimulus_tuning"], dtype=float)
    return theta, fixation, feature


@deterministic_test(
    spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="T-A610C-6C-peak-ratio",
)
def test_6C_feature_peak_ratio_matches_author_cross():
    """MUST-PASS (CONTRACT_BUG, Fig 6C): the attend-feature / attend-fixation peak
    ratio equals the digitized-panel / author-'cross' value 1.108 (±0.01). The
    committed flat-x full-γ proxy OVER-scales to ~1.167 because it applies the θ-gain
    at full strength everywhere in x instead of the author additive 'cross' field
    (attentionModel.m:146-162). EXPECTED RED today (~1.167, |Δ|≈0.06 ≫ 0.01).

    Satisfiable by the CORRECT mechanism alone: routing 6C through the ledger geometry
    (RF stimulus at figure_6C.stim_rf_x=100, contra at stim_contra_x=-100, attend-
    fixation at attend_fixation_x=0) and the author 'cross' shape (AxWidth=30,
    AthetaWidth=60) lands the peak ratio at the digitized 1.108 — verified author
    reproduction 1.109. Do NOT tune the proxy γ/width to silence it (that would be the
    laundering the pipeline exists to prevent).

    The target is anchored to the DIGITIZED reference (ref_peak), not to the record the
    protocol draws from — a fidelity check, not self-consistency.

    Citation: Finding 6C CONTRACT_BUG ; calibration.yaml:638-702 (stim_rf_x=100,
    stim_contra_x=-100, attend_fixation_x=0; Ashape='cross') ; Figure6C.m:3-25 +
    attentionModel.m:146-162 ; protocols.py:388-441 (hard-coded -50/50 flat-x proxy) ;
    figures/figure_6/panel_C (digitized peak ratio 1.107).
    """
    theta, fixation, feature = _record()
    model_ratio = float(feature.max() / max(fixation.max(), 1e-12))

    # Fidelity anchor: the digitized panel ratio must itself be ~1.108 (flag if not).
    ref_ratio = ref_peak(6, "C", "attend_contralateral") / ref_peak(6, "C", "attend_fixation")
    assert abs(ref_ratio - _DIGITIZED_PEAK_RATIO) < 0.01, (
        f"digitized 6C attend-feature/attend-fixation peak ratio {ref_ratio:.4f} should "
        f"be ~{_DIGITIZED_PEAK_RATIO} (the author 'cross' target); flag the reference if "
        "it has drifted before chasing this test."
    )

    assert abs(model_ratio - _DIGITIZED_PEAK_RATIO) <= _PEAK_RATIO_TOL, (
        f"6C attend-feature/attend-fixation peak ratio must equal the digitized/author-"
        f"'cross' {_DIGITIZED_PEAK_RATIO} (±{_PEAK_RATIO_TOL}); got {model_ratio:.4f} "
        "(the committed ~1.167 OVER-scales because the flat-x full-γ proxy applies the "
        "θ-gain at full strength everywhere in x). Route 6C through the ledger geometry "
        "(stim_rf_x=100/stim_contra_x=-100/attend_fixation_x=0) and the author 'cross' "
        "shape (AxWidth=30, AthetaWidth=60); do NOT tune."
    )


@deterministic_test(
    spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="T-A610C-6C-fwhm-ratio",
)
def test_6C_feature_fwhm_ratio_matches_author_cross():
    """MUST-PASS (CONTRACT_BUG, Fig 6C): the attend-feature / attend-fixation FWHM
    ratio is in the author-'cross' / digitized band [0.87, 0.89]. The committed flat-x
    full-γ proxy OVER-sharpens to ~0.79 (FWHM ratio) — it narrows the tuning far more
    than the author additive 'cross' field does. EXPECTED RED today (~0.79 < 0.87).

    Satisfiable by the CORRECT mechanism alone: the author 'cross' shape sharpens to
    FWHM ratio 0.886-0.889 (verified) and the digitized panel to ~0.87; the band
    [0.87, 0.89] brackets both and EXCLUDES the over-sharpened 0.79. Drive it green by
    implementing the 'cross' shape + ledger geometry, NOT by widening the proxy.

    Citation: Finding 6C CONTRACT_BUG ; Figure6C.m AxWidth=30, AthetaWidth=60 ;
    attentionModel.m:146-162 (additive separable spatial×feature gain) ; digitized 6C
    FWHM ratio ~0.87 / author 'cross' ~0.889.
    """
    theta, fixation, feature = _record()
    fwhm_fix = fwhm(fixation, theta)
    assert fwhm_fix > 0.0, "attend-fixation FWHM is degenerate; cannot form the ratio."
    fwhm_ratio = fwhm(feature, theta) / fwhm_fix

    assert _FWHM_RATIO_LO <= fwhm_ratio <= _FWHM_RATIO_HI, (
        f"6C attend-feature/attend-fixation FWHM ratio must be in the author-'cross' / "
        f"digitized band [{_FWHM_RATIO_LO}, {_FWHM_RATIO_HI}]; got {fwhm_ratio:.3f} (the "
        "committed ~0.79 OVER-sharpens because the flat-x full-γ proxy applies the θ-gain "
        "everywhere in x). Implement the author 'cross' shape (AxWidth=30, AthetaWidth=60) "
        "routed through the ledger geometry; do NOT tune the proxy width."
    )


@deterministic_test(
    spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="T-A610C-6C-ledger-geometry",
)
def test_6C_protocol_honors_binding_ledger_geometry():
    """MUST-PASS (CONTRACT_BUG, Fig 6C): ``run_figure_6C`` honors the BINDING ledger
    geometry (calibration.yaml:638-702) instead of the hard-coded ``x_opposite=-50``/
    ``x_fixation=50`` + RF-at-x=0 invented geometry. The ledger records the recorded /
    RF-stimulus column at ``figure_6C.stim_rf_x=100``, the contralateral / attend-
    opposite centre at ``stim_contra_x=-100``, and the attend-fixation centre at
    ``attend_fixation_x=0`` — none of which the committed code uses.

    This is the MECHANISM half of the contract bug, complementary to the two numeric
    bands above: even a tuned proxy that happened to hit 1.108 / 0.88 at the wrong
    geometry would NOT be the author 'cross' field. We assert the protocol source no
    longer carries the invented ``-50/50`` defaults AND that the protocol consumes the
    ledger geometry keys. EXPECTED RED today (source hard-codes -50/50, never reads the
    stim_rf_x/stim_contra_x/attend_fixation_x keys).

    Satisfiable by the correct mechanism alone: wiring the protocol to the ledger keys
    is a contract-conformance change, not a free parameter. Do NOT merely rename the
    constants — the geometry values (100/-100/0) and the 'cross' shape must actually be
    used (the numeric bands above guard that they produce the right curve).

    Citation: Finding 6C CONTRACT_BUG ; calibration.yaml:638-702 (binding keys) ;
    protocols.py:388 (def run_figure_6C(..., x_opposite=-50.0, x_fixation=50.0)).
    """
    src = inspect.getsource(protocols.run_figure_6C)
    compact = src.replace(" ", "")

    has_invented_geometry = ("x_opposite=-50" in compact) or ("x_fixation=50" in compact)
    assert not has_invented_geometry, (
        "run_figure_6C still hard-codes the invented geometry (x_opposite=-50 and/or "
        "x_fixation=50); the binding ledger records stim_rf_x=100, stim_contra_x=-100, "
        "attend_fixation_x=0 (calibration.yaml:638-702). Route the protocol through the "
        "ledger keys instead of the invented -50/50 defaults."
    )
    # The corrected protocol must actually consume the binding ledger geometry keys.
    consumes_ledger = (
        "stim_rf_x" in src and "stim_contra_x" in src and "attend_fixation_x" in src
    )
    assert consumes_ledger, (
        "run_figure_6C must consume the binding ledger geometry keys figure_6C.stim_rf_x "
        "(=100), figure_6C.stim_contra_x (=-100), figure_6C.attend_fixation_x (=0) — the "
        "code records them in calibration.yaml:638-702 but never reads them. Wire the "
        "RF stimulus to stim_rf_x, the attend-opposite centre to stim_contra_x, and the "
        "attend-fixation centre to attend_fixation_x, with the author 'cross' shape."
    )
