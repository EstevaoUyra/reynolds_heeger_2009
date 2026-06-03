# Reynolds & Heeger 2009 — The Normalization Model of Attention

## Model

Reynolds JH, Heeger DJ. **The Normalization Model of Attention.** *Neuron.* 2009 Jan 29;61(2):168–185. doi:[10.1016/j.neuron.2009.01.002](https://doi.org/10.1016/j.neuron.2009.01.002) (PMCID PMC2752446).

This is the foundational **normalization model of attention**: it explains a large and apparently contradictory body of attention data (contrast-gain vs. response-gain modulation, multiplicative tuning-curve scaling, feature-based sharpening, tuning shifts with two stimuli in the receptive field) with a single divisive-normalization circuit. A population of neurons indexed by receptive-field center `x` and feature preference `θ` receives an excitatory **stimulus drive** `E(x,θ)`, is gated by a multiplicative **attention field** `A(x,θ) ≥ 1`, and is divisively normalized by a pooled **suppressive drive** `S(x,θ)`. The central claim is that the *shape* of attentional modulation is not a free parameter — it emerges from the relative size of the attention field and the stimulus.

The model computes, per neuron, the rectified divisive-normalization response (Eq. 5):

```
R(x,θ) = ⌊ A(x,θ)·E(x,θ) / (S(x,θ) + σ) ⌋_T
```

where the suppressive drive is the suppressive field convolved with the *attention-modulated* stimulus drive (Eq. 6),

```
S(x,θ) = s(x,θ) ∗ [ A(x,θ)·E(x,θ) ],     ∫ s(x,θ) dx dθ = 1   (Eq. 2)
```

`A`, `E`, and the suppressive/stimulation fields all have Gaussian profiles in space and in feature (orientation/direction). The attention field is `A = 1 + (γ−1)·G`, a Gaussian bump `G` of peak gain `γ`. Because the same product `A·E` appears in both the numerator and (after pooling) the denominator, growing the attention field relative to the stimulus continuously moves the modulation from a **contrast-gain** signature (a leftward shift of the contrast-response function, biggest percent change at low contrast) to a **response-gain** signature (a multiplicative scaling sustained at high contrast). This implementation runs the full population simulation directly rather than the closed-form limiting cases (Eqs. 3/4/7/8), which the paper uses only to expose those two regimes analytically.

**Scope.** Seven figures are in scope (each has an `article_aware/figures/figure_<N>_visual_checklist.md`): the pipeline schematic (Fig 1), the two-regime contrast-response demonstration (Fig 2), the V4 empirical-pattern fits (Fig 3), two-stimulus contrast-response modulation (Fig 4C/4E), spatial-attention multiplicative scaling (Fig 5C), feature-based tuning sharpening (Fig 6C), and combined spatial+feature tuning shifts with two stimuli in the RF (Fig 7C). The reproduction targets the model-output panels; empirical reference panels and multi-panel legends/icon rows are out of scope (SQ-003).

**Faithfulness-regime status: FAITHFUL.** This is the foundational R&H 2009 normalization model from which the `hermann2010` and `carrasco2021` models reuse primitives (e.g. `rh_model.crf_protocol.run_crf`). Under the new faithfulness regime the core maps operator-for-operator to the paper: Eq. 5 (numerator `A·E`, denominator `S+σ`, half-wave rectification at `T`), Eq. 6 (pooling the product `A·E`), and the integral-normalized kernel (Eq. 2) are all faithful, with verbatim Table-1 quotes on every audited scientific parameter. The regime audit **restored the paper-present Fig 4 dashed percent-attentional-modulation curve** (right twin axis) that the original reproduction had dropped — its `views.py` comment had mislabeled this paper-and-checklist-required curve as a "spurious" panel — and **corrected audited-flag provenance** (assumption-sourced values that had been marked `audited:true` without a paper quote were honestly downgraded to `audited:false` under their SQ/assumption). The full test suite (81 tests) passes.

## Reproduced figures

### Figure 1 — Pipeline schematic: stimulus drive × attention field ÷ suppressive drive → output  ✅ faithful
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_1.jpg" width="430"></td><td><img src="figures_reproduced/figure_1.png" width="430"></td></tr></table>

A 1D-display schematic (A-006) of the `E × A ÷ S → R` pipeline: two stimulus stripes, a localized attention field over the right (attended) stimulus, and an output that enhances the attended stimulus relative to the unattended one — matching the paper's architectural introduction.

### Figure 2 — Contrast gain vs. response gain: the two attentional regimes  ✅ faithful
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_2.jpg" width="430"></td><td><img src="figures_reproduced/figure_2.png" width="430"></td></tr></table>

The paper's central demonstration. Panel 2A (small attention field / large stimulus → **contrast gain**): attended and unattended contrast-response functions converge at high contrast and percent modulation falls monotonically from low contrast. Panel 2B (large attention field / small stimulus → **response gain**): the curves diverge multiplicatively with modulation sustained at high contrast. The high-contrast saturation is gentler than the paper's flat plateau — a documented, non-binding shape concession (SQ-001) that preserves the discriminating regime signatures.

### Figure 3 — Empirical V4 contrast-response patterns and model fits  ✅ faithful
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_3.jpg" width="430"></td><td><img src="figures_reproduced/figure_3.png" width="430"></td></tr></table>

Model panels 3C (contrast-gain-like: percent modulation peaks low and falls) and 3F (response-gain-like: sustained modulation, largest absolute separation at high contrast), each carrying the dashed percent-modulation twin axis as in the paper. Empirical reference panels are out of scope (not generated by the implementation).

### Figure 4 — Two-stimulus contrast-response modulation (attend-nonpreferred vs. attend-preferred)  ✅ faithful
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_4.jpg" width="430"></td><td><img src="figures_reproduced/figure_4.png" width="430"></td></tr></table>

Panel 4C (attend-nonpreferred suppresses the response below attend-away, contrast-gain-like) and 4E (attend-preferred scales multiplicatively above attend-nonpreferred), each now with the **dashed percent-attentional-modulation curve on the right twin axis restored** — this was the regime audit's one open divergence (FIG-4CE-MOD), where the original view dropped a paper-present, checklist-required curve under a comment falsely calling it "spurious"; the data was always in the model record (the deterministic 4C test asserts on it). Note: Fig 4C uses an implementation-side 75° suppressive tuning width (SQ-004) — an honestly flagged, `audited:false` provisional assumption for the 1D reduction, because the paper states no 4C-specific suppressive tuning width and no other sanctioned calibration knob reproduces the claimed contrast-gain recovery.

### Figure 5 — Spatial attention as multiplicative scaling of the tuning curve  ✅ faithful
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_5.jpg" width="430"></td><td><img src="figures_reproduced/figure_5.png" width="430"></td></tr></table>

Panel 5C: the attended tuning curve is a clean multiplicative scaling of the unattended one — same width, scaled peak, no shape change — reproducing the McAdams & Maunsell result.

### Figure 6 — Feature-based attention and tuning sharpening  ✅ faithful
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_6.jpg" width="430"></td><td><img src="figures_reproduced/figure_6.png" width="430"></td></tr></table>

Panel 6C: the feature-matched curve ("attend opposite stimulus") is narrower than the attend-fixation curve — the model's account of feature-based sharpening in MT.

### Figure 7 — Two stimuli in the RF: combined spatial + feature attention shifts tuning  ✅ faithful
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_7.jpg" width="430"></td><td><img src="figures_reproduced/figure_7.png" width="430"></td></tr></table>

Panel 7C (the sole model-output deliverable, per the SQ-003 human resolution): direction-tuning curves order as attend-variable > attend-fixation > attend-nonpreferred, all peaking at the preferred direction. The attend-variable peak ratio is exaggerated (~3.3× vs. the paper's ~1.5×) — a documented, non-binding magnitude note; the ordering and tuning shift are faithful. Panel A/B/legend/arrow-row items are out of scope.

## How it was verified

**Faithfulness regime.** Two independent auditors reviewed the model. The **Faithfulness Auditor** compared the paper (`paper/extracted_text.md` equations, Table 1, verbatim captions, and the `article_aware/figures/figure_*.jpg` images) against the implementation, re-rendering all seven PNGs from source; the **Process Auditor** checked the reasoning trail for drift (e.g. audited-flag provenance, laundered contradictions). The audit confirmed Eqs. 5/6/2 and the stimulus/attention/suppressive-field construction are faithful, surfaced and closed the one open view-layer divergence (FIG-4CE-MOD — the restored Fig 4 percent-modulation curve), and confirmed no result-bearing frozen stub exists: every figure is a live `protocols.run_figure_*` → `measurements` → `views` computation, not a constructed answer. Audit records are in `logs/faithfulness_audit/` (rounds r0/r1/r2, 2026-06-03).

**Deterministic tests.** 81 tests (`pytest --collect-only`) assert the qualitative claims directly on the model record — e.g. the Fig 4C test asserts attend-nonpreferred *suppresses* (attended ≤ unattended, negative percent modulation) with a rightward half-max shift, the paper's stated direction, not its inverse; the Fig 2A/4E tests assert genuine high-contrast saturation. All 81 pass.

**Key frozen stubs / assumptions.** The model is run as a 1D discretization (A-006). The honestly-contained `audited:false` knobs are: σ/α/T/β and fixed sweep contrasts (assumptions A-001/002/003/010); per-figure suppressive-drive gains and response baselines (SQ-001/SQ-002); and the Fig-4C-only 75° suppressive tuning width (SQ-004, provisional, soft-blocked on human review). The closed-form limiting equations (Eqs. 3/4/7/8) are not on the simulation path. Open spec questions are tracked in `logs/spec_questions.md`.

## Repository layout

`implementation/src/rh_model/` holds the model (`model.py`), protocols, measurements, and the `views.py` render entry (`python -m rh_model.views` writes `implementation/figure_outputs/figure_<N>.png`). `article_aware/spec/` carries the structured spec, citations, and calibration ledger; `article_aware/figures/` the paper images and visual checklists; `figures_reproduced/` the committed reproduced PNGs; `logs/` the audit and spec-question records.
