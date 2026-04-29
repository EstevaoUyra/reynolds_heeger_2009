# Figure 1 Protocol — Schematic / Population Visualization

## Purpose
Illustrative. Produce the four population fields (stimulus drive E,
attention field A, suppressive drive S, output firing rate R) for a
two-grating stimulus with attention to the right stimulus. No
quantitative reproduction of the 2D schematic is attempted (per A-006:
1D simulations only).

## Inputs
- Two stimuli (gratings, preferred orientation θ_0 = 0°):
  - Left: x = -10, contrast c = 0.5
  - Right: x = +10, contrast c = 0.5
- Attention directed to the right stimulus (attention field centered at x = +10).
- Parameters (overrides from spec): stimulus_size = 3, attention_field_size = 30,
  peak_attention_gain_gamma = 2, tuning_width = 30°.

## Procedure
1. Build E(x, θ) per EQ-stim, summing both stimulus contributions.
2. Build A(x, θ): Gaussian in x (σ = attention_field_size) centered at x = +10,
   flat (uniform) in θ; baseline 1, peak γ = 2.
3. Compute S(x, θ) per EQ-6.
4. Compute R(x, θ) per EQ-5.

## Outputs
- 1D slices through θ = 0 of E, A, S, R as functions of x.
- Population sums Σ_x E, Σ_x R for sanity logging.

## Expected behavior (citations)
- C-009: All four fields exhibit smooth (Gaussian-derived) profiles in space
  and feature.
- C-021: R is larger at the attended stimulus location (x = +10) than at the
  unattended one (x = -10).
