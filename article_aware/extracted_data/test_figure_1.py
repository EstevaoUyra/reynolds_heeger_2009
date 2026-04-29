from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_1", claim_id="Q-001")
def test_attended_location_response_exceeds_unattended():
    """Output R is larger at attended x=+10 than unattended x=-10.

    Citation: C-021
    """
    out = protocols.run_figure_1()
    assert out["R_at_attended"] > out["R_at_unattended"]


@deterministic_test(spec_ref="simulation_protocols.figure_1", claim_id="Q-002")
def test_attention_field_baseline_and_peak():
    """Attention field is >= 1 everywhere and peaks near gamma=2.

    Citation: C-005
    """
    out = protocols.run_figure_1()
    assert np.all(out["A"] >= 1.0)
    assert abs(out["A"].max() - 2.0) < 0.1


@deterministic_test(spec_ref="simulation_protocols.figure_1", claim_id="Q-003")
def test_population_fields_are_non_negative():
    """Population fields E, A, S, and R are non-negative.

    Citation: C-001
    """
    out = protocols.run_figure_1()
    assert np.all(out["E"] >= 0.0)
    assert np.all(out["A"] >= 1.0)
    assert np.all(out["S"] >= 0.0)
    assert np.all(out["R"] >= 0.0)
