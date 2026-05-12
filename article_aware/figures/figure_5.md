# Figure 5 - Spatial Attention and Multiplicative Scaling of Tuning Curves

## Role in the paper

Figure 5 shows that the normalization model can reproduce the McAdams and Maunsell
(1999) spatial-attention result: when attention is directed to a stimulus inside the
recorded neuron's receptive field and the attention field is broad over orientation, the
orientation tuning curve is scaled upward without a visible change in shape. Panels A and
B provide task and empirical context, while panel C is the generated model simulation
target for this protocol (C-016, C-022).

---

## Verbatim caption

> "Spatial Attention Causes a Multiplicative Scaling of Tuning Curves. (A) Stimulus and task. On some trials, monkeys attended to the grating in the receptive field of the neuron being recorded (dashed red circle) to report whether two successive gratings were identical or differed in orientation by 90°. On other trials, attention was instead directed to a colored blob appearing in the opposite hemifield (dashed blue circle) to report whether successive stimuli differed in color. (B) Orientation tuning curves averaged across a population of V4 neurons, with and without attention (adapted from McAdams and Maunsell, 1999). These curves were obtained by fitting each neuron's tuning curve with a Gaussian, shifting the neuron's preferred orientation to align all tuning curves and then averaging the Gaussian fits. Red indicates orientation tuning when attention was directed to stimuli in the receptive field, to perform the orientation discrimination task. Blue, orientation tuning when attention was directed away from the receptive field to perform the color discrimination task. (C) Model simulation yielded similar results; multiplicative scaling of the tuning curve when spatial attention was directed to a stimulus in the receptive field."

---

## Simulation parameters

| Parameter | Figure 5C model value | Citation |
|-----------|------------------------|----------|
| Generated model panel | Panel C only | C-016 |
| Stimulus configuration | Single grating at the recorded neuron's receptive-field location | C-016 |
| Recorded neuron | x = 0, preferred orientation theta = 0 degrees | C-016 |
| Orientation sweep | Stimulus orientation varied across trials around the preferred orientation | C-016, C-022 |
| Stimulus contrast | Fixed mid-range contrast c = 0.5 in the repository protocol | figure_5_protocol.md |
| Stimulus size (Gaussian spatial size) | 10 | C-016 |
| Attention field size (Gaussian spatial size) | 10 | C-016 |
| Stimulation field size | 5 | C-010 |
| Suppressive field size | 20 | C-010 |
| V4 orientation tuning width | 30 degrees | C-011 |
| Suppressive orientation tuning width | 180 degrees | C-011 |
| Peak attention gain (gamma) | 2 | C-016 |
| Attention field feature profile | Flat over orientation for spatial attention | C-016, C-022 |
| Attended condition | Attention centered on the RF grating, with peak gain gamma | C-016, C-022 |
| Unattended condition | Attention directed to the opposite hemifield, so gain over the RF is effectively 1 | C-016, C-022 |

The fixed contrast value and the exact orientation sweep grid are implementation-contract
details in `pseudocode/figure_5_protocol.md`; they are not numeric values stated in the
paper text.

---

## Coordinate convention

- **Panel A:** left/right positions are visual hemifields. The black dot is fixation. The
  solid circle marks the recorded neuron's receptive field around the right grating.
  Dashed circles mark the possible attention fields: one around the RF grating and one
  around the opposite-hemifield colored blob.
- **Panel B:** empirical population orientation tuning. The x-axis is orientation
  relative to each neuron's aligned preferred orientation. The y-axis is normalized
  response. This panel is context, not generated model output.
- **Panel C:** model orientation tuning. The x-axis is stimulus orientation relative to
  the model neuron's preferred orientation, with 0 degrees at the center. The y-axis is
  normalized response. The attended curve is the higher curve; the unattended or
  opposite-hemifield-attention curve is the lower curve.
- **Ratio output:** the implementation protocol also records attended_tuning divided by
  unattended_tuning at each orientation. The paper panel does not draw this ratio, but a
  correct model should make it approximately constant across orientations where the
  response is not near zero (C-022).

---

## Pipeline and expected behavior

### Panel A - Spatial-attention task schematic

Panel A is a task schematic, not a model response panel. It shows the two attention
conditions used to motivate the Figure 5C simulation: attention can be directed to the
grating in the recorded neuron's receptive field for an orientation task, or away from
the receptive field to a colored blob in the opposite hemifield for a color task. The
simulation abstracts this into two attention-field conditions: an RF-centered spatial
attention field and an opposite-hemifield attention condition that leaves gain near 1
over the recorded RF (C-016, C-022).

### Panel B - Empirical population orientation tuning

Panel B is empirical reference data adapted from McAdams and Maunsell (1999), not a
generated model output. The plotted empirical curves were made by Gaussian-fitting each
V4 neuron's tuning curve, aligning preferred orientations, and averaging the fits. The
qualitative target supplied by this panel is that attention increases response while
preserving tuning-curve shape: the attended curve is a scaled-up version of the
unattended curve rather than a shifted or narrowed curve (C-016, C-022).

### Panel C - Model simulation of multiplicative scaling

Panel C is generated by the standard attention-normalization pipeline. For each stimulus
orientation in the sweep, the model constructs stimulus drive E for one grating at x = 0
using the V4 orientation tuning width, constructs the attention field A, computes
suppressive drive S from the product A times E, computes output R from A times E divided
by S plus sigma, and reads out R at the recorded neuron's coordinates x = 0 and theta =
0 degrees (EQ-stim, EQ-attention, EQ-6, EQ-5, C-005, C-006, C-011, C-016).

In the attended condition, A is spatially centered on the RF stimulus and is broad or flat
over orientation. Because it does not preferentially enhance one stimulus orientation
over another, it scales the stimulus drive across the orientation sweep without imposing a
new orientation-selective profile. In the unattended condition, attention is directed away
from the RF and A is effectively 1 over the recorded neuron's RF. The expected result is
therefore a higher attended tuning curve with the same preferred orientation and the same
width as the unattended curve (EQ-attention, EQ-5, EQ-6, C-016, C-022).

The protocol's named outputs are `theta_0_grid`, `attended_tuning`,
`unattended_tuning`, and `ratio`. The key computational signature is that
`attended_tuning` is greater than or equal to `unattended_tuning` across the orientation
sweep, while `ratio` is approximately constant wherever the denominator is not near zero.
This is the model's multiplicative-scaling claim for spatial attention with an
orientation-broad attention field (C-016, C-022).

---

## Key inter-panel relationships

1. **Empirical-to-model qualitative match:** Panel C should reproduce the qualitative
   structure of panel B: attention increases response amplitude while preserving tuning
   shape. Detailed empirical data geometry from panel B is not part of the generated
   model target (C-016, C-022).

2. **Spatial attention differs from feature-based sharpening:** Figure 5C should show
   multiplicative scaling, not tuning sharpening. A generated model curve that becomes
   narrower under attention would contradict the spatial-attention claim for an
   orientation-broad attention field (C-022, C-023).

3. **Same preferred orientation:** Both attended and unattended model curves should peak
   at the recorded neuron's preferred orientation. The attention field changes gain but
   does not introduce orientation selectivity in this protocol (EQ-attention, C-016,
   C-022).

4. **Same apparent tuning width:** The attended curve should preserve the unattended
   curve's width because spatial attention is flat over orientation. The model should not
   produce a left/right shift, a narrower peak, or a broader peak in panel C
   (EQ-attention, C-016, C-022).

5. **Ratio is the hidden diagnostic:** Even if the plotted panel only shows two tuning
   curves, the protocol output `ratio = attended_tuning / unattended_tuning` should be
   approximately flat across orientations where both responses are appreciably above
   zero. This follows from the multiplicative-scaling interpretation of the Figure 5C
   model output (C-016, C-022).

6. **Attention condition controls only gain at the RF:** The difference between panel C's
   two curves is caused by whether the RF stimulus lies under the attention field. The
   stimulus, recorded-neuron coordinates, contrast, and orientation sweep are otherwise
   unchanged between attended and unattended conditions (EQ-stim, EQ-attention, C-016).
