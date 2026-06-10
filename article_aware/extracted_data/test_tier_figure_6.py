"""Three-tier figure tests for Figure 6 panel 6C (WORKFLOW.md §3b).

Feature-based attention sharpening of motion-direction tuning. Evaluated on the
implementation record (protocols.run_figure_6C) in the pinned display frame;
expected values from the digitized reference.

STATUS (updated 2026-06-10 render-and-certify): RESOLVED. These tier tests were AUTHORED
against an earlier model state where the two 6C curves essentially OVERLAPPED (peak ratio
~1.01, feature effect absent), so the qualitative sharpening + hard peak-ratio tests were
INTENDED FAILURES. The committed model now implements the author Ashape='cross' additive
separable spatial×feature field on the binding ledger geometry (stim_rf_x=100/
stim_contra_x=-100/attend_fixation_x=0), so 6C lands at the digitized/author value with no
tuning: at the tier grid (n=49) the peak ratio is ~1.108 (digitized 1.107), and these
tests PASS for the RIGHT reason (the faithful 'cross' field, not the over-corrected flat-x
proxy that briefly read ~1.167). The authoritative, tight two-sided 6C target lives in
test_audit_2026_06_10_contract.py (peak 1.108 ±0.01; FWHM ratio 0.87-0.89), measured at
the authors' native 1° grid; these coarse tier tests are the qualitative complement.
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
)
def test_6C_sharpening_present_at_peak():
    """QUALITATIVE MUST-PASS: the paper SHARPENS the attended curve — attend-
    contralateral is clearly ABOVE attend-fixation at the peak (0 deg) by ~0.10.

    RESOLVED (2026-06-10): the author 'cross' field now produces this peak
    enhancement (model peak gap > 0.05), so the feature-based effect is present and
    this passes. The earlier "INTENDED FAILURE — curves overlap ~0.009" framing
    described the pre-fix state. Citation: CODE-018 Ashape='cross'; digitized
    figures/figure_6/panel_C."""
    x, contra, fix = _record()
    ref_peak_gap = (ref_value_at(6, "C", "attend_contralateral", 0.0, log_x=False)
                    - ref_value_at(6, "C", "attend_fixation", 0.0, log_x=False))
    assert ref_peak_gap > 0.05  # the digitized reference DOES enhance the peak
    model_peak_gap = value_at(x, contra, 0.0) - value_at(x, fix, 0.0)
    assert model_peak_gap > 0.05


@tier_test(
    tier="hard", spec_ref="figures.figure_6.panel_C", figure=6,
    claim_id="T-6C-H-peakratio",
)
def test_6C_peak_ratio_matches_digitized():
    """HARD MUST-PASS: attend-contralateral/attend-fixation peak ratio ~ digitized
    (~1.107) +/- 0.06.

    RESOLVED (2026-06-10): the author 'cross' field lands the model at ~1.108
    (digitized 1.107) with no tuning, inside the band. The earlier "INTENDED
    FAILURE — model ~1.01, no enhancement" framing described the pre-fix overlap
    state. SAME assertion/tolerance kept (passes because the model is correct now).
    The tight authoritative band (1.108 ±0.01) is in test_audit_2026_06_10_contract.py.
    Do NOT loosen or edit the model. Citation: CODE-018 Ashape='cross'; digitized
    figures/figure_6/panel_C (peak ratio 1.107)."""
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
