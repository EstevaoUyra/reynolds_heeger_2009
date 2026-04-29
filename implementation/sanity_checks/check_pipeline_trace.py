from __future__ import annotations

import numpy as np

from _common import matrix_excerpt, matrix_stats, output_dir, require_plotting, save_heatmap_grid, write_text
from rh_model.model import (
    build_attention_field,
    build_stimulus_drive,
    build_suppressive_kernel,
    compute_output,
    compute_suppressive_drive,
    default_params,
)


def run_trace(name: str, stimuli: list[dict], attention: dict, overrides: dict) -> dict:
    params = default_params(**overrides)
    x_grid = params.x_grid
    theta_grid = params.theta_grid
    dx = float(x_grid[1] - x_grid[0])
    dtheta = float(theta_grid[1] - theta_grid[0])

    s_x, s_theta = build_suppressive_kernel(
        x_grid,
        theta_grid,
        params.suppressive_field_size,
        params.suppressive_tuning_width,
        params.theta_period,
    )
    E = build_stimulus_drive(
        stimuli,
        x_grid,
        theta_grid,
        params.stimulus_size,
        params.tuning_width or 30.0,
        params.theta_period,
    )
    A = build_attention_field(
        attention,
        x_grid,
        theta_grid,
        params.attention_field_size,
        params.peak_attention_gain_gamma,
        params.tuning_width,
        params.theta_period,
    )
    S = compute_suppressive_drive(s_x, s_theta, A, E, dx, dtheta)
    R = compute_output(A, E, S, params.sigma, params.threshold_T)
    return {
        "name": name,
        "x_grid": x_grid,
        "theta_grid": theta_grid,
        "E": E,
        "A": A,
        "AE": A * E,
        "S": S,
        "R": R,
    }


def main() -> None:
    plt, sns = require_plotting()
    out_dir = output_dir(__file__)

    small_grid = {
        "x_grid": np.arange(-30.0, 30.5, 1.0),
        "theta_grid": np.arange(-180.0, 180.0, 10.0),
    }
    scenarios = [
        run_trace(
            "figure2A_attended_c1_small_grid",
            [{"x": 0.0, "theta": 0.0, "contrast": 1.0}],
            {"spatial_center": 0.0, "feature_center": None},
            {
                **small_grid,
                "stimulus_size": 3.0,
                "attention_field_size": 30.0,
                "peak_attention_gain_gamma": 2.0,
                "tuning_width": 30.0,
            },
        ),
        run_trace(
            "figure4C_attend_nonpref_cpref1_small_grid",
            [
                {"x": 0.0, "theta": 0.0, "contrast": 1.0},
                {"x": 0.0, "theta": 180.0, "contrast": 0.5},
            ],
            {"spatial_center": 0.0, "feature_center": 180.0},
            {
                **small_grid,
                "stimulus_size": 5.0,
                "attention_field_size": 5.0,
                "peak_attention_gain_gamma": 5.0,
                "tuning_width": 20.0,
            },
        ),
    ]

    text_sections = ["Pipeline trace sanity check"]
    for scenario in scenarios:
        fields = ["E", "A", "AE", "S", "R"]
        matrices = [scenario[field] for field in fields]
        titles = [f"{scenario['name']}: {field}" for field in fields]
        fig, axes = plt.subplots(2, 3, figsize=(14, 8), constrained_layout=True)
        save_heatmap_grid(fig, axes, matrices, titles, sns=sns)
        fig.suptitle(f"Pipeline fields for {scenario['name']}", y=1.03)
        fig.savefig(out_dir / f"{scenario['name']}_fields.png", dpi=160, bbox_inches="tight")
        plt.close(fig)

        center_theta = int(np.argmin(np.abs(scenario["theta_grid"])))
        fig, ax = plt.subplots(figsize=(9, 5))
        for field in fields:
            ax.plot(scenario["x_grid"], scenario[field][center_theta], label=field)
        ax.set_title(f"Center-theta spatial slices for {scenario['name']}")
        ax.set_xlabel("x")
        ax.set_ylabel("value")
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / f"{scenario['name']}_center_theta_slices.png", dpi=160)
        plt.close(fig)

        parts = [scenario["name"]]
        for field in fields:
            parts.append(
                "\n".join(
                    matrix_stats(
                        field,
                        scenario[field],
                        x_grid=scenario["x_grid"],
                        theta_grid=scenario["theta_grid"],
                    )
                )
                + "\n  center excerpt:\n"
                + matrix_excerpt(scenario[field])
            )
        text_sections.append("\n\n".join(parts))

    write_text(out_dir / "pipeline_trace_summary.txt", text_sections)


if __name__ == "__main__":
    main()
