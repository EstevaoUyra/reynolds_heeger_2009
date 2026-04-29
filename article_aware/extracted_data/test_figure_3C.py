from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import half_max_contrast, value_at
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-014")
def test_attended_response_exceeds_unattended():
    """Attended response is at least unattended response at every contrast.

    Citation: C-021
    """
    out = protocols.run_figure_3C()
    assert np.all(out["attended_CRF"] >= out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-015")
def test_percent_modulation_peaks_in_lower_half():
    """Percent modulation is largest in the lower half of contrast range.

    Citation: C-014
    """
    out = protocols.run_figure_3C()
    assert int(np.argmax(out["percent_modulation"])) < len(out["percent_modulation"]) / 2


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-016")
def test_attended_crf_is_left_shifted():
    """Attended CRF has smaller half-max contrast than unattended CRF.

    Citation: C-014
    """
    out = protocols.run_figure_3C()
    assert half_max_contrast(out["attended_CRF"], out["c"]) < half_max_contrast(
        out["unattended_CRF"], out["c"]
    )


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-017")
def test_lowest_contrast_response_is_positive():
    """Smallest-contrast response is positive with baseline included.

    Citation: C-014
    """
    out = protocols.run_figure_3C()
    assert out["attended_CRF"][0] > 0.0
    assert out["unattended_CRF"][0] > 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_3C", claim_id="Q-018")
def test_attended_crf_saturates_at_high_contrast():
    """Attended CRF changes little between c=0.5 and c=1.

    Citation: C-020
    """
    out = protocols.run_figure_3C()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3
