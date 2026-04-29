"""Reynolds & Heeger (2009) normalization model — pipeline.

Implements the computation steps defined in article_aware/spec/model_spec.yaml
under `pipeline`. Each function corresponds to one step and references the
equation it implements.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.signal import fftconvolve

from .helpers import gaussian_1d, gaussian_periodic_1d


# Per A-005, A-008
DEFAULT_X_MIN, DEFAULT_X_MAX, DEFAULT_DX = -100.0, 100.0, 0.5
DEFAULT_THETA_PERIOD = 360.0  # MT/MST motion direction; V4 protocols use the same grid
DEFAULT_DTHETA = 5.0


@dataclass
class ModelParams:
    """Parameters needed to run the model. Defaults from spec/model_spec.yaml.

    Per-protocol values (stimulus_size, attention_field_size, tuning_width,
    peak_attention_gain_gamma) must be set by the caller; left as None here.
    """

    # Underspecified globals (spec values per assumptions A-001..A-003, A-010)
    sigma: float = 0.1                       # A-001
    alpha: float = 1.0                       # A-002
    threshold_T: float = 0.0                 # A-003
    beta: float = 1.0                        # A-010 (used only by closed-form CRFs)

    # Constants from paper (C-010, C-011)
    stimulation_field_size: float = 5.0
    suppressive_field_size: float = 20.0
    suppressive_tuning_width: float = 180.0

    # Grid (A-005, A-008)
    x_grid: np.ndarray = field(default_factory=lambda: np.arange(
        DEFAULT_X_MIN, DEFAULT_X_MAX + DEFAULT_DX, DEFAULT_DX
    ))
    theta_grid: np.ndarray = field(default_factory=lambda: np.arange(
        -DEFAULT_THETA_PERIOD / 2, DEFAULT_THETA_PERIOD / 2, DEFAULT_DTHETA
    ))
    theta_period: float = DEFAULT_THETA_PERIOD

    # Per-protocol (must be set by caller)
    stimulus_size: float | None = None
    attention_field_size: float | None = None
    tuning_width: float | None = None
    peak_attention_gain_gamma: float | None = None

    # Optional baselines for figs 3C / 3F (A-007)
    baseline_modulated_by_attention: float = 0.0
    baseline_unmodulated: float = 0.0

    # Per-protocol calibration for 1D discretized suppressive pooling.
    suppressive_drive_gain: float = 1.0

    # Recorded neuron coordinates (default: origin)
    recorded_x: float = 0.0
    recorded_theta: float = 0.0


def default_params(**overrides) -> ModelParams:
    """Build a ModelParams with defaults plus any overrides."""
    p = ModelParams()
    for k, v in overrides.items():
        setattr(p, k, v)
    return p


# --- Pipeline steps ---


def build_suppressive_kernel(
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    suppressive_field_size: float,
    suppressive_tuning_width: float,
    theta_period: float = DEFAULT_THETA_PERIOD,
) -> tuple[np.ndarray, np.ndarray]:
    """Build the separable suppressive kernel (s_x, s_theta).

    Each component is a 1D Gaussian normalized to integrate to 1 in its
    dimension, so that the joint kernel s(x,θ) = s_x(x) · s_θ(θ) integrates
    to 1 over (x, θ).

    Citation: C-002, C-009, C-011 (EQ-suppressive_kernel)
    Assumption: A-004 (sigma convention), A-011 (periodic in θ)
    """
    s_x = gaussian_1d(x_grid, 0.0, suppressive_field_size)
    s_theta = gaussian_periodic_1d(theta_grid, 0.0, suppressive_tuning_width, theta_period)
    dx = float(x_grid[1] - x_grid[0])
    dtheta = float(theta_grid[1] - theta_grid[0])
    s_x = s_x / (s_x.sum() * dx)
    s_theta = s_theta / (s_theta.sum() * dtheta)
    return s_x, s_theta


def build_stimulus_drive(
    stimuli: list[dict],
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    stimulus_size: float,
    tuning_width: float,
    theta_period: float = DEFAULT_THETA_PERIOD,
) -> np.ndarray:
    """Sum of per-stimulus Gaussian contributions to the stimulus drive.

    Each stimulus is a dict with keys 'x', 'theta', 'contrast'.

    Citation: C-009 (EQ-stim)
    Assumption: A-009 (form of stimulus drive)
    """
    E = np.zeros((len(theta_grid), len(x_grid)))
    for stim in stimuli:
        gx = gaussian_1d(x_grid, stim["x"], stimulus_size)
        gt = gaussian_periodic_1d(theta_grid, stim["theta"], tuning_width, theta_period)
        E = E + stim["contrast"] * np.outer(gt, gx)
    return E


def build_attention_field(
    attention_condition: dict,
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    attention_field_size: float,
    peak_attention_gain_gamma: float,
    feature_tuning_width: float | None = None,
    theta_period: float = DEFAULT_THETA_PERIOD,
) -> np.ndarray:
    """Construct A(x, θ) = 1 + (γ-1) · G_x · G_θ.

    `attention_condition` is a dict with keys:
        'spatial_center': float or None — None = no spatial component (flat in x).
        'feature_center': float or None — None = no feature component (flat in θ).
    If both are None, A = 1 everywhere (no attention modulation).

    Citation: C-005, C-009 (EQ-attention)
    Assumption: A-004 (sigma convention)
    """
    spatial_center = attention_condition.get("spatial_center")
    feature_center = attention_condition.get("feature_center")
    n_theta, n_x = len(theta_grid), len(x_grid)
    if spatial_center is None and feature_center is None:
        return np.ones((n_theta, n_x))
    gx = (
        gaussian_1d(x_grid, spatial_center, attention_field_size)
        if spatial_center is not None
        else np.ones(n_x)
    )
    if feature_center is not None:
        if feature_tuning_width is None:
            raise ValueError("feature_tuning_width required when feature_center is set")
        gt = gaussian_periodic_1d(
            theta_grid, feature_center, feature_tuning_width, theta_period
        )
    else:
        gt = np.ones(n_theta)
    return 1.0 + (peak_attention_gain_gamma - 1.0) * np.outer(gt, gx)


def compute_suppressive_drive(
    s_x: np.ndarray,
    s_theta: np.ndarray,
    A: np.ndarray,
    E: np.ndarray,
    dx: float,
    dtheta: float,
) -> np.ndarray:
    """S(x,θ) = s ∗ (A · E), separable. Zero-padded in x; circular in θ.

    Citation: C-002, C-006 (EQ-6)
    Assumption: A-011 (boundary conditions)
    """
    AE = A * E
    # x convolution: linear (zero-padded), 'same' returns input shape.
    conv_x = fftconvolve(AE, s_x[np.newaxis, :], mode="same", axes=1) * dx
    # θ convolution: circular via FFT. Kernel must be aligned at index 0.
    n_theta = AE.shape[0]
    s_theta_aligned = np.fft.ifftshift(s_theta) if (n_theta % 2 == 0) else np.roll(
        s_theta, -(n_theta // 2)
    )
    F_kernel = np.fft.fft(s_theta_aligned)[:, np.newaxis]
    F_AE = np.fft.fft(conv_x, axis=0)
    S = np.fft.ifft(F_AE * F_kernel, axis=0).real * dtheta
    return S


def compute_output(
    A: np.ndarray,
    E: np.ndarray,
    S: np.ndarray,
    sigma: float,
    threshold_T: float,
) -> np.ndarray:
    """R(x,θ) = ⌊(A·E) / (S + σ)⌋_T.

    Citation: C-005 (EQ-5)
    Assumption: A-001 (sigma value), A-003 (T = 0)
    """
    R = (A * E) / (S + sigma)
    return np.maximum(R - threshold_T, 0.0)


# --- Top-level orchestrator ---


def simulate(
    stimuli: list[dict],
    attention_condition: dict,
    params: ModelParams,
) -> dict:
    """Run the full pipeline; return the recorded neuron's response and the population fields.

    Pipeline order (per spec/model_spec.yaml `pipeline`):
        1. build_suppressive_kernel
        2. build_stimulus_drive
        2.5 add modulated baseline (if set)
        3. build_attention_field
        4. compute_suppressive_drive
        5. compute_output
        5.5 add unmodulated baseline (if set)
        6. extract recorded neuron response

    Citation: C-005, C-006 (EQ-5, EQ-6) end-to-end
    """
    if any(
        getattr(params, name) is None
        for name in ("stimulus_size", "attention_field_size", "peak_attention_gain_gamma")
    ):
        raise ValueError(
            "stimulus_size, attention_field_size, peak_attention_gain_gamma must be set"
        )

    x_grid, theta_grid = params.x_grid, params.theta_grid
    dx = float(x_grid[1] - x_grid[0])
    dtheta = float(theta_grid[1] - theta_grid[0])

    s_x, s_theta = build_suppressive_kernel(
        x_grid, theta_grid,
        params.suppressive_field_size, params.suppressive_tuning_width,
        params.theta_period,
    )

    E = build_stimulus_drive(
        stimuli, x_grid, theta_grid,
        params.stimulus_size, params.tuning_width or 30.0,
        params.theta_period,
    )

    if params.baseline_modulated_by_attention != 0.0:
        E = E + params.baseline_modulated_by_attention

    A = build_attention_field(
        attention_condition, x_grid, theta_grid,
        params.attention_field_size, params.peak_attention_gain_gamma,
        params.tuning_width, params.theta_period,
    )

    S = compute_suppressive_drive(s_x, s_theta, A, E, dx, dtheta)
    S = params.suppressive_drive_gain * S
    R = compute_output(A, E, S, params.sigma, params.threshold_T)

    if params.baseline_unmodulated != 0.0:
        R = R + params.baseline_unmodulated

    i = int(np.argmin(np.abs(x_grid - params.recorded_x)))
    j = int(np.argmin(np.abs(theta_grid - params.recorded_theta)))
    return {
        "response": float(R[j, i]),
        "E": E,
        "A": A,
        "S": S,
        "R": R,
    }
