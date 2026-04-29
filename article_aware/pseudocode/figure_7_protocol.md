# Figure 7 Protocol — Two Stimuli in RF, Three Attention Conditions

## Purpose
Reproduce Treue & Martinez-Trujillo (1999): with two stimuli in the same RF
(one nonpreferred and fixed, one variable direction), spatial+feature
attention to one or the other shifts the tuning curve in opposite ways.

## Inputs
- Two stimuli, both in the receptive field of the recorded MT neuron (x = 0):
  - Nonpreferred stimulus: motion direction θ_np = 180° (opposite to neuron's
    preferred), contrast 0.5, fixed.
  - Variable stimulus: motion direction θ_var varied across trials, contrast
    0.5.
- Three attention conditions:
  - Attend fixation: spatial attention away from RF; feature flat.
  - Attend nonpreferred: spatial attention at x = 0 (RF), feature-selective
    for θ_np.
  - Attend variable: spatial attention at x = 0 (RF), feature-selective for
    the current θ_var.
- Parameters: stimulus_size = 5, attention_field_size = 5, tuning_width = 45°
  (for the feature-selective conditions), γ = 5.

## Sweep
- θ_var across [-180°, 180°] in steps of ~15°.
- Attention condition ∈ {fixation, nonpreferred, variable}.

## Procedure
For each (θ_var, attention_condition):
1. Construct E(x, θ) summing the two stimuli (nonpreferred at θ_np, variable
   at θ_var; both at x = 0, contrast 0.5).
2. Construct A(x, θ):
   - fixation: spatial Gaussian away from RF (e.g., x_fix = +30), flat in θ.
   - nonpreferred: spatial Gaussian at x = 0, feature-selective at θ_np
     (σ_θ = 45°).
   - variable: spatial Gaussian at x = 0, feature-selective at θ_var
     (σ_θ = 45°).
3. Compute S, R per EQ-6, EQ-5.
4. Record R(x = 0, θ = 0).

## Outputs
- fixation_tuning[θ_var]
- attend_nonpref_tuning[θ_var]
- attend_variable_tuning[θ_var]

## Expected behavior (citations)
- C-018, C-021 / Tuning when attending the variable stimulus has larger
  responses near the preferred direction than the fixation baseline.
- C-018, C-021 / Tuning when attending the nonpreferred stimulus has smaller
  responses near the preferred direction than the fixation baseline.
- The two attention conditions (variable vs nonpreferred) shift the apparent
  tuning in opposite directions.
