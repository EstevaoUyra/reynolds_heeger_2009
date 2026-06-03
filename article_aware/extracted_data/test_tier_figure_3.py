"""Three-tier figure tests for Figure 3 panels 3C / 3F (WORKFLOW.md §3b).

Evaluated on the implementation record (protocols.run_figure_3*) in the pinned
display frame; expected values from the digitized reference. See
test_tier_figure_2.py for the tier convention. Some tests are EXPECTED to fail
(intended) — do not weaken them or edit the model.
"""

from __future__ import annotations

import numpy as np

from rh_model import protocols
from rh_tier_helpers import (
    norm_pair_shared, ref_value_at, tier_test, value_at_log,
)

_C_HI = 1.0
_C_MID = 0.1233

# Map each 3-group protocol runner to its panel for the shared-scale normalizer.
_PANEL_OF = {protocols.run_figure_3C: "C", protocols.run_figure_3F: "F"}


def _record(fn):
    # SHARED-SCALE (Finding 1): 3C and 3F are placed on ONE common response scale
    # (figure_3 group), not per-pair-renormalized to 1.0.
    r = fn(n_contrasts=24)
    att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 3, _PANEL_OF[fn])
    return r["c"], att, una, np.abs(np.asarray(r["percent_modulation"], dtype=float))


# === Figure 3C — mixed attention effect (converging) ======================

@tier_test(tier="qualitative", spec_ref="figures.figure_3.panel_C", figure=3,
           claim_id="T-3C-Q-order")
def test_3C_attended_at_or_above_unattended():
    _, att, una, _ = _record(protocols.run_figure_3C)
    assert np.all(att >= una - 0.03)


@tier_test(tier="qualitative", spec_ref="figures.figure_3.panel_C", figure=3,
           claim_id="T-3C-Q-converge")
def test_3C_curves_converge_at_high_contrast():
    """Paper 3C: the two CRFs sit close and converge to ~1.0 at high contrast."""
    c, att, una, _ = _record(protocols.run_figure_3C)
    sep = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    assert sep < 0.10


@tier_test(tier="hard", spec_ref="figures.figure_3.panel_C", figure=3,
           claim_id="T-3C-H-converge")
def test_3C_high_contrast_separation_matches_digitized():
    """HARD: attended-unattended at c=1 ~ digitized (~0.01) +/- 0.12."""
    c, att, una, _ = _record(protocols.run_figure_3C)
    sep = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    ref = (ref_value_at(3, "C", "attended", _C_HI, log_x=True)
           - ref_value_at(3, "C", "unattended", _C_HI, log_x=True))
    assert abs(sep - ref) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_3.panel_C", figure=3,
           claim_id="T-3C-S-modbump")
def test_3C_modulation_has_interior_bump():
    """SOFT: paper 3C % modulation has an INTERIOR peak (not at an endpoint),
    ~30 at intermediate contrast. The model's curve falls monotonically from
    the low-contrast end, so its argmax is at index 0 — this soft test is
    EXPECTED to surface that mismatch (reported, non-blocking)."""
    c, _, _, pm = _record(protocols.run_figure_3C)
    peak = int(np.argmax(pm))
    assert 0 < peak < len(pm) - 1


# === Figure 3F — mixed attention effect (persistent separation) ===========

@tier_test(tier="qualitative", spec_ref="figures.figure_3.panel_F", figure=3,
           claim_id="T-3F-Q-order")
def test_3F_attended_above_unattended():
    _, att, una, _ = _record(protocols.run_figure_3F)
    assert np.all(att >= una - 0.02)


@tier_test(tier="qualitative", spec_ref="figures.figure_3.panel_F", figure=3,
           claim_id="T-3F-Q-sep")
def test_3F_separation_persists_at_high_contrast():
    """Paper 3F: attend-in-RF stays ABOVE attend-contralateral at high contrast
    (separation persists)."""
    c, att, una, _ = _record(protocols.run_figure_3F)
    sep = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    assert sep > 0.05


@tier_test(tier="hard", spec_ref="figures.figure_3.panel_F", figure=3,
           claim_id="T-3F-H-sep")
def test_3F_high_contrast_separation_matches_digitized():
    """HARD: attended-unattended at c=1 ~ digitized (~0.15) +/- 0.12."""
    c, att, una, _ = _record(protocols.run_figure_3F)
    sep = value_at_log(c, att, _C_HI) - value_at_log(c, una, _C_HI)
    ref = (ref_value_at(3, "F", "attended", _C_HI, log_x=True)
           - ref_value_at(3, "F", "unattended", _C_HI, log_x=True))
    assert abs(sep - ref) < 0.12


@tier_test(tier="soft", spec_ref="figures.figure_3.panel_F", figure=3,
           claim_id="T-3F-S-modlow")
def test_3F_modulation_largest_at_low_contrast():
    """SOFT: % modulation largest at low contrast (~100) +/- 15."""
    c, _, _, pm = _record(protocols.run_figure_3F)
    ref = ref_value_at(3, "F", "percent_modulation", c[0], log_x=True)
    assert abs(float(pm[0]) - ref) < 15.0
