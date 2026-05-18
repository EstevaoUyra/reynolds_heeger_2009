"""Contract tests for the named forward stages (ARCHITECTURE.md §5(1)).

Capability-keyed; reused across swaps. These verify the typed
consumes/produces contract (shapes, units-as-ranges, purity) of each
stage — NOT paper claims (those live in article_aware/extracted_data).
"""

from __future__ import annotations

import numpy as np
import pytest

from rh_model.model import DEFAULT_THETA_PERIOD, default_params
from rh_model.stages import (
    attention_field,
    normalization,
    readout,
    stimulus_drive,
    suppression,
    suppressive_kernel,
)

P = default_params()
XG = P.x_grid
TG = P.theta_grid
DX = float(XG[1] - XG[0])
DTH = float(TG[1] - TG[0])


def test_suppressive_kernel_contract():
    """produces s_x:(n_x,), s_theta:(n_th,), each integrating to 1."""
    s_x, s_theta = suppressive_kernel.run(XG, TG, 20.0, 180.0, DEFAULT_THETA_PERIOD)
    assert s_x.shape == XG.shape
    assert s_theta.shape == TG.shape
    assert np.all(np.isfinite(s_x)) and np.all(np.isfinite(s_theta))
    np.testing.assert_allclose(s_x.sum() * DX, 1.0, rtol=1e-6)
    np.testing.assert_allclose(s_theta.sum() * DTH, 1.0, rtol=1e-6)


def test_stimulus_drive_contract():
    """produces E:(n_th, n_x) ≥ 0, peaked at the stimulus location."""
    stimuli = [{"x": 0.0, "theta": 0.0, "contrast": 0.5}]
    E = stimulus_drive.run(stimuli, XG, TG, 5.0, 30.0)
    assert E.shape == (TG.size, XG.size)
    assert np.all(E >= 0.0) and np.all(np.isfinite(E))
    peak_x = XG[int(np.argmax(E[int(np.argmin(np.abs(TG)))]))]
    assert abs(peak_x) <= 1.0
    # purity: a second call with the same inputs gives the same array
    np.testing.assert_array_equal(E, stimulus_drive.run(stimuli, XG, TG, 5.0, 30.0))


def test_attention_field_contract():
    """produces A:(n_th, n_x) ≥ 1; flat-in-θ when feature_center is None."""
    A = attention_field.run(
        {"spatial_center": 0.0, "feature_center": None}, XG, TG, 10.0, 2.0, 30.0
    )
    assert A.shape == (TG.size, XG.size)
    assert np.all(A >= 1.0 - 1e-12) and np.all(np.isfinite(A))
    assert np.max(np.ptp(A, axis=0)) <= 1e-10  # flat over θ
    A_none = attention_field.run(
        {"spatial_center": None, "feature_center": None}, XG, TG, 10.0, 2.0, 30.0
    )
    np.testing.assert_allclose(A_none, 1.0)


def test_suppression_contract():
    """consumes kernel+A+E; produces S:(n_th,n_x) ≥ 0, same shape."""
    s_x, s_theta = suppressive_kernel.run(XG, TG, 20.0, 180.0)
    E = stimulus_drive.run([{"x": 0.0, "theta": 0.0, "contrast": 0.5}], XG, TG, 5.0, 30.0)
    A = np.ones_like(E)
    S = suppression.run(s_x, s_theta, A, E, DX, DTH)
    assert S.shape == E.shape
    assert np.all(S >= 0.0) and np.all(np.isfinite(S))


def test_normalization_contract_and_variant_selector():
    """produces R:(n_th,n_x) ≥ 0; variant is config, unknown is hard error."""
    E = np.full((TG.size, XG.size), 0.5)
    A = np.ones_like(E) * 2.0
    S = np.full_like(E, 0.3)
    R = normalization.run(A, E, S, 0.1, 0.0, variant="divisive")
    assert R.shape == E.shape
    assert np.all(R >= 0.0) and np.all(np.isfinite(R))
    # trivial variant drops S → strictly larger response here
    R_id = normalization.run(A, E, S, 0.1, 0.0, variant="identity_suppression")
    assert np.all(R_id >= R - 1e-12) and np.any(R_id > R)
    with pytest.raises(ValueError):
        normalization.run(A, E, S, 0.1, 0.0, variant="bogus")


def test_readout_contract():
    """produces a scalar response read at the recorded grid sample."""
    R = np.zeros((TG.size, XG.size))
    i = int(np.argmin(np.abs(XG - 10.0)))
    j = int(np.argmin(np.abs(TG - 0.0)))
    R[j, i] = 7.0
    val = readout.run(R, XG, TG, 10.0, 0.0)
    assert val == pytest.approx(7.0)


def test_named_stage_pipeline_matches_model_simulate():
    """The named-stage pipeline is byte-for-behavior identical to the
    monolithic model.simulate (structure migration invariant)."""
    from rh_model.model import simulate

    params = default_params(
        stimulus_size=3.0, attention_field_size=30.0,
        peak_attention_gain_gamma=2.0, tuning_width=30.0,
    )
    stimuli = [{"x": 0.0, "theta": 0.0, "contrast": 0.4}]
    cond = {"spatial_center": 0.0, "feature_center": None}
    out = simulate(stimuli, cond, params)

    s_x, s_theta = suppressive_kernel.run(
        params.x_grid, params.theta_grid,
        params.suppressive_field_size * params.suppressive_spatial_sigma_scale,
        params.suppressive_tuning_width, params.theta_period,
    )
    E = stimulus_drive.run(
        stimuli, params.x_grid, params.theta_grid,
        params.stimulus_size * params.stimulus_spatial_sigma_scale,
        params.tuning_width or 30.0, params.theta_period,
    )
    A = attention_field.run(
        cond, params.x_grid, params.theta_grid,
        params.attention_field_size * params.attention_spatial_sigma_scale,
        params.peak_attention_gain_gamma, params.tuning_width, params.theta_period,
    )
    S = suppression.run(
        s_x, s_theta, A, E,
        float(params.x_grid[1] - params.x_grid[0]),
        float(params.theta_grid[1] - params.theta_grid[0]),
    )
    S = params.suppressive_drive_gain * S
    R = normalization.run(A, E, S, params.sigma, params.threshold_T)
    resp = readout.run(
        R, params.x_grid, params.theta_grid, params.recorded_x, params.recorded_theta
    )
    assert resp == pytest.approx(out["response"], rel=0, abs=0)
