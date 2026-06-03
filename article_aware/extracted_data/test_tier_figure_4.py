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
    norm_pair, ref_value_at, tier_test, value_at_log,
)

_C_HI = 1.0
_C_MID = 0.1233


def _record_4C():
    r = protocols.run_figure_4C(n_contrasts=24)
    att, una = norm_pair(r["attended_CRF"], r["unattended_CRF"])
    return r["c_pref"], att, una, np.abs(np.asarray(r["percent_modulation"], dtype=float))


def _record_4E():
    r = protocols.run_figure_4E(n_contrasts=24)
    pref, nonpref = norm_pair(r["attend_pref_CRF"], r["attend_nonpref_CRF"])
    pm = np.abs((np.asarray(r["ratio"], dtype=float) - 1.0) * 100.0)
    return r["c"], pref, nonpref, pm


# === Figure 4C — two stimuli, attend nonpreferred (near-overlap) ==========

@tier_test(tier="qualitative", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-Q-overlap")
def test_4C_curves_nearly_overlap():
    """Paper 4C: the two CRFs nearly OVERLIE each other across contrast."""
    c, att, una, _ = _record_4C()
    assert float(np.max(np.abs(att - una))) < 0.15


@tier_test(tier="hard", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-H-sep")
def test_4C_high_contrast_separation_matches_digitized():
    """HARD: |attended-unattended| at c=1 ~ digitized (~0.01) +/- 0.12."""
    c, att, una, _ = _record_4C()
    sep = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    ref = (ref_value_at(4, "C", "attended", _C_HI, log_x=True)
           - ref_value_at(4, "C", "unattended", _C_HI, log_x=True))
    assert abs(sep - ref) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_4.panel_C", figure=4,
           claim_id="T-4C-S-modfall")
def test_4C_modulation_declines_to_high_contrast():
    """SOFT: % modulation declines from low to high contrast (within 0-100)."""
    c, _, _, pm = _record_4C()
    assert pm[-1] < pm[0]
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
