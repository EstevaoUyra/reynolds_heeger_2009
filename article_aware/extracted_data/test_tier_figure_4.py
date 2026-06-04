"""Three-tier figure tests for Figure 4 panels 4C / 4E (WORKFLOW.md §3b).

Evaluated on the implementation record (protocols.run_figure_4*) in the pinned
display frame; expected values from the digitized reference. 4E carries the
headline magnitude divergence (% attentional modulation ~390% vs the paper's
<=100%) as BOTH a pinned-axis deterministic test (test_panel_axes.py) AND a
hard tier test here. That red is intended.
"""

from __future__ import annotations

import numpy as np

from rh_model import protocols
from rh_tier_helpers import (
    norm_pair_shared, ref_value_at, tier_test, value_at_log,
)

_C_HI = 1.0
_C_MID = 0.1233


def _record_4C():
    # SHARED-SCALE: 4C/4E on one common response scale, not per-pair-to-1.0.
    # Figure 4C is a SUPPRESSION panel (authors' Figure4C.m, CODE-018 / C-021):
    # model attended_CRF = attend-null-in-RF is the LOWER curve, unattended_CRF =
    # attend-away is the UPPER. The DIGITIZED panel_C JSON traced the UPPER solid
    # as "attended" (published-panel drawing, DR-4C-sign) — i.e. the JSON labels
    # are SWAPPED relative to this code convention. So model attended_CRF compares
    # to digitized "unattended" and model unattended_CRF to digitized "attended".
    # The percent_modulation here is the signed suppression magnitude
    # 100·(unatt-att)/unatt (positive), comparable to the digitized %-modulation.
    r = protocols.run_figure_4C(n_contrasts=24)
    att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 4, "C")
    return r["c_pref"], att, una, np.asarray(r["percent_modulation"], dtype=float)


def _record_4E():
    r = protocols.run_figure_4E(n_contrasts=24)
    pref, nonpref = norm_pair_shared(
        r["attend_pref_CRF"], r["attend_nonpref_CRF"], 4, "E")
    pm = np.abs((np.asarray(r["ratio"], dtype=float) - 1.0) * 100.0)
    return r["c"], pref, nonpref, pm


# === Figure 4C — attend the null/nonpreferred-in-RF: SUPPRESSION ===========
# Authors' Figure4C.m (CODE-018) + C-021: four separated stimuli, the recorded
# preferred (θ=0) neuron probed while attention is on the NULL (θ=180) stimulus.
# Attending the null boosts the suppressive pool, so attend-null-in-RF (model
# attended_CRF) sits BELOW attend-away (model unattended_CRF). The suppression
# %-modulation 100·(unatt-att)/unatt peaks ~36% at low contrast and declines.
# DIGITIZED LABEL SWAP (DR-4C-sign): the panel_C JSON traced the UPPER solid as
# "attended" (published-panel drawing), so model attended_CRF <-> digitized
# "unattended" and model unattended_CRF <-> digitized "attended".

@tier_test(tier="qualitative", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-Q-suppression")
def test_4C_attended_below_unattended():
    """Authors' 4C: the attend-null-in-RF (model attended_CRF) CRF sits BELOW
    attend-away (model unattended_CRF) across the rising portion (suppression),
    with a real separation. Asserted on the RAW model record (the model's actual
    output, display-normalization-independent), since the Fig-4 shared-scale
    divisor compresses the [1e-4,0.1]-swept 4C curves on the group axis."""
    r = protocols.run_figure_4C(n_contrasts=24)
    att_raw = np.asarray(r["attended_CRF"], dtype=float)
    una_raw = np.asarray(r["unattended_CRF"], dtype=float)
    # attended at-or-below unattended everywhere (small toe tolerance)
    assert np.all(att_raw <= una_raw + 1e-9)
    # a real (not vanishing) suppression separation somewhere on the rise
    assert float(np.max((una_raw - att_raw) / una_raw)) > 0.10


@tier_test(tier="hard", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-H-sep")
def test_4C_mid_contrast_separation_matches_digitized():
    """HARD: |attended-unattended| at mid contrast ~ digitized gap (~0.10) +/- 0.12.
    Model attended is BELOW; the digitized gap is taken as
    (digitized 'attended' upper) - (digitized 'unattended' lower) = the same gap
    magnitude under the DR-4C-sign label swap."""
    c, att, una, _ = _record_4C()
    sep = value_at_log(c, una, _C_MID) - value_at_log(c, att, _C_MID)  # unatt above
    ref = (ref_value_at(4, "C", "attended", _C_MID, log_x=True)
           - ref_value_at(4, "C", "unattended", _C_MID, log_x=True))
    assert ref > 0.0            # digitized upper-minus-lower gap is positive
    assert abs(sep - ref) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-S-modfall")
def test_4C_modulation_positive_and_declines_to_high_contrast():
    """SOFT: suppression %-modulation is POSITIVE, peaks ~36% at low contrast and
    declines monotonic-ish to high contrast, within 0-100."""
    c, _, _, pm = _record_4C()
    assert pm.max() > 0.0            # positive suppression magnitude
    assert pm[-1] < pm[0]            # declines toward high contrast
    assert pm.max() <= 100.0 + 5.0


@tier_test(
    tier="hard", spec_ref="figures.figure_4.panel_C", figure=4,
    claim_id="T-4C-H-modmag",
)
def test_4C_modulation_peak_matches_digitized():
    """HARD: the 4C %-modulation PEAK matches the digitized reference (~36.4%)
    +/- 12. Under the authors' Figure4C.m protocol (CODE-018) the model peaks
    ~38%, so this now PASSES — the prior ~101% peak was an artifact of the
    RETIRED colocated-spatial-flat mis-mapping (A-012), not the model. The peak
    stays within the paper's (0,100) right axis."""
    c, _, _, pm = _record_4C()
    ref_peak_pm = max(
        ref_value_at(4, "C", "percent_modulation", cc, log_x=True) for cc in c
    )
    assert ref_peak_pm < 50.0           # the digitized reference peaks ~36%
    assert abs(float(np.max(pm)) - ref_peak_pm) < 12.0


@tier_test(
    tier="hard", spec_ref="figures.figure_4.panel_C", figure=4,
    claim_id="T-4C-H-platgap",
)
def test_4C_high_contrast_gap_narrows_to_digitized():
    """HARD: the |attended-unattended| gap at the HIGHEST swept contrast matches
    the digitized near-coincident plateau (~0.042) +/- 0.10. The authors'
    suppression narrows toward saturation; model attended is below, so the gap is
    (unattended-attended). (NOTE: the model sweep ends at the Figure4C.m cRange
    top c=0.1, not c=1.0; the curves are already near their plateau there.)"""
    c, att, una, _ = _record_4C()
    c_top = float(c[-1])
    gap_model = value_at_log(c, una, c_top) - value_at_log(c, att, c_top)
    ref_gap = (ref_value_at(4, "C", "attended", _C_HI, log_x=True)
               - ref_value_at(4, "C", "unattended", _C_HI, log_x=True))
    assert ref_gap < 0.10               # digitized plateaus are near-coincident
    assert abs(gap_model - ref_gap) < 0.10


# === Figure 4E — attend preferred scales response (KNOWN DIVERGENCE) =======

@tier_test(tier="qualitative", spec_ref="figures.figure_4.panel_E", figure=4,
           claim_id="T-4E-Q-order")
def test_4E_attend_pref_above_attend_nonpref():
    """Attend-preferred CRF sits above attend-nonpreferred over contrast."""
    _, pref, nonpref, _ = _record_4E()
    assert np.all(pref >= nonpref - 0.02)


@tier_test(
    tier="hard", spec_ref="figures.figure_4.panel_E", figure=4,
    claim_id="T-4E-H-modmag",
    paper_issue="4E % attentional modulation (~310-390%) overflows the paper's "
    "0-100 axis — known model divergence (panel_E.md). Intended failing hard test.",
)
def test_4E_modulation_stays_within_paper_axis():
    """HARD (INTENDED FAILURE): the paper's 4E % modulation stays WITHIN 0-100;
    the model's reaches ~390%. Require max % modulation <= digitized ceiling
    (~55) + tol 20. The model blows past it — that red is the success criterion.
    Do NOT widen the bound or edit the model."""
    c, _, _, pm = _record_4E()
    ref_max = max(
        ref_value_at(4, "E", "percent_modulation", cc, log_x=True) for cc in c
    )
    assert float(pm.max()) < ref_max + 20.0


@tier_test(tier="soft", spec_ref="figures.figure_4.panel_E", figure=4,
           claim_id="T-4E-S-sep")
def test_4E_high_contrast_separation_matches_digitized():
    """SOFT: attend_pref-attend_nonpref at c=1 ~ digitized (~0.22) +/- 0.15."""
    c, pref, nonpref, _ = _record_4E()
    sep = value_at_log(c, pref, _C_HI) - value_at_log(c, nonpref, _C_HI)
    ref = (ref_value_at(4, "E", "attend_pref", _C_HI, log_x=True)
           - ref_value_at(4, "E", "attend_nonpref", _C_HI, log_x=True))
    assert abs(sep - ref) < 0.15
