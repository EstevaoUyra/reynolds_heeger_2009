# Figure 2 Protocol — Contrast vs Response Gain

## Purpose
Demonstrate that varying stimulus size and attention-field size relative to
the stimulation field yields qualitatively different attentional modulation
patterns: contrast gain (2A) vs response gain (2B).

## Inputs
- Single stimulus in the receptive field of the recorded neuron (x = 0, θ = 0,
  preferred).
- Per panel (parameter overrides from spec):
  - 2A: stimulus_size = 3, attention_field_size = 30, γ = 2.
  - 2B: stimulus_size = 5, attention_field_size = 3, γ = 2.

## Sweep
- Contrast c logarithmically across [0.01, 1] with 8 points.
- Attention condition ∈ {attended, unattended}.

## Procedure
For each (c, attention_condition):
1. Construct E(x, θ) for the stimulus at contrast c per EQ-stim.
2. Construct A(x, θ): Gaussian centered at x = 0, peak γ for attended;
   constant 1 (no modulation) for unattended.
3. Compute S(x, θ) per EQ-6.
4. Compute R(x, θ) per EQ-5.
5. Record R(x = 0, θ = 0).

## Outputs
- For each panel: attended_CRF[c], unattended_CRF[c],
  percent_modulation[c] = 100 · (attended - unattended) / unattended.

## Expected behavior (citations)
- C-019 / 2A: contrast gain — attended curve leftward-shifted on log-contrast
  axis vs unattended; percent modulation peaks at intermediate contrasts.
- C-019 / 2B: response gain — attended curve upward-shifted; percent
  modulation roughly flat or largest at high contrast.
- C-020: Both — output saturates as c → 1.
- C-021: attended ≥ unattended at every contrast.
