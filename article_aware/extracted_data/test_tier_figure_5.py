"""Three-tier figure tests for Figure 5 panel 5C (WORKFLOW.md §3b).

Spatial attention as multiplicative orientation-tuning scaling. Evaluated on the
implementation record (protocols.run_figure_5C) in the pinned display frame;
expected values from the digitized reference.

KNOWN DIVERGENCE: the model's attended/unattended peak ratio is ~1.59 vs the
paper's ~1.22 — the gain is too strong. The hard ratio test FAILS by design.
"""

from __future__ import annotations

import numpy as np

from rh_model import protocols
from rh_tier_helpers import (
    norm_curves, ref_peak, ref_value_at, tier_test, value_at,
)


def _record():
    r = protocols.run_figure_5C(n_orientations=37)
    att, una = norm_curves(r["attended_tuning"], r["unattended_tuning"])
    return np.asarray(r["theta_0_grid"], dtype=float), att, una


@tier_test(tier="qualitative", spec_ref="figures.figure_5.panel_C", figure=5,
           claim_id="T-5C-Q-order")
def test_5C_attended_above_unattended_over_centre():
    """Attended >= unattended across the central tuning region (qualitative)."""
    x, att, una = _record()
    centre = np.abs(x) <= 45.0
    assert np.all(att[centre] >= una[centre] - 0.02)


@tier_test(tier="qualitative", spec_ref="figures.figure_5.panel_C", figure=5,
           claim_id="T-5C-Q-samewidth")
def test_5C_same_tuning_width_no_sharpening():
    """Multiplicative scaling, no sharpening: attended and unattended FWHM
    match within tolerance (same bandwidth)."""
    x, att, una = _record()

    def fwhm(curve):
        above = np.flatnonzero(curve >= 0.5 * curve.max())
        return float(x[above[-1]] - x[above[0]])

    assert abs(fwhm(att) - fwhm(una)) < 15.0


@tier_test(
    tier="hard", spec_ref="figures.figure_5.panel_C", figure=5,
    claim_id="T-5C-H-ratio",
    paper_issue="5C attended/unattended peak ratio ~1.59 vs paper ~1.22 — gain "
    "too strong (known divergence). Intended failing hard test.",
)
def test_5C_peak_ratio_matches_digitized():
    """HARD (INTENDED FAILURE): attended/unattended peak ratio ~ digitized
    (~1.22) +/- 0.15. The model's ~1.59 exceeds it — that red is the success
    criterion. Do NOT loosen the tolerance or edit the model."""
    x, att, una = _record()
    model_ratio = float(att.max() / una.max())
    ref_ratio = ref_peak(5, "C", "attended") / ref_peak(5, "C", "unattended")
    assert abs(model_ratio - ref_ratio) < 0.15


@tier_test(tier="soft", spec_ref="figures.figure_5.panel_C", figure=5,
           claim_id="T-5C-S-una0")
def test_5C_unattended_peak_matches_digitized():
    """SOFT: unattended normalized response at the peak (0 deg) ~ digitized
    (~0.82) +/- 0.12."""
    x, att, una = _record()
    model = value_at(x, una, 0.0)
    ref = ref_value_at(5, "C", "unattended", 0.0, log_x=False)
    assert abs(model - ref) < 0.12
