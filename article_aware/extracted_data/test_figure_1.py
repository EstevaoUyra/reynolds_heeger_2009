from __future__ import annotations

from functools import lru_cache

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols


LEFT_STIM_X = -10.0
RIGHT_STIM_X = 10.0


@lru_cache(maxsize=1)
def _figure_1_output() -> dict:
    return protocols.run_figure_1()


def _array(out: dict, key: str, *, ndim: int | None = None) -> np.ndarray:
    arr = np.asarray(out[key], dtype=float)
    if ndim is not None:
        assert arr.ndim == ndim, f"{key} should be {ndim}D, got shape {arr.shape}"
    assert np.all(np.isfinite(arr)), f"{key} contains non-finite values"
    return arr


def _nearest_index(x_grid: np.ndarray, target: float) -> int:
    return int(np.argmin(np.abs(x_grid - target)))


def _value_at(x_grid: np.ndarray, values: np.ndarray, target: float) -> float:
    return float(values[_nearest_index(x_grid, target)])


def _window_max(x_grid: np.ndarray, values: np.ndarray, lo: float, hi: float) -> float:
    mask = (x_grid >= lo) & (x_grid <= hi)
    assert np.any(mask), f"empty x-window [{lo}, {hi}]"
    return float(np.max(values[mask]))


def _window_peak_x(x_grid: np.ndarray, values: np.ndarray, lo: float, hi: float) -> float:
    mask = (x_grid >= lo) & (x_grid <= hi)
    assert np.any(mask), f"empty x-window [{lo}, {hi}]"
    indices = np.flatnonzero(mask)
    return float(x_grid[indices[int(np.argmax(values[mask]))]])


def _regions_above_fraction(
    x_grid: np.ndarray,
    values: np.ndarray,
    fraction: float,
) -> list[tuple[float, float, float]]:
    threshold = float(fraction) * float(np.max(values))
    above = np.flatnonzero(values >= threshold)
    if len(above) == 0:
        return []

    regions: list[tuple[int, int]] = []
    start = int(above[0])
    prev = int(above[0])
    for idx in map(int, above[1:]):
        if idx != prev + 1:
            regions.append((start, prev))
            start = idx
        prev = idx
    regions.append((start, prev))

    return [
        (float(x_grid[start]), float(x_grid[end]), float(x_grid[end] - x_grid[start]))
        for start, end in regions
    ]


def _stripe_widths_at_half_height(
    x_grid: np.ndarray,
    values: np.ndarray,
) -> tuple[float, float]:
    regions = _regions_above_fraction(x_grid, values, 0.5)
    assert len(regions) == 2, f"expected two half-height regions, got {regions}"
    left, right = regions
    assert left[0] < LEFT_STIM_X < left[1], f"left region misses stimulus: {left}"
    assert right[0] < RIGHT_STIM_X < right[1], f"right region misses stimulus: {right}"
    return left[2], right[2]


def _orientation_half_height_fraction(field: np.ndarray, x_index: int) -> float:
    column = np.asarray(field[:, x_index], dtype=float)
    peak = float(np.max(column))
    assert peak > 0.0
    return float(np.mean(column >= 0.5 * peak))


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-001")
def test_population_field_output_contract_and_value_ranges():
    """Protocol returns finite matched population fields with legal value ranges.

    Citation: C-005, C-006, C-009, C-012
    """
    out = _figure_1_output()
    required_keys = {
        "x_grid",
        "E_slice",
        "A_slice",
        "S_slice",
        "R_slice",
        "R_at_attended",
        "R_at_unattended",
        "E",
        "A",
        "S",
        "R",
    }
    assert required_keys.issubset(out.keys())

    x_grid = _array(out, "x_grid", ndim=1)
    assert len(x_grid) > 50
    assert np.all(np.diff(x_grid) > 0)
    assert x_grid[0] < LEFT_STIM_X < 0.0 < RIGHT_STIM_X < x_grid[-1]

    fields = {name: _array(out, name, ndim=2) for name in ("E", "A", "S", "R")}
    assert len({field.shape for field in fields.values()}) == 1
    for name in ("E_slice", "A_slice", "S_slice", "R_slice"):
        assert _array(out, name, ndim=1).shape == x_grid.shape

    assert np.all(fields["E"] >= 0.0)
    assert np.all(fields["A"] >= 1.0)
    assert np.all(fields["S"] >= 0.0)
    assert np.all(fields["R"] >= 0.0)


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-002")
def test_stimulus_drive_has_two_equal_narrow_separated_stripes():
    """E has two equal narrow peaks at the equal-contrast stimulus locations.

    Citation: C-009, C-012
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)

    left_peak = _window_max(x_grid, E_slice, -15.0, -5.0)
    right_peak = _window_max(x_grid, E_slice, 5.0, 15.0)
    assert abs(left_peak - right_peak) / max(left_peak, right_peak) < 0.03

    left_peak_x = _window_peak_x(x_grid, E_slice, -15.0, -5.0)
    right_peak_x = _window_peak_x(x_grid, E_slice, 5.0, 15.0)
    assert abs(left_peak_x - LEFT_STIM_X) <= 1.0
    assert abs(right_peak_x - RIGHT_STIM_X) <= 1.0

    left_width, right_width = _stripe_widths_at_half_height(x_grid, E_slice)
    assert 3.0 <= left_width <= 10.0
    assert 3.0 <= right_width <= 10.0

    peak = max(left_peak, right_peak)
    assert _window_max(x_grid, E_slice, -3.0, 3.0) < 0.15 * peak
    assert _window_max(x_grid, E_slice, -80.0, -40.0) < 0.01 * peak
    assert _window_max(x_grid, E_slice, 40.0, 80.0) < 0.01 * peak


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-003")
def test_stimulus_drive_is_orientation_tuned_not_full_height():
    """E stripes taper along orientation rather than filling the full panel height.

    Citation: C-009, C-011, C-012
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E = _array(out, "E", ndim=2)
    left_i = _nearest_index(x_grid, LEFT_STIM_X)
    right_i = _nearest_index(x_grid, RIGHT_STIM_X)

    left_fraction = _orientation_half_height_fraction(E, left_i)
    right_fraction = _orientation_half_height_fraction(E, right_i)
    assert 0.10 <= left_fraction <= 0.40
    assert 0.10 <= right_fraction <= 0.40
    assert abs(left_fraction - right_fraction) <= 0.05

    for idx in (left_i, right_i):
        column = E[:, idx]
        assert max(float(column[0]), float(column[-1])) < 0.05 * float(np.max(column))


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-004")
def test_attention_field_is_broad_right_centered_and_orientation_flat():
    """A is a broad right-centered spatial gain field, flat in orientation.

    Citation: C-005, C-009, C-012
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    A = _array(out, "A", ndim=2)
    A_slice = _array(out, "A_slice", ndim=1)

    assert np.min(A) >= 1.0
    assert abs(float(np.max(A)) - 2.0) <= 0.05
    assert np.max(np.ptp(A, axis=0)) <= 1e-10

    peak_x = float(x_grid[int(np.argmax(A_slice))])
    assert 5.0 <= peak_x <= 15.0
    assert _value_at(x_grid, A_slice, RIGHT_STIM_X) > _value_at(x_grid, A_slice, LEFT_STIM_X)

    enhancement = A_slice - 1.0
    enhanced_regions = _regions_above_fraction(x_grid, enhancement, 0.5)
    assert len(enhanced_regions) == 1
    assert 50.0 <= enhanced_regions[0][2] <= 90.0
    assert _value_at(x_grid, A_slice, x_grid[0]) <= 1.05
    assert _value_at(x_grid, A_slice, x_grid[-1]) <= 1.05


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-005")
def test_suppressive_drive_has_two_separable_broad_bands():
    """S contains two broad but distinct bands, with a visible gap between them.

    Citation: C-006, C-010, C-011, C-012
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)
    S_slice = _array(out, "S_slice", ndim=1)

    e_left_width, e_right_width = _stripe_widths_at_half_height(x_grid, E_slice)
    s_regions = _regions_above_fraction(x_grid, S_slice, 0.5)
    assert len(s_regions) == 2, f"S should have two separated bands, got {s_regions}"
    left_region, right_region = s_regions
    assert left_region[0] < LEFT_STIM_X < left_region[1]
    assert right_region[0] < RIGHT_STIM_X < right_region[1]
    assert left_region[2] >= 2.0 * e_left_width
    assert right_region[2] >= 2.0 * e_right_width

    left_peak = _window_max(x_grid, S_slice, -18.0, -2.0)
    right_peak = _window_max(x_grid, S_slice, 2.0, 18.0)
    center_gap = _window_max(x_grid, S_slice, -3.0, 3.0)
    assert center_gap <= 0.75 * min(left_peak, right_peak)
    assert right_peak >= 1.10 * left_peak


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-006")
def test_suppressive_drive_spreads_across_orientation_axis():
    """S bands extend across nearly the full orientation axis.

    Citation: C-006, C-011
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    S = _array(out, "S", ndim=2)

    for target in (LEFT_STIM_X, RIGHT_STIM_X):
        column = S[:, _nearest_index(x_grid, target)]
        peak = float(np.max(column))
        assert peak > 0.0
        assert float(np.min(column)) >= 0.20 * peak
        assert np.mean(column >= 0.5 * peak) >= 0.80


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-007")
def test_population_response_has_two_narrow_stripes_at_stimulus_locations():
    """R has two narrow stripes at the E locations, not broad S-like bands.

    Citation: C-005, C-012
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)
    S_slice = _array(out, "S_slice", ndim=1)
    R_slice = _array(out, "R_slice", ndim=1)

    e_left_width, e_right_width = _stripe_widths_at_half_height(x_grid, E_slice)
    r_left_width, r_right_width = _stripe_widths_at_half_height(x_grid, R_slice)
    assert r_left_width <= 1.50 * e_left_width
    assert r_right_width <= 1.50 * e_right_width

    s_regions = _regions_above_fraction(x_grid, S_slice, 0.5)
    if len(s_regions) == 2:
        assert s_regions[0][2] >= 2.0 * r_left_width
        assert s_regions[1][2] >= 2.0 * r_right_width

    peak = float(np.max(R_slice))
    assert _window_max(x_grid, R_slice, -3.0, 3.0) < 0.15 * peak
    assert _window_max(x_grid, R_slice, -80.0, -40.0) < 0.01 * peak
    assert _window_max(x_grid, R_slice, 40.0, 80.0) < 0.01 * peak


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-008")
def test_population_response_is_asymmetric_but_unattended_stripe_remains_visible():
    """The attended right R stripe is brighter, while the left stripe remains visible.

    Citation: C-005, C-012, C-021
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    R_slice = _array(out, "R_slice", ndim=1)

    left_peak = _window_max(x_grid, R_slice, -15.0, -5.0)
    right_peak = _window_max(x_grid, R_slice, 5.0, 15.0)
    assert right_peak >= 1.20 * left_peak
    assert left_peak >= 0.10 * right_peak
    assert out["R_at_attended"] >= 1.20 * out["R_at_unattended"]


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-009")
def test_attention_introduces_asymmetry_after_symmetric_stimulus_drive():
    """E is symmetric, but S and R are right-biased by attention.

    Citation: C-005, C-006, C-012
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)
    S_slice = _array(out, "S_slice", ndim=1)
    R_slice = _array(out, "R_slice", ndim=1)

    e_left = _window_max(x_grid, E_slice, -15.0, -5.0)
    e_right = _window_max(x_grid, E_slice, 5.0, 15.0)
    s_left = _window_max(x_grid, S_slice, -18.0, -2.0)
    s_right = _window_max(x_grid, S_slice, 2.0, 18.0)
    r_left = _window_max(x_grid, R_slice, -15.0, -5.0)
    r_right = _window_max(x_grid, R_slice, 5.0, 15.0)

    assert abs(e_left - e_right) / max(e_left, e_right) < 0.03
    assert s_right >= 1.10 * s_left
    assert r_right >= 1.20 * r_left


@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-010")
def test_population_response_orientation_tuning_tracks_stimulus_drive_not_suppression():
    """R is orientation-localized like E, unlike the broad orientation spread of S.

    Citation: C-005, C-006, C-011
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E = _array(out, "E", ndim=2)
    S = _array(out, "S", ndim=2)
    R = _array(out, "R", ndim=2)

    for target in (LEFT_STIM_X, RIGHT_STIM_X):
        idx = _nearest_index(x_grid, target)
        e_fraction = _orientation_half_height_fraction(E, idx)
        s_fraction = _orientation_half_height_fraction(S, idx)
        r_fraction = _orientation_half_height_fraction(R, idx)
        assert r_fraction <= 1.50 * e_fraction
        assert s_fraction >= 2.0 * e_fraction
        assert s_fraction >= 2.0 * r_fraction
