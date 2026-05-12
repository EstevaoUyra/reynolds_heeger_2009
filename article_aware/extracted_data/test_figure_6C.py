from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import fwhm
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-037")
def test_feature_attention_narrows_tuning():
    """Feature-based attention narrows the motion-direction tuning curve.

    Citation: C-023
    """
    out = protocols.run_figure_6C()
    assert fwhm(out["attend_opposite_stimulus_tuning"], out["theta_stim_grid"]) < fwhm(
        out["attend_fixation_tuning"], out["theta_stim_grid"]
    )


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-038")
def test_tuning_curves_peak_at_preferred_direction():
    """Both tuning curves peak near the recorded neuron's preferred direction.

    Citation: C-023
    """
    out = protocols.run_figure_6C()
    fixation_peak = out["theta_stim_grid"][int(np.argmax(out["attend_fixation_tuning"]))]
    opposite_peak = out["theta_stim_grid"][
        int(np.argmax(out["attend_opposite_stimulus_tuning"]))
    ]
    assert abs(fixation_peak) < 15.0
    assert abs(opposite_peak) < 15.0


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-039")
def test_tuning_curves_are_non_negative():
    """Both tuning curves are non-negative everywhere.

    Citation: C-001
    """
    out = protocols.run_figure_6C()
    assert np.all(out["attend_fixation_tuning"] >= 0.0)
    assert np.all(out["attend_opposite_stimulus_tuning"] >= 0.0)


@deterministic_test(spec_ref="simulation_protocols.figure_6C", figure=6, claim_id="Q-040")
def test_feature_attention_boosts_preferred_response():
    """Feature attention boosts the preferred response.

    Citation: C-021
    """
    out = protocols.run_figure_6C()
    assert out["attend_opposite_stimulus_tuning"].max() > out["attend_fixation_tuning"].max()
