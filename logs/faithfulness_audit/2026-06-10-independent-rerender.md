# Faithfulness Audit — Reynolds & Heeger (2009) — 2026-06-10 (independent re-render)

Independent re-render + paper/author-code audit of the CURRENTLY committed
`implementation/`, by an auditor who is NOT the builder. Author MATLAB code
(`paper/code/attentionModel/`) re-implemented from scratch in Python as the
lineage resolver / ground truth. Every numeric claim below was measured by this
auditor, not carried over.

## Method
- Re-rendered all 7 figures from the committed model
  (`PYTHONPATH=implementation/src python -m rh_model.figures`, parent `.venv`).
- Re-implemented `attentionModel.m` + `conv2sepYcirc.m` + `makeGaussian.m` in
  Python (`/tmp/author_sim.py`) and ran Fig 6C/7C and the Finding-1 probe input
  through BOTH the author reproduction and the committed `rh_model`.
- Mapped Eq 1-8 to code operator-by-operator; spot-checked the calibration
  ledger `quote:` fields against the author `.m` files (σ, baselines, Table-1
  sizes).
- Full suite: passes (exit 0).

## Verdict: PARTIAL

The forward model (Eq 5/6, stimulus drive, attention field, normalization) is
faithful on single-stimulus inputs and the separable convolution OPERATOR is
bit-identical to the author's `conv2sepYcirc` (I proved max-abs-diff = 0 on an
identical 361 grid + identical input + identical kernels). One real
model-scope CODE_BUG remains, surfacing in the two-stimulus θ-tuning panel
(Fig 7C). The prior audit's second major finding (Fig 6C "over-sharpens to
0.79") does NOT reproduce on the committed render — it now renders at 0.875,
faithful to author/digitized.

---

## Finding 1 — θ stimulus profile is periodic + θ-grid is 360 not 361; null-stimulus suppressive mass inflated 43%

**Tag: CODE_BUG · scope=model · severity=major**

On the author's Fig-7C two-stimulus pair (variable grating x=93 θ=0, null grating
x=107 θ=180, contrast 1, NO attention), the committed impl suppressive drive at
the recorded neuron (x=100, θ=0) is **S=0.001186** vs the author code's
**S=0.001012** — ~17% too large — while the stimulus drive E matches
(0.00730 vs 0.00728).

I localized the root cause precisely, and it is NOT the convolution-wrap
semantics the previous audit named (that operator is bit-identical — verified
diff=0). The cause is two convention mismatches in how the θ stimulus profile is
built:

1. **Periodic vs non-periodic θ stimulus Gaussian.** The impl
   `build_stimulus_drive` builds each stimulus's θ profile with
   `gaussian_periodic_1d(theta, θ_stim, σ=1, period=360)` — it WRAPS at ±180. The
   author code uses `makeGaussian(theta,θ_stim,1,1)` = a plain `normpdf` over the
   finite buffer `theta=[-180:180]'` with NO wrap. For the NULL stimulus at
   θ=180 (the +180 grid edge), the author Gaussian's tail (181°, 182°, …) falls
   off the buffer and is lost, so its θ-column mass = **1.7533**; the impl's
   periodic version wraps that tail back and sums to **2.5066** — a **+43.0%
   inflation** of exactly the stimulus that drives suppression-only (the null
   contributes nothing to drive at the preferred neuron, only to S).
2. **Grid 360 vs 361.** The impl θ grid is `arange(-180,180,1)` = 360 samples
   (drops the +180 endpoint); the author grid is `[-180:180]` = 361 samples. The
   `model.py:24` docstring claims "361 samples" — the code builds 360.

Because `R = A·E/(S+σ)` and the inflated S sits in the denominator of the
fixation/away baseline (whose A=1, so S is not separately scaled by attention),
the inflated null-suppression depresses the baseline and inflates the measured
var/fixation peak ratio.

Measured end-to-end (var-attend peak / fixation peak, normalized panel):
- committed impl Fig 7C: **1.413** (fixation 0.71 of var peak)
- author code (my Python reproduction): **1.323**
- digitized panel C (logs/digitization_audit): **≈1.32** ("the old 1.4 refuted")

The author code AND the paper's own digitized panel agree at 1.32 and BOTH
disagree with the committed 1.41. The 7C test asserts only ordering
(var > fixation > nonpref), so it passes regardless — the magnitude divergence
ships green.

**Fix (spec-level):** match the author's θ stimulus convention. (a) Adopt the
author's 361-sample θ buffer `arange(-180,181)`; (b) build the per-stimulus θ
profile with a NON-periodic Gaussian (`normpdf`/`makeGaussian`-equivalent, no
wrap) so a stimulus at the ±180 edge loses its off-grid tail exactly as the
author code does — do NOT use `gaussian_periodic_1d` for the stimulus θ profile.
The suppressive/stimulation/attention KERNELS remain circular in θ (the operator
is already correct). Acceptance: on the no-attention pair above, impl S(0,100)
must equal author 0.001012 (±0.5%), and Fig 7C var/fixation peak ratio must land
at 1.32 (±0.03).

NOTE — convention is paper-underdetermined; lineage resolves it. For motion
direction a periodic θ wrap is arguably more physical, and the paper does not
pin the buffer. But faithfulness to the released author code requires the
non-periodic truncated form, and the digitized panel agrees with the author
(1.32), so the lineage ladder (rung 1 = released code, corroborated by rung 0 =
the published panel) resolves it toward the non-periodic author convention. This
is a CODE_BUG (impl diverges from the convention the paper's own figure was made
with), not a paper issue.

source_hint: `model.py:65-67` (θ grid `arange(-180,180)` = 360) + `model.py:24`
docstring ("361 samples", contradicting the code) + `model.py:213` /
`build_stimulus_drive` using `gaussian_periodic_1d` for the stimulus θ profile,
vs `makeGaussian.m` (`normpdf`, non-periodic) over `theta=[-180:180]'` in
`Figure7C.m:9` and the `[-180:180]'` buffer in every author `Figure*.m`.

---

## Finding 2 — Fig 6C feature-attention field is a flat-in-x proxy, not the author 'cross'; outcome currently faithful

**Tag: GENUINE_DIVERGENCE · scope=figure (Figure 6C) · severity=minor**

`run_figure_6C` (protocols.py:388-441) builds the attend-feature condition as
`{spatial_center: None, feature_center: θ_stim}` — A flat in x, θ-selective —
and uses `x_opposite=-50`, `x_fixation=50`, which differ from the author
`Figure6C.m` (`Ashape='cross'`, `Ax=-100`/`AxWidth=30`, second stimulus at -100,
attend-fixation `Ax=0`). So the MECHANISM is a proxy, not the author 'cross'.

However, the OUTCOME is faithful on the committed render (this auditor's
measurement, contradicting the prior audit's "0.79"):
- impl Fig 6C FWHM ratio (attend-feature / attend-fixation): **0.875**
- author 'cross' (my reproduction): FWHM 124/140 = **0.886**
- digitized panel C: σ 53/61 = **≈0.87**

All three agree at ~0.87-0.89. The rendered panel shows the blue
(attend-feature) curve elevated AND modestly narrower than gray — the paper's
sharpening, correct direction and magnitude. The prior audit's Finding-2 value
(σ-ratio 0.79, "over-sharpens") does not reproduce on the current committed
model; the flat-x proxy happens to land on the author/digitized number here.

This stays a GENUINE_DIVERGENCE (mechanism ≠ author 'cross', and the
x_opposite=-50/x_fixation=50 geometry is invented, not the author's
-100/0), not a *_BUG, because the figure output is faithful. If a future change
moves it off 0.87, the proper fix is to implement the author 'cross' Ashape
(`attentionModel.m:146-162`) and route 6C through it with the `Figure6C.m`
params (AxWidth=30, AthetaWidth=60), rather than the flat-x proxy.

source_hint: `protocols.py:388-441` (flat-x proxy, x_opposite=-50, x_fixation=50)
+ assumption A-014 / SQ-006 vs `Figure6C.m:3-7` (`Ashape='cross'`, Ax=-100,
AxWidth=30) and `attentionModel.m:146-162` (the 'cross' build).

---

## Finding 3 — Fig 1 Output panel shows no visible attended-side enhancement

**Tag: GENUINE_DIVERGENCE · scope=figure (Figure 1) · severity=minor**

The rendered "Output firing rate" panel draws the attended (right) and
unattended (left) bands at near-equal brightness (R_attended/R_unattended ≈
1.01). The paper's Fig-1 population-response panel draws the attended band
clearly brighter. This is the genuine behaviour of Eq 5/6 for BROAD spatial
attention on a single isolated stimulus: γ multiplies both E (numerator) and the
locally-pooled S (denominator), so the gain nearly cancels at the recorded
neuron. Figure 1 is a mechanism schematic with no `Figure1.m` to pin its exact
γ/contrast, so the divergence is faithful to the equations, not a code bug — but
the rendered panel does not communicate the enhancement the paper's panel
illustrates. Confirmed by re-render (the suppressive-drive panel DOES show the
correct right-side brightening; only the final output panel washes out).

source_hint: paper Fig 1 caption ("white indicates a value greater than 1 …
output firing rates") vs `run_figure_1` R_attended/R_unattended ≈ 1.01. No
author script for Fig 1.

---

## Finding 4 — Fig 4C curve order (attend-RF below attend-away)

**Tag: PAPER_ISSUE · scope=figure (Figure 4C) · severity=minor · already-dispositioned**

Re-confirmed: the rendered 4C draws attend-nonpref-in-RF BELOW attend-away
(suppression at low/mid contrast, crossing near the top), matching the author
`Figure4C.m` and the suppression prose, but OPPOSITE the *published* panel C
(which draws attend-RF above and labels the dashed curve a "percentage
increase"). Resolved earlier via the lineage ladder (rung 1 = released code) as a
documented paper/figure defect (DR-4C-sign, A-012). Faithful to the author code;
no change required. Flagged for completeness only.

source_hint: `Figure4C.m:53-61` + assumption A-012 / `test_dr_4c_sign_resolution.py`.

---

## Finding 5 — Human-facing figure_*.md docs teach superseded values (contract drift)

**Tag: CONTRACT_BUG · scope=figure (Figures 2,3,4 docs) · severity=minor · already-logged**

The 2026-06-10 spec audit (`logs/spec_audit/contract_audit_2026-06-10.md`) found
`article_aware/figures/figure_3.md` still documents A-007 baselines (0.05/0.05),
contradicting the binding calibration (CODE-017: 5e-7; 5.0/0.0), and
`figure_4.md` Panel-C section still teaches the retired C-021 mechanism. The
figure PNG outputs are faithful (I re-rendered and checked); this is a
documentation-vs-contract divergence, not a figure-output divergence. Re-noted
here so it is not lost; the fix is in that spec audit (rewrite the .md sections to
CODE-017 / A-012).

source_hint: `logs/spec_audit/contract_audit_2026-06-10.md` F3/F4 + `figure_3.md:37-42`,
`figure_4.md:207`.

---

## Checked and FAITHFUL (with what I checked)

- **Eq 1-2, 5-6 → code:** `compute_output` R=(A·E)/(S+σ) (Eq 5), S=conv(A·E)
  (Eq 6), A multiplies E before normalization. Operator-by-operator match.
- **Separable convolution operator:** impl `_separable_conv` is bit-identical to
  author `conv2sepYcirc` (`upConv` zero-pad rows / circular cols) on identical
  grid+input+kernels (max-abs-diff = 0). The previous audit's claim that the FFT
  wrap/centre convention diverges is REFUTED.
- **Single-stimulus forward model:** impl E matches author to 5 dp.
- **Calibration ledger quotes:** σ=1e-6 (`attentionModel.m:117`), baselineMod=5e-7,
  baselineUnmod=5 (3C)/0 (3F) (`Figure3C/F.m:5-6`), stimulation/suppressive sizes
  (5/20), tuning widths (60/360), per-figure stimulus/attention sizes — all
  match Table 1 + the author `Figure*.m`. baselineMod is correctly
  attention-modulated (added to E before A·E) in both author and impl.
- **Fig 2A/2B:** contrast-gain left-shift (A) vs response-gain overshoot + flat
  high-contrast %-mod (B). Matches paper.
- **Fig 3C/3F:** baseline offsets, low-contrast %-mod bump (C), non-converging
  high-contrast gap (F). Matches Reynolds-2000 / Williford-Maunsell.
- **Fig 4E:** attend-pref above attend-nonpref, multiplicative scaling. Matches.
- **Fig 5C:** multiplicative scaling, no FWHM change. Matches McAdams-Maunsell.
- **Fig 6C:** FWHM ratio 0.875 (author 0.886, digitized 0.87) — faithful (see
  Finding 2 for the mechanism caveat).
- **Fig 7C ordering + shape:** attend-variable > fixation > attend-nonpref,
  Gaussian-shaped — faithful; only the var/fixation MAGNITUDE ratio diverges
  (Finding 1).

## Not in scope (per 2026-06-02 ruling)
Empirical data points / error bars absent from the model panels are NOT findings;
the A/B/empirical sub-panels render as "not reproduced" placeholders by design.

## Correction to the prior (same-day) audit
- Finding 1 root cause restated: it is the periodic-vs-truncated θ STIMULUS
  profile + the 360-vs-361 grid, NOT the convolution-operator wrap semantics
  (operator proven identical, diff=0). The fix changes accordingly.
- Finding 2 downgraded major→minor and CODE_BUG→GENUINE_DIVERGENCE: the
  committed model renders Fig 6C at FWHM-ratio 0.875 (faithful), not 0.79.
