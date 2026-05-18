"""Explore Figure 4C suppressive-pooling calibration.

Same family as Figure 2A/3C: the 1D suppressive spatial pooling (σ from
C-010/C-011) is too broad, so the two-stimulus-in-RF CRFs never saturate
and the nonpreferred-attention suppression gap fails to weaken at high
contrast. Sweep the A-006 suppressive_spatial_sigma scale (and gain) for
Figure 4C and report every Q-026..Q-029 predicate group.

Exploration only — no asserts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parents[1] / "src"
DATA = Path(__file__).resolve().parents[2] / "article_aware" / "extracted_data"
sys.path[:0] = [str(SRC), str(DATA)]

from rh_claim_helpers import half_max_contrast  # noqa: E402
from rh_model.model import default_params, simulate  # noqa: E402


def _run_4c(gain, sigma, sup_tw=180.0, sup_scale=1.0, n=8, c_nonpref=0.5):
    contrasts = np.logspace(np.log10(0.01), np.log10(1.0), n)
    att = np.zeros(n)
    unatt = np.zeros(n)
    for i, cp in enumerate(contrasts):
        ov = dict(
            stimulus_size=5.0, attention_field_size=5.0,
            peak_attention_gain_gamma=5.0, tuning_width=20.0,
            suppressive_drive_gain=gain, sigma=sigma,
            suppressive_tuning_width=sup_tw,
            suppressive_spatial_sigma_scale=sup_scale,
        )
        stim = [
            {"x": 0.0, "theta": 0.0, "contrast": float(cp)},
            {"x": 0.0, "theta": 180.0, "contrast": c_nonpref},
        ]
        att[i] = simulate(stim, {"spatial_center": 0.0, "feature_center": 180.0},
                          default_params(**ov))["response"]
        unatt[i] = simulate(stim, {"spatial_center": None, "feature_center": None},
                            default_params(**ov))["response"]
    return contrasts, att, unatt


def _preds(c, att, unatt):
    pm = 100.0 * (att - unatt) / unatt
    fls = lambda v: float(np.diff(v)[-1] / np.diff(np.log(c))[-1])
    mls = lambda v: float(np.max(np.diff(v) / np.diff(np.log(c))))
    ng = (unatt - att) / unatt
    a_half = half_max_contrast(att, c)
    u_half = half_max_contrast(unatt, c)
    q026 = bool(np.all(att <= unatt + 1e-10) and pm.min() < -1.0)
    q027 = bool(a_half > 1.05 * u_half and att[-1] >= 0.80 * unatt[-1])
    absm = np.abs(pm)
    pk = int(np.argmax(absm))
    q028 = bool(0 <= pk < len(absm) - 1 and absm[-1] < 0.95 * absm[pk]
                and absm[: len(absm) // 2].max() >= absm[-1])
    q029 = bool(
        att[-1] > att[0] and unatt[-1] > unatt[0]
        and fls(att) < 0.95 * mls(att) and fls(unatt) < 0.95 * mls(unatt)
        and ng[-1] < ng.max() and ng[-1] <= 1.10 * ng[-2]
    )
    return q026, q027, q028, q029, att[-1] / unatt[-1], a_half / u_half


print("Confirming ONLY the C-011 suppressive_tuning_width (sup_tw=180) "
      "moves 4C; gain/sigma held at a representative point.\n")
print(f"{'sup_tw':>7} {'gain':>5} {'sigma':>6} {'Q026':>5} {'Q027':>5} "
      f"{'Q028':>5} {'Q029':>5} {'a[-1]/u[-1]':>11} {'aH/uH':>6}")
for sup_tw in (180.0, 120.0, 90.0, 60.0, 45.0, 30.0):
    for gain in (8.0, 5.0):
        c, a, u = _run_4c(gain, 0.05, sup_tw=sup_tw)
        q26, q27, q28, q29, recov, shift = _preds(c, a, u)
        flag = "  <== ALL GREEN" if (q26 and q27 and q28 and q29) else ""
        print(f"{sup_tw:>7} {gain:>5} {0.05:>6} {str(q26):>5} {str(q27):>5} "
              f"{str(q28):>5} {str(q29):>5} {recov:>11.3f} {shift:>6.3f}{flag}")
