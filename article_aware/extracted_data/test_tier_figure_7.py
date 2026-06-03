"""Three-tier figure tests for Figure 7 panel 7C (WORKFLOW.md §3b).

Two stimuli in the RF, three attention conditions on direction tuning. Evaluated
on the implementation record (protocols.run_figure_7C) in the pinned display
frame; expected values from the digitized reference.

KNOWN DIVERGENCE: the curve ORDERING (attend-variable > ignored >
attend-nonpreferred) is correct, but the model's attend-variable/ignored peak
ratio is ~3.3 vs the paper's ~1.4 — the attention gain is more than twice too
strong. The hard ratio test FAILS by design.
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
    paper_issue="7C attend-variable/ignored peak ratio ~3.3 vs paper ~1.4 — "
    "attention gain more than twice too strong. Intended failing hard test.",
)
def test_7C_variable_over_fixation_ratio_matches_digitized():
    """HARD (INTENDED FAILURE): attend-variable/ignored peak ratio ~ digitized
    (~1.39) +/- 0.3. The model's ~3.3 blows past it — that red is the success
    criterion. Do NOT loosen the tolerance or edit the model."""
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
