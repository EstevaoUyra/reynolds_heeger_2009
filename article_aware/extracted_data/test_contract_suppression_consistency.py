"""Contract test for the ONE-suppression-normalization invariant (audit CONTRACT_BUG).

This file is the machine-checkable form of the 2026-06-04 audit's model-scope
CONTRACT_BUG finding ("model (contract test)"):

  CONTRACT_BUG — "test_contract_suppression_consistency.py required a single
  NON-None suppressive_drive_gain / suppressive_spatial_sigma_scale resolved on
  every CRF panel. The SQ-005 resolution settled from the AUTHOR CODE that NO
  per-panel suppression gain exists; the faithful model resolves None everywhere,
  so the test fails its LETTER while satisfying its INTENT (one global suppression
  normalization on every panel). The test encoded the RETIRED per-panel-gain shape
  of fix."

  fix — "Rewrite the predicate to assert 'no per-panel suppression key resolves
  on any protocol; the global suppressive_field_size and suppressive_tuning_width
  are identical across panels'."

This is the SAME scientific invariant the prior version targeted — one model, one
suppression normalization for every panel — but stated in the shape the faithful
mechanism actually takes after the per-panel knobs were DELETED (commit a6419a9,
SQ-005 resolved from paper/code/attentionModel/attentionModel.m). The prior file
asserted the invariant via a single NON-None per-panel gain; the authors' code has
no per-panel gain at all, so the faithful contract resolves those keys to None on
every protocol and carries the suppression spec as TWO global constants:

  - model.suppressive_field_size  (IxWidth, spatial pool σ) = 20, attentionModel.m
  - model.suppressive_tuning_width (IthetaWidth, feature pool σ) = 360 (≈ all
    orientations; the impl ledger overrides the paper's nominal 180 per
    attentionModel.m's IthetaWidth default — see calibration.yaml SQ-005 note).

Per skills/author-tests/SKILL.md a ``*_BUG`` finding is a **MUST-PASS** test, and
this one is satisfiable by the **correct mechanism alone**: a faithful model that
took the authors' single space×feature suppressive pool has, BY CONSTRUCTION, no
per-panel suppression knob and one global field-size/tuning-width — it CANNOT be
greened by tuning a figure. (Indeed the committed model already satisfies it; the
test now guards against a regression that would re-introduce a per-panel knob, the
exact laundering SQ-005 retired.)

WHY THIS IS A FIDELITY CHECK, not a self-consistency tautology: the EXPECTED
invariant (no per-panel suppression key; one global field-size + one global
tuning-width) is taken from the paper's one-model / Table-1-only suppression
specification and the authors' attentionModel.m — NOT from any digitized figure
curve. It is evaluated on calibration.resolve / resolve_namespace, the SAME merged
ledger protocols.py consumes and the measurement record hashes.

------------------------------------------------------------------------------
SUPERSEDES the prior (2026-06-03) version of this file, which asserted a single
NON-None per-panel suppressive_drive_gain / suppressive_spatial_sigma_scale across
panels. That predicate encoded the RETIRED per-panel-gain shape of fix (SQ-007
Gap 2) and is unsatisfiable by the faithful model (every knob now resolves None).
The 2026-06-04 audit, resolved from the author code, established that the faithful
contract has NO per-panel suppression gain; this file is rewritten to that shape.
------------------------------------------------------------------------------
"""

from __future__ import annotations

import pytest

from neuromodels.framework.testing import deterministic_test
from rh_model import calibration


# Every per-figure response protocol — CRF panels AND tuning panels. One model,
# one suppression normalization for EVERY panel, so the no-per-panel-knob
# invariant must hold on the whole set (Fig 1 is the schematic).
_CRF_PROTOCOLS = ("figure_2A", "figure_2B", "figure_3C", "figure_3F",
                  "figure_4C", "figure_4E")
_TUNING_PROTOCOLS = ("figure_5C", "figure_6C", "figure_7C")
_ALL_RESPONSE_PROTOCOLS = _CRF_PROTOCOLS + _TUNING_PROTOCOLS

# The per-panel suppression-FITTING knobs the prior contract carried and SQ-005
# RETIRED. A faithful model resolves each of these to None on every protocol —
# there is no per-figure suppression gain or spatial-σ scale in the author code.
_RETIRED_PER_PANEL_KNOBS = (
    "suppressive_drive_gain",
    "suppressive_spatial_sigma_scale",
)

# The TWO global suppression constants that DO carry the spec (attentionModel.m
# IxWidth / IthetaWidth; Table-1 "Constants for all simulations"). These are
# model.* (cross-figure) keys, identical for every panel by construction.
_GLOBAL_SUPPRESSION_KEYS = (
    "model.suppressive_field_size",    # spatial pool σ (IxWidth) = 20
    "model.suppressive_tuning_width",  # feature pool σ (IthetaWidth) = 360
)


def _resolved_knob(protocol: str, knob: str):
    """The value the model actually applies for ``<protocol>.<knob>``.

    Reads the SAME merged calibration ledger protocols.py consumes and the
    measurement record hashes (resolved_ledger_hash), so this measures the
    mechanism, never a re-derivation.
    """
    ns = calibration.resolve_namespace(protocol)
    return ns.get(knob)


@deterministic_test(
    spec_ref="figures.figure_2",  # cross-figure invariant; anchored on first CRF
    figure="cross",
    claim_id="T-CONTRACT-supp-no-per-panel-knob",
)
@pytest.mark.parametrize("knob", _RETIRED_PER_PANEL_KNOBS)
def test_no_per_panel_suppression_knob_resolves_on_any_protocol(knob):
    """MUST-PASS (CONTRACT_BUG, 2026-06-04): NO per-panel suppression knob
    resolves on ANY response protocol — the authors' code (attentionModel.m) has
    one space×feature suppressive pool and no per-figure suppression gain or
    spatial-σ scale. A faithful model that adopts that pool resolves
    ``suppressive_drive_gain`` and ``suppressive_spatial_sigma_scale`` to None on
    every CRF AND tuning panel.

    This is the predicate the audit's ``fix`` prescribes ("no per-panel
    suppression key resolves on any protocol"). It is satisfiable by the correct
    mechanism alone — a single global suppressive pool has, by construction, no
    per-panel knob — and CANNOT be greened by tuning a figure. It guards against a
    regression that re-introduces a per-panel suppression knob (the SQ-005
    laundering this audit retired).

    Citation: SQ-005 / paper/code/attentionModel/attentionModel.m (single
    conv2sepYcirc suppressive pool, no per-panel gain); calibration.yaml SQ-005
    note (per-panel suppressive_drive_gain / suppressive_spatial_sigma_scale
    RETIRED).
    """
    resolved = {p: _resolved_knob(p, knob) for p in _ALL_RESPONSE_PROTOCOLS}
    offenders = {p: v for p, v in resolved.items() if v is not None}
    assert not offenders, (
        f"the authors' code carries NO per-panel {knob}; a faithful model resolves "
        f"it to None on every panel. These protocols re-introduce a per-panel "
        f"suppression knob: {offenders}. Remove it — the suppression spec is the "
        f"global model.suppressive_field_size / model.suppressive_tuning_width, "
        f"not a per-figure value. Do NOT tune to fit a figure."
    )


@deterministic_test(
    spec_ref="figures.figure_2",
    figure="cross",
    claim_id="T-CONTRACT-supp-global-field-size-single",
)
def test_global_suppressive_field_size_is_one_constant_for_all_panels():
    """MUST-PASS (CONTRACT_BUG, 2026-06-04): the suppressive SPATIAL field size
    (IxWidth) is ONE global constant for every panel — model.suppressive_field_size
    = 20 (Table-1 "Constants for all simulations"; attentionModel.m IxWidth=20).
    There is no per-panel spatial suppression width; the single global key is what
    every protocol's suppressive pool uses.

    Verifies (a) the global key resolves to a positive scalar, and (b) NO protocol
    namespace shadows it with a per-panel ``suppressive_field_size`` override that
    differs from the global value (which would re-create the per-figure tuning).

    Citation: C-010 / Table 1 ("suppressive field size = 20"); attentionModel.m
    IxWidth=20.
    """
    global_value = calibration.resolve("model.suppressive_field_size")
    assert global_value is not None and float(global_value) > 0.0, (
        "model.suppressive_field_size must resolve to the single Table-1 spatial "
        f"suppressive σ (20); got {global_value!r}."
    )
    # no protocol overrides it with a differing per-panel value
    overrides = {
        p: v for p in _ALL_RESPONSE_PROTOCOLS
        if (v := _resolved_knob(p, "suppressive_field_size")) is not None
        and float(v) != float(global_value)
    }
    assert not overrides, (
        "the suppressive spatial field size is a single global constant for all "
        f"simulations ({global_value}); these panels override it per-figure: "
        f"{overrides}. Remove the override — one model, one suppressive field size."
    )


@deterministic_test(
    spec_ref="figures.figure_2",
    figure="cross",
    claim_id="T-CONTRACT-supp-global-tuning-width-single",
)
def test_global_suppressive_tuning_width_is_one_constant_for_all_panels():
    """MUST-PASS (CONTRACT_BUG, 2026-06-04): the suppressive FEATURE tuning width
    (IthetaWidth) is ONE global constant for every panel —
    model.suppressive_tuning_width (≈360, all-orientations pool per
    attentionModel.m's IthetaWidth default; calibration.yaml SQ-005 note). There is
    no per-panel feature suppression width.

    Verifies the global key resolves to a positive scalar and no protocol shadows
    it with a differing per-panel ``suppressive_tuning_width``.

    Citation: SQ-005 / attentionModel.m IthetaWidth; calibration.yaml
    model.suppressive_tuning_width note.
    """
    global_value = calibration.resolve("model.suppressive_tuning_width")
    assert global_value is not None and float(global_value) > 0.0, (
        "model.suppressive_tuning_width must resolve to the single global feature "
        f"suppressive σ; got {global_value!r}."
    )
    overrides = {
        p: v for p in _ALL_RESPONSE_PROTOCOLS
        if (v := _resolved_knob(p, "suppressive_tuning_width")) is not None
        and float(v) != float(global_value)
    }
    assert not overrides, (
        "the suppressive feature tuning width is a single global constant for all "
        f"simulations ({global_value}); these panels override it per-figure: "
        f"{overrides}. Remove the override — one model, one suppressive tuning width."
    )
