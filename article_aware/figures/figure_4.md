# Figure 4 - Two-Stimulus Contrast-Response Modulation

## Role in the paper

Figure 4 shows that the normalization model can produce two different
attentional effects with the same two-stimulus MT setup and the same simulation
parameters. In Figure 4C, the preferred-direction stimulus contrast varies
while the nonpreferred stimulus contrast is fixed; attention to the
nonpreferred stimulus increases suppression and produces a contrast-gain-like
effect in which the attended-nonpreferred condition has lower responses than
the opposite-hemifield condition. In Figure 4E, the preferred and
nonpreferred stimulus contrasts covary, and directing attention to the
preferred stimulus produces a higher response than directing attention to the
nonpreferred stimulus, approximating response gain. The point is that the same
attention-normalization equations can explain both outcomes by changing which
stimulus is attended and how contrasts are swept (C-015, C-021).

---

## Verbatim caption

> "Attentional Modulation of Neuronal Contrast-Response Functions with Two Stimuli in the Receptive Field. (A) Stimulus and task used by Martinez-Trujillo and Treue (2002) while recording in MT. The contrast of the preferred direction stimulus (indicated by the upward arrow) within the receptive field was systematically varied across trials, whereas the contrast of the nonpreferred stimulus (indicated by the downward arrow) was held fixed. The monkey was cued to attend either the nonpreferred stimulus in the receptive field (dashed red circle) or the stimulus in the opposite hemifield (dashed blue circle). (B) Attention caused predominantly a change in contrast gain. Red curve and data points, responses as a function of contrast, when attention was directed to the nonpreferred stimulus in the receptive field. Blue curve and data points, responses to the identical stimuli, when attending the opposite hemifield. Dashed gray curve, percentage increase in firing rate at each contrast. (C) Model simulation exhibiting results similar to those observed experimentally. (D) Complementary experiment with two stimuli placed within the receptive field, one preferred and the other nonpreferred. The contrasts of the two stimuli covaried (always identical to one another). (E) Simulated neuronal responses were larger when attention was directed to the preferred-direction stimulus (green curve) than when it was directed to the nonpreferred stimulus (red curve). The effect of attention was approximated by a response gain change (multiplicative scaling). Simulation parameters were identical to those in (C) (Table 1)."

---

## Simulation parameters

| Parameter | Figure 4C model simulation | Figure 4E model simulation | Citation |
|-----------|----------------------------|----------------------------|----------|
| Recorded model neuron | RF center x = 0, preferred motion direction theta = 0 | RF center x = 0, preferred motion direction theta = 0 | C-015 |
| Stimulus configuration | Two colocated stimuli in the RF: preferred direction and nonpreferred direction | Two colocated stimuli in the RF: preferred direction and nonpreferred direction | C-015 |
| Preferred stimulus direction | theta = 0, matching the recorded neuron | theta = 0, matching the recorded neuron | C-015 |
| Nonpreferred stimulus direction | theta = 180 degrees, opposite the recorded neuron's preference | theta = 180 degrees, opposite the recorded neuron's preference | C-015 |
| Contrast sweep | Preferred contrast c_pref is log-spaced from 0.01 to 1 | Shared contrast c is log-spaced from 0.01 to 1 | C-015 |
| Fixed nonpreferred contrast | c_nonpref = 0.5 | Not fixed separately; c_nonpref = c_pref = c | C-015 |
| Attention conditions | Attend nonpreferred stimulus in RF vs attend opposite hemifield | Attend preferred stimulus in RF vs attend nonpreferred stimulus in RF | C-015 |
| Stimulus size | 5 | 5 | C-015 |
| Attention field size | 5 | 5 | C-015 |
| Stimulation field size | 5 | 5 | C-010 |
| Suppressive field size | 20 | 20 | C-010 |
| Motion-direction tuning width | 20 degrees | 20 degrees | C-015 |
| Suppressive direction tuning width | Doubled MT/MST convention over 360 degrees | Doubled MT/MST convention over 360 degrees | C-011 |
| Peak attention gain gamma | 5 | 5 | C-015 |
| Model equations | Stimulus drive, attention field, suppressive drive, output normalization | Stimulus drive, attention field, suppressive drive, output normalization | C-005, C-006, C-009 |

---

## Coordinate convention

- **Schematic panels A and D:** left/right positions are visual hemifields.
  The black dot is fixation. The solid circle marks the recorded neuron's
  receptive field. The stimulus with the upward arrow is the preferred-direction
  stimulus; the stimulus with the downward arrow is the nonpreferred-direction
  stimulus. Dashed circles mark possible attention fields.
- **Panel B:** empirical MT data adapted from Martinez-Trujillo and Treue
  (2002). The x-axis is log contrast for the preferred-direction stimulus. The
  left y-axis is firing response, and the right y-axis is percent attentional
  modulation (C-015).
- **Panel C:** model output for the Figure 4C protocol. The x-axis is log
  contrast of the preferred stimulus, c_pref, increasing left to right while
  the nonpreferred contrast is fixed at 0.5. The left y-axis is normalized
  model response of the recorded preferred-direction neuron. The right y-axis
  is percent attentional modulation (C-015).
- **Panel E:** model output for the Figure 4E protocol. The x-axis is log
  contrast c, increasing left to right, with c_pref = c_nonpref = c. The left
  y-axis is normalized model response. The paper-style panel overlays percent
  attentional modulation on a right axis, while the protocol declares the
  generated auxiliary output as a ratio, attend_pref / attend_nonpref (C-015).
- **Curve encoding in Panel C:** the condition attending the nonpreferred
  stimulus in the RF is the lower solid response curve; the opposite-hemifield
  attention condition is the higher solid response curve. The dashed curve is
  percent attentional modulation (C-015, C-021).
- **Curve encoding in Panel E:** the condition attending the preferred stimulus
  is the higher solid response curve; the condition attending the nonpreferred
  stimulus is the lower solid response curve. The dashed curve is percent
  attentional modulation (C-015, C-021).
- **"Rightward shift"** means the attended-nonpreferred response in Panel C
  reaches its steep rising portion or half-maximum at a higher preferred
  contrast than the opposite-hemifield condition. This is the contrast-gain-like
  signature for Figure 4C (C-015, C-019, C-021).
- **"Response-gain-like"** means the two solid curves in Panel E rise over
  similar contrast ranges, but the attend-preferred curve is vertically higher
  and saturates above the attend-nonpreferred curve (C-015, C-019, C-021).

---

## Pipeline and expected behavior

### Panel A - Martinez-Trujillo and Treue 2002 task schematic

Panel A is an experimental task schematic, not a model response surface or
contrast-response output. It shows two stimuli in the recorded neuron's
receptive field: an upward-arrow preferred-direction stimulus and a
downward-arrow nonpreferred-direction stimulus. The preferred-direction
stimulus contrast is varied across trials, while the nonpreferred stimulus
contrast is fixed. The dashed attention fields indicate the two attention
conditions used for the empirical comparison: attention to the nonpreferred
stimulus in the RF or attention to the opposite hemifield (C-015).

### Panel B - Empirical contrast-gain-like data

Panel B is empirical reference data and is not generated by the model
protocol. It provides the qualitative target for Panel C: attending to the
nonpreferred stimulus in the RF produces responses consistent with a
predominant contrast-gain change relative to attending the opposite hemifield
(C-015). In the model interpretation, this pattern is expected because the
preferred direction contributes strongly to the recorded neuron's stimulus
drive, whereas both preferred and nonpreferred stimuli contribute to the
suppressive drive (C-021).

### Panel C - Model simulation for preferred-contrast sweep with fixed nonpreferred contrast

Panel C is generated by the Figure 4C protocol. For each preferred contrast
c_pref, the model builds stimulus drive E from two colocated stimuli: a
preferred-direction component with contrast c_pref and a nonpreferred-direction
component with fixed contrast c_nonpref = 0.5 (EQ-stim, C-009, C-015). For the
attend-nonpreferred condition, the attention field is centered at the RF
location and feature-selective for theta = 180 degrees; for the opposite-
hemifield condition, the attention field is effectively flat over the recorded
neuron's RF (EQ-attention, C-005, C-015). The suppressive drive S is computed
from the attention-modulated stimulus drive, and the recorded neuron's response
R is the attention-modulated drive divided by S plus sigma (EQ-6, EQ-5,
C-005, C-006).

Because the recorded neuron is preferred for theta = 0, attending the
nonpreferred stimulus boosts a stimulus component that contributes little to
the recorded neuron's numerator but contributes to the suppressive denominator.
This shifts the excitation-suppression balance toward the nonpreferred
stimulus, increasing suppression of the recorded neuron and lowering its
response relative to the opposite-hemifield condition (C-021). The resulting
solid model curve for attend-nonpreferred is lower and right-shifted relative
to the opposite-hemifield curve, so a larger preferred contrast is required to
reach comparable normalized responses (C-015, C-019, C-021). The dashed
percent-modulation curve is largest in absolute effect around low-to-
intermediate preferred contrasts and becomes smaller as both response curves
saturate at high contrast (C-019, C-020).

### Panel D - Complementary two-stimulus covarying-contrast schematic

Panel D is a schematic for the complementary Figure 4E condition. The two
stimuli remain colocated in the recorded neuron's RF, one moving in the
preferred direction and one in the nonpreferred direction. Unlike Panel A, the
preferred and nonpreferred stimulus contrasts covary and are always identical
to one another. This panel defines the contrast manipulation for Panel E, but
the model protocol's declared outputs are the contrast-response curves and
their ratio, not a separate schematic output (C-015).

### Panel E - Model simulation for covarying preferred and nonpreferred contrasts

Panel E is generated by the Figure 4E protocol. For each contrast c, the model
builds E from two colocated stimuli with c_pref = c_nonpref = c, one at theta =
0 and one at theta = 180 degrees (EQ-stim, C-009, C-015). The two attention
conditions both target the RF location, but one attention field is
feature-selective for the preferred direction and the other is feature-
selective for the nonpreferred direction (EQ-attention, C-005, C-015). The
model then computes S from A times E and computes the recorded neuron's output
R by divisive normalization (EQ-6, EQ-5, C-005, C-006).

Attending the preferred stimulus multiplies the component that contributes
directly to the recorded neuron's numerator, while attending the nonpreferred
stimulus gives more weight to a component that contributes mainly through the
suppressive denominator (C-021). Therefore, the attend-preferred curve is above
the attend-nonpreferred curve across the contrast range (C-015, C-021). Because
both stimulus contrasts covary, the separation is approximately multiplicative:
the attend-preferred curve is vertically scaled upward rather than being mainly
left-shifted, and it saturates at a higher normalized response than the
attend-nonpreferred curve (C-015, C-019, C-021). As a visual observation from
the printed Figure 4E model panel, the dashed modulation curve decreases from
left to right rather than peaking at high contrast; this should be checked with
some tolerance because the dashed curve is small and the right-axis labels are
sparse (C-015).

---

## Key inter-panel relationships

1. **Same parameters, different contrast manipulation:** Panels C and E use the
   same stimulus size, attention field size, tuning width, and peak attention
   gain; the qualitative change comes from varying only the preferred contrast
   in C versus covarying preferred and nonpreferred contrasts in E (C-015).

2. **Same equations, different attended feature:** Both model panels use the
   same attention-normalization equations. In C, attention to the nonpreferred
   stimulus increases the suppressive influence relative to the recorded
   neuron's numerator; in E, attention to the preferred stimulus boosts the
   numerator more directly than attention to the nonpreferred stimulus (EQ-5,
   EQ-6, C-005, C-006, C-021).

3. **Panel C is contrast-gain-like and suppressive:** The attend-nonpreferred
   curve in Panel C is lower and right-shifted relative to the opposite-
   hemifield curve. This follows from boosting the fixed nonpreferred stimulus,
   which contributes to suppression of the preferred neuron (C-015, C-019,
   C-021).

4. **Panel E is response-gain-like and facilitatory for preferred attention:**
   The attend-preferred curve in Panel E is above the attend-nonpreferred curve
   across the contrast range and saturates higher, matching the response-gain
   qualitative regime (C-015, C-019, C-021).

5. **The sign of the attended condition differs across model panels:** In
   Panel C, the attention condition drawn as "attend nonpreferred in RF" should
   be below the opposite-hemifield condition; in Panel E, the attention
   condition drawn as "attend preferred in RF" should be above the attend-
   nonpreferred condition (C-015, C-021).

6. **Both model panels saturate at high contrast:** The solid model curves in C
   and E level off as contrast approaches 1 because divisive normalization
   saturates high-contrast responses (C-020).

7. **Panel C should have the stronger horizontal shift:** Panel C's diagnostic
   feature is a rightward shift of the attend-nonpreferred curve relative to
   the opposite-hemifield curve, whereas Panel E's diagnostic feature is a
   vertical separation between attend-preferred and attend-nonpreferred curves
   over a similar contrast range (C-015, C-019).

8. **Empirical panels are context, not direct model outputs:** Panels A, B, and
   D explain the experimental/task conditions motivating the simulations, but
   the Figure 4 protocol declares generated model outputs for the curve arrays
   in C and E (C-015).
