"""Contract test for the formalized calibrated 1D-CRF entry point.

ARCHITECTURE.md §1 / ARCHITECTURE_WATCHLIST.md: this is the deliverable
that fixes the hermann2010 leak. The success criterion is that a
dependent can get a calibrated CRF by passing ONLY scientific parameters
+ a regime name — carrying zero discretization knobs and with zero
regime-conditional in its own code.
"""

from __future__ import annotations

import inspect

import numpy as np
import pytest

from rh_model import crf_protocol
from rh_model.model import default_params, simulate


CONTRASTS = np.logspace(np.log10(0.01), np.log10(1.0), 24)


@pytest.mark.parametrize("regime", crf_protocol.REGIMES)
def test_run_crf_returns_calibrated_record(regime):
    """The entry point returns a schema-versioned, ledger-traceable record
    of attended/ignored CRFs from only scientific params + a regime."""
    rec = crf_protocol.run_crf(
        stimulus_size=3.0, attention_field_size=30.0, gamma=2.0,
        regime=regime, contrasts=CONTRASTS,
    )
    for key in ("contrasts", "attended_response", "ignored_response"):
        arr = np.asarray(rec[key], float)
        assert arr.shape == CONTRASTS.shape
        assert np.all(np.isfinite(arr)) and np.all(arr >= -1e-9)
    assert "resolved_ledger_hash" in rec and rec["schema_version"] >= 1
    assert rec["regime"] == regime
    # attention raises (or holds) the response everywhere
    assert np.all(
        np.asarray(rec["attended_response"], float)
        >= np.asarray(rec["ignored_response"], float) - 1e-9
    )


def test_signature_carries_only_scientific_params():
    """The public signature exposes ONLY scientific params + regime +
    contrasts — no suppressive_*/baseline_*/sigma discretization knob."""
    sig = inspect.signature(crf_protocol.run_crf)
    params = set(sig.parameters)
    assert params == {
        "stimulus_size",
        "attention_field_size",
        "gamma",
        "regime",
        "contrasts",
        "tuning_width",
    }
    leaky = {
        "suppressive_drive_gain",
        "suppressive_spatial_sigma_scale",
        "suppressive_tuning_width",
        "baseline_unmodulated",
        "baseline_modulated_by_attention",
        "sigma",
    }
    assert not (params & leaky)


def test_regime_conditional_lives_behind_the_entry_point():
    """Selecting a regime is the ONLY regime input the caller gives; the
    contrast_gain vs response_gain calibration difference (the hermann
    regime-conditional) is internal — the caller writes no conditional.

    Proven by: passing the same scientific params with the two regime
    names yields different calibrated CRFs WITHOUT the caller ever
    referencing a suppressive scale.
    """
    cg = crf_protocol.run_crf(3.0, 30.0, 2.0, "contrast_gain", CONTRASTS)
    rg = crf_protocol.run_crf(3.0, 30.0, 2.0, "response_gain", CONTRASTS)
    assert not np.allclose(cg["attended_response"], rg["attended_response"])
    with pytest.raises(ValueError):
        crf_protocol.run_crf(3.0, 30.0, 2.0, "not_a_regime", CONTRASTS)


def test_run_crf_matches_hand_rolled_calibrated_path():
    """run_crf reproduces, byte-for-behavior, the hand-rolled calibrated
    CRF a dependent used to build (so a dependent can switch to it with
    zero behavior change). contrast_gain ≡ R&H Fig 2A calibration."""
    overrides = dict(
        stimulus_size=3.0, attention_field_size=30.0,
        peak_attention_gain_gamma=2.0, tuning_width=30.0,
        suppressive_drive_gain=4.0, suppressive_spatial_sigma_scale=0.55,
        baseline_unmodulated=0.01,
    )
    att = np.empty(CONTRASTS.size)
    ign = np.empty(CONTRASTS.size)
    for i, c in enumerate(CONTRASTS):
        p = default_params(**overrides)
        st = [{"x": 0.0, "theta": 0.0, "contrast": float(c)}]
        att[i] = simulate(st, {"spatial_center": 0.0, "feature_center": None}, p)["response"]
        ign[i] = simulate(st, {"spatial_center": None, "feature_center": None}, p)["response"]

    rec = crf_protocol.run_crf(3.0, 30.0, 2.0, "contrast_gain", CONTRASTS)
    np.testing.assert_array_equal(att, np.asarray(rec["attended_response"], float))
    np.testing.assert_array_equal(ign, np.asarray(rec["ignored_response"], float))
