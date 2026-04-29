"""Sanity-check shim: handle model-local sys.path, re-export framework helpers.

The reusable helpers (require_plotting, output_dir, matrix_stats,
matrix_excerpt, write_text, save_heatmap_grid) live in
`neuromodels.framework.explore` so all models share the same style. This
shim exists only because individual `check_*.py` scripts run as `__main__`
and need the model's `src/` on sys.path to import the model package.
"""

from __future__ import annotations

import sys
from pathlib import Path

from neuromodels.framework.explore import (
    matrix_excerpt,
    matrix_stats,
    output_dir,
    require_plotting,
    save_heatmap_grid,
    write_text,
)

IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = IMPLEMENTATION_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


__all__ = [
    "IMPLEMENTATION_ROOT",
    "SRC_ROOT",
    "matrix_excerpt",
    "matrix_stats",
    "output_dir",
    "require_plotting",
    "save_heatmap_grid",
    "write_text",
]
