from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import half_max_contrast
from rh_model import protocols


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-025")
def test_attending_nonpreferred_decreases_response():
    """Attending nonpreferred-in-RF decreases the preferred-stimulus response.

    Citation: C-021
    """
    out = protocols.run_figure_4C()
    assert np.all(out["attended_CRF"] <= out["unattended_CRF"])


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-026")
def test_attended_crf_is_right_shifted():
    """Attend-nonpreferred CRF has larger half-max contrast.

    Citation: C-021
    """
    out = protocols.run_figure_4C()
    assert half_max_contrast(out["attended_CRF"], out["c_pref"]) > half_max_contrast(
        out["unattended_CRF"], out["c_pref"]
    )


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-027")
def test_absolute_percent_modulation_does_not_peak_at_highest_contrast():
    """Absolute percent modulation does not peak at the highest contrast.

    Citation: C-019
    """
    out = protocols.run_figure_4C()
    assert int(np.argmax(np.abs(out["percent_modulation"]))) < len(out["percent_modulation"]) - 1


@deterministic_test(spec_ref="simulation_protocols.figure_4C", claim_id="Q-028")
def test_crfs_converge_at_high_contrast():
    """CRF gap at high contrast is smaller than the maximum normalized gap.

    Citation: C-020
    """
    out = protocols.run_figure_4C()
    high_contrast_gap = (
        abs(out["attended_CRF"][-1] - out["unattended_CRF"][-1])
        / out["unattended_CRF"][-1]
    )
    max_gap = abs(out["attended_CRF"] - out["unattended_CRF"]).max() / out[
        "unattended_CRF"
    ].max()
    assert high_contrast_gap < max_gap
