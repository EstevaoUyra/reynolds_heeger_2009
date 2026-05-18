"""Stage: normalization.

Contract (model_spec.yaml stages.normalization):
  consumes:
    A         : (n_th, n_x) float  units: dimensionless gain (≥ 1)
    E         : (n_th, n_x) float  units: arbitrary drive (≥ 0)
    S         : (n_th, n_x) float  units: arbitrary drive (≥ 0)
  produces:
    R         : (n_th, n_x) float  units: arbitrary response (≥ 0)
  params (ledger):
    model.sigma          (A-001, paper/spec ledger)
    model.threshold_T    (A-003, paper/spec ledger)
    figure_*.sigma       (SQ-001, impl ledger — per-protocol override)
  citation: C-005 (EQ-5)
  assumption: A-001 (sigma value), A-003 (T = 0)

R = ⌊(A·E) / (S + σ)⌋_T. Pure. σ and T arrive resolved from the ledger
(global value, or a per-protocol implementation-side override) — this
stage holds no tunable literal. This is the swappable normalization
stage exercised by the §5(4) modification smoke test
(``RH_NORMALIZATION_VARIANT`` / config). Wraps the unchanged kernel
``rh_model.model.compute_output`` for the default variant.
"""

from __future__ import annotations

import numpy as np

from ..model import compute_output

#: Config-selectable variant. The default ("divisive") is the paper's
#: Eq. 5. ``identity_suppression`` is a trivial variant for the §5(4)
#: modification smoke test: it drops the suppressive term (S → 0) so the
#: pipeline/record/figure regenerate with a config-only change and ZERO
#: edits to unrelated code. Selected by the ``variant`` argument the
#: protocol passes from config — never by editing this module.
VARIANTS = ("divisive", "identity_suppression")


def run(
    A: np.ndarray,
    E: np.ndarray,
    S: np.ndarray,
    sigma: float,
    threshold_T: float,
    variant: str = "divisive",
) -> np.ndarray:
    """R(x,θ) = ⌊(A·E) / (S + σ)⌋_T  (variant='divisive', the paper Eq. 5).

    variant='identity_suppression' replaces S by 0 (trivial swap variant
    for the modification smoke test; config-only, no unrelated edits).

    Citation: C-005 ; Assumption: A-001, A-003
    """
    if variant not in VARIANTS:
        raise ValueError(f"normalization variant must be one of {VARIANTS}")
    if variant == "identity_suppression":
        S = np.zeros_like(S)
    return compute_output(A, E, S, sigma, threshold_T)


__all__ = ["run", "VARIANTS"]
