"""Model-side figure runner: produce records, then call the Phase-A view.

ARCHITECTURE.md §2 separates *running the model* (this module, Phase B /
``implementation/``) from *presentation* (the Phase-A view, which pins axes /
scale / normalization). This runner runs the per-figure ``protocols`` to
produce measurement records, computes the model-derived shared-scale input, and
hands those records to the Phase-A-owned declarative view
(``article_aware/views.py``). It owns NO presentation: every axis limit, colour,
and normalization rule lives in the Phase-A view.

The Phase-A view is a pure renderer that imports nothing from the model; this
runner is the only place records and the view meet. The public API here is
unchanged from the pre-migration ``views.py`` so existing callers (the axis
tests, the ``rh_model.figures`` shim, ``python -m rh_model.views``) keep working
byte-for-behavior identically.

(Presentation relocated to ``article_aware/views.py`` so Phase A owns the
contract unambiguously — chore/view-to-article-aware.)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

from . import protocols


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "figure_outputs"


# ---------------------------------------------------------------------------
# Load the Phase-A view (article_aware/views.py). It is not an installed
# package, so import it by its known path relative to this model directory and
# cache it under a stable module name.
# ---------------------------------------------------------------------------
_ARTICLE_AWARE_VIEWS = (
    Path(__file__).resolve().parents[3] / "article_aware" / "views.py"
)


def _load_view():
    name = "rh_article_aware_views"
    mod = sys.modules.get(name)
    if mod is not None:
        return mod
    spec = importlib.util.spec_from_file_location(name, _ARTICLE_AWARE_VIEWS)
    if spec is None or spec.loader is None:  # pragma: no cover - path guard.
        raise ImportError(f"cannot load Phase-A view from {_ARTICLE_AWARE_VIEWS}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


view = _load_view()

# Re-export the presentation contract so existing callers keep importing it from
# ``rh_model.views`` unchanged (it is *owned* by the Phase-A view).
PAPER_PANEL_LIMITS = view.PAPER_PANEL_LIMITS
paper_panel_limits = view.paper_panel_limits


def _output_dir(output_dir: str | Path | None) -> Path:
    """Resolve the destination directory, defaulting to implementation/figure_outputs.

    The pure Phase-A view requires an explicit directory; the model side owns
    the default artifact location.
    """
    path = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------------------
# Shared-scale CRF normalization: the model half of the ratio.
#
# The Phase-A view pins the SHARED response scale per CRF figure-group
# (2A/2B, 3C/3F, 4C/4E) and owns the *reference* group peak. The *model* group
# peak is a property of a model RUN, so it is computed here from the protocol
# records and passed to the view. The runs use n_contrasts=24 (matching
# article_aware/extracted_data/rh_tier_helpers._model_group_peak exactly) so the
# scale the view applies equals the scale the tier tests measure.
# ---------------------------------------------------------------------------
_CRF_GROUP_SCALE_RUNNERS = {
    (2, "A"): (lambda: protocols.run_figure_2A(n_contrasts=24),
               ("attended_CRF", "unattended_CRF")),
    (2, "B"): (lambda: protocols.run_figure_2B(n_contrasts=24),
               ("attended_CRF", "unattended_CRF")),
    (3, "C"): (lambda: protocols.run_figure_3C(n_contrasts=24),
               ("attended_CRF", "unattended_CRF")),
    (3, "F"): (lambda: protocols.run_figure_3F(n_contrasts=24),
               ("attended_CRF", "unattended_CRF")),
    (4, "C"): (lambda: protocols.run_figure_4C(n_contrasts=24),
               ("attended_CRF", "unattended_CRF")),
    (4, "E"): (lambda: protocols.run_figure_4E(n_contrasts=24),
               ("attend_pref_CRF", "attend_nonpref_CRF")),
}

_GROUP_PEAK_CACHE: dict[tuple, float] = {}
_GROUP_SCALE_CACHE: dict[tuple, float] = {}


def _model_group_peak(members) -> float:
    """Max raw model response across every panel in a CRF group (n_contrasts=24)."""
    peak = 0.0
    for key in members:
        runner, (a_key, b_key) = _CRF_GROUP_SCALE_RUNNERS[key]
        r = runner()
        peak = max(peak, float(np.max(r[a_key])), float(np.max(r[b_key])))
    return peak if peak > 1e-12 else 1.0


def _crf_group_scale(panel_id: str) -> float:
    """Shared-scale divisor for ``panel_id``'s CRF group (memoized per group).

    Equals the view's ``crf_group_scale(panel_id, model_group_peak)``: the model
    group peak (this side) over the reference group peak (the view's side).
    """
    members = view.crf_group_members(panel_id)
    if members is None:
        raise KeyError(f"panel {panel_id} is not in a CRF figure-group")
    if members not in _GROUP_SCALE_CACHE:
        if members not in _GROUP_PEAK_CACHE:
            _GROUP_PEAK_CACHE[members] = _model_group_peak(members)
        _GROUP_SCALE_CACHE[members] = view.crf_group_scale(
            panel_id, _GROUP_PEAK_CACHE[members]
        )
    return _GROUP_SCALE_CACHE[members]


# ---------------------------------------------------------------------------
# Per-figure runners: produce records, then delegate rendering to the view.
# ---------------------------------------------------------------------------

def save_figure_1(output_dir: str | Path | None = None) -> Path:
    """Run the Figure-1 protocol and render via the Phase-A view. Citation: C-012"""
    record = protocols.run_figure_1()
    return view.render_figure_1(record, _output_dir(output_dir))["path"]


def render_figure_2(output_dir: str | Path | None = None) -> dict:
    """Run Figure-2 protocols and render via the Phase-A view. Citation: C-013"""
    records = {
        "2A": protocols.run_figure_2A(n_contrasts=32),
        "2B": protocols.run_figure_2B(n_contrasts=32),
    }
    return view.render_figure_2(records, _crf_group_scale("2A"), _output_dir(output_dir))


def save_figure_2(output_dir: str | Path | None = None) -> Path:
    """Backward-compatible wrapper: render Figure 2 and return only the PNG path."""
    return render_figure_2(output_dir)["path"]


def render_figure_3(output_dir: str | Path | None = None) -> dict:
    """Run Figure-3 protocols and render via the Phase-A view. Citation: C-014"""
    records = {
        "3C": protocols.run_figure_3C(n_contrasts=32),
        "3F": protocols.run_figure_3F(n_contrasts=32),
    }
    return view.render_figure_3(records, _crf_group_scale("3C"), _output_dir(output_dir))


def save_figure_3(output_dir: str | Path | None = None) -> Path:
    """Backward-compatible wrapper: render Figure 3 and return only the PNG path."""
    return render_figure_3(output_dir)["path"]


def render_figure_4(output_dir: str | Path | None = None) -> dict:
    """Run Figure-4 protocols and render via the Phase-A view. Citation: C-015"""
    records = {
        "4C": protocols.run_figure_4C(n_contrasts=24),
        "4E": protocols.run_figure_4E(n_contrasts=24),
    }
    return view.render_figure_4(records, _crf_group_scale("4C"), _output_dir(output_dir))


def save_figure_4(output_dir: str | Path | None = None) -> Path:
    """Backward-compatible wrapper: render Figure 4 and return only the PNG path."""
    return render_figure_4(output_dir)["path"]


def render_figure_5(output_dir: str | Path | None = None) -> dict:
    """Run the Figure-5 protocol and render via the Phase-A view. Citation: C-016"""
    record = protocols.run_figure_5C(n_orientations=61)
    return view.render_figure_5(record, _output_dir(output_dir))


def save_figure_5(output_dir: str | Path | None = None) -> Path:
    """Backward-compatible wrapper: render Figure 5 and return only the PNG path."""
    return render_figure_5(output_dir)["path"]


def render_figure_6(output_dir: str | Path | None = None) -> dict:
    """Run the Figure-6 protocol and render via the Phase-A view. Citation: C-017"""
    record = protocols.run_figure_6C(n_directions=73)
    return view.render_figure_6(record, _output_dir(output_dir))


def save_figure_6(output_dir: str | Path | None = None) -> Path:
    """Backward-compatible wrapper: render Figure 6 and return only the PNG path."""
    return render_figure_6(output_dir)["path"]


def render_figure_7(output_dir: str | Path | None = None) -> dict:
    """Run the Figure-7 protocol and render via the Phase-A view. Citation: C-018"""
    record = protocols.run_figure_7C(n_directions=73)
    return view.render_figure_7(record, _output_dir(output_dir))


def save_figure_7(output_dir: str | Path | None = None) -> Path:
    """Backward-compatible wrapper: render Figure 7 and return only the PNG path."""
    return render_figure_7(output_dir)["path"]


def save_all_references(output_dir: str | Path | None = None) -> list[Path]:
    """Render every digitized-reference figure (delegates to the Phase-A view)."""
    return view.save_all_references(_output_dir(output_dir))


def save_all_figures(output_dir: str | Path | None = None) -> list[Path]:
    """Render all available model-output reproductions to PNG files.

    Citation: C-012, C-013, C-014, C-015, C-016, C-017, C-018
    """
    target = _output_dir(output_dir)
    return [
        save_figure_1(target),
        save_figure_2(target),
        save_figure_3(target),
        save_figure_4(target),
        save_figure_5(target),
        save_figure_6(target),
        save_figure_7(target),
    ]


def main() -> int:
    """Command-line entry point for rendering all figure PNGs.

    Renders BOTH the implementation figures (model record → Phase-A view) and the
    digitized-reference figures (paper digitization → same view), so the
    §3b four-up comparison is available from one command.

    Assumption: a simple module entry point is sufficient for local
    reproduction runs.
    """
    paths = save_all_figures()
    paths += save_all_references()
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
