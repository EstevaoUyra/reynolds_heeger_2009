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

def norm_pair(attended: np.ndarray, unattended: np.ndarray):
    """Normalize a CRF pair to the larger plotted peak (== views._normalized_pair)."""
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
    digitized JSON lives in: left-axis main curves normalized to [0, 1] by the
    shared plotted peak (``norm_pair`` / ``norm_curves``); the right-axis
    ``percent_modulation`` curve as the model percent. Keys match the digitized
    curve names so ``shape_deviation`` can pair them up.
    """
    from rh_model import protocols  # local: keep helper import light

    key = (figure, panel)
    if key == (2, "A"):
        r = protocols.run_figure_2A(n_contrasts=24)
        att, una = norm_pair(r["attended_CRF"], r["unattended_CRF"])
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (2, "B"):
        r = protocols.run_figure_2B(n_contrasts=24)
        att, una = norm_pair(r["attended_CRF"], r["unattended_CRF"])
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (3, "C"):
        r = protocols.run_figure_3C(n_contrasts=24)
        att, una = norm_pair(r["attended_CRF"], r["unattended_CRF"])
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (3, "F"):
        r = protocols.run_figure_3F(n_contrasts=24)
        att, una = norm_pair(r["attended_CRF"], r["unattended_CRF"])
        return (np.asarray(r["c"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (4, "C"):
        r = protocols.run_figure_4C(n_contrasts=24)
        att, una = norm_pair(r["attended_CRF"], r["unattended_CRF"])
        return (np.asarray(r["c_pref"], float), True, {
            "attended": att, "unattended": una,
            "percent_modulation": np.abs(np.asarray(r["percent_modulation"], float))})
    if key == (4, "E"):
        r = protocols.run_figure_4E(n_contrasts=24)
        pref, nonpref = norm_pair(r["attend_pref_CRF"], r["attend_nonpref_CRF"])
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
