# Faithfulness audit — Reynolds & Heeger 2009 (independent re-render)

Date: 2026-06-03 (date rollover during run). Auditor: independent post-build critic
(not the builder). Re-rendered every figure from the committed model
(`PYTHONPATH=src python -m rh_model.views`) before judging. Read the paper
(`paper/extracted_text.md`) and the paper panel JPGs directly; the `article_aware`
contract was audited as a suspect.

Test state at audit: **15 failed / 117 passed / 15 xfailed / 4 xpassed.**

## Verdict: PARTIAL.

Equations, kernel, attention-field algebra, and Fig 1 are faithful. Figs 2–7 carry
real divergences. The **root cause of the Fig 2/3/4C/5/7 magnitude divergences is a
single live CONTRACT_BUG already filed in the contract (A-006/A-013) and encoded as a
gating-red test, but NOT YET implemented by Phase B**: the model still applies
per-panel, figure-fitted suppression knobs the contract now forbids. Fig 6 carries an
independent CODE_BUG (feature attention spatially confined so it cannot reach the
recorded neuron). Fig 4E is a genuine magnitude overflow not resolved by either fix.

---

## FAITHFUL

- **Equations 5/6/2 → code.** `compute_output` = `(A·E)/(S+σ)` rectified at T=0;
  `compute_suppressive_drive` = `s ∗ (A·E)` with `s` integral-normalized
  (`∫ s dx dθ = 1`). Operator-for-operator match. `build_attention_field` =
  `1 + (γ−1)·G_x·G_θ`, gain ≥ 1, applied before normalization. Gaussian "size" = σ_g
  (A-004). All faithful.
- **Figure 1 (schematic).** Stimulus drive × attention field ÷ pooled suppressive
  drive → output, attended (right) stimulus enhanced. Topology and iconography match
  the caption. Panel order is left-to-right vs the paper's top/middle/bottom/right —
  a layout rearrangement, not a content divergence.

---

## DIVERGENT — root cause: CONTRACT_BUG (per-panel suppression knobs, fix unimplemented)

**Finding (already in the contract).** The 1D suppressive pooling under-normalizes, so
S comes out too small vs A·E and CRFs do not saturate. The implementation patches this
with **per-panel, figure-fitted** `suppressive_drive_gain`
(12/6/8/8/12/8 for 2A/2B/3C/3F/4C/4E), `suppressive_spatial_sigma_scale`
(0.55/1.0/0.45/0.7), and per-panel Fig-3 baselines (0.005, not the single 0.05·α).
The paper has ONE model with ONE σ and only Table-1 sizes — no per-figure suppression
gain. **A-006 and A-013 (dated 2026-06-03) already forbid these knobs** and prescribe
the fix (resolve suppression on the paper's 2D image plane, OR promote a single audited
cross-panel constant κ). `test_contract_suppression_consistency.py` encodes this as a
MUST-PASS and **fails RED today (4 tests)**. `implementation/calibration.yaml` still
carries all the per-panel entries and `protocols.py` still reads them → the Phase-A
contract fix is outstanding in Phase B.

This one unimplemented fix is the cross-figure origin of:

- **2A under-saturation** — plateau ~0.34 vs paper ~0.62; curves don't fully converge.
- **3C/3F shape** — separation larger than the paper's; %-mod shape off.
- **5C gain too strong** — peak ratio 1.586 (the protocol runs gain=1) vs paper ~1.2.
  *Empirically demonstrated:* unifying the suppressive gain to ~12 (the value the CRF
  panels already use) drops 5C's ratio to 1.215 — the paper's value. The tuning
  protocols (Figs 5/6/7) apply **no** suppressive gain while CRF protocols apply 6–12;
  this inconsistency is itself the bug.
- **7C gain too strong** — variable/fixation ratio 3.28 (gain=1) vs paper ~1.4.
  Unifying the gain helps (3.28→2.38 at gain 12) but does not fully close it; 7C has a
  residual two-stimulus-geometry component on top of the suppression-knob root cause.
- **4C magnitude** — direction now FAITHFUL (facilitation, attended ≥ unattended
  everywhere — the prior 4C sign fix held), but %-mod peaks ~101% vs paper ~36% and the
  CRFs do not converge at high contrast (saturation test fails). Same under-normalized
  suppression root cause.

**Fix (spec-level):** implement the A-006 binding spec — compute S on the paper's 2D
image plane (s integral-normalized over dx dy dθ with the single cited
`suppressive_field_size=20`, `suppressive_tuning_width=180°`), and DELETE every
`figure_*.suppressive_drive_gain` / `suppressive_spatial_sigma_scale` /
per-panel `baseline_*` from `implementation/calibration.yaml`. If a 1D stand-in is
kept, promote ONE audited `model.suppression_normalization` constant identical across
all panels. Apply the SAME suppression normalization to the tuning protocols
(Figs 5/6/7), which currently apply none.

---

## DIVERGENT — Figure 6C: CODE_BUG (feature attention spatially confined)

`run_figure_6C` builds the "attend opposite-hemifield stimulus" condition as a spatial
Gaussian centered at x = −50 (the opposite hemifield) **times** a feature Gaussian.
Because the attention field is the product `1 + (γ−1)·G_x·G_θ`, at the recorded
neuron's location x = 0 (far from x = −50, spatial size 30) `G_x ≈ 0`, so A ≈ 1
regardless of θ — the feature-based modulation never reaches the recorded neuron. Result:
the two curves overlap (peak ratio ~1.01, no sharpening), independent of the suppression
gain. The paper's feature-based attention is **spatially global** (it modulates
matched-feature neurons everywhere, including the recorded RF): caption "feature-based
attention was matched to the stimulus in the receptive field."

*Empirically demonstrated:* making the attend-opposite condition feature-only
(spatial flat, `spatial_center=None`) restores both signatures — peak elevation ratio
1.01→1.31 (paper ~1.1–1.3) and FWHM narrows 133°→104° (sharpening) vs 133°→118°
(negligible). The same spatial-confinement structure affects Fig 7C's attend-nonpref
(blue) condition.

**Fix (spec-level):** feature-based attention must be spatially broad/global, not a
spatial Gaussian pinned to the opposite-hemifield location. Construct the 6C
attend-opposite attention field with a feature-tuned θ component that is uniform (or
broad) in x so it reaches the recorded neuron — i.e. spatial attention away from RF must
not also remove the feature component from the RF. (Alternatively, document a precise
attention-field factorization in the spec if a different convention is intended; the
paper's panel and caption both demand that the matched-feature curve sharpens.)

---

## DIVERGENT — Figure 4E: GENUINE_DIVERGENCE (magnitude, not resolved by either fix)

Attend-preferred vs attend-nonpreferred with γ=5 (Table-1 value, faithful) and
feature-tuned attention produces %-modulation ~310–390% — far past the paper's 0–100
right axis. Ordering (attend-pref above attend-nonpref) is faithful. The overflow is
**not** fixed by the suppression gain (stays ~360–390% even at gain 40), so it is not the
CONTRACT_BUG; it is emergent from the γ=5 feature-attention two-stimulus competition (the
attend-nonpref response is driven near zero, inflating the ratio). The paper's panel
keeps %-mod < 100%, so either the paper's readout/normalization differs or the
two-stimulus feature-attention mechanism is too strong here.

**source_hint:** Table-1 (4E: γ=5, tuning width 20°); Fig-4E caption (response-gain /
multiplicative scaling, %-mod 0–100 axis); the lineage two-stimulus feature-attention
papers (Martinez-Trujillo & Treue 2002; Treue & Martinez-Trujillo 1999) for the expected
modulation magnitude.

---

## Notes on what I did NOT re-flag

- Fig 1 panel order, color substitution (blue/gray for the paper's thin/thick black),
  and the "not reproduced" placeholders for empirical/legend panels are in-scope-excused
  (model-panels-only ruling) — not findings.
- I did not re-audit the digitized references except to confirm my model-vs-paper
  divergences hold against the **paper panel pixels** directly (they do), so they are
  independent of any digitization residual.
