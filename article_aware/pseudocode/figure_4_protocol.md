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

> **PHASE-B BUILD NOTE (Finding 2, figure_4C_investigation-2026-06-03).** The 4C
> "attend nonpreferred-in-RF" condition is a **SPATIAL (location) attention cue
> to the receptive-field location** — the Martinez-Trujillo & Treue (2002) task:
> attend that RF patch to detect a target. A spatial cue at x = 0 boosts the
> drives of **BOTH** colocated stimuli (the swept preferred at θ = 0 AND the
> fixed nonpreferred at θ = 180°), so the gain reaches the recorded θ = 0
> neuron's numerator → **contrast-gain facilitation** (attended CRF ABOVE
> attend-away, leftward shift, positive %-modulation).
>
> The attention field must therefore be **flat over θ** (`feature_center = None`,
> uniform in feature, so the spatial Gaussian alone sets the gain over the RF).
> A *narrow feature-tuned* field isolated on θ = 180° (the prior build) lands the
> gain almost entirely on the nonpreferred population, which feeds ONLY the
> suppressive pool of the θ = 0 neuron and produces the wrong (suppression) sign —
> that is the **Fig-4E** mechanism (C-021), not 4C. Do NOT feature-tune the 4C
> attention field on θ = 180°.

For each (c_pref, attention_condition):
1. Construct E(x, θ) = sum over the two stimuli (preferred at θ = 0,
   contrast c_pref; nonpreferred at θ = 180°, contrast c_nonpref = 0.5).
2. Construct A(x, θ): for "attend nonpref-in-RF", a **spatial** attention field —
   Gaussian centered at x = 0 (σ_x = attention_field_size), **flat (uniform)
   over θ** — so the gain γ reaches both colocated stimuli, including the
   recorded neuron's preferred θ = 0 drive. For "attend opposite hemifield",
   the spatial Gaussian is centered far from the RF, so A ≈ 1 over the recorded
   neuron's RF (constant 1).
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
- C-015, C-019 / 4C: attending the nonpreferred-in-RF stimulus (a SPATIAL cue to
  the RF that boosts both colocated stimuli) **facilitates** the recorded
  neuron, producing a **contrast-gain change**. The attended curve is
  **leftward-shifted relative to unattended (the attended curve is the HIGHER
  one)**, and percent modulation is **positive**, largest (~+36%) at low /
  intermediate c_pref and declining toward high contrast (C-019: "contrast gain
  regime predicts a leftward shift … largest percentage modulation at
  intermediate contrasts"). Referent: Fig-4 caption + panel_C_digitized.json.
  (C-021 is the 4E mechanism prose and is NOT cited for 4C — see Finding 2.)
- C-015, C-021 / 4E: attending preferred yields larger response than
  attending nonpreferred across the full contrast range; the difference is
  approximately a multiplicative scaling (response gain).
