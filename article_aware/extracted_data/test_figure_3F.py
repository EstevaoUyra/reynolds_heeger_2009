from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import value_at
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-019")
def test_attended_response_exceeds_unattended():
    """Attended response is at least unattended response at every contrast.

    Citation: C-021
    """
    out = protocols.run_figure_3F()
    assert np.all(out["attended_CRF"] >= out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-020")
def test_percent_modulation_peaks_in_lower_half():
    """Percent modulation is largest at low contrasts.

    Citation: C-014
    """
    out = protocols.run_figure_3F()
    assert int(np.argmax(out["percent_modulation"])) < len(out["percent_modulation"]) / 2


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-021")
def test_absolute_difference_peaks_in_upper_half():
    """Absolute difference peaks in the upper half of contrast range.

    Citation: C-014
    """
    out = protocols.run_figure_3F()
    assert int(np.argmax(out["absolute_difference"])) >= len(out["absolute_difference"]) / 2


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-022")
def test_percent_and_absolute_difference_peak_apart():
    """Percent modulation and absolute difference peak at different extremes.

    Citation: C-014
    """
    out = protocols.run_figure_3F()
    percent_peak = int(np.argmax(out["percent_modulation"]))
    difference_peak = int(np.argmax(out["absolute_difference"]))
    assert abs(percent_peak - difference_peak) > len(out["percent_modulation"]) / 3


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-023")
def test_lowest_contrast_response_is_positive():
    """Smallest-contrast response is positive with baseline included.

    Citation: C-014
    """
    out = protocols.run_figure_3F()
    assert out["attended_CRF"][0] > 0.0
    assert out["unattended_CRF"][0] > 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_3F", figure=3, claim_id="Q-024")
def test_attended_crf_saturates_at_high_contrast():
    """Attended CRF changes little between c=0.5 and c=1.

    Citation: C-020
    """
    out = protocols.run_figure_3F()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3
