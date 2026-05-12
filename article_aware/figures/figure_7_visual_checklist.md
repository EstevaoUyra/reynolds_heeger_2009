# Figure 7 - Visual Checklist

Each item is a binary pass/fail visual claim. No paper access is required; all context
needed to evaluate the generated figure is included here. Items tagged `<!-- UNSURE -->`
were difficult to read from the paper figure and deserve extra attention during review.

---

## Coordinate convention

Figure 7 has three panels arranged left to right:

- **Panel A:** stimulus/task schematic. The solid circle is the recorded neuron's
  receptive field. Dashed circles are possible attention fields. Arrow icons indicate
  stimulus motion directions.
- **Panel B:** empirical reference data from Treue and Martinez-Trujillo (1999). It is
  context for the model result and is not a generated model output in the Figure 7C
  protocol.
- **Panel C:** generated model tuning curves. This is the primary reproduction target.
- **Horizontal axis for panels B and C:** motion direction of the variable stimulus. The
  paper figure uses arrows rather than numeric tick labels. Left and right ends indicate
  nonpreferred/downward motion; the center upward arrow indicates the recorded neuron's
  preferred direction. In protocol terms, the center is theta_var = 0 degrees and the
  ends are approximately theta_var = +/-180 degrees.
- **Vertical axis for panel C:** normalized response of the recorded model neuron at
  x = 0 and preferred direction theta = 0.
- **Curve encoding in panel C:** highest/dark curve = attend variable stimulus; middle
  curve = attend fixation / ignored RF stimuli; lowest curve = attend nonpreferred
  stimulus. The printed legend identifies these as variable-attended, ignored, and
  nonpreferred-attended conditions.
- **Attention-condition outputs:** `attend_variable_tuning`, `fixation_tuning`, and
  `attend_nonpref_tuning` are plotted against the same `theta_var_grid`.

---

## Overall figure structure

- [ ] The figure contains exactly three panels arranged in one horizontal row.
- [ ] The panels are labeled A, B, and C from left to right.
- [ ] Panel C is a model-output panel with smooth tuning curves, not point/error-bar data.
- [ ] A single legend below the panels identifies the solid receptive-field circle.
- [ ] The bottom legend identifies dashed circles as attention fields.
- [ ] The bottom legend identifies arrow icons as stimulus motion directions.
- [ ] The bottom legend distinguishes the three tuning curves: attend variable stimulus,
      ignored/fixation, and attend nonpreferred stimulus.
- [ ] The motion-direction arrow row under panels B and C has a central upward arrow and
      downward arrows at both ends.

---

## Panel A - Stimulus and task schematic (context)

Panel A is a task schematic rather than an implementation output for Figure 7C. These
checks are coarse context checks only; a generated model-output-only figure should not
fail because it omits detailed task artwork.

- [ ] If panel A is included, it shows one solid receptive-field circle containing the
      two RF stimuli.
- [ ] If panel A is included, it shows a fixation marker outside the receptive field.
- [ ] If panel A is included, one dashed attention circle is drawn at fixation and two
      dashed attention circles overlap the RF stimulus region.
- [ ] If panel A is included, the RF contains one fixed downward/nonpreferred stimulus
      arrow and one variable-direction stimulus arrow.

---

## Panel B - Empirical reference data (not a model reproduction target)

Panel B is empirical reference data adapted from Treue and Martinez-Trujillo (1999). The
Figure 7C implementation protocol does not generate these data, so a reviewer should not
score detailed empirical point locations, error bars, or firing-rate values for model
reproduction.

- [ ] If panel B is included, it is visually distinguishable from panel C as empirical
      reference data, for example by using point/error-bar data or a source label.
- [ ] If panel B is included as context, the generated figure does not imply that the
      empirical firing-rate data were produced by the model.

---

## Panel C - Model responses of a neuron with two stimuli in the RF

- [ ] Panel C contains exactly three smooth tuning curves plotted over the variable
      stimulus motion-direction axis.
- [ ] All three curves are single-peaked around the central preferred-direction arrow.
- [ ] All three curves are low near the left and right nonpreferred/downward ends of the
      motion-direction axis.
- [ ] The attend-variable curve has the highest peak at the preferred-direction center.
- [ ] The fixation/ignored curve has a peak below the attend-variable peak.
- [ ] The attend-nonpreferred curve has the lowest peak at the preferred-direction
      center.
- [ ] Near the preferred-direction center, the vertical ordering is attend variable
      above fixation/ignored above attend nonpreferred.
- [ ] The attend-variable curve is broader than the attend-nonpreferred curve around the
      central peak. <!-- UNSURE: the scan is small and the exact curve widths are hard to separate -->
- [ ] The attend-nonpreferred curve remains visibly below the fixation/ignored curve
      through most of the rising and falling flanks near the central peak.
- [ ] The attend-variable curve remains visibly above the fixation/ignored curve through
      most of the rising and falling flanks near the central peak.
- [ ] The three curves approach similar low responses at the far left and far right
      endpoints. <!-- UNSURE: the endpoints are close together and the printed curves overlap -->
- [ ] No model curve is flat: each curve rises from a low endpoint to a central peak and
      then falls again.
- [ ] The y-axis label for panel C is normalized response or an equivalent model-response
      label, not firing rate in Hz.
- [ ] The panel does not include empirical data markers or error bars inside the model
      output plot.

---

## Cross-panel and protocol checks

- [ ] Panel C uses motion direction of the variable stimulus as the horizontal axis, not
      stimulus contrast.
- [ ] Panel C compares attention conditions, not different stimulus contrasts.
- [ ] The model panel preserves the qualitative ordering described by the protocol:
      attending the variable stimulus increases responses near the preferred direction,
      while attending the nonpreferred stimulus decreases them.
- [ ] The generated model output focuses on panel C; panel B empirical geometry is not
      treated as a required model-simulation reproduction target.
