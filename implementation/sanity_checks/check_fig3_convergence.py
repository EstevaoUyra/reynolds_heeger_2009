"""Explore Figure 3C/3F suppressive-pooling calibration.

Same root cause as Figure 2A: the suppressive spatial pooling (σ from
C-010/C-011) is too broad in the 1D protocol, so the contrast-gain 3C CRFs
never converge at high contrast (absolute attended-unattended difference
stays near its peak instead of falling below 75% of it). 3F is
response-gain-like (small attention field) and must keep a larger
high-contrast separation than 3C.

Exploration only — no asserts. Sweeps the A-006 suppressive_spatial_sigma
scale for 3C (and a couple of 3F values), reports the two failing
predicates plus guards against regressing the passing ones.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path[:0] = [str(SRC)]

from rh_model import protocols  # noqa: E402
from rh_model.model import default_params, simulate  # noqa: E402


def _panel(stim, attn, gain, sup_scale, base_mod, base_unmod, n=8):
    contrasts = np.logspace(np.log10(0.01), np.log10(1.0), n)
    att = np.zeros(n)
    unatt = np.zeros(n)
    for i, c in enumerate(contrasts):
        ov = dict(
            stimulus_size=stim, attention_field_size=attn,
            peak_attention_gain_gamma=2.0, tuning_width=30.0,
            suppressive_drive_gain=gain,
            suppressive_spatial_sigma_scale=sup_scale,
            baseline_modulated_by_attention=base_mod,
            baseline_unmodulated=base_unmod,
        )
        s = [{"x": 0.0, "theta": 0.0, "contrast": float(c)}]
        att[i] = simulate(s, {"spatial_center": 0.0, "feature_center": None},
                          default_params(**ov))["response"]
        unatt[i] = simulate(s, {"spatial_center": None, "feature_center": None},
                            default_params(**ov))["response"]
    return contrasts, att, unatt


def _metrics(c, att, unatt):
    diff = att - unatt
    pm = 100.0 * (att - unatt) / unatt
    dpk = int(np.argmax(diff))
    ppk = int(np.argmax(pm))
    return {
        "diff": diff, "pm": pm,
        "conv_3C": diff[-1] < 0.75 * diff[dpk],          # failing 3C predicate
        "pm_lowweight": (ppk < len(pm) // 2) and (pm[-1] < 0.5 * pm[ppk]),
        "diff_pk_ok": dpk < len(diff) - 1,
        "att_ge_unatt": bool(np.all(att >= unatt - 1e-9)),
        "monotonic": bool(np.all(np.diff(att) >= -1e-10)
                          and np.all(np.diff(unatt) >= -1e-10)),
        "diff_last": float(diff[-1]),
        "diff_ratio": float(diff[-1] / diff[0]),
    }


# 3F baseline (unchanged): stim=7 attn=7 gain=8 base_mod=0.05 base_unmod=0.05
cf, af, uf = _panel(7.0, 7.0, 8.0, 1.0, 0.05, 0.05)
mf = _metrics(cf, af, uf)

print("3F (unchanged, sup_scale=1.0): "
      f"diff_last={mf['diff_last']:.4f} diff_ratio={mf['diff_ratio']:.3f}\n")
print(f"{'3C sup_scale':>12} {'conv_3C':>8} {'pm_lw':>6} {'mono':>5} "
      f"{'a>=u':>5} {'3C diff_last':>12} {'3F>3C last':>10} {'3F>3C ratio':>11}")
for sup_scale in (1.0, 0.8, 0.7, 0.6, 0.55, 0.5, 0.45, 0.4, 0.3):
    cc, ac, uc = _panel(5.0, 30.0, 5.0, sup_scale, 0.02, 0.1)
    mc = _metrics(cc, ac, uc)
    f_gt_c_last = mf["diff_last"] > mc["diff_last"]
    f_gt_c_ratio = mf["diff_ratio"] > mc["diff_ratio"]
    all_green = (mc["conv_3C"] and mc["pm_lowweight"] and mc["monotonic"]
                 and mc["att_ge_unatt"] and mc["diff_pk_ok"]
                 and f_gt_c_last and f_gt_c_ratio)
    flag = "  <== ALL GREEN" if all_green else ""
    print(f"{sup_scale:>12} {str(mc['conv_3C']):>8} "
          f"{str(mc['pm_lowweight']):>6} {str(mc['monotonic']):>5} "
          f"{str(mc['att_ge_unatt']):>5} {mc['diff_last']:>12.4f} "
          f"{str(f_gt_c_last):>10} {str(f_gt_c_ratio):>11}{flag}")
