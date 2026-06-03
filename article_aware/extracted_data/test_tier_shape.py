"""Mechanical dozen-point SHAPE check (WORKFLOW.md §3b).

For every digitized curve of every panel, require the IMPLEMENTATION curve to
pass within tolerance of each digitized point across the x-range — the "dozen
points along the line" shape backbone. Generated MECHANICALLY from the digitized
JSON (one soft test per panel, looping its curves), NOT from agent-chosen
scalars: this is what closes the gap the worked example exposed, where Figs 2/3
passed every endpoint-scalar hard test while their curve SHAPE diverged
(2A max|Δ|~0.22, 3C max|Δ|~0.29 vs the digitized reference).

SOFT tier by default (human decision, WORKFLOW §3b): always measured & reported,
never blocks. A human promotes a panel's shape check to a hard gate with a
one-line tier flip once the digitization for that panel is trusted.
"""

from __future__ import annotations

from rh_tier_helpers import ALL_PANELS, load_digitized, shape_deviation, tier_test

LEFT_TOL = 0.05   # normalized-axis units (fraction of full 0-1 left axis)
PCT_TOL = 10.0    # percent-axis units (right axis, 0-100)


def _make_shape_test(figure: int, panel: str):
    @tier_test(tier="soft", spec_ref=f"figures.figure_{figure}.panel_{panel}",
               figure=figure, claim_id=f"T-{figure}{panel}-S-shape")
    def _test():
        curves = load_digitized(figure, panel)["curves"]
        reports, ok_flags = [], []
        for name, cd in curves.items():
            tol = PCT_TOL if cd.get("axis") == "right" else LEFT_TOL
            mx, mean, at_x = shape_deviation(figure, panel, name)
            ok = mx <= tol
            ok_flags.append(ok)
            reports.append(
                f"{name}: max|Δ|={mx:.3f}@x={at_x:g} mean={mean:.3f} "
                f"tol={tol:g} {'ok' if ok else 'OFF'}")
        assert all(ok_flags), (
            f"shape vs digitized dozen points, panel {figure}{panel} — "
            + " | ".join(reports))

    _test.__name__ = f"test_{figure}{panel}_shape_matches_digitized_dozen_points"
    _test.__qualname__ = _test.__name__
    _test.__doc__ = (
        f"SOFT: implementation curve(s) of panel {figure}{panel} stay within "
        f"tolerance of every digitized point (shape, not just endpoints).")
    return _test


for _figure, _panel in ALL_PANELS:
    _shape_test = _make_shape_test(_figure, _panel)
    globals()[_shape_test.__name__] = _shape_test

del _figure, _panel, _shape_test
