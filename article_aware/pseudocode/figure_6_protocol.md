# Figure 6 Protocol — Feature-Based Attention, Tuning Sharpening

## Purpose
Reproduce Martinez-Trujillo & Treue (2004): feature-based attention selective
for motion direction sharpens the recorded neuron's direction tuning.

## Inputs
- Two stimuli (moving gratings/dots), one in the RF of the recorded MT neuron
  (x = 0), one in the opposite hemifield (x_opp = -20). Their motion
  directions are yoked (always the same θ_stim).
- Spatial attention is always away from the recorded neuron's RF (i.e., not
  on the stimulus in the RF).
- Two attention conditions:
  - Attend fixation: attention field flat across motion directions, centered
    on the fixation point (i.e., neither at the recorded RF nor at the
    opposite-hemifield stimulus).
  - Attend opposite-hemifield stimulus: spatial attention at x_opp,
    feature-selective for the current θ_stim.
- Parameters: stimulus_size = 10, attention_field_size = 30,
  tuning_width = 60° (when attending stimulus; flat when attending fixation),
  γ = 2.

## Sweep
- θ_stim across [-180°, 180°] in steps of ~15°.
- Attention condition ∈ {attend_fixation, attend_opposite_stimulus}.

## Procedure
For each (θ_stim, attention_condition):
1. Construct E(x, θ) summing the two stimuli (both at θ_stim, one at x = 0,
   one at x_opp = -20), each at fixed contrast 0.5.
2. Construct A(x, θ):
   - attend_fixation: spatial Gaussian centered at fixation (e.g., x_fix =
     +20, far from both RF and opposite stimulus), flat in θ.
   - attend_opposite_stimulus: spatial Gaussian centered at x_opp = -20,
     feature-selective with σ_θ = tuning_width = 60° around θ_stim.
3. Compute S, R per EQ-6, EQ-5.
4. Record R(x = 0, θ = 0).

## Outputs
- attend_fixation_tuning[θ_stim]
- attend_opposite_stimulus_tuning[θ_stim]
- normalized_attend_opposite_tuning[θ_stim] = tuning normalized to its peak
  (for shape comparison).

## Expected behavior (citations)
- C-023: attend_opposite_stimulus tuning is narrower (sharper) than
  attend_fixation tuning. Quantitatively: full-width-at-half-maximum of
  the attend_opposite tuning curve is smaller than that of the attend_fixation
  tuning curve.
- C-021 (location-dependent): the attend_opposite condition can have larger
  responses at θ_stim near the recorded neuron's preferred direction
  (θ = 0) and smaller responses far from it, due to feature selectivity.
