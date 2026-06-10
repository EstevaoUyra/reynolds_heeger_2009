"""Encode the DR-4C-sign RESOLUTION (commit 2125e53, 2026-06-10) as tests.

The most-recent contract change closed the long-open DR-4C-sign decision-needed
item: the apparent conflict between the published Figure-4C panel (which *looks*
like it draws the attended curve ABOVE attend-away with a "percentage INCREASE")
and the authors' released Figure4C.m (which computes
``100*(unattCRF - attCRF)/unattCRF`` and makes attend-null-in-RF a SUPPRESSION,
attended BELOW). The resolution: there is NO genuine paper-vs-code contradiction.
The apparent conflict was a DIGITIZER LABEL SWAP.

  - In Figure4C.m the legend is ('Att Away','Att RF'): ``unattCRF`` = Att-Away
    (contralateral, Ax=-110) and ``attCRF`` = Att-RF (attend-null-in-RF, Ax=110).
    The dashed modulation ``100*(unattCRF-attCRF)/unattCRF`` is drawn POSITIVE
    (~36% peak, declining). For that dashed curve to be positive, ``unattCRF``
    (Att-Away) must be the UPPER solid and ``attCRF`` (Att-RF) the LOWER solid —
    i.e. attending the null in the RF SUPPRESSES the recorded preferred neuron
    (C-021). So the published UPPER solid is the CONTRALATERAL/unattended curve,
    NOT "attended".
  - ``panel_C_digitized.json`` mislabeled the UPPER solid ``"attended"`` (it is
    the author's Att-Away / unattCRF) and the LOWER ``"unattended"``. Recomputing
    the author formula on the digitized solids — with the labels corrected
    (UPPER = unattCRF, LOWER = attCRF) — reproduces the published percent
    modulation across the response-bearing contrast range.

This module is the machine-checkable form of that closure. All three tests are
MUST-PASS (qualitative tier): they encode a RESOLVED, code-resolvable contract
fact (a BUG-class disposition: digitizer label swap corrected), not a genuine
divergence. They do NOT require any model change — the model already follows
Figure4C.m and is correct; these certify the reference matches Figure4C.m and
that the model reproduces that label-corrected reference.

Tag -> test kind (skills/author-tests/SKILL.md): CONTRACT-BUG (digitizer label
swap) -> MUST-PASS. Satisfiable by the correct (already-built) mechanism alone;
NO tuning. The expected values are read from the DIGITIZED REFERENCE (the curves
the auditor digitized), and the model is compared AGAINST that reference, never
against its own record.

Citation: paper/code/attentionModel/Figure4C.m ; A-012 (RESOLVED) ;
figures/figure_4/panel_C.md ; C-021 ; CODE-018 ; CODE-021.
"""

from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols
from rh_tier_helpers import ref_curve


# The digitized panel_C curves were traced under the SWAPPED labels. The
# label-corrected assignment (DR-4C-sign resolution) is:
#   author unattCRF (Att-Away)  == the curve digitized as "attended"  (UPPER solid)
#   author attCRF   (Att-RF)    == the curve digitized as "unattended" (LOWER solid)
# Both are sampled over the same contrast grid.
def _label_corrected_4c_reference() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return (c, unattCRF_upper, attCRF_lower, published_percent_modulation).

    Reads the DIGITIZED reference and applies the DR-4C-sign label correction:
    the curve digitized as "attended" is the author's unattCRF (Att-Away, the
    UPPER solid); the curve digitized as "unattended" is the author's attCRF
    (Att-RF, the LOWER solid). Per Figure4C.m the panel's dashed modulation is
    ``100*(unattCRF-attCRF)/unattCRF``.

    Citation: paper/code/attentionModel/Figure4C.m ; figures/figure_4/panel_C.md
    """
    c_up, unatt_upper = ref_curve(4, "C", "attended")     # mislabeled: author unattCRF
    c_lo, att_lower = ref_curve(4, "C", "unattended")     # mislabeled: author attCRF
    c_pm, published_pm = ref_curve(4, "C", "percent_modulation")
    # the three reference curves share one contrast grid
    assert np.allclose(c_up, c_lo)
    assert np.allclose(c_up, c_pm)
    return c_up, np.asarray(unatt_upper), np.asarray(att_lower), np.asarray(published_pm)


def _response_bearing_mask(unatt_upper: np.ndarray, att_lower: np.ndarray) -> np.ndarray:
    """Samples where BOTH solids carry response and are resolvably separated.

    The lowest few contrasts were digitized to a near-identical merged value
    (~0.019), where 100*(unatt-att)/unatt is a 0/0-like artifact and the traced
    percent modulation is unreliable; the DR-4C-sign resolution states the
    pointwise reproduction holds in the RESPONSE-BEARING mid/high range. This mask
    selects that range so the self-consistency check is on the trustworthy points.

    Assumption: A-012 (RESOLVED)
    """
    scale = float(max(unatt_upper.max(), att_lower.max(), 1e-12))
    return (unatt_upper > 0.10 * scale) & (att_lower > 0.10 * scale)


@deterministic_test(
    spec_ref="figures.figure_4.panel_C", figure=4, claim_id="DR-4C-sign-order"
)
def test_published_4c_upper_solid_is_attend_away_not_attended():
    """MUST-PASS (CONTRACT-BUG: digitizer label swap). The published UPPER 4C
    solid is the author's unattCRF (Att-Away), the LOWER is attCRF (Att-RF /
    attend-null-in-RF). Under the corrected labels the UPPER curve is at or above
    the LOWER everywhere — i.e. attending the null in the RF SUPPRESSES the
    recorded preferred neuron (C-021), the LOWER curve. This is the geometric
    consequence the DR-4C-sign resolution requires for the panel's dashed
    modulation to be POSITIVE.

    Citation: paper/code/attentionModel/Figure4C.m (legend 'Att Away','Att RF';
    mod = 100*(unattCRF-attCRF)/unattCRF) ; C-021
    """
    _, unatt_upper, att_lower, _ = _label_corrected_4c_reference()
    # UPPER (author Att-Away / unattCRF) at or above LOWER (Att-RF / attCRF):
    # attend-null-in-RF is the suppressed (lower) condition.
    assert np.all(unatt_upper >= att_lower - 1e-9)
    # and meaningfully separated somewhere on the rise (a real suppression, not a tie)
    scale = float(max(unatt_upper.max(), att_lower.max(), 1e-12))
    assert float(np.max((unatt_upper - att_lower) / scale)) > 0.03


@deterministic_test(
    spec_ref="figures.figure_4.panel_C", figure=4, claim_id="DR-4C-sign-formula"
)
def test_author_suppression_formula_reproduces_published_percent_modulation():
    """MUST-PASS (CONTRACT-BUG: digitizer label swap). Recomputing the author
    Figure4C.m formula ``100*(unattCRF-attCRF)/unattCRF`` on the LABEL-CORRECTED
    digitized solids (UPPER=unattCRF, LOWER=attCRF) reproduces the panel's
    published dashed percent modulation across the response-bearing contrast
    range. This confirms published-panel == Figure4C.m (no paper/code defect):
    the only error was the digitizer's curve labels.

    The published modulation is POSITIVE everywhere and DECLINES from low to high
    contrast (peak ~36% in the low-contrast half toward ~3% at the top) — the
    suppression sign, not a facilitation increase.

    Citation: paper/code/attentionModel/Figure4C.m (line 74: dashed = 100*(unattCRF-attCRF)/unattCRF)
    """
    _, unatt_upper, att_lower, published_pm = _label_corrected_4c_reference()

    # Sign + shape of the PUBLISHED dashed curve (the digitized right-axis trace).
    assert np.all(published_pm >= -1e-6)              # positive (suppression sign)
    peak_idx = int(np.argmax(published_pm))
    assert peak_idx < len(published_pm) // 2 + 1      # peak in the low-contrast half
    assert published_pm[-1] < published_pm[peak_idx]  # declines toward high contrast
    assert published_pm.max() <= 100.0                # within the panel's 0-100 axis

    # Pointwise reproduction of the published modulation by the author formula on
    # the (label-corrected) solids, in the trustworthy response-bearing range.
    recomputed = 100.0 * (unatt_upper - att_lower) / np.maximum(unatt_upper, 1e-12)
    mask = _response_bearing_mask(unatt_upper, att_lower)
    assert np.count_nonzero(mask) >= 6
    # recomputed-from-solids vs the independently traced dashed curve agree to
    # within the digitization noise of two separate traces (generous +/-12 % pts).
    assert float(np.max(np.abs(recomputed[mask] - published_pm[mask]))) < 12.0


@deterministic_test(
    spec_ref="simulation_protocols.figure_4C", figure=4, claim_id="DR-4C-sign-model-follows-code"
)
def test_model_4c_reproduces_label_corrected_suppression_reference():
    """MUST-PASS (CONTRACT-BUG: digitizer label swap). The model already follows
    Figure4C.m and is correct: its 4C record is a SUPPRESSION panel whose
    suppression-sign percent modulation ``100*(unatt-att)/unatt`` matches the
    label-corrected published reference in sign, shape, and peak magnitude.

    Compared AGAINST the digitized reference (the auditor's traced values), not
    against the model's own record: the model peak suppression modulation must
    land near the published peak (~36%), be positive, and decline toward high
    contrast. ``attended_CRF`` is the model's attend-null-in-RF (author attCRF);
    ``unattended_CRF`` is attend-away (author unattCRF).

    Citation: paper/code/attentionModel/Figure4C.m ; C-021 ; A-012 (RESOLVED)
    """
    out = protocols.run_figure_4C()
    att = np.asarray(out["attended_CRF"], dtype=float)     # attend-null-in-RF (attCRF)
    una = np.asarray(out["unattended_CRF"], dtype=float)   # attend-away (unattCRF)

    # Same suppression geometry as the label-corrected reference: attCRF <= unattCRF.
    assert np.all(att <= una + 1e-9)

    model_pm = 100.0 * (una - att) / np.maximum(una, 1e-12)
    assert float(model_pm.max()) > 1.0
    model_peak_idx = int(np.argmax(model_pm))
    assert model_peak_idx < len(model_pm) // 2 + 1       # low-contrast-weighted
    assert model_pm[-1] < model_pm[model_peak_idx]       # declining
    assert float(model_pm.max()) <= 100.0                # within the 0-100 axis

    # Quantitative agreement with the PUBLISHED peak modulation (digitized ~36%).
    _, _, _, published_pm = _label_corrected_4c_reference()
    published_peak = float(published_pm.max())
    assert published_peak < 60.0                          # reference sanity (~36%)
    assert abs(float(model_pm.max()) - published_peak) < 15.0
