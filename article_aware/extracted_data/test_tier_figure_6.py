"""Three-tier figure tests for Figure 6 panel 6C (WORKFLOW.md §3b).

Feature-based attention sharpening of motion-direction tuning. Evaluated on the
implementation record (protocols.run_figure_6C) in the pinned display frame;
expected values from the digitized reference.

STATUS (updated 2026-06-10 contract audit): these tier tests were AUTHORED against an
earlier model state where the two 6C curves essentially OVERLAPPED (peak ratio ~1.01,
feature effect absent), so the qualitative sharpening + hard peak-ratio tests were
INTENDED FAILURES. The committed model has since moved PAST that: the flat-x full-γ
proxy now OVER-corrects (peak ratio ~1.167, peak gap ~0.14), so these digitized-anchored
tests now PASS — but for the WRONG reason (over-correction, not the faithful author
'cross' field). The genuine remaining defect is the OPPOSITE end: the proxy OVER-scales
PAST the digitized 1.108 and OVER-sharpens to FWHM ratio ~0.79. That two-sided contract
bug is caught by the tight MUST-PASS in test_audit_2026_06_10_contract.py (peak 1.108
±0.01 EXCLUDES 1.167; FWHM ratio 0.87-0.89 EXCLUDES 0.79). These coarse one-sided tier
tripwires are LEFT in place (digitized-anchored, framework-owned) but no longer carry the
divergence signal — see the contract module for the authoritative 6C target.
"""

from __future__ import annotations

import numpy as np

from rh_model import protocols
from rh_tier_helpers import (
    norm_curves, ref_peak, ref_value_at, tier_test, value_at,
)

_FLANK = 120.0  # |direction| at which the paper shows the sharpening difference


def _record():
    r = protocols.run_figure_6C(n_directions=49)
    # attend_contralateral is the attended curve; attend_fixation the baseline.
    contra, fix = norm_curves(
        r["attend_opposite_stimulus_tuning"], r["attend_fixation_tuning"]
    )
    return np.asarray(r["theta_stim_grid"], dtype=float), contra, fix


@tier_test(tier="qualitative", spec_ref="figures.figure_6.panel_C", figure=6,
           claim_id="T-6C-Q-peakorder")
def test_6C_attended_at_least_as_tall_at_peak():
    """At the peak (0 deg) the attended (contralateral) curve is >= the
    fixation curve (the enhancement is not negative)."""
    x, contra, fix = _record()
    assert value_at(x, contra, 0.0) >= value_at(x, fix, 0.0) - 0.02


@tier_test(
    tier="qualitative", spec_ref="figures.figure_6.panel_C", figure=6,
    claim_id="T-6C-Q-sharpen",
    paper_issue="6C feature-based sharpening absent — model curves overlap (peak "
    "enhancement ~0.009) vs the paper's clear ~0.10 peak enhancement of "
    "attend-contralateral over attend-fixation. Intended failing qualitative test.",
)
def test_6C_sharpening_present_at_peak():
    """QUALITATIVE (INTENDED FAILURE): the paper SHARPENS the attended curve —
    attend-contralateral is clearly ABOVE attend-fixation at the peak (0 deg) by
    ~0.10. The model's two curves overlap at the peak (~0.009 apart), so the
    feature-based effect is essentially absent and this fails — that red is the
    success criterion (the sharpening the model does not produce)."""
    x, contra, fix = _record()
    ref_peak_gap = (ref_value_at(6, "C", "attend_contralateral", 0.0, log_x=False)
                    - ref_value_at(6, "C", "attend_fixation", 0.0, log_x=False))
    assert ref_peak_gap > 0.05  # the digitized reference DOES enhance the peak
    model_peak_gap = value_at(x, contra, 0.0) - value_at(x, fix, 0.0)
    assert model_peak_gap > 0.05


@tier_test(
    tier="hard", spec_ref="figures.figure_6.panel_C", figure=6,
    claim_id="T-6C-H-peakratio",
    paper_issue="6C attend-contralateral/attend-fixation peak ratio ~1.01 vs "
    "paper ~1.11 — feature-based enhancement essentially absent. Intended failing "
    "hard test.",
)
def test_6C_peak_ratio_matches_digitized():
    """HARD (INTENDED FAILURE): attend-contralateral/attend-fixation peak ratio ~
    digitized (~1.11) +/- 0.06. The model's ~1.01 (essentially no enhancement)
    misses it — that red is the success criterion. Do NOT edit the model."""
    x, contra, fix = _record()
    model_ratio = float(contra.max() / fix.max())
    ref_ratio = ref_peak(6, "C", "attend_contralateral") / ref_peak(6, "C", "attend_fixation")
    assert abs(model_ratio - ref_ratio) < 0.06


@tier_test(tier="soft", spec_ref="figures.figure_6.panel_C", figure=6,
           claim_id="T-6C-S-flankdiff")
def test_6C_flank_difference_matches_digitized():
    """SOFT: the flank difference (attend-fixation minus attend-contralateral at
    |dir|=120) ~ digitized (~0.05) +/- 0.03 (reported, non-blocking). The model
    happens to land near this even with the peak enhancement absent, which is
    exactly why this is soft rather than hard."""
    x, contra, fix = _record()
    model_flank = value_at(x, fix, _FLANK) - value_at(x, contra, _FLANK)
    ref_flank = (ref_value_at(6, "C", "attend_fixation", _FLANK, log_x=False)
                 - ref_value_at(6, "C", "attend_contralateral", _FLANK, log_x=False))
    assert abs(model_flank - ref_flank) < 0.03
