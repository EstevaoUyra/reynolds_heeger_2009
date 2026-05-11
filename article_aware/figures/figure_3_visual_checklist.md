# Figure 3 - Visual Checklist

Each item is a binary pass/fail visual claim. No paper access is required; all context
needed to evaluate the generated figure is included here. Items tagged `<!-- UNSURE -->`
were difficult to read from the paper figure and deserve extra attention during review.

---

## Coordinate convention

Figure 3 has two rows of three panels:

- **Panels A and D:** schematic stimulus/task panels. Left and right refer to the two
  visual hemifields. The black dot between them is fixation. The recorded neuron's
  receptive field is around the right-side stimulus. Dashed circles indicate possible
  attention fields for attention directed to either stimulus sequence.
- **Panels B and E:** empirical contrast-response data. The x-axis is stimulus contrast
  from low/0% at left to high contrast at right. The left y-axis is firing rate in Hz.
  The right y-axis is attentional modulation in percent, ranging from 0% at bottom to
  100% at top.
- **Panels C and F:** model contrast-response curves. The x-axis is log contrast from
  low contrast at left to high contrast at right. The left y-axis is normalized model
  response from 0 to 1. The right y-axis is attentional modulation in percent from 0% to
  100%.
- **Curve encoding:** solid dark curve = attend stimulus in the receptive field; solid
  lighter/thinner curve = attend stimulus contralateral to the receptive field; dashed
  curve = percent attentional modulation.
- **"Left-shifted"** means the attended curve reaches its inflection point or half-
  maximum at a lower contrast than the unattended curve.
- **"Absolute difference"** means the vertical separation between the two solid response
  curves at the same contrast.

---

## Overall figure structure

- [ ] The figure contains exactly six panels arranged as two rows by three columns.
- [ ] The top row panels are labeled A, B, and C from left to right.
- [ ] The bottom row panels are labeled D, E, and F from left to right.
- [ ] A single legend spans the bottom of the figure.
- [ ] The bottom legend identifies the receptive field as a solid circle.
- [ ] The bottom legend identifies attention fields as dashed circles.
- [ ] The bottom legend identifies stimulus patches as vertical grating bars.
- [ ] The bottom legend distinguishes the two solid response curves and the dashed
      percent-modulation curve.
- [ ] Panels C and F are both titled "Mixed Attention Effect" or equivalent.

---

## Panel A - Reynolds et al. 2000 Schematic

- [ ] The schematic shows two small vertical grating patches, one in the left hemifield
      and one in the right hemifield.
- [ ] A small black fixation dot appears between the two grating patches.
- [ ] The right-side stimulus is enclosed by a solid receptive-field circle.
- [ ] The right-side stimulus is also enclosed by a dashed attention-field circle.
- [ ] The left-side stimulus is enclosed by a dashed attention-field circle.
- [ ] The dashed attention-field circles are visibly larger than the grating patches.
- [ ] The grating patch inside the right receptive field is smaller than the receptive-
      field circle, leaving visible blank space around the bars.
- [ ] The two stimulus patches are visually similar in size and orientation.

---

## Panel B - Reynolds et al. 2000 Empirical Data

- [ ] The panel title states that the data are adapted from Reynolds, Pasternak, and
      Desimone (2000), or an equivalent source label.
- [ ] Two solid contrast-response curves are plotted with point/error-bar data.
- [ ] The attended response curve is above the unattended response curve at every
      contrast shown.
- [ ] Both solid curves rise as contrast increases.
- [ ] The attended curve begins above zero firing rate at the lowest contrast shown.
- [ ] The unattended curve begins above zero firing rate at the lowest contrast shown.
- [ ] The largest vertical separation between the solid curves occurs at an intermediate
      or high contrast, not at the leftmost contrast. <!-- UNSURE: error bars and sparse data make the exact largest separation hard to read -->
- [ ] A dashed percent-modulation curve is present.
- [ ] The dashed curve is highest in the low-to-intermediate contrast range and declines
      toward the right side of the panel.
- [ ] The dashed curve approaches the bottom of the right y-axis at the highest contrast.

---

## Panel C - Model Fit to Reynolds et al. 2000 Pattern

- [ ] The panel contains two solid sigmoidal model response curves.
- [ ] The attended response curve is above the unattended response curve at every
      contrast shown.
- [ ] The attended response curve is left-shifted relative to the unattended response
      curve: its steep rising portion starts at lower contrast.
- [ ] The two solid curves converge at high contrast near the top of the normalized
      response axis.
- [ ] The high-contrast endpoint separation between the two solid curves is small.
- [ ] A dashed percent-modulation curve is present.
- [ ] The dashed curve reaches its maximum at low-to-intermediate contrast, near the
      lower part of the solid curves' rising phase.
- [ ] The dashed curve declines toward near-zero modulation by the highest contrasts.
- [ ] Short vertical stimulus tick marks appear near the bottom of the plot at the high-
      contrast end.

---

## Panel D - Williford & Maunsell 2006 Schematic

- [ ] The schematic shows two vertical grating patches, one in the left hemifield and
      one in the right hemifield.
- [ ] The grating patches are larger than the grating patches in panel A.
- [ ] A small black fixation dot appears between the two grating patches.
- [ ] The right-side stimulus is enclosed by a solid receptive-field circle.
- [ ] The right-side stimulus nearly fills the solid receptive-field circle.
- [ ] Dashed attention-field circles are drawn around the left and right stimulus
      locations.
- [ ] The dashed attention-field circles are smaller relative to the stimulus patches
      than the dashed attention-field circles in panel A.
- [ ] The right-side dashed attention field is comparable in size to the right stimulus
      patch rather than much larger than it.

---

## Panel E - Williford & Maunsell 2006 Empirical Data

- [ ] The panel title states that the data are adapted from Williford and Maunsell
      (2006), or an equivalent source label.
- [ ] Two solid contrast-response curves are plotted with point/error-bar data.
- [ ] The attended response curve is above the unattended response curve at every
      contrast shown.
- [ ] Both solid curves rise as contrast increases.
- [ ] The attended and unattended curves have their largest absolute separation at high
      contrast on the right side of the panel.
- [ ] The solid curves do not converge to the same high-contrast firing rate.
- [ ] A dashed percent-modulation curve is present.
- [ ] The dashed curve is highest at the lowest contrast or in the low-contrast region.
- [ ] The dashed curve declines as contrast increases.
- [ ] The dashed curve remains visibly above zero at high contrast, roughly around the
      lower fifth of the modulation axis. <!-- UNSURE: the printed label near the curve is small and the exact high-contrast percentage is hard to read -->

---

## Panel F - Model Fit to Williford & Maunsell 2006 Pattern

- [ ] The panel contains two solid sigmoidal model response curves.
- [ ] The attended response curve is above the unattended response curve at every
      contrast shown.
- [ ] The attended and unattended curves rise over approximately the same log-contrast
      range; the attended curve is primarily higher, not strongly left-shifted.
- [ ] The attended curve saturates at a higher normalized response than the unattended
      curve.
- [ ] The two solid curves remain vertically separated at high contrast.
- [ ] The high-contrast endpoint separation in panel F is visibly larger than the high-
      contrast endpoint separation in panel C.
- [ ] A dashed percent-modulation curve is present.
- [ ] The dashed curve is highest at low contrast, near the top of the modulation axis.
- [ ] The dashed curve decreases monotonically or nearly monotonically as contrast
      increases.
- [ ] The dashed curve remains above zero at high contrast rather than collapsing to the
      x-axis.
- [ ] Short vertical stimulus tick marks appear near the bottom of the plot at the high-
      contrast end.

---

## Cross-panel structural checks

- [ ] Panel D shows larger stimulus patches than panel A.
- [ ] Panel A shows attention fields that are large relative to the stimuli, whereas
      panel D shows attention fields that are comparable to the larger stimuli.
- [ ] Panel C shows a stronger leftward contrast shift than panel F.
- [ ] Panel F shows a larger high-contrast vertical separation between attended and
      unattended model curves than panel C.
- [ ] In both model panels C and F, percent modulation peaks at lower contrast than the
      largest absolute separation between the solid response curves.
- [ ] The dashed modulation curve falls to near zero at high contrast in panel C but
      remains visibly above zero at high contrast in panel F.
- [ ] Panels B and C share the same qualitative pattern: percent modulation is largest
      at low-to-intermediate contrast and then decreases at high contrast.
- [ ] Panels E and F share the same qualitative pattern: percent modulation is largest
      at low contrast while the largest absolute response difference is at high contrast.
