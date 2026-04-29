from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import fwhm, is_multiplicative_scaling
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-033")
def test_attended_tuning_exceeds_unattended():
    """Attended tuning is at least unattended tuning at every orientation.

    Citation: C-022
    """
    out = protocols.run_figure_5C()
    assert np.all(out["attended_tuning"] >= out["unattended_tuning"])


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-034")
def test_tuning_ratio_is_approximately_constant():
    """Spatial attention scales tuning without changing shape.

    Citation: C-022
    """
    out = protocols.run_figure_5C()
    assert is_multiplicative_scaling(
        out["attended_tuning"],
        out["unattended_tuning"],
        mask_below_frac=0.05,
        max_ratio_spread=1.3,
    )


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-035")
def test_both_tuning_curves_peak_at_same_orientation():
    """Both tuning curves peak at the recorded neuron's preferred orientation.

    Citation: C-022
    """
    out = protocols.run_figure_5C()
    attended_peak = out["theta_0_grid"][int(np.argmax(out["attended_tuning"]))]
    unattended_peak = out["theta_0_grid"][int(np.argmax(out["unattended_tuning"]))]
    assert abs(attended_peak - unattended_peak) < 5.0


@deterministic_test(spec_ref="simulation_protocols.figure_5C", claim_id="Q-036")
def test_fwhm_is_approximately_equal():
    """Tuning width is approximately equal with and without attention.

    Citation: C-022
    """
    out = protocols.run_figure_5C()
    attended_width = fwhm(out["attended_tuning"], out["theta_0_grid"])
    unattended_width = fwhm(out["unattended_tuning"], out["theta_0_grid"])
    assert abs(attended_width - unattended_width) / unattended_width < 0.2
