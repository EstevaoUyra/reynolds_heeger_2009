"""Reynolds & Heeger (2009) Normalization Model of Attention.

Implementation follows article_aware/spec/model_spec.yaml and the
ARCHITECTURE.md shape: named typed-contract ``stages`` (§1), a pure
``measurements`` record (§2, single source of truth), declarative
``views`` (§2), a §3 two-ledger ``calibration`` (paper-derived in
article_aware/spec/calibration.yaml; implementation-side in
implementation/calibration.yaml), and the formalized calibrated 1D-CRF
entry point ``crf_protocol.run_crf`` — the clean cross-model reuse
surface (a dependent passes only scientific params + a regime name and
carries zero discretization knobs / zero regime-conditional).

The forward-primitive functions are still exported at the top level so a
dependent may reuse the clean primitive stages directly (carrasco2021
pattern). A dependent must NOT reach into a calibrated protocol — use
``crf_protocol.run_crf`` instead (ARCHITECTURE.md §1).
"""

from . import (
    calibration,
    crf_protocol,
    helpers,
    measurements,
    protocols,
    stages,
    views,
)
from .model import (
    ModelParams,
    build_attention_field,
    build_stimulus_drive,
    build_suppressive_kernel,
    compute_output,
    compute_suppressive_drive,
    default_params,
    simulate,
)

# `figures` is a back-compat shim re-exporting `views`.
from . import figures  # noqa: E402

__all__ = [
    "ModelParams",
    "build_attention_field",
    "build_stimulus_drive",
    "build_suppressive_kernel",
    "compute_output",
    "compute_suppressive_drive",
    "default_params",
    "simulate",
    "protocols",
    "helpers",
    "stages",
    "measurements",
    "views",
    "figures",
    "calibration",
    "crf_protocol",
]
