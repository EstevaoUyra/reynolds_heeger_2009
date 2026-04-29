"""Model-output figure reproduction for Reynolds & Heeger (2009)."""

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


def _plot_percent_modulation(
    ax,
    x: np.ndarray,
    percent_modulation: np.ndarray,
    *,
    title: str,
    xlabel: str = "contrast",
) -> None:
    """Plot percent modulation across a contrast sweep.

    Citation: C-019, C-020, C-021
    """
    ax.semilogx(
        x,
        percent_modulation,
        color=COLORS["accent"],
        marker="o",
        linewidth=1.8,
    )
    ax.axhline(0.0, color="#888888", linewidth=0.8)
    _finish_axes(ax, xlabel=xlabel, ylabel="% modulation", title=title)


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


def save_figure_1(output_dir: str | Path | None = None) -> Path:
    """Render Figure 1-style population fields and theta=0 slices.

    Citation: C-012
    """
    plt = _pyplot()
    out = protocols.run_figure_1()
    path = _output_dir(output_dir) / "figure_1.png"

    fig, axes = plt.subplots(2, 4, figsize=(13.5, 6.6), constrained_layout=True)
    fields = [
        ("Stimulus drive E", out["E"], out["E_slice"]),
        ("Attention field A", out["A"], out["A_slice"]),
        ("Suppressive drive S", out["S"], out["S_slice"]),
        ("Response R", out["R"], out["R_slice"]),
    ]
    x_grid = out["x_grid"]
    extent = [float(x_grid[0]), float(x_grid[-1]), -180.0, 175.0]

    for col, (title, field, slice_values) in enumerate(fields):
        image = axes[0, col].imshow(
            field,
            origin="lower",
            aspect="auto",
            extent=extent,
            cmap="magma",
        )
        axes[0, col].set_title(title, fontsize=10)
        axes[0, col].set_xlabel("RF center x")
        axes[0, col].set_ylabel("feature preference")
        fig.colorbar(image, ax=axes[0, col], fraction=0.046, pad=0.04)

        axes[1, col].plot(x_grid, slice_values, color=COLORS["attended"], linewidth=1.8)
        axes[1, col].axvline(-10.0, color=COLORS["unattended"], linestyle="--", linewidth=1.0)
        axes[1, col].axvline(10.0, color=COLORS["attended"], linestyle="--", linewidth=1.0)
        _finish_axes(axes[1, col], xlabel="RF center x", ylabel="theta=0 slice")

    fig.suptitle("Figure 1: population fields for two stimuli, attend right", fontsize=12)
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
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.4), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_3.png"

    panels = [
        ("3C: mixed attention effect", protocols.run_figure_3C(n_contrasts=32)),
        ("3F: mixed attention effect", protocols.run_figure_3F(n_contrasts=32)),
    ]
    for row, (title, out) in enumerate(panels):
        _plot_normalized_crf_with_modulation(
            axes[row, 0],
            out["c"],
            out["attended_CRF"],
            out["unattended_CRF"],
            out["percent_modulation"],
            title=title,
        )
        axes[row, 1].semilogx(
            out["c"],
            out["absolute_difference"],
            color=COLORS["accent"],
            marker="o",
            linewidth=1.8,
        )
        _finish_axes(
            axes[row, 1],
            xlabel="log contrast",
            ylabel="attended - unattended response",
            title=f"{title}: absolute difference",
        )
    fig.suptitle("Figure 3: baseline shifts percent and absolute modulation", fontsize=12)
    return _save(fig, path)


def save_figure_4(output_dir: str | Path | None = None) -> Path:
    """Render Figure 4-style two-stimulus contrast-response panels.

    Citation: C-015
    """
    plt = _pyplot()
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.4), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_4.png"

    fig4c = protocols.run_figure_4C(n_contrasts=24)
    _plot_crf(
        axes[0, 0],
        fig4c["c_pref"],
        fig4c["attended_CRF"],
        fig4c["unattended_CRF"],
        attended_label="attend nonpreferred",
        unattended_label="attend away",
        title="4C: nonpreferred attention suppresses preferred response",
        xlabel="preferred-stimulus contrast",
    )
    _plot_percent_modulation(
        axes[1, 0],
        fig4c["c_pref"],
        fig4c["percent_modulation"],
        title="4C: percent modulation",
        xlabel="preferred-stimulus contrast",
    )

    fig4e = protocols.run_figure_4E(n_contrasts=24)
    _plot_crf(
        axes[0, 1],
        fig4e["c"],
        fig4e["attend_pref_CRF"],
        fig4e["attend_nonpref_CRF"],
        attended_label="attend preferred",
        unattended_label="attend nonpreferred",
        title="4E: attention to preferred scales response",
    )
    axes[1, 1].semilogx(
        fig4e["c"],
        fig4e["ratio"],
        color=COLORS["accent"],
        marker="o",
        linewidth=1.8,
    )
    _finish_axes(axes[1, 1], xlabel="contrast", ylabel="attend pref / nonpref", title="4E: ratio")
    fig.suptitle("Figure 4: attention changes two-stimulus competition", fontsize=12)
    return _save(fig, path)


def save_figure_5(output_dir: str | Path | None = None) -> Path:
    """Render Figure 5-style spatial-attention orientation tuning.

    Citation: C-016
    """
    plt = _pyplot()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), constrained_layout=True)
    path = _output_dir(output_dir) / "figure_5.png"
    out = protocols.run_figure_5C(n_orientations=61)

    _plot_tuning(
        axes[0],
        out["theta_0_grid"],
        [
            ("unattended", out["unattended_tuning"], COLORS["unattended"]),
            ("attended", out["attended_tuning"], COLORS["attended"]),
        ],
        title="5C: spatial attention scales orientation tuning",
        xlabel="stimulus orientation (deg)",
    )
    axes[1].plot(out["theta_0_grid"], out["ratio"], color=COLORS["accent"], linewidth=1.8)
    _finish_axes(axes[1], xlabel="stimulus orientation (deg)", ylabel="attended / unattended", title="5C: ratio")
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
