"""Formalized calibrated 1D-CRF entry point — the cross-model reuse surface.

THIS is the deliverable that fixes the hermann2010 leak
(ARCHITECTURE_WATCHLIST.md; ARCHITECTURE.md §1). hermann reused R&H's
*calibrated 1D-CRF protocol* by hand and consequently (a) carried R&H's
un-re-derivable 1D-discretization knobs (``suppressive_drive_gain``,
``suppressive_spatial_sigma_scale``, ``baseline_unmodulated``, …) as 22
``audited:false`` magic numbers in its OWN ledger, and (b) put a
``if regime == "contrast_gain"`` **regime-conditional in its own stage
code** reaching into an R&H-internal detail (the 0.55 vs 1.0 suppressive
spatial sigma scale) invisible at the dependent layer.

``run_crf`` closes that boundary. A dependent calls it with **only the
scientific parameters** — stimulus size, attention-field size, peak gain
γ, a named regime, and the contrast grid — and gets a calibrated CRF
back. The per-regime implementation-side calibration is read INTERNALLY
from ``implementation/calibration.yaml`` (the ``regime.*`` namespace) and
never crosses the boundary. The dependent:

  * carries **zero** discretization knobs,
  * has **zero** regime-conditional in its own code (it passes a regime
    *name*; the conditional that selects calibration lives here, behind
    the entry point, as ledger lookup — not as a literal in the
    dependent),
  * is traceable: the resolved-ledger hash is on the returned record.

Scientific contract (model_spec.yaml protocols.calibrated_crf):
  consumes:
    stimulus_size         : float  units: R&H arbitrary spatial units (σ)
    attention_field_size  : float  units: R&H arbitrary spatial units (σ)
    gamma                 : float  units: dimensionless (peak attn gain ≥ 1)
    regime                : str enum {contrast_gain, response_gain}
    contrasts             : (n,) float  units: contrast c ∈ [0,1]
    tuning_width          : float  units: degrees (optional; default 30)
  produces (measurement record):
    contrasts, attended_response, ignored_response,
    half_max{attended,ignored}, schema_version, resolved_ledger_hash
  citation: C-005, C-006, C-013 ; assumption: A-001, A-002, A-006

A dependent depending on this entry point declares it in its
model_spec.yaml ``depends_on.reused_stages`` as
``rh_model.crf_protocol.run_crf`` and needs NO ``rh_model``
implementation-side calibration in its own ledger.
"""

from __future__ import annotations

import numpy as np

from . import measurements
from .calibration import resolve_namespace
from .model import default_params
from .stages import (
    attention_field,
    normalization,
    readout,
    stimulus_drive,
    suppression,
    suppressive_kernel,
)

#: Named gain regimes. These mirror the reproduced R&H Figure-2 single-
#: grating CRF panels: contrast_gain ≡ Fig 2A geometry; response_gain ≡
#: Fig 2B geometry. The regime selects the implementation-side 1D
#: calibration (``regime.<name>.*`` in implementation/calibration.yaml).
REGIMES = ("contrast_gain", "response_gain")


def _forward_response(
    params, stimuli: list[dict], attention_condition: dict
) -> float:
    """Run the named forward stages once and read the recorded neuron.

    This is the same ordered stage pipeline as ``rh_model.model.simulate``
    expressed through the named stages; behaviourally identical.
    """
    x_grid, theta_grid = params.x_grid, params.theta_grid

    s_x, s_theta = suppressive_kernel.run(
        x_grid,
        theta_grid,
        params.suppressive_field_size,
        params.suppressive_tuning_width,
        params.theta_period,
    )
    E = stimulus_drive.run(
        stimuli,
        x_grid,
        theta_grid,
        params.stimulus_size,
        params.stimulus_tuning_width,
        params.theta_period,
        params.stimulation_field_size,
        params.stimulation_tuning_width,
    )
    if params.baseline_modulated_by_attention != 0.0:
        E = E + params.baseline_modulated_by_attention
    A = attention_field.run(
        attention_condition,
        x_grid,
        theta_grid,
        params.attention_field_size,
        params.peak_attention_gain_gamma,
        params.tuning_width,
        params.theta_period,
    )
    S = suppression.run(s_x, s_theta, A, E)
    R = normalization.run(
        A, E, S, params.sigma, params.threshold_T,
        variant=params.normalization_variant,
    )
    if params.baseline_unmodulated != 0.0:
        R = R + params.baseline_unmodulated
    return readout.run(
        R, x_grid, theta_grid, params.recorded_x, params.recorded_theta
    )


def run_crf(
    stimulus_size: float,
    attention_field_size: float,
    gamma: float,
    regime: str,
    contrasts,
    *,
    tuning_width: float = 30.0,
) -> dict:
    """Calibrated attended/ignored 1D contrast-response functions.

    The caller supplies ONLY scientific parameters. The per-regime calibration
    is the Fig-2A (contrast-gain) vs Fig-2B (response-gain) GEOMETRY (the
    attention-field σ, Table 1) — resolved INTERNALLY from
    implementation/calibration.yaml's ``regime.<regime>`` namespace; the
    dependent never sees or carries it, and there is no regime-conditional in
    the dependent's code. Under the faithful suppression mechanism (the separable
    space×feature pool, σ=1e-6, no per-panel gain — SQ-005/A-013) there is no
    suppression knob to expose: the regimes differ purely by geometry.

    The "attended" condition is spatial attention centered on the RF
    stimulus (orientation-unselective); "ignored" is attend-elsewhere,
    i.e. A ≈ 1 at the RF (A-002), modeled as both attention centers None.

    Returns the measurement record (single source of truth, §2) with the
    resolved-ledger hash for traceability.

    Citation: C-005, C-006, C-013 ; Assumption: A-001, A-002, A-006
    """
    if regime not in REGIMES:
        raise ValueError(f"regime must be one of {REGIMES}, got {regime!r}")

    # The regime selects the Fig-2A (contrast-gain) vs Fig-2B (response-gain)
    # GEOMETRY (Table-1 attention-field size — the only lever that distinguishes
    # the regimes under the faithful no-gain suppression mechanism). It is read
    # internally; the dependent passes only a regime NAME and carries no R&H
    # discretization knob. The caller's attention_field_size argument is the
    # scientific default for the named regime and is overridden by the regime's
    # canonical Table-1 size so the two regimes differ from identical caller args.
    cal = resolve_namespace(f"regime.{regime}")  # internal; not exposed
    contrasts = np.asarray(contrasts, dtype=float)

    overrides = dict(
        stimulus_size=float(stimulus_size),
        attention_field_size=float(cal["attention_field_size"]),
        peak_attention_gain_gamma=float(gamma),
        tuning_width=float(tuning_width),
    )

    attended = np.empty(contrasts.shape, dtype=float)
    ignored = np.empty(contrasts.shape, dtype=float)
    for i, c in enumerate(contrasts):
        params = default_params(**overrides)
        stimuli = [{"x": 0.0, "theta": 0.0, "contrast": float(c)}]
        attended[i] = _forward_response(
            params, stimuli, {"spatial_center": 0.0, "feature_center": None}
        )
        ignored[i] = _forward_response(
            params, stimuli, {"spatial_center": None, "feature_center": None}
        )

    rec = measurements.crf_pair_record(
        contrasts, attended, ignored, contrast_key="contrasts"
    )
    # Expose the canonical cross-model field names alongside the legacy
    # CRF-pair keys (the record is a superset; dependents read these).
    rec["attended_response"] = rec["attended_CRF"]
    rec["ignored_response"] = rec["unattended_CRF"]
    rec["regime"] = regime
    return rec


__all__ = ["run_crf", "REGIMES"]
