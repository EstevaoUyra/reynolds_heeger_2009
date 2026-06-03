"""Phase-A (article-aware) declarative figure view — the presentation contract.

ARCHITECTURE.md §2: the view renders panels-as-data. It is **Phase-A-owned**
because it declares the per-panel presentation contract that BOTH sides must
honour: the digitized paper reference AND the implementation's measurement
record are drawn through the SAME pinned axes / scale / normalization, so a
passing deterministic test and the rendered figure read the same numbers and
cannot disagree. Pinning the presentation here (and only here) is what lets the
faithfulness gate catch magnitude divergence (e.g. Fig 4E overflow).

This module is a **pure view**: it imports NOTHING from the model
(``model.py`` / ``protocols.py`` / ``measurements.py``). It consumes a plain
*measurement record* (a dict of arrays produced elsewhere) plus the
Phase-A-owned digitized references under ``article_aware/figures/…``. The model
RUN that produces records lives in ``implementation/`` and calls into these
renderers; see ``rh_model.views`` for the model-side runner that wires records
to this view and preserves the ``python -m rh_model.views`` entry point.

(Migrated from ``implementation/src/rh_model/views.py`` so Phase A owns the
presentation contract unambiguously — behavior-preserving relocation +
record/run decoupling, chore/view-to-article-aware.)
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np


# Phase-A digitized references (WORKFLOW.md §3b). The view is Phase-A-owned and
# renders EITHER the implementation's measurement record OR the paper-digitized
# reference through the SAME pinned axes. The digitized JSONs live under
# article_aware/figures/figure_<N>/panel_<X>_digitized.json — this module sits
# in article_aware/, so they are one directory below it.
ARTICLE_AWARE_FIGURES = Path(__file__).resolve().parent / "figures"


COLORS = {
    "attended": "#2f6fbb",
    "unattended": "#555555",
    "suppressed": "#b33f3f",
    "accent": "#2a9d8f",
    "third": "#7a5195",
}


# ---------------------------------------------------------------------------
# Paper-panel axis limits (WORKFLOW.md §3: axis limits are a HARD, code-checkable
# requirement per plot panel). Each entry is read OFF THE PAPER FIGURE IMAGE and
# mirrored in article_aware/figures/figure_<N>/panel_<X>.md. The view sets these
# limits EXPLICITLY (never autoscale); the deterministic axis tests assert the
# rendered Axes limits equal these, and that the plotted data lies within them.
#
# `right` is the twin (attentional-modulation) axis; `None` means no twin axis.
# These are the paper's numbers — they are deliberately NOT widened to fit the
# model's curves. Fig 4E's modulation magnitude overflows (0, 100): that overflow
# is the intended deterministic FAILURE (see panel_E.md).
# ---------------------------------------------------------------------------
PAPER_PANEL_LIMITS: dict[str, dict] = {
    # Figure 2 — model CRF panels (Normalized Model Response / Attentional Mod %).
    "2A": {"xlim": (0.01, 1.0), "xscale": "log", "ylim": (0.0, 1.0), "right": (0.0, 100.0)},
    "2B": {"xlim": (0.01, 1.0), "xscale": "log", "ylim": (0.0, 1.0), "right": (0.0, 100.0)},
    # Figure 3 — model CRF panels.
    "3C": {"xlim": (0.01, 1.0), "xscale": "log", "ylim": (0.0, 1.0), "right": (0.0, 100.0)},
    "3F": {"xlim": (0.01, 1.0), "xscale": "log", "ylim": (0.0, 1.0), "right": (0.0, 100.0)},
    # Figure 4 — model CRF panels. 4E's right axis is the paper's (0, 100); the
    # model's modulation curve overflows it (intended failure).
    "4C": {"xlim": (0.01, 1.0), "xscale": "log", "ylim": (0.0, 1.0), "right": (0.0, 100.0)},
    "4E": {"xlim": (0.01, 1.0), "xscale": "log", "ylim": (0.0, 1.0), "right": (0.0, 100.0)},
    # Figure 5/6/7 — model tuning panels (Normalized Response, no twin axis).
    "5C": {"xlim": (-90.0, 90.0), "xscale": "linear", "ylim": (0.0, 1.0), "right": None},
    "6C": {"xlim": (-180.0, 175.0), "xscale": "linear", "ylim": (0.0, 1.0), "right": None},
    "7C": {"xlim": (-180.0, 175.0), "xscale": "linear", "ylim": (0.0, 1.0), "right": None},
}


def paper_panel_limits(panel_id: str) -> dict:
    """Return the declared paper-panel axis limits for a model panel id.

    The single source of the per-panel axis numbers the view pins and the
    deterministic axis tests assert against (WORKFLOW.md §3).
    """
    return PAPER_PANEL_LIMITS[panel_id]


# ---------------------------------------------------------------------------
# Digitized-reference loading (WORKFLOW.md §3b). A digitized JSON stores, per
# curve, ~a dozen [x, y] points read off the paper panel in the panel's pinned
# frame (left axis normalized 0-1; right axis 0-100). We resample those points
# onto a dense grid in the panel's pinned x-range so the reference renders as a
# smooth curve through the SAME view helpers the implementation record uses.
# ---------------------------------------------------------------------------

def load_digitized(figure: int, panel: str) -> dict:
    """Load the digitized reference JSON for figure_<N>/panel_<X>."""
    path = ARTICLE_AWARE_FIGURES / f"figure_{figure}" / f"panel_{panel}_digitized.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _resample_curve(points: list, x_grid: np.ndarray, *, log_x: bool) -> np.ndarray:
    """Interpolate digitized [x, y] points onto ``x_grid`` (log-x if requested)."""
    pts = np.asarray(points, dtype=float)
    xs, ys = pts[:, 0], pts[:, 1]
    if log_x:
        return np.interp(np.log(x_grid), np.log(xs), ys)
    return np.interp(x_grid, xs, ys)


def _digitized_x_grid(dig: dict, n: int = 64) -> np.ndarray:
    lo, hi = dig["x_range"]
    if dig.get("x_scale") == "log":
        return np.logspace(np.log10(lo), np.log10(hi), n)
    return np.linspace(lo, hi, n)


def _pyplot():
    """Import pyplot with a noninteractive backend.

    Assumption: figure reproduction is a local artifact-generation step and
    may run in headless CI or agent sessions.
    """
    mpl_config_dir = Path(tempfile.gettempdir()) / "rh_model_matplotlib"
    mpl_config_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(mpl_config_dir))
    try:
        import matplotlib

        matplotlib.use("Agg", force=True)
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on optional deps.
        raise RuntimeError(
            "Matplotlib is required to render figures. Install with "
            '`pip install -e ".[sanity]"` from the repository root.'
        ) from exc
    return plt


def _output_dir(output_dir: str | Path | None) -> Path:
    """Create and return the target directory for rendered PNGs.

    Assumption: model-generated figures are regenerated artifacts; the caller
    (the model-side runner) supplies the destination directory.
    """
    if output_dir is None:
        raise ValueError("output_dir is required: the pure view does not own a default location")
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save(fig, path: Path) -> Path:
    """Save one matplotlib figure as a PNG.

    Assumption: PNG output is the human-review format requested for visual
    reproduction.
    """
    fig.savefig(path, dpi=180, bbox_inches="tight")
    _pyplot().close(fig)
    return path


def _finish_axes(ax, *, xlabel: str, ylabel: str, title: str | None = None) -> None:
    """Apply shared axis labels and quiet plotting style.

    Assumption: styling need not match the article exactly, but should preserve
    plot type, axes, and condition comparisons.
    """
    if title:
        ax.set_title(title, fontsize=10)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color="#dddddd", linewidth=0.6, alpha=0.8)


# ---------------------------------------------------------------------------
# Shared-scale CRF normalization (model_spec.yaml rendering_conventions.
# crf_shared_response_scale; Finding 1, phaseA-contract-update-2026-06-03).
#
# Each CRF figure-GROUP (2A/2B, 3C/3F, 4C/4E) renders on ONE shared response
# axis: every panel in the group is divided by a SINGLE common scale so the
# cross-panel ceiling difference (e.g. 2B's attended plateau above 2A's)
# survives instead of being pinned to 1.0 per pair. The common scale maps the
# model group's overall peak onto the reference group's overall peak, so the
# model curves land on the digitized shared sub-1.0 scale. This mirrors
# article_aware/extracted_data/rh_tier_helpers.group_scale exactly.
#
# The view owns the REFERENCE half of that ratio (it loads the digitized JSONs
# that pin the shared scale). The MODEL half — the raw model group peak — is a
# property of a model RUN, so it is supplied by the model-side runner that
# produces the records (``rh_model.views``); the view never runs the model. The
# digitized-reference render is ALREADY on the shared scale, so it is plotted
# unscaled (``normalize=False``) — it is NOT passed through a per-pair
# normalizer. Tuning panels (5C/6C/7C) are excluded (they keep _plot_tuning's
# shared-peak-within-panel normalization).
# ---------------------------------------------------------------------------

# (figure, panel) members of each CRF group; keyed by panel_id "2A","2B",...
_CRF_GROUPS = {
    "figure_2": ((2, "A"), (2, "B")),
    "figure_3": ((3, "C"), (3, "F")),
    "figure_4": ((4, "C"), (4, "E")),
}


def _panel_id_to_key(panel_id: str) -> tuple[int, str]:
    return int(panel_id[:-1]), panel_id[-1]


def crf_group_members(panel_id: str):
    """The (figure, panel) members of ``panel_id``'s CRF group, or ``None``."""
    fig, pan = _panel_id_to_key(panel_id)
    for members in _CRF_GROUPS.values():
        if (fig, pan) in members:
            return members
    return None


def reference_group_peak(panel_id: str) -> float:
    """Max digitized left-axis (response) value across every panel in a group.

    The reference's shared-scale ceiling. The view owns this because it owns the
    digitized references. (== rh_tier_helpers._reference_group_peak.)
    """
    members = crf_group_members(panel_id)
    if members is None:
        raise KeyError(f"panel {panel_id} is not in a CRF figure-group")
    peak = 0.0
    for fig, pan in members:
        dig = load_digitized(fig, pan)
        for cdata in dig["curves"].values():
            if cdata.get("axis") == "right":
                continue  # right axis is percent, not the response scale
            ys = np.asarray(cdata["points"], dtype=float)[:, 1]
            peak = max(peak, float(ys.max()))
    return peak if peak > 1e-12 else 1.0


def crf_group_scale(panel_id: str, model_group_peak: float) -> float:
    """Common divisor placing a model CRF group onto the reference shared scale.

    ``model_curve / scale`` lands the model group's overall peak
    (``model_group_peak``, a property of the model RUN, supplied by the runner)
    at the reference group's overall peak, so every panel's plateau renders at
    its TRUE relative height. == ``rh_tier_helpers.group_scale``.
    """
    return float(model_group_peak) / reference_group_peak(panel_id)


def _plot_crf(
    ax,
    x: np.ndarray,
    attended: np.ndarray,
    unattended: np.ndarray,
    *,
    attended_label: str = "attended",
    unattended_label: str = "unattended",
    title: str,
    xlabel: str = "contrast",
) -> None:
    """Plot attended and unattended contrast-response functions.

    Citation: C-013, C-014, C-015
    """
    ax.semilogx(
        x,
        unattended,
        color=COLORS["unattended"],
        marker="o",
        linewidth=1.7,
        label=unattended_label,
    )
    ax.semilogx(
        x,
        attended,
        color=COLORS["attended"],
        marker="o",
        linewidth=1.9,
        label=attended_label,
    )
    _finish_axes(ax, xlabel=xlabel, ylabel="response", title=title)
    ax.legend(frameon=False, fontsize=8)


def _plot_normalized_crf_with_modulation(
    ax,
    panel_id: str,
    x: np.ndarray,
    attended: np.ndarray,
    unattended: np.ndarray,
    percent_modulation: np.ndarray,
    *,
    title: str,
    xlabel: str = "Log Contrast",
    attended_label: str = "attended",
    unattended_label: str = "ignored / unattended",
    group_scale: float | None = None,
) -> dict:
    """Plot a paper-style normalized CRF panel with dashed modulation on a twin axis.

    The paper's model panels (Figs 2/3/4C/4E) overlay a dashed
    percent-attentional-modulation curve on a right twin axis labelled
    "Attentional Modulation (%)". This helper reproduces that twin-axis layout
    and PINS every axis limit to the paper panel's declared values
    (``PAPER_PANEL_LIMITS[panel_id]``) — autoscale is OFF on both axes.

    Left-axis normalization (rendering_conventions.crf_shared_response_scale):
    when ``group_scale`` is given (the model render) the attended/unattended
    pair is divided by that single group-wide scale so the cross-panel ceiling
    difference (e.g. 2B above 2A) survives. When ``group_scale`` is None (the
    digitized-reference render) the curves are already on the shared scale and
    are plotted unscaled.

    The percent_modulation argument is the raw (un-normalized) signed
    modulation curve from the record; the dashed curve is drawn as a
    *magnitude* (absolute percent) so a suppressive panel reads on the same
    positive axis as a facilitatory one. Crucially the right axis is NOT widened
    to fit the curve: for Fig 4E the magnitude exceeds the paper's 100% top, so
    the curve overflows — the intended deterministic failure (panel_E.md).

    Returns an introspection dict (Axes + plotted arrays + declared limits) so a
    deterministic test can assert rendered limits and data-within-limits without
    re-rendering.

    Citation: C-013, C-014, C-015, C-019, C-020
    """
    limits = paper_panel_limits(panel_id)
    percent_modulation = np.abs(np.asarray(percent_modulation, dtype=float))
    if group_scale is not None:
        # Model render: place the pair on its CRF figure-group's shared scale.
        attended_norm = np.asarray(attended, dtype=float) / group_scale
        unattended_norm = np.asarray(unattended, dtype=float) / group_scale
    else:
        # Reference render: digitized curves are ALREADY on the shared scale.
        attended_norm = np.asarray(attended, dtype=float)
        unattended_norm = np.asarray(unattended, dtype=float)
    ax.plot(
        x, unattended_norm, color=COLORS["unattended"], linewidth=1.9,
        label=unattended_label,
    )
    ax.plot(
        x, attended_norm, color=COLORS["attended"], linewidth=2.1,
        label=attended_label,
    )
    _finish_axes(ax, xlabel=xlabel, ylabel="Normalized Model Response", title=title)
    # PIN the paper panel's limits explicitly; autoscale OFF.
    ax.set_xscale(limits["xscale"])
    ax.set_xlim(*limits["xlim"])
    ax.set_ylim(*limits["ylim"])
    ax.set_autoscale_on(False)

    ax_mod = ax.twinx()
    ax_mod.plot(
        x, percent_modulation, color="#222222", linestyle=(0, (4, 3)),
        linewidth=1.7, label="% attentional modulation",
    )
    ax_mod.set_ylabel("Attentional Modulation (%)")
    ax_mod.set_xscale(limits["xscale"])
    ax_mod.set_xlim(*limits["xlim"])
    ax_mod.set_ylim(*limits["right"])  # paper's (0, 100) — NOT widened to fit.
    ax_mod.set_autoscale_on(False)
    ax_mod.spines["top"].set_visible(False)
    ax_mod.grid(False)

    lines, labels = ax.get_legend_handles_labels()
    mod_lines, mod_labels = ax_mod.get_legend_handles_labels()
    ax.legend(lines + mod_lines, labels + mod_labels, frameon=False, fontsize=7, loc="lower right")

    return {
        "panel_id": panel_id,
        "ax": ax,
        "ax_right": ax_mod,
        "limits": limits,
        "x": np.asarray(x, dtype=float),
        "left_curves": [attended_norm, unattended_norm],
        "right_curve": percent_modulation,
    }


def _plot_tuning(
    ax,
    panel_id: str,
    x: np.ndarray,
    curves: Iterable[tuple[str, np.ndarray, str]],
    *,
    title: str,
    xlabel: str,
) -> dict:
    """Plot one or more tuning curves on the PAPER-PINNED axes for ``panel_id``.

    The paper tuning panels (5C/6C/7C) plot "Normalized Response" with the
    largest curve's peak at 1.0; this helper normalizes every curve by that
    shared peak and PINS x/y to ``PAPER_PANEL_LIMITS[panel_id]`` (autoscale OFF).
    Returns an introspection dict for the deterministic axis test.

    Citation: C-016, C-017, C-018
    """
    limits = paper_panel_limits(panel_id)
    curves = list(curves)
    peak = float(max((np.max(np.asarray(y, dtype=float)) for _, y, _ in curves), default=1.0))
    peak = peak if peak > 1e-12 else 1.0
    normed: list[np.ndarray] = []
    for label, y, color in curves:
        yn = np.asarray(y, dtype=float) / peak
        normed.append(yn)
        ax.plot(x, yn, marker="o", markersize=3, linewidth=1.8, label=label, color=color)
    _finish_axes(ax, xlabel=xlabel, ylabel="Normalized Response", title=title)
    ax.set_xscale(limits["xscale"])
    ax.set_xlim(*limits["xlim"])
    ax.set_ylim(*limits["ylim"])
    ax.set_autoscale_on(False)
    ax.legend(frameon=False, fontsize=8)
    return {
        "panel_id": panel_id,
        "ax": ax,
        "ax_right": None,
        "limits": limits,
        "x": np.asarray(x, dtype=float),
        "left_curves": normed,
        "right_curve": None,
    }


def _draw_not_reproduced(ax, label: str = "not reproduced") -> None:
    """Render an explicit empty placeholder panel for a paper panel we do not
    reproduce (config / empirical-data / legend), preserving the paper's layout.

    WORKFLOW.md §3: the reassembled figure must line up with the paper's, with an
    explicit ``not reproduced`` cell wherever the paper had a panel we omit —
    omissions visible and honest, never a clean panel masquerading as the figure.
    """
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color("#bbbbbb")
        spine.set_linestyle((0, (3, 3)))
    ax.set_facecolor("#f6f6f6")
    ax.text(
        0.5, 0.5, label, ha="center", va="center", fontsize=9,
        color="#888888", style="italic", transform=ax.transAxes,
    )


def _draw_stimulus_schematic(ax) -> None:
    """Draw the Figure 1 two-grating stimulus cartoon.

    Citation: C-012
    """
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.85, 0.85)
    ax.set_aspect("equal")
    ax.set_facecolor("white")
    ax.axis("off")

    stripe_x = np.linspace(0.0, 2.0 * np.pi * 5.0, 120)
    grating = 0.35 + 0.55 * (np.sin(stripe_x)[np.newaxis, :] > 0.0)
    grating = np.repeat(grating, 120, axis=0)
    for center in (-0.55, 0.55):
        ax.imshow(
            grating,
            extent=(center - 0.28, center + 0.28, -0.28, 0.28),
            cmap="gray",
            vmin=0.0,
            vmax=1.0,
            origin="lower",
            zorder=1,
        )

    plt = _pyplot()
    solid_rf = plt.Circle((0.55, 0.0), 0.34, fill=False, color="#222222", linewidth=1.8)
    attention = plt.Circle(
        (0.55, 0.0),
        0.43,
        fill=False,
        color="#b33f3f",
        linewidth=1.7,
        linestyle=(0, (4, 3)),
    )
    ax.add_patch(solid_rf)
    ax.add_patch(attention)
    ax.plot(0.0, 0.0, "o", color="black", markersize=4.5, zorder=3)
    ax.set_title("Stimulus", fontsize=10)


def _show_population_image(
    ax,
    field: np.ndarray,
    x_grid: np.ndarray,
    *,
    title: str,
    cmap: str,
    vmin: float,
    vmax: float | None = None,
) -> None:
    """Render one RF-center by feature-preference population panel.

    Citation: C-012
    """
    extent = [float(x_grid[0]), float(x_grid[-1]), -180.0, 175.0]
    ax.imshow(
        field,
        origin="lower",
        aspect="auto",
        extent=extent,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
    )
    ax.set_title(title, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def render_figure_1(record: dict, output_dir: str | Path | None = None) -> dict:
    """Render Figure 1-style population fields and theta=0 slices from a record.

    ``record`` is the Figure-1 measurement record (``figure_1_record``):
    population fields ``E/A/S/R`` and the ``x_grid``.

    Citation: C-012
    """
    plt = _pyplot()
    path = _output_dir(output_dir) / "figure_1.png"

    x_grid = record["x_grid"]
    fig = plt.figure(figsize=(14.0, 4.4), constrained_layout=True)
    grid = fig.add_gridspec(
        1,
        8,
        width_ratios=[1.15, 1.0, 0.16, 1.0, 0.55, 1.0, 0.16, 1.0],
    )
    ax_stim = fig.add_subplot(grid[0, 0])
    ax_e = fig.add_subplot(grid[0, 1])
    ax_mul = fig.add_subplot(grid[0, 2])
    ax_a = fig.add_subplot(grid[0, 3])
    ax_pool = fig.add_subplot(grid[0, 4])
    ax_s = fig.add_subplot(grid[0, 5])
    ax_div = fig.add_subplot(grid[0, 6])
    ax_r = fig.add_subplot(grid[0, 7])

    _draw_stimulus_schematic(ax_stim)
    _show_population_image(
        ax_e,
        record["E"],
        x_grid,
        title="Stimulus drive",
        cmap="magma",
        vmin=0.0,
    )
    _show_population_image(
        ax_a,
        record["A"],
        x_grid,
        title="Attention field",
        cmap="gray",
        vmin=0.0,
        vmax=2.0,
    )
    _show_population_image(
        ax_s,
        record["S"],
        x_grid,
        title="Suppressive drive",
        cmap="magma",
        vmin=0.0,
    )
    _show_population_image(
        ax_r,
        record["R"],
        x_grid,
        title="Output firing rate",
        cmap="magma",
        vmin=0.0,
    )

    for ax in (ax_mul, ax_pool, ax_div):
        ax.axis("off")
    ax_mul.text(0.5, 0.5, "×", ha="center", va="center", fontsize=24)
    ax_div.text(0.5, 0.5, "÷", ha="center", va="center", fontsize=24)
    ax_pool.text(
        0.5,
        0.62,
        "pool over\nspace and orientation",
        ha="center",
        va="center",
        fontsize=8,
        transform=ax_pool.transAxes,
    )
    ax_pool.annotate(
        "",
        xy=(0.90, 0.42),
        xytext=(0.10, 0.42),
        xycoords=ax_pool.transAxes,
        arrowprops={"arrowstyle": "->", "linewidth": 1.0, "color": "#333333"},
    )

    fig.suptitle("Normalization model of attention", fontsize=12)
    return {"path": _save(fig, path), "panels": {}}


def render_figure_2(records: dict, group_scale: float,
                    output_dir: str | Path | None = None) -> dict:
    """Render the FULL Figure-2 paper grid from records; per-panel introspection.

    ``records`` maps panel id -> measurement record: ``{"2A": rec, "2B": rec}``
    (``crf_pair_record`` outputs). ``group_scale`` is the single shared-scale
    divisor for the figure-2 CRF group (model group peak / reference group peak).

    Layout (article_aware/figures/figure_2_layout.yaml): top row = two model CRF
    panels [2A | 2B], bottom row = the paper's legend rendered as a single
    ``not reproduced`` placeholder spanning both columns.

    Returns ``{"path": Path, "panels": {panel_id: introspection_dict}}`` so the
    deterministic axis tests can read the rendered Axes limits and plotted data
    from the same render the PNG was made from.

    Citation: C-013
    """
    plt = _pyplot()
    fig = plt.figure(figsize=(10.2, 6.0), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.18])
    path = _output_dir(output_dir) / "figure_2.png"

    panels: dict[str, dict] = {}

    fig2a = records["2A"]
    panels["2A"] = _plot_normalized_crf_with_modulation(
        fig.add_subplot(grid[0, 0]), "2A",
        fig2a["c"], fig2a["attended_CRF"], fig2a["unattended_CRF"],
        fig2a["percent_modulation"],
        title="A — predominantly contrast gain",
        group_scale=group_scale,
    )

    fig2b = records["2B"]
    panels["2B"] = _plot_normalized_crf_with_modulation(
        fig.add_subplot(grid[0, 1]), "2B",
        fig2b["c"], fig2b["attended_CRF"], fig2b["unattended_CRF"],
        fig2b["percent_modulation"],
        title="B — predominantly response gain",
        group_scale=group_scale,
    )

    _draw_not_reproduced(fig.add_subplot(grid[1, :]), "legend — not reproduced")

    fig.suptitle("Figure 2: attention can produce contrast or response gain", fontsize=12)
    return {"path": _save(fig, path), "panels": panels}


def render_figure_3(records: dict, group_scale: float,
                    output_dir: str | Path | None = None) -> dict:
    """Render the FULL Figure-3 paper grid from records (2 rows x 3 cols + legend).

    ``records`` maps ``{"3C": rec, "3F": rec}``; ``group_scale`` is the figure-3
    CRF group's shared-scale divisor.

    Layout (figure_3_layout.yaml):
      Row0: [A config (NR) | B empirical R,P&D 2000 (NR) | C MODEL]
      Row1: [D config (NR) | E empirical Williford&Maunsell (NR) | F MODEL]
      Row2: legend (NR, spanning).
    Reproduced model panels: 3C, 3F. Returns per-panel introspection.

    Citation: C-014
    """
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 8.4), constrained_layout=True)
    grid = fig.add_gridspec(3, 3, height_ratios=[1.0, 1.0, 0.16])
    path = _output_dir(output_dir) / "figure_3.png"

    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), "B · empirical\nReynolds et al. 2000\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 0]), "D · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 1]), "E · empirical\nWilliford & Maunsell 2006\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[2, :]), "legend — not reproduced")

    panels: dict[str, dict] = {}
    out_c = records["3C"]
    panels["3C"] = _plot_normalized_crf_with_modulation(
        fig.add_subplot(grid[0, 2]), "3C",
        out_c["c"], out_c["attended_CRF"], out_c["unattended_CRF"],
        out_c["percent_modulation"],
        title="C — mixed attention effect",
        attended_label="attend in RF", unattended_label="attend contralateral",
        group_scale=group_scale,
    )
    out_f = records["3F"]
    panels["3F"] = _plot_normalized_crf_with_modulation(
        fig.add_subplot(grid[1, 2]), "3F",
        out_f["c"], out_f["attended_CRF"], out_f["unattended_CRF"],
        out_f["percent_modulation"],
        title="F — mixed attention effect",
        attended_label="attend in RF", unattended_label="attend contralateral",
        group_scale=group_scale,
    )
    fig.suptitle("Figure 3: baseline shifts attentional modulation across contrast", fontsize=12)
    return {"path": _save(fig, path), "panels": panels}


def render_figure_4(records: dict, group_scale: float,
                    output_dir: str | Path | None = None) -> dict:
    """Render the FULL Figure-4 paper grid from records (2 rows x 3 cols + legend).

    ``records`` maps ``{"4C": rec, "4E": rec}`` where 4C is a ``crf_pair_record``
    (keyed on ``c_pref``) and 4E a ``crf_ratio_record``; ``group_scale`` is the
    figure-4 CRF group's shared-scale divisor.

    Layout (figure_4_layout.yaml):
      Row0: [A config (NR) | B empirical M-T&Treue 2002 (NR) | C MODEL]
      Row1: [D config (NR) | blank (NR)                      | E MODEL]
      Row2: legend (NR, spanning).
    Reproduced model panels: 4C, 4E.

    ⚠️ 4E's right (Attentional Modulation %) axis is PINNED to the paper's
    (0, 100) with autoscale OFF. The model's 4E modulation magnitude reaches
    ~300-400%, so the dashed curve OVERFLOWS the axis — visible in the PNG and
    caught by ``test_figure_4E_modulation_within_paper_axis`` as the intended
    deterministic FAILURE. Do not widen the axis (panel_E.md).

    Citation: C-015
    """
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 8.4), constrained_layout=True)
    grid = fig.add_gridspec(3, 3, height_ratios=[1.0, 1.0, 0.16])
    path = _output_dir(output_dir) / "figure_4.png"

    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), "B · empirical\nMartinez-Trujillo & Treue 2002\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 0]), "D · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 1]), "not reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[2, :]), "legend — not reproduced")

    panels: dict[str, dict] = {}
    fig4c = records["4C"]
    panels["4C"] = _plot_normalized_crf_with_modulation(
        fig.add_subplot(grid[0, 2]), "4C",
        fig4c["c_pref"], fig4c["attended_CRF"], fig4c["unattended_CRF"],
        fig4c["percent_modulation"],
        attended_label="attend nonpreferred", unattended_label="attend away",
        title="C — attend nonpreferred in RF",
        group_scale=group_scale,
    )

    fig4e = records["4E"]
    # Percent attentional modulation for 4E uses the same definition as the
    # crf_pair_record helper, 100*(attended - unattended)/unattended, which for
    # the attend-pref vs attend-nonpref pair equals (ratio - 1) * 100.
    fig4e_pct_mod = (np.asarray(fig4e["ratio"], dtype=float) - 1.0) * 100.0
    panels["4E"] = _plot_normalized_crf_with_modulation(
        fig.add_subplot(grid[1, 2]), "4E",
        fig4e["c"], fig4e["attend_pref_CRF"], fig4e["attend_nonpref_CRF"],
        fig4e_pct_mod,
        attended_label="attend preferred", unattended_label="attend nonpreferred",
        title="E — attend preferred scales response",
        group_scale=group_scale,
    )
    fig.suptitle("Figure 4: attention changes two-stimulus competition", fontsize=12)
    return {"path": _save(fig, path), "panels": panels}


def _render_tuning_figure(
    *, fig_n: int, panel_id: str, record: dict, curves_from, title: str,
    xlabel: str, suptitle: str, output_dir, b_label: str,
) -> dict:
    """Shared 1x3+legend paper grid for the tuning figures (5/6/7).

    Row0: [A config (NR) | B empirical (NR) | C MODEL]; Row1: legend (NR).
    ``record`` is the tuning measurement record for the model panel.
    """
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 4.6), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.18])
    path = _output_dir(output_dir) / f"figure_{fig_n}.png"

    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), b_label)
    _draw_not_reproduced(fig.add_subplot(grid[1, :]), "legend — not reproduced")

    panel = _plot_tuning(
        fig.add_subplot(grid[0, 2]), panel_id,
        record[curves_from["x"]], curves_from["curves"](record),
        title=title, xlabel=xlabel,
    )
    fig.suptitle(suptitle, fontsize=12)
    return {"path": _save(fig, path), "panels": {panel_id: panel}}


def render_figure_5(record: dict, output_dir: str | Path | None = None) -> dict:
    """Render the FULL Figure-5 paper grid from a record; model panel 5C.

    Citation: C-016
    """
    return _render_tuning_figure(
        fig_n=5, panel_id="5C", record=record,
        curves_from={
            "x": "theta_0_grid",
            "curves": lambda out: [
                ("attend contralateral", out["unattended_tuning"], COLORS["unattended"]),
                ("attend in RF", out["attended_tuning"], COLORS["attended"]),
            ],
        },
        title="C — spatial attention scales orientation tuning",
        xlabel="stimulus orientation (deg)",
        suptitle="Figure 5: multiplicative scaling without tuning-width change",
        output_dir=output_dir,
        b_label="B · empirical\nMcAdams & Maunsell 1999\nnot reproduced",
    )


def render_figure_6(record: dict, output_dir: str | Path | None = None) -> dict:
    """Render the FULL Figure-6 paper grid from a record; model panel 6C.

    Citation: C-017
    """
    return _render_tuning_figure(
        fig_n=6, panel_id="6C", record=record,
        curves_from={
            "x": "theta_stim_grid",
            "curves": lambda out: [
                ("attend fixation", out["attend_fixation_tuning"], COLORS["unattended"]),
                ("attend contralateral", out["attend_opposite_stimulus_tuning"], COLORS["attended"]),
            ],
        },
        title="C — feature-based attention scales tuning",
        xlabel="motion direction (deg)",
        suptitle="Figure 6: feature-based attention",
        output_dir=output_dir,
        b_label="B · empirical\nMartinez-Trujillo & Treue 2004\nnot reproduced",
    )


def render_figure_7(record: dict, output_dir: str | Path | None = None) -> dict:
    """Render the FULL Figure-7 paper grid from a record; model panel 7C.

    Citation: C-018
    """
    return _render_tuning_figure(
        fig_n=7, panel_id="7C", record=record,
        curves_from={
            "x": "theta_var_grid",
            "curves": lambda out: [
                ("ignored / fixation", out["fixation_tuning"], COLORS["unattended"]),
                ("attend nonpreferred", out["attend_nonpref_tuning"], COLORS["suppressed"]),
                ("attend variable", out["attend_variable_tuning"], COLORS["attended"]),
            ],
        },
        title="C — two-stimulus direction tuning",
        xlabel="variable stimulus direction (deg)",
        suptitle="Figure 7: attention shifts two-stimulus direction tuning",
        output_dir=output_dir,
        b_label="B · empirical\nTreue & Martinez-Trujillo 1999\nnot reproduced",
    )


# ---------------------------------------------------------------------------
# Reference figures rendered FROM THE DIGITIZATION (WORKFLOW.md §3b). These use
# the SAME _plot_* helpers and the SAME pinned axes as the implementation
# renders above, so (paper panel) vs (digitized reference) vs (implementation)
# line up cell-for-cell on identical axes. They read ONLY the digitized JSONs
# (Phase-A-owned), so they need no model record.
# ---------------------------------------------------------------------------

def _crf_reference_panel(ax, figure: int, panel: str, *, title: str,
                         attended_key: str, unattended_key: str,
                         attended_label: str, unattended_label: str) -> dict:
    """Render one digitized CRF panel (left curves + dashed % modulation)."""
    dig = load_digitized(figure, panel)
    x = _digitized_x_grid(dig)
    att = _resample_curve(dig["curves"][attended_key]["points"], x, log_x=True)
    una = _resample_curve(dig["curves"][unattended_key]["points"], x, log_x=True)
    pm = _resample_curve(dig["curves"]["percent_modulation"]["points"], x, log_x=True)
    return _plot_normalized_crf_with_modulation(
        ax, f"{figure}{panel}", x, att, una, pm, title=title,
        attended_label=attended_label, unattended_label=unattended_label,
        group_scale=None,  # digitized curves are already on the shared scale.
    )


def render_figure_2_reference(output_dir: str | Path | None = None) -> dict:
    """Figure 2 grid rendered from the digitized paper curves. Citation: C-013"""
    plt = _pyplot()
    fig = plt.figure(figsize=(10.2, 6.0), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.18])
    path = _output_dir(output_dir) / "figure_2_reference.png"
    panels = {
        "2A": _crf_reference_panel(
            fig.add_subplot(grid[0, 0]), 2, "A", title="A — predominantly contrast gain",
            attended_key="attended", unattended_key="unattended",
            attended_label="attended", unattended_label="ignored / unattended"),
        "2B": _crf_reference_panel(
            fig.add_subplot(grid[0, 1]), 2, "B", title="B — predominantly response gain",
            attended_key="attended", unattended_key="unattended",
            attended_label="attended", unattended_label="ignored / unattended"),
    }
    _draw_not_reproduced(fig.add_subplot(grid[1, :]), "legend — not reproduced")
    fig.suptitle("Figure 2 (digitized reference): contrast vs response gain", fontsize=12)
    return {"path": _save(fig, path), "panels": panels}


def render_figure_3_reference(output_dir: str | Path | None = None) -> dict:
    """Figure 3 grid rendered from the digitized paper curves. Citation: C-014"""
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 8.4), constrained_layout=True)
    grid = fig.add_gridspec(3, 3, height_ratios=[1.0, 1.0, 0.16])
    path = _output_dir(output_dir) / "figure_3_reference.png"
    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), "B · empirical\nReynolds et al. 2000\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 0]), "D · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 1]), "E · empirical\nWilliford & Maunsell 2006\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[2, :]), "legend — not reproduced")
    panels = {
        "3C": _crf_reference_panel(
            fig.add_subplot(grid[0, 2]), 3, "C", title="C — mixed attention effect",
            attended_key="attended", unattended_key="unattended",
            attended_label="attend in RF", unattended_label="attend contralateral"),
        "3F": _crf_reference_panel(
            fig.add_subplot(grid[1, 2]), 3, "F", title="F — mixed attention effect",
            attended_key="attended", unattended_key="unattended",
            attended_label="attend in RF", unattended_label="attend contralateral"),
    }
    fig.suptitle("Figure 3 (digitized reference): baseline shift across contrast", fontsize=12)
    return {"path": _save(fig, path), "panels": panels}


def render_figure_4_reference(output_dir: str | Path | None = None) -> dict:
    """Figure 4 grid rendered from the digitized paper curves. Citation: C-015"""
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 8.4), constrained_layout=True)
    grid = fig.add_gridspec(3, 3, height_ratios=[1.0, 1.0, 0.16])
    path = _output_dir(output_dir) / "figure_4_reference.png"
    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), "B · empirical\nMartinez-Trujillo & Treue 2002\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 0]), "D · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, 1]), "not reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[2, :]), "legend — not reproduced")
    panels = {
        "4C": _crf_reference_panel(
            fig.add_subplot(grid[0, 2]), 4, "C", title="C — attend nonpreferred in RF",
            attended_key="attended", unattended_key="unattended",
            attended_label="attend nonpreferred", unattended_label="attend away"),
        "4E": _crf_reference_panel(
            fig.add_subplot(grid[1, 2]), 4, "E", title="E — attend preferred scales response",
            attended_key="attend_pref", unattended_key="attend_nonpref",
            attended_label="attend preferred", unattended_label="attend nonpreferred"),
    }
    fig.suptitle("Figure 4 (digitized reference): two-stimulus competition", fontsize=12)
    return {"path": _save(fig, path), "panels": panels}


def _tuning_reference_panel(ax, figure: int, panel: str, curve_specs: list,
                            *, title: str, xlabel: str) -> dict:
    """Render one digitized tuning panel from a list of (json_key, label, color)."""
    dig = load_digitized(figure, panel)
    x = _digitized_x_grid(dig)
    curves = [
        (label, _resample_curve(dig["curves"][key]["points"], x, log_x=False), color)
        for key, label, color in curve_specs
    ]
    return _plot_tuning(ax, f"{figure}{panel}", x, curves, title=title, xlabel=xlabel)


def render_figure_5_reference(output_dir: str | Path | None = None) -> dict:
    """Figure 5 grid rendered from the digitized paper curves. Citation: C-016"""
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 4.6), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.18])
    path = _output_dir(output_dir) / "figure_5_reference.png"
    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), "B · empirical\nMcAdams & Maunsell 1999\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, :]), "legend — not reproduced")
    panel = _tuning_reference_panel(
        fig.add_subplot(grid[0, 2]), 5, "C",
        [("unattended", "attend contralateral", COLORS["unattended"]),
         ("attended", "attend in RF", COLORS["attended"])],
        title="C — spatial attention scales orientation tuning",
        xlabel="stimulus orientation (deg)")
    fig.suptitle("Figure 5 (digitized reference): multiplicative scaling", fontsize=12)
    return {"path": _save(fig, path), "panels": {"5C": panel}}


def render_figure_6_reference(output_dir: str | Path | None = None) -> dict:
    """Figure 6 grid rendered from the digitized paper curves. Citation: C-017"""
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 4.6), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.18])
    path = _output_dir(output_dir) / "figure_6_reference.png"
    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), "B · empirical\nMartinez-Trujillo & Treue 2004\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, :]), "legend — not reproduced")
    panel = _tuning_reference_panel(
        fig.add_subplot(grid[0, 2]), 6, "C",
        [("attend_fixation", "attend fixation", COLORS["unattended"]),
         ("attend_contralateral", "attend contralateral", COLORS["attended"])],
        title="C — feature-based attention scales tuning",
        xlabel="motion direction (deg)")
    fig.suptitle("Figure 6 (digitized reference): feature-based attention", fontsize=12)
    return {"path": _save(fig, path), "panels": {"6C": panel}}


def render_figure_7_reference(output_dir: str | Path | None = None) -> dict:
    """Figure 7 grid rendered from the digitized paper curves. Citation: C-018"""
    plt = _pyplot()
    fig = plt.figure(figsize=(12.0, 4.6), constrained_layout=True)
    grid = fig.add_gridspec(2, 3, height_ratios=[1.0, 0.18])
    path = _output_dir(output_dir) / "figure_7_reference.png"
    _draw_not_reproduced(fig.add_subplot(grid[0, 0]), "A · config\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[0, 1]), "B · empirical\nTreue & Martinez-Trujillo 1999\nnot reproduced")
    _draw_not_reproduced(fig.add_subplot(grid[1, :]), "legend — not reproduced")
    panel = _tuning_reference_panel(
        fig.add_subplot(grid[0, 2]), 7, "C",
        [("fixation", "ignored / fixation", COLORS["unattended"]),
         ("attend_nonpref", "attend nonpreferred", COLORS["suppressed"]),
         ("attend_variable", "attend variable", COLORS["attended"])],
        title="C — two-stimulus direction tuning",
        xlabel="variable stimulus direction (deg)")
    fig.suptitle("Figure 7 (digitized reference): two-stimulus direction tuning", fontsize=12)
    return {"path": _save(fig, path), "panels": {"7C": panel}}


_REFERENCE_RENDERERS = {
    2: render_figure_2_reference,
    3: render_figure_3_reference,
    4: render_figure_4_reference,
    5: render_figure_5_reference,
    6: render_figure_6_reference,
    7: render_figure_7_reference,
}


def save_all_references(output_dir: str | Path | None = None) -> list[Path]:
    """Render every digitized-reference figure (WORKFLOW.md §3b)."""
    target = _output_dir(output_dir)
    return [render(target)["path"] for render in _REFERENCE_RENDERERS.values()]
