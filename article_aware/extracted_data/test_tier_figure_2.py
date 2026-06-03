"""Three-tier figure tests for Figure 2 panels 2A / 2B (WORKFLOW.md §3b).

Evaluated on the IMPLEMENTATION's measurement record (protocols.run_figure_2*),
placed in the panel's pinned display frame (left axis normalized 0-1; right axis
percent) — the SAME frame the Phase-A view renders — with expected values taken
from the PAPER-DIGITIZED reference (panel_<X>_digitized.json).

EXPECTATION: the model is unchanged and diverges, so some qualitative/hard tests
FAIL. That red is the intended success criterion of this worked example. Do NOT
weaken the tests or edit the model to green them.
"""

from __future__ import annotations

import numpy as np

from rh_model import protocols
from rh_tier_helpers import (
    norm_pair_shared, ref_peak, ref_value_at, tier_test, value_at_log,
)

_C_HI = 1.0           # highest sampled contrast
_C_MID = 0.1233       # an intermediate contrast on the swept grid


def _record_2A():
    # SHARED-SCALE (Finding 1): 2A and 2B are placed on ONE common response scale
    # so 2B's attended ceiling renders ABOVE 2A's, matching the digitized
    # references. NOT per-pair-renormalized to 1.0.
    r = protocols.run_figure_2A(n_contrasts=24)
    att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 2, "A")
    return r["c"], att, una, np.abs(np.asarray(r["percent_modulation"], dtype=float))


def _record_2B():
    r = protocols.run_figure_2B(n_contrasts=24)
    att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 2, "B")
    return r["c"], att, una, np.abs(np.asarray(r["percent_modulation"], dtype=float))


# === Figure 2A — predominantly contrast gain ==============================

@tier_test(tier="qualitative", spec_ref="figures.figure_2.panel_A", figure=2,
           claim_id="T-2A-Q-order")
def test_2A_attended_at_or_above_unattended():
    """Attended CRF >= unattended over the swept contrast (qualitative floor)."""
    _, att, una, _ = _record_2A()
    assert np.all(att >= una - 0.02)


@tier_test(tier="qualitative", spec_ref="figures.figure_2.panel_A", figure=2,
           claim_id="T-2A-Q-converge")
def test_2A_curves_converge_at_high_contrast():
    """Paper 2A: the two CRFs CONVERGE at the high-contrast end (pure contrast
    gain). Digitized attended-unattended at c=1 is ~0; require the model's
    separation there to be small."""
    c, att, una, _ = _record_2A()
    sep_model = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    ref_sep = (ref_value_at(2, "A", "attended", _C_HI, log_x=True)
               - ref_value_at(2, "A", "unattended", _C_HI, log_x=True))
    # ref_sep ~ 0.01; allow a generous qualitative band of 0.10.
    assert ref_sep < 0.05
    assert sep_model < 0.10


@tier_test(tier="qualitative", spec_ref="figures.figure_2.panel_A", figure=2,
           claim_id="T-2A-Q-modfall")
def test_2A_modulation_falls_toward_high_contrast():
    """Dashed % modulation is largest at low contrast and falls toward high
    contrast (low-contrast-weighted contrast gain)."""
    c, _, _, pm = _record_2A()
    assert pm[0] > pm[-1]
    assert pm[-1] < 0.5 * pm.max()


@tier_test(tier="hard", spec_ref="figures.figure_2.panel_A", figure=2,
           claim_id="T-2A-H-converge")
def test_2A_high_contrast_separation_matches_digitized():
    """HARD: attended-unattended at the highest contrast ~ digitized (~0) +/- 0.12."""
    c, att, una, _ = _record_2A()
    sep_model = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    ref_sep = (ref_value_at(2, "A", "attended", _C_HI, log_x=True)
               - ref_value_at(2, "A", "unattended", _C_HI, log_x=True))
    assert abs(sep_model - ref_sep) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_2.panel_A", figure=2,
           claim_id="T-2A-S-mid")
def test_2A_attended_value_at_mid_contrast():
    """SOFT: attended normalized response at c=0.123 ~ digitized +/- 0.12."""
    c, att, _, _ = _record_2A()
    model = value_at_log(c, att, _C_MID)
    ref = ref_value_at(2, "A", "attended", _C_MID, log_x=True)
    assert abs(model - ref) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_2.panel_A", figure=2,
           claim_id="T-2A-S-modlow")
def test_2A_modulation_at_low_contrast():
    """SOFT: % modulation at the lowest contrast ~ digitized (~98%) +/- 15."""
    c, _, _, pm = _record_2A()
    model = float(pm[0])
    ref = ref_value_at(2, "A", "percent_modulation", c[0], log_x=True)
    assert abs(model - ref) < 15.0


# === Figure 2B — predominantly response gain ==============================

@tier_test(tier="qualitative", spec_ref="figures.figure_2.panel_B", figure=2,
           claim_id="T-2B-Q-order")
def test_2B_attended_above_unattended():
    """Attended CRF >= unattended over contrast (response gain)."""
    _, att, una, _ = _record_2B()
    assert np.all(att >= una - 0.02)


@tier_test(tier="qualitative", spec_ref="figures.figure_2.panel_B", figure=2,
           claim_id="T-2B-Q-noconverge")
def test_2B_curves_do_not_converge_at_high_contrast():
    """Paper 2B: a SUSTAINED vertical separation at high contrast (response
    gain) — the curves do NOT converge (contrast with 2A)."""
    c, att, una, _ = _record_2B()
    sep_model = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    ref_sep = (ref_value_at(2, "B", "attended", _C_HI, log_x=True)
               - ref_value_at(2, "B", "unattended", _C_HI, log_x=True))
    assert ref_sep > 0.15
    assert sep_model > 0.12


@tier_test(tier="hard", spec_ref="figures.figure_2.panel_B", figure=2,
           claim_id="T-2B-H-sep")
def test_2B_high_contrast_separation_matches_digitized():
    """HARD: attended-unattended at c=1 ~ digitized (~0.28) +/- 0.12 (response gain)."""
    c, att, una, _ = _record_2B()
    sep_model = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    ref_sep = (ref_value_at(2, "B", "attended", _C_HI, log_x=True)
               - ref_value_at(2, "B", "unattended", _C_HI, log_x=True))
    assert abs(sep_model - ref_sep) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_2.panel_B", figure=2,
           claim_id="T-2B-S-unahi")
def test_2B_unattended_peak_matches_digitized():
    """SOFT: unattended normalized response at c=1 ~ digitized (~0.72) +/- 0.12."""
    c, _, una, _ = _record_2B()
    model = value_at_log(c, una, _C_HI)
    ref = ref_value_at(2, "B", "unattended", _C_HI, log_x=True)
    assert abs(model - ref) < 0.12


# === Cross-panel ceiling — the response-gain CLAIM (Finding 1) =============
# On the paper's SHARED response scale, 2B's attended plateau (~0.85) sits ABOVE
# 2A's shared plateau (~0.615). That ceiling difference IS the response-gain
# claim. Per-pair-to-1.0 normalization pins both panels to 1.0 and erases it;
# these tests are only meaningful because the records are now placed on the
# group's shared scale (norm_pair_shared).

@tier_test(tier="qualitative", spec_ref="figures.figure_2", figure=2,
           claim_id="T-2-Q-ceiling")
def test_2B_attended_ceiling_above_2A_ceiling():
    """Paper Fig 2 (shared scale): 2B's attended high-contrast plateau is ABOVE
    2A's. On per-pair-to-1.0 normalization both are pinned to 1.0 and this is
    untestable; on the shared scale it must hold (response gain lifts the
    ceiling). Reference: 2B attended ~0.85 > 2A attended ~0.615."""
    c2a, att2a, _, _ = _record_2A()
    c2b, att2b, _, _ = _record_2B()
    plateau_2a = value_at_log(c2a, att2a, _C_HI)
    plateau_2b = value_at_log(c2b, att2b, _C_HI)
    ref_2a = ref_value_at(2, "A", "attended", _C_HI, log_x=True)
    ref_2b = ref_value_at(2, "B", "attended", _C_HI, log_x=True)
    assert ref_2b > ref_2a + 0.10          # the reference encodes the claim
    assert plateau_2b > plateau_2a + 0.05   # the model must reproduce it


@tier_test(
    tier="hard", spec_ref="figures.figure_2", figure=2, claim_id="T-2-H-ceiling",
    paper_issue="On the shared scale, 2B's attended plateau matches the digitized "
    "~0.85, but 2A's attended plateau renders LOW (~0.34 vs digitized ~0.615): the "
    "model's 2A saturates too far below the group ceiling. This magnitude "
    "divergence was hidden by per-pair-to-1.0 (both pinned to 1.0) and is surfaced "
    "only by the shared-scale convention (Finding 1). Faithful-direction red; not a "
    "tuning target — record, do not green by widening the bound.",
)
def test_2B_attended_ceiling_matches_digitized():
    """HARD: on the shared scale, 2B's attended plateau (~0.85) matches the
    digitized value +/- 0.15, AND 2A's attended plateau (~0.615) matches +/-
    0.15. This pins the absolute cross-panel ceilings the per-pair convention
    destroyed. The 2B half passes; the 2A half is EXPECTED RED (the model's 2A
    under-saturates on the shared scale — a genuine magnitude divergence now made
    visible). Do NOT widen the bound."""
    c2a, att2a, _, _ = _record_2A()
    c2b, att2b, _, _ = _record_2B()
    assert abs(value_at_log(c2b, att2b, _C_HI) - ref_peak(2, "B", "attended")) < 0.15
    assert abs(value_at_log(c2a, att2a, _C_HI) - ref_peak(2, "A", "attended")) < 0.15
