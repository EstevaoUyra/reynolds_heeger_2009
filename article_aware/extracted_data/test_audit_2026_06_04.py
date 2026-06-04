"""Tests encoding the 2026-06-04 faithfulness-audit findings (author-tests skill).

This module is the machine-checkable form of the 2026-06-04 audit (see the README
"Current exit" / the SQ-007 re-investigation). The headline of that audit is that
the prior build's three "GENUINE-DIVERGENCE intended failures" (the CRF
left-shift reds, the 4E/7C over-modulation) are NOT genuine divergences at all —
they are **protocol-level CODE/CONTRACT bugs**: a clipped contrast window, two
co-located stimuli where the author code uses four separated ones, and (for 4C)
the wrong experimental condition + %-modulation sign. The forward model
(model.py, Eqs. 5-6) is FAITHFUL; every target below was reproduced by running
the author's exact geometry through the *committed* ``simulate`` (no model edit).

Tag -> test kind (skills/author-tests/SKILL.md):
  - CODE_BUG / CONTRACT_BUG  -> MUST-PASS. The faithful mechanism reproduces the
    paper value once the protocol geometry/window is corrected; the paper-blind
    implementer drives these green by fixing ``protocols.py`` (and, for the CRF
    window, the view xlim + re-digitization) ALONE. Verified reachable by the
    committed simulate, so they are satisfiable by the correct mechanism, not by
    tuning (A-013).
  - GENUINE_DIVERGENCE       -> RED TRIPWIRE (soft / xfail). A faithful mechanism
    still misses it; it flips green only if the model genuinely improves.

EXPECTED values are the author-script geometry reruns (cross-checked against the
digitized references), NOT the same record the protocol draws from.

------------------------------------------------------------------------------
CONFLICT FLAGGED (do not silently resolve here):
  Finding 4C is a CONTRACT_BUG that REVERSES the panel's direction. The existing
  ``test_figure_4C.py`` (Q-026/Q-027/Q-029), ``test_figure_4E.py`` (Q-053) and
  ``test_tier_figure_4.py`` (T-4C-*) encode 4C as FACILITATION (attended >=
  attend-away, positive %-mod, leftward shift). The 2026-06-04 audit, verified
  against ``paper/code/attentionModel/Figure4C.m`` (attCRF = attend NULL in RF
  -> Ax=110/Atheta=180; %-mod = 100*(unatt-att)/unatt; ylim [0 100]), shows 4C is
  SUPPRESSION: attending the null in the RF LOWERS the recorded preferred
  neuron's response (att < unatt everywhere), %-mod peaks ~+38% at LOW contrast.
  The facilitation tests are the prior (refuted) interpretation and MUST BE
  RETIRED when this contract fix lands — they cannot both be satisfied. They are
  left in place (not deleted by the test-author) and called out in the commit
  message + return so Phase A / the implementer retires them deliberately.
------------------------------------------------------------------------------
"""

from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols
from rh_tier_helpers import ref_peak, ref_value_at, tier_test


# ===========================================================================
# Finding A (CODE_BUG) — CRF contrast window clips the rising limb + left-shift
#   protocols._contrast_sweep hardcodes logspace(log10(0.01), log10(1.0)); the
#   author CRF scripts use cRange=[1e-5,1] (2A/2B/3C/3F). The committed model
#   half-saturates at c~0.0013-0.0025 (verified), so over [0.01,1] both CRFs are
#   already a flat plateau and the attended-vs-ignored left-shift is INVISIBLE
#   (half-max clips to the 0.01 left edge -> spurious shift ratio == 1.0). Over
#   [1e-5,1] the attended half-max (~0.0013) lands clearly LEFT of the ignored
#   (~0.0025): shift ratio ~0.5, shared plateau = contrast gain (paper Fig 2A/3C).
#   FIX (no model change): per-panel cRange from the author script in BOTH the
#   sweep generator and the view xlim; re-digitize with the author x_range.
# ===========================================================================

# Author CRF contrast windows (paper/code/attentionModel/Figure*.m `cRange`).
_AUTHOR_CRANGE = {
    "2A": (1e-5, 1.0), "2B": (1e-5, 1.0),
    "3C": (1e-5, 1.0), "3F": (1e-5, 1.0),
    "4C": (1e-4, 0.1), "4E": (1e-4, 0.1),
}


def _half_max_log(contrast: np.ndarray, curve: np.ndarray) -> float:
    """Half-max contrast by linear interpolation on the log-contrast axis."""
    contrast = np.asarray(contrast, dtype=float)
    curve = np.asarray(curve, dtype=float)
    target = 0.5 * float(curve.max())
    above = np.flatnonzero(curve >= target)
    if len(above) == 0:
        return float("nan")
    i = int(above[0])
    if i == 0:
        return float(contrast[0])
    c0, c1 = np.log(contrast[i - 1]), np.log(contrast[i])
    r0, r1 = curve[i - 1], curve[i]
    if r1 == r0:
        return float(contrast[i])
    t = (target - r0) / (r1 - r0)
    return float(np.exp(c0 + t * (c1 - c0)))


@deterministic_test(
    spec_ref="simulation_protocols._contrast_sweep", figure=2, claim_id="AUD-A-2A-window"
)
def test_2A_contrast_sweep_uses_author_window_not_hardcoded_001():
    """MUST-PASS (CODE_BUG): Figure 2A's contrast sweep must span the author
    cRange [1e-5, 1], not the hardcoded [0.01, 1]. The diagnostic contrast-gain
    rise lives below 0.01; a sweep that starts at 0.01 clips it off. Encoded as a
    lower-edge bound so the implementer routes the per-panel cRange through the
    sweep generator (and the view xlim).

    Citation: C-013 / paper/code/attentionModel/Figure2A.m (cRange=[1e-5 1])
    """
    c = np.asarray(protocols.run_figure_2A()["c"], dtype=float)
    lo, hi = _AUTHOR_CRANGE["2A"]
    # left edge at/below the author floor (1e-5), with a little numeric slack
    assert float(c.min()) <= lo * 1.5
    assert float(c.max()) >= hi * 0.99
    # and not the old hardcoded 0.01 floor
    assert float(c.min()) < 0.01


@deterministic_test(
    spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="AUD-A-2A-leftshift"
)
def test_2A_attended_left_shift_is_visible_in_author_window():
    """MUST-PASS (CODE_BUG): with the author contrast window, the attended CRF
    half-saturates LEFT of the ignored CRF (contrast gain) and the two share a
    common high-contrast plateau. Over the clipped [0.01,1] window both half-maxes
    pin to the left edge and the shift ratio is a spurious 1.0; the author window
    recovers shift ratio ~0.5 (verified: 0.0013 vs 0.0025). This is the 2A/2B/3C/3F
    left-shift the prior reds mis-attributed to a model divergence.

    Citation: C-007, C-019, C-021 / Figure2A.m
    """
    out = protocols.run_figure_2A()
    c = np.asarray(out["c"], dtype=float)
    att = np.asarray(out["attended_CRF"], dtype=float)
    una = np.asarray(out["unattended_CRF"], dtype=float)

    att_half = _half_max_log(c, att)
    una_half = _half_max_log(c, una)
    # attended half-max strictly left of ignored (contrast-gain left shift)
    assert att_half < 0.85 * una_half
    # neither half-max pinned at the very left edge (window not clipping the rise)
    assert att_half > c.min() * 1.5
    # shared high-contrast plateau (contrast gain, NOT response gain): the curves
    # converge at the top of the (full) window.
    assert abs(att[-1] - una[-1]) <= 0.10 * max(att[-1], una[-1])


@deterministic_test(
    spec_ref="simulation_protocols.figure_3C", figure=3, claim_id="AUD-A-3C-window"
)
def test_3C_contrast_sweep_uses_author_window():
    """MUST-PASS (CODE_BUG): Figure 3C sweep spans the author cRange [1e-5,1].

    Citation: C-014 / paper/code/attentionModel/Figure3C.m (cRange=[1e-5 1])
    """
    c = np.asarray(protocols.run_figure_3C()["c"], dtype=float)
    lo, hi = _AUTHOR_CRANGE["3C"]
    assert float(c.min()) <= lo * 1.5
    assert float(c.max()) >= hi * 0.99
    assert float(c.min()) < 0.01


@deterministic_test(
    spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="AUD-A-4E-window"
)
def test_4E_contrast_sweep_uses_author_window():
    """MUST-PASS (CODE_BUG): Figure 4E sweep spans the author cRange [1e-4, 0.1]
    (NOT [0.01, 1]). The 4C/4E CRFs in Martinez-Trujillo & Treue 2002 live in a
    lower-contrast window than the single-grating panels.

    Citation: C-015 / paper/code/attentionModel/Figure4E.m (cRange=[1e-4 0.1])
    """
    c = np.asarray(protocols.run_figure_4E()["c"], dtype=float)
    lo, hi = _AUTHOR_CRANGE["4E"]
    assert float(c.min()) <= lo * 1.5
    assert abs(float(c.max()) - hi) <= 0.02


# ===========================================================================
# Finding B (CODE_BUG) — Figure 4E geometry: two co-located stimuli at x=0 vs
#   the author's FOUR separated stimuli. Co-locating (sigma_stim=5) makes the two
#   patches overlap, feature competition crushes the nonpreferred response, and
#   %-modulation overflows to ~386% (the prior "intended failure"). The author
#   geometry (RF x=90/110 theta 0/180, contralateral x=-90/-110, RF_center=100,
#   Apeak=5/AxWidth=5/AthetaWidth=20, cRange [1e-4,0.1]) through the committed
#   simulate gives %-mod ~50-54% (verified), matching the digitized ~54%. FIX:
#   replace the co-located layout with the four separated stimuli. No model edit.
# ===========================================================================

@deterministic_test(
    spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="AUD-B-4E-modmag",
)
def test_4E_percent_modulation_matches_paper_with_author_geometry():
    """MUST-PASS (CODE_BUG): 4E percent attentional modulation stays WITHIN the
    paper's 0-100 axis and matches the digitized ~54%. The committed simulate run
    over the author's four-separated-stimulus geometry yields ~50-54% (verified) —
    so the paper value is reachable by the FAITHFUL mechanism once the co-located
    geometry bug is fixed. The prior ~386% was the co-location artifact, NOT a
    genuine divergence; this test must pass by fixing the protocol geometry, not by
    tuning (A-013).

    Citation: C-015 / paper/code/attentionModel/Figure4E.m
    """
    out = protocols.run_figure_4E()
    ratio = np.asarray(out["ratio"], dtype=float)
    pm = (ratio - 1.0) * 100.0
    peak = float(np.max(np.abs(pm)))
    # digitized 4E percent-modulation peaks ~54%
    ref_peak_pm = float(
        max(
            ref_value_at(4, "E", "percent_modulation", cc, log_x=True)
            for cc in np.asarray(out["c"], dtype=float)
        )
    )
    assert ref_peak_pm < 70.0  # the reference peaks ~54%
    # within the paper's 0-100 axis ...
    assert peak <= 100.0
    # ... and quantitatively near the digitized value (generous +/-18 band;
    # author-geometry rerun lands ~50-54).
    assert abs(peak - ref_peak_pm) < 18.0


# ===========================================================================
# Finding C (CONTRACT_BUG) — Figure 4C wrong condition + wrong %-mod sign.
#   Author Figure4C.m records a PREFERRED neuron while attention is on the
#   NONPREFERRED (null) stimulus IN the RF (Ax=110, Atheta=180), null fixed at
#   contrast 0.01, four separated stimuli, %-mod = 100*(unatt-att)/unatt
#   (SUPPRESSION; ylim [0 100]). The committed simulate over that geometry gives
#   att < unatt EVERYWHERE and %-mod peaking ~+38% at low contrast (verified),
#   matching the digitized ~36%. The impl models the wrong (facilitation)
#   condition with the wrong sign. FIX: adopt the author 4C protocol. No model edit.
#
#   These tests CONTRADICT the existing facilitation tests (see module docstring
#   CONFLICT FLAGGED). They encode the audit's corrected contract.
# ===========================================================================

@deterministic_test(
    spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="AUD-C-4C-suppression",
)
def test_4C_attending_null_in_rf_suppresses_preferred_response():
    """MUST-PASS (CONTRACT_BUG): in the author 4C condition, attending the
    NONPREFERRED (null) stimulus in the RF LOWERS the recorded preferred neuron's
    response across contrast — attended (attend-null-in-RF) sits AT-OR-BELOW
    attend-away. This reverses the impl's facilitation direction. Verified: the
    committed simulate over the author geometry gives att < unatt everywhere.

    The protocol record's ``attended_CRF`` is the attend-null-in-RF response and
    ``unattended_CRF`` is the attend-away response (the author attCRF/unattCRF).

    Citation: C-015, C-019 / paper/code/attentionModel/Figure4C.m
    """
    out = protocols.run_figure_4C()
    att = np.asarray(out["attended_CRF"], dtype=float)
    una = np.asarray(out["unattended_CRF"], dtype=float)
    # suppression: attend-null-in-RF is at or below attend-away everywhere
    assert np.all(att <= una + 1e-9)
    # and meaningfully below somewhere on the rise (not a degenerate tie)
    assert float(np.max((una - att) / np.maximum(una, 1e-12))) > 0.05


@deterministic_test(
    spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="AUD-C-4C-modsign",
)
def test_4C_percent_modulation_is_suppressive_sign_and_low_contrast_weighted():
    """MUST-PASS (CONTRACT_BUG): the author 4C %-modulation is
    100*(unatt-att)/unatt (suppression), POSITIVE under that sign, largest at LOW
    contrast (~+38% verified vs digitized ~36%) and declining toward high
    contrast. The impl currently reports (att-unatt)/unatt (facilitation), the
    wrong sign. Evaluated against the SUPPRESSION-sign percent modulation.

    Citation: C-019 / paper/code/attentionModel/Figure4C.m (mod=(unatt-att)/unatt)
    """
    out = protocols.run_figure_4C()
    att = np.asarray(out["attended_CRF"], dtype=float)
    una = np.asarray(out["unattended_CRF"], dtype=float)
    c = np.asarray(out["c_pref"], dtype=float)
    pm_suppressive = 100.0 * (una - att) / una

    # suppression sign: positive under (unatt-att)/unatt
    assert float(np.max(pm_suppressive)) > 1.0
    # low-contrast weighted: peak in the lower-contrast half, declines to high c
    peak_idx = int(np.argmax(pm_suppressive))
    assert peak_idx < len(pm_suppressive) // 2 + 1
    assert pm_suppressive[-1] < pm_suppressive[peak_idx]

    # quantitative magnitude near the digitized ~36% peak (within the paper's
    # 0-100 axis). Author-geometry rerun peaks ~38%.
    ref_peak_pm = float(
        max(ref_value_at(4, "C", "percent_modulation", cc, log_x=True) for cc in c)
    )
    assert ref_peak_pm < 60.0
    assert float(np.max(pm_suppressive)) <= 100.0
    assert abs(float(np.max(pm_suppressive)) - ref_peak_pm) < 18.0


# ===========================================================================
# Finding D (CODE_BUG) — Figure 7C geometry: two co-located stimuli at x=0 +
#   fixation at x=50 vs the author's separated layout (variable x=93, null
#   theta=180 at x=107, RF_center=100, attend-away at x=-100, Apeak=5/AxWidth=5/
#   AthetaWidth=45). Co-locating inflates the variable/attend-away peak ratio to
#   2.73 (the prior "intended failure"); the author geometry through the committed
#   simulate gives 1.41 (verified), matching the paper/digitized ~1.3-1.4. FIX:
#   author separated geometry. No model edit.
# ===========================================================================

@deterministic_test(
    spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="AUD-D-7C-ratio",
)
def test_7C_variable_over_baseline_ratio_matches_paper_with_author_geometry():
    """MUST-PASS (CODE_BUG): the 7C attend-variable / baseline peak ratio matches
    the paper's ~1.3-1.4 (digitized attend_variable/fixation ~1.33; author-geometry
    rerun 1.41 verified). The prior ~2.73 was the co-located-geometry artifact, NOT
    a genuine over-modulation. The faithful mechanism reaches the paper ratio once
    the author's separated x=93/107 (and attend-away x=-100) geometry is restored;
    pass by fixing the protocol geometry, not by tuning (A-013).

    The protocol's baseline curve is ``fixation_tuning`` (the attend-away
    condition); the author panel divides the attend-variable peak by it.

    Citation: C-018 / paper/code/attentionModel/Figure7C.m
    """
    out = protocols.run_figure_7C()
    var = np.asarray(out["attend_variable_tuning"], dtype=float)
    base = np.asarray(out["fixation_tuning"], dtype=float)
    model_ratio = float(var.max() / base.max())

    ref_ratio = ref_peak(7, "C", "attend_variable") / ref_peak(7, "C", "fixation")
    assert ref_ratio < 1.6  # digitized ~1.33
    # generous +/-0.35 band around the digitized ratio; the author-geometry rerun
    # lands 1.41, comfortably inside.
    assert abs(model_ratio - ref_ratio) < 0.35


# ===========================================================================
# Finding E (GENUINE_DIVERGENCE) — Figure 6C oval-vs-cross attention field.
#   The author 6C attend-RF condition uses Ashape='cross' (an additive
#   plus-shaped field whose feature arm reaches the recorded neuron along all x);
#   the impl approximates it with a feature-global oval. With the author geometry
#   this lands 6C peak ratio ~1.17 vs paper/digitized ~1.11 (sharpening present,
#   FWHM ~103 vs ~133). A faithful mechanism with the oval approximation still
#   overshoots ~1.11. RED TRIPWIRE: flips green only if Ashape='cross' is added
#   and the ratio genuinely drops to ~1.11. DO NOT tune to pass.
# ===========================================================================

@tier_test(
    tier="soft", spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="AUD-E-6C-cross-tripwire",
    paper_issue="6C attend-RF peak ratio ~1.17 (oval approximation) vs paper "
    "~1.11. The author code uses Ashape='cross' (additive plus-shaped attention "
    "field, attentionModel.m), which the impl does not implement; the oval "
    "feature-global approximation mildly overshoots. GENUINE_DIVERGENCE: flips "
    "green only if the cross attention-field construction is added and the ratio "
    "drops to ~1.11. Do NOT tune the oval to fit.",
)
def test_6C_peak_ratio_matches_paper_only_with_cross_field():
    """RED TRIPWIRE (GENUINE_DIVERGENCE): 6C attend-contralateral / attend-fixation
    peak ratio matches the paper's ~1.11 +/- 0.04 (i.e. ratio <= ~1.15). The
    faithful oval-approximation mechanism lands ~1.17 (verified), OUTSIDE the band,
    so this is EXPECTED to xfail until the Ashape='cross' additive field is
    implemented and the ratio drops toward ~1.11. The +/-0.04 band is set so the
    current 1.17 overshoot is RED while a genuine improvement to ~1.11 flips it
    green — it is a progress signal, not a fit target. Soft tier: measured &
    reported, never gates. Do NOT tune the oval to land inside the band.

    Citation: C-017, C-023 / paper/code/attentionModel/attentionModel.m (Ashape
    'cross' branch), Figure6C.m (Ashape='cross', AthetaWidth=60)
    """
    out = protocols.run_figure_6C()
    contra = np.asarray(out["attend_opposite_stimulus_tuning"], dtype=float)
    fix = np.asarray(out["attend_fixation_tuning"], dtype=float)
    peak_ratio = float(contra.max() / fix.max())
    # paper/digitized attend-RF sharpening peak ratio ~1.11; the oval ~1.17 must
    # be outside this band (tripwire RED) while a true cross-field ~1.11 passes.
    assert abs(peak_ratio - 1.11) < 0.04
