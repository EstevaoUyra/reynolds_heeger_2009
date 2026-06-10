"""Reynolds & Heeger (2009) normalization model — pipeline.

Implements the computation steps defined in article_aware/spec/model_spec.yaml
under `pipeline`. Each function corresponds to one step and references the
equation it implements.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.signal import fftconvolve

from .helpers import (
    gaussian_1d,
    gaussian_periodic_1d,
    normpdf_1d,
    normpdf_periodic_1d,
)


# Grid convention = the authors' code grid (CODE-019): x ∈ [-200, 200] step 1
# (401 samples), θ ∈ [-180, 180] step 1 (361 samples). Unit sample spacing is
# REQUIRED here: the suppressive/stimulation kernels are unit-volume Gaussians
# (normpdf) and the convolution is NOT integral-normalized (no ·dx/·dθ), so the
# absolute pooled-drive scale — and therefore where the CRF half-saturates —
# depends on the grid spacing. The authors' code runs at spacing 1; reproducing
# its S/(A·E) balance (the SQ-005 saturation mechanism) requires the same grid.
DEFAULT_X_MIN, DEFAULT_X_MAX, DEFAULT_DX = -200.0, 200.0, 1.0
DEFAULT_THETA_PERIOD = 360.0  # MT/MST motion direction; V4 protocols use the same grid
DEFAULT_DTHETA = 1.0


@dataclass
class ModelParams:
    """Parameters needed to run the model. Defaults from spec/model_spec.yaml.

    Per-protocol values (stimulus_size, attention_field_size, tuning_width,
    peak_attention_gain_gamma) must be set by the caller; left as None here.
    """

    # Globals resolved from the authors' code (SQ-005, CODE-014/CODE-013).
    # sigma ≈ 0: saturation comes from the pooled suppressive drive S, NOT σ.
    sigma: float = 1.0e-6                     # CODE-014
    alpha: float = 1.0                       # A-002
    threshold_T: float = 0.0                 # A-003
    beta: float = 1.0                        # A-010 (used only by closed-form CRFs)

    # Constants from paper / code (C-010, CODE-010..013).
    stimulation_field_size: float = 5.0      # ExWidth (CODE-012 / C-010)
    stimulation_tuning_width: float = 60.0   # EthetaWidth (CODE-013)
    suppressive_field_size: float = 20.0     # IxWidth (CODE-010 / C-010)
    suppressive_tuning_width: float = 360.0  # IthetaWidth, near-flat θ pool (CODE-011)

    # σ_θ of each input stimulus patch (a near-impulse grating, makeGaussian
    # θ-width 1 in the authors' code, CODE-019). The per-figure ``tuning_width``
    # is the ATTENTION-field feature width (AthetaWidth), a different kernel.
    stimulus_tuning_width: float = 1.0       # CODE-019

    # Grid (A-005, A-008)
    x_grid: np.ndarray = field(default_factory=lambda: np.arange(
        DEFAULT_X_MIN, DEFAULT_X_MAX + DEFAULT_DX, DEFAULT_DX
    ))
    theta_grid: np.ndarray = field(default_factory=lambda: np.arange(
        -DEFAULT_THETA_PERIOD / 2, DEFAULT_THETA_PERIOD / 2 + DEFAULT_DTHETA, DEFAULT_DTHETA
    ))
    theta_period: float = DEFAULT_THETA_PERIOD

    # Per-protocol (must be set by caller)
    stimulus_size: float | None = None
    attention_field_size: float | None = None
    tuning_width: float | None = None
    peak_attention_gain_gamma: float | None = None

    # Optional baselines for figs 3C / 3F, resolved from the authors' code
    # (CODE-017): baseline_modulated (added to E, attention-modulated path) and
    # baseline_unmodulated (added to R after normalization).
    baseline_modulated_by_attention: float = 0.0
    baseline_unmodulated: float = 0.0

    # Recorded neuron coordinates (default: origin)
    recorded_x: float = 0.0
    recorded_theta: float = 0.0

    # Config-selectable normalization stage variant (§1 variants-as-config;
    # §5(4) modification smoke test). Default "divisive" = paper Eq. 5 and
    # is byte-for-behavior identical to the pre-migration path. A non-default
    # value is set ONLY via config/ledger, never by editing stage code.
    normalization_variant: str = "divisive"


def _resolved_normalization_variant() -> str:
    """Config-only normalization-stage selector (§1 variants-as-config).

    Resolution order (all config, never code): the
    ``RH_NORMALIZATION_VARIANT`` environment variable, else the
    ``model.normalization_variant`` ledger key, else "divisive". This is
    what makes the §5(4) modification smoke test a pure config swap.
    """
    import os

    env = os.environ.get("RH_NORMALIZATION_VARIANT")
    if env:
        return env
    try:
        from .calibration import resolve

        return str(resolve("model.normalization_variant"))
    except Exception:
        return "divisive"


def default_params(**overrides) -> ModelParams:
    """Build a ModelParams with defaults plus any overrides.

    The normalization-stage variant is resolved from config (ledger / env)
    unless explicitly overridden, so a stage swap is config-only.
    """
    p = ModelParams()
    p.normalization_variant = _resolved_normalization_variant()
    for k, v in overrides.items():
        setattr(p, k, v)
    return p


# --- Pipeline steps ---


def _separable_conv(
    image: np.ndarray,
    kernel_x: np.ndarray,
    kernel_theta: np.ndarray,
) -> np.ndarray:
    """conv2sepYcirc: separable 2D convolution — zero-pad in x, circular in θ.

    Plain DISCRETE convolution (unit sample spacing): the kernels are unit-volume
    (normpdf) Gaussians and are NOT integral-normalized, so there is NO ·dx / ·dθ
    factor. Both the stimulus drive and the suppressive drive use this operator
    (attentionModel.m:166, :171).

    Code: CODE-001, CODE-002, CODE-003 (conv2sepYcirc; zero-pad x, circular θ)
    Assumption: A-011 (boundary conditions)
    """
    # x axis: linear convolution, zero-padded ('same' returns input width).
    conv_x = fftconvolve(image, kernel_x[np.newaxis, :], mode="same", axes=1)
    # θ axis: circular convolution via FFT. Align the kernel peak to index 0.
    kernel_theta_aligned = np.roll(kernel_theta, -int(np.argmax(kernel_theta)))
    F_kernel = np.fft.fft(kernel_theta_aligned)[:, np.newaxis]
    F_image = np.fft.fft(conv_x, axis=0)
    return np.fft.ifft(F_image * F_kernel, axis=0).real


def build_suppressive_kernel(
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    suppressive_field_size: float,
    suppressive_tuning_width: float,
    theta_period: float = DEFAULT_THETA_PERIOD,
) -> tuple[np.ndarray, np.ndarray]:
    """Build the separable suppressive kernel (s_x, s_theta).

    Each component is a UNIT-VOLUME (normpdf) 1D Gaussian — the authors'
    ``makeGaussian`` with no height argument (CODE-002). The kernel is NOT
    renormalized to a joint integral of 1: on the unit-spacing grid the spatial
    kernel sums to ~1 and the near-flat θ kernel (σ=360 ≫ the θ span) sums to
    ~0.384. This broad, near-flat θ pool is what makes the pooled suppressive
    drive S commensurate with A·E so the CRFs saturate (SQ-005). The earlier
    integral-normalized form made S too small and the CRFs never bent over.

    Citation: C-002, C-009, C-011 (EQ-suppressive_kernel)
    Code: CODE-001, CODE-002, CODE-010, CODE-011
    Assumption: A-004 (sigma convention), A-011 (periodic in θ)
    """
    s_x = normpdf_1d(x_grid, 0.0, suppressive_field_size)
    s_theta = normpdf_periodic_1d(theta_grid, 0.0, suppressive_tuning_width, theta_period)
    return s_x, s_theta


def build_stimulus_drive(
    stimuli: list[dict],
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    stimulus_size: float,
    tuning_width: float,
    theta_period: float = DEFAULT_THETA_PERIOD,
    stimulation_field_size: float = 5.0,
    stimulation_tuning_width: float = 60.0,
) -> np.ndarray:
    """Stimulus drive Eraw = conv2sepYcirc(stim, ExKernel, EthetaKernel).

    Each stimulus is a dict with keys 'x', 'theta', 'contrast'. The raw stimulus
    image is a sum of amplitude-(contrast) Gaussians — spatial σ = ``stimulus_size``
    (stimWidth) and feature σ = ``tuning_width`` (the per-stimulus θ width, a
    near-impulse σ=1 grating in the authors' code, CODE-019). That image is then
    convolved with the STIMULATION FIELD — unit-volume kernels of spatial σ =
    ``stimulation_field_size`` (ExWidth=5) and feature σ = ``stimulation_tuning_width``
    (EthetaWidth=60) — exactly as the code builds Eraw (attentionModel.m:166).

    This stimulation-field convolution sets the absolute magnitude of E (hence of
    the pooled S), which is what places the CRF's half-saturation inside the swept
    contrast window; a direct Gaussian (no convolution) over-scales E and the CRF
    saturates below the window. The rendered Figure-1 "Stimulus drive" panel is
    this Eraw (PRE-attention), so E is left/right symmetric (figure_1.md #1).

    Citation: C-009 (EQ-stim)
    Code: CODE-001, CODE-002, CODE-012, CODE-013, CODE-019
    Assumption: A-009 (form of stimulus drive)
    """
    stim_image = np.zeros((len(theta_grid), len(x_grid)))
    for stim in stimuli:
        gx = gaussian_1d(x_grid, stim["x"], stimulus_size)
        # Per-stimulus θ profile: the author makeGaussian(theta, center, sigma, height=1)
        # is a NON-periodic peak-1 Gaussian over theta=[-180:180]' (Figure*.m; makeGaussian.m
        # = normpdf, here with an explicit height of 1). It does NOT wrap at ±180. The earlier
        # periodic form wrapped the +180-edge null stimulus's off-grid tail back, inflating its
        # θ-column mass (+43%) and the suppressive drive S (+17%) — Finding 1 (Fig 7C). The
        # stimulation/suppression/attention KERNELS stay circular (that operator is correct).
        gt = gaussian_1d(theta_grid, stim["theta"], tuning_width)
        stim_image = stim_image + stim["contrast"] * np.outer(gt, gx)
    ex = normpdf_1d(x_grid, 0.0, stimulation_field_size)
    etheta = normpdf_periodic_1d(
        theta_grid, 0.0, stimulation_tuning_width, theta_period
    )
    # Clamp FFT round-off negatives (≈ -1e-21): the drive is non-negative.
    return np.maximum(_separable_conv(stim_image, ex, etheta), 0.0)


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
        'shape': 'oval' (default) or 'cross' — the attention-field SHAPE
            (attentionModel.m ``Ashape``). 'oval' is the separable peak-1 Gaussian
            product (the default for every other panel). 'cross' is the authors'
            additive separable spatial×feature field used by Figure 6C
            (CODE-018 / attentionModel.m:146-162).
    If both centers are None, A = 1 everywhere (no attention modulation).

    Citation: C-005, C-009 (EQ-attention)
    Code: CODE-018 ('cross' shape, attentionModel.m:146-162)
    Assumption: A-004 (sigma convention)
    """
    spatial_center = attention_condition.get("spatial_center")
    feature_center = attention_condition.get("feature_center")
    shape = attention_condition.get("shape", "oval")
    n_theta, n_x = len(theta_grid), len(x_grid)
    if spatial_center is None and feature_center is None:
        return np.ones((n_theta, n_x))

    if shape == "cross":
        return _build_attention_field_cross(
            spatial_center, feature_center, x_grid, theta_grid,
            attention_field_size, peak_attention_gain_gamma, feature_tuning_width,
            theta_period,
        )

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


def _build_attention_field_cross(
    spatial_center: float | None,
    feature_center: float | None,
    x_grid: np.ndarray,
    theta_grid: np.ndarray,
    attention_field_size: float,
    peak_attention_gain_gamma: float,
    feature_tuning_width: float | None,
    theta_period: float,
) -> np.ndarray:
    """Authors' 'cross' attention field (attentionModel.m:146-162, CODE-018).

    Faithful transcription of the MATLAB ``Ashape=='cross'`` branch with
    Apeak = ``peak_attention_gain_gamma``, Abase = 1::

        attnGainX     = (Apeak-Abase)·makeGaussian(x,Ax,AxWidth,1) + Abase
        attnGainTheta = (Apeak-Abase)·makeGaussian(theta,0,AthetaWidth,1) + Abase
        impulse       = (theta == Atheta)
        attnGain      = conv2sepYcirc(impulse·attnGainX, [1], attnGainTheta)
        attnGain      = (Apeak-Abase)·attnGain + Abase

    Note the DOUBLE baseline-lift: each separable factor is lifted to
    [Abase, Apeak], their (circular-θ) convolution is formed, then the whole
    field is lifted to [Abase, ...] again. Unlike the 'oval' field this is NOT a
    simple ``1+(γ-1)·G_x·G_θ`` product, so the peak gain at the attended
    locus exceeds γ; but at the recorded RF column (far in x from the attended
    Ax) ``attnGainX≈Abase`` so the directional gain reaches the RF only through
    the θ-convolution, at moderated strength — the mechanism that makes 6C land
    at the digitized peak ratio 1.108 (CODE-018).

    A flat factor (its center None) is replaced by the all-ones factor BEFORE the
    baseline-lift, matching the MATLAB ``isnan(Ax)`` / ``isnan(Atheta)`` guards.

    Code: CODE-018 (Figure6C.m: AxWidth=30, AthetaWidth=60, Ashape='cross')
    Citation: C-017 (separable spatial×feature attention field)
    """
    apeak = float(peak_attention_gain_gamma)
    abase = 1.0
    nth, nx = len(theta_grid), len(x_grid)

    if spatial_center is not None:
        attn_gain_x = (apeak - abase) * gaussian_1d(
            x_grid, spatial_center, attention_field_size
        ) + abase
    else:
        attn_gain_x = np.ones(nx)

    if feature_center is not None:
        if feature_tuning_width is None:
            raise ValueError("feature_tuning_width required when feature_center is set")
        # makeGaussian(theta, 0, AthetaWidth, 1): the θ profile is centred at 0
        # and SHIFTED to Atheta by the impulse·conv step below (attentionModel.m).
        attn_gain_theta = (apeak - abase) * gaussian_periodic_1d(
            theta_grid, 0.0, feature_tuning_width, theta_period
        ) + abase
        atheta = feature_center
    else:
        attn_gain_theta = np.ones(nth)
        atheta = 0.0

    # impulse·attnGainX: a (nth, nx) image whose only non-zero row is at θ=Atheta.
    j = int(np.argmin(np.abs(theta_grid - atheta)))
    impulse_image = np.zeros((nth, nx))
    impulse_image[j, :] = attn_gain_x

    # conv2sepYcirc(impulse·attnGainX, [1], attnGainTheta): identity in x, circular
    # convolution in θ with the (lifted) θ profile — spreads attnGainX across θ
    # weighted by attnGainTheta shifted to Atheta.
    attn_gain = _separable_conv(impulse_image, np.array([1.0]), attn_gain_theta)
    return (apeak - abase) * attn_gain + abase


def compute_suppressive_drive(
    s_x: np.ndarray,
    s_theta: np.ndarray,
    A: np.ndarray,
    E: np.ndarray,
) -> np.ndarray:
    """S(x,θ) = conv2sepYcirc(A·E, s_x, s_theta): zero-padded in x, circular in θ.

    Plain discrete convolution with the unit-volume suppressive kernels (no
    integral ·dx / ·dθ factor — SQ-005, CODE-001/CODE-002).

    Citation: C-002, C-006 (EQ-6)
    Code: CODE-001, CODE-002, CODE-003
    Assumption: A-011 (boundary conditions)
    """
    S = _separable_conv(A * E, s_x, s_theta)
    return np.maximum(S, 0.0)


def compute_output(
    A: np.ndarray,
    E: np.ndarray,
    S: np.ndarray,
    sigma: float,
    threshold_T: float,
) -> np.ndarray:
    """R(x,θ) = ⌊(A·E) / (S + σ)⌋_T.

    σ ≈ 0 (CODE-014): saturation comes from the pooled suppressive drive S, not σ.

    Citation: C-005 (EQ-5)
    Code: CODE-014 (sigma=1e-6)
    Assumption: A-003 (T = 0)
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
    Code: CODE-001, CODE-002 (separable space×feature suppression; no per-panel gain)
    Assumption: A-009 (stimulus-drive form), A-011 (boundary conditions)
    """
    if any(
        getattr(params, name) is None
        for name in ("stimulus_size", "attention_field_size", "peak_attention_gain_gamma")
    ):
        raise ValueError(
            "stimulus_size, attention_field_size, peak_attention_gain_gamma must be set"
        )

    x_grid, theta_grid = params.x_grid, params.theta_grid

    # ONE suppressive field for every panel: the single cited/code spatial σ (20)
    # and near-flat feature σ (360). No per-panel gain or width scale (A-013).
    s_x, s_theta = build_suppressive_kernel(
        x_grid, theta_grid,
        params.suppressive_field_size,
        params.suppressive_tuning_width,
        params.theta_period,
    )

    # Eraw = conv2sepYcirc(stim, ExKernel, EthetaKernel). The per-stimulus θ width
    # is the near-impulse stimulus_tuning_width (=1, CODE-019), NOT the per-figure
    # tuning_width (that is the ATTENTION feature width below).
    E = build_stimulus_drive(
        stimuli, x_grid, theta_grid,
        params.stimulus_size,
        params.stimulus_tuning_width,
        params.theta_period,
        params.stimulation_field_size,
        params.stimulation_tuning_width,
    )

    if params.baseline_modulated_by_attention != 0.0:
        E = E + params.baseline_modulated_by_attention

    A = build_attention_field(
        attention_condition,
        x_grid,
        theta_grid,
        params.attention_field_size,
        params.peak_attention_gain_gamma,
        params.tuning_width,
        params.theta_period,
    )

    S = compute_suppressive_drive(s_x, s_theta, A, E)
    # Normalization stage (config-selectable variant). The default
    # "divisive" path is identical to the pre-migration compute_output.
    from .stages import normalization as _normalization

    R = _normalization.run(
        A, E, S, params.sigma, params.threshold_T,
        variant=params.normalization_variant,
    )

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
