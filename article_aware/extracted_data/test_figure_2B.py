from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import is_multiplicative_scaling, value_at
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-009")
def test_attended_response_exceeds_unattended():
    """Attended response is at least unattended response at every contrast.

    Citation: C-021
    """
    out = protocols.run_figure_2B()
    assert np.all(out["attended_CRF"] >= out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-010")
def test_high_contrast_modulation_remains_substantial():
    """High-contrast modulation remains at least half the maximum modulation.

    Citation: C-019
    """
    out = protocols.run_figure_2B()
    assert out["percent_modulation"][-1] >= 0.5 * out["percent_modulation"].max()


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-011")
def test_attended_crf_is_multiplicative_scaling():
    """Attended CRF is approximately multiplicative scaling of unattended CRF.

    Citation: C-019
    """
    out = protocols.run_figure_2B()
    assert is_multiplicative_scaling(
        out["attended_CRF"],
        out["unattended_CRF"],
        mask_below_frac=0.01,
        max_ratio_spread=1.5,
    )


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-012")
def test_peak_attended_response_exceeds_peak_unattended():
    """Peak attended response exceeds peak unattended response.

    Citation: C-019
    """
    out = protocols.run_figure_2B()
    assert out["attended_CRF"].max() > out["unattended_CRF"].max()


@deterministic_test(spec_ref="simulation_protocols.figure_2B", figure=2, claim_id="Q-013")
def test_attended_crf_saturates_at_high_contrast():
    """Attended CRF changes little between c=0.5 and c=1.

    Citation: C-020
    """
    out = protocols.run_figure_2B()
    attended_at_half = value_at(out["c"], out["attended_CRF"], 0.5)
    assert (out["attended_CRF"][-1] - attended_at_half) / attended_at_half < 0.3
