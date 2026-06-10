# Figure 6 Protocol — Feature-Based Attention, Tuning Sharpening

## Purpose
Reproduce Martinez-Trujillo & Treue (2004): feature-based attention selective
for motion direction sharpens the recorded neuron's direction tuning.

## Inputs
> **AUTHORS' Figure6C.m (CODE-018/CODE-021) — the authoritative 6C contract.**

- **TWO separated stimuli**, both motion direction θ = 0, contrast 1.0
  (CODE-021), spatial σ = stimWidth = 10:
  - x = +100 (RF of recorded MT neuron) — stim1.
  - x = -100 (opposite hemifield) — stim2.
  - Stimulus construction (CODE-021): `stim = contrast² · stim1 + stim2`
    (RF stimulus scaled by contrast², contralateral by 1). At contrast = 1.0
    this is the identity sum `stim1 + stim2`.
- The recorded neuron's RF is at **x = +100**; spatial attention is always
  directed AWAY from it (to fixation or to the opposite-hemifield stimulus).
- Two attention conditions:
  - **Attend fixation** (baseline): an orientation-FLAT spatial Gaussian at
    fixation `Ax = 0` (AxWidth = 30); flat in θ. (Spatial attention away from
    the RF is represented by this baseline, NOT by stripping the feature
    component — see A-014/SQ-006.)
  - **Attend opposite-hemifield stimulus**: a `cross`-shape attention field
    (separable spatial × feature gain, Ashape='cross', CODE-018) centred at
    the opposite stimulus `Ax = -100` (AxWidth = 30) AND feature-selective for
    its direction `Atheta = 0` (AthetaWidth = 60°). Feature-based attention is
    **spatially GLOBAL** so the directional gain reaches the recorded neuron at
    x = +100 (A-014/SQ-006); the recorded neuron is read as the column at x=+100.
- Parameters: stimulus_size (stimWidth) = 10, attention_field_size
  (AxWidth) = 30, tuning_width (AthetaWidth) = 60° (when attending the moving
  stimulus; flat when attending fixation), γ (Apeak) = 2, contrast = 1.0 (CODE-021).

> **Ashape='cross' (CODE-018).** Figure6C.m uses Ashape='cross' for the
> attend-stimulus condition — a SEPARABLE spatial×feature gain (an additive
> "cross" of a spatial arm and a feature arm) rather than the default 'oval'
> outer product. The oval approximation mildly overshoots the digitized
> magnitude (~1.17 vs ~1.11); do NOT tune it (the residual is the cross-vs-oval
> shape, not a free knob).

## Sweep
- The tuning curve is the recorded column R(:, x=+100) across all motion-direction
  preferences θ ∈ [-180°, 180°], read in one model run per attention condition.
- Stimulus contrast: **fixed at 1.0** (CODE-021).
- Attention condition ∈ {attend_fixation, attend_opposite_stimulus}.

## Procedure
For each attention_condition:
1. Construct E(x, θ): `contrast² · stim1(x=+100, θ=0) + stim2(x=-100, θ=0)`,
   contrast = 1.0.
2. Construct A(x, θ):
   - attend_fixation: spatial Gaussian centred at x = 0 (AxWidth = 30), flat in θ.
   - attend_opposite_stimulus: cross-shape field — spatial arm centred at
     x = -100, feature arm selective for θ = 0 (σ_θ = AthetaWidth = 60°);
     feature component is spatially global so it reaches x = +100 (A-014).
3. Compute S, R per EQ-6, EQ-5.
4. Record the column R(:, x = +100) — the recorded neuron's tuning across θ.

## Outputs
- attend_fixation_tuning[θ]
- attend_opposite_stimulus_tuning[θ]
- normalized_attend_opposite_tuning[θ] = tuning normalized to its peak
  (for shape comparison).

## Expected behavior (citations)
- C-023: attend_opposite_stimulus tuning is narrower (sharper) than
  attend_fixation tuning. Quantitatively: full-width-at-half-maximum of
  the attend_opposite tuning curve is smaller than that of the attend_fixation
  tuning curve.
- C-021 (location-dependent): the attend_opposite condition can have larger
  responses near the recorded neuron's preferred direction (θ = 0) and smaller
  responses far from it, due to feature selectivity.
