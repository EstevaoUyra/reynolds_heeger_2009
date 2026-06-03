# Reynolds & Heeger 2009 — The Normalization Model of Attention

> ⚠️ **NOT a faithful reproduction (corrected 2026-06-03).** This model previously
> shipped as "FAITHFUL across all 7 figures." A panel restructure (pinning each panel's
> axes to the paper's) plus careful side-by-side inspection found that verdict was
> **wrong**: the schematic (Fig 1) is faithful, but **Figures 2–7 carry real divergences
> in the model's curve shapes and attention-gain magnitudes** — the kind of quantitative
> error that matters precisely because this is a *normalization model* (the gain/
> modulation magnitude *is* the scientific claim). Only Fig 4E's divergence is currently
> a deterministic failing test; the others were caught by eye and become deterministic
> once per-panel **curve digitization** lands (the next process stage). This entry is a
> documented case of the auditor being too lenient — see "How it was verified."

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

`A`, `E`, and the suppressive/stimulation fields all have Gaussian profiles in space and in feature. The attention field is `A = 1 + (γ−1)·G`, a Gaussian bump `G` of peak gain `γ`. Because the same product `A·E` appears in both the numerator and (after pooling) the denominator, growing the attention field relative to the stimulus continuously moves the modulation from a **contrast-gain** signature (a leftward shift of the contrast-response function) to a **response-gain** signature (a multiplicative scaling sustained at high contrast). **The equations themselves map operator-for-operator to the paper and are faithful** — the divergences below are in the model's *quantitative output* (the realized gains and curve shapes), not the transcription of Eqs. 5/6/2.

**Figures use the paper's panel layout.** Each figure is reassembled as the paper's panel grid: reproduced model panels are drawn with axes pinned to the paper's, and omitted panels (empirical data, schematic configs, legends) appear as explicit **"not reproduced"** placeholders. This makes the side-by-side comparison line up and the omissions honest.

## Reproduced figures — per-figure verdict

### Figure 1 — Pipeline schematic  ✅ faithful (schematic)
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_1.jpg" width="430"></td><td><img src="figures_reproduced/figure_1.png" width="430"></td></tr></table>

The `E × A ÷ S → R` pipeline — stimulus drive, a localized attention field over the attended stimulus, the pooled suppressive drive, and an output that enhances the attended stimulus. The iconography and topology match the paper's architectural figure. (Schematic: no data curve to digitize.)

### Figure 2 — Contrast gain vs. response gain  ❌ DIVERGENT (curve shape)
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_2.jpg" width="430"></td><td><img src="figures_reproduced/figure_2.png" width="430"></td></tr></table>

The two regimes are present qualitatively, but the **CRF shapes are wrong**: in the contrast-gain panel (2A) the attended and unattended curves should **converge to a common asymptote** at high contrast (a pure leftward shift) and they do not, and the percent-modulation curve shape does not match the paper's. *(Inspection-identified; deterministic once digitized.)*

### Figure 3 — Baseline shift across contrast  ❌ DIVERGENT (shape + % modulation)
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_3.jpg" width="430"></td><td><img src="figures_reproduced/figure_3.png" width="430"></td></tr></table>

Both the main-curve shapes **and** the percent-attentional-modulation curves diverge from the paper, and the figure's actual subject — an **additive baseline shift** — is not faithfully shown (the reproduction reads as scaled sigmoids, not a baseline offset). Empirical panels (B/E) are correctly "not reproduced." *(Inspection-identified.)*

### Figure 4 — Two-stimulus contrast-response modulation  ❌ DIVERGENT (4E — FAILING TEST)
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_4.jpg" width="430"></td><td><img src="figures_reproduced/figure_4.png" width="430"></td></tr></table>

Panel **4E's percent-attentional-modulation reaches 310–390%**, far above the paper's right axis of **0–100%**. With the axis now pinned to the paper's (no auto-scaling), `test_figure_4E_modulation_within_paper_axis` is **RED** — the divergence the original view *hid by auto-scaling its axis to ~400*. 4C is closer but unverified at the curve level. *(4E: deterministic failing test.)*

### Figure 5 — Spatial attention as multiplicative scaling  ❌ DIVERGENT (gain too strong)
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_5.jpg" width="430"></td><td><img src="figures_reproduced/figure_5.png" width="430"></td></tr></table>

The scaling is multiplicative and same-width (the right *kind* of effect), but the attended and unattended curves are **too far apart** — the gain exceeds the paper's modest enhancement. *(Inspection-identified.)*

### Figure 6 — Feature-based attention sharpening  ❌ DIVERGENT (effect essentially absent)
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_6.jpg" width="430"></td><td><img src="figures_reproduced/figure_6.png" width="430"></td></tr></table>

The two tuning curves **overlap** — the feature-based sharpening/difference the paper shows is essentially missing (the opposite failure to Fig 5: too weak rather than too strong). *(Inspection-identified.)*

### Figure 7 — Two stimuli in the RF: combined attention shifts  ❌ DIVERGENT (gain magnitude)
<table><tr><th>Paper</th><th>Reproduced</th></tr><tr><td><img src="article_aware/figures/figure_7.jpg" width="430"></td><td><img src="figures_reproduced/figure_7.png" width="430"></td></tr></table>

The curve ordering (attend-variable > fixation > attend-nonpreferred) is right, but the attend-variable peak is **~3.3× the ignored** vs the paper's **~1.4×** — the attention gain is more than twice too strong. *(Inspection-identified.)*

## How it was verified — and how it slipped through

**The auditors passed this as faithful, and were wrong.** The Faithfulness Auditor compared the rendered figures to the paper images and the Process Auditor checked the reasoning trail; both signed off "faithful," and the deterministic tests (81, all green) passed — because every test asserted only *qualitative shape* claims ("attended above ignored," "same width," "multiplicative scaling"), never the **magnitudes**, and the "absolute magnitude is non-binding" convention explicitly excused exactly the errors above. A normalization model's magnitudes are its result, so that convention was a leniency hole.

What actually caught the divergences was (1) **a human eye on the side-by-side**, and (2) **pinning each panel's axes to the paper's**, which turned Fig 4E's hidden overflow into a failing test. The systemic fix in progress: **per-panel curve digitization** — digitize the paper's curve and require the model's curve to overlay it within tolerance — which will turn Figs 2/3/5/6/7's inspection-found divergences into deterministic failures too, and (with Phase A owning the view) make presentation deviation impossible rather than merely caught.

**No constructed stub.** Every figure is a live `protocols.run_figure_*` → `measurements` → `views` computation from the divisive-normalization equations — the divergences are genuine model behavior, not a hand-built answer. Audit records: `logs/faithfulness_audit/` (r0/r1/r2, 2026-06-03); open items: `logs/spec_questions.md`.

## Repository layout

`implementation/src/rh_model/` holds the model (`model.py`), protocols, measurements, and `views.py` (`python -m rh_model.views` writes `implementation/figure_outputs/figure_<N>.png`). `article_aware/spec/` carries the spec, citations, and calibration ledger; `article_aware/figures/` the paper images, per-panel crops/descriptions, and visual checklists; `figures_reproduced/` the committed reproduced PNGs (panel layout); `logs/` the audit and spec-question records.
