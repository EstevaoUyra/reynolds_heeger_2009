"""Explore Figure 2A calibration: which (suppressive_drive_gain,
suppressive_spatial_sigma_scale) make the 2A CRFs saturate by the
high-contrast endpoint while keeping every other Figure 2 predicate green.

Exploration only — no asserts (an assert would make this a test). Run:
    python implementation/sanity_checks/check_fig2_saturation.py

Hypothesis under test: the suppressive spatial pooling (σ=20, C-010/C-011)
is too broad in the 1D protocol, so S grows too slowly with contrast and the
CRF never bends over within [0.01, 1]. Narrowing the effective pooling
(A-006 scale) or raising the SQ-001 gain should pull the half-saturation
contrast c* = σ/(gain·k2) well below 1.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parents[1] / "src"
DATA = Path(__file__).resolve().parents[2] / "article_aware" / "extracted_data"
sys.path[:0] = [str(SRC), str(DATA)]

from rh_claim_helpers import half_max_contrast, value_at  # noqa: E402
from rh_model.model import default_params, simulate  # noqa: E402


def _sweep(stim_size, attn_size, gain, sup_scale, baseline_unmod, n=8):
    contrasts = np.logspace(np.log10(0.01), np.log10(1.0), n)
    att = np.zeros(n)
    unatt = np.zeros(n)
    for i, c in enumerate(contrasts):
        ov = dict(
            stimulus_size=stim_size,
            attention_field_size=attn_size,
            peak_attention_gain_gamma=2.0,
            tuning_width=30.0,
            suppressive_drive_gain=gain,
            suppressive_spatial_sigma_scale=sup_scale,
            baseline_unmodulated=baseline_unmod,
        )
        stim = [{"x": 0.0, "theta": 0.0, "contrast": float(c)}]
        att[i] = simulate(stim, {"spatial_center": 0.0, "feature_center": None},
                          default_params(**ov))["response"]
        unatt[i] = simulate(stim, {"spatial_center": None, "feature_center": None},
                            default_params(**ov))["response"]
    return contrasts, att, unatt


def _predicates(contrasts, att, unatt):
    """Mirror the deterministic 2A assertions; return dict of bool/values."""
    def fls(curve):
        return float(np.diff(curve)[-1] / np.diff(np.log(contrasts))[-1])

    def mls(curve):
        return float(np.max(np.diff(curve) / np.diff(np.log(contrasts))))

    res = {}
    res["monotonic"] = bool(
        np.all(np.diff(att) >= -1e-10) and np.all(np.diff(unatt) >= -1e-10)
    )
    # saturating: final slope < 0.95 * max slope, and near-saturation by c=0.5
    sat_ok = True
    for curve in (att, unatt):
        half_v = value_at(contrasts, curve, 0.5)
        sat_ok &= fls(curve) < 0.95 * mls(curve)
        sat_ok &= (curve[-1] - half_v) / half_v < 0.35
    res["saturating"] = bool(sat_ok)
    res["fls/mls(unatt)"] = round(fls(unatt) / mls(unatt), 3)
    res["fls/mls(att)"] = round(fls(att) / mls(att), 3)
    # left-shift without response gain
    a_half = half_max_contrast(att, contrasts)
    u_half = half_max_contrast(unatt, contrasts)
    scale = float(np.concatenate([att, unatt]).max() - np.concatenate([att, unatt]).min())
    final_sep = att[-1] - unatt[-1]
    peak_sep = float(np.max(att - unatt))
    res["leftshift"] = bool(
        np.all(att >= unatt - 1e-10)
        and a_half < 0.80 * u_half
        and final_sep < 0.25 * scale
        and final_sep < 0.95 * peak_sep
        and att[-1] < 1.35 * unatt[-1]
    )
    res["a_half/u_half"] = round(a_half / u_half, 3)
    # percent modulation peaks then falls
    pm = 100.0 * (att - unatt) / unatt
    peak = int(np.argmax(pm))
    res["pm_peak_falls"] = bool(
        0 < peak < len(pm) - 2
        and contrasts[peak] <= 1.25 * a_half
        and pm[-1] < 0.40 * pm[peak]
        and pm[-1] < pm[0]
    )
    return res


if __name__ == "__main__":
    print("Figure 2A spec params: stim=3, attn=30, gamma=2  (sigma default 0.1)\n")
    print(f"{'gain':>5} {'supScale':>8} {'sat':>4} {'lshift':>6} {'pmPk':>5} "
          f"{'fls/mls(u)':>10} {'fls/mls(a)':>10} {'aH/uH':>6}")
    for sup_scale in (0.45, 0.5, 0.55, 0.6, 0.65, 0.7):
        for gain in (3.0, 3.5, 4.0, 4.5, 5.0):
            c, a, u = _sweep(3.0, 30.0, gain, sup_scale, 0.01)
            r = _predicates(c, a, u)
            flag = "  <== ALL GREEN" if (
                r["monotonic"] and r["saturating"] and r["leftshift"] and r["pm_peak_falls"]
            ) else ""
            print(f"{gain:>5} {sup_scale:>8} "
                  f"{str(r['saturating']):>4} {str(r['leftshift']):>6} "
                  f"{str(r['pm_peak_falls']):>5} "
                  f"{r['fls/mls(unatt)']:>10} {r['fls/mls(att)']:>10} "
                  f"{r['a_half/u_half']:>6}{flag}")
