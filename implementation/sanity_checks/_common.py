from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = IMPLEMENTATION_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def require_plotting():
    cache_dir = Path(tempfile.gettempdir()) / "neuromodels_matplotlib_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    import os

    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Plotting dependencies are missing. Install them with: "
            '.venv/bin/python -m pip install -e ".[sanity]"'
        ) from exc
    return plt, sns


def output_dir(script_path: str | Path) -> Path:
    path = Path(script_path)
    out = path.with_name(f"{path.stem}_outputs")
    out.mkdir(parents=True, exist_ok=True)
    return out


def matrix_stats(name: str, matrix: np.ndarray, *, x_grid=None, theta_grid=None) -> list[str]:
    arr = np.asarray(matrix)
    lines = [
        f"{name}",
        f"  shape: {arr.shape}",
        f"  min: {arr.min():.6g}",
        f"  max: {arr.max():.6g}",
        f"  mean: {arr.mean():.6g}",
        f"  sum: {arr.sum():.6g}",
    ]
    if arr.ndim == 2:
        peak = np.unravel_index(int(np.argmax(arr)), arr.shape)
        lines.append(f"  peak_index: theta={peak[0]}, x={peak[1]}")
        if theta_grid is not None and x_grid is not None:
            lines.append(
                f"  peak_coords: theta={float(theta_grid[peak[0]]):.6g}, "
                f"x={float(x_grid[peak[1]]):.6g}"
            )
    elif arr.ndim == 1:
        peak = int(np.argmax(arr))
        lines.append(f"  peak_index: {peak}")
    return lines


def matrix_excerpt(matrix: np.ndarray, rows: int = 7, cols: int = 9) -> str:
    arr = np.asarray(matrix)
    if arr.ndim != 2:
        return np.array2string(arr, precision=3, suppress_small=True)
    r0 = max((arr.shape[0] - rows) // 2, 0)
    c0 = max((arr.shape[1] - cols) // 2, 0)
    excerpt = arr[r0 : r0 + rows, c0 : c0 + cols]
    return np.array2string(excerpt, precision=3, suppress_small=True)


def write_text(path: Path, sections: list[str]) -> None:
    path.write_text("\n\n".join(sections) + "\n", encoding="utf-8")


def save_heatmap_grid(fig, axes, matrices, titles, *, sns, cbar=False) -> None:
    for ax, matrix, title in zip(np.ravel(axes), matrices, titles, strict=False):
        sns.heatmap(np.asarray(matrix), ax=ax, cmap="viridis", cbar=cbar)
        ax.set_title(title)
        ax.set_xlabel("x index")
        ax.set_ylabel("theta index")
    for ax in np.ravel(axes)[len(matrices) :]:
        ax.axis("off")
