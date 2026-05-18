"""Backward-compatibility shim — figures.py was renamed to views.py.

ARCHITECTURE.md §2 renames the declarative renderer layer to ``views``.
This module re-exports the public renderers so any existing caller of
``rh_model.figures.save_figure_N`` / ``save_all_figures`` / ``main``
keeps working unchanged. New code should import ``rh_model.views``.
"""

from __future__ import annotations

from .views import (  # noqa: F401
    DEFAULT_OUTPUT_DIR,
    main,
    save_all_figures,
    save_figure_1,
    save_figure_2,
    save_figure_3,
    save_figure_4,
    save_figure_5,
    save_figure_6,
    save_figure_7,
)

__all__ = [
    "DEFAULT_OUTPUT_DIR",
    "save_figure_1",
    "save_figure_2",
    "save_figure_3",
    "save_figure_4",
    "save_figure_5",
    "save_figure_6",
    "save_figure_7",
    "save_all_figures",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
