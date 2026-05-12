from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import is_multiplicative_scaling, value_at
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-029")
def test_attending_preferred_exceeds_attending_nonpreferred():
    """Attending preferred yields larger responses at every contrast.

    Citation: C-021
    """
    out = protocols.run_figure_4E()
    assert np.all(out["attend_pref_CRF"] > out["attend_nonpref_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-030")
def test_crfs_are_multiplicative_scaling():
    """Attend-pref and attend-nonpref CRFs differ by response gain.

    Citation: C-019
    """
    out = protocols.run_figure_4E()
    assert is_multiplicative_scaling(
        out["attend_pref_CRF"],
        out["attend_nonpref_CRF"],
        mask_below_frac=0.01,
        max_ratio_spread=1.5,
    )


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-031")
def test_attend_pref_crf_saturates_at_high_contrast():
    """Attend-pref CRF changes little between c=0.5 and c=1.

    Citation: C-020
    """
    out = protocols.run_figure_4E()
    attend_pref_at_half = value_at(out["c"], out["attend_pref_CRF"], 0.5)
    assert (out["attend_pref_CRF"][-1] - attend_pref_at_half) / attend_pref_at_half < 0.3


@deterministic_test(spec_ref="simulation_protocols.figure_4E", figure=4, claim_id="Q-032")
def test_peak_attend_pref_exceeds_peak_attend_nonpreferred():
    """Peak attend-pref response exceeds peak attend-nonpref response.

    Citation: C-019
    """
    out = protocols.run_figure_4E()
    assert out["attend_pref_CRF"].max() > out["attend_nonpref_CRF"].max()
