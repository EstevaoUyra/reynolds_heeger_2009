"""Per-panel axis-limit + data-within-limit tests (WORKFLOW.md §3).

Axis limits are a HARD, code-checkable requirement per plot panel. For each
reproduced MODEL panel we assert two things on the *rendered* figure (read off
the Axes objects, drawn from the same record the PNG is):

  (a) the rendered Axes limits (x-range, y-range, right/twin range, scale) EQUAL
      the paper panel's declared limits (article_aware/figures/figure_<N>/
      panel_<X>.md, encoded in views.PAPER_PANEL_LIMITS);
  (b) the plotted data lies WITHIN those limits.

Pinning the axes to the paper's numbers (autoscale OFF in the view) is what
catches magnitude divergence: Figure 4E's percent-attentional-modulation curve
reaches ~310-390 %, far above the paper's (0, 100) right axis, so its
data-within-axis test FAILS BY DESIGN — that RED is the intended, successful
outcome (the check now catches a divergence the old auto-scaling view hid). Do
NOT "fix" the model or widen the axis to green it.

The render functions return ``{"path", "panels": {id: {ax, ax_right, limits, x,
left_curves, right_curve}}}``; these tests read that, never re-deriving limits.
"""

from __future__ import annotations

import numpy as np
import pytest

from neuromodels.framework.testing import deterministic_test
from rh_model import views


# Render each figure ONCE per test session and cache the introspection dicts.
_RENDER = {
    2: views.render_figure_2,
    3: views.render_figure_3,
    4: views.render_figure_4,
    5: views.render_figure_5,
    6: views.render_figure_6,
    7: views.render_figure_7,
}
_PANELS_CACHE: dict[int, dict] = {}


def _panels(fig_n: int, tmp_path_factory) -> dict:
    if fig_n not in _PANELS_CACHE:
        out_dir = tmp_path_factory.mktemp(f"fig{fig_n}_axes")
        _PANELS_CACHE[fig_n] = _RENDER[fig_n](out_dir)["panels"]
    return _PANELS_CACHE[fig_n]


def _panel(fig_n: int, panel_id: str, tmp_path_factory) -> dict:
    return _panels(fig_n, tmp_path_factory)[panel_id]


def _assert_axes_match_paper(panel: dict) -> None:
    """(a) Rendered Axes limits EQUAL the declared paper-panel limits."""
    limits = panel["limits"]
    ax = panel["ax"]
    assert ax.get_xscale() == limits["xscale"]
    assert ax.get_xlim() == pytest.approx(limits["xlim"], rel=1e-9, abs=1e-9)
    assert ax.get_ylim() == pytest.approx(limits["ylim"], rel=1e-9, abs=1e-9)
    if limits["right"] is None:
        assert panel["ax_right"] is None
    else:
        ax_r = panel["ax_right"]
        assert ax_r is not None
        assert ax_r.get_ylim() == pytest.approx(limits["right"], rel=1e-9, abs=1e-9)
        # The twin axis shares the pinned x-range.
        assert ax_r.get_xlim() == pytest.approx(limits["xlim"], rel=1e-9, abs=1e-9)


def _assert_data_within_axes(panel: dict) -> None:
    """(b) Every plotted point lies WITHIN the declared paper-panel limits.

    This is the magnitude check. It FAILS for Fig 4E's modulation curve (the
    intended outcome) because that curve overflows the paper's (0, 100) right
    axis.
    """
    limits = panel["limits"]
    x = panel["x"]
    xlo, xhi = limits["xlim"]
    tol = 1e-6
    assert np.all(x >= xlo - tol) and np.all(x <= xhi + tol), "x data outside paper x-range"

    ylo, yhi = limits["ylim"]
    for curve in panel["left_curves"]:
        c = np.asarray(curve, dtype=float)
        assert np.all(c >= ylo - tol) and np.all(c <= yhi + tol), "left-axis data outside paper y-range"

    if panel["right_curve"] is not None and limits["right"] is not None:
        rlo, rhi = limits["right"]
        r = np.asarray(panel["right_curve"], dtype=float)
        # Allow a tiny tolerance only; a curve reaching ~310% blows past it.
        assert np.all(r >= rlo - tol) and np.all(r <= rhi + tol), (
            "right-axis (Attentional Modulation %) data overflows the paper's "
            "(0, 100) axis"
        )


# --- Figure 2 -------------------------------------------------------------

@deterministic_test(spec_ref="figures.figure_2.panel_A", figure=2, claim_id="AX-2A-limits")
def test_figure_2A_axes_match_paper(tmp_path_factory):
    """Citation: C-013"""
    _assert_axes_match_paper(_panel(2, "2A", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_2.panel_A", figure=2, claim_id="AX-2A-within")
def test_figure_2A_data_within_paper_axis(tmp_path_factory):
    """Citation: C-013"""
    _assert_data_within_axes(_panel(2, "2A", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_2.panel_B", figure=2, claim_id="AX-2B-limits")
def test_figure_2B_axes_match_paper(tmp_path_factory):
    """Citation: C-013"""
    _assert_axes_match_paper(_panel(2, "2B", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_2.panel_B", figure=2, claim_id="AX-2B-within")
def test_figure_2B_data_within_paper_axis(tmp_path_factory):
    """Citation: C-013"""
    _assert_data_within_axes(_panel(2, "2B", tmp_path_factory))


# --- Figure 3 -------------------------------------------------------------

@deterministic_test(spec_ref="figures.figure_3.panel_C", figure=3, claim_id="AX-3C-limits")
def test_figure_3C_axes_match_paper(tmp_path_factory):
    """Citation: C-014"""
    _assert_axes_match_paper(_panel(3, "3C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_3.panel_C", figure=3, claim_id="AX-3C-within")
def test_figure_3C_data_within_paper_axis(tmp_path_factory):
    """Citation: C-014"""
    _assert_data_within_axes(_panel(3, "3C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_3.panel_F", figure=3, claim_id="AX-3F-limits")
def test_figure_3F_axes_match_paper(tmp_path_factory):
    """Citation: C-014"""
    _assert_axes_match_paper(_panel(3, "3F", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_3.panel_F", figure=3, claim_id="AX-3F-within")
def test_figure_3F_data_within_paper_axis(tmp_path_factory):
    """Citation: C-014"""
    _assert_data_within_axes(_panel(3, "3F", tmp_path_factory))


# --- Figure 4 -------------------------------------------------------------

@deterministic_test(spec_ref="figures.figure_4.panel_C", figure=4, claim_id="AX-4C-limits")
def test_figure_4C_axes_match_paper(tmp_path_factory):
    """Citation: C-015"""
    _assert_axes_match_paper(_panel(4, "4C", tmp_path_factory))


@deterministic_test(
    spec_ref="figures.figure_4.panel_C",
    figure=4,
    claim_id="AX-4C-within",
)
def test_figure_4C_data_within_paper_axis(tmp_path_factory):
    """4C's suppression %-modulation stays WITHIN the paper's (0, 100) right axis.

    Under the authors' Figure4C.m protocol (CODE-018, A-012) the %-modulation
    100·(unatt-att)/unatt peaks ~38% (matching the digitized ~36%) and declines —
    well within the pinned (0, 100) axis, so this PASSES. The prior ~101% overflow
    was an artifact of the RETIRED colocated-spatial-flat mis-mapping, not the
    model. Do NOT widen the axis.

    Citation: C-015, C-021
    """
    _assert_data_within_axes(_panel(4, "4C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_4.panel_E", figure=4, claim_id="AX-4E-limits")
def test_figure_4E_axes_match_paper(tmp_path_factory):
    """The 4E Axes are PINNED to the paper's (0, 1) / (0, 100) — this passes.

    Citation: C-015
    """
    _assert_axes_match_paper(_panel(4, "4E", tmp_path_factory))


@deterministic_test(
    spec_ref="figures.figure_4.panel_E",
    figure=4,
    claim_id="AX-4E-within",
    paper_issue="4E modulation magnitude (~310-390%) overflows the paper's "
    "(0, 100) Attentional-Modulation axis — known model divergence (panel_E.md)",
)
def test_figure_4E_modulation_within_paper_axis(tmp_path_factory):
    """INTENDED FAILURE: 4E's modulation curve overflows the paper's (0, 100).

    This RED is the goal of the worked example. The model's percent attentional
    modulation for the covarying-contrast attend-preferred condition reaches
    ~310-390 %, far above the paper's right axis. With the axis pinned to the
    paper's (0, 100) (autoscale OFF), the data-within-axis check fails — exactly
    the magnitude divergence the old auto-scaling view silently hid. Do NOT green
    this by widening the axis or editing the model.

    Citation: C-015
    """
    _assert_data_within_axes(_panel(4, "4E", tmp_path_factory))


# --- Figures 5/6/7 (tuning) ----------------------------------------------

@deterministic_test(spec_ref="figures.figure_5.panel_C", figure=5, claim_id="AX-5C-limits")
def test_figure_5C_axes_match_paper(tmp_path_factory):
    """Citation: C-016"""
    _assert_axes_match_paper(_panel(5, "5C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_5.panel_C", figure=5, claim_id="AX-5C-within")
def test_figure_5C_data_within_paper_axis(tmp_path_factory):
    """Citation: C-016"""
    _assert_data_within_axes(_panel(5, "5C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_6.panel_C", figure=6, claim_id="AX-6C-limits")
def test_figure_6C_axes_match_paper(tmp_path_factory):
    """Citation: C-017"""
    _assert_axes_match_paper(_panel(6, "6C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_6.panel_C", figure=6, claim_id="AX-6C-within")
def test_figure_6C_data_within_paper_axis(tmp_path_factory):
    """Citation: C-017"""
    _assert_data_within_axes(_panel(6, "6C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_7.panel_C", figure=7, claim_id="AX-7C-limits")
def test_figure_7C_axes_match_paper(tmp_path_factory):
    """Citation: C-018"""
    _assert_axes_match_paper(_panel(7, "7C", tmp_path_factory))


@deterministic_test(spec_ref="figures.figure_7.panel_C", figure=7, claim_id="AX-7C-within")
def test_figure_7C_data_within_paper_axis(tmp_path_factory):
    """Citation: C-018"""
    _assert_data_within_axes(_panel(7, "7C", tmp_path_factory))
