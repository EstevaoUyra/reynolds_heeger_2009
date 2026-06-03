# Faithfulness audit — POST-CHANGE re-audit — reynolds_heeger_2009

- Date: 2026-06-03
- Role: post-build faithfulness auditor (report-only; edited no code/tests/calibration/contract; wrote no APPROVED, marked nothing `reproduced`)
- Trigger: an improvement pass claims it (a) flipped Fig 4C from suppression to facilitation via a spatial attention field, (b) put the CRF figures on a shared response scale, (c) deleted the SQ-004 4C suppressive-tuning override. **All three re-derived independently below — none taken on trust.**
- Standard: `paper/extracted_text.md` (Eqs 1–8, Table 1, verbatim captions) + paper panel JPGs + the digitized references `panel_<X>_digitized.json` (the binding quantitative stand-in for the paper curves).
- Step 0 freshness: re-rendered ALL figures myself (`python -m rh_model.views`, exit 0) — 7 model PNGs + 6 reference PNGs. Judged the fresh renders, not committed snapshots. Numbers below are from running `protocols.run_figure_*` directly against the live source in `implementation/src/rh_model/`.

---

## Verification of the three claimed changes (independent re-derivation)

### (a) Fig 4C direction — VERIFIED FIXED (now facilitation)
`protocols.run_figure_4C` now builds the "attend nonpreferred-in-RF" condition as a **spatial** field at the RF, **flat over θ** (`attended = {"spatial_center": 0.0, "feature_center": None}`, protocols.py:214; documented as Assumption A-012, protocols.py:187-198). Measured (8-pt sweep):

| contrast | attended | unattended | % mod |
|---|---|---|---|
| 0.010 | 0.097 | 0.048 | +101.1 |
| 0.139 | 1.034 | 0.561 | +84.4 |
| 1.000 | 2.910 | 1.930 | +50.8 |

attended ≥ unattended at **every** contrast; mean %-mod **+82.5%**; %-mod **positive and declining** (left→right); attended half-max **0.268** vs unattended **0.518** → **leftward shift**. This is the paper's 4C signature (contrast-gain facilitation). The prior pass's −23.6% suppression / right-shift is **gone**. **Direction fix is real.**

### (b) Shared-scale CRF normalization — VERIFIED FIXED
`views._normalized_pair` (views.py:305-319) now divides BOTH curves of a panel by ONE group-wide constant `_crf_group_scale` (groups: 2A/2B, 3C/3F, 4C/4E; views.py:228-302), mapping the model group's overall peak onto the digitized group's overall peak — replacing the old per-pair-to-1.0 pinning. Verified for Fig 2:

| | raw model max | rendered plateau (shared scale) | digitized target |
|---|---|---|---|
| 2A attended | 1.247 | **0.338** | 0.615 |
| 2B attended | 3.161 | **0.858** | 0.852 |
| 2B unattended | 2.39 | 0.605 | 0.605 |

2B's attended plateau (0.86) now renders **visibly above** 2A's (0.34) on one shared 0–1 axis — confirmed in the rendered `figure_2.png`. The reference render is no longer corrupted: `render_figure_2_reference` plots the digitized curves with `normalize=False`, so REF 2A=0.615 / REF 2B=0.852 now match their JSON (the prior pass's 1.000/0.993 corruption is fixed). **Shared-scale fix is real and the reference render is repaired.**

### (c) SQ-004 4C override deletion — VERIFIED DELETED
No `figure_4C.sigma` and no 75° feature/suppressive-tuning override remain anywhere in `implementation/src/` or `implementation/calibration.yaml`. The calibration ledger explicitly records the retirement (calibration.yaml:201-207: *"tuning width (75°) and the figure_4C.sigma override are RETIRED … symptoms of the wrong (suppression) 4C regime"*). `run_figure_4C` uses only the cited Table-1 knobs + the global σ. **Override deletion is real.**

**Side-effect of (c)/this pass — calibration retune (see Finding R1).** While verifying, I found the same pass *also* raised three suppressive-drive gains: `figure_2A` 4→12, `figure_2B` 4→6, `figure_4E` 4→8 (calibration.yaml notes dated 2026-06-03). These are `audited:false`, SQ-001-sourced, and the regime surface (`regime.contrast_gain.*`) was deliberately frozen at the original gain 4 so the hermann2010 reuse surface is not perturbed. Not a paper-distance defect, but it is undisclosed scope in a "direction + normalization + override-delete" change and is logged below.

---

## Equation & parameter layer — re-checked, FAITHFUL (unchanged by this pass)

Operator-by-operator against the paper (the change touched protocols/views/calibration, not the stage equations):

| Paper eq | Code locus | Status |
|---|---|---|
| Eq.5 `R=⌊A·E/(S+σ)⌋_T` | `model.compute_output` / `stages/normalization` | FAITHFUL |
| Eq.6 `S=s∗(A·E)` | `model.compute_suppressive_drive` | FAITHFUL (pools product A·E) |
| Eq.2 `∫s dxdθ=1` | `model.build_suppressive_kernel` | FAITHFUL |
| Eq.7 contrast-gain (γ scales A·E in num+denom) | sim path | FAITHFUL |
| A=1+(γ−1)·G_x·G_θ | `stages/attention_field.run` → `build_attention_field` | FAITHFUL to A-004/A-012 |

The A-012 4C remap is a **condition-mapping / attention-field-structure** change, not an equation change: the same `build_attention_field` now receives `feature_center=None` (flat-over-θ spatial gain) so γ reaches the recorded θ=0 neuron's numerator — the mechanistically clean reading of the M&T-2002 spatial-attention task. This is the fix the 4C investigation prescribed; it is faithful.

---

## Per-figure current verdicts

### Figure 1 — schematic — FAITHFUL
E×A÷S→R population structure correct; output enhances the attended (right) stimulus. Schematic; unchanged.

### Figure 2 (2A, 2B) — FAITHFUL direction/convention; 2A under-saturation now SURFACED — DIVERGENT (minor, magnitude)
- 2A contrast-gain signature (curves converge at high c, %-mod falls to ~0) and 2B response-gain signature (sustained separation, 2B attended ceiling above 2A) — both correct, and the **cross-panel ceiling claim (2B>2A) is now visible** thanks to the shared scale. This is the headline fix.
- **NEW divergence the shared scale revealed: 2A under-saturates.** Model 2A attended plateau **0.338** vs digitized **0.615** (~2× low). This is a *real* divergence, not a rendering artifact: the shared scale is a single group divisor, so it preserves the raw ratio (raw 2A 1.247 / 2B 3.161 = 0.39 = rendered 0.34/0.86). The per-pair-to-1.0 convention HID it (both panels were pinned to 1.0). Surfaced and pinned by `test_tier_figure_2.py::test_2B_attended_ceiling_matches_digitized` (RED, explicitly faithful-direction, do-not-tune). Severity minor (it does not invert the A-vs-B story); status DIVERGENT.

### Figure 3 (3C, 3F) — FAITHFUL (qualitative)
3C %-mod peaks low and converges; 3F sustained with largest absolute gap at high c; dashed twin axis present. Now also on the shared 3C/3F scale. No regression. FAITHFUL.

### Figure 4C — direction FAITHFUL; magnitude DIVERGENT (major)
- **Direction: FAITHFUL.** Facilitation, attended-above, leftward shift, positive declining %-mod (re-derived above). The prior sign inversion is resolved; this overturns the improvement-pass's open SUSPECTED-PAPER-ISSUE/condition-mapping finding for 4C — it is now correctly mapped.
- **Magnitude: DIVERGENT, major (confirmed as the brief predicted).** Model %-mod peaks **+101%** vs paper/digitized **~36%** (~3× too strong), and the attended/unattended gap is far too wide (rendered plateaus **0.60 / 0.40** vs digitized near-coincident **0.815 / 0.773**). The %-mod curve **overflows** the paper's (0,100) right axis (peak 101.1%) — surfaced by `test_panel_axes.py::test_figure_4C_data_within_paper_axis` (RED, NEW this pass). Additionally `test_figure_4C.py::test_crfs_saturate_and_facilitation_gap_narrows_at_high_contrast` (Q-029) is RED: the attended CRF only marginally bends (log-slope peaks 2.36 then 2.08) and does **not plateau** within [0.01,1], so the gap does not narrow toward saturation the way the paper's curves do. Faithful direction, divergent magnitude/shape; not a tuning target.

### Figure 4E — ordering FAITHFUL; %-mod overflow DIVERGENT (minor, standing)
attend-pref multiplicatively above attend-nonpref (ordering FAITHFUL). %-mod **310–390%** vs paper ~36–54%, overflowing the (0,100) axis — intended, pinned by `test_panel_axes.py::test_figure_4E_modulation_within_paper_axis` + `test_tier_figure_4.py` (RED). Unchanged by this pass. DIVERGENT minor.

### Figure 5C — shape FAITHFUL; peak ratio DIVERGENT (minor, standing)
Clean multiplicative scaling, no width change (FWHM att 66.0° = unatt 66.0°). Peak ratio **1.586** vs digitized ~1.1–1.4 — too strong. `test_tier_figure_5.py::test_5C_peak_ratio_matches_digitized` RED. Unchanged. DIVERGENT minor.

### Figure 6C — direction FAITHFUL; sharpening far too weak DIVERGENT (minor, standing)
Feature-based attention sharpens in the right direction but only **~6.9%** narrowing (FWHM 143.0°→133.1°) and peak ratio **1.009** (no scaling). Curves nearly overlap in the render. `test_tier_figure_6.py::test_6C_sharpening_present_at_peak` + `test_6C_peak_ratio_matches_digitized` RED. Unchanged. DIVERGENT minor.

### Figure 7C — ordering FAITHFUL; peak ratio DIVERGENT (minor, standing)
Ordering variable>fixation>nonpref correct (peaks 9.35 / 2.85 / 2.08). attend-variable/fixation peak ratio **3.28×** vs paper ~1.4 (>2× too strong). `test_tier_figure_7.py::test_7C_variable_over_fixation_ratio_matches_digitized` RED. Unchanged. DIVERGENT minor.

---

## FINDING R1 — undisclosed calibration retune rode along with this change — process/transparency, MINOR, not paper-distance
`figure_2A.suppressive_drive_gain` 4→12, `figure_2B` 4→6, `figure_4E` 4→8 were raised this pass (calibration.yaml notes, 2026-06-03) to make the rendered CRFs bend over more visibly. All `audited:false`, SQ-001-sourced, in the same regime as before; the `regime.contrast_gain.*` reuse surface was held at gain 4 ON PURPOSE so hermann2010 is not perturbed. Not a faithfulness defect (these are honest 1D-discretization knobs, not paper values), but it is scope beyond "direction + normalization + override-delete" and should be recorded as such. Note: even after the 2A gain→12, 2A still under-saturates (Fig 2 finding), so the retune did not paper over that divergence.

## No regressions found
- No figure the change touched moved in the wrong direction. The Fig-2/3/4 shared-scale convention did not break the 3C/3F or 4E qualitative signatures (verified renders + tests green where expected).
- The 4C remap did not perturb 4E (still ordering-faithful) or any tuning panel.
- 117 passed / 9 failed / 15 xfailed / 4 xpassed. **All 9 reds are intended faithful-direction magnitude/overflow tripwires** (2A ceiling, 4C axis-overflow, 4C non-saturation Q-029, 4E overflow ×2, 5C/6C/7C ratios, 6C sharpening) — each carries a `paper_issue=`/do-not-tune note. None is a silent re-greening, none asserts a paper-contradicting direction. The Step-4 laundered-contradiction that the prior pass flagged in `test_figure_4C.py` (Q-026/Q-027 asserting suppression/right-shift) is **gone** — the 4C tests now assert facilitation.

---

## Refute pass (each surviving finding defended against)
- *"4C is still wrong — maybe attended-above is a fluke of the sweep."* Refuted: attended≥unattended at all 8 (and 24) contrasts, +101%→+51% monotone-declining %-mod, half-max 0.27<0.52 — a robust contrast-gain left-shift matching the digitized panel direction. Direction fix survives.
- *"2A under-saturation is a shared-scale artifact."* Refuted: the shared scale is one group divisor; it preserves the raw 2A/2B plateau ratio (0.39), which already under-shoots in the raw model output. The divergence is in the model, exposed (not created) by the convention. Survives.
- *"4C magnitude (+101%) might be within digitization error of ~36%."* Refuted: 101% vs 36% is ~3×, the gap (0.60/0.40) vs near-coincident (0.815/0.773) is qualitatively wider, and the curve overflows the paper axis — far outside any digitization slack. Survives.
- *"The shared-scale reference might still be mis-rendered."* Refuted: REF 2A=0.615, REF 2B=0.852, REF 4C=0.815/0.773 all now equal their JSON to 3 d.p. (normalize=False path). The prior corruption is fixed. Survives.

---

## Verdict table (README-ready)

| Figure/panel | Status | One-line evidence |
|---|---|---|
| Fig 1 | FAITHFUL | E×A÷S→R schematic; output enhances attended stimulus |
| Fig 2A | DIVERGENT (minor, magnitude) | shared-scale convention now FAITHFUL, but surfaces 2A under-saturation: plateau 0.34 vs digitized 0.615 |
| Fig 2B | FAITHFUL | response-gain ceiling 0.86 now renders visibly above 2A on one shared axis (the A-vs-B claim) |
| Fig 3C | FAITHFUL | %-mod peaks low & converges; shared 3C/3F scale; dashed twin axis |
| Fig 3F | FAITHFUL | sustained %-mod, largest absolute gap at high c |
| Fig 4C | DIVERGENT (major, magnitude) — direction now FAITHFUL | facilitation/left-shift/+%-mod FIXED (was suppression); but +101% vs paper ~36%, gap too wide, %-mod overflows axis, CRF doesn't plateau |
| Fig 4E | DIVERGENT (minor, standing) | ordering FAITHFUL; %-mod 310–390% overflows paper (0,100) axis |
| Fig 5C | DIVERGENT (minor, standing) | multiplicative shape FAITHFUL; peak ratio 1.59 vs ~1.1–1.4 |
| Fig 6C | DIVERGENT (minor, standing) | sharpening direction FAITHFUL; only ~7% narrowing, peak ratio 1.01 (too weak) |
| Fig 7C | DIVERGENT (minor, standing) | ordering FAITHFUL; variable/fixation peak ratio 3.3× vs paper ~1.4 |
| Equations 5/6/2/7, kernel, attention-field, ledger quotes | FAITHFUL | operator-by-operator; A-012 4C remap is condition-mapping, not eq change |
| (process) calibration retune R1 | not paper-distance (minor) | 2A/2B/4E gains raised this pass; regime surface frozen for hermann2010 |

**Headline.** All three claimed fixes are REAL and FAITHFUL: (a) Fig 4C direction is corrected to facilitation (attended-above, left-shift, +%-mod) — the prior SUSPECTED-PAPER-ISSUE/laundered Q-026/Q-027 is resolved; (b) the shared-scale CRF convention is faithful and renders 2B's ceiling above 2A's, and the reference render is no longer corrupted; (c) the SQ-004 override is gone. **Remaining divergences are all MAGNITUDE, not direction:** 4C is still ~3× too strong (+101% vs ~36%, axis overflow, no plateau — MAJOR); 2A under-saturates (0.34 vs 0.615 — newly surfaced, minor); 5C/7C peak ratios and 4E %-mod overflow and 6C sharpening-too-weak are the standing minor magnitude reds. No regressions; the 9 failing tests are all intended faithful-direction tripwires. Overall model status: **partial** — direction/convention/equations faithful, magnitudes (esp. 4C) divergent.
