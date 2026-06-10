"""Tests encoding the SQ-002 RESOLUTION — the x=0 single-stimulus reduction
equivalence + the CODE-020 contrast-sweep window (author-tests skill).

WHAT THIS ENCODES (the MOST RECENT contract change)
---------------------------------------------------
The most recent contract change to this model is the Phase-A contract-consistency
pass (commit ac2281d, "propagate CODE-017/CODE-020 to all Fig-2/3 artifacts"),
which RESOLVED SQ-002 (logs/spec_questions.md, resolution_2026-06-10) via the
original author code. The Fig-2/3 baselines/window are no longer a Phase-A
assumption to be tuned — they are released author constants, and the 1D x=0
single-stimulus reduction is documented as a NUMERICALLY-VERIFIED equivalence to
the author two-separated-stimulus geometry (Figure2A/2B/3C/3F.m: two preferred
gratings at x = ±100, recorded at x = +100, attended Ax=+100 / unattended
attend-away Ax=-100; cRange = [1e-5, 1]).

The resolution's LOAD-BEARING numeric claims (pseudocode/figure_2_protocol.md
"Geometry note", verified bit-for-bit when this test was authored):

  (1) CONTRALATERAL stimulus drive at the recorded neuron = 0.0. The far
      preferred grating (Δx = 200 from the recorded one) contributes 0.0 to the
      stimulus drive E at the recorded neuron (its Gaussian, σ = stimulus_size
      ≤ 7, is negligible 200 units away). So the author two-stimulus E at the
      recorded neuron equals the single-stimulus E — dropping the far stimulus
      changes nothing there.

  (2) ATTEND-AWAY spatial gain at the recorded neuron ≈ 2.2e-10 ≈ A = 1
      (~6.7σ away). The unattended "attend away" attention field (Ax = -100,
      AxWidth = attention_field_size) evaluated at x = +100 is, to ~10 dp, a flat
      A = 1 field at the recorded neuron — so the protocol's `spatial_center=None`
      unattended condition (a genuine flat A=1) reproduces the author attend-away
      field at the recorded neuron.

  (3) The contrast sweep window is the author Figure*.m cRange = [1e-5, 1]
      (CODE-020), NOT the prior guessed [0.01, 1] that clipped the rising limb /
      contrast-gain left-shift.

Together (1)+(2) are the JUSTIFICATION for the whole 1D reduction the Fig-2/3
protocols use: the simpler single-stimulus-at-x=0 setup is faithful at the
recorded neuron precisely because the far stimulus drives nothing and the
attend-away field is flat there. (3) is the window that makes the saturating CRF
and the left-shift visible.

TAG -> TEST KIND (skills/author-tests/SKILL.md)
-----------------------------------------------
SQ-002 is RESOLVED via released author code (the lineage ladder rung 1) — it is a
code-grounded contract CORRECTION, not a GENUINE_DIVERGENCE/PAPER_ISSUE. So per
the skill these are MUST-PASS tests: the faithful mechanism (the author geometry
+ the cited field sizes + the CODE-020 window) satisfies them with NO free
parameter — they ARE the geometry, not a fit. They are GREEN today and stand as
the regression tripwire that keeps the documented equivalence (and the corrected
window) from silently drifting back to the retired [0.01, 1] / un-justified
reduction.

  - The equivalence is evaluated on the model's OWN E/A fields built with the
    author geometry (x = ±100, recorded x = +100), with the EXPECTED values taken
    from the SQ-002 resolution / author-code geometry (contralateral E
    contribution = 0; attend-away excess gain ≈ 2.2e-10) — not re-derived from the
    record the Fig-2/3 protocols draw from. A drift in the field construction
    (e.g. a wrap that leaks the far stimulus in, or an attention field that is not
    flat at 6.7σ) breaks the documented equivalence and trips these.

  - The window pin reads the binding calibration ledger (CODE-020) AND the actual
    swept endpoints the protocol produces, so a regression to [0.01, 1] in either
    the ledger or the protocol trips it.

NOT DUPLICATED HERE
-------------------
  - The CODE-017 BASELINE pin (baseline_modulated=5e-7; baseline_unmodulated=5.0
    for 3C / 0.0 for 3F) is already encoded by
    test_audit_2026_06_10.py::test_figure_3_baselines_are_code017_not_retired_a007
    (T-A610-3-baseline-code017-pin). SQ-002's baseline half is covered there; this
    module covers SQ-002's GEOMETRY-EQUIVALENCE + WINDOW half, which no existing
    test pins as a deterministic assertion.
"""

from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model.calibration import resolve, resolve_namespace
from rh_model.model import build_attention_field, build_stimulus_drive, default_params
from rh_model import protocols


# The author two-separated-stimulus geometry (Figure2A/2B/3C/3F.m): two preferred
# gratings at x = ±100 (θ = 0), the recorded neuron at the attended one (x = +100).
_RECORDED_X, _RECORDED_THETA = 100.0, 0.0
_FAR_X = -100.0

# The Fig-2/3 single-grating CRF panels that use the x=0 reduction + CODE-020 window.
_SINGLE_GRATING_PANELS = ("figure_2A", "figure_2B", "figure_3C", "figure_3F")


def _fields_for_panel(panel: str):
    """Build E (one- and two-stimulus) and the attend-away A field at the recorded
    neuron, using the panel's OWN cited field sizes (the author geometry).

    Returns (i, j, E_one, E_two, A_away) where (i, j) index the recorded neuron.
    """
    s = resolve_namespace(panel)
    p = default_params(
        stimulus_size=s["stimulus_size"],
        attention_field_size=s["attention_field_size"],
        peak_attention_gain_gamma=s["peak_attention_gain_gamma"],
        tuning_width=s["tuning_width"],
        recorded_x=_RECORDED_X,
        recorded_theta=_RECORDED_THETA,
    )
    xg, tg = p.x_grid, p.theta_grid
    i = int(np.argmin(np.abs(xg - _RECORDED_X)))
    j = int(np.argmin(np.abs(tg - _RECORDED_THETA)))

    one = build_stimulus_drive(
        [{"x": _RECORDED_X, "theta": 0.0, "contrast": 1.0}],
        xg, tg, s["stimulus_size"], s["tuning_width"],
    )
    two = build_stimulus_drive(
        [
            {"x": _RECORDED_X, "theta": 0.0, "contrast": 1.0},
            {"x": _FAR_X, "theta": 0.0, "contrast": 1.0},
        ],
        xg, tg, s["stimulus_size"], s["tuning_width"],
    )
    a_away = build_attention_field(
        {"spatial_center": _FAR_X, "feature_center": None},
        xg, tg, p.attention_field_size, p.peak_attention_gain_gamma,
    )
    return i, j, one[j, i], two[j, i], a_away[j, i], s["peak_attention_gain_gamma"]


@deterministic_test(
    spec_ref="simulation_protocols.figure_2A", figure=2,
    claim_id="T-SQ002-contralateral-drive-zero",
)
def test_far_stimulus_contributes_zero_drive_at_recorded_neuron():
    """MUST-PASS (SQ-002 resolution, equivalence claim 1): the far preferred grating
    at x = -100 (Δx = 200 from the recorded neuron at x = +100) contributes 0.0 to
    the stimulus drive E at the recorded neuron, so the author two-separated-stimulus
    E equals the single-stimulus E there. This is the first half of the documented
    justification for the x=0 single-stimulus reduction the Fig-2/3 protocols use.

    Evaluated on the model's own E field built with the AUTHOR geometry; the EXPECTED
    value (0.0 contralateral contribution) is the SQ-002 resolution / author-code
    geometry, not a re-derivation from the protocol record. Satisfiable by the
    correct mechanism alone — it is the geometry, not a fit (the stimulus Gaussian
    σ = stimulus_size ≤ 7 is negligible 200 units away). GREEN today; trips if a
    future field change leaks the far stimulus into the recorded drive (e.g. a wrap).

    Citation: SQ-002 resolution_2026-06-10 ; pseudocode/figure_2_protocol.md geometry
    note ("Δx = 200 ... contributes 0.0") ; Figure2A/2B/3C/3F.m two-stimulus geometry.
    """
    for panel in _SINGLE_GRATING_PANELS:
        _, _, e_one, e_two, _, _ = _fields_for_panel(panel)
        contra = abs(e_two - e_one)
        # Negligible relative to the recorded single-stimulus drive (which is O(0.2-0.4)).
        assert contra <= 1e-9 * max(e_one, 1.0), (
            f"{panel}: the far grating at x={_FAR_X} contributes {contra:.3e} to the "
            f"recorded-neuron drive E (single={e_one:.6f}, two-stim={e_two:.6f}); the "
            "SQ-002 reduction requires ~0 contralateral contribution (Δx=200, σ≤7). A "
            "non-zero value means the x=0 single-stimulus reduction is no longer "
            "faithful to the author two-stimulus geometry at the recorded neuron."
        )


@deterministic_test(
    spec_ref="simulation_protocols.figure_2A", figure=2,
    claim_id="T-SQ002-attend-away-gain-flat",
)
def test_attend_away_attention_field_is_flat_at_recorded_neuron():
    """MUST-PASS (SQ-002 resolution, equivalence claim 2): the author "attend away"
    attention field (centred on the FAR stimulus, Ax = -100) evaluated at the recorded
    neuron (x = +100, ~6.7σ away for the wide 2A/3C field) is, to ~10 dp, a flat
    A = 1 field — its EXCESS gain (A-1)/(γ-1) = G_x(+100) ≈ 2.2e-10. This is why the
    protocol's flat (spatial_center=None) unattended condition reproduces the author
    attend-away condition at the recorded neuron — the second half of the documented
    x=0-reduction justification.

    Evaluated on the model's own A field built with the AUTHOR attend-away geometry;
    the EXPECTED value (excess ≈ 2.2e-10 for the afs=30 panels) is the SQ-002
    resolution / author-code geometry. Satisfiable by the correct mechanism alone (a
    Gaussian field 6.7σ from its centre is ~0). GREEN today; trips if the attention
    field stops being flat at the far recorded location.

    The widest sigma-distance is the afs=30 panels (2A/3C): 200/30 ≈ 6.7σ, excess
    ≈ 2.2e-10. Narrower fields (2B afs=3, 3F afs=7) are even flatter (≫6.7σ), so the
    bound below (excess < 1e-8, i.e. A within 1e-8 of 1) holds for every panel and
    excludes the documented value with ample margin.

    Citation: SQ-002 resolution_2026-06-10 ; pseudocode/figure_2_protocol.md geometry
    note ("attend-away ... gain ≈ 2.2e-10 ≈ 1 ... ~6.7σ away") ; build_attention_field
    A = 1 + (γ-1)·G_x ; Figure2A/2B/3C/3F.m attend-away (Ax = -100).
    """
    for panel in _SINGLE_GRATING_PANELS:
        _, _, _, _, a_away, gamma = _fields_for_panel(panel)
        excess = (a_away - 1.0) / (gamma - 1.0)  # = G_x(+100) for the away field
        assert excess >= 0.0
        assert excess < 1e-8, (
            f"{panel}: attend-away excess gain G_x(+100) = {excess:.3e} (A_away = "
            f"{a_away:.12f}); the SQ-002 reduction requires the attend-away field to be "
            "flat (A ≈ 1) at the recorded neuron (the afs=30 2A/3C value is ≈2.2e-10, "
            "6.7σ away). A larger value means the unattended flat-A=1 protocol "
            "condition no longer matches the author attend-away field there."
        )

    # Anchor the documented ~2.2e-10 / 6.7σ value on the wide 2A field specifically,
    # so the test pins the actual SQ-002 number, not just "small".
    _, _, _, _, a_away_2A, gamma_2A = _fields_for_panel("figure_2A")
    excess_2A = (a_away_2A - 1.0) / (gamma_2A - 1.0)
    afs_2A = resolve("figure_2A.attention_field_size")
    sigma_dist = abs(_RECORDED_X - _FAR_X) / afs_2A
    assert abs(sigma_dist - 6.6667) < 0.01, (
        f"2A attend-away distance {sigma_dist:.4f}σ should be ~6.67σ (200/afs=30); "
        f"afs={afs_2A}."
    )
    assert abs(excess_2A - 2.2336e-10) <= 0.05e-10, (
        f"2A attend-away excess gain {excess_2A:.4e} should equal the SQ-002-documented "
        "≈2.2e-10 (6.7σ away). A divergence here means the attention-field geometry or "
        "the field size drifted from the author values."
    )


@deterministic_test(
    spec_ref="simulation_protocols.figure_2A", figure=2,
    claim_id="T-SQ002-crange-code020-window",
)
def test_fig2_fig3_contrast_window_is_author_code020_not_retired_001():
    """MUST-PASS (SQ-002 resolution, claim 3 / CODE-020): every single-grating CRF
    panel (2A/2B/3C/3F) sweeps the author Figure*.m cRange = [1e-5, 1], NOT the
    retired guessed [0.01, 1] that clipped the rising limb and the contrast-gain
    left-shift. Pins BOTH the binding calibration ledger (CODE-020) and the actual
    swept contrast endpoints the protocol produces, so a regression to [0.01, 1] in
    either layer trips it.

    Code-grounded must-pass (the window is the author script value, no free
    parameter). GREEN today; the regression tripwire against drifting the floor back
    up to 0.01 (which the prior pass proved hides the saturating CRF + left-shift).

    Citation: SQ-002 resolution_2026-06-10 ; calibration.yaml CODE-020
    (figure_*.c_range_lo/hi) ; Figure2A/2B/3C/3F.m cRange = [1e-5 1].
    """
    runners = {
        "figure_2A": protocols.run_figure_2A,
        "figure_2B": protocols.run_figure_2B,
        "figure_3C": protocols.run_figure_3C,
        "figure_3F": protocols.run_figure_3F,
    }
    for panel, runner in runners.items():
        lo = resolve(f"{panel}.c_range_lo")
        hi = resolve(f"{panel}.c_range_hi")
        # Ledger pins the CODE-020 author window.
        assert abs(lo - 1e-5) <= 1e-12, (
            f"{panel}.c_range_lo must be the author CODE-020 floor 1e-5 (the retired "
            f"guess was 0.01, which clips the rising limb); got {lo!r}."
        )
        assert hi == 1.0, (
            f"{panel}.c_range_hi must be the author CODE-020 ceiling 1.0; got {hi!r}."
        )
        # The protocol's actually-swept endpoints honour the CODE-020 window.
        c = np.asarray(runner()["c"], dtype=float)
        assert abs(c[0] - 1e-5) <= 1e-9, (
            f"{panel}: swept contrast floor {c[0]:.3e} must be the CODE-020 1e-5, not "
            "the retired 0.01 — the protocol clipped the rising limb if it is 0.01."
        )
        assert abs(c[-1] - 1.0) <= 1e-9, (
            f"{panel}: swept contrast ceiling {c[-1]:.6f} must be the CODE-020 1.0."
        )
