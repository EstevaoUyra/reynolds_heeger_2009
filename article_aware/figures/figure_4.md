# Figure 4 - Two-Stimulus Contrast-Response Modulation

## Role in the paper

Figure 4 shows that the normalization model can produce two different
attentional effects with the same FOUR-separated-stimulus MT setup and the same
simulation parameters. In Figure 4C, the preferred-direction stimulus contrast
varies while the nonpreferred (null, theta = 180) stimulus contrast is fixed;
both conditions attend the NULL stimulus, comparing attend-null-in-RF
(spatial centre x = 110) against attend-null-contralateral (x = -110). Attending
the null boosts the theta = 180 population, which feeds ONLY the recorded
theta = 0 neuron's suppressive pool, so attend-null-in-RF LOWERS the recorded
neuron's response: the attended (in-RF) curve sits BELOW the attend-away curve —
a SUPPRESSION whose magnitude is largest at low contrast (A-012, CODE-018,
C-021). In Figure 4E, all four stimulus contrasts covary, and directing
attention to the preferred stimulus produces a higher response than directing
attention to the nonpreferred stimulus, approximating response gain. The point
is that the same attention-normalization equations explain both outcomes by
changing which stimulus is attended and how contrasts are swept (C-015, C-019).

---

## Verbatim caption

> "Attentional Modulation of Neuronal Contrast-Response Functions with Two Stimuli in the Receptive Field. (A) Stimulus and task used by Martinez-Trujillo and Treue (2002) while recording in MT. The contrast of the preferred direction stimulus (indicated by the upward arrow) within the receptive field was systematically varied across trials, whereas the contrast of the nonpreferred stimulus (indicated by the downward arrow) was held fixed. The monkey was cued to attend either the nonpreferred stimulus in the receptive field (dashed red circle) or the stimulus in the opposite hemifield (dashed blue circle). (B) Attention caused predominantly a change in contrast gain. Red curve and data points, responses as a function of contrast, when attention was directed to the nonpreferred stimulus in the receptive field. Blue curve and data points, responses to the identical stimuli, when attending the opposite hemifield. Dashed gray curve, percentage increase in firing rate at each contrast. (C) Model simulation exhibiting results similar to those observed experimentally. (D) Complementary experiment with two stimuli placed within the receptive field, one preferred and the other nonpreferred. The contrasts of the two stimuli covaried (always identical to one another). (E) Simulated neuronal responses were larger when attention was directed to the preferred-direction stimulus (green curve) than when it was directed to the nonpreferred stimulus (red curve). The effect of attention was approximated by a response gain change (multiplicative scaling). Simulation parameters were identical to those in (C) (Table 1)."

---

## Simulation parameters

| Parameter | Figure 4C model simulation | Figure 4E model simulation | Citation |
|-----------|----------------------------|----------------------------|----------|
| Recorded model neuron | RF center x = 100 (= round(mean(90,110))), preferred motion direction theta = 0 | RF center x = 100, preferred motion direction theta = 0 | CODE-018 |
| Stimulus configuration | FOUR separated stimuli: RF pair x=90 (theta=0, preferred) and x=110 (theta=180, null); contralateral pair x=-90 and x=-110 | FOUR separated stimuli: same layout (x=90/110 RF pair; x=-90/-110 contralateral pair) | CODE-018 |
| Preferred stimulus direction | theta = 0, matching the recorded neuron (at x=90 / x=-90) | theta = 0, matching the recorded neuron | C-015, CODE-018 |
| Nonpreferred stimulus direction | theta = 180 degrees, opposite the recorded neuron's preference (at x=110 / x=-110) | theta = 180 degrees, opposite the recorded neuron's preference | C-015, CODE-018 |
| Contrast sweep | Preferred contrast c_pref log-spaced over cRange [1e-4, 0.1] | Shared contrast c log-spaced over cRange [1e-4, 0.1] (all four covary) | CODE-018, CODE-020 |
| Fixed nonpreferred contrast | c_nonpref = 0.01 (null held fixed) | Not fixed separately; all four contrasts covary = c | CODE-018, CODE-020 |
| Attention conditions | Both attend the NULL stimulus: attend-null-in-RF (Ax=110) vs attend-null-contralateral (Ax=-110) | Attend preferred (Ax=90, Atheta=0) vs attend nonpreferred (Ax=110, Atheta=180) | C-015, CODE-018 |
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
  contrast of the preferred stimulus, c_pref, increasing left to right over
  cRange [1e-4, 0.1] while the null contrast is fixed at 0.01. The left y-axis
  is normalized model response of the recorded preferred-direction neuron. The
  right y-axis is percent attentional modulation, reported as the suppression
  magnitude 100*(unattended-attended)/unattended (CODE-018).
- **Panel E:** model output for the Figure 4E protocol. The x-axis is log
  contrast c, increasing left to right, with c_pref = c_nonpref = c. The left
  y-axis is normalized model response. The paper-style panel overlays percent
  attentional modulation on a right axis, while the protocol declares the
  generated auxiliary output as a ratio, attend_pref / attend_nonpref (C-015).
- **Curve encoding in Panel C:** the condition attending the null in the RF
  (attended) is the LOWER solid response curve — attending the null in the RF
  SUPPRESSES the recorded preferred neuron; the attend-null-contralateral
  (attend-away / unattended) condition is the HIGHER solid response curve
  (A-012, C-021). The dashed curve is the positive suppression magnitude
  100*(unattended-attended)/unattended (CODE-018). NOTE: the digitized
  panel_C JSON mislabeled the UPPER solid as "attended"; the upper solid is in
  fact the author Att-Away/unattended condition (A-012 / DR-4C-sign resolution).
- **Curve encoding in Panel E:** the condition attending the preferred stimulus
  is the higher solid response curve; the condition attending the nonpreferred
  stimulus is the lower solid response curve. The dashed curve is percent
  attentional modulation (C-015, C-021).
- **Suppression signature (Panel C):** attending the null in the RF holds the
  recorded preferred neuron's response BELOW the attend-away condition across
  the swept contrasts, with the suppression magnitude largest at low contrast
  and declining toward high contrast as both curves saturate (A-012, CODE-018,
  C-021). (The earlier "leftward-shift / contrast-gain facilitation" framing was
  the retired colocated-x=0 build, overturned by the author Figure4C.m.)
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

Panel B is empirical reference data (Martinez-Trujillo & Treue 2002 firing
rates) and is not generated by the model protocol. The empirical caption
describes a "percentage increase" in the DATA panel; that describes the data,
not the model panel C. In the model (author Figure4C.m, A-012), the 4C "attend
the null stimulus in RF" condition boosts the theta = 180 population that feeds
ONLY the recorded theta = 0 neuron's suppressive pool, so attend-null-in-RF
LOWERS the recorded neuron's response relative to attend-away — a SUPPRESSION,
reported as a positive suppression magnitude (C-021, CODE-018).

### Panel C - Model simulation for preferred-contrast sweep with fixed nonpreferred contrast

Panel C is generated by the Figure 4C protocol exactly as the authors' released
Figure4C.m (CODE-018, A-012). For each preferred contrast c_pref, the model
builds stimulus drive E from FOUR separated stimuli: a preferred (theta = 0)
component at x = 90 and x = -90 with contrast c_pref, and a null (theta = 180)
component at x = 110 and x = -110 with fixed contrast 0.01 (EQ-stim, C-009,
CODE-018). Both attention conditions attend the NULL stimulus via an OVAL
attention field — a spatial Gaussian centred on the null stimulus times a
theta = 180 feature Gaussian (AthetaWidth = 20 degrees): the attended condition
centres the spatial field in the RF (Ax = 110) and the unattended condition
centres it contralaterally (Ax = -110) (EQ-attention, C-005, CODE-018). The
suppressive drive S is computed from the attention-modulated stimulus drive, and
the recorded neuron's response R is the attention-modulated drive divided by S
plus sigma (EQ-6, EQ-5, C-005, C-006).

Because attending the null boosts the theta = 180 population that feeds ONLY the
recorded theta = 0 neuron's suppressive denominator (not its numerator),
attend-null-in-RF LOWERS the recorded neuron's response relative to the
attend-away (contralateral) condition — a SUPPRESSION (C-021). The resulting
solid model curve for attend-null-in-RF (attended) sits BELOW the attend-away
(unattended) curve across the swept contrasts. The dashed percent-modulation
curve is the positive suppression magnitude 100*(unattended-attended)/unattended
(Figure4C.m:74), peaking ~38% at low contrast and declining as both response
curves saturate at high contrast (CODE-018, C-019, C-020). Verified end-to-end
through rh_model.simulate: the configuration reproduces Figure4C.m's CRFs and a
%-mod peak ~38%, matching the digitized panel ~36% (A-012).

### Panel D - Complementary two-stimulus covarying-contrast schematic

Panel D is a schematic for the complementary Figure 4E condition. As in 4C the
model uses FOUR separated stimuli (RF pair at x=90 theta=0 / x=110 theta=180,
contralateral pair at x=-90 / x=-110), one moving in the preferred direction and
one in the nonpreferred direction within the RF. Unlike Panel A, all four
stimulus contrasts covary and are always identical to one another. This panel
defines the contrast manipulation for Panel E, but the model protocol's declared
outputs are the contrast-response curves and their ratio, not a separate
schematic output (C-015, CODE-018).

### Panel E - Model simulation for covarying preferred and nonpreferred contrasts

Panel E is generated by the Figure 4E protocol (author Figure4E.m, CODE-018).
For each contrast c, the model builds E from the SAME four-separated-stimulus
layout as 4C (RF pair x=90 theta=0 / x=110 theta=180; contralateral pair
x=-90 / x=-110), with all four contrasts covarying together
(stim = c*(stim1+stim2+stim3+stim4)) — unlike 4C the null is NOT held fixed
(EQ-stim, C-009, CODE-018, CODE-020). The two attention conditions both target
the RF location via an oval field, but one is feature-selective for the
preferred direction (Ax=90, Atheta=0) and the other for the nonpreferred
direction (Ax=110, Atheta=180) (EQ-attention, C-005, CODE-018). The model then
computes S from A times E and computes the recorded neuron's output R by
divisive normalization (EQ-6, EQ-5, C-005, C-006). Note: co-locating the two
stimuli at x=0 (the retired build) inflates %-modulation to ~386%; the author
four-separated geometry yields ~52% (matching the digitized ~54%, CODE-018).

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

2. **Same equations, different attention target:** Both model panels use the
   same attention-normalization equations. In C, both conditions attend the NULL
   (theta = 180) stimulus, which feeds only the recorded neuron's suppressive
   denominator — attending it in the RF SUPPRESSES the recorded neuron; in E,
   attention to the preferred stimulus boosts the numerator more directly than
   attention to the nonpreferred stimulus (EQ-5, EQ-6, C-005, C-006).

3. **Panel C is suppressive for attend-null-in-RF:** The attend-null-in-RF
   (attended) curve in Panel C sits BELOW the attend-away (contralateral) curve.
   This follows from attending the null boosting the theta = 180 population that
   feeds only the recorded neuron's suppressive pool, yielding a positive
   suppression magnitude (A-012, C-021, CODE-018).

4. **Panel E is response-gain-like and facilitatory for preferred attention:**
   The attend-preferred curve in Panel E is above the attend-nonpreferred curve
   across the contrast range and saturates higher, matching the response-gain
   qualitative regime (C-015, C-019, C-021).

5. **The two panels differ in sign at the recorded neuron:** In Panel C, the
   attended (attend-null-in-RF) condition is BELOW the attend-away condition
   (suppression); in Panel E, the attend-preferred condition is above the
   attend-nonpreferred condition (enhancement). The sign difference follows from
   WHICH stimulus is attended relative to the recorded neuron's preference — the
   null feeds suppression, the preferred feeds the numerator (A-012, C-021).

6. **Both model panels saturate at high contrast:** The solid model curves in C
   and E level off as contrast approaches the top of the sweep because divisive
   normalization saturates high-contrast responses (C-020).

7. **Panel C diagnostic is a suppression gap:** Panel C's diagnostic feature is
   the vertical gap with attend-null-in-RF BELOW attend-away (largest at low
   contrast), whereas Panel E's diagnostic feature is a vertical separation with
   attend-preferred ABOVE attend-nonpreferred over a similar contrast range
   (A-012, C-015, C-019, C-021).

8. **Empirical panels are context, not direct model outputs:** Panels A, B, and
   D explain the experimental/task conditions motivating the simulations, but
   the Figure 4 protocol declares generated model outputs for the curve arrays
   in C and E (C-015).
