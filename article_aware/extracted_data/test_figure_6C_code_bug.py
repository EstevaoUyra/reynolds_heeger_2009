"""MUST-PASS tests for the Figure 6C feature-attention CODE_BUG (2026-06-03 audit).

Finding (tag CODE_BUG -> MUST-PASS per author-tests/SKILL.md):

  run_figure_6C builds the attend-opposite condition as a SPATIAL Gaussian
  centered at x=-50 TIMES a feature Gaussian. Because the attention field is
  A = 1 + (gamma-1)*G_x*G_theta, at the recorded neuron x=0 (far from x=-50,
  spatial size 30) the spatial factor G_x ~ 0, so A ~ 1 regardless of theta —
  feature attention NEVER reaches the recorded neuron. The two curves overlap
  (peak ratio ~1.01, no sharpening). The paper's feature-based attention is
  spatially GLOBAL: Fig 6 caption — "feature-based attention was matched to the
  stimulus in the receptive field"; panel_C.jpg shows clear sharpening.

  Empirically demonstrated in the finding (and reconfirmed here): making the
  condition feature-only (spatial flat) restores peak elevation 1.01 -> 1.31
  (paper ~1.1-1.3) and FWHM sharpening 133deg -> 104deg (vs 133 -> 118, i.e.
  negligible, today).

WHY MUST-PASS (satisfiable by the correct mechanism alone): the fix is a
mechanism correction, not a fit — construct the 6C attend-opposite field with a
feature-tuned theta component that is uniform/broad in x so it reaches the
recorded neuron. The peak-enhancement and sharpening targets below are exactly
what the FAITHFUL spatially-global feature attention produces (verified: the
feature-only field yields ratio 1.31 and FWHM 140->111 on this grid). The only
way to pass is to make the feature component reach the RF — the genuine fix the
finding prescribes. A figure-fitted gain cannot pass it (the spatial
confinement, not the gain, is the cause: "independent of suppression gain").

The tier tripwires in test_tier_figure_6.py (T-6C-Q-sharpen, T-6C-H-peakratio)
record the SAME divergence as INTENDED FAILURES against the digitized reference;
these MUST-PASS tests pin the mechanism target the implementer drives green.
They flip green together when the feature component reaches the RF.

NOTE ON 7C: the finding also says "Same spatial-confinement structure affects
Fig 7C's attend-nonpref condition" and asks to "do the same for 7C's
attend-nonpref." But run_figure_7C's attend_nonpref uses spatial_center=0 (AT
the RF), not x=-50, so the x-confinement mechanism described for 6C does not
apply there, and the finding gives NO verified 7C target value (unlike 6C's
1.31 / 104deg). Per author-tests/SKILL.md ("verify the target before you encode
it ... do not encode a wrong target the implementer would then chase"), the 7C
sub-claim is FLAGGED, not encoded here — see the final return message.

Evaluated on the implementation record (protocols.run_figure_6C). The expected
peak-enhancement / sharpening targets are the paper's (Fig-6 caption + digitized
panel_C ~1.11 ratio and a clearly narrower attended curve), not a re-derivation
from the same record the model draws from.
"""

from __future__ import annotations

import numpy as np

from neuromodels.framework.testing import deterministic_test
from rh_claim_helpers import fwhm
from rh_model import protocols


def _record():
    r = protocols.run_figure_6C(n_directions=49)
    theta = np.asarray(r["theta_stim_grid"], dtype=float)
    fixation = np.asarray(r["attend_fixation_tuning"], dtype=float)
    opposite = np.asarray(r["attend_opposite_stimulus_tuning"], dtype=float)
    return theta, fixation, opposite


def _peak_at_zero(theta: np.ndarray, curve: np.ndarray) -> float:
    return float(curve[int(np.argmin(np.abs(theta)))])


@deterministic_test(
    spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="T-6C-CODEBUG-peak-enhancement",
)
def test_feature_attention_reaches_recorded_neuron_peak_enhancement():
    """MUST-PASS (CODE_BUG): the attend-opposite (feature-based) curve is clearly
    enhanced at the preferred direction relative to attend-fixation.

    The paper's feature-based attention is spatially global, so it reaches the
    recorded neuron and elevates the preferred-direction response (digitized
    panel_C peak ratio ~1.11; the verified feature-only fix gives ~1.31). EXPECTED
    RED today: the spatial Gaussian at x=-50 strips the feature gain from the RF,
    so the curves overlap (peak ratio ~1.01). Drive green by making the feature
    component reach the RF — never by tuning suppression (the cause is spatial
    confinement, not gain). Threshold 1.08 is below the verified faithful 1.31 and
    the digitized 1.11, so the correct mechanism passes by construction; the
    current ~1.01 fails.
    """
    theta, fixation, opposite = _record()
    peak_ratio = opposite.max() / max(fixation.max(), 1e-12)
    assert peak_ratio >= 1.08, (
        "feature-based attention must reach the recorded neuron and elevate the "
        f"preferred-direction peak (paper/digitized ~1.11, faithful fix ~1.31); "
        f"got peak ratio {peak_ratio:.3f} (~1.01 == curves overlap). The attend-"
        "opposite field's spatial Gaussian at x=-50 zeroes the feature gain at the "
        "RF (x=0) — make the feature component spatially global so it reaches the "
        "recorded neuron. Do not tune suppression; the cause is spatial confinement."
    )


@deterministic_test(
    spec_ref="simulation_protocols.figure_6C", figure=6,
    claim_id="T-6C-CODEBUG-sharpening",
)
def test_feature_attention_sharpens_tuning_at_recorded_neuron():
    """MUST-PASS (CODE_BUG): feature-based attention NARROWS the attend-opposite
    tuning curve relative to attend-fixation (sharpening), and does so by a
    margin the spatially-confined build cannot reach.

    The paper sharpens the attended curve (Fig-6 caption; panel_C). The finding's
    verified feature-only fix narrows FWHM 133deg -> 104deg (a ~29deg, ~22%
    sharpening), whereas the confined build narrows it only ~133 -> 118 (~11%,
    negligible — an incidental side effect, not the feature mechanism). Require a
    real sharpening margin (>= 18deg on this grid; the faithful fix delivers ~30,
    the confined build only ~15). EXPECTED RED today. Drive green by making the
    feature gain reach the RF — not by tuning.
    """
    theta, fixation, opposite = _record()
    fwhm_fix = fwhm(fixation, theta)
    fwhm_opp = fwhm(opposite, theta)
    sharpening = fwhm_fix - fwhm_opp
    assert sharpening >= 18.0, (
        "feature-based attention must SHARPEN the recorded neuron's tuning "
        f"(faithful fix narrows FWHM by ~30deg, paper-clear); got only "
        f"{sharpening:.1f}deg (fix {fwhm_fix:.1f} -> opp {fwhm_opp:.1f}) — the "
        "incidental narrowing of a feature field that never reaches the RF. Make "
        "the feature component spatially global so it sharpens the recorded neuron."
    )
