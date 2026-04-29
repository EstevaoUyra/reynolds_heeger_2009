# Figure 5 Protocol — Spatial Attention, Multiplicative Scaling of Tuning

## Purpose
Reproduce McAdams & Maunsell (1999): spatial attention with a broad
(orientation-flat) attention field multiplicatively scales the orientation
tuning curve without changing its shape.

## Inputs
- Single grating stimulus at x = 0 (in RF of recorded V4 neuron); orientation
  varied across trials.
- Two attention conditions:
  - Attend grating in RF (orientation discrimination task) — attention field
    centered at x = 0, flat across θ.
  - Attend opposite hemifield (color discrimination task) — attention field
    flat at 1 over the recorded neuron's RF.
- Parameters: stimulus_size = 10, attention_field_size = 10, γ = 2,
  tuning_width = 30° (V4 oriented gratings; per C-011).

## Sweep
- Stimulus orientation θ_0 across [-90°, 90°] in steps of ~10°.
- Stimulus contrast: fixed at a mid-range value (c = 0.5).
- Attention condition: attended vs unattended.

## Procedure
For each (θ_0, attention_condition):
1. Construct E(x, θ) for the stimulus at orientation θ_0, contrast 0.5.
2. Construct A(x, θ): Gaussian centered at x = 0 in space, flat in θ for
   attended (peak γ baseline 1); constant 1 over the RF for unattended.
3. Compute S, R per EQ-6, EQ-5.
4. Record R(x = 0, θ = 0) — the recorded neuron's response.

## Outputs
- attended_tuning[θ_0]
- unattended_tuning[θ_0]
- ratio[θ_0] = attended_tuning / unattended_tuning

## Expected behavior (citations)
- C-022: Attended tuning curve is approximately a multiplicative scaling
  of unattended tuning curve, with the ratio approximately constant across
  θ_0 (no shape change).
- C-021: attended ≥ unattended at every θ_0.
