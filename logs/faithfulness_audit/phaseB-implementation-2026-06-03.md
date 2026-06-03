# Phase-B implementation — reynolds_heeger_2009

- Date: 2026-06-03
- Role: Phase-B implementer (paper-blind). Built ONLY to the
  `phaseA-contract-update-2026-06-03.md` contract, the updated
  `pseudocode/figure_4_protocol.md`, `spec/model_spec.yaml`
  (rendering_conventions) and `assumptions.yaml` A-012. Did NOT read `paper/`.
  Did NOT edit `article_aware/` or any test.
- Posture: implement the SPECIFIED mechanism only. No parameter tuned to fit a
  curve. Genuine magnitude divergences left RED (GUARD).

---

## Code changes (three, per build order)

### 1. Fig 4C — spatial attention field
`implementation/src/rh_model/protocols.py::run_figure_4C`

- `attended` condition changed from the narrow feature-tuned field
  `{"spatial_center": 0.0, "feature_center": 180.0}` to a SPATIAL field at the
  RF: `{"spatial_center": 0.0, "feature_center": None}` (flat/uniform over θ),
  so the gain γ boosts BOTH colocated stimuli — including the recorded θ=0
  neuron's preferred drive (A-012). `unattended` unchanged.
- Dropped the now-removed `sigma` and `suppressive_tuning_width` overrides from
  the `overrides` dict (they no longer exist in calibration). 4C now uses the
  cited 180° suppressive tuning (C-011) and the global σ.
- Docstring rewritten: cites C-015/C-019 and A-012; the old SQ-004 note removed.

### 2. Deleted the SQ-004 overrides
`implementation/calibration.yaml`

- Removed `figure_4C.suppressive_tuning_width: 75.0` and `figure_4C.sigma: 0.05`
  entirely. `figure_4C.suppressive_drive_gain: 8.0` kept. Replaced the section
  header comment to record that the overrides are RETIRED per A-012 (they were
  symptoms of the wrong suppression regime).

### 3. Shared-scale view normalization
`implementation/src/rh_model/views.py`

- Replaced the per-pair-to-1.0 `_normalized_pair(att, una)` with a
  GROUP-shared-scale version `_normalized_pair(panel_id, att, una)` that divides
  both curves by ONE common `_crf_group_scale(panel_id)` per CRF figure-group
  (2A/2B, 3C/3F, 4C/4E). The scale mirrors
  `rh_tier_helpers.group_scale` exactly: `model_group_peak / reference_group_peak`
  (memoized per group; reference peak skips right-axis percent curves).
- `_plot_normalized_crf_with_modulation` gained a `normalize: bool = True`
  parameter. Model render (default) applies the group scale; the
  digitized-reference render (`_crf_reference_panel`) passes `normalize=False`
  because the digitized curves are ALREADY on the shared sub-1.0 scale — they
  are NOT passed through a per-pair normalizer.
- Tuning panels 5C/6C/7C untouched (`_plot_tuning` shared-peak-within-panel).

---

## Verification

Re-render: `PYTHONPATH=implementation/src python -m rh_model.views` — all 7
model figures + 6 reference figures written to `implementation/figure_outputs/`.

### (a) 4C facilitation — YES

Run `protocols.run_figure_4C(n_contrasts=24)` (raw response, before render scale):

- Attended ≥ unattended at EVERY contrast (gap min +0.049, max +0.98). Positive.
- %-modulation positive throughout: peaks **+101.1%** at the lowest contrast
  (c_pref=0.01), declines monotonically to **+50.8%** at c=1.0 (largest at low
  contrast, declining toward high — the contrast-gain signature).
- Left shift: attended half-max at c≈0.239 vs unattended c≈0.293 (attended curve
  is the leftward/higher one).

The facilitation SIGN, ordering, left-shift, and declining-positive-modulation
shape all match the contract (A-012, C-019). NOTE the MAGNITUDE is larger than
the paper's ~+36% — the model facilitates ~+101% at low contrast. That is a
genuine magnitude divergence under the correct mechanism, NOT tuned away (see
RED #3 below).

### (b) Shared-scale Fig 2 — 2B renders ABOVE 2A — YES

Group scale (figure_2) = 3.684. On the shared scale:
- 2A attended plateau ≈ **0.338**
- 2B attended plateau ≈ **0.858**  → 2B above 2A confirmed.
- 2A unattended ≈ 0.318; 2B unattended ≈ 0.605.

2B's attended ceiling (0.858) matches digitized ~0.85; 2A's (0.338)
under-saturates vs digitized ~0.615 (the surfaced 2A red, RED #2).

### (c) Tier-test tally — 99 passed, 10 failed, 15 xfailed, 4 xpassed

All 10 failures classify as intended/genuine divergences (none is a regression
introduced by hacking the mechanism):

| # | Test | Classification |
|---|------|----------------|
| 1 | `test_tier_figure_2::test_2B_attended_ceiling_matches_digitized` | **Intended RED** — `paper_issue`-flagged 2A under-saturation (0.338 vs 0.615); 2B half passes. Finding-1 side effect, surfaced by the shared scale. |
| 2 | `test_tier_figure_4::test_4E_modulation_stays_within_paper_axis` | **Intended RED** — 4E %-mod overflows the paper's (0,100) axis (documented genuine divergence). |
| 3 | `test_panel_axes::test_figure_4E_modulation_within_paper_axis` | **Intended RED** — same 4E overflow, axis-render check. |
| 4 | `test_tier_figure_5::test_5C_peak_ratio_matches_digitized` | **Genuine RED** — 5C gain divergence (untouched). |
| 5 | `test_tier_figure_6::test_6C_sharpening_present_at_peak` | **Genuine RED** — 6C sharpening absent (untouched). |
| 6 | `test_tier_figure_6::test_6C_peak_ratio_matches_digitized` | **Genuine RED** — 6C gain ~1.01 vs ~1.11 (untouched). |
| 7 | `test_tier_figure_7::test_7C_variable_over_fixation_ratio_matches_digitized` | **Genuine RED** — 7C gain ~3.3 vs ~1.4 (untouched). |
| 8 | `test_figure_4C::test_crfs_saturate_and_facilitation_gap_narrows_at_high_contrast` (Q-029) | **Genuine RED (newly surfaced)** — under the cited 180° suppressive tuning + global σ (overrides removed), 4C does NOT bend over within [0.01,1]: final log-slope == max log-slope. This is the saturation magnitude divergence the SQ-004 override used to mask. GUARD: leave red, do not re-add an override. |
| 9 | `test_panel_axes::test_figure_4C_data_within_paper_axis` | **Genuine RED (newly surfaced)** — the 4C facilitation %-mod reaches ~+101% at low contrast, just over the paper's (0,100) right axis. Magnitude divergence of the correct (facilitation) mechanism; the paper's ~+36% is smaller. Not hacked. |
| 10 | `test_figure_4E::test_figure_4C_and_4E_attention_effects_have_opposite_signs` (Q-053) | **Contract-staleness RED** — this test (in `test_figure_4E.py`, NOT updated by Phase A) still asserts 4C SUPPRESSION (`attended_c <= unattended_c`, C-021), the OLD wrong sign. With the correct facilitation 4C it now (correctly) fails. Phase A flipped the 4C tests in `test_figure_4C.py`/`test_tier_figure_4.py` but did not update this 4E-file cross-check. I did NOT edit it (no test edits allowed). Flag for Phase A. |

GREENED by this Phase B (were RED at handoff):
- `test_figure_4C`: Q-026 (`test_attending_nonpreferred_in_rf_increases_response`),
  Q-027 (`test_attended_crf_is_left_shifted`),
  Q-028 (`test_percent_modulation_does_not_peak_at_highest_contrast`) — all PASS.
- `test_tier_figure_4`: `test_4C_attended_above_unattended`,
  `test_4C_mid_contrast_separation_matches_digitized`,
  `test_4C_modulation_positive_and_declines_to_high_contrast` (xpass) — all PASS.
- `test_tier_figure_2`: `test_2B_attended_ceiling_above_2A_ceiling` (qualitative
  shared-scale ceiling claim) — PASS.

---

## GUARD compliance

No parameter was tuned to fit a curve. The 4C spatial field is the specified
mechanism; the SQ-004 overrides were deleted, not replaced. The newly-surfaced
4C reds (no high-contrast saturation; +101% > +36% facilitation magnitude) are
left RED as findings — re-adding the 75°/σ override is exactly the hack this
build undoes. The standing 4E/5C/6C/7C magnitude reds are untouched.

## Flag for Phase A (contract owner)

`test_figure_4E.py::test_figure_4C_and_4E_attention_effects_have_opposite_signs`
(Q-053) still encodes the retired 4C suppression sign (C-021) and was not
flipped alongside the other 4C tests. It now fails because 4C is correctly
facilitatory. Phase B cannot edit it; it needs the same Finding-2 update.
