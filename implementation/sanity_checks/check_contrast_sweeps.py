from __future__ import annotations

import numpy as np

from _common import output_dir, require_plotting, write_text
from rh_model import protocols


def value_at(x_grid: np.ndarray, values: np.ndarray, target: float) -> float:
    return float(np.interp(target, np.asarray(x_grid, dtype=float), np.asarray(values, dtype=float)))


def high_contrast_increment(contrast: np.ndarray, response: np.ndarray) -> float:
    response_at_half = value_at(contrast, response, 0.5)
    return float((response[-1] - response_at_half) / response_at_half)


def plot_attended_unattended(ax, contrast, attended, unattended, title):
    ax.semilogx(contrast, attended, marker="o", label="attended")
    ax.semilogx(contrast, unattended, marker="o", label="unattended")
    ax.set_title(title)
    ax.set_xlabel("contrast")
    ax.set_ylabel("response")
    ax.legend(fontsize=8)


def main() -> None:
    plt, sns = require_plotting()
    sns.set_theme(style="whitegrid")
    out_dir = output_dir(__file__)

    figure_outputs = {
        "figure_2A": protocols.run_figure_2A(),
        "figure_2B": protocols.run_figure_2B(),
        "figure_3C": protocols.run_figure_3C(),
        "figure_3F": protocols.run_figure_3F(),
        "figure_4C": protocols.run_figure_4C(),
        "figure_4E": protocols.run_figure_4E(),
    }

    fig, axes = plt.subplots(3, 2, figsize=(12, 12), constrained_layout=True)
    for ax, name in zip(axes.flat, ["figure_2A", "figure_2B", "figure_3C", "figure_3F"], strict=False):
        out = figure_outputs[name]
        plot_attended_unattended(
            ax,
            out["c"],
            out["attended_CRF"],
            out["unattended_CRF"],
            name,
        )
    out = figure_outputs["figure_4C"]
    plot_attended_unattended(
        axes.flat[4],
        out["c_pref"],
        out["attended_CRF"],
        out["unattended_CRF"],
        "figure_4C attend nonpref vs unattended",
    )
    out = figure_outputs["figure_4E"]
    axes.flat[5].semilogx(out["c"], out["attend_pref_CRF"], marker="o", label="attend_pref")
    axes.flat[5].semilogx(out["c"], out["attend_nonpref_CRF"], marker="o", label="attend_nonpref")
    axes.flat[5].set_title("figure_4E attend pref vs nonpref")
    axes.flat[5].set_xlabel("contrast")
    axes.flat[5].set_ylabel("response")
    axes.flat[5].legend(fontsize=8)
    fig.suptitle("Current contrast response sweeps", y=1.02)
    fig.savefig(out_dir / "contrast_response_sweeps.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for ax, name in zip(axes.flat, ["figure_2A", "figure_2B", "figure_3C", "figure_3F"], strict=True):
        out = figure_outputs[name]
        ax.semilogx(out["c"], out["percent_modulation"], marker="o")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(f"{name} percent modulation")
        ax.set_xlabel("contrast")
        ax.set_ylabel("% modulation")
    fig.savefig(out_dir / "percent_modulation_sweeps.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    sections = ["Contrast-sweep sanity check"]
    for name in ["figure_2A", "figure_2B", "figure_3C", "figure_3F"]:
        out = figure_outputs[name]
        sections.append(
            "\n".join(
                [
                    name,
                    f"  contrasts: {np.array2string(out['c'], precision=4)}",
                    f"  attended_CRF: {np.array2string(out['attended_CRF'], precision=4)}",
                    f"  unattended_CRF: {np.array2string(out['unattended_CRF'], precision=4)}",
                    f"  percent_modulation: {np.array2string(out['percent_modulation'], precision=2)}",
                    f"  percent_modulation_argmax: {int(np.argmax(out['percent_modulation']))}",
                    f"  attended_high_contrast_increment_from_c0.5: {high_contrast_increment(out['c'], out['attended_CRF']):.6g}",
                ]
            )
        )

    out = figure_outputs["figure_4C"]
    high_gap = abs(out["attended_CRF"][-1] - out["unattended_CRF"][-1]) / out["unattended_CRF"][-1]
    max_gap = abs(out["attended_CRF"] - out["unattended_CRF"]).max() / out["unattended_CRF"].max()
    sections.append(
        "\n".join(
            [
                "figure_4C",
                f"  c_pref: {np.array2string(out['c_pref'], precision=4)}",
                f"  attended_CRF: {np.array2string(out['attended_CRF'], precision=4)}",
                f"  unattended_CRF: {np.array2string(out['unattended_CRF'], precision=4)}",
                f"  percent_modulation: {np.array2string(out['percent_modulation'], precision=2)}",
                f"  abs_percent_modulation_argmax: {int(np.argmax(np.abs(out['percent_modulation'])))}",
                f"  high_contrast_gap_ratio: {high_gap:.6g}",
                f"  max_gap_ratio: {max_gap:.6g}",
            ]
        )
    )

    out = figure_outputs["figure_4E"]
    sections.append(
        "\n".join(
            [
                "figure_4E",
                f"  contrasts: {np.array2string(out['c'], precision=4)}",
                f"  attend_pref_CRF: {np.array2string(out['attend_pref_CRF'], precision=4)}",
                f"  attend_nonpref_CRF: {np.array2string(out['attend_nonpref_CRF'], precision=4)}",
                f"  ratio: {np.array2string(out['ratio'], precision=4)}",
                f"  attend_pref_high_contrast_increment_from_c0.5: {high_contrast_increment(out['c'], out['attend_pref_CRF']):.6g}",
            ]
        )
    )

    write_text(out_dir / "contrast_sweep_metrics.txt", sections)


if __name__ == "__main__":
    main()
