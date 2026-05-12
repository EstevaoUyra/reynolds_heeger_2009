# Figure 7 - Two Stimuli in the RF with Combined Spatial and Feature Attention

## Role in the paper

Figure 7 shows how the normalization model accounts for attention-dependent shifts in
motion-direction tuning when two stimuli occupy the same receptive field. One stimulus is
fixed in the recorded neuron's nonpreferred direction, while the other stimulus varies in
motion direction. The non-trivial result is that changing only the attention field changes
the apparent tuning: attending the variable stimulus raises responses near the preferred
direction, whereas attending the fixed nonpreferred stimulus lowers them. Panel C is the
model simulation target; Panels A and B provide task and empirical context (C-018, C-021).

---

## Verbatim caption

> "Attentional Modulation of Tuning when Two Stimuli Are Present within the Receptive Field. (A) Stimulus and task. A pair of stimuli was presented simultaneously while recording responses of a neuron in visual cortical area MT. Both stimuli were presented within the recorded neuron's receptive field. One stimulus moved in the nonpreferred direction (indicated as downward), and the other varied in motion direction. Attention was directed either to the fixation point (dashed yellow circle) or to one of the two stimuli in the receptive field (dashed red and blue circles) to detect a change in speed or direction. (B) Responses were larger when attending the variable direction stimulus (particularly when it moved in the preferred direction) and smaller when attending the nonpreferred stimulus (adapted from Treue and Martinez-Trujillo, 1999). Yellow, tuning (response as a function of the motion direction of the variable stimulus) when attention was directed to fixation. Blue, tuning when attention was directed to the nonpreferred stimulus. Red, tuning when attention was directed to the stimulus with variable motion direction. (C) Responses of a model neuron. Yellow, simulated responses when the attention field was flat (equal) for all motion directions, and spatial attention was directed to the fixation point (i.e., away from the model neuron's receptive field). Blue, simulated responses when the attention field was selective for the spatial location corresponding to the receptive field of the model neuron, and selective for the direction of motion opposite to that preferred by the model neuron. Feature-based attention was thus restricted to a nonpreferred direction of motion. Red, simulated responses when the attention field matched that of the variable stimulus, i.e., with a spatial selectivity corresponding to the receptive field and with a direction selectivity that varied with the stimulus motion direction."

---

## Simulation parameters

| Parameter | Figure 7C value | Citation |
|-----------|-----------------|----------|
| Recorded area / stimulus class | MT motion-direction simulation | C-011, C-018 |
| Recorded model neuron | RF center x = 0, preferred direction theta = 0 | C-018 |
| Stimulus configuration | Two stimuli in the RF: one fixed nonpreferred stimulus and one variable-direction stimulus | C-018 |
| Fixed nonpreferred stimulus direction | theta_np = 180 degrees, opposite the recorded neuron's preferred direction | C-018 |
| Variable stimulus direction | swept over motion direction; protocol uses approximately -180 to +180 degrees | C-018; protocol-specified grid |
| Stimulus contrasts | 0.5 for both the fixed nonpreferred and variable stimuli | protocol-specified value; two-stimulus setup in C-018 |
| Stimulus size | 5 | C-018 |
| Attention field size | 5 | C-018 |
| Stimulation field size | 5 | C-010 |
| Suppressive field size | 20 | C-010 |
| Direction tuning width for feature-selective attention | 45 degrees | C-018 |
| Suppressive field tuning width | doubled for MT/MST motion-direction simulations | C-011 |
| Peak attention gain gamma | 5 | C-018 |
| Attention conditions | fixation/flat direction field away from RF; attend nonpreferred in RF; attend variable stimulus in RF | C-018 |
| Model outputs | `fixation_tuning`, `attend_nonpref_tuning`, `attend_variable_tuning` | C-018 |

The exact numeric sweep grid for theta_var and the contrast value 0.5 are part of the
article-aware implementation protocol rather than values printed directly on the paper
figure. The protocol uses approximately 15-degree steps from -180 degrees to +180 degrees.

---

## Coordinate convention

- **Spatial coordinate:** both stimuli are at the recorded RF center, x = 0. The fixation
  attention condition is spatially away from the RF, so attention gain is approximately
  flat/baseline at the recorded RF location (C-018).
- **Feature coordinate:** theta = 0 is the recorded neuron's preferred motion direction,
  shown by the central upward arrow under panels B and C. Theta = +/-180 degrees is the
  nonpreferred/downward direction, shown by downward arrows at the left and right ends
  of the direction axis (C-018).
- **Panel C x-axis:** motion direction of the variable stimulus, not contrast.
- **Panel C y-axis:** normalized response of the recorded model neuron, read out at
  x = 0 and theta = 0 after normalization (EQ-5, EQ-6, C-005, C-006).
- **Curve encoding in Panel C:** yellow/fixation is the flat-direction attention condition
  away from the RF; blue/nonpreferred is spatial attention at the RF plus feature
  selectivity for the nonpreferred direction; red/variable is spatial attention at the
  RF plus feature selectivity matched to the current variable stimulus direction (C-018).

---

## Pipeline and expected behavior

### Panel A - Stimulus and task schematic

Panel A is a schematic of the experimental task, not a generated model response. It shows
the two-stimulus RF configuration that the model protocol abstracts: both stimuli are
inside the recorded neuron's receptive field, one moves in the nonpreferred direction,
and the other stimulus changes direction across trials. The dashed circles encode the
three possible attention targets: fixation, the nonpreferred RF stimulus, or the variable
RF stimulus (C-018). The schematic matters for the model because it determines whether
the attention field is away from the RF and flat over direction, centered on the RF and
feature-selective for the nonpreferred direction, or centered on the RF and feature-
selective for the variable stimulus direction (C-018, C-005).

### Panel B - Empirical tuning reference

Panel B is the empirical pattern adapted from Treue and Martinez-Trujillo (1999). It is
not generated by the implementation protocol, but it provides the qualitative target for
Panel C: responses are largest when attention is directed to the variable stimulus,
especially when that variable stimulus moves in the preferred direction, and smallest
when attention is directed to the fixed nonpreferred stimulus (C-018). The empirical
panel should be treated as context rather than a pointwise reproduction target for model
simulation output.

### Panel C - Model responses

Panel C is generated by the full attention-normalization pipeline. For each value of the
variable stimulus direction, the model builds stimulus drive E by summing two stimulus
components at x = 0: the fixed nonpreferred stimulus and the variable-direction stimulus
(EQ-stim, C-009, C-018). It then constructs an attention field A according to the current
attention condition: flat over direction and away from the RF for fixation, selective for
the nonpreferred direction at the RF for attend-nonpreferred, or selective for the current
variable direction at the RF for attend-variable (C-018, C-005). Suppressive drive S is
computed by convolving A times E with the normalized suppressive field (EQ-6, C-006).
The output response R is then A times E divided by S plus sigma, with readout at the
recorded neuron's coordinates x = 0 and theta = 0 (EQ-5, C-005).

The central peak occurs when the variable stimulus is near the recorded neuron's
preferred direction. At that point, attending the variable stimulus multiplies the
preferred-direction stimulus drive, increasing the numerator of the recorded neuron's
response and shifting the balance toward the preferred stimulus (C-018, C-021). By
contrast, attending the fixed nonpreferred stimulus increases gain for the nonpreferred
component. That component contributes strongly to suppressive drive but weakly to the
recorded neuron's preferred-direction excitatory drive, so the recorded output decreases
relative to the fixation baseline (C-021, C-006). The fixation condition lies between
the two because its attention field is effectively away from the RF and flat over motion
direction at the recorded neuron's location (C-018).

Across the direction sweep, all three model curves should have low responses near the
nonpreferred/downward endpoints and a central peak near the preferred/upward direction.
The important model-generated relationship is the vertical ordering around the central
preferred direction: attend variable above fixation, fixation above attend nonpreferred
(C-018, C-021). Exact absolute response values are not specified by the figure caption;
the article-aware contract therefore emphasizes qualitative curve ordering and shape.

---

## Key inter-panel relationships

1. **Panel C reproduces the Panel B qualitative ordering, not its empirical data points.**
   The model output should show larger responses for attend-variable and smaller responses
   for attend-nonpreferred near the preferred direction, matching the empirical pattern
   described in the caption (C-018).

2. **The three Panel C curves differ only by the attention field.** The two stimuli,
   their contrasts, stimulus size, and recorded neuron readout are fixed across attention
   conditions; the attention field determines whether gain is flat/away, nonpreferred-
   selective, or matched to the variable stimulus (C-018, C-005).

3. **Attend-variable raises the preferred-direction peak.** When theta_var is near the
   recorded neuron's preferred direction, attention matched to the variable stimulus
   amplifies the preferred component of E before normalization, so the recorded response
   is higher than fixation (EQ-5, EQ-6, C-018, C-021).

4. **Attend-nonpreferred lowers the preferred-direction peak.** When attention is
   directed to the fixed nonpreferred stimulus, gain favors a component that adds
   suppression without adding much preferred-direction excitation to the recorded neuron,
   so the recorded response is lower than fixation near the preferred direction (EQ-5,
   EQ-6, C-018, C-021).

5. **The x-axis is feature tuning, not contrast response.** Unlike Figures 2-4, Figure 7C
   sweeps variable-stimulus motion direction while keeping the two stimulus contrasts
   fixed, so the expected output is a set of direction tuning curves rather than
   contrast-response functions (C-018).

6. **Both stimuli share the same RF location.** Spatial attention to either RF stimulus
   is centered at x = 0; the difference between attend-nonpreferred and attend-variable
   is feature selectivity in direction, not spatial location (C-018).
