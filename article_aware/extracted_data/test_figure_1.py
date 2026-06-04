"""Figure 1 — four RENDERED population fields (E, A, S, R), MUST-PASS.

Encodes the contract correction of commit 60f700a ("Re-scope Figure 1: four
E/A/S/R fields are rendered model outputs, not a schematic") and its binding
config CODE-019 (the authors' own Test/debug `R1` call in attentionModel.m).
This is the CONTRACT change being authored into tests per author-tests/SKILL.md.

WHY MUST-PASS (not a fit target). Every claim below is a STRUCTURAL consequence
of running the authors' published CODE-019 configuration through the FAITHFUL
mechanism — there is no free magnitude to tune:

  * Geometry is fixed by CODE-019: two equal-contrast vertical gratings at
    x = ±100 on a grid x ∈ [−200, 200] (401 samples), θ ∈ [−180, 180];
    attention on the RIGHT (Ax = +100), AxWidth = 30, peak gain γ = 2
    (Apeak, CODE-015/C-012), baseline 1 (Abase); stimulation σ_x = 5 / σ_θ = 60,
    suppressive IxWidth = 20 and IthetaWidth = 360 (near-flat θ pool, CODE-011),
    sigma = 1e-6 (CODE-014). No per-panel knob exists in the code.
  * The KEY CORRECTION of the re-scope: the rendered "Stimulus drive" box is
    `Eraw` (PRE-attention, attentionModel.m:200), so E is left/right SYMMETRIC.
    The attention asymmetry (right brighter) appears ONLY in S and R, which use
    E = attnGain·Eraw. A render where E is already brighter on the right has
    shown the wrong quantity. (figure_1.md relations #1, #2.)
  * The broad-θ suppressive pool (IthetaWidth = 360, CODE-011) and σ ≈ 0
    (CODE-014) are the SQ-005 suppression-fix values, settled from the original
    author code (logs/spec_questions.md SQ-005 human_resolution, 2026-06-04).
    The S and R renders are the paper-image check on exactly those values: S
    spans the full orientation height (broad-θ pool), R does not (it tracks E).

These are satisfiable by the correct mechanism alone — they assert the SHAPE and
SIGN relationships the authors' config produces, with the only absolute anchors
(stim at ±100, grid [−200, 200], peak A = 2, A-floor = 1) read directly from
CODE-019 / the caption ("Midgray indicates a value of 1, white > 1"). They
CANNOT be greened by tuning a suppression magnitude.

Evaluated on the implementation's Figure-1 measurement record
(protocols.run_figure_1 → measurements.figure_1_record), NOT on any digitized
curve — a mechanism-fidelity check, not a self-consistency tautology.

STATUS NOTE FOR THE FIX PASS: the implementation's figure_1 protocol/ledger
still carries the PRE-rescope geometry (stim at ±10, recorded_x = 10,
sigma = 1.5, ad-hoc *_sigma_scale fudge factors) and there is a pre-existing
ledger collision (figure_3C.baseline_unmodulated defined in both ledgers) that
makes calibration.resolve raise. So these tests are RED today by construction;
they flip green when the fix pass rebuilds run_figure_1 to CODE-019 (stim ±100,
grid [−200,200], γ=2, IxWidth=20, IthetaWidth=360, sigma=1e-6) and clears the
ledger collision. That is the must-pass target this file pins.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import pytest

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols


# The R-asymmetry the authors' own CODE-019 arithmetic produces (verified by a
# numpy reproduction of attentionModel.m: R_right/R_left ≈ 1.013 at the recorded
# θ=0 row). See the GENUINE-DIVERGENCE note on the tripwire tests below.
CODE019_R_RIGHT_OVER_LEFT = 1.013


# --- CODE-019 absolute geometry anchors (read from the authors' code) ----------
# Two equal-contrast gratings; attended on the RIGHT.
CODE019_LEFT_STIM_X = -100.0
CODE019_RIGHT_STIM_X = 100.0
CODE019_GRID_MIN = -200.0
CODE019_GRID_MAX = 200.0
CODE019_PEAK_ATTENTION_GAIN = 2.0   # Apeak (CODE-015 / C-012)
CODE019_ATTENTION_BASELINE = 1.0    # Abase (caption: midgray = 1)
# Half-window (in x units) used to localize each stimulus' peak. With stimuli
# 200 samples apart and the broadest pool σ = 20, ±40 cleanly isolates a side.
SIDE_HALFWIN = 40.0


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


def _left_window(x: float = CODE019_LEFT_STIM_X) -> tuple[float, float]:
    return (x - SIDE_HALFWIN, x + SIDE_HALFWIN)


def _right_window(x: float = CODE019_RIGHT_STIM_X) -> tuple[float, float]:
    return (x - SIDE_HALFWIN, x + SIDE_HALFWIN)


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


def _side_width_at_own_half_peak(
    x_grid: np.ndarray,
    values: np.ndarray,
    center: float,
    halfwin: float = SIDE_HALFWIN,
) -> float:
    """Width of ONE band, measured at half of that band's OWN local peak.

    Robust to left/right asymmetry: a dim left band and a bright right band are
    each measured relative to their own peak, so a global-max threshold does not
    truncate the dimmer band's apparent width. Returns the contiguous extent
    around ``center`` that lies above 0.5 × (local peak within ±halfwin).
    """
    mask = (x_grid >= center - halfwin) & (x_grid <= center + halfwin)
    assert np.any(mask), f"empty window around {center}"
    local_peak = float(np.max(values[mask]))
    assert local_peak > 0.0
    above = values >= 0.5 * local_peak
    c_idx = _nearest_index(x_grid, center)
    assert above[c_idx], f"center {center} not above its own half-peak"
    lo = c_idx
    while lo - 1 >= 0 and above[lo - 1]:
        lo -= 1
    hi = c_idx
    while hi + 1 < len(x_grid) and above[hi + 1]:
        hi += 1
    return float(x_grid[hi] - x_grid[lo])


def _e_stripe_widths(x_grid: np.ndarray, E_slice: np.ndarray) -> tuple[float, float]:
    """E's two stripe widths (E is symmetric, so a global threshold is fine)."""
    regions = _regions_above_fraction(x_grid, E_slice, 0.5)
    assert len(regions) == 2, f"expected two half-height E regions, got {regions}"
    left, right = regions
    assert left[0] < CODE019_LEFT_STIM_X < left[1], f"left region misses stimulus: {left}"
    assert right[0] < CODE019_RIGHT_STIM_X < right[1], f"right region misses stimulus: {right}"
    return left[2], right[2]


def _orientation_half_height_fraction(field: np.ndarray, x_index: int) -> float:
    column = np.asarray(field[:, x_index], dtype=float)
    peak = float(np.max(column))
    assert peak > 0.0
    return float(np.mean(column >= 0.5 * peak))


# ------------------------------------------------------------------------------
# Q-001 — output contract + CODE-019 geometry
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-001")
def test_population_field_output_contract_and_code019_geometry():
    """Protocol returns finite matched fields on the CODE-019 grid with legal ranges.

    The re-scope binds Figure 1 to the authors' code (CODE-019): grid
    x ∈ [−200, 200], two equal gratings at x = ±100, attention on the right.

    Citation: C-005, C-006, C-009, C-012 ; Code: CODE-019, CODE-011, CODE-014
    """
    out = _figure_1_output()
    required_keys = {
        "x_grid", "E_slice", "A_slice", "S_slice", "R_slice",
        "R_at_attended", "R_at_unattended", "E", "A", "S", "R",
    }
    assert required_keys.issubset(out.keys())

    x_grid = _array(out, "x_grid", ndim=1)
    assert len(x_grid) > 50
    assert np.all(np.diff(x_grid) > 0)
    # CODE-019 grid spans [−200, 200]; the two stimuli sit at x = ±100, each at
    # the half-way point between center and edge (NOT flush at the edge).
    assert x_grid[0] <= CODE019_GRID_MIN + 1.0
    assert x_grid[-1] >= CODE019_GRID_MAX - 1.0
    assert x_grid[0] < CODE019_LEFT_STIM_X < 0.0 < CODE019_RIGHT_STIM_X < x_grid[-1]

    fields = {name: _array(out, name, ndim=2) for name in ("E", "A", "S", "R")}
    assert len({field.shape for field in fields.values()}) == 1
    for name in ("E_slice", "A_slice", "S_slice", "R_slice"):
        assert _array(out, name, ndim=1).shape == x_grid.shape

    assert np.all(fields["E"] >= 0.0)
    assert np.all(fields["A"] >= CODE019_ATTENTION_BASELINE - 1e-6)
    assert np.all(fields["S"] >= 0.0)
    assert np.all(fields["R"] >= 0.0)


# ------------------------------------------------------------------------------
# Q-002 — E: two equal, narrow, separated stripes at x = ±100
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-002")
def test_stimulus_drive_has_two_equal_narrow_stripes_at_pm100():
    """E (Eraw) has two EQUAL narrow peaks at x = ±100, well separated.

    figure_1.md relation #1: E is rendered pre-attention, so its two stripes are
    EQUAL in brightness. Stimulus σ_x = 5 broadened by stimulation σ_x = 5 makes
    each stripe narrow relative to the 401-wide x-axis (centers 200 apart).

    Citation: C-009, C-012 ; Code: CODE-019, CODE-012
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)

    left_peak = _window_max(x_grid, E_slice, *_left_window())
    right_peak = _window_max(x_grid, E_slice, *_right_window())
    # E is Eraw (pre-attention) → left/right SYMMETRIC (key correction).
    assert abs(left_peak - right_peak) / max(left_peak, right_peak) < 0.05

    left_peak_x = _window_peak_x(x_grid, E_slice, *_left_window())
    right_peak_x = _window_peak_x(x_grid, E_slice, *_right_window())
    assert abs(left_peak_x - CODE019_LEFT_STIM_X) <= 5.0
    assert abs(right_peak_x - CODE019_RIGHT_STIM_X) <= 5.0

    # Narrow stripes: σ ≈ sqrt(5² + 5²) ≈ 7 → half-height width an order of
    # magnitude below the 400-wide axis, and far below the 200-sample separation.
    left_width, right_width = _e_stripe_widths(x_grid, E_slice)
    assert 3.0 <= left_width <= 40.0
    assert 3.0 <= right_width <= 40.0

    peak = max(left_peak, right_peak)
    # Dark gap between the stripes, and near-black background away from stimuli.
    assert _window_max(x_grid, E_slice, -20.0, 20.0) < 0.20 * peak
    assert _window_max(x_grid, E_slice, -190.0, -150.0) < 0.02 * peak
    assert _window_max(x_grid, E_slice, 150.0, 190.0) < 0.02 * peak


# ------------------------------------------------------------------------------
# Q-003 — E: orientation-tuned (tapers in θ), not full panel height
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-003")
def test_stimulus_drive_is_orientation_tuned_not_full_height():
    """E stripes taper along orientation (σ_θ = 60), not filling the panel height.

    Citation: C-009, C-012, C-013 ; Code: CODE-013
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E = _array(out, "E", ndim=2)
    left_i = _nearest_index(x_grid, CODE019_LEFT_STIM_X)
    right_i = _nearest_index(x_grid, CODE019_RIGHT_STIM_X)

    left_fraction = _orientation_half_height_fraction(E, left_i)
    right_fraction = _orientation_half_height_fraction(E, right_i)
    # Bounded θ band: clearly less than full height, clearly more than a single row.
    assert 0.02 <= left_fraction <= 0.60
    assert 0.02 <= right_fraction <= 0.60
    # E is pre-attention and attention is θ-flat, so the two columns' θ-extent matches.
    assert abs(left_fraction - right_fraction) <= 0.05

    for idx in (left_i, right_i):
        column = E[:, idx]
        # Tapers toward the orientation extremes (top/bottom rows are dim).
        assert max(float(column[0]), float(column[-1])) < 0.10 * float(np.max(column))


# ------------------------------------------------------------------------------
# Q-004 — A: broad right-centered spatial gain, flat in θ, peak 2 / floor 1
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-004")
def test_attention_field_is_broad_right_centered_orientation_flat_peak2():
    """A is a γ=2 right-centered (x=+100, σ=30) spatial gain, flat in θ, floor 1.

    Caption: "Midgray indicates a value of 1 and white indicates a value greater
    than 1" → A ∈ [1 (Abase), 2 (Apeak)], never black. "attentional gain varied
    as a function of stimulus position, without regard to orientation" → flat in θ.

    Citation: C-005, C-009, C-012 ; Code: CODE-019, CODE-015
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    A = _array(out, "A", ndim=2)
    A_slice = _array(out, "A_slice", ndim=1)

    # Floor = baseline 1 (midgray), peak = γ = 2 (white). Never below 1.
    assert np.min(A) >= CODE019_ATTENTION_BASELINE - 1e-6
    assert abs(float(np.max(A)) - CODE019_PEAK_ATTENTION_GAIN) <= 0.05
    # Flat in orientation: every row identical at a given x (no θ gradient).
    assert np.max(np.ptp(A, axis=0)) <= 1e-9

    # Right-centered Gaussian bump at x ≈ +100; left half at baseline.
    peak_x = float(x_grid[int(np.argmax(A_slice))])
    assert abs(peak_x - CODE019_RIGHT_STIM_X) <= 15.0
    assert _value_at(x_grid, A_slice, CODE019_RIGHT_STIM_X) > _value_at(
        x_grid, A_slice, CODE019_LEFT_STIM_X
    )

    # Single enhanced region (a Gaussian bump, not a step/ramp-to-edge); it
    # returns toward baseline before the right edge.
    enhancement = A_slice - CODE019_ATTENTION_BASELINE
    enhanced_regions = _regions_above_fraction(x_grid, enhancement, 0.5)
    assert len(enhanced_regions) == 1
    # σ = 30 → half-height width ≈ 2.355·30 ≈ 70 (one bump, not the whole axis).
    assert 30.0 <= enhanced_regions[0][2] <= 130.0
    assert _value_at(x_grid, A_slice, x_grid[0]) <= 1.05
    assert _value_at(x_grid, A_slice, x_grid[-1]) <= 1.05


# ------------------------------------------------------------------------------
# Q-005 — S: two broad bands, right brighter, separable (attention enters here)
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-005")
def test_suppressive_drive_has_two_broad_bands_right_brighter():
    """S has two broad (σ_x=20) bands; the RIGHT band is brighter (attention).

    figure_1.md relations #2, #3: S uses E = attnGain·Eraw, so attention (×2 on
    the right) makes the right band brighter — the asymmetry first appears HERE.
    The σ_x = 20 spatial pool smears each narrow E stripe into a broad band.

    Citation: C-006, C-010, C-012 ; Code: CODE-010
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)
    S_slice = _array(out, "S_slice", ndim=1)

    e_left_width, e_right_width = _e_stripe_widths(x_grid, E_slice)
    # Per-band widths (each band relative to its OWN local peak): robust to the
    # left band being dimmer than the right (attention makes the right ~2× — a
    # global-max threshold would truncate the dim left band's apparent width).
    s_left_width = _side_width_at_own_half_peak(x_grid, S_slice, CODE019_LEFT_STIM_X)
    s_right_width = _side_width_at_own_half_peak(x_grid, S_slice, CODE019_RIGHT_STIM_X)
    # S bands are substantially wider in x than E stripes (σ 20 vs ≈7).
    assert s_left_width >= 1.5 * e_left_width
    assert s_right_width >= 1.5 * e_right_width

    left_peak = _window_max(x_grid, S_slice, *_left_window())
    right_peak = _window_max(x_grid, S_slice, *_right_window())
    center_gap = _window_max(x_grid, S_slice, -20.0, 20.0)
    assert center_gap <= 0.85 * min(left_peak, right_peak)
    # Attention asymmetry FIRST APPEARS in S: the right band is brighter than the
    # left (attention multiplies the right drive by ~γ=2 before pooling). The
    # authors' CODE-019 arithmetic gives S_right/S_left ≈ 1.98 — well above 1.10.
    assert right_peak >= 1.10 * left_peak


# ------------------------------------------------------------------------------
# Q-006 — S: near-flat across the full orientation axis (broad-θ pool, CODE-011)
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-006")
def test_suppressive_drive_spans_full_orientation_axis_broad_theta_pool():
    """S spans the FULL orientation height, nearly uniform — IthetaWidth = 360.

    This is the direct visual signature of the SQ-005 suppression-fix value
    IthetaWidth = 360 (CODE-011, near-flat θ pool, settled from author code):
    each S band fills the whole vertical extent of the panel. A narrow θ pool
    (e.g. σ_θ = 30) would FAIL this — the band would be θ-bounded like E.

    Citation: C-006, C-011 ; Code: CODE-011
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    S = _array(out, "S", ndim=2)

    for target in (CODE019_LEFT_STIM_X, CODE019_RIGHT_STIM_X):
        column = S[:, _nearest_index(x_grid, target)]
        peak = float(np.max(column))
        assert peak > 0.0
        # Near-flat top-to-bottom: minimum row ≥ 20% of peak; ≥80% of rows ≥ half-peak.
        assert float(np.min(column)) >= 0.20 * peak
        assert np.mean(column >= 0.5 * peak) >= 0.80


# ------------------------------------------------------------------------------
# Q-007 — R: two narrow stripes (E width, NOT S width)
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-007")
def test_population_response_has_two_narrow_stripes_like_E_not_S():
    """R stripes are narrow like E (not broadened to the S-band width).

    figure_1.md relation #5: R = E/(I+σ); dividing the localized numerator A·E by
    the broad smooth S does not widen the peaks, so R width ≈ E width ≪ S width.
    If R is as wide as the S bands, the division by S is wrong.

    Citation: C-005, C-012 ; Code: CODE-014
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)
    S_slice = _array(out, "S_slice", ndim=1)
    R_slice = _array(out, "R_slice", ndim=1)

    e_left_width, e_right_width = _e_stripe_widths(x_grid, E_slice)
    r_left_width = _side_width_at_own_half_peak(x_grid, R_slice, CODE019_LEFT_STIM_X)
    r_right_width = _side_width_at_own_half_peak(x_grid, R_slice, CODE019_RIGHT_STIM_X)
    assert r_left_width <= 1.50 * e_left_width
    assert r_right_width <= 1.50 * e_right_width

    # The right S band (per its own peak) is far wider than the R stripe.
    s_right_width = _side_width_at_own_half_peak(x_grid, S_slice, CODE019_RIGHT_STIM_X)
    assert s_right_width >= 1.5 * r_right_width

    peak = float(np.max(R_slice))
    assert _window_max(x_grid, R_slice, -20.0, 20.0) < 0.20 * peak
    assert _window_max(x_grid, R_slice, -190.0, -150.0) < 0.02 * peak
    assert _window_max(x_grid, R_slice, 150.0, 190.0) < 0.02 * peak


# ------------------------------------------------------------------------------
# Q-008a — R: both stripes present, left survives (no winner-take-all) — MUST-PASS
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-008a")
def test_population_response_left_stripe_survives_no_winner_take_all():
    """The unattended (left) R stripe is present and comparable — not suppressed away.

    figure_1.md relation #6: normalization REDUCES the unattended response, it is
    NOT winner-take-all — a visible left stripe at x = −100 must remain in R. This
    no-WTA property holds under the faithful CODE-019 mechanism (R_left ≈ R_right),
    so it is MUST-PASS. (The SEPARATE claim that the right stripe is *noticeably
    brighter* is a divergence — see the Q-008b tripwire below.)

    Citation: C-005, C-012, C-021 ; Code: CODE-019
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    R_slice = _array(out, "R_slice", ndim=1)

    left_peak = _window_max(x_grid, R_slice, *_left_window())
    right_peak = _window_max(x_grid, R_slice, *_right_window())
    # Left stripe survives at a magnitude comparable to the right (no WTA).
    assert left_peak >= 0.50 * right_peak
    assert out["R_at_unattended"] >= 0.50 * out["R_at_attended"]
    # Right is at least not DIMMER than left (attention does not invert the order).
    assert right_peak >= 0.98 * left_peak
    assert out["R_at_attended"] >= 0.98 * out["R_at_unattended"]


# ------------------------------------------------------------------------------
# Q-008b — TRIPWIRE (GENUINE-DIVERGENCE): "R right NOTICEABLY brighter"
# ------------------------------------------------------------------------------
@pytest.mark.xfail(
    strict=True,
    reason=(
        "GENUINE-DIVERGENCE vs the authors' OWN CODE-019 arithmetic. figure_1.md "
        "relation #6 / the caption assert the attended (right) R stripe is "
        "'noticeably brighter' than the left. A numpy reproduction of "
        "attentionModel.m (R = E/(I+σ), σ=1e-6, IthetaWidth=360, attend right) "
        "gives R_right/R_left ≈ 1.013 — essentially SYMMETRIC: at high contrast "
        "attention scales the numerator (A·E) and the pooled denominator (I, which "
        "pools A·E) nearly proportionally, so the response-gain modulation almost "
        "cancels in R even though it is plainly visible (≈1.98×) in S. The faithful "
        "mechanism does NOT make R noticeably right-brighter, so requiring ≥1.10 is "
        "an INTENDED FAILURE that flips green only if a future model genuinely "
        "produces stronger R asymmetry — never a fit target. FLAGGED: the contract "
        "(figure_1.md) overstates the R asymmetry relative to the code it cites."
    ),
)
@deterministic_test(
    spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-008b",
    paper_issue="Fig1-R-asymmetry-overstated-vs-CODE-019",
)
def test_population_response_right_noticeably_brighter_TRIPWIRE():
    """TRIPWIRE: R_right ≥ 1.10 × R_left. Author code gives ≈1.013 — RED by design."""
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    R_slice = _array(out, "R_slice", ndim=1)
    left_peak = _window_max(x_grid, R_slice, *_left_window())
    right_peak = _window_max(x_grid, R_slice, *_right_window())
    assert right_peak >= 1.10 * left_peak
    assert out["R_at_attended"] >= 1.10 * out["R_at_unattended"]


# ------------------------------------------------------------------------------
# Q-009 — KEY CORRECTION: E symmetric, asymmetry first appears in S — MUST-PASS
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-009")
def test_attention_asymmetry_is_absent_in_E_and_first_appears_in_S():
    """E is left/right SYMMETRIC; the attention asymmetry first appears in S.

    THE KEY CORRECTION of the re-scope (figure_1.md relations #1/#2): the rendered
    Stimulus-Drive box is Eraw (PRE-attention) → SYMMETRIC. Attention enters via
    E = attnGain·Eraw, which feeds S (and R), so right > left appears in S and must
    be ABSENT in E. A render where E is already right-biased has shown the wrong
    quantity (attnGain·Eraw instead of Eraw). The S asymmetry is reproduced by the
    faithful CODE-019 mechanism (S_right/S_left ≈ 1.98), so this is MUST-PASS.

    NOTE: the contract also claims R is right-biased; the authors' code gives R
    nearly SYMMETRIC (≈1.013), so that R claim is the Q-008b TRIPWIRE, not here.

    Citation: C-005, C-006, C-012 ; Code: CODE-019
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E_slice = _array(out, "E_slice", ndim=1)
    S_slice = _array(out, "S_slice", ndim=1)

    e_left = _window_max(x_grid, E_slice, *_left_window())
    e_right = _window_max(x_grid, E_slice, *_right_window())
    s_left = _window_max(x_grid, S_slice, *_left_window())
    s_right = _window_max(x_grid, S_slice, *_right_window())

    # E symmetric (asymmetry NOT yet entered) ...
    assert abs(e_left - e_right) / max(e_left, e_right) < 0.05
    # ... but S is right-biased (attention enters through E = attnGain·Eraw).
    assert s_right >= 1.10 * s_left


# ------------------------------------------------------------------------------
# Q-010 — R orientation tuning tracks E (localized), NOT the broad-θ S
# ------------------------------------------------------------------------------
@deterministic_test(spec_ref="simulation_protocols.figure_1", figure=1, claim_id="Q-010")
def test_population_response_orientation_tuning_tracks_E_not_S():
    """R is orientation-localized like E, unlike the broad-θ spread of S.

    figure_1.md relation #4/#5: S fills the orientation axis (IthetaWidth = 360),
    but R = E/(I+σ) collapses back to E's localized θ-band — R's θ-extent ≈ E's,
    and far below S's. A telltale that R divides by the broad S yet keeps E's
    feature tuning.

    Citation: C-005, C-006, C-011 ; Code: CODE-011, CODE-014
    """
    out = _figure_1_output()
    x_grid = _array(out, "x_grid", ndim=1)
    E = _array(out, "E", ndim=2)
    S = _array(out, "S", ndim=2)
    R = _array(out, "R", ndim=2)

    for target in (CODE019_LEFT_STIM_X, CODE019_RIGHT_STIM_X):
        idx = _nearest_index(x_grid, target)
        e_fraction = _orientation_half_height_fraction(E, idx)
        s_fraction = _orientation_half_height_fraction(S, idx)
        r_fraction = _orientation_half_height_fraction(R, idx)
        assert r_fraction <= 1.50 * e_fraction      # R tracks E
        assert s_fraction >= 2.0 * e_fraction        # S far broader in θ than E
        assert s_fraction >= 2.0 * r_fraction        # ... and than R
