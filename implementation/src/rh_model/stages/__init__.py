"""Reynolds & Heeger 2009 — named, typed-contract forward stages.

ARCHITECTURE.md §1: a model is an ordered list of named stages; the
contract (consumes/produces with shapes AND units, citation/assumption,
the ledger param names) is the primary artifact.

R&H is **feedforward** — there is NO ODE integrator/solver stage (stated
explicitly in model_spec.yaml `pipeline.integrator: none`). Each stage is
a pure function of its `consumes` plus resolved ledger `params`; no stage
contains a tunable numeric literal (numbers come from the §3 ledgers via
``rh_model.calibration`` / ``ModelParams``).

These stages wrap the numerically-validated kernels in ``rh_model.model``
unchanged (this is a STRUCTURE migration — behavior is byte-for-behavior
identical). The primitive stages here are the clean reuse surface for
dependents (carrasco2021 reuses them directly); a dependent must NOT reach
into a calibrated protocol — see ``rh_model.crf_protocol`` for the
formalized calibrated entry point.

Stage order (model_spec.yaml `pipeline`):
  1. suppressive_kernel   2. stimulus_drive   3. attention_field
  4. suppression          5. normalization    6. readout
"""

from __future__ import annotations

from . import (
    attention_field,
    normalization,
    readout,
    stimulus_drive,
    suppression,
    suppressive_kernel,
)

__all__ = [
    "suppressive_kernel",
    "stimulus_drive",
    "attention_field",
    "suppression",
    "normalization",
    "readout",
]
