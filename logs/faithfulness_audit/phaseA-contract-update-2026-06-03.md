# Phase-A contract update — reynolds_heeger_2009

- Date: 2026-06-03
- Role: Phase-A contract editor (paper-aware). Edited `article_aware/` (spec,
  pseudocode, citations-usage, figure docs, tier/figure tests) and the
  `logs/` ledgers only. Did NOT touch `implementation/src/` (Phase B owns it).
- Sources: `improvement-pass-2026-06-03.md` (Finding 1 normalization),
  `figure_4C_investigation-2026-06-03.md` (Finding 2 condition mapping).
- Posture: encode the CORRECT mechanism and the paper's direction from the
  evidence. Did NOT tune parameters to fit a curve. The standing magnitude
  divergences (6C/5C/7C/4E) stay flagged and untouched.

---

## Finding ① — shared-scale normalization (contract side)

The paper renders each CRF figure-GROUP on ONE shared response axis (Fig 2's 2A
~0.615 and 2B ~0.85 on the same sub-1.0 scale; that ceiling difference is the
response-gain claim). Per-pair-to-1.0 normalization pinned every panel's top
curve to 1.0 and erased it. Contract changes:

- **`extracted_data/rh_tier_helpers.py`** — added the shared-scale machinery:
  `CRF_FIGURE_GROUPS` (figure_2 = {2A,2B}, figure_3 = {3C,3F}, figure_4 =
  {4C,4E}), `group_scale(figure,panel)` (one common divisor per group, mapping
  the model group's overall peak onto the reference group's overall peak), and
  `norm_pair_shared(att,una,fig,panel)`. The old per-pair `norm_pair` is kept
  but DEPRECATED in its docstring (do-not-use-for-CRF). `panel_model_curves`
  (the shape-deviation adapter) now uses `norm_pair_shared` for all six CRF
  panels.
- **`extracted_data/test_tier_figure_2.py`, `_3.py`, `_4.py`** — all CRF records
  switched from `norm_pair` to `norm_pair_shared`. Added two NEW Fig-2 tests
  asserting the cross-panel ceiling claim: `test_2B_attended_ceiling_above_2A_ceiling`
  (qualitative — PASSES: 2B 0.858 > 2A 0.338 on shared scale) and
  `test_2B_attended_ceiling_matches_digitized` (hard — 2B half passes; 2A half
  is EXPECTED RED, flagged `paper_issue`: the model's 2A under-saturates to ~0.34
  vs digitized ~0.615, a genuine magnitude divergence the per-pair convention
  hid). Did not widen the bound.
- **`spec/model_spec.yaml`** — added a `rendering_conventions` block with
  `crf_shared_response_scale`: the binding rule (one common scale per group;
  same rule applied to the reference render; do NOT per-pair max-normalize;
  tuning panels 5C/6C/7C excluded — they stay shared-peak-within-panel).
- **Figure docs** — `figures/figure_2.md` left-axis convention rewritten to the
  shared scale; `figures/figure_4/panel_C.md` "peak normalized to 1.0" removed.

**Phase-B instruction (recorded in spec):** render CRF figure-groups on one
shared response scale matching the digitized references; do not per-pair
max-normalize; apply the same rule to the reference render.

## Finding ② — Fig 4C condition mapping (contract side)

4C resolved to **facilitation / contrast-gain left-shift** (attend-nonpreferred-
in-RF ABOVE attend-away, +~36% modulation) via a **spatial-location** attention
field at the RF (boosts both colocated stimuli) — NOT a feature-based field
isolated on θ=180° (which produced suppression, the Fig-4E mechanism). Contract
changes:

- **`pseudocode/figure_4_protocol.md`** — re-authored the 4C Procedure step 2 to
  specify a SPATIAL (location) attention field at x=0, FLAT over θ, plus a
  prominent Phase-B build note explaining why a narrow feature-tuned-on-θ=180
  field is wrong. Re-authored "Expected behavior (4C)" to facilitation /
  leftward shift / positive declining %-modulation, citing C-015 + C-019 (NOT
  C-021).
- **`extracted_data/test_figure_4C.py`** — flipped Q-026 (`test_attending_
  nonpreferred_in_rf_increases_response`: attended ≥ unattended, %-mod ≥ 0,
  positive peak), Q-027 (`test_attended_crf_is_left_shifted`: smaller half-max),
  Q-028 (positive %-mod peaks at low/intermediate, not the endpoint), Q-029
  (facilitation gap narrows at high contrast). Citations updated: C-021 dropped
  from 4C; C-015/C-019 cited. These now fail RED against the un-fixed model
  (correct handoff state — Phase B must implement the spatial field to green
  them).
- **`extracted_data/test_tier_figure_4.py`** — 4C tier tests re-authored to
  facilitation: `test_4C_attended_above_unattended` (gap > 0.04, attended
  above), `test_4C_mid_contrast_separation_matches_digitized` (positive ~+0.10),
  `test_4C_modulation_positive_and_declines_to_high_contrast`. The 4C record now
  keeps the SIGNED %-modulation so the sign is asserted, not masked by abs().
- **Citations:** C-021 retired as the 4C referent (it is 4E mechanism prose);
  Fig-4 caption + C-019 (contrast-gain / leftward shift) are now the 4C referent
  throughout pseudocode/tests/panel doc.
- **SQ-004 / override:** `logs/spec_questions.md` SQ-004 marked RETIRED with a
  `resolution_2026-06-03` explaining the override (75° suppressive tuning) was a
  symptom of the wrong (suppression) regime; under the spatial mapping 4C
  saturates/recovers with the cited 180° (C-011), so the override is removed.
  New assumption **A-012** added to `spec/assumptions.yaml` recording the 4C
  spatial-attention-facilitation regime, the lineage evidence, and the two
  overrides Phase B must delete.

## GUARD compliance

No parameters tuned to fit curves. The genuine magnitude divergences stay red
and untouched: 4E %-mod overflow (`test_4E_modulation_stays_within_paper_axis`
still red), 6C/5C/7C tier tests not touched. The newly-surfaced 2A
under-saturation (Finding-1 side effect) is flagged as a faithful-direction red,
not greened.

---

## Phase-B build order (exact implementation changes)

Phase B is paper-blind; build to the updated contract. Three changes:

1. **4C spatial attention field** (`implementation/src/rh_model/protocols.py::run_figure_4C`).
   Change the `attended` condition from the narrow feature-tuned field
   (`feature_center=180.0`, tuning width 20°) to a SPATIAL field at the RF:
   `spatial_center=0.0`, `feature_center=None` (flat/uniform over θ), so the gain
   γ boosts both colocated stimuli and reaches the recorded θ=0 neuron's
   numerator. Result must be facilitation: attended CRF above attend-away,
   leftward shift, positive %-modulation peaking ~+36% at low contrast,
   declining toward high contrast. (Satisfies test_figure_4C.py Q-026/027/028/029
   and test_tier_figure_4.py 4C tier; pseudocode/figure_4_protocol.md Procedure 4C.)

2. **Delete the SQ-004 overrides** (`implementation/calibration.yaml`). Remove
   `figure_4C.suppressive_tuning_width: 75.0` and the `figure_4C.sigma` override
   that was added for the same forced-recovery reason. 4C now uses the cited
   180° suppressive tuning (C-011) and the global σ. The "never saturates"
   pathology does not arise under the spatial mapping.

3. **Shared-scale view normalization** (`implementation/src/rh_model/views.py`).
   Replace `_normalized_pair` (per-pair max → 1.0) for the CRF figure-GROUPS
   (2A/2B, 3C/3F, 4C/4E) with a shared-scale normalizer: divide every panel in a
   group by ONE common scale (mirror `rh_tier_helpers.group_scale` — the model
   group's overall peak mapped onto the reference group's overall peak), so 2B's
   attended ceiling renders visibly above 2A's. Apply the SAME shared-scale rule
   to the digitized-reference render (`render_figure_*_reference`) — do NOT pass
   the already-shared-scale digitized curves through a per-pair normalizer.
   Tuning panels 5C/6C/7C keep `_plot_tuning`/shared-peak-within-panel
   (unchanged). (Satisfies model_spec.yaml rendering_conventions.crf_shared_response_scale
   and the Fig-2 ceiling tier tests.)

After Phase B: the 4C facilitation tests and the Fig-2 qualitative ceiling test
should green; the 2A-plateau hard half and the 4E/6C/5C/7C magnitude tiers stay
red by design (faithful divergences).
