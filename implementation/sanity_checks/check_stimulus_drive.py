from __future__ import annotations

import numpy as np

from _common import matrix_excerpt, matrix_stats, output_dir, require_plotting, write_text
from rh_model.model import build_stimulus_drive


def main() -> None:
    plt, sns = require_plotting()
    out_dir = output_dir(__file__)

    x_grid = np.linspace(-12.0, 12.0, 25)
    theta_grid = np.linspace(-90.0, 90.0, 19)
    positions = [-6.0, 0.0, 6.0]
    contrasts = [0.1, 0.5, 1.0]
    stimulus_size = 3.0
    tuning_width = 30.0

    matrices = []
    titles = []
    text_sections = [
        "Stimulus drive sanity check",
        (
            f"x_grid={x_grid[0]:.1f}..{x_grid[-1]:.1f} ({len(x_grid)} samples), "
            f"theta_grid={theta_grid[0]:.1f}..{theta_grid[-1]:.1f} ({len(theta_grid)} samples)"
        ),
    ]

    for x in positions:
        for contrast in contrasts:
            stimulus = [{"x": x, "theta": 0.0, "contrast": contrast}]
            E = build_stimulus_drive(
                stimulus,
                x_grid,
                theta_grid,
                stimulus_size,
                tuning_width,
            )
            matrices.append(E)
            titles.append(f"x={x:g}, c={contrast:g}")
            text_sections.append(
                "\n".join(
                    matrix_stats(
                        f"E for stimulus x={x:g}, theta=0, contrast={contrast:g}",
                        E,
                        x_grid=x_grid,
                        theta_grid=theta_grid,
                    )
                )
                + "\n  center excerpt:\n"
                + matrix_excerpt(E)
            )

    fig, axes = plt.subplots(3, 3, figsize=(12, 9), constrained_layout=True)
    save_path = out_dir / "stimulus_drive_heatmaps.png"
    from _common import save_heatmap_grid

    save_heatmap_grid(fig, axes, matrices, titles, sns=sns)
    fig.suptitle("Stimulus drive E(x, theta) across positions and contrasts", y=1.02)
    fig.savefig(save_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    center_theta = int(np.argmin(np.abs(theta_grid)))
    fig, ax = plt.subplots(figsize=(9, 5))
    for x, contrast, E in zip(
        np.repeat(positions, len(contrasts)),
        contrasts * len(positions),
        matrices,
        strict=True,
    ):
        ax.plot(x_grid, E[center_theta], label=f"x={x:g}, c={contrast:g}")
    ax.set_title("Stimulus-drive spatial slices at theta=0")
    ax.set_xlabel("x")
    ax.set_ylabel("E(theta=0, x)")
    ax.legend(ncol=3, fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / "stimulus_drive_spatial_slices.png", dpi=160)
    plt.close(fig)

    write_text(out_dir / "stimulus_drive_summary.txt", text_sections)


if __name__ == "__main__":
    main()
