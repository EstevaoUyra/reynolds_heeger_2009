from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import half_max_contrast, value_at
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-004")
def test_attended_response_exceeds_unattended():
    """Attended response is at least unattended response at every contrast.

    Citation: C-021
    """
    out = protocols.run_figure_2A()
    assert np.all(out["attended_CRF"] >= out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-005")
def test_percent_modulation_peaks_at_intermediate_contrast():
    """Percent modulation peaks inside the swept contrast range.

    Citation: C-019
    """
    out = protocols.run_figure_2A()
    peak = int(np.argmax(out["percent_modulation"]))
    assert 0 < peak < len(out["percent_modulation"]) - 1


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-006")
def test_attended_crf_is_left_shifted():
    """Attended CRF has smaller half-max contrast than unattended CRF.

    Citation: C-019
    """
    out = protocols.run_figure_2A()
    assert half_max_contrast(out["attended_CRF"], out["c"]) < half_max_contrast(
        out["unattended_CRF"], out["c"]
    )


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-007")
def test_attended_crf_saturates_at_high_contrast():
    """Attended CRF changes little between c=0.5 and c=1.

    Citation: C-020
    """
    out = protocols.run_figure_2A()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3


@deterministic_test(spec_ref="simulation_protocols.figure_2A", figure=2, claim_id="Q-008")
def test_high_contrast_modulation_is_below_peak_modulation():
    """Highest-contrast percent modulation is below peak modulation.

    Citation: C-019
    """
    out = protocols.run_figure_2A()
    assert out["percent_modulation"][-1] < out["percent_modulation"].max()
