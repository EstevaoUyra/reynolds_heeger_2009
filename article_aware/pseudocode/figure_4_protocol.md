# Figure 4 Protocol — Two Stimuli in RF, Attention by Direction

## Purpose
Show that the same model produces (4C) contrast-gain-like and (4E)
response-gain-like attentional modulation depending on which stimulus is
attended and how stimulus contrasts are configured.

## Inputs
- Two stimuli, both inside the receptive field of the recorded MT neuron
  (x = 0, θ_pref = 0):
  - "Preferred" stimulus: motion direction θ = 0 (matches recorded neuron).
  - "Nonpreferred" stimulus: motion direction θ = 180° (opposite).
- Stimuli colocated at x = 0 (within RF, not separated).
- Per protocol:
  - 4C: contrast of preferred stimulus c_pref varied; contrast of
    nonpreferred stimulus c_nonpref fixed. Two attention conditions:
    attend nonpreferred-in-RF vs attend opposite hemifield.
  - 4E: contrasts of preferred and nonpreferred stimuli covary
    (c_pref = c_nonpref = c). Two attention conditions: attend preferred
    vs attend nonpreferred.
- Parameters: stimulus_size = 5, attention_field_size = 5, tuning_width = 20°,
  γ = 5.

## Sweep
- 4C: c_pref logarithmically across [0.01, 1] with 8 points; c_nonpref = 0.5
  (a fixed mid-range contrast).
- 4E: c logarithmically across [0.01, 1] with 8 points (covaried).

## Procedure (4C)
For each (c_pref, attention_condition):
1. Construct E(x, θ) = sum over the two stimuli (preferred at θ = 0,
   contrast c_pref; nonpreferred at θ = 180°, contrast c_nonpref = 0.5).
2. Construct A(x, θ): Gaussian centered at x = 0; for "attend nonpref",
   feature-selective for θ = 180° with σ_θ = tuning_width; for "attend
   opposite hemifield", flat over the recorded neuron's RF (constant 1).
3. Compute S, R per EQ-6, EQ-5.
4. Record R(x = 0, θ = 0).

## Procedure (4E)
For each (c, attention_condition):
1. Construct E(x, θ) with both stimuli at contrast c.
2. Construct A(x, θ): Gaussian centered at x = 0; feature-selective for
   θ = 0 ("attend preferred") OR θ = 180° ("attend nonpreferred"), σ_θ =
   tuning_width.
3. Compute S, R as above; record R(x = 0, θ = 0).

## Outputs
- 4C: attended_CRF[c_pref], unattended_CRF[c_pref], percent_modulation[c_pref].
- 4E: attend_pref_CRF[c], attend_nonpref_CRF[c], ratio[c] =
  attend_pref / attend_nonpref.

## Expected behavior (citations)
- C-015, C-021 / 4C: attending the nonpreferred-in-RF stimulus shifts the
  balance toward suppression of the recorded neuron, producing a suppressive
  contrast-gain change. The attended curve is rightward-shifted relative to
  unattended (unattended curve is the higher one), and the absolute value of
  percent modulation is largest at low / intermediate c_pref.
- C-015, C-021 / 4E: attending preferred yields larger response than
  attending nonpreferred across the full contrast range; the difference is
  approximately a multiplicative scaling (response gain).
