"""Numerical helpers used by the model and by tests."""

from __future__ import annotations

import numpy as np


def gaussian_1d(grid: np.ndarray, center: float, sigma: float) -> np.ndarray:
    """Unnormalized (peak-1) Gaussian on a 1D grid; peak value 1 at center.

    Used for the stimulus/attention *amplitude* profiles (makeGaussian with an
    explicit height of 1 in the authors' code, CODE-019).

    Citation: C-009
    Assumption: A-004
    """
    return np.exp(-0.5 * ((grid - center) / sigma) ** 2)


def gaussian_periodic_1d(
    grid: np.ndarray, center: float, sigma: float, period: float
) -> np.ndarray:
    """Unnormalized (peak-1) periodic Gaussian on a 1D grid (orientation/direction).

    Assumption: A-011 (periodic boundary in feature dimension)
    """
    diff = grid - center
    diff = (diff + period / 2.0) % period - period / 2.0
    return np.exp(-0.5 * (diff / sigma) ** 2)


def normpdf_1d(grid: np.ndarray, center: float, sigma: float) -> np.ndarray:
    """Unit-volume (normpdf) Gaussian on a 1D grid: amplitude 1/(σ·√(2π)).

    This is ``makeGaussian(grid, center, sigma)`` with NO height argument in the
    authors' code — i.e. ``normpdf`` (unit area in unit sample spacing). The
    stimulation- and suppression-field kernels are these unit-volume Gaussians
    and are NOT renormalized to a joint integral of 1 (the discrete convolution
    uses unit sample spacing).

    Code: CODE-002 (makeGaussian no-height => normpdf, unit volume)
    """
    return np.exp(-0.5 * ((grid - center) / sigma) ** 2) / (sigma * np.sqrt(2.0 * np.pi))


def normpdf_periodic_1d(
    grid: np.ndarray, center: float, sigma: float, period: float
) -> np.ndarray:
    """Unit-volume (normpdf) periodic Gaussian on a 1D grid.

    The circular feature-axis counterpart of :func:`normpdf_1d`. On a θ grid
    much narrower than σ (the near-flat IthetaWidth=360 pool) it sums to < 1
    (the code's IthetaKernel sums to ~0.384) — this is intended; the kernel is
    unit-volume per unit sample spacing, not renormalized over the grid.

    Code: CODE-002 (makeGaussian no-height => normpdf)
    Assumption: A-011 (periodic boundary in feature dimension)
    """
    diff = grid - center
    diff = (diff + period / 2.0) % period - period / 2.0
    return np.exp(-0.5 * (diff / sigma) ** 2) / (sigma * np.sqrt(2.0 * np.pi))


__all__ = [
    "gaussian_1d",
    "gaussian_periodic_1d",
    "normpdf_1d",
    "normpdf_periodic_1d",
]
