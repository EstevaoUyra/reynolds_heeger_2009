"""Three-tier figure-test helpers (WORKFLOW.md §3b).

Each figure panel that shows curves is checked by comparing the IMPLEMENTATION's
measurement record against the PAPER-DIGITIZED reference, both placed in the
panel's pinned display frame (left axis normalized 0-1; right axis percent),
exactly the frame the Phase-A-owned view renders.

Three tiers, declared per-test via ``tier``:

  - ``qualitative`` — MUST PASS. Precise-but-weak structural claims (orderings,
    crossings, convergence/separation). A faithful figure always satisfies them.
  - ``hard``        — MUST PASS. A few strong quantitative claims the agent is
    confident about (e.g. a peak ratio within a tolerance of the digitized value).
  - ``soft``        — MEASURED, REPORTED, NEVER BLOCKS. Other quantitative claims;
    the digitization is not trusted to the last percent, so these surface to a
    human who promotes them to ``hard`` (a one-line tier flip) if warranted.

``tier_test(tier=..., ...)`` wraps ``deterministic_test`` and additionally marks
soft tests with ``pytest.mark.soft`` so the runner can record-but-not-block them
(see conftest.py: soft failures are reported as xfail-style "soft-fail", never a
build failure). qualitative + hard gate the build.

The EXPECTED values come from the digitized JSON; the MEASURED values come from
the implementation record. Because the model is unchanged and known to diverge,
several qualitative/hard tests are EXPECTED TO FAIL — that red is the success
criterion of this worked example, not a defect to paper over.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path

import numpy as np
import pytest

from neuromodels.framework.testing import deterministic_test

_FIGURES_ROOT = Path(__file__).resolve().parents[1] / "figures"

VALID_TIERS = ("qualitative", "hard", "soft")


def tier_test(*, tier: str, spec_ref: str, claim_id: str, figure, paper_issue=None):
    """Decorate a tiered figure test.

    ``tier`` is a declared, human-editable per-test attribute (promote soft→hard
    in one line). qualitative/hard gate; soft is recorded but never blocks.
    """
    if tier not in VALID_TIERS:
        raise ValueError(f"tier must be one of {VALID_TIERS}, got {tier!r}")

    def decorate(func):
        func = deterministic_test(
            spec_ref=spec_ref, claim_id=claim_id, figure=figure, paper_issue=paper_issue
        )(func)
        func = pytest.mark.tier(tier)(func)
        if tier == "soft":
            func = pytest.mark.soft(func)
        func.__tier__ = tier
        return func

    return decorate


# --- digitized-reference loading ------------------------------------------

@functools.lru_cache(maxsize=None)
def load_digitized(figure: int, panel: str) -> dict:
    path = _FIGURES_ROOT / f"figure_{figure}" / f"panel_{panel}_digitized.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def ref_curve(figure: int, panel: str, name: str) -> tuple[np.ndarray, np.ndarray]:
    """Return (x, y) digitized points for one reference curve."""
    pts = np.asarray(load_digitized(figure, panel)["curves"][name]["points"], dtype=float)
    return pts[:, 0], pts[:, 1]


def ref_value_at(figure: int, panel: str, name: str, x: float, *, log_x: bool) -> float:
    """Digitized reference y at x (interp on log-x if requested)."""
    xs, ys = ref_curve(figure, panel, name)
    if log_x:
        return float(np.interp(np.log(x), np.log(xs), ys))
    return float(np.interp(x, xs, ys))


def ref_peak(figure: int, panel: str, name: str) -> float:
    _, ys = ref_curve(figure, panel, name)
    return float(ys.max())


# --- implementation-record normalization (matches the view) ---------------

# --- SHARED-SCALE normalization convention (binding contract) -------------
# The paper renders each CRF figure-GROUP (e.g. Fig 2's 2A + 2B) on ONE shared
# response axis: 2A's plateau (~0.615) and 2B's attended plateau (~0.85) sit on
# the SAME sub-1.0 scale, and that height difference IS the response-gain claim.
# The digitized references encode this shared sub-1.0 scale directly.
#
# Therefore CRF model curves must be placed on a SINGLE common scale across all
# panels in the group — NOT per-pair-renormalized to 1.0 (which pins every panel's
# top curve to 1.0 and erases the cross-panel ceiling difference). The common
# scale is chosen so the model group's overall peak maps onto the reference
# group's overall peak, i.e. the digitized shared-scale values are the target.

# Figure-group membership: every CRF panel that shares one response axis with its
# siblings. Keyed by group name -> the (figure, panel) members rendered together.
CRF_FIGURE_GROUPS = {
    "figure_2": [(2, "A"), (2, "B")],
    "figure_3": [(3, "C"), (3, "F")],
    "figure_4": [(4, "C"), (4, "E")],
}


def group_of(figure: int, panel: str) -> str | None:
    """Return the CRF figure-group name a panel belongs to, or None."""
    for name, members in CRF_FIGURE_GROUPS.items():
        if (figure, panel) in members:
            return name
    return None


def _reference_group_peak(figure: int, panel: str) -> float:
    """Max digitized left-axis (response) value across ALL panels in the group.

    This is the reference's shared-scale ceiling; the model group is scaled so
    its overall peak lands here, preserving cross-panel ceiling differences.
    """
    members = CRF_FIGURE_GROUPS[group_of(figure, panel)]
    peak = 0.0
    for fig, pan in members:
        dig = load_digitized(fig, pan)
        for cname, cdata in dig["curves"].items():
            if cdata.get("axis") == "right":
                continue  # right axis is percent, not the response scale
            ys = np.asarray(cdata["points"], dtype=float)[:, 1]
            peak = max(peak, float(ys.max()))
    return peak if peak > 1e-12 else 1.0


def _model_group_peak(figure: int, panel: str) -> float:
    """Max RAW model response across ALL panels in the same CRF group.

    Computed from the same protocol records the tier tests measure, so every
    panel in the group is divided by ONE common model scale.
    """
    from rh_model import protocols  # local import: keep helper import light

    members = CRF_FIGURE_GROUPS[group_of(figure, panel)]
    runners = {
        (2, "A"): lambda: protocols.run_figure_2A(n_contrasts=24),
        (2, "B"): lambda: protocols.run_figure_2B(n_contrasts=24),
        (3, "C"): lambda: protocols.run_figure_3C(n_contrasts=24),
        (3, "F"): lambda: protocols.run_figure_3F(n_contrasts=24),
        (4, "C"): lambda: protocols.run_figure_4C(n_contrasts=24),
        (4, "E"): lambda: protocols.run_figure_4E(n_contrasts=24),
    }
    pair_keys = {
        (4, "E"): ("attend_pref_CRF", "attend_nonpref_CRF"),
    }
    peak = 0.0
    for fig, pan in members:
        r = runners[(fig, pan)]()
        a_key, b_key = pair_keys.get((fig, pan), ("attended_CRF", "unattended_CRF"))
        peak = max(peak, float(np.max(r[a_key])), float(np.max(r[b_key])))
    return peak if peak > 1e-12 else 1.0


@functools.lru_cache(maxsize=None)
def group_scale(figure: int, panel: str) -> float:
    """Common divisor placing a model CRF group onto the reference shared scale.

    model_curve / group_scale lands the model group's overall peak at the
    reference group's overall peak, so each panel's plateau renders at its TRUE
    relative height (2B above 2A), matching the digitized references. This is the
    binding shared-scale convention; ``views`` (Phase B) renders with the same
    rule. Do NOT divide each pair independently by its own max.
    """
    if group_of(figure, panel) is None:
        raise KeyError(f"panel {figure}{panel} is not in a CRF figure-group")
    return _model_group_peak(figure, panel) / _reference_group_peak(figure, panel)


def norm_pair_shared(attended: np.ndarray, unattended: np.ndarray,
                     figure: int, panel: str):
    """Place a CRF pair on the GROUP's shared response scale (binding convention).

    Divides by the single group-wide ``group_scale`` so cross-panel ceiling
    differences survive and the curves land on the digitized shared sub-1.0
    scale. This REPLACES the old per-pair-to-1.0 ``norm_pair`` for the figure
    tests (see Finding 1, improvement-pass-2026-06-03).
    """
    scale = group_scale(figure, panel)
    return (np.asarray(attended, dtype=float) / scale,
            np.asarray(unattended, dtype=float) / scale)


def norm_pair(attended: np.ndarray, unattended: np.ndarray):
    """DEPRECATED per-pair-to-1.0 normalization (the Finding-1 defect).

    Pins each panel's top curve to 1.0, erasing the paper's cross-panel response
    ceiling claim (2B's plateau above 2A's). Retained only for non-CRF callers
    that genuinely want a self-normalized pair; the Fig-2/3/4 CRF tier tests now
    use ``norm_pair_shared`` instead. Do NOT use for CRF figure-group panels.
    """
    attended = np.asarray(attended, dtype=float)
    unattended = np.asarray(unattended, dtype=float)
    scale = float(max(attended.max(), unattended.max(), 1e-12))
    return attended / scale, unattended / scale


def norm_curves(*curves: np.ndarray):
    """Normalize tuning curves by the shared peak (== views._plot_tuning)."""
    arrs = [np.asarray(c, dtype=float) for c in curves]
    peak = float(max(a.max() for a in arrs))
    peak = peak if peak > 1e-12 else 1.0
    return [a / peak for a in arrs]


def value_at_log(contrast: np.ndarray, curve: np.ndarray, target: float) -> float:
    return float(np.interp(np.log(target), np.log(np.asarray(contrast, dtype=float)),
                           np.asarray(curve, dtype=float)))


def value_at(grid: np.ndarray, curve: np.ndarray, target: float) -> float:
    return float(np.interp(target, np.asarray(grid, dtype=float),
                           np.asarray(curve, dtype=float)))


# --- dozen-point SHAPE check (WORKFLOW §3b) --------------------------------
# The digitized ~dozen points are the SHAPE backbone, not just a source for a
# few hand-picked scalars. ``panel_model_curves`` renders the implementation
# record into the same display frame the Phase-A view plots and the digitized
# reference lives in, keyed by the digitized curve names; ``shape_deviation``
# then measures how far the model curve strays from each digitized point. This
# is generated MECHANICALLY for every curve of every panel (not agent-chosen),
# so a curve-SHAPE divergence cannot slip through the way endpoint scalars do.

# Every (figure, panel) that carries a digitized reference curve.
ALL_PANELS = (
    (2, "A"), (2, "B"), (3, "C"), (3, "F"), (4, "C"), (4, "E"),
    (5, "C"), (6, "C"), (7, "C"),
)


@functools.lru_cache(maxsize=None)
def panel_model_curves(figure: int, panel: str):
    """Return ``(x_model, log_x, {digitized_curve_name: y_model})`` for one panel.

    The model curves are placed in EXACTLY the frame the view renders and the
    digitized JSON lives in: CRF figure-group panels (2A/2B, 3C/3F, 4C/4E) are
    placed on the GROUP's shared response scale (``norm_pair_shared`` — Finding
    1), so cross-panel ceiling differences survive; tuning panels use the
    shared-peak-within-panel ``norm_curves``; the right-axis ``percent_modulation``
    curve is the model percent. Keys match the digitized curve names so
    ``shape_deviation`` can pair them up.
    """
    from rh_model import protocols  # local: keep helper import light

    key = (figure, panel)
    if key == (2, "A"):
        r = protocols.run_figure_2A(n_contrasts=24)
        att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 2, "A")
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (2, "B"):
        r = protocols.run_figure_2B(n_contrasts=24)
        att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 2, "B")
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (3, "C"):
        r = protocols.run_figure_3C(n_contrasts=24)
        att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 3, "C")
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (3, "F"):
        r = protocols.run_figure_3F(n_contrasts=24)
        att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 3, "F")
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (4, "C"):
        r = protocols.run_figure_4C(n_contrasts=24)
        att, una = norm_pair_shared(r["attended_CRF"], r["unattended_CRF"], 4, "C")
        return (np.asarray(r["c_pref"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (4, "E"):
        r = protocols.run_figure_4E(n_contrasts=24)
        pref, nonpref = norm_pair_shared(
            r["attend_pref_CRF"], r["attend_nonpref_CRF"], 4, "E")
        return (np.asarray(r["c"], float), True, {
            "attend_pref": pref, "attend_nonpref": nonpref,
            "percent_modulation": np.abs((np.asarray(r["ratio"], float) - 1.0) * 100.0)})
    if key == (5, "C"):
        r = protocols.run_figure_5C(n_orientations=37)
        att, una = norm_curves(r["attended_tuning"], r["unattended_tuning"])
        return (np.asarray(r["theta_0_grid"], float), False, {
            "attended": att, "unattended": una})
    if key == (6, "C"):
        r = protocols.run_figure_6C(n_directions=49)
        contra, fix = norm_curves(
            r["attend_opposite_stimulus_tuning"], r["attend_fixation_tuning"])
        return (np.asarray(r["theta_stim_grid"], float), False, {
            "attend_contralateral": contra, "attend_fixation": fix})
    if key == (7, "C"):
        r = protocols.run_figure_7C(n_directions=49)
        var, fix, nonpref = norm_curves(
            r["attend_variable_tuning"], r["fixation_tuning"], r["attend_nonpref_tuning"])
        return (np.asarray(r["theta_var_grid"], float), False, {
            "attend_variable": var, "fixation": fix, "attend_nonpref": nonpref})
    raise KeyError(f"no model-curve adapter for panel {figure}{panel}")


def shape_deviation(figure: int, panel: str, curve: str):
    """Max/mean abs deviation of the model curve from the digitized dozen points.

    Returns ``(max_abs, mean_abs, x_at_max)`` in the curve's own frame (left =
    normalized 0-1, right = percent). The model is interpolated onto each
    digitized x (on log-x where the panel is log-scaled), so this measures shape
    across the whole range, not just the endpoints.
    """
    x_model, log_x, curves = panel_model_curves(figure, panel)
    y_model = np.asarray(curves[curve], float)
    pts = np.asarray(load_digitized(figure, panel)["curves"][curve]["points"], float)
    rx, ry = pts[:, 0], pts[:, 1]
    if log_x:
        my = np.interp(np.log(rx), np.log(x_model), y_model)
    else:
        my = np.interp(rx, x_model, y_model)
    dev = np.abs(my - ry)
    return float(dev.max()), float(dev.mean()), float(rx[int(dev.argmax())])
