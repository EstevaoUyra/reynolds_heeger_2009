from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import is_multiplicative_scaling, value_at
from rh_model import protocols


def _validated_outputs(out: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return Figure 4E outputs after checking the declared curve contract.

    Assumption: A-006
    """
    expected = {"attend_pref_CRF", "attend_nonpref_CRF", "ratio", "c"}
    assert expected.issubset(out.keys())

    attend_pref = np.asarray(out["attend_pref_CRF"], dtype=float)
    attend_nonpref = np.asarray(out["attend_nonpref_CRF"], dtype=float)
    ratio = np.asarray(out["ratio"], dtype=float)
    contrast = np.asarray(out["c"], dtype=float)

    assert attend_pref.ndim == attend_nonpref.ndim == ratio.ndim == contrast.ndim == 1
    assert attend_pref.shape == attend_nonpref.shape == ratio.shape == contrast.shape
    assert attend_pref.size >= 8
    assert np.all(np.isfinite(attend_pref))
    assert np.all(np.isfinite(attend_nonpref))
    assert np.all(np.isfinite(ratio))
    assert np.all(np.isfinite(contrast))
    assert np.all(contrast > 0.0)
    assert np.all(np.diff(contrast) > 0.0)
    assert np.allclose(np.diff(np.log(contrast)), np.diff(np.log(contrast))[0], rtol=0.15)
    assert np.all(attend_pref >= 0.0)
    assert np.all(attend_nonpref > 0.0)

    expected_ratio = attend_pref / attend_nonpref
    assert np.allclose(ratio, expected_ratio, rtol=1e-6, atol=1e-8)
    return attend_pref, attend_nonpref, ratio, contrast


def _max_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the largest finite CRF slope on a log-contrast axis.

    Assumption: A-006
    """
    return float(np.max(np.diff(curve) / np.diff(np.log(contrast))))


def _final_log_slope(curve: np.ndarray, contrast: np.ndarray) -> float:
    """Return the final finite CRF slope on a log-contrast axis.

    Assumption: A-006
    """
    return float(np.diff(curve)[-1] / np.diff(np.log(contrast))[-1])


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-047")
def test_figure_4E_output_contract_and_ratio():
    """Figure 4E returns finite CRFs and a consistent attention ratio.

    Citation: C-015
    """
    _validated_outputs(protocols.run_figure_4E())


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-048")
def test_attending_preferred_exceeds_attending_nonpreferred():
    """Attending preferred yields larger responses at every contrast.

    Citation: C-021
    """
    attend_pref, attend_nonpref, ratio, _ = _validated_outputs(protocols.run_figure_4E())

    assert np.all(attend_pref >= attend_nonpref - 1e-10)
    assert np.all(ratio > 1.0)
    assert attend_pref[-1] > attend_nonpref[-1]


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-049")
def test_crfs_are_multiplicative_scaling():
    """Attend-pref and attend-nonpref CRFs differ by response gain.

    Citation: C-015, C-019, C-021
    """
    attend_pref, attend_nonpref, ratio, _ = _validated_outputs(protocols.run_figure_4E())

    assert is_multiplicative_scaling(
        attend_pref,
        attend_nonpref,
        mask_below_frac=0.01,
        max_ratio_spread=1.5,
    )
    response_bearing = attend_nonpref > 0.05 * attend_nonpref.max()
    ratio_bearing = ratio[response_bearing]
    assert ratio_bearing.max() / ratio_bearing.min() < 1.5
    assert ratio_bearing.mean() > 1.05


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-050")
def test_crfs_are_monotonic_and_saturating():
    """Both Figure 4E CRFs rise monotonically and level off at high contrast.

    Citation: C-020
    """
    attend_pref, attend_nonpref, _, contrast = _validated_outputs(protocols.run_figure_4E())

    for curve in (attend_pref, attend_nonpref):
        assert np.all(np.diff(curve) >= -1e-10)
        assert curve[-1] > curve[0]
        assert _final_log_slope(curve, contrast) < 0.95 * _max_log_slope(curve, contrast)


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-051")
def test_attend_pref_crf_saturates_at_high_contrast():
    """Attend-pref CRF changes little between c=0.5 and c=1.

    Citation: C-020
    """
    attend_pref, _, _, contrast = _validated_outputs(protocols.run_figure_4E())

    attend_pref_at_half = value_at(contrast, attend_pref, 0.5)
    # Paper-grounded plateau (C-020, "responses saturate at high stimulus
    # contrasts ... when c >> sigma, r(c) ~ alpha"): the closed-form CRF with
    # sigma=0.1 is within ~15% of its half-max value by c=1. This bound asserts
    # the PAPER'S saturation claim against the single faithful suppression
    # mechanism (A-006 2D-plane integral normalization); it is NOT set to make
    # any particular suppressive_drive_gain pass/fail (A-013 forbids gain
    # tuning) — the faithful mechanism saturates by construction.
    assert (attend_pref[-1] - attend_pref_at_half) / attend_pref_at_half < 0.15


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-052")
def test_peak_attend_pref_exceeds_peak_attend_nonpreferred():
    """Peak attend-pref response exceeds peak attend-nonpref response.

    Citation: C-019
    """
    attend_pref, attend_nonpref, _, _ = _validated_outputs(protocols.run_figure_4E())

    assert attend_pref.max() > attend_nonpref.max()
    assert attend_pref[-1] >= 1.05 * attend_nonpref[-1]


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-053")
def test_figure_4C_suppresses_while_4E_attend_pref_enhances():
    """Figure 4C (attend the NULL) and Figure 4E (attend the PREFERRED) move the
    recorded preferred neuron in OPPOSITE directions — exactly the C-021 / authors'
    Figure4C.m account.

    4C (authors' Figure4C.m, CODE-018): attending the nonpreferred/null stimulus
    in the RF SUPPRESSES the recorded preferred neuron — its boosted θ=180°
    population feeds only the recorded θ=0 neuron's suppressive pool (C-021,
    "increasing its suppressive effect and yielding a smaller output firing
    rate"). So attended_CRF (attend-null-in-RF) sits AT-OR-BELOW unattended_CRF
    (attend-away), and the suppression percent_modulation 100·(unatt-att)/unatt is
    positive.

    4E: attending the PREFERRED stimulus ENHANCES it relative to attending the
    nonpreferred (ratio > 1). The two panels are therefore opposite-signed for the
    recorded neuron — the prior "same-sign facilitation" premise (the refuted
    figure_4C_investigation-2026-06-03 / Finding 2) is OVERTURNED by the author
    code; see A-012 / DR-4C-sign.

    Citation: C-015, C-021
    """
    out_c = protocols.run_figure_4C()
    expected_c = {"attended_CRF", "unattended_CRF", "percent_modulation", "c_pref"}
    assert expected_c.issubset(out_c.keys())

    attended_c = np.asarray(out_c["attended_CRF"], dtype=float)
    unattended_c = np.asarray(out_c["unattended_CRF"], dtype=float)
    percent_c = np.asarray(out_c["percent_modulation"], dtype=float)
    assert attended_c.shape == unattended_c.shape == percent_c.shape
    assert np.all(np.isfinite(attended_c))
    assert np.all(np.isfinite(unattended_c))
    assert np.all(np.isfinite(percent_c))
    # 4C: SUPPRESSION — attend-null-in-RF at or below attend-away; the record's
    # suppression-sign percent_modulation = 100·(unatt-att)/unatt is positive.
    assert np.all(attended_c <= unattended_c + 1e-10)
    assert np.all(percent_c >= -1e-8)
    assert percent_c.max() > 1.0

    # 4E: attend-preferred above attend-nonpreferred — enhancement (opposite sign).
    attend_pref, attend_nonpref, ratio, _ = _validated_outputs(protocols.run_figure_4E())
    assert np.all(attend_pref >= attend_nonpref - 1e-10)
    assert np.all(ratio > 1.0)
