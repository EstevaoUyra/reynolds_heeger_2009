from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols


EXPECTED_KEYS = {
    "attended_CRF",
    "unattended_CRF",
    "percent_modulation",
    "absolute_difference",
    "c",
}


def _arrays(out: dict[str, np.ndarray]) -> tuple[np.ndarray, ...]:
    c = np.asarray(out["c"], dtype=float)
    attended = np.asarray(out["attended_CRF"], dtype=float)
    unattended = np.asarray(out["unattended_CRF"], dtype=float)
    percent = np.asarray(out["percent_modulation"], dtype=float)
    difference = np.asarray(out["absolute_difference"], dtype=float)
    return c, attended, unattended, percent, difference


def _assert_monotonic_and_saturating(curve: np.ndarray) -> None:
    increments = np.diff(curve)
    total_rise = float(curve[-1] - curve[0])
    assert np.all(increments >= -1e-10)
    assert total_rise > 0.0
    assert increments[-1] < 0.35 * total_rise


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-019")
def test_protocol_output_contract_and_curve_shapes():
    """Figure 3F returns finite same-shaped log-contrast protocol arrays.

    Citation: C-014
    """
    out = protocols.run_figure_3F()
    assert EXPECTED_KEYS.issubset(out.keys())
    c, attended, unattended, percent, difference = _arrays(out)
    assert c.ndim == 1
    assert attended.shape == unattended.shape == percent.shape == difference.shape == c.shape
    assert len(c) >= 6
    assert np.all(np.isfinite(c))
    assert np.all(np.isfinite(attended))
    assert np.all(np.isfinite(unattended))
    assert np.all(np.isfinite(percent))
    assert np.all(np.isfinite(difference))
    assert np.all(c > 0.0)
    assert np.all(np.diff(c) > 0.0)
    np.testing.assert_allclose(np.diff(np.log(c)), np.diff(np.log(c))[0], rtol=0.08)


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-020")
def test_reported_modulation_and_difference_match_crfs():
    """Figure 3F modulation outputs are derived from attended and unattended CRFs.

    Citation: C-014
    """
    out = protocols.run_figure_3F()
    _, attended, unattended, percent, difference = _arrays(out)
    expected_difference = attended - unattended
    np.testing.assert_allclose(difference, expected_difference, rtol=1e-7, atol=1e-9)
    np.testing.assert_allclose(
        percent,
        100.0 * expected_difference / unattended,
        rtol=1e-7,
        atol=1e-9,
    )


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-021")
def test_attended_and_unattended_crfs_have_baseline_and_saturate():
    """Figure 3F CRFs are positive, monotonic, saturating, and attention ordered.

    Citation: C-020 C-021
    """
    out = protocols.run_figure_3F()
    _, attended, unattended, _, _ = _arrays(out)
    assert attended[0] > 0.0
    assert unattended[0] > 0.0
    assert np.all(attended >= unattended)
    _assert_monotonic_and_saturating(attended)
    _assert_monotonic_and_saturating(unattended)


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-022")
def test_absolute_difference_peaks_above_modulation_and_stays_elevated():
    """Figure 3F absolute response difference peaks at intermediate contrast
    (ABOVE the low-contrast %-modulation peak) and stays substantially elevated
    at high contrast.

    The prior assertion ``peak >= len//2`` ("absolute difference peaks in the
    HIGH-contrast half") was a CLIPPED-WINDOW ARTIFACT and is REFUTED by the
    panel's own digitized data: over the corrected author window [1e-5, 1]
    (CODE-020), the 3F absolute difference peaks at INTERMEDIATE contrast
    (c ~ 1e-3, the lower-middle of the five-decade sweep), exactly where the
    DIGITIZED 3F reference peaks (c ~ 1.3e-3). 3F (Williford & Maunsell) is the
    contrast-gain-weighted panel — %-mod peaks LOW (panel_F.md) and the absolute
    separation peaks just ABOVE it, then stays high (last/peak ~0.83 in both the
    model and the digitized reference), it does NOT concentrate in the
    high-contrast half. The faithful claim, consistent with the digitized data:
    abs-diff peaks above the %-mod peak and remains elevated at high contrast.

    Citation: C-014, C-019; CODE-020 (Figure3F.m cRange); panel_F_digitized.json
    (abs-diff peak c ~1.3e-3, last/peak ~0.83)
    """
    out = protocols.run_figure_3F()
    c, _, _, percent, difference = _arrays(out)
    peak = int(np.argmax(difference))
    # abs-diff peak sits ABOVE the low-contrast %-modulation peak ...
    assert c[peak] > c[int(np.argmax(percent))]
    # ... and is NOT at the very low-contrast foot (it is an interior peak).
    assert peak > 0
    # stays substantially elevated through high contrast (digitized last/peak ~0.83).
    assert difference[-1] > difference[0]
    assert difference[-1] >= 0.75 * float(difference[peak])


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-023")
def test_percent_modulation_peaks_low_not_high():
    """Figure 3F percent modulation peaks low and declines toward high contrast.

    Citation: C-014
    """
    out = protocols.run_figure_3F()
    _, _, _, percent, _ = _arrays(out)
    peak = int(np.argmax(percent))
    assert peak < len(percent) // 2
    assert peak != len(percent) - 1
    assert percent[-1] < float(percent[peak])
    assert percent[-1] > 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-024")
def test_absolute_and_percent_peaks_are_separated():
    """Figure 3F absolute-difference peak is at higher contrast than modulation peak.

    Citation: C-014 C-019
    """
    out = protocols.run_figure_3F()
    c, _, _, percent, difference = _arrays(out)
    assert c[int(np.argmax(difference))] > c[int(np.argmax(percent))]


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-026")
def test_figure_3f_has_larger_high_contrast_separation_than_3c():
    """Figure 3F keeps a larger high-contrast attended-unattended separation.

    Citation: C-014 C-019 C-020
    """
    out_f = protocols.run_figure_3F()
    out_c = protocols.run_figure_3C()
    _, _, _, _, difference_f = _arrays(out_f)
    _, _, _, _, difference_c = _arrays(out_c)
    assert difference_f[-1] > difference_c[-1]
    assert float(difference_f[-1]) / float(difference_f[0]) > float(
        difference_c[-1]
    ) / float(difference_c[0])
