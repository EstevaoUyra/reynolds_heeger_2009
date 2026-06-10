# Faithfulness Audit — Reynolds & Heeger (2009) — 2026-06-10

Independent re-render + paper/author-code audit of the CURRENTLY committed
`implementation/`. Author MATLAB code (`paper/code/attentionModel/`) is the
lineage resolver and is used here as ground truth wherever the single paper
underdetermines a mechanism.

## Method

- Re-rendered all 7 figures fresh from the committed model
  (`PYTHONPATH=src python -m rh_model.figures`, root `.venv` for matplotlib).
- Mapped every paper equation (Eq 1-8) to code; checked the calibration ledger
  against the author code with the verbatim `quote:` fields.
- Re-implemented the author scripts (`attentionModel.m`, `Figure6C.m`,
  `Figure7C.m`) numerically in Python and ran the same conditions through
  `rh_model.simulate` on identical inputs to localize divergences.
- Full suite: 150 passed, 9 xfailed, 18 xpassed.

## Verdict: PARTIAL

The forward model (stimulus drive, attention field, normalization Eq 5/6) is
**byte-faithful to the author code on single-stimulus inputs** (verified: E and
R match to 5 decimals). Two real divergences remain, both surfacing in the
feature/two-stimulus tuning panels:

1. CODE_BUG (model scope) — the suppressive circular-θ convolution does not
   reproduce the author `conv2sepYcirc`; impl S is ~17% too large on identical
   input. Shifts condition *ratios* (Fig 7C 1.41 vs author/digitized 1.32).
2. CODE_BUG (figure scope, Fig 6C) — the author 'cross' Ashape is not
   implemented; the flat-in-x feature proxy over-sharpens (σ-ratio 0.79 vs
   author 0.89 / digitized 0.87).

Plus one minor figure-scope GENUINE_DIVERGENCE (Fig 1 Output panel) and one
already-dispositioned PAPER_ISSUE (Fig 4C curve order, DR-4C-sign / A-012).

---

## Finding 1 — Suppressive θ-convolution does not match author `conv2sepYcirc`

**Tag: CODE_BUG · scope=model · severity=major**

On an IDENTICAL two-stimulus pair (x=93 θ=0, x=107 θ=180, contrast 1, NO
attention) the impl suppressive drive at the recorded neuron is
`S(0,100)=0.001186` vs the author code's `0.001012` — **~17% too large** — even
though the stimulus drive E matches exactly (impl 0.00730 vs author 0.00728) and
the two θ-kernels sum nearly identically (0.3829 vs 0.3839). Because
`R = A·E/(S+σ)`, an inflated S depresses responses and, crucially, changes the
*ratio* between attention conditions.

Locus: `implementation/src/rh_model/model.py:130-151` `_separable_conv` — the
θ axis is done as an FFT circular convolution with the kernel re-centred by
`np.roll(theta_kernel, -argmax)`. The author's `conv2sepYcirc.m` runs
`upConv(...,'circular',...)` over the 361-sample θ buffer `[-180:180]'`. The
impl θ grid is `arange(-180,180,1)` = **360 samples** (drops +180), and the FFT
wrap/centre convention differs from `upConv`. The `model.py:24` docstring claims
"361 samples" — the code actually builds 360 (the +180 endpoint is excluded).

Verified NOT the cause: switching the grid to 361 pts / period 361 leaves the 7C
ratio at 1.4149 (≈ current 1.4147), so the residual is the **convolution wrap
semantics**, not the sample count alone. The single-orientation CRFs (Fig 2/3)
are nearly immune because they normalize away the absolute scale and the broad
σ=360 pool dominates; the bug bites where a *ratio across θ-structured
conditions* is the measured quantity.

Impact: Fig 7C var/fixation peak ratio = **1.41**, vs author code **1.32** and
the digitized panel **1.32** (the digitization audit explicitly says "the old
1.4 refuted" — yet the committed model still renders 1.41). The 7C test only
asserts ordering, so it passes regardless.

**Fix (spec-level):** make the suppressive (and stimulus-drive) θ-convolution
bit-match the author `conv2sepYcirc`/`upConv` circular convention on a θ grid
that matches the author's. Concretely: adopt the author's 361-sample θ buffer
`[-180,180]` and a circular convolution whose phase/centre matches `upConv`
(MATLAB centres an odd filter on its middle tap; the FFT path must reproduce
that, not `-argmax`). Acceptance: on the no-attention pair above, impl
`S(0,100)` must equal the author `0.001012` (±0.5%), and Fig 7C var/fixation
ratio must land at 1.32 (±0.03).

source_hint: `attentionModel.m:171` (`I = conv2sepYcirc(E,IxKernel,IthKernel)`)
and `conv2sepYcirc.m:18-19` (`upConv(...,'circular',...)`) vs
`model.py:_separable_conv` + the 360-vs-361 grid at `model.py:65-67`.

---

## Finding 2 — Fig 6C oversharpens: author 'cross' Ashape not implemented

**Tag: CODE_BUG · scope=figure (Figure 6C) · severity=major**

The author `Figure6C.m` builds the feature-attention field with
`Ashape='cross'`, `Ax=-100`, `AxWidth=30`, `Atheta=0`, `AthetaWidth=60` — an
*additive-separable* "cross" (high along the whole θ=0 row AND the whole x=-100
column), per `attentionModel.m:146-162`. The committed model implements ONLY the
'oval' product `A = 1+(γ-1)·G_x·G_θ` (`model.py:223-260`) and, for the
feature-selective condition, sets `spatial_center=None` to make A *flat in x*
(A-014). Flat-in-x is a strictly stronger sharpening than the author 'cross'
(which still carries a spatial Gaussian term).

Measured (FWHM of the direction tuning, fixation → attend-feature):
- impl flat-x:        143 → 113.4  (σ-ratio **0.79**)
- author 'cross':     142 → 126    (σ-ratio **0.89**)
- digitized panel C:  σ 61 → 53    (σ-ratio **0.87**)

The author code and the digitized panel agree (~0.87-0.89); the committed model
over-sharpens to 0.79. The 360-vs-361 grid has NO effect here (verified: 0.793
on both), so this is purely the flat-x vs 'cross' mechanism choice.

A-014 correctly diagnoses that a *confined* G_x·G_θ centred at x=-100 zeroes the
gain at the RF (the old 6C CODE_BUG) — but its chosen remedy (perfectly flat in
x) overshoots in the other direction. The faithful object is the author 'cross':
feature gain reaches the RF *and* keeps a spatial profile, yielding the milder,
panel-matching sharpening.

**Fix (spec-level):** implement the author 'cross' Ashape in
`build_attention_field` (config-selectable, default 'oval'), and route Fig 6C
(and any feature-selective condition the author runs as 'cross') through it with
the `Figure6C.m` params (AxWidth=30, AthetaWidth=60, Apeak=2). Formula from
`attentionModel.m:146-162`: `attnGainX=(γ-1)·G_x+1`, `attnGainθ=(γ-1)·G_θ+1`,
`attnGain=(γ-1)·[G_θ(θ-Aθ)·G_x(x-Ax)]+1` (the impulse-then-θ-conv collapses to
the product of the two affine-shifted profiles). Acceptance: Fig 6C σ-ratio in
[0.85, 0.90].

source_hint: `attentionModel.m:146-162` (`Ashape=='cross'`) + `Figure6C.m:5-7`
(`Ashape='cross'`, AxWidth=30, AthetaWidth=60) vs `model.py:build_attention_field`
(oval only) and `protocols.py:432-435` (flat-x proxy) / assumption A-014.

---

## Finding 3 — Fig 1 Output panel shows no visible attended-side enhancement

**Tag: GENUINE_DIVERGENCE · scope=figure (Figure 1) · severity=minor**

The rendered "Output firing rate" panel shows the attended (right) and
unattended (left) bands at essentially equal brightness: model
`R_attended/R_unattended = 1.0098`. The paper's Figure-1 population-response
panel draws the attended (right) band clearly brighter. This is the genuine
behaviour of the equations for *broad spatial* attention on a single isolated
stimulus (γ multiplies both E in the numerator and the locally-pooled S in the
denominator, so the gain nearly cancels) — Figure 1 is a mechanism *schematic*
with no `Figure1.m` to pin its exact contrast/γ. So the divergence is faithful
to the model, not a bug; but the rendered panel does not communicate the
enhancement the paper's panel illustrates.

source_hint: paper Fig 1 caption ("white indicates a value greater than 1 …
output firing rates") vs `protocols.run_figure_1` `R_at_attended` /
`R_at_unattended` (1.0098 ratio). No author script for Fig 1.

---

## Finding 4 — Fig 4C curve order (attend-RF below attend-away)

**Tag: PAPER_ISSUE · scope=figure (Figure 4C) · severity=minor · already-dispositioned**

The rendered 4C draws attend-nonpref-in-RF BELOW attend-away (suppression), with
%-mod ~38% declining — matching the author `Figure4C.m` and C-021's suppression
prose, but OPPOSITE to the *published* panel C, which draws attend-RF above and
labels the dashed curve a "percentage increase". Resolved earlier via the
lineage ladder (rung 1 = released code) as a documented paper/figure defect
(DR-4C-sign, A-012). Re-confirmed faithful to the author code; flagged here only
for completeness. No change required.

source_hint: `Figure4C.m:53-61` (attend-RF is the lower curve) + assumption
A-012 / `test_dr_4c_sign_resolution.py`.

---

## Checked and FAITHFUL

- **Eq 1-2, 5-6 → code:** `compute_output` `R=(A·E)/(S+σ)` (Eq 5), `S=conv(A·E)`
  (Eq 6), attention multiplies E before normalization. Operator-by-operator
  match. σ=1e-6, T=0 from CODE-014/A-003 (verbatim-quoted in ledger).
- **Single-stimulus forward model:** impl E and R match author code to 5 dp.
- **Fig 2A/2B:** contrast-gain left-shift + convergence (A); response-gain
  overshoot 0.86 vs 0.60 + flat high %-mod (B). Matches paper. cRange [1e-5,1]
  from `Figure2*.m` (CODE-020).
- **Fig 3C/3F:** baseline offsets (CODE-017 mod=5e-7, 3C unmod=5), low-contrast
  %-mod bump (C), non-converging high-contrast gap (F). Matches Reynolds-2000 /
  Williford-Maunsell descriptions.
- **Fig 4E:** attend-pref above attend-nonpref, %-mod peak 53.6 vs digitized ~54.
- **Fig 4C %-mod:** peak 37.9 vs digitized ~36 / author ~38 (in range; the
  suppression-conv bug does not push 4C/4E out of the digitized envelope).
- **Fig 5C:** multiplicative scaling, no width change (attend-RF = 1.0,
  attend-contra = 0.857, identical FWHM). Matches McAdams-Maunsell panel.
- **Fig 7C ordering:** attend-variable > fixation > attend-nonpref (1.0 / 0.71 /
  0.41 of peak). Ordering and shape faithful; only the magnitude ratio diverges
  (Finding 1).
- **Calibration ledger:** every `audited:true` paper-derived constant carries a
  verbatim quote backed by Table 1 or the author code line; spot-checked
  stimulation/suppressive field sizes (5/20), tuning widths (60/360),
  per-figure stimulus/attention sizes — all consistent with Table 1 + Figure*.m.

## Not in scope (per 2026-06-02 ruling)

Empirical data points / error bars absent from the model panels are NOT findings;
the A/B/empirical sub-panels render as "not reproduced" placeholders by design.
