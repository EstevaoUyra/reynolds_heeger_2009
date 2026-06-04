"""Contract test for the cross-figure root cause (audit CONTRACT_BUG).

ONE finding from the 2026-06-03 re-audit is encoded here, and it is the ROOT
CAUSE the per-figure tier tripwires (test_tier_figure_2..7, test_panel_axes)
already pin RED downstream:

  CONTRACT_BUG — "The contract patches the 1D suppression deficit with UNBOUNDED,
  FIGURE-FITTED, per-panel implementation-side knobs — suppressive_drive_gain
  (tuned 12/6/8/8/12/8 across panels), suppressive_spatial_sigma_scale
  (0.45/0.55/0.7/1.0), baseline_* — each note says the value is 'tuned
  per-protocol to match the paper's qualitative shape'. The paper has ONE model
  with ONE sigma and only the Table-1 sizes — NO per-panel suppression-gain."

Per author-tests/SKILL.md a ``*_BUG`` finding is a **MUST-PASS** test, and the
finding's ``fix`` makes the must-pass invariant explicit and paper-grounded:

  "if 1D is kept, promote ONE consistent suppression-normalization constant ...
  and REQUIRE it to hold UNCHANGED across all panels — forbid per-panel
  suppressive_drive_gain / sigma_scale / baseline tuning."

So the deterministic invariant is: the suppression-normalization knobs the model
applies (calibration.resolve, the SAME merged ledger the protocols consume and
the measurement record hashes) are IDENTICAL across every CRF protocol — ONE
model, ONE suppression normalization, as the paper has.

WHY THIS IS A LEGITIMATE MUST-PASS (not a fit target): the paper's Table-1
"Constants for all simulations" line (article_aware/spec/calibration.yaml:
model.sigma, model.suppressive_field_size 20, model.suppressive_tuning_width
180 — all cross-figure) is the only suppression specification; per-figure
suppression GAIN does not appear in the paper. A faithful mechanism — the genuine
2D field, OR a single promoted suppression constant — satisfies this by
construction. It CANNOT be greened by tuning a value to fit one figure: the only
way to pass is to make the suppression normalization the SAME everywhere (the
genuine fix the finding's ``fix`` prescribes). That is precisely the must-pass
property the SKILL requires (satisfiable by the correct mechanism alone).

These tests FAIL today (gain 12 vs 6 vs 8 vs 12; sigma-scale 0.55 vs 1.0 vs 0.45
vs 0.7) — that red is the root-cause record, and it is a GATING red (not a soft
tripwire) because the fix is a real, paper-grounded mechanism, not a magnitude
the cited parameters cannot reach. When the implementer unifies the suppression
normalization (one constant, or the 2D field), this flips green AND the per-panel
magnitude tripwires (2A under-saturation, 3C/3F shape, 4C/4E/5C/7C over-strong
gain, 6C absent sharpening) become reachable by the single faithful mechanism.

Evaluated on calibration.resolve_namespace (the model's resolved ledger), with the
expected invariant (one value) taken from the paper's one-model / Table-1-only
suppression specification — NOT from any figure's digitized curve, so this is a
fidelity check on the mechanism, not a self-consistency tautology.
"""

from __future__ import annotations

import pytest

from neuromodels.framework.testing import deterministic_test
from rh_model import calibration


# Every per-figure CRF protocol that drives suppression through a per-panel knob.
# (Fig 1 is the schematic; Figs 5/6/7 are tuning panels.)
_CRF_PROTOCOLS = ("figure_2A", "figure_2B", "figure_3C", "figure_3F",
                  "figure_4C", "figure_4E")

# The tuning-panel protocols (Figs 5/6/7). The 2026-06-03 re-audit SHARPENED the
# CONTRACT_BUG: not only do the CRF panels carry per-panel gains, the tuning
# protocols apply NO suppression gain at all (resolve -> None == effective gain
# 1), while the CRF panels apply 6-12. The finding states this directly:
# "the tuning protocols 5/6/7 apply gain=1 while CRF protocols apply 6-12 — that
# inconsistency is the bug." One model has ONE suppression normalization for
# EVERY panel, tuning panels included; the same normalization the CRF panels use
# must also be applied to 5/6/7 (finding's fix: "Apply the same suppression
# normalization to the tuning protocols (5/6/7), which currently apply none.").
_TUNING_PROTOCOLS = ("figure_5C", "figure_6C", "figure_7C")
_ALL_RESPONSE_PROTOCOLS = _CRF_PROTOCOLS + _TUNING_PROTOCOLS

# The suppression-normalization knobs the finding names as figure-fitted. The
# paper has ONE of each (or none — the paper has no suppression GAIN at all).
_SUPPRESSION_KNOBS = ("suppressive_drive_gain", "suppressive_spatial_sigma_scale")


def _resolved_knob(protocol: str, knob: str):
    """The value the model actually applies for ``<protocol>.<knob>``.

    Reads the SAME merged calibration ledger protocols.py consumes and the
    measurement record hashes (calibration_hash), so this measures the
    mechanism, never a re-derivation.
    """
    ns = calibration.resolve_namespace(protocol)
    return ns.get(knob)


@deterministic_test(
    spec_ref="figures.figure_2",  # cross-figure; anchored on the first CRF group
    figure="cross",
    claim_id="T-CONTRACT-supp-gain-single",
)
def test_suppressive_drive_gain_is_single_across_all_crf_panels():
    """MUST-PASS (CONTRACT_BUG root cause): the suppressive-drive gain is ONE
    value across every CRF protocol.

    The paper has one model and no per-figure suppression gain; a faithful
    mechanism (2D field, or one promoted suppression constant) uses the same
    suppression normalization for all panels. EXPECTED RED today: the contract
    tunes the gain per panel (12 / 6 / 8 / 8 / 12 / 8). Drive it green by
    UNIFYING the suppression mechanism — never by tuning a figure. Do NOT relax
    this to xfail/soft: it is a real, paper-grounded target.
    """
    gains = {p: _resolved_knob(p, "suppressive_drive_gain")
             for p in _CRF_PROTOCOLS}
    distinct = sorted({float(v) for v in gains.values() if v is not None})
    assert len(distinct) == 1, (
        "the paper has ONE model with NO per-figure suppressive_drive_gain; the "
        f"contract tunes it per panel: {gains}. Unify the suppression "
        "normalization (one constant, or the genuine 2D field) — do not tune."
    )


@deterministic_test(
    spec_ref="figures.figure_2",
    figure="cross",
    claim_id="T-CONTRACT-supp-sigma-single",
)
def test_suppressive_spatial_sigma_scale_is_single_across_crf_panels():
    """MUST-PASS (CONTRACT_BUG root cause): the suppressive spatial sigma-scale
    is ONE value wherever it is applied.

    The paper's suppressive field size (20) is a single Table-1 constant for all
    simulations (model.suppressive_field_size); the 1D effective-width scale that
    stands in for it must likewise be ONE value, not the per-panel
    0.55 / 1.0 / 0.45 / 0.7 the contract fits. EXPECTED RED today. Drive green by
    unifying the suppression field, not by per-panel tuning.
    """
    scales = {p: _resolved_knob(p, "suppressive_spatial_sigma_scale")
              for p in _CRF_PROTOCOLS}
    distinct = sorted({float(v) for v in scales.values() if v is not None})
    assert len(distinct) == 1, (
        "the paper's suppressive field size is a single constant for all "
        f"simulations; the contract tunes the 1D width scale per panel: {scales}. "
        "Unify it — do not tune per figure."
    )


@deterministic_test(
    spec_ref="figures.figure_2",
    figure="cross",
    claim_id="T-CONTRACT-supp-no-per-figure-gain",
)
@pytest.mark.parametrize("knob", _SUPPRESSION_KNOBS)
def test_no_crf_panel_overrides_suppression_relative_to_figure_2A(knob):
    """MUST-PASS (CONTRACT_BUG root cause): no CRF panel carries a suppression
    knob that DIFFERS from the Fig-2A baseline.

    A finer-grained restatement of the single-value invariant: pin Fig-2A as the
    reference and require every other CRF panel to inherit the SAME suppression
    normalization (the paper's one-model contract). EXPECTED RED today for the
    panels whose knob was tuned away from 2A's (e.g. 2B gain 6 vs 2A 12, 2B/3C/3F
    sigma-scale vs 2A 0.55). Flips green only when the per-panel suppression
    overrides are removed — the genuine fix, never a figure-fit.
    """
    baseline = _resolved_knob("figure_2A", knob)
    assert baseline is not None, f"figure_2A must define {knob} as the reference"
    offenders = {
        p: v for p in _CRF_PROTOCOLS
        if (v := _resolved_knob(p, knob)) is not None and float(v) != float(baseline)
    }
    assert not offenders, (
        f"{knob} must be inherited unchanged from figure_2A ({baseline}) by every "
        f"CRF panel (one model, one suppression normalization); these override it: "
        f"{offenders}. Remove the per-panel override — do not tune to fit."
    )


@deterministic_test(
    spec_ref="figures.figure_2",  # cross-figure; one suppression normalization
    figure="cross",
    claim_id="T-CONTRACT-supp-gain-tuning-equals-crf",
)
def test_tuning_protocols_apply_the_same_suppression_gain_as_crf_panels():
    """MUST-PASS (CONTRACT_BUG, 2026-06-03 sharpened): the tuning protocols
    (Figs 5/6/7) apply the SAME suppression-drive gain as the CRF panels — ONE
    model, ONE suppression normalization for EVERY panel.

    The re-audit demonstrated empirically that the CRF protocols apply
    suppressive_drive_gain 6-12 while the tuning protocols 5/6/7 apply NONE
    (resolve -> None, i.e. effective gain 1): "the tuning protocols 5/6/7 apply
    gain=1 while CRF protocols apply 6-12 — that inconsistency is the bug." The
    finding's fix is explicit: "Apply the same suppression normalization to the
    tuning protocols (5/6/7), which currently apply none."

    EXPECTED RED today: the CRF panels resolve a positive gain; the tuning panels
    resolve None. Drive green by UNIFYING the suppression mechanism across ALL
    panels (the genuine 2D field, or one promoted suppression constant applied
    everywhere) — never by tuning a figure. This is satisfiable by the correct
    mechanism alone: a single suppression normalization is, by construction, the
    same on every panel. Do NOT relax to xfail/soft.

    Evaluated on calibration.resolve_namespace (the model's resolved ledger, the
    SAME one protocols consume), with the expected invariant (one suppression
    normalization for all panels) taken from the paper's one-model / Table-1-only
    suppression specification — not from any digitized curve.
    """
    crf_gains = {p: _resolved_knob(p, "suppressive_drive_gain")
                 for p in _CRF_PROTOCOLS}
    tuning_gains = {p: _resolved_knob(p, "suppressive_drive_gain")
                    for p in _TUNING_PROTOCOLS}
    # The single suppression normalization the CRF panels (should) share; today
    # they disagree (covered by the tests above), but in EVERY case it is a
    # positive gain, whereas the tuning panels apply none — the inconsistency the
    # finding names. Require the resolved gain to be present AND identical across
    # the whole response-panel set.
    all_gains = {p: _resolved_knob(p, "suppressive_drive_gain")
                 for p in _ALL_RESPONSE_PROTOCOLS}
    missing = sorted(p for p, v in all_gains.items() if v is None)
    assert not missing, (
        "the tuning protocols apply NO suppression gain while the CRF panels "
        f"apply {sorted({float(v) for v in crf_gains.values() if v is not None})} "
        f"(tuning resolves: {tuning_gains}). The paper has ONE suppression "
        "normalization for every panel — apply it to 5/6/7 too. These panels "
        f"apply none: {missing}. Unify the suppression mechanism; do not tune."
    )
    distinct = sorted({float(v) for v in all_gains.values() if v is not None})
    assert len(distinct) == 1, (
        "one model, one suppression normalization across CRF AND tuning panels; "
        f"the resolved gains differ across the response set: {all_gains}. Unify "
        "the suppression mechanism (2D field, or one promoted constant) — do not "
        "tune per figure."
    )
