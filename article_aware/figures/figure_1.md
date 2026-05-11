# Figure 1 — Normalization Model of Attention: Pipeline Schematic

## Role in the paper

Figure 1 is the architectural introduction to the normalization model. It appears immediately
after the model equations and makes the pipeline concrete by showing the four key population
fields — stimulus drive (E), attention field (A), suppressive drive (S), and output firing
rate (R) — as 2D population images for a specific example: two equal-contrast vertical
gratings, one per hemifield, with attention directed to the right. It establishes the visual
representation convention (RF center × orientation preference) used throughout the paper.
The figure makes no quantitative claim about a gain regime; that is the subject of Figures
2–7. Its purpose is to show that the model pipeline produces a sensible, interpretable
population response and to make explicit how attention reshapes the population by selectively
amplifying the attended location before normalization.

---

## Verbatim caption

> "Normalization Model of Attention. The stimulus drive is multiplied by the attention field
> and divided by the suppressive drive to yield the output firing rates. Left panel depicts
> the stimulus. A pair of vertically orientated gratings were presented as input to the model,
> identical in contrast, one in each hemifield. Central black dot, fixation point. Solid circle
> indicates the receptive field of a model neuron selective for vertical orientation and centered
> on the grating stimulus in the right hemifield. Dashed red circle indicates the attention
> field, which was centered on the stimulus on the right. Middle panel depicts the stimulus
> drive for a collection of neurons with different receptive field centers and orientation
> preferences. Neurons are organized according to their receptive field center (horizontal
> position) and preferred orientation (vertical position). Brightness at each location in the
> image corresponds to the stimulus drive to a single neuron. Top panel depicts the attention
> field when attending to the stimulus on the right (i.e., corresponding to the dashed red
> circle in the left panel). The attentional field is the strength of the attentional
> modulation as a function of receptive field center and orientation preference. Here,
> attentional gain varied as a function of stimulus position, without regard to orientation.
> Midgray indicates a value of 1 and white indicates a value greater than 1. The attention
> field is multiplied point-by-point with the stimulus drive. The suppressive drive (bottom
> panel) is computed from the product of the stimulus drive and the attention field, and then
> pooled over space and orientation. The panel on the right shows a neural image depicting
> the output firing rates of the population of neurons, computed by dividing the stimulus
> drive by the suppressive drive. The stimulus, stimulation field, suppressive field, and
> attention field all had Gaussian profiles in space and orientation."

---

## Simulation parameters

| Parameter                          | Value | Citation |
|------------------------------------|-------|----------|
| Stimulus size (Gaussian σ, space)  | 3     | C-012    |
| Stimulation field size (σ, space)  | 5     | C-010    |
| Suppressive field size (σ, space)  | 20    | C-010    |
| Attention field size (σ, space)    | 30    | C-012    |
| Peak attention gain (γ)            | 2     | C-012    |
| Attention field orientation tuning | Flat (unselective) | C-009, C-012 |
| Suppressive field orientation tuning | Broad (180°)    | C-011    |
| Left stimulus contrast             | Equal to right    | C-012    |
| Right stimulus contrast            | Equal to left     | C-012    |
| Attended location                  | Right hemifield   | C-012    |

Spatial sizes are in arbitrary units; only relative values are meaningful (C-010). All
fields have Gaussian profiles in space and orientation (C-009).

---

## Coordinate convention

The population image panels share a 2D coordinate frame. The paper figure shows no axis
tick marks; positions are described using the protocol values as reference.

- **Horizontal axis (RF center, x):** left = left hemifield, right = right hemifield. Per
  the figure protocol, the left stimulus is at x = −10 and the right stimulus is at x = +10.
  Attention is directed to the right stimulus.
- **Vertical axis (orientation preference, θ):** spans the full range of orientation
  preferences. The stimuli are vertical gratings, so neurons tuned to vertical (θ ≈ 0°)
  receive the strongest stimulus drive.
- **Colormap for E, S, R:** black = zero; brighter/whiter = larger value. Standard
  zero-baseline encoding.
- **Colormap for A only:** midgray = 1 (no attentional gain). White = value > 1
  (attentional enhancement). Black would indicate gain < 1, which does not occur since
  the attention field baseline is 1. This non-standard encoding is stated explicitly in
  the verbatim caption and must not be confused with the zero-baseline encoding of the
  other panels.

---

## Pipeline and expected behavior

### Panel: Stimulus (schematic, not a population image)

A cartoon panel establishing the experimental scenario. It shows two vertical grating
patches, equal in contrast, one per hemifield, with a fixation dot at center. A solid
circle marks the RF of the model neuron of interest (right hemifield grating). A dashed
red circle marks the attention field centered on the same right stimulus. This panel is
informative about stimulus position, stimulus orientation, and attention location, but
contains no simulated population data.

### Panel: Stimulus Drive (E)

Governed by EQ-stim (C-009). E(x, θ) is the summed Gaussian contribution from both
gratings. Because both gratings are vertical and equal in contrast, E produces two
symmetric narrow bright stripes in (x, θ) space — one at the left stimulus position, one
at the right — against a black background.

- **Narrow in x:** stimulus size σ = 3 is smaller than the stimulation field size σ = 5
  (C-010), so each stripe is compact in the RF-center dimension.
- **Extended in θ:** neurons tuned to vertical receive maximum drive; the response falls
  off with a Gaussian of σ = 30° in orientation (C-011). The stripes are tall relative to
  the panel but taper toward the orientation extremes.
- **Equal brightness:** both stimuli have identical contrast, so both stripes are equally
  bright (C-012).
- **Separated:** the stimuli are 20 units apart (x = ±10) and each stripe is narrow (σ = 3),
  so there is a clear dark gap between them.

### Panel: Attention Field (A)

Governed by EQ-5 numerator term (C-005). A(x, θ) encodes attentional gain as a function
of RF center and orientation preference. With attention directed to the right stimulus:

- **Spatial profile:** Gaussian in x centered at x = +10 with σ = 30 (C-012). Because
  σ = 30 is large — 10× the stimulus size and 6× the stimulation field — the attention
  field is broad. Its peak is located in the right half of the x-axis, and the field
  returns toward the baseline before reaching the rightmost edge of the panel. The left
  portion of the panel is at or near the baseline (gain ≈ 1, midgray).
- **Orientation profile:** flat across all θ — "without regard to orientation" (verbatim
  caption, C-009). Every row of the panel looks identical.
- **Value range:** baseline = 1 (midgray); peak = γ = 2 (white) at x = +10 (C-012).
- **Colormap:** midgray encodes 1, not 0. The panel is nowhere black in a correct
  implementation, because gain ≥ 1 everywhere.

### Panel: Suppressive Drive (S)

Governed by EQ-6 (C-006): S(x, θ) = s(x, θ) ∗ [A(x, θ) · E(x, θ)], where s is a
Gaussian suppressive field with σ = 20 in space and σ = 180° in orientation (C-010, C-011).

- **Broadened in x:** convolving the narrow E stripes (σ = 3) with the large suppressive
  kernel (σ = 20) substantially smears each peak. The result is two broad bands, much
  wider in x than the corresponding E stripes. The ratio of suppressive field to stimulus
  size is 20/3 ≈ 6.7, so the broadening is visually dramatic.
- **Two distinct bands:** despite the broadening, the two peaks remain distinguishable.
  The stimuli are separated by 20 units and the suppressive field σ = 20, so the peaks
  are separated by approximately one kernel width — broad but not merged. A dark region
  is visible between them.
- **Right band brighter than left:** A(x, θ) · E(x, θ) is larger at x = +10 than at
  x = −10 because the attention field amplifies the right stimulus before pooling (C-006).
  Therefore the right suppressive band is brighter.
- **Extended in θ:** the suppressive field is nearly orientation-flat (σ_θ = 180°, C-011),
  so suppression spreads across the full orientation axis. Both bands span the full vertical
  extent of the panel.
- **Background:** regions far from both stimuli receive suppression from the pooling kernel's
  tails; the background is not pure black but is very dark.

### Panel: Population Response (R)

Governed by EQ-5 (C-005): R(x, θ) = ⌊[A(x, θ) · E(x, θ)] / [S(x, θ) + σ]⌋_T.

- **Two stripes, similar width to E:** the numerator A·E is localized at the two stimulus
  positions (same spatial structure as E, scaled by A). Dividing by the nearly-smooth S
  does not shift the peaks — the ratio preserves the spatial structure of the stimulus drive
  rather than the broadness of S. The stripes in R are therefore narrow, comparable in
  width to those in E (C-005).
- **Right brighter than left:** at x = +10, A ≈ 2 amplifies the numerator while the
  denominator S increases only modestly (pooling dilutes the local attention effect). At
  x = −10, A ≈ 1 so the numerator is not amplified. Net result: R_right > R_left (C-005,
  C-012).
- **Left stripe visible and non-negligible:** the unattended stimulus still drives E at
  x = −10; normalization reduces but does not eliminate this response. The left stripe in
  R is dimmer than the right but clearly present (C-005).
- **Dark gap preserved:** as in E, neurons between the two stimulus positions have near-zero
  numerators, so the dark gap persists in R.

---

## Key inter-panel relationships

1. **S is wider than E (suppressive field broadening):** the two narrow stripes in E become
   two broad bands in S because the suppressive field σ (20) is much larger than the stimulus
   size σ (3). This is visually the most dramatic inter-panel change. A correct implementation
   must show S bands substantially wider than E stripes along the x-axis. (EQ-6, C-002, C-010)

2. **S bands are distinct, not merged:** despite the broadening, the two bands in S remain
   separable — a dark region is visible between them. The stimulus separation (20 units) is
   comparable to the suppressive field σ (20), so the peaks broaden but do not fully collapse
   into a single blob. (EQ-6, C-010)

3. **Right band in S is brighter than left:** attention multiplies E before suppression is
   computed (EQ-6, C-006). The right stimulus receives higher gain (A ≈ 2) than the left
   (A ≈ 1), so the right S band is brighter. This asymmetry is introduced by attention.

4. **E is symmetric; R is not:** both stripes in E are equal in brightness (equal contrast,
   C-012). The two stripes in R are unequal — right brighter than left. This asymmetry is
   introduced entirely by A acting on the numerator. Any implementation where R is also
   symmetric has failed to apply attentional gain. (EQ-5, C-005)

5. **R stripe widths match E, not S:** the normalization ratio collapses back to the spatial
   footprint of the stimulus drive. R stripes are narrow (≈ E width), not broad like the S
   bands. This is a diagnostic check: if R stripes are as wide as S bands, the implementation
   is not correctly dividing by S. (EQ-5, C-005)

6. **R left stripe is present:** the unattended response is reduced but not eliminated.
   Winner-take-all suppression is not what the model predicts. A correct implementation shows
   a visible, non-negligible stripe at x = −10 in R. (EQ-5, C-005, C-021)

7. **A is orientation-flat:** every row of the attention field panel is identical. No
   vertical banding or orientation gradient should appear. This reflects the spatially
   selective but orientation-unselective attention condition in Figure 1 (C-009, C-012).
