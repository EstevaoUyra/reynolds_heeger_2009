# Figure 3 - Empirical Contrast-Response Patterns and Model Fits

## Role in the paper

Figure 3 shows that the normalization model can reproduce two empirical V4 attention
patterns that are not clean instances of either limiting case from Figure 2. The top row
reproduces the Reynolds et al. (2000) pattern: percent modulation is largest at lower
contrasts and the model fit behaves like a mixed effect with a visible leftward component.
The bottom row reproduces the Williford and Maunsell (2006) pattern: percent modulation is
largest at low contrast, but the largest absolute attended-minus-unattended response
difference occurs at high contrast. The figure's point is that changing stimulus size and
attention-field size, with the baseline handling specified for Figure 3, lets the same
normalization equations generate both qualitative patterns (C-014, C-019).

---

## Verbatim caption

> "Attentional Modulation of Neuronal Contrast-Response Functions. (A) Stimulus and task used by Reynolds et al. (2000) while recording neural activity in V4. Sequences of gratings were presented to the left and right visual fields, one of which was positioned within the receptive field of the recorded neuron. Monkeys were cued to attend either to the stimulus sequence in the receptive field (dashed red circle) or the stimulus sequence in the opposite hemifield (dashed blue circle), to detect a target that appeared in the sequence. (B) Attention caused the largest percentage increase in firing rates at low contrast (adapted from Reynolds et al., 2000). Red curve and data points, responses as a function of contrast, when attention was directed to stimuli in the receptive field. Blue curve and data points, responses to the identical stimuli when unattended. Dashed gray curve, percentage increase in firing rate at each contrast. (C) Normalization model of attention can exhibit similar results. Stimuli, receptive fields, and attention fields are not drawn to scale; Simulation parameters are listed in Table 1. (D) Stimulus and task used in a similar experiment by Williford and Maunsell (2006), also while recording in V4. (E) Attention caused neither a pure contrast gain change nor a pure response gain change (adapted from Williford and Maunsell, 2006). Rather, the greatest percentage increase in firing rates was at low contrasts (dashed gray curve), but with the largest absolute increase in firing rates at high contrasts (compare red and blue curves). (F) Normalization model of attention can exhibit similar results. The simulation was identical to that in (C) except (1) the stimulus was larger and attention field was smaller and (2) additional baseline activity was added for (C) (see Table 1)."

---

## Simulation parameters

| Parameter | Panel C: Reynolds 2000 model | Panel F: Williford & Maunsell 2006 model | Citation |
|-----------|------------------------------|-------------------------------------------|----------|
| Stimulus configuration | Single preferred grating at recorded RF center | Single preferred grating at recorded RF center | C-014 |
| Recorded neuron | x = 0, theta = 0 | x = 0, theta = 0 | C-014 |
| Contrast sweep | Log-spaced contrasts from 0.01 to 1 | Log-spaced contrasts from 0.01 to 1 | C-014 |
| Stimulus size (Gaussian spatial size) | 5 | 7 | C-014 |
| Attention field size (Gaussian spatial size) | 30 | 7 | C-014 |
| Stimulation field size | 5 | 5 | C-010 |
| Suppressive field size | 20 | 20 | C-010 |
| V4 orientation tuning width | 30 degrees | 30 degrees | C-011 |
| Suppressive orientation tuning width | 180 degrees | 180 degrees | C-011 |
| Peak attention gain (gamma) | 2 | 2 | C-014 |
| Baseline added to stimulus drive before attention/normalization | 0.05 (assumed value) | 0.05 (assumed value) | A-007 |
| Baseline added after normalization | 0.05 (assumed value) | 0.05 (assumed value) | A-007 |

The caption and Table 1 identify baseline activity for Figure 3 but do not provide numeric
baseline values. The repo contract therefore uses A-007: both a small attention-modulated
baseline in the stimulus drive and a small unmodulated output baseline are set to 0.05
for the Figure 3 model protocols.

---

## Coordinate convention

- **Schematic panels A and D:** left/right positions are visual hemifields. The black dot
  is fixation. The recorded neuron's receptive field is drawn around the right stimulus.
  Dashed circles mark possible attention fields when attention is directed to the right
  RF stimulus or to the opposite-hemifield stimulus.
- **Empirical panels B and E:** x-axis is contrast from low/0% at left to high contrast
  at right. Left y-axis is firing rate in Hz. Right y-axis is percent attentional
  modulation from 0% to 100%.
- **Model panels C and F:** x-axis is log contrast from low at left to high at right.
  Left y-axis is normalized model response from 0 to 1. Right y-axis is percent
  attentional modulation from 0% to 100%.
- **Curve encoding:** attended/RF condition is the solid dark curve; unattended or
  contralateral-attention condition is the solid lighter curve; percent modulation is
  the dashed curve.
- **Absolute difference:** attended response minus unattended response at the same
  contrast.

---

## Pipeline and expected behavior

### Panel A - Reynolds et al. 2000 task schematic

Panel A is a task schematic, not a simulated response. It shows two small vertical grating
sequences, one in each hemifield, with the recorded neuron's receptive field around the
right-side grating. The dashed attention circles indicate the two attention conditions:
attend the RF stimulus or attend the opposite-hemifield stimulus. The small stimulus
relative to the broad attention field is the visual setup corresponding to the Figure 3C
simulation parameters: stimulus size 5 and attention field size 30 (C-014).

### Panel B - Reynolds et al. 2000 empirical contrast-response data

Panel B is the empirical target pattern for Panel C. The attended response is higher than
the unattended response across the sampled contrasts, and the dashed percent-modulation
curve is largest at low contrast and declines toward high contrast (C-014). Because the
curves are firing-rate data rather than model outputs, they are not generated by the
implementation pipeline, but they define the qualitative pattern that Figure 3C should
match.

### Panel C - Model fit for the Reynolds et al. 2000 pattern

Panel C is generated by the standard attention-normalization pipeline with Figure 3C
parameters. The model first builds the stimulus drive E for a single preferred stimulus
(EQ-stim), adds the assumed attention-modulated baseline to E (A-007), constructs the
attention field A centered on the RF stimulus for the attended condition or effectively
flat over the RF for the unattended condition (EQ-attention), computes suppressive drive
from A times E (EQ-6), computes output R from A times E divided by S plus sigma (EQ-5),
and then adds the unmodulated baseline (A-007).

The broad attention field in 3C (size 30) covers the stimulus footprint more uniformly
than the stimulus itself (size 5), so attention behaves partly like the contrast-gain
limiting case: it moves the attended contrast-response curve leftward on the log-contrast
axis (EQ-7, C-007, C-014). The additional baseline makes the lowest-contrast responses
positive and supports strong percentage modulation at low contrast (A-007, C-014). At high
contrast both solid model curves saturate and nearly converge, so the dashed percent-
modulation curve drops toward zero (C-020).

### Panel D - Williford and Maunsell 2006 task schematic

Panel D is the schematic counterpart to Panel A for the Williford and Maunsell experiment.
It shows larger grating patches, again with the recorded neuron's receptive field around
the right-side stimulus and dashed attention fields for the two attention conditions. The
stimulus is larger and the attention field is smaller than in Panel A, matching the Figure
3F parameter change: stimulus size 7 and attention field size 7 instead of stimulus size 5
and attention field size 30 (C-014).

### Panel E - Williford and Maunsell 2006 empirical contrast-response data

Panel E is the empirical target pattern for Panel F. It is explicitly described as neither
a pure contrast-gain change nor a pure response-gain change: the dashed percent-modulation
curve is largest at low contrasts, while the largest absolute separation between attended
and unattended firing-rate curves appears at high contrasts (C-014). This combination is
the central qualitative constraint for the Figure 3F model output.

### Panel F - Model fit for the Williford and Maunsell 2006 pattern

Panel F uses the same ordered pipeline as Panel C: build E (EQ-stim), add the assumed
modulated baseline (A-007), build A (EQ-attention), compute suppressive drive from A times
E (EQ-6), compute R from the normalized attention-modulated drive (EQ-5), and add the
unmodulated output baseline (A-007). The critical parameter difference is that the stimulus
and attention field are both size 7 (C-014). Because the attention field no longer dwarfs
the stimulus, attention does not simply rescale effective contrast. Instead, the attended
curve is elevated and remains separated from the unattended curve at high contrast, giving
the largest absolute response difference on the right side of the plot (EQ-8, C-008,
C-014, C-019). The baseline keeps percent modulation high at low contrast, so the dashed
curve can peak at low contrast even though the largest absolute response difference occurs
at high contrast (A-007, C-014).

---

## Key inter-panel relationships

1. **Same model, different size ratio:** Panels C and F use the same normalization
   equations and peak attention gain, but Panel F has a larger stimulus and smaller
   attention field than Panel C. This size-ratio change is the main model reason the
   high-contrast separation is larger in F than in C (EQ-5, EQ-6, C-014, C-019).

2. **Percent modulation peaks low in both empirical targets:** Panels B and E both show
   the dashed percent-modulation curve largest at low or low-to-intermediate contrast.
   The model panels C and F should preserve that qualitative low-contrast modulation
   pattern (C-014).

3. **Absolute difference separates the two regimes:** In Panel C, the attended and
   unattended model curves nearly converge at high contrast. In Panel F, they remain
   separated at high contrast, so the largest absolute difference is high-contrast rather
   than low-contrast (C-014, C-019, C-020).

4. **Panel C retains contrast-gain structure:** The attended curve in C is left-shifted:
   its inflection point is at lower contrast than the unattended curve. This follows from
   the large attention field approximating uniform gain over the stimulus footprint
   (EQ-7, C-007, C-014).

5. **Panel F is mixed, not pure response gain:** Panel F has a sustained high-contrast
   vertical separation like response gain, but its percent-modulation curve still peaks at
   low contrast because of the Figure 3 baseline handling. A correct implementation should
   not make the dashed curve peak at high contrast just because the absolute difference
   peaks there (A-007, C-014, C-019).

6. **Baseline makes zero/low contrast responses positive:** The Figure 3 protocols include
   an attention-modulated baseline before normalization and an unmodulated baseline after
   normalization. Therefore, both attended and unattended CRFs begin above zero at the
   lowest contrast in C and F (A-007, C-014).

7. **Both model panels saturate:** In C and F, the solid model curves should level off as
   contrast approaches 1 because divisive normalization saturates at high contrast
   (C-020).

8. **Schematic panels encode parameter changes:** Panel D must show larger stimuli and
   smaller relative attention fields than Panel A. That visual change is not decorative;
   it corresponds directly to the Figure 3C versus Figure 3F simulation parameter change
   in stimulus size and attention-field size (C-014).
