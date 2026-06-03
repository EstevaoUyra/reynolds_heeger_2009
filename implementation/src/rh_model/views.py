"""Declarative figure renderers (ARCHITECTURE.md §2: the view).

The view *only reads* the measurement record produced by ``protocols`` /
``measurements`` (the single source of truth) and draws panels-as-data. It
recomputes NO model output — there is no call to ``model.simulate`` or any
stage here. Style (colors, axes, normalization-for-display) lives here and
only here; a passing deterministic test and the rendered figure read the
same record so they cannot disagree.

(Renamed from ``figures.py``; ``rh_model.figures`` remains a thin
compatibility shim re-exporting these renderers.)
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterable

import numpy as np

from . import protocols


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "figure_outputs"

COLORS = {
    "attended": "#2f6fbb",
    "unattended": "#555555",
    "suppressed": "#b33f3f",
    "accent": "#2a9d8f",
    "third": "#7a5195",
}


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

    Assumption: model-generated figures are regenerated artifacts, so the
    default location is implementation/figure_outputs.
    """
    path = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
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


def _normalized_pair(attended: np.ndarray, unattended: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Normalize paired response curves to the largest plotted response.

    Assumption: Figures 2 and 3 in the article report normalized model
    response, so figure reproduction should scale model-output curves to
    emphasize CRF shape rather than absolute response units.
    """
    scale = float(max(np.max(attended), np.max(unattended), 1e-12))
    return attended / scale, unattended / scale


def _plot_normalized_crf_with_modulation(
    ax,
    x: np.ndarray,
    attended: np.ndarray,
    unattended: np.ndarray,
    percent_modulation: np.ndarray,
    *,
    title: str,
    xlabel: str = "log contrast",
) -> None:
    """Plot article-style normalized CRFs with dashed modulation on twin axis.

    Citation: C-013, C-014, C-019, C-020
    """
    attended_norm, unattended_norm = _normalized_pair(attended, unattended)
    ax.semilogx(
        x,
        unattended_norm,
        color=COLORS["unattended"],
        linewidth=1.9,
        label="ignored / unattended",
    )
    ax.semilogx(
        x,
        attended_norm,
        color=COLORS["attended"],
        linewidth=2.1,
        label="attended",
    )
    _finish_axes(ax, xlabel=xlabel, ylabel="normalized model response", title=title)
    ax.set_ylim(-0.02, 1.05)

    ax_mod = ax.twinx()
    ax_mod.semilogx(
        x,
        percent_modulation,
        color="#222222",
        linestyle=(0, (4, 3)),
        linewidth=1.7,
        label="% attentional modulation",
    )
    ax_mod.set_ylabel("attentional modulation (%)")
    ax_mod.set_ylim(0.0, max(100.0, float(np.max(percent_modulation)) * 1.1))
    ax_mod.spines["top"].set_visible(False)
    ax_mod.grid(False)

    lines, labels = ax.get_legend_handles_labels()
    mod_lines, mod_labels = ax_mod.get_legend_handles_labels()
    ax.legend(lines + mod_lines, labels + mod_labels, frameon=False, fontsize=8, loc="lower right")


def _plot_tuning(
    ax,
    x: np.ndarray,
    curves: Iterable[tuple[str, np.ndarray, str]],
    *,
    title: str,
    xlabel: str,
) -> None:
    """Plot one or more orientation or direction tuning curves.

    Citation: C-016, C-017, C-018
    """
    for label, y, color in curves:
        ax.plot(x, y, marker="o", markersize=3, linewidth=1.8, label=label, color=color)
    _finish_axes(ax, xlabel=xlabel, ylabel="response", title=title)
    ax.legend(frameon=False, fontsize=8)


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


def save_figure_1(output_dir: str | Path | None = None) -> Path:
    """Render Figure 1-style population fields and theta=0 slices.

    Citation: C-012
    """
    plt = _pyplot()
    out = protocols.run_figure_1()
    path = _output_dir(output_dir) / "figure_1.png"

    x_grid = out["x_grid"]
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
        out["E"],
        x_grid,
        title="Stimulus drive",
        cmap="magma",
        vmin=0.0,
    )
    _show_population_image(
        ax_a,
        out["A"],
        x_grid,
        title="Attention field",
        cmap="gray",
        vmin=0.0,
        vmax=2.0,
    )
    _show_population_image(
        ax_s,
        out["S"],
        x_grid,
        title="Suppressive drive",
        cmap="magma",
        vmin=0.0,
    )
    _show_population_image(
        ax_r,
        out["R"],
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
    return _save(fig, path)


def save_figure_2(output_dir: str | Path | None = None) -> Path:
    """Render Figure 2-style contrast-gain and response-gain panels.

    Citation: C-013
    """
    plt = _pyplot()
    fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.8), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_2.png"

    fig2a = protocols.run_figure_2A(n_contrasts=32)
    _plot_normalized_crf_with_modulation(
        axes[0],
        fig2a["c"],
        fig2a["attended_CRF"],
        fig2a["unattended_CRF"],
        fig2a["percent_modulation"],
        title="2A: predominantly contrast gain",
    )

    fig2b = protocols.run_figure_2B(n_contrasts=32)
    _plot_normalized_crf_with_modulation(
        axes[1],
        fig2b["c"],
        fig2b["attended_CRF"],
        fig2b["unattended_CRF"],
        fig2b["percent_modulation"],
        title="2B: predominantly response gain",
    )
    fig.suptitle("Figure 2: attention can produce contrast or response gain", fontsize=12)
    return _save(fig, path)


def save_figure_3(output_dir: str | Path | None = None) -> Path:
    """Render Figure 3-style baseline CRF reproductions.

    Citation: C-014
    """
    plt = _pyplot()
    # Paper Fig 3 model panels (C, F) are single normalized-CRF plots with a
    # dashed percent-modulation overlay on a twin axis — no separate
    # "absolute difference" panel. MODEL-PANELS-ONLY: one panel per model row.
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_3.png"

    panels = [
        ("3C: mixed attention effect", protocols.run_figure_3C(n_contrasts=32)),
        ("3F: mixed attention effect", protocols.run_figure_3F(n_contrasts=32)),
    ]
    for col, (title, out) in enumerate(panels):
        _plot_normalized_crf_with_modulation(
            axes[col],
            out["c"],
            out["attended_CRF"],
            out["unattended_CRF"],
            out["percent_modulation"],
            title=title,
        )
    fig.suptitle("Figure 3: baseline shifts attentional modulation across contrast", fontsize=12)
    return _save(fig, path)


def save_figure_4(output_dir: str | Path | None = None) -> Path:
    """Render Figure 4-style two-stimulus contrast-response panels.

    Citation: C-015
    """
    plt = _pyplot()
    # Paper Fig 4 model panels (C, E) are single CRF plots. MODEL-PANELS-ONLY:
    # no separate "percent modulation" or "ratio" panel (those were spurious
    # analysis panels the paper figure does not contain).
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.6), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_4.png"

    fig4c = protocols.run_figure_4C(n_contrasts=24)
    _plot_crf(
        axes[0],
        fig4c["c_pref"],
        fig4c["attended_CRF"],
        fig4c["unattended_CRF"],
        attended_label="attend nonpreferred",
        unattended_label="attend away",
        title="4C: nonpreferred attention suppresses preferred response",
        xlabel="preferred-stimulus contrast",
    )

    fig4e = protocols.run_figure_4E(n_contrasts=24)
    _plot_crf(
        axes[1],
        fig4e["c"],
        fig4e["attend_pref_CRF"],
        fig4e["attend_nonpref_CRF"],
        attended_label="attend preferred",
        unattended_label="attend nonpreferred",
        title="4E: attention to preferred scales response",
    )
    fig.suptitle("Figure 4: attention changes two-stimulus competition", fontsize=12)
    return _save(fig, path)


def save_figure_5(output_dir: str | Path | None = None) -> Path:
    """Render Figure 5-style spatial-attention orientation tuning.

    Citation: C-016
    """
    plt = _pyplot()
    # Paper Fig 5C is a single orientation-tuning panel (attended vs
    # unattended). MODEL-PANELS-ONLY: no separate "ratio" analysis panel.
    fig, ax = plt.subplots(figsize=(6.7, 4.6), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_5.png"
    out = protocols.run_figure_5C(n_orientations=61)

    _plot_tuning(
        ax,
        out["theta_0_grid"],
        [
            ("unattended", out["unattended_tuning"], COLORS["unattended"]),
            ("attended", out["attended_tuning"], COLORS["attended"]),
        ],
        title="5C: spatial attention scales orientation tuning",
        xlabel="stimulus orientation (deg)",
    )
    fig.suptitle("Figure 5: multiplicative scaling without tuning-width change", fontsize=12)
    return _save(fig, path)


def save_figure_6(output_dir: str | Path | None = None) -> Path:
    """Render Figure 6-style feature-attention tuning sharpening.

    Citation: C-017
    """
    plt = _pyplot()
    fig, ax = plt.subplots(figsize=(6.7, 4.6), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_6.png"
    out = protocols.run_figure_6C(n_directions=73)

    _plot_tuning(
        ax,
        out["theta_stim_grid"],
        [
            ("attend fixation", out["attend_fixation_tuning"], COLORS["unattended"]),
            (
                "attend opposite stimulus",
                out["attend_opposite_stimulus_tuning"],
                COLORS["attended"],
            ),
        ],
        title="6C: feature-based attention narrows tuning",
        xlabel="motion direction (deg)",
    )
    return _save(fig, path)


def save_figure_7(output_dir: str | Path | None = None) -> Path:
    """Render Figure 7-style three-condition direction tuning.

    Citation: C-018
    """
    plt = _pyplot()
    fig, ax = plt.subplots(figsize=(7.0, 4.6), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_7.png"
    out = protocols.run_figure_7C(n_directions=73)

    _plot_tuning(
        ax,
        out["theta_var_grid"],
        [
            ("fixation", out["fixation_tuning"], COLORS["unattended"]),
            ("attend nonpreferred", out["attend_nonpref_tuning"], COLORS["suppressed"]),
            ("attend variable", out["attend_variable_tuning"], COLORS["attended"]),
        ],
        title="7C: attention shifts two-stimulus direction tuning",
        xlabel="variable stimulus direction (deg)",
    )
    return _save(fig, path)


def save_all_figures(output_dir: str | Path | None = None) -> list[Path]:
    """Render all available model-output reproductions to PNG files.

    Citation: C-012, C-013, C-014, C-015, C-016, C-017, C-018
    """
    target = _output_dir(output_dir)
    return [
        save_figure_1(target),
        save_figure_2(target),
        save_figure_3(target),
        save_figure_4(target),
        save_figure_5(target),
        save_figure_6(target),
        save_figure_7(target),
    ]


def main() -> int:
    """Command-line entry point for rendering all figure PNGs.

    Assumption: a simple module entry point is sufficient for local
    reproduction runs.
    """
    paths = save_all_figures()
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
