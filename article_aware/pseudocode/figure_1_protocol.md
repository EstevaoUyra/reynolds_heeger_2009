# Figure 1 Protocol — Four Rendered Population Fields (E, A, S, R)

## Purpose

Reproduce the four rendered model-output boxes of Figure 1 as **2D grayscale heatmaps**
(receptive-field center × orientation preference): Stimulus Drive (E = `Eraw`), Attention
Field (A), Suppressive Drive (S = `I`), and Population Response (R). These are NOT a cartoon —
they are the activity maps the authors render with `showActivityMaps=1` in the Test/debug
section of `attentionModel.m` (the `R1` call, tagged CODE-019). The S and R renders are the
paper-image check on the suppression-fix values `IthetaWidth = 360` (CODE-011) and
`sigma = 1e-6` (CODE-014).

## Binding configuration (CODE-019 — the authors' `R1` call)

- Grids:
  - `x = -200:200` (401 samples, step 1) — RF center axis.
  - `theta = -180:180` (361 samples, step 1) — orientation-preference axis.
- Stimulus (two equal-amplitude vertical gratings):
  - Right (attended): center `x = +100`, `θ = 0`.
  - Left: center `x = -100`, `θ = 0`.
  - Each = outer product `makeGaussian(theta, 0, 1, height=1) ⊗ makeGaussian(x, center, 5, height=1)`
    (σ_θ = 1, σ_x = stimWidth = 5, peak height 1). `stim = stim1 + stim2`.
- Attention (on the RIGHT): `Ax = +100`, `AxWidth = 30`, `Atheta` UNSET → flat in θ,
  `Ashape = 'oval'`, `Apeak = 2` (γ), `Abase = 1`.
- Engaged defaults: `ExWidth = 5`, `EthetaWidth = 60`, `IxWidth = 20`,
  `IthetaWidth = 360` (CODE-011), `sigma = 1e-6` (CODE-014).
- Kernels are **unit-volume separable Gaussians** (`makeGaussian` no-height → `normpdf`):
  `ExKernel = G(x;0,5)`, `EthetaKernel = G(θ;0,60)`, `IxKernel = G(x;0,20)`,
  `IthetaKernel = G(θ;0,360)`. Convolution is separable, **zero-padded in x, circular in θ**
  (CODE-002 / CODE-003).

## Procedure (matches attentionModel.m)

1. **Build the stimulus** `stim(θ, x)` = sum of the two outer-product gratings above.
2. **Stimulus drive (rendered E):**
   `Eraw = conv2sepYcirc(stim, ExKernel, EthetaKernel)`.
   This is the quantity rendered in the "Stimulus drive" box — **before** attention.
3. **Attention field (rendered A):**
   `attnGainX = makeGaussian(x, Ax=100, AxWidth=30, height=1)` (peak 1, Gaussian in x).
   `attnGainTheta = ones(size(theta))` (Atheta unset → flat in θ).
   `attnGain = (Apeak - Abase) * (impulse_θ0 ⊗ attnGainX convolved with attnGainTheta) + Abase`
   → ranges Abase=1 (baseline) to Apeak=2 (peak at x=+100), flat in θ.
4. **Attention-modulated drive:** `E = attnGain .* Eraw` (used for S and R, NOT for the E render).
5. **Suppressive drive (rendered S):**
   `I = conv2sepYcirc(E, IxKernel, IthetaKernel)` (σ_x=20, σ_θ=360, circular in θ).
6. **Population response (rendered R):**
   `R = E ./ (I + sigma)`, `sigma = 1e-6`.

## Rendering (the four heatmaps)

For each field, render a grayscale image with x = RF center (horizontal) and θ = orientation
preference (vertical), matching the authors' `imshow(_, [0, max])`:

- E box: `imshow(Eraw, [0, max(Eraw)])` — per-panel [0, max], black=0.
- A box: `imshow(attnGain, [0, max(attnGain)])` — 0→black, 1→midgray, 2→white.
- S box: `imshow(I, [0, max(I)])` — per-panel [0, max], black=0.
- R box: `imshow(R, [0, max(R)])` — per-panel [0, max], black=0.

Label x = "Receptive field center", y = "Orientation preference" on each.

## Outputs

- `E`, `A`, `S`, `R` — the four 2D fields (θ × x) and their grayscale renders.
- For sanity logging / tests, also expose 1D slices through θ = 0 (`E_slice`, `A_slice`,
  `S_slice`, `R_slice` vs x) and the attended/unattended R peaks
  (`R_at_attended = R(θ=0, x=+100)`, `R_at_unattended = R(θ=0, x=-100)`).

## Expected behavior (checks — see figure_1_visual_checklist.md)

- **E render is left/right SYMMETRIC** (it is `Eraw`, pre-attention): two equally-bright,
  narrow vertical stripes at x = ±100. (CODE-019)
- **A**: flat in θ, Gaussian bump in x peaked at x = +100, baseline midgray on the left, never
  black. (C-009)
- **S**: two broad bands much wider in x than the E stripes; **right band brighter** than left;
  near-uniform along the full θ height (broad-θ pool, CODE-011). (EQ-6, C-006)
- **R**: two narrow stripes (≈ E width, NOT S width); **right stripe brighter** than left;
  left stripe present but dimmer; dark gap between. `R_at_attended > R_at_unattended`.
  (EQ-5, C-005, C-021)
