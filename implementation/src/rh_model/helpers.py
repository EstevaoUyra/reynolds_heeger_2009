"""Numerical helpers used by the model and by tests."""

from __future__ import annotations

import numpy as np


def gaussian_1d(grid: np.ndarray, center: float, sigma: float) -> np.ndarray:
    """Unnormalized Gaussian on a 1D grid; peak value 1 at center.

    Citation: C-009
    Assumption: A-004
    """
    return np.exp(-0.5 * ((grid - center) / sigma) ** 2)


def gaussian_periodic_1d(
    grid: np.ndarray, center: float, sigma: float, period: float
) -> np.ndarray:
    """Unnormalized Gaussian on a periodic 1D grid (orientation/direction).

    Assumption: A-011 (periodic boundary in feature dimension)
    """
    diff = grid - center
    diff = (diff + period / 2.0) % period - period / 2.0
    return np.exp(-0.5 * (diff / sigma) ** 2)


def half_max_contrast(response: np.ndarray, contrast: np.ndarray) -> float:
    """Contrast at which response first reaches half its maximum.

    Linear interpolation between bracketing samples. Assumes monotonic rise
    on the rising portion of the curve.
    """
    half = response.max() / 2.0
    above = response >= half
    if not above.any():
        return float(contrast[-1])
    idx = int(np.argmax(above))
    if idx == 0:
        return float(contrast[0])
    r0, r1 = response[idx - 1], response[idx]
    c0, c1 = contrast[idx - 1], contrast[idx]
    if r1 == r0:
        return float(c0)
    return float(c0 + (c1 - c0) * (half - r0) / (r1 - r0))


def fwhm(response: np.ndarray, theta: np.ndarray) -> float:
    """Full-width-at-half-maximum of a tuning curve.

    Assumes a single peak; returns 0 if nothing crosses half-max.
    """
    half = response.max() / 2.0
    above = response >= half
    if not above.any():
        return 0.0
    idx_left = int(np.argmax(above))
    idx_right = len(above) - 1 - int(np.argmax(above[::-1]))
    return float(theta[idx_right] - theta[idx_left])


def value_at(curve: np.ndarray, x_grid: np.ndarray, x_target: float) -> float:
    """Linearly interpolate `curve` at `x_target` along `x_grid`."""
    return float(np.interp(x_target, x_grid, curve))
