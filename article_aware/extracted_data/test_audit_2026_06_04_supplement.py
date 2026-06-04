"""Supplement to test_audit_2026_06_04.py — the audit findings that the main
audit file mentions but does not yet pin as their own deterministic tests.

The headline of the 2026-06-04 audit (see test_audit_2026_06_04.py) is that the
forward model (model.py, Eqs. 5-6) is FAITHFUL operator-for-operator against the
authors' released MATLAB (paper/code/attentionModel/attentionModel.m), and the CRF
"divergences" are protocol-level CODE/CONTRACT bugs — a clipped contrast window and
co-located stimuli. The main file encodes 2A/3C/4E/4C/7C/6C. This supplement adds:

  1. Figure 2B and Figure 3F contrast-window tests (CONTRACT_BUG) — the audit names
     2A/2B/3C/3F as sharing ONE window bug (author cRange [1e-5,1], not [0.01,1]),
     but the main file only pins 2A and 3C. 2B and 3F sweep [0.01,1] today and need
     the same MUST-PASS window assertion so the implementer routes the per-panel
     cRange through THEIR sweep generators (and view xlim) too.

  2. Digitized-reference x_range tripwire (PAPER_ISSUE) — the 2A/2B/3C/3F/4C/4E
     digitized JSON x_range is [0.01,1] (the digitizer guessed the left edge; the
     paper has no numeric x ticks), but the AUTHOR axis floor is 1e-5 (and 1e-4 for
     4C/4E). The references therefore place the rise ~20-30× too high. Per
     skills/author-tests/SKILL.md a SUSPECTED-PAPER-ISSUE is a RED TRIPWIRE, not a
     must-pass: it flips green only when the references are RE-DIGITIZED over the
     author window. Soft tier — measured, reported, never gates.

  3. Faithful-forward-operator regression guards (FAITHFUL) — the audit's strongest
     finding is that the forward model IS the authors' operator. These pin the
     load-bearing constants/operators (rectification at 0, σ=1e-6, attention field
     A=1+(γ-1)·G, unit-volume separable suppressive pool) so a future edit that
     silently breaks faithfulness trips a MUST-PASS test. Targets are the authors'
     MATLAB constants, not a digitized figure curve.

Tag -> test kind (skills/author-tests/SKILL.md):
  CONTRACT_BUG / FAITHFUL-guard -> MUST-PASS (correct mechanism reproduces it).
  PAPER_ISSUE                   -> RED TRIPWIRE (soft / xfail; progress signal).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import model, protocols
from rh_tier_helpers import tier_test


_FIGURES_ROOT = Path(__file__).resolve().parents[1] / "figures"

# Author CRF contrast windows (paper/code/attentionModel/Figure*.m `cRange`),
# echoing _AUTHOR_CRANGE in test_audit_2026_06_04.py.
_AUTHOR_CRANGE = {
    "2A": (1e-5, 1.0), "2B": (1e-5, 1.0),
    "3C": (1e-5, 1.0), "3F": (1e-5, 1.0),
    "4C": (1e-4, 0.1), "4E": (1e-4, 0.1),
}


# ===========================================================================
# 1. Figure 2B / 3F contrast-window (CODE_BUG) — same clipped-window bug the
#    main file pins for 2A/3C. The author CRF scripts use cRange=[1e-5,1]; 2B/3F
#    sweep [0.01,1] today, clipping the entire rising limb and the attended-vs-
#    ignored left-shift off the left edge. MUST-PASS: route the per-panel cRange
#    through run_figure_2B / run_figure_3F. No model change.
# ===========================================================================

@deterministic_test(
    spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="AUD-A-2B-window",
)
def test_2B_contrast_sweep_uses_author_window():
    """MUST-PASS (CODE_BUG): Figure 2B's contrast sweep spans the author cRange
    [1e-5, 1], not the hardcoded [0.01, 1]. 2B is named alongside 2A/3C/3F in the
    audit as sharing the clipped-window bug; the main audit file pins 2A but not
    2B. The diagnostic contrast-gain rise lives below 0.01.

    Citation: C-013 / paper/code/attentionModel/Figure2B.m (cRange=[1e-5 1])
    """
    c = np.asarray(protocols.run_figure_2B()["c"], dtype=float)
    lo, hi = _AUTHOR_CRANGE["2B"]
    assert float(c.min()) <= lo * 1.5
    assert float(c.max()) >= hi * 0.99
    assert float(c.min()) < 0.01  # not the old hardcoded 0.01 floor


@deterministic_test(
    spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="AUD-A-3F-window",
)
def test_3F_contrast_sweep_uses_author_window():
    """MUST-PASS (CODE_BUG): Figure 3F's contrast sweep spans the author cRange
    [1e-5, 1], not [0.01, 1]. 3F (the response-gain baseline panel, unmod=0,
    mod=5e-7) shares the clipped-window bug; the main audit file pins 3C but not
    3F.

    Citation: C-014 / paper/code/attentionModel/Figure3F.m (cRange=[1e-5 1])
    """
    c = np.asarray(protocols.run_figure_3F()["c"], dtype=float)
    lo, hi = _AUTHOR_CRANGE["3F"]
    assert float(c.min()) <= lo * 1.5
    assert float(c.max()) >= hi * 0.99
    assert float(c.min()) < 0.01


# ===========================================================================
# 2. Digitized-reference x_range tripwire (PAPER_ISSUE) — the digitized JSON
#    x_range is the digitizer's GUESS ([0.01,1]); the author axis floor is 1e-5
#    (2A/2B/3C/3F) / 1e-4 (4C/4E). The references place the rise ~20-30× too high,
#    so the half-max / left-shift claims are not yet testable against them. This
#    is a reference-ARTIFACT issue, routed like a tripwire: it flips green only
#    when the references are re-digitized over the author window. Soft tier
#    (conftest non-strict xfail): measured & reported, NEVER gates. DO NOT "fix"
#    by editing the model — the resolution is re-digitization (a Phase-A artifact
#    change), and until then this RED is the standing progress signal.
# ===========================================================================

def _digitized_x_range(figure: int, panel: str) -> tuple[float, float]:
    path = _FIGURES_ROOT / f"figure_{figure}" / f"panel_{panel}_digitized.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    lo, hi = data["x_range"]
    return float(lo), float(hi)


# (figure, panel, author_floor, author_ceiling)
_DIGITIZED_WINDOW_TARGETS = [
    (2, "A", 1e-5, 1.0), (2, "B", 1e-5, 1.0),
    (3, "C", 1e-5, 1.0), (3, "F", 1e-5, 1.0),
    (4, "C", 1e-4, 0.1), (4, "E", 1e-4, 0.1),
]


def _make_digitization_tripwire(figure: int, panel: str, lo: float, hi: float):
    @tier_test(
        tier="soft",
        spec_ref=f"figures.figure_{figure}",
        figure=figure,
        claim_id=f"AUD-PAPER-{figure}{panel}-digitized-window",
        paper_issue=(
            f"figure_{figure}/panel_{panel}_digitized.json x_range is the "
            f"digitizer's guessed [0.01,1] (the paper has no numeric x ticks); the "
            f"AUTHOR axis floor is [{lo:g},{hi:g}] (Figure{figure}{panel}.m cRange). "
            f"The reference therefore places the contrast-gain rise ~20-30x too "
            f"high, so the half-max / left-shift claims are not testable against it. "
            f"PAPER_ISSUE tripwire: flips green only on RE-DIGITIZATION over the "
            f"author window. Do NOT edit the model to satisfy it."
        ),
    )
    def _test():
        f"""RED TRIPWIRE (PAPER_ISSUE): figure_{figure}/panel_{panel} digitized
        x_range must span the AUTHOR contrast window [{lo:g}, {hi:g}], not the
        digitizer's guessed [0.01, 1]. EXPECTED to xfail until the panel is
        re-digitized over the author window; a soft (non-blocking) progress signal,
        not a model-fit target."""
        dlo, dhi = _digitized_x_range(figure, panel)
        # left edge re-digitized down to (≈) the author floor ...
        assert dlo <= lo * 1.5, (
            f"digitized x_range floor {dlo:g} is the guessed edge; re-digitize to "
            f"the author floor {lo:g}"
        )
        # ... and the ceiling at the author top (1.0 for 2/3, 0.1 for 4C/4E).
        assert abs(dhi - hi) <= max(0.02, hi * 0.02), (
            f"digitized x_range ceiling {dhi:g} != author ceiling {hi:g}"
        )

    _test.__name__ = f"test_{figure}{panel}_digitized_window_matches_author_range"
    _test.__qualname__ = _test.__name__
    return _test


# Bind one tripwire per panel at module scope so pytest collects them.
for _fig, _pan, _lo, _hi in _DIGITIZED_WINDOW_TARGETS:
    _t = _make_digitization_tripwire(_fig, _pan, _lo, _hi)
    globals()[_t.__name__] = _t
del _fig, _pan, _lo, _hi, _t


# ===========================================================================
# 3. Faithful-forward-operator regression guards (FAITHFUL) — pin the authors'
#    operator so an edit that breaks faithfulness trips. Targets are the authors'
#    MATLAB constants (attentionModel.m), NOT a digitized curve. MUST-PASS: the
#    committed faithful model satisfies them by construction.
# ===========================================================================

@deterministic_test(
    spec_ref="model.compute_output", figure="model", claim_id="AUD-FAITH-rectify",
)
def test_compute_output_rectifies_at_zero_eq5():
    """MUST-PASS (FAITHFUL): compute_output (Eq. 5) rectifies the response at 0 —
    a negative numerator (A*E below threshold_T) clamps to 0, never negative.
    attentionModel.m: R = max(0, (A.*E)./(S+sigma)). Guards the rectification the
    audit verified operator-for-operator.

    Citation: Eq. 5 / paper/code/attentionModel/attentionModel.m (max(0,...))
    """
    # A*E spans negative→positive; S+sigma strictly positive. Output must be >= 0.
    A = np.array([[1.0, 1.0, 1.0]])
    E = np.array([[-2.0, 0.0, 3.0]])
    S = np.array([[0.5, 0.5, 0.5]])
    R = model.compute_output(A, E, S, sigma=1e-6, threshold_T=0.0)
    assert np.all(R >= 0.0), "Eq. 5 output must be rectified at 0 (max(0, ...))"
    # the positive drive passes through divisively; the negative one clamps to 0.
    assert R[0, 0] == 0.0
    assert R[0, 2] > 0.0


@deterministic_test(
    spec_ref="model.build_attention_field", figure="model",
    claim_id="AUD-FAITH-attfield",
)
def test_attention_field_is_one_plus_gamma_minus_one_gaussian_eq():
    """MUST-PASS (FAITHFUL): the attention field is A = 1 + (γ-1)·G (baseline 1.0
    far from the attended locus, peak γ at it), per attentionModel.m
    attentionGain = 1 + (Apeak-Abase)*G with Abase=1. Guards the attention-field
    construction the audit verified (oval G_x·G_theta).

    Citation: C-019 / attentionModel.m (A = Abase + (Apeak-Abase).*attfield, Abase=1)
    """
    x_grid = np.arange(-200.0, 201.0, 1.0)
    theta_grid = np.arange(-180.0, 180.0, 1.0)
    gamma = 2.0
    # spatial attention centered at x=100 (the audit's Fig-1 R1 locus). The
    # condition-dict schema is {'spatial_center', 'feature_center'} (model.py).
    A = model.build_attention_field(
        attention_condition={"spatial_center": 100.0, "feature_center": None},
        x_grid=x_grid, theta_grid=theta_grid,
        attention_field_size=30.0, peak_attention_gain_gamma=gamma,
    )
    # baseline far from the attended locus is 1.0 (NOT 0): A = 1 + (γ-1)·G.
    assert abs(float(A.min()) - 1.0) < 1e-3, "attention-field baseline must be 1.0"
    # peak is exactly γ at the attended locus (G=1 there); never exceeds γ.
    assert float(A.max()) <= gamma + 1e-6
    assert abs(float(A.max()) - gamma) < 1e-3, "peak must reach γ at the locus"
    # a flat (no-attention) field is exactly 1.0 everywhere — the γ-1 prefactor.
    A_flat = model.build_attention_field(
        attention_condition={"spatial_center": None, "feature_center": None},
        x_grid=x_grid, theta_grid=theta_grid,
        attention_field_size=30.0, peak_attention_gain_gamma=gamma,
    )
    assert np.allclose(A_flat, 1.0), "no-attention field must be 1.0 everywhere"


@deterministic_test(
    spec_ref="model.compute_suppressive_drive", figure="model",
    claim_id="AUD-FAITH-supp-pool",
)
def test_suppressive_drive_is_separable_unit_volume_pool_eq6():
    """MUST-PASS (FAITHFUL): the suppressive drive is a SEPARABLE space×feature
    convolution of (A*E) with NO dx/dtheta spacing factor, and the SPATIAL kernel
    is unit-volume (sum=1, the normpdf normalization). For a uniform unit input,
    separability makes the pooled drive equal sum(s_x)·sum(s_theta) everywhere in
    the spatial interior (away from the zero-padded x edges) — i.e. exactly the
    product of the two kernel masses, with no extra spacing factor. This pins the
    conv2sepYcirc.m operator the audit verified (separable, unit-volume normpdf
    space kernel, circular feature kernel, no spacing factor).

    NOTE: the feature kernel mass is NOT 1 here — a σ=360 circular normpdf over the
    360°-period θ grid sums to ~0.38, so the uniform-input pool is ~0.38, NOT 1.
    That is the faithful behavior; the test asserts the SEPARABILITY identity
    (pool == s_x.sum()·s_theta.sum()), not a guessed ≈1.

    Citation: C-010 / attentionModel.m conv2sepYcirc(A.*E, s_x, s_theta);
    conv2sepYcirc.m (separable, no spacing factor)
    """
    x_grid = np.arange(-200.0, 201.0, 1.0)
    theta_grid = np.arange(-180.0, 180.0, 1.0)
    s_x, s_theta = model.build_suppressive_kernel(
        x_grid, theta_grid, suppressive_field_size=20.0, suppressive_tuning_width=360.0
    )
    # spatial kernel is unit-volume (normpdf, no spacing factor).
    assert abs(float(s_x.sum()) - 1.0) < 1e-6, "spatial suppressive kernel must be unit-volume"
    AE = np.ones((theta_grid.size, x_grid.size))  # uniform unit input
    S = model.compute_suppressive_drive(s_x, s_theta, A=np.ones_like(AE), E=AE)
    # separability identity: interior pool == sum(s_x)·sum(s_theta), no spacing factor.
    expected = float(s_x.sum()) * float(s_theta.sum())
    interior = S[:, 50:-50]
    assert abs(float(interior.mean()) - expected) < 1e-3, (
        "separable suppressive pool of a uniform unit input must equal "
        f"sum(s_x)·sum(s_theta)={expected:.4f} in the interior; got "
        f"{float(interior.mean()):.4f} (a mismatch implies an extra spacing factor "
        "or a non-separable pool — not the faithful conv2sepYcirc operator)."
    )
