from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import value_at_min_abs
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-041")
def test_attending_variable_boosts_preferred_response():
    """Attending variable stimulus boosts response near preferred direction.

    Citation: C-021
    """
    out = protocols.run_figure_7C()
    assert (
        value_at_min_abs(out["attend_variable_tuning"] - out["fixation_tuning"], out["theta_var_grid"])
        > 0.0
    )


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-042")
def test_attending_nonpreferred_suppresses_preferred_response():
    """Attending nonpreferred stimulus suppresses response near preferred direction.

    Citation: C-021
    """
    out = protocols.run_figure_7C()
    assert (
        value_at_min_abs(out["attend_nonpref_tuning"] - out["fixation_tuning"], out["theta_var_grid"])
        < 0.0
    )


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-043")
def test_variable_and_nonpreferred_shift_in_opposite_directions():
    """Variable and nonpreferred attention shift preferred response oppositely.

    Citation: C-021
    """
    out = protocols.run_figure_7C()
    variable_delta = value_at_min_abs(
        out["attend_variable_tuning"] - out["fixation_tuning"], out["theta_var_grid"]
    )
    nonpreferred_delta = value_at_min_abs(
        out["attend_nonpref_tuning"] - out["fixation_tuning"], out["theta_var_grid"]
    )
    assert variable_delta * nonpreferred_delta < 0.0


@deterministic_test(spec_ref="simulation_protocols.figure_7C", figure=7, claim_id="Q-044")
def test_tuning_curves_are_non_negative():
    """All three tuning curves are non-negative everywhere.

    Citation: C-001
    """
    out = protocols.run_figure_7C()
    assert np.all(out["fixation_tuning"] >= 0.0)
    assert np.all(out["attend_nonpref_tuning"] >= 0.0)
    assert np.all(out["attend_variable_tuning"] >= 0.0)
