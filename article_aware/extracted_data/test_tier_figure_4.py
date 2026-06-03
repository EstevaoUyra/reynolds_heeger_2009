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
    # SHARED-SCALE (Finding 1): 4C/4E on one common response scale, not
    # per-pair-to-1.0. The 4C percent_modulation here is the SIGNED model value
    # (positive = facilitation), so the facilitation direction (Finding 2) can be
    # asserted rather than masked by np.abs.
    r = protocols.run_figure_4C(n_contrasts=24)
    att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 4, "C")
    return r["c_pref"], att, una, np.asarray(r["percent_modulation"], dtype=float)


def _record_4E():
    r = protocols.run_figure_4E(n_contrasts=24)
    pref, nonpref = norm_pair_shared(
        r["attend_pref_CRF"], r["attend_nonpref_CRF"], 4, "E")
    pm = np.abs((np.asarray(r["ratio"], dtype=float) - 1.0) * 100.0)
    return r["c"], pref, nonpref, pm


# === Figure 4C — two stimuli, attend nonpreferred-in-RF: FACILITATION ======
# Paper 4C (Finding 2 / figure_4C_investigation-2026-06-03): a SPATIAL attention
# cue to the RF boosts BOTH colocated stimuli -> contrast-gain facilitation. The
# attend-nonpreferred-in-RF (attended) CRF sits ABOVE attend-away (unattended),
# a leftward (contrast-gain) shift, with POSITIVE %-modulation peaking ~+36% at
# low contrast and declining. Reference: panel_C_digitized.json. C-021 (the 4E
# mechanism prose) is NOT the referent; cite the Fig-4 caption + C-019.

@tier_test(tier="qualitative", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-Q-facilitation")
def test_4C_attended_above_unattended():
    """Paper 4C: the attend-nonpreferred-in-RF CRF sits ABOVE attend-away across
    the rising portion (facilitation / contrast gain), with a visible gap
    (~0.10 mid-contrast in the digitized reference), merging only in the toe."""
    c, att, una, _ = _record_4C()
    # attended at-or-above unattended everywhere (small toe tolerance)
    assert np.all(att >= una - 0.02)
    # a real (not vanishing) separation somewhere on the rise
    assert float(np.max(att - una)) > 0.04


@tier_test(tier="hard", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-H-sep")
def test_4C_mid_contrast_separation_matches_digitized():
    """HARD: attended-unattended at mid contrast ~ digitized (~+0.10, attended
    ABOVE) +/- 0.12. Positive sign = facilitation."""
    c, att, una, _ = _record_4C()
    sep = value_at_log(c, att, _C_MID) - value_at_log(c, una, _C_MID)
    ref = (ref_value_at(4, "C", "attended", _C_MID, log_x=True)
           - ref_value_at(4, "C", "unattended", _C_MID, log_x=True))
    assert ref > 0.0            # the reference encodes facilitation
    assert abs(sep - ref) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-S-modfall")
def test_4C_modulation_positive_and_declines_to_high_contrast():
    """SOFT: %-modulation is POSITIVE (facilitation), peaks ~+36% at low
    contrast and declines monotonic-ish to high contrast, within 0-100."""
    c, _, _, pm = _record_4C()
    assert pm.max() > 0.0            # positive = facilitation
    assert pm[-1] < pm[0]            # declines toward high contrast
    assert pm.max() <= 100.0 + 5.0


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
