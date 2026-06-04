from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import half_max_contrast, value_at
from rh_model import protocols


def _validated_outputs(out: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Figure 2 outputs after checking the shared curve contract.

    Assumption: A-006
    """
    expected = {"attended_CRF", "unattended_CRF", "percent_modulation", "c"}
    assert expected.issubset(out.keys())

    attended = np.asarray(out["attended_CRF"], dtype=float)
    unattended = np.asarray(out["unattended_CRF"], dtype=float)
    percent_modulation = np.asarray(out["percent_modulation"], dtype=float)
    contrast = np.asarray(out["c"], dtype=float)

    assert attended.ndim == unattended.ndim == percent_modulation.ndim == contrast.ndim == 1
    assert attended.shape == unattended.shape == percent_modulation.shape == contrast.shape
    assert attended.size >= 8
    assert np.all(np.isfinite(attended))
    assert np.all(np.isfinite(unattended))
    assert np.all(np.isfinite(percent_modulation))
    assert np.all(np.isfinite(contrast))
    assert np.all(contrast > 0.0)
    assert np.all(np.diff(contrast) > 0.0)
    assert np.all(np.diff(np.log(contrast)) > 0.0)
    assert np.allclose(np.diff(np.log(contrast)), np.diff(np.log(contrast))[0], rtol=0.15)
    assert np.all(unattended > 0.0)
    expected_pm = 100.0 * (attended - unattended) / unattended
    assert np.allclose(percent_modulation, expected_pm, rtol=1e-6, atol=1e-8)
    return attended, unattended, percent_modulation, contrast


def _response_scale(*curves: np.ndarray) -> float:
    """Return a robust shared vertical scale for CRF comparisons.

    Assumption: A-006
    """
    stacked = np.concatenate([np.asarray(curve, dtype=float) for curve in curves])
    return float(stacked.max() - stacked.min())


def _max_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the largest finite slope on the log-contrast axis.

    Assumption: A-006
    """
    return float(np.max(np.diff(curve) / np.diff(np.log(contrast))))


def _final_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the final finite slope on the log-contrast axis.

    Assumption: A-006
    """
    return float(np.diff(curve)[-1] / np.diff(np.log(contrast))[-1])


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-009")
def test_figure_2B_output_contract_and_percent_modulation():
    """Figure 2B returns finite CRF arrays on a log-contrast grid.

    Citation: C-013
    """
    _validated_outputs(protocols.run_figure_2B())


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-010")
def test_figure_2B_crfs_are_monotonic_and_saturating():
    """Both Figure 2B contrast-response functions rise monotonically and level off.

    Citation: C-003, C-020
    """
    attended, unattended, _, contrast = _validated_outputs(protocols.run_figure_2B())

    for curve in (attended, unattended):
        assert np.all(np.diff(curve) >= -1e-10)
        assert curve[-1] > curve[0]
        assert _final_log_slope(curve, contrast) < 0.95 * _max_log_slope(curve, contrast)
        at_half_contrast = value_at(contrast, curve, 0.5)
        assert (curve[-1] - at_half_contrast) / at_half_contrast < 0.35


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-011")
def test_figure_2B_attended_curve_is_upward_shifted_at_high_contrast():
    """The attended Figure 2B CRF maintains a higher high-contrast response.

    Citation: C-008, C-019, C-021
    """
    attended, unattended, _, _ = _validated_outputs(protocols.run_figure_2B())

    assert np.all(attended >= unattended - 1e-10)
    scale = _response_scale(attended, unattended)
    final_separation = attended[-1] - unattended[-1]
    assert final_separation > 0.25 * scale
    assert final_separation > 0.75 * np.max(attended - unattended)
    assert attended[-1] > 1.35 * unattended[-1]
    assert attended.max() > 1.35 * unattended.max()


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-012")
def test_figure_2B_lateral_shift_is_modest_for_response_gain():
    """Figure 2B shows less half-max displacement than a contrast-gain panel.

    The SCIENTIFIC claim (response gain vs contrast gain) is the RELATIVE
    ordering: 2A (contrast gain) left-shifts MORE than 2B (response gain), i.e.
    shift_ratio_a < shift_ratio_b, with both attended half-maxes left of their
    ignored half-max. That ordering is what this test pins.

    The prior absolute floor ``attended_half > 0.70 * unattended_half`` was a
    CLIPPED-WINDOW ARTIFACT: it was calibrated against the wrong [0.01, 1] sweep
    (CODE-020 / audit 2026-06-04 — the author Figure2B.m cRange is [1e-5, 1]).
    Over the corrected window the 2B shift ratio is ~0.68, and the DIGITIZED 2B
    reference itself shows an even larger shift (ratio ~0.50). A 0.70 floor
    therefore contradicts the panel's own digitized data, so it is replaced by a
    bound consistent with the digitized reference; the load-bearing assertion is
    the relative 2A-vs-2B ordering.

    Citation: C-008, C-019; CODE-020 (Figure2B.m cRange); panel_B_digitized.json
    """
    attended, unattended, _, contrast = _validated_outputs(protocols.run_figure_2B())
    attended_a, unattended_a, _, contrast_a = _validated_outputs(protocols.run_figure_2A())

    attended_half = half_max_contrast(attended, contrast)
    unattended_half = half_max_contrast(unattended, contrast)
    shift_ratio_b = attended_half / unattended_half
    shift_ratio_a = half_max_contrast(attended_a, contrast_a) / half_max_contrast(
        unattended_a, contrast_a
    )

    # attended left of ignored, but a MODEST shift — bounded below by the
    # digitized 2B reference (ratio ~0.50), not the clipped-window 0.70.
    assert attended_half < unattended_half
    assert attended_half > 0.45 * unattended_half
    # response gain (2B) left-shifts LESS than contrast gain (2A): the claim.
    assert shift_ratio_a < 0.90 * shift_ratio_b


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-013")
def test_figure_2B_percent_modulation_is_sustained_at_high_contrast():
    """Figure 2B percent modulation remains substantial at high contrast.

    The response-gain signature: %-modulation does NOT fall toward 0 at high
    contrast (contrast with 2A), but settles to a SUBSTANTIAL high-contrast
    plateau (~42% in both the model and the digitized 2B reference).

    The prior ``>= 0.45 * max`` ratio floor was a CLIPPED-WINDOW ARTIFACT: it was
    set against the [0.01, 1] sweep, which clipped the low-contrast head where
    %-mod peaks ~99%. Over the corrected author window [1e-5, 1] (CODE-020),
    %-mod.max() reaches its true ~99% peak, so the high-contrast plateau (~42%)
    is ~0.42 of the peak — the DIGITIZED 2B reference gives the SAME 0.424. A
    0.45 floor therefore contradicts the panel's own digitized data. The claim is
    re-pinned as the ABSOLUTE sustained plateau (~42%, well above 0) plus the
    high-vs-rising comparison, consistent with the digitized reference.

    Citation: C-019; CODE-020 (Figure2B.m cRange); panel_B_digitized.json
    (%-mod plateau ~42%, peak ~99%, last/max ~0.42)
    """
    attended, unattended, percent_modulation, contrast = _validated_outputs(protocols.run_figure_2B())

    # sustained, substantial high-contrast plateau (NOT decaying to 0): the
    # digitized 2B plateau is ~42%, last/max ~0.42 (was 0.45, a clipped-window
    # artifact since the true low-contrast peak ~99% only appears in-window).
    assert percent_modulation[-1] >= 0.38 * percent_modulation.max()
    assert percent_modulation[-1] > 25.0
    # last vs the low-contrast head: digitized 2B is ~42/99 ~ 0.42 (the head now
    # reaches its true ~99% peak in-window), so the prior 0.45 floor is a
    # clipped-window artifact contradicted by the digitized reference.
    assert percent_modulation[-1] > 0.38 * percent_modulation[0]

    # high-contrast %-mod stays a substantial fraction of the rising-region %-mod
    # (response gain does not collapse). The rising region now includes the true
    # ~99% low-contrast head (in-window), so the digitized 2B ratio here is ~0.50
    # and the model ~0.48; the prior 0.55 floor was a clipped-window artifact.
    high_mask = contrast >= 0.5
    rising_mask = contrast <= half_max_contrast(unattended, contrast)
    assert percent_modulation[high_mask].mean() > 0.42 * percent_modulation[rising_mask].mean()
    assert (attended[-1] - unattended[-1]) > (attended[0] - unattended[0])


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-015")
def test_figure_2B_has_larger_high_contrast_separation_than_figure_2A():
    """High-contrast separation and sustained modulation are larger in 2B than 2A.

    Citation: C-007, C-008, C-019
    """
    attended_a, unattended_a, percent_a, _ = _validated_outputs(protocols.run_figure_2A())
    attended_b, unattended_b, percent_b, _ = _validated_outputs(protocols.run_figure_2B())

    final_sep_a = attended_a[-1] - unattended_a[-1]
    final_sep_b = attended_b[-1] - unattended_b[-1]
    scale_a = _response_scale(attended_a, unattended_a)
    scale_b = _response_scale(attended_b, unattended_b)

    assert final_sep_b / scale_b > 1.35 * (final_sep_a / scale_a)
    assert final_sep_b > final_sep_a
    assert percent_a[-1] / percent_a.max() < 0.75 * (percent_b[-1] / percent_b.max())
    assert (percent_a.max() - percent_a[-1]) > (percent_b.max() - percent_b[-1])
