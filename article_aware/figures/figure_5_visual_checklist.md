# Figure 5 - Visual Checklist

Each item is a binary pass/fail visual claim. No paper access is required; all context
needed to evaluate the generated model output is included here. Items tagged
`<!-- UNSURE -->` were difficult to read from the paper figure and deserve extra attention
during review.

---

## Coordinate convention

Figure 5 has three panels in the paper, but the implementation protocol generates the
model simulation output for **panel C** only.

- **Panel A:** task schematic context. It is not a generated model output for this
  protocol.
- **Panel B:** empirical V4 population tuning curves adapted from McAdams and Maunsell
  (1999). It is not a generated model output for this protocol.
- **Panel C:** model orientation tuning curves. The horizontal axis is stimulus
  orientation relative to the recorded neuron's preferred orientation. The center of the
  x-axis is the preferred orientation (0 degrees); left and right sides are nonpreferred
  orientations of opposite sign. The vertical axis is normalized response, with 0 at the
  bottom and 1 near the top.
- **Curve encoding for panel C:** the upper solid curve is the response when attention is
  directed to the stimulus in the receptive field. The lower solid curve is the response
  when attention is directed to the opposite hemifield. A correct generated model figure
  may use color or line weight to distinguish these conditions, but the attended curve
  must be visually identifiable as the larger response curve.
- **Multiplicative scaling:** the attended and unattended tuning curves should have the
  same peak location and the same apparent width. The attended condition should look like
  a scaled-up version of the unattended condition, not like a shifted or sharpened curve.

---

## Overall generated-output scope

- [ ] The generated Figure 5 output includes the model simulation panel corresponding to
      panel C.
- [ ] The visual comparison does not require reproducing detailed empirical data geometry
      from panel B.
- [ ] The visual comparison does not require reproducing detailed task-schematic geometry
      from panel A.

---

## Panel C - Model Spatial-Attention Tuning Curves

- [ ] The panel contains exactly two primary solid orientation-tuning curves.
- [ ] Both curves are single-peaked and approximately bell-shaped.
- [ ] Both curves reach their maximum at the center of the x-axis, corresponding to the
      recorded neuron's preferred orientation.
- [ ] The attended curve is above the unattended curve at the central peak.
- [ ] The attended curve is above the unattended curve across the visible orientation
      range, not only at the peak.
- [ ] The two curves have the same peak orientation; the attended curve is not shifted
      left or right relative to the unattended curve.
- [ ] The two curves have approximately the same width at half-height; attention does not
      visibly narrow or broaden the tuning curve.
- [ ] The two curves have approximately parallel rising flanks on the left side of the
      peak.
- [ ] The two curves have approximately parallel falling flanks on the right side of the
      peak.
- [ ] Both curves decline toward low response values at the left and right edges of the
      orientation range.
- [ ] The curve separation is largest in absolute response units near the central peak and
      smaller near the low-response tails.
- [ ] The attended curve appears to be a near-uniform multiplicative scaling of the
      unattended curve rather than an additive upward offset. <!-- UNSURE: tails are close to the axis in the printed panel, so constant ratio is easier to infer from shape than to read directly at the edges -->
- [ ] No additional curve shows feature-based sharpening or a narrower attention-selective
      profile.
- [ ] If a ratio trace or ratio annotation is included in the generated output, it is
      approximately flat across orientations except where both response curves are very
      close to zero. <!-- UNSURE: the paper panel itself does not draw the ratio, but the protocol exposes ratio as a named output -->

---

## Cross-output checks

- [ ] The visual impression of panel C is response scaling without shape change: higher
      amplitude, same center, same width.
- [ ] The panel C model curves qualitatively match the empirical pattern described for
      panel B only at the level of two aligned tuning curves with attention increasing
      response; detailed empirical point locations, averaging, or fitted-data geometry are
      not required.
