"""Three-tier figure tests for Figure 7 panel 7C (WORKFLOW.md §3b).

Two stimuli in the RF, three attention conditions on direction tuning. Evaluated
on the implementation record (protocols.run_figure_7C) in the pinned display
frame; expected values from the digitized reference.

STATUS (2026-06-10): RESOLVED. The curve ORDERING (attend-variable > ignored >
attend-nonpreferred) is correct AND the model's attend-variable/ignored peak ratio
now lands at ~1.3215 (digitized 1.325) after the author separated geometry +
θ-stimulus convention fixes. The hard ratio test PASSES (it was an intended failure
under the earlier co-located geometry; the model is faithful now). The soft
variable/nonpref ratio is also within band (~2.10 vs digitized 2.12).
"""

from __future__ import annotations

import numpy as np

from rh_model import protocols
from rh_tier_helpers import norm_curves, ref_peak, tier_test


def _record():
    r = protocols.run_figure_7C(n_directions=49)
    var, fix, nonpref = norm_curves(
        r["attend_variable_tuning"], r["fixation_tuning"], r["attend_nonpref_tuning"]
    )
    return np.asarray(r["theta_var_grid"], dtype=float), var, fix, nonpref


@tier_test(tier="qualitative", spec_ref="figures.figure_7.panel_C", figure=7,
           claim_id="T-7C-Q-order")
def test_7C_peak_ordering():
    """Paper 7C: peak heights reorder attend-variable > ignored >
    attend-nonpreferred."""
    _, var, fix, nonpref = _record()
    assert var.max() > fix.max() > nonpref.max()


@tier_test(
    tier="hard", spec_ref="figures.figure_7.panel_C", figure=7,
    claim_id="T-7C-H-varfix",
)
def test_7C_variable_over_fixation_ratio_matches_digitized():
    """HARD MUST-PASS: attend-variable/ignored peak ratio ~ digitized (~1.325) +/- 0.3.

    RESOLVED (2026-06-10): the model now lands at var/fixation peak ratio ~1.3215
    (digitized 1.325), squarely inside the band. The earlier "INTENDED FAILURE —
    model ~3.3 blows past it" framing described the co-located-at-x=0 geometry that
    has since been corrected to the author separated geometry (var x=93, null x=107,
    recorded x=100, att-away x=-100) AND the θ-stimulus convention (361 grid +
    non-periodic profile) fix. SAME assertion/tolerance kept (passes because the
    model is correct now, NOT because the tolerance was loosened). Do NOT loosen or
    edit the model. Citation: CODE-018 author geometry; T-A610-7C-ratio (tight 1.32
    ±0.03 must-pass); digitized figures/figure_7/panel_C (var/fixation ratio 1.325)."""
    _, var, fix, _ = _record()
    model_ratio = float(var.max() / fix.max())
    ref_ratio = ref_peak(7, "C", "attend_variable") / ref_peak(7, "C", "fixation")
    assert abs(model_ratio - ref_ratio) < 0.3


@tier_test(
    tier="soft", spec_ref="figures.figure_7.panel_C", figure=7,
    claim_id="T-7C-S-varnonpref",
)
def test_7C_variable_over_nonpref_ratio_matches_digitized():
    """SOFT: attend-variable/attend-nonpreferred peak ratio ~ digitized (~2.0)
    +/- 0.4. The model's ~4.5 is too strong (reported, non-blocking)."""
    _, var, _, nonpref = _record()
    model_ratio = float(var.max() / nonpref.max())
    ref_ratio = ref_peak(7, "C", "attend_variable") / ref_peak(7, "C", "attend_nonpref")
    assert abs(model_ratio - ref_ratio) < 0.4
