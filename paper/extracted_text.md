# The Normalization Model of Attention

**Authors:** John H. Reynolds (Salk Institute) and David J. Heeger (NYU)
**Citation:** Neuron, 2009 Jan 29; 61(2):168–185. doi: 10.1016/j.neuron.2009.01.002
**PMCID:** PMC2752446 | **PMID:** 19186161
**Source:** https://pmc.ncbi.nlm.nih.gov/articles/PMC2752446/

---

## Abstract

"Attention has been found to have a wide variety of effects on the responses of neurons in visual cortex. We describe a model of attention that exhibits each of these different forms of attentional modulation, depending on the stimulus conditions and the spread (or selectivity) of the attention field in the model. The model helps reconcile proposals that have been taken to represent alternative theories of attention. We argue that the variety and complexity of the results reported in the literature emerge from the variety of empirical protocols that were used, such that the results observed in any one experiment depended on the stimulus conditions and the subject's attentional strategy, a notion that we define precisely in terms of the attention field in the model, but that has not typically been completely under experimental control."

---

## Section Headings

1. Introduction
2. The Normalization Model of Attention
   - Stimulation Fields and Stimulus Drive
   - Suppressive Fields and Normalization
   - Attention Fields and Attentional Gain
   - A Unified Account of Attentional Modulation of the Contrast-Response Function
   - Attentional Modulation of the Contrast-Response Function with Two Stimuli in the Receptive Field
   - Spatial Attention and Multiplicative Scaling of Neuronal Tuning Curves
   - Feature-Based Attention and Nonmultiplicative Scaling of Neuronal Tuning
   - Attentional Modulation of Tuning Curves with Two Stimuli in the Receptive Field
3. Discussion (Relation to Other Models, Predictions, Computational Benefits, Limitations, Descriptive/Computational/Mechanistic Models)

---

## Equations

### Equation 1 — Output firing rate (no attention)

R(x, θ) = ⌊E(x, θ) / [S(x, θ) + σ]⌋_T

- R(x, θ): firing rate of neuron with receptive field center x and orientation preference θ
- E(x, θ): stimulus drive
- S(x, θ): suppressive drive
- σ: constant determining contrast gain (nonnegative)
- ⌊·⌋_T: rectification with respect to threshold T

### Equation 2 — Suppressive drive

S(x, θ) = s(x, θ) ∗ E(x, θ)

- s(x, θ): suppressive field (extent of pooling over space and orientation)
- ∗: convolution
- ∫ s(x, θ) dx dθ = 1 (suppressive field normalized to integrate to 1)

### Equation 3 — Contrast-response function (single neuron, single stimulus)

R(c; x, θ) = ⌊E(x, θ; c) / [s(x, θ) ∗ E(x, θ; c) + σ]⌋_T

Simplified:

r(c) = α c / (c + σ)

- α: response gain (max attainable response)
- σ: contrast gain (contrast at half-maximum response)

### Equation 4 — Stimulus size effect (center + surround)

r(c) = α c / (c + β c_s + σ)

- c: center stimulus contrast
- c_s: surround stimulus contrast
- β ∈ [0, 1]: scale factor on surround suppression

### Equation 5 — Output firing rate with attention

R(x, θ) = ⌊[A(x, θ) E(x, θ)] / [S(x, θ) + σ]⌋_T

- A(x, θ): attention field (gain ≥ 1, applied before normalization)

### Equation 6 — Suppressive drive with attention

S(x, θ) = s(x, θ) ∗ [A(x, θ) E(x, θ)]

### Equation 7 — Contrast gain case (small stimulus, large attention field)

r(c) = α (γ c) / (γ c + σ) = α c / (c + σ/γ)

- γ > 1: peak gain of attention field (treated as constant because the field is large)

### Equation 8 — Response gain case (large stimulus, small attention field)

r(c) = α (γ c) / (γ c + β c + σ)

- γ > 1: peak gain (multiplies center contrast only because attention field is small)
- β ∈ (0, 1): scale factor on surround suppression

---

## Model Components

1. **Stimulation field** — range of spatial positions and orientations that evoke an excitatory response. Characterized by receptive field center and orientation preference.
2. **Suppressive field** — range of spatial positions and orientations contributing to suppression. Pools over a broader range than the stimulation field. Can be nonspecific (e.g., orientation-independent).
3. **Attention field A(x, θ)** — gain ≥ 1 specified per neuron. Spatial and featural extents are variable. Spatial attention: narrow in space, broad in orientation. Feature-based attention: vice versa. Multiplies stimulus drive before normalization.

The stimulus, stimulation field, suppressive field, and attention field all have **Gaussian profiles** in space and orientation (per Figure 1 caption).

---

## Table 1 — Per-Figure Parameters

Constants for all simulations: stimulation field size = 5, suppressive field size = 20.

| Panel | Stimulus Size | Attn Field Size | Tuning Width (deg) | Peak Mod (γ) | Unmod baseline |
|-------|---------------|------------------|---------------------|--------------|----------------|
| 1     | 3             | 30               | –                   | 2            | –              |
| 2A    | 3             | 30               | –                   | 2            | –              |
| 2B    | 5             | 3                | –                   | 2            | –              |
| 3C    | 5             | 30               | –                   | 2            | X              |
| 3F    | 7             | 7                | –                   | 2            | X              |
| 4C    | 5             | 5                | 20                  | 5            | –              |
| 4E    | 5             | 5                | 20                  | 5            | –              |
| 5C    | 10            | 10               | –                   | 2            | –              |
| 6C    | 10            | 30               | 60*                 | 2            | –              |
| 7C    | 5             | 5                | 45*                 | 5            | –              |

Notes from text:
- Spatial sizes in arbitrary units; only relative values meaningful.
- Orientation/direction tuning curves: Gaussian functions.
- V4 experiments (oriented gratings): orientation tuning width 30°, suppressive field tuning width 180°.
- MT/MST experiments (moving stimuli): tuning widths doubled to cover 360° motion directions.
- Dash (–) for attention field tuning width = unselective (all orientations/directions attended equally).
- Asterisk (*) for Figures 6C, 7C = tuning width when attending moving stimuli; unselective when attending fixation.
- "X" under Mod / Unmod columns indicate the form of baseline added.

---

## Per-Figure Simulation Protocols

### Figure 1 — Schematic
Two vertical gratings, equal contrast, one per hemifield. Population responses: stimulus drive, attention field, suppressive drive, output firing rates. Parameters in Table 1.

### Figure 2 — Stimulus and attention-field size effects
- **2A (contrast gain):** stimulus 0.6× stimulation field, attention field 6× stimulation field.
- **2B (response gain):** stimulus = stimulation field (5/3 larger than 2A), attention field 10× smaller than 2A (~2/3 stimulation field).
- Other parameters identical between panels.
- Measurement: contrast-response curves (attended vs unattended) and percent modulation across contrast.

### Figure 3 — Reynolds et al. 2000 vs Williford & Maunsell 2006
- **3C (Reynolds 2000):** single small stimulus in RF, large attention field. Baseline activity added to stimulus drive (modulated by attention) AND additional unmodulated baseline after normalization.
- **3F (Williford & Maunsell 2006):** single larger stimulus filling classical RF, smaller attention field. Same baseline handling.
- Measurement: contrast-response (attended vs unattended), percent modulation per contrast.

### Figure 4 — Two stimuli in RF (contrast and direction)
- **4C (Martinez-Trujillo & Treue 2002):** preferred-direction stimulus contrast varied; nonpreferred fixed. Attention to nonpreferred-in-RF vs opposite hemifield.
- **4E:** preferred and nonpreferred stimuli, contrasts covary. Attention to preferred vs nonpreferred.
- Measurement: contrast-response curves; assess gain type (response vs contrast).

### Figure 5 — Spatial attention and multiplicative scaling
- Single grating in RF, orientation varied across trials.
- Attention to grating (orientation discrimination) vs to opposite hemifield blob (color discrimination).
- Attention field broad (flat) for orientation, selective for spatial position.
- Measurement: orientation tuning curves aligned and averaged; compare with vs without attention.

### Figure 6 — Feature-based attention and tuning sharpening
- Pair of moving stimuli (one in RF, one opposite). Motion directions yoked.
- Spatial attention always away from RF. Feature-based attention to fixation vs to opposite-hemifield stimulus.
- Attention field selective for spatial location AND for motion direction when attending moving stimulus; flat for direction when attending fixation.
- Measurement: tuning curves (response vs motion direction) across attention conditions.

### Figure 7 — Two stimuli in RF + spatial/feature attention combined
- Nonpreferred moving stimulus (fixed direction) plus variable-direction stimulus, both in same RF.
- Three attention conditions: fixation, nonpreferred stimulus, variable stimulus.
- Attention field: flat (spatial selectivity at fixation); spatial+directional for nonpreferred; spatial+directional matching variable.
- Measurement: tuning curves across the three attention conditions.

---

## Figure Captions (Verbatim)

### Figure 1
"Normalization Model of Attention. The stimulus drive is multiplied by the attention field and divided by the suppressive drive to yield the output firing rates. Left panel depicts the stimulus. A pair of vertically orientated gratings were presented as input to the model, identical in contrast, one in each hemifield. Central black dot, fixation point. Solid circle indicates the receptive field of a model neuron selective for vertical orientation and centered on the grating stimulus in the right hemifield. Dashed red circle indicates the attention field, which was centered on the stimulus on the right. Middle panel depicts the stimulus drive for a collection of neurons with different receptive field centers and orientation preferences. Neurons are organized according to their receptive field center (horizontal position) and preferred orientation (vertical position). Brightness at each location in the image corresponds to the stimulus drive to a single neuron. Top panel depicts the attention field when attending to the stimulus on the right (i.e., corresponding to the dashed red circle in the left panel). The attentional field is the strength of the attentional modulation as a function of receptive field center and orientation preference. Here, attentional gain varied as a function of stimulus position, without regard to orientation. Midgray indicates a value of 1 and white indicates a value greater than 1. The attention field is multiplied point-by-point with the stimulus drive. The suppressive drive (bottom panel) is computed from the product of the stimulus drive and the attention field, and then pooled over space and orientation. The panel on the right shows a neural image depicting the output firing rates of the population of neurons, computed by dividing the stimulus drive by the suppressive drive. The stimulus, stimulation field, suppressive field, and attention field all had Gaussian profiles in space and orientation."

### Figure 2
"The Normalization Model of Attention Exhibits Qualitatively Different Forms of Attentional Modulation, Depending on the Stimulus Size and the Size of the Attention Field. Each panel shows contrast-response functions for a simulated neuron, when attending to a stimulus within the neuron's receptive field and when attending to a stimulus in the opposite hemifield. (A) Contrast gain for small stimulus size and large attention field. Red curve, simulated responses as a function of contrast when the stimulus in the receptive field was attended. Blue curve, responses when attending toward the opposite hemifield. Attentional modulation is indicated by the dashed gray curve, which quantifies the percentage increase in the responses when the stimulus within the neuron's receptive field was attended versus not. The stimulus was 0.6 times the size to the stimulation field and the attention field was six times the size of the stimulation field (not drawn to scale, see Table 1 for simulation parameters). (B) Response gain for larger stimulus size and smaller attention field. In comparison to (A), the stimulus size was 5/3 larger (i.e., equal to the size of the stimulation field) and the attention field was 10 times smaller (i.e., about 2/3 the size of the stimulation field). All other model parameters were identical in both panels (Table 1)."

### Figure 3
"Attentional Modulation of Neuronal Contrast-Response Functions. (A) Stimulus and task used by Reynolds et al. (2000) while recording neural activity in V4. Sequences of gratings were presented to the left and right visual fields, one of which was positioned within the receptive field of the recorded neuron. Monkeys were cued to attend either to the stimulus sequence in the receptive field (dashed red circle) or the stimulus sequence in the opposite hemifield (dashed blue circle), to detect a target that appeared in the sequence. (B) Attention caused the largest percentage increase in firing rates at low contrast (adapted from Reynolds et al., 2000). Red curve and data points, responses as a function of contrast, when attention was directed to stimuli in the receptive field. Blue curve and data points, responses to the identical stimuli when unattended. Dashed gray curve, percentage increase in firing rate at each contrast. (C) Normalization model of attention can exhibit similar results. Stimuli, receptive fields, and attention fields are not drawn to scale; Simulation parameters are listed in Table 1. (D) Stimulus and task used in a similar experiment by Williford and Maunsell (2006), also while recording in V4. (E) Attention caused neither a pure contrast gain change nor a pure response gain change (adapted from Williford and Maunsell, 2006). Rather, the greatest percentage increase in firing rates was at low contrasts (dashed gray curve), but with the largest absolute increase in firing rates at high contrasts (compare red and blue curves). (F) Normalization model of attention can exhibit similar results. The simulation was identical to that in (C) except (1) the stimulus was larger and attention field was smaller and (2) additional baseline activity was added for (C) (see Table 1)."

### Figure 4
"Attentional Modulation of Neuronal Contrast-Response Functions with Two Stimuli in the Receptive Field. (A) Stimulus and task used by Martinez-Trujillo and Treue (2002) while recording in MT. The contrast of the preferred direction stimulus (indicated by the upward arrow) within the receptive field was systematically varied across trials, whereas the contrast of the nonpreferred stimulus (indicated by the downward arrow) was held fixed. The monkey was cued to attend either the nonpreferred stimulus in the receptive field (dashed red circle) or the stimulus in the opposite hemifield (dashed blue circle). (B) Attention caused predominantly a change in contrast gain. Red curve and data points, responses as a function of contrast, when attention was directed to the nonpreferred stimulus in the receptive field. Blue curve and data points, responses to the identical stimuli, when attending the opposite hemifield. Dashed gray curve, percentage increase in firing rate at each contrast. (C) Model simulation exhibiting results similar to those observed experimentally. (D) Complementary experiment with two stimuli placed within the receptive field, one preferred and the other nonpreferred. The contrasts of the two stimuli covaried (always identical to one another). (E) Simulated neuronal responses were larger when attention was directed to the preferred-direction stimulus (green curve) than when it was directed to the nonpreferred stimulus (red curve). The effect of attention was approximated by a response gain change (multiplicative scaling). Simulation parameters were identical to those in (C) (Table 1)."

### Figure 5
"Spatial Attention Causes a Multiplicative Scaling of Tuning Curves. (A) Stimulus and task. On some trials, monkeys attended to the grating in the receptive field of the neuron being recorded (dashed red circle) to report whether two successive gratings were identical or differed in orientation by 90°. On other trials, attention was instead directed to a colored blob appearing in the opposite hemifield (dashed blue circle) to report whether successive stimuli differed in color. (B) Orientation tuning curves averaged across a population of V4 neurons, with and without attention (adapted from McAdams and Maunsell, 1999). These curves were obtained by fitting each neuron's tuning curve with a Gaussian, shifting the neuron's preferred orientation to align all tuning curves and then averaging the Gaussian fits. Red indicates orientation tuning when attention was directed to stimuli in the receptive field, to perform the orientation discrimination task. Blue, orientation tuning when attention was directed away from the receptive field to perform the color discrimination task. (C) Model simulation yielded similar results; multiplicative scaling of the tuning curve when spatial attention was directed to a stimulus in the receptive field."

### Figure 6
"Feature-Based Attention Can Cause a Sharpening of Tuning Curves. (A) Stimulus and task. A pair of stimuli were presented simultaneously while recording responses of a neuron in visual cortical area MT. One stimulus was in the receptive field of the recorded neuron and the other was in the opposite hemifield. The directions of the two stimuli were yoked. The monkey was cued to attend either to the fixation point (dashed blue circle), or to the stimulus in the opposite hemifield (dashed red circle) to detect a change in speed or direction. That is, spatial attention was always directed away from the receptive field, but feature-based attention was matched to the stimulus in the receptive field on half the trials. (B) Feature-based attention caused a sharpening of motion direction tuning (adapted from Martinez-Trujillo and Treue, 2004). Blue, responses when attention was directed to the fixation point. Red, responses when attention was directed to the stimulus in the opposite hemifield. (C) Model simulations yielded similar results. Blue, responses of a model neuron when the attention field was flat (equal) for all motion directions, and spatial attention was directed away from the model neuron's receptive field. Red, responses when attention was again directed away from the simulated neuron's receptive field but to the same direction of motion as the stimulus in the receptive field."

### Figure 7
"Attentional Modulation of Tuning when Two Stimuli Are Present within the Receptive Field. (A) Stimulus and task. A pair of stimuli was presented simultaneously while recording responses of a neuron in visual cortical area MT. Both stimuli were presented within the recorded neuron's receptive field. One stimulus moved in the nonpreferred direction (indicated as downward), and the other varied in motion direction. Attention was directed either to the fixation point (dashed yellow circle) or to one of the two stimuli in the receptive field (dashed red and blue circles) to detect a change in speed or direction. (B) Responses were larger when attending the variable direction stimulus (particularly when it moved in the preferred direction) and smaller when attending the nonpreferred stimulus (adapted from Treue and Martinez-Trujillo, 1999). Yellow, tuning (response as a function of the motion direction of the variable stimulus) when attention was directed to fixation. Blue, tuning when attention was directed to the nonpreferred stimulus. Red, tuning when attention was directed to the stimulus with variable motion direction. (C) Responses of a model neuron. Yellow, simulated responses when the attention field was flat (equal) for all motion directions, and spatial attention was directed to the fixation point (i.e., away from the model neuron's receptive field). Blue, simulated responses when the attention field was selective for the spatial location corresponding to the receptive field of the model neuron, and selective for the direction of motion opposite to that preferred by the model neuron. Feature-based attention was thus restricted to a nonpreferred direction of motion. Red, simulated responses when the attention field matched that of the variable stimulus, i.e., with a spatial selectivity corresponding to the receptive field and with a direction selectivity that varied with the stimulus motion direction."

---

## Qualitative Claims About Model Behavior

### Contrast gain regime (Eq. 7)
- Leftward shift of contrast-response function (on log-contrast axis).
- Attentional modulation (% change) larger on the rising portion than on saturating contrasts.
- Largest percentage modulation at intermediate contrasts.

### Response gain regime (Eq. 8)
- Contrast-response function shifted upward (not leftward).
- Attentional modulation large across the full contrast range.
- Largest absolute effects at highest contrasts.

### Response saturation
- Resulting neural responses saturate at high stimulus contrasts due to normalization, regardless of preferred/nonpreferred status.
- When c ≫ σ, r(c) ≈ α.

### Stimulus size effects
- A small stimulus evokes strong stimulus drive but relatively weak suppressive drive.
- Making a stimulus smaller is equivalent to setting surround contrast to zero (decreases suppressive drive).
- Increasing stimulus size by making c_s nonzero increases suppression and decreases output firing rate.

### Two-stimulus interactions
- Only the preferred direction contributes to stimulus drive but both contribute to suppressive drive.
- Response to the pair is less than the response to the preferred direction alone.
- Attending to preferred direction multiplies stimulus drive (equivalent to increasing its contrast).
- Suppression from nonpreferred direction is reduced when preferred is attended.
- Attending to nonpreferred shifts balance in favor of nonpreferred, increasing its suppressive effect and lowering output firing rate.

### Tuning curve scaling
- Spatial attention with broad orientation attention field → multiplicative scaling of orientation tuning curve, no shape change.
- Feature-based attention selective for motion direction → tuning becomes narrower (sharper).

### General
- The attention field reshapes the distribution of activity across the population, shifting the balance between excitation and suppression.
- The particular result depends on the size of the stimulus and attention field, both relative to stimulation and suppressive field sizes.
- Results observed in any one experiment depend on the stimulus conditions and the subject's attentional strategy.

---

## Known Gaps in This Extract (to revisit)

- Exact formula for Gaussian profiles ("size" interpretation: σ vs FWHM vs full extent).
- σ (contrast gain constant) numeric value.
- α (response gain) numeric value.
- T (threshold) value.
- Discretization details (number of neurons in population, range of x).
- Numeric values for "baseline activity" added in Figures 3C / 3F.
- Whether spatial dimension x is 1D or 2D in simulations.
