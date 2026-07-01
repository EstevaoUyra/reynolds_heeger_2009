# Figure 1 — Normalization Model of Attention: Four Rendered Population Fields

## Role in the paper

Figure 1 is the architectural introduction to the normalization model. It is laid out as a
flow diagram — Stimulus → Stimulus Drive → (× Attention Field) → (pool → Suppressive Drive)
→ (÷) → Population Response — but **four of its boxes are not cartoons: they are rendered
model outputs.** The Stimulus Drive (E), Attention Field (A), Suppressive Drive (S), and
Population Response (R) boxes are grayscale 2D heatmaps of the corresponding population field,
plotted with **receptive-field center on the horizontal axis** and **orientation preference
on the vertical axis** (axis labels are printed on each box in the figure). Only the
far-left "Stimulus" box is a true schematic (two grating patches, fixation dot, RF circle,
attention-field circle).

These four field renders ARE a reproduction target (per extract-figure SKILL: a panel that
is a rendered model output is a reproduction target even inside a schematic). In particular,
the S and R renders are a **paper-grounded check on the suppression-fix values** — the
code-alone `IthetaWidth = 360` (CODE-011) and `sigma = 1e-6` (CODE-014): if the rendered S
field does not look like the paper's Suppressive-Drive box, the code values do not reproduce
the authors' own Figure 1, independent of the CRF curves in Figures 2–7.

The exact stimulus/attention configuration is fixed by the authors' own code — the
Test/debug section of `attentionModel.m` (the `R1` call), tagged **CODE-019** — not inferred.
This is the example the authors used to produce Figure 1 (`showActivityMaps=1` renders
exactly Stimulus / Stimulus drive / Attention field / Suppressive drive / Population response).

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

## Binding configuration (from the authors' code — CODE-019)

The four field renders are the outputs of the `R1` call in `attentionModel.m` (Test/debug
section, lines 225–245), tagged **CODE-019** in `code_refs.yaml`. This is the binding Fig-1
stimulus/attention config; the values below are read from that code, not from Table 1.

| Quantity | Value | Source |
|---|---|---|
| Spatial grid `x` | `-200:200` (401 samples, step 1) | CODE-019 |
| Orientation grid `θ` | `-180:180` (361 samples, step 1) | CODE-019 |
| Stimulus σ in space (`stimWidth`) | 5 | CODE-019 |
| Stimulus σ in orientation | 1 (near-impulse, vertical) | CODE-019 |
| Right stimulus center (`stimCenter1`, attended) | x = **+100** | CODE-019 |
| Left stimulus center (`stimCenter2`) | x = **−100** | CODE-019 |
| Both stimulus orientations | θ = 0 (vertical), equal amplitude | CODE-019 |
| Attention spatial center (`Ax`) | **+100** (the RIGHT stimulus) | CODE-019 |
| Attention spatial width (`AxWidth`) | 30 | CODE-019 |
| Attention orientation (`Atheta`) | unspecified → **flat in θ** | CODE-019 |
| Attention shape (`Ashape`) | `oval` (default) | CODE-019 |
| Peak attention gain (`Apeak` = γ) | 2 | CODE-015 / C-012 |
| Attention baseline (`Abase`) | 1 | CODE-015 |
| Stimulation field σ in space (`ExWidth`) | 5 | CODE-012 / C-010 |
| Stimulation field σ in θ (`EthetaWidth`) | 60° | CODE-013 |
| Suppressive field σ in space (`IxWidth`) | 20 | CODE-010 / C-010 |
| Suppressive field σ in θ (`IthetaWidth`) | **360°** (near-flat θ pool) | CODE-011 |
| Semi-saturation (`sigma`) | **1e-6** (≈ 0) | CODE-014 |

Notes:
- **Attention is on the RIGHT** (Ax = stimCenter1 = +100). The caption confirms "attention
  directed to the right."
- **`Atheta` is not passed**, so `attnGainTheta = ones` — the attention field is **flat in
  orientation** ("attentional gain varied as a function of stimulus position, without regard
  to orientation," caption / C-009).
- `IthetaWidth = 360°` (CODE-011) and `sigma = 1e-6` (CODE-014) are **code-alone** values not
  given in the paper text; the S and R renders are the paper-image check on them.

---

## Coordinate and colormap convention

The four field panels share a 2D frame; axis labels ("Receptive field center" on x,
"Orientation preference" on y) are printed in the figure.

- **Horizontal axis (RF center, x):** left = left hemifield (x = −100), right = right
  hemifield (x = +100). The grid spans x ∈ [−200, 200]; the two stimuli sit at x = ±100, i.e.
  each at the **half-way point between center and edge** on its side. Attention is on the
  right stimulus.
- **Vertical axis (orientation preference, θ):** spans θ ∈ [−180, 180], vertical (θ = 0) at
  the **vertical center**. The stimuli are vertical (θ = 0), so neurons tuned to vertical
  (mid-height) receive the strongest drive.
- **Colormap for E, S, R:** each is rendered with `imshow(_, [0, panel_max])` — black = 0,
  white = that panel's own maximum (per-panel min–max grayscale). This is a **per-panel**
  scale, so brightness is comparable *within* a panel, not *across* panels.
- **Colormap for A:** rendered `imshow(attnGain, [0, max(attnGain)])`. Because attnGain ranges
  from Abase = 1 (baseline) to Apeak = 2 (peak), and 0 maps to black: baseline 1 → **midgray**
  (halfway up the [0,2] scale), peak 2 → white. The caption states this explicitly: "Midgray
  indicates a value of 1 and white indicates a value greater than 1." A is **never black** in
  a correct render (its minimum value is 1 = midgray, not 0).

---

## Pipeline and per-panel expected behavior

### Box: Stimulus (true schematic — NOT a render)

Cartoon establishing the scenario: two vertical grating patches (equal contrast), one per
hemifield, fixation dot at center, a solid circle marking the RF of the model neuron (right
grating), and a dashed circle marking the attention field (centered on the right grating).
Encodes stimulus position/orientation and attention location; contains no simulated data.

### Box: Stimulus Drive (E) — rendered (`Eraw`)

The rendered "Stimulus drive" is **`Eraw = conv2sepYcirc(stim, ExKernel, EthetaKernel)`** —
the stimulus drive **before** the attention field is applied (`imshow(Eraw,[0,Emax])`,
attentionModel.m:200). Governed by the stimulation-field convolution (EQ-stim, C-009).

- **Two stripes, one per stimulus:** each grating produces one bright blob; both gratings are
  vertical and equal in amplitude, so E shows **two equally-bright stripes** at x = −100 and
  x = +100 against a near-black background.
- **Symmetric left/right:** the displayed E is `Eraw` (pre-attention), so the two stripes are
  **equal in brightness** — the attention asymmetry has NOT entered yet (it first appears in S
  and R, which use `E = attnGain.·Eraw`). This is the key correction over a naive reading:
  do not expect E to be brighter on the right.
- **Narrow in x:** each stripe's spatial spread is set by stimulus σ = 5 broadened by
  stimulation-field σ = 5 → compact relative to the 401-wide x-axis, well separated (centers
  200 samples apart).
- **Bounded in θ:** stimulus σ_θ = 1 broadened by stimulation-field σ_θ = 60° → a vertically
  centered band that tapers toward the orientation extremes; it does not fill the full height.

### Box: Attention Field (A) — rendered (`attnGain`)

The rendered "Attention field" is `attnGain = (Apeak−Abase)·[G_x(σ=30, ctr=+100) ⊗ ones_θ] +
Abase` (attentionModel.m:138–163, 205). EQ-5 numerator gain term (C-005).

- **Spatial profile:** Gaussian in x centered at **x = +100** with σ = AxWidth = 30. Its peak
  sits in the **right half** of the x-axis (at the right stimulus) and returns toward baseline
  before the right edge. The left half is at baseline.
- **Orientation profile:** **flat** across all θ (Atheta unspecified → `attnGainTheta = ones`).
  Every row is identical — no orientation gradient (C-009, caption).
- **Value range / colormap:** baseline = 1 (Abase) → **midgray**; peak = 2 (Apeak) → white.
  Nowhere black (minimum value is 1).

### Box: Suppressive Drive (S) — rendered (`I`)

`I = conv2sepYcirc(E, IxKernel, IthetaKernel)` with **`E = attnGain.·Eraw`** (the
attention-modulated drive), IxKernel σ = 20, IthetaKernel σ = 360° (CODE-011), unit-volume
separable Gaussians, circular in θ / zero-pad in x (CODE-002/003). `imshow(I,[0,Imax])`.
EQ-6 (C-006).

- **Broadened in x:** convolving the narrow E stripes with the σ = 20 spatial kernel smears
  each peak into a **broad band**, much wider in x than the E stripe (kernel σ = 20 vs.
  stimulus σ = 5).
- **Two bands, distinguishable:** the stimuli are 200 samples apart while IxWidth = 20, so the
  two bands broaden but remain **separable**, with a darker region between them.
- **Right band brighter than left:** attention enters S through `E = attnGain·Eraw`. The right
  stimulus is multiplied by A ≈ 2; the left by A ≈ 1. So the **right S band is brighter** —
  this is the first place the attention asymmetry appears.
- **Near-flat in θ:** IthetaWidth = 360° ≫ the 361-sample θ span, so the θ pool is essentially
  flat — each band spans the **full vertical (orientation) extent** of the panel, nearly
  uniform top-to-bottom (the broad-θ pool of CODE-011 is exactly what this render exercises).
- **Background:** dark but not pure black — the broad pooling tails leave a low non-zero floor.

### Box: Population Response (R) — rendered

`R = E ./ (I + sigma)` with `E = attnGain.·Eraw` and sigma = 1e-6 (CODE-014).
`imshow(R,[0,Rmax])`. EQ-5 (C-005).

- **Two stripes, narrow like E:** the numerator A·E is localized at the two stimulus positions;
  dividing by the broad, smooth S does not broaden the peaks. R stripes are **narrow**,
  comparable to E — NOT as broad as the S bands. (If R looks as wide as S, the division is wrong.)
- **Right noticeably brighter than left:** the attended (right) stripe is visibly brighter than
  the unattended (left) stripe in R — this is the phenomenon Figure 1 exists to demonstrate.
  The attention field (A=2 at the right stimulus, A=1 at the left) multiplies the numerator
  A·E; at the figure's operating contrast the denominator pool(A·E) is not yet at the
  scale-invariant plateau, so the boost is not cancelled, producing a clearly visible right>left
  ratio in R. The left (unattended) stripe remains present — normalization reduces it, not
  eliminates it (no winner-take-all, C-021). [ADJ-001 (2026-06-10) had softened this to
  "~1.01, not noticeably"; that adjudication is retracted — see logs/adjudications.yaml
  ADJ-001-RETRACTED.]
- **σ ≈ 0:** since sigma = 1e-6 ≪ I, R ≈ E/I; saturation/scale comes from the pooled I, not σ
  (CODE-014). The render is a paper-image check that this near-zero σ still yields a sensible R.
- **Dark gap preserved:** neurons between the two stimuli have near-zero numerators → dark gap
  between the two stripes persists.

---

## Key inter-panel relationships (grounded in equations)

1. **E is rendered pre-attention and is left/right SYMMETRIC.** The displayed Stimulus-Drive
   box is `Eraw` (attentionModel.m:200), before `attnGain` is applied. Its two stripes are
   **equal** in brightness. Any render where the E box is already brighter on the right has
   used the wrong quantity (it showed `E = attnGain·Eraw` instead of `Eraw`). (CODE-019)

2. **The attention asymmetry first appears in S, then R — not in E.** Because S and R use
   `E = attnGain·Eraw`, the right band/stripe is brighter than the left in **S and R**, while
   E stays symmetric. Right > left must hold in S and R and must be absent in E. (EQ-6/EQ-5,
   C-005/C-006)

3. **S is much wider in x than E (suppressive broadening).** The narrow E stripes (σ ≈ 5)
   become broad S bands via the σ = 20 spatial pool. S bands must be visibly wider than E
   stripes along x. (EQ-6, C-002/C-010, IxWidth=20)

4. **S is near-uniform along θ (broad-θ pool, CODE-011).** With IthetaWidth = 360° each S band
   spans the full orientation height with little top-to-bottom variation — a direct visual
   signature of the code-alone 360° θ pool. (CODE-011)

5. **R stripe widths match E, not S.** The normalization ratio collapses back to the stimulus
   footprint: R stripes are narrow like E, not broad like S. If R stripes are as wide as the S
   bands, division by S is not implemented correctly. (EQ-5, C-005)

6. **R right stripe is noticeably brighter than R left.** The attended (right) response is
   visibly higher than the unattended (left); the left stripe remains present (not eliminated —
   no winner-take-all), but clearly dimmer. This is the phenomenon the figure exists to show.
   (EQ-5, C-005/C-021)

7. **A is orientation-flat and right-biased in space.** Every row of A is identical (flat in θ);
   its bright peak sits over the right stimulus (x = +100) and decays to baseline (midgray) on
   the left. A is never black (min = 1 = midgray). (C-009, caption, CODE-019)
