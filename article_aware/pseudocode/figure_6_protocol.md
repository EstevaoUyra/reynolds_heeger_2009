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
  - **Attend opposite-hemifield stimulus**: the author `cross`-shape attention
    field (additive separable spatial × feature gain, Ashape='cross', CODE-018,
    EQ-attention 'cross' form) centred at the opposite stimulus `Ax = -100`
    (AxWidth = 30) AND feature-selective for its direction `Atheta = 0`
    (AthetaWidth = 60°). Because the spatial arm is centred at x = -100 and the
    recorded RF is at x = +100 (~6.7σ away), the spatial arm ≈ 1 there, so the
    'cross' reduces over the RF to `A(RF,θ) = γ + (γ-1)²·G_θ(θ)` — the directional
    gain DOES reach the recorded neuron (A-014/SQ-006). The recorded neuron is read
    as the column at x = +100 (BINDING ledger key figure_6C.stim_rf_x).
- Parameters: stimulus_size (stimWidth) = 10, attention_field_size
  (AxWidth) = 30, tuning_width (AthetaWidth) = 60° (when attending the moving
  stimulus; flat when attending fixation), γ (Apeak) = 2, contrast = 1.0 (CODE-021).

> **Ashape='cross' is BINDING (CODE-018, A-014).** Figure6C.m uses Ashape='cross'
> for the attend-stimulus condition — the ADDITIVE separable spatial×feature gain
> A=(γ-1)·attnGainX·attnGainθ+1 (attentionModel.m:146-162), NOT the default 'oval'
> outer product and NOT a flat-in-x full-γ θ proxy. The author 'cross' lands at the
> digitized panel (attend-feature/attend-fixation peak ratio 1.108, FWHM ratio
> ~0.87-0.89; verified author reproduction 1.109/0.887). The oval/flat-x proxy
> OVER-scales (peak ratio 1.170, +5.5%) and OVER-sharpens (FWHM ratio 0.831) — it
> is the 6C CONTRACT BUG (2026-06-10 contract audit) and MUST NOT be substituted.
> The targets are reachable by the correct mechanism from the single Table-1/code
> constants (γ=2, AxWidth=30, AthetaWidth=60); do NOT tune the proxy to fit them.

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
   - attend_fixation: oval spatial Gaussian centred at x = 0 (AxWidth = 30),
     flat in θ — A = 1 + (γ-1)·G_x(x-0).
   - attend_opposite_stimulus: author 'cross' field (EQ-attention cross form,
     A-014) —
       attnGainX(x) = (γ-1)·G_x(x-(-100); AxWidth=30) + 1
       attnGainθ(θ) = (γ-1)·G_θ(θ-0; AthetaWidth=60) + 1
       A(x,θ)       = (γ-1)·attnGainX(x)·attnGainθ(θ) + 1
     At the recorded RF (x=+100) the spatial arm ≈ 1, so the feature gain reaches
     the neuron: A(RF,θ) = γ + (γ-1)²·G_θ(θ). Do NOT use the oval/flat-x proxy.
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
