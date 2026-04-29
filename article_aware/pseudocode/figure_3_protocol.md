# Figure 3 Protocol — Reynolds 2000 vs Williford & Maunsell 2006

## Purpose
Reconcile two empirical V4 attention patterns within a single model by
varying stimulus / attention sizes and adding baseline activity.
- 3C (Reynolds 2000): largest percent modulation at low contrast (apparent
  contrast gain).
- 3F (Williford & Maunsell 2006): percent modulation largest at low contrast,
  but largest absolute attended-minus-unattended difference at high contrast.

## Inputs
- Single stimulus at x = 0, θ = 0 (preferred).
- Per panel:
  - 3C: stimulus_size = 5, attention_field_size = 30, γ = 2.
  - 3F: stimulus_size = 7, attention_field_size = 7, γ = 2.
- Both panels (per A-007):
  - baseline_modulated_by_attention = 0.05
  - baseline_unmodulated = 0.05

## Sweep
- Contrast c logarithmically across [0.01, 1] with 8 points.
- Attention condition ∈ {attended, unattended}.

## Procedure
For each (c, attention_condition):
1. Construct E(x, θ) for the stimulus at contrast c per EQ-stim.
2. Form attention-modulated stimulus drive including baseline:
       E_with_baseline(x, θ) = E(x, θ) + baseline_modulated_by_attention.
3. Construct A(x, θ): Gaussian centered at x = 0, peak γ for attended;
   constant 1 for unattended.
4. Compute S(x, θ) per EQ-6, using A · E_with_baseline as the input that
   gets convolved with the suppressive field (i.e., the modulated baseline
   participates in normalization).
5. Compute R(x, θ) per EQ-5 using E_with_baseline in the numerator.
6. Add unmodulated baseline to the output:
       R_obs(x, θ) = R(x, θ) + baseline_unmodulated.
7. Record R_obs(x = 0, θ = 0).

## Outputs
- Per panel: attended_CRF[c], unattended_CRF[c], percent_modulation[c],
  absolute_difference[c] = attended - unattended.

## Expected behavior (citations)
- C-014, C-019 / 3C: percent modulation peaks at low contrast (contrast-gain
  flavor); attended curve leftward-shifted.
- C-014 / 3F: percent modulation still peaks at low contrast, but absolute
  difference largest at high contrast (mixed pattern).
- C-020: Both saturate as c → 1.
- C-021: attended ≥ unattended at every contrast for both.
