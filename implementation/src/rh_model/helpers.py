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


__all__ = [
    "gaussian_1d",
    "gaussian_periodic_1d",
]
