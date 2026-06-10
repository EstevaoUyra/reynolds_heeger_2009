# Figure 5 Protocol — Spatial Attention, Multiplicative Scaling of Tuning

## Purpose
Reproduce McAdams & Maunsell (1999): spatial attention with a broad
(orientation-flat) attention field multiplicatively scales the orientation
tuning curve without changing its shape.

## Inputs
> **AUTHORS' Figure5C.m (CODE-018/CODE-021) — the authoritative 5C contract.**

- **TWO separated stimuli**, both preferred orientation θ = 0, contrast 1.0
  (CODE-021), spatial σ = stimWidth = 10:
  - x = +100 (RF of recorded neuron) — the **attended/RF** stimulus (stim1).
  - x = -100 (opposite hemifield) — the contralateral stimulus (stim2).
  - Stimulus construction (CODE-021): `stim = contrast² · stim1 + stim2`
    (the RF stimulus scaled by contrast², the contralateral by 1). At the
    author contrast = 1.0 this is the identity sum `stim1 + stim2`; the
    asymmetric contrast² factor only matters if a non-1 contrast is used.
- The recorded neuron's RF is at **x = +100**; its response is read across all
  feature preferences θ (one population column = one tuning curve).
- Two attention conditions, both an **orientation-FLAT (broad) spatial Gaussian**
  (AxWidth = attention_field_size = 10, Atheta unspecified → flat in θ, γ = 2):
  - Attend RF: spatial attention centred at x = +100 (the recorded RF).
  - Attend away: spatial attention centred at x = -100 (opposite hemifield).
- Parameters: stimulus_size (stimWidth) = 10, attention_field_size
  (AxWidth) = 10, γ (Apeak) = 2, contrast = 1.0 (CODE-021). The orientation
  tuning width is the model's stimulation-feature width (no per-figure
  attention θ width — the attention field is flat in θ here).

## Sweep
- The tuning curve is the recorded column R(:, x=+100) — i.e. responses across
  all orientation preferences θ ∈ [-180°, 180°], read in one model run per
  attention condition (NOT a per-orientation loop; the author records the whole
  population column at the RF center).
- Stimulus contrast: **fixed at 1.0** (CODE-021).
- Attention condition: attend-RF (x=+100) vs attend-away (x=-100).

## Procedure
For each attention_condition:
1. Construct E(x, θ) from the two stimuli: `contrast² · stim1(x=+100, θ=0)
   + stim2(x=-100, θ=0)`, contrast = 1.0.
2. Construct A(x, θ): an orientation-FLAT spatial Gaussian
   (σ_x = attention_field_size = 10, peak γ = 2, flat in θ), centred at
   x = +100 (attend-RF) or x = -100 (attend-away).
3. Compute S, R per EQ-6, EQ-5.
4. Record the column R(:, x = +100) — the recorded neuron's tuning across θ.

## Outputs
- attended_tuning[θ]   (= column at x=+100, attend-RF)
- unattended_tuning[θ] (= column at x=+100, attend-away)
- ratio[θ] = attended_tuning / unattended_tuning

## Expected behavior (citations)
- C-022: Attended tuning curve is approximately a multiplicative scaling
  of unattended tuning curve, with the ratio approximately constant across
  θ (no shape change — same FWHM, no sharpening).
- C-021: attended ≥ unattended at every θ.
