"""Paper-specific helpers for Reynolds & Heeger qualitative claim tests."""

from __future__ import annotations

import numpy as np


def half_max_contrast(response: np.ndarray, contrast: np.ndarray) -> float:
    """Contrast where a contrast-response function first reaches half-max.

    Linear interpolation is performed on the log-contrast axis used by the
    figure protocols.

    Assumption: A-006
    """
    response = np.asarray(response, dtype=float)
    contrast = np.asarray(contrast, dtype=float)
    target = 0.5 * float(response.max())
    above = np.flatnonzero(response >= target)
    if len(above) == 0:
        return float("nan")
    idx = int(above[0])
    if idx == 0:
        return float(contrast[0])
    c0, c1 = np.log(contrast[idx - 1]), np.log(contrast[idx])
    r0, r1 = response[idx - 1], response[idx]
    if r1 == r0:
        return float(contrast[idx])
    t = (target - r0) / (r1 - r0)
    return float(np.exp(c0 + t * (c1 - c0)))


def value_at(x_grid: np.ndarray, values: np.ndarray, target: float) -> float:
    """Linearly interpolate values at a target x coordinate.

    Assumption: A-006
    """
    return float(
        np.interp(
            float(target),
            np.asarray(x_grid, dtype=float),
            np.asarray(values, dtype=float),
        )
    )


def fwhm(response: np.ndarray, theta: np.ndarray) -> float:
    """Full-width at half-maximum for single-peaked tuning curves.

    Assumption: A-006
    """
    response = np.asarray(response, dtype=float)
    theta = np.asarray(theta, dtype=float)
    above = np.flatnonzero(response >= 0.5 * float(response.max()))
    if len(above) == 0:
        return 0.0
    return float(theta[int(above[-1])] - theta[int(above[0])])


def is_multiplicative_scaling(
    curve_a: np.ndarray,
    curve_b: np.ndarray,
    *,
    mask_below_frac: float,
    max_ratio_spread: float,
) -> bool:
    """True when the ratio between two curves is approximately constant.

    Assumption: A-006
    """
    curve_a = np.asarray(curve_a, dtype=float)
    curve_b = np.asarray(curve_b, dtype=float)
    mask = curve_b > float(mask_below_frac) * float(curve_b.max())
    ratio = curve_a[mask] / curve_b[mask]
    return bool(ratio.max() / ratio.min() < float(max_ratio_spread))


def value_at_min_abs(curve: np.ndarray, grid: np.ndarray) -> float:
    """Return a curve value at the grid sample nearest zero.

    Assumption: A-006
    """
    return float(np.asarray(curve, dtype=float)[int(np.argmin(np.abs(grid)))])
