# Figure 4 - Visual Checklist

Each item is a binary pass/fail visual claim. No paper access is required; all
context needed to evaluate the generated figure is included here. Items tagged
`<!-- UNSURE -->` were difficult to read from the paper figure or depend on a
renderer choice and deserve extra attention during review.

This checklist focuses on the generated model simulation outputs for Figure 4C
and Figure 4E. Panels A, B, and D in the paper figure are experimental/task
context; do not fail a generated model figure for omitting detailed empirical
point locations, error bars, or source labels from those panels unless the
implementation explicitly chooses to render them.

---

## Coordinate convention

- **Panel C model output:** x-axis is log contrast of the preferred-direction
  stimulus, c_pref, increasing left to right. The nonpreferred stimulus is
  fixed at contrast 0.5. The left y-axis is normalized response of the model
  neuron preferred for theta = 0. The right y-axis is percent attentional
  modulation from 0% at bottom to 100% at top.
- **Panel E model output:** x-axis is log contrast c, increasing left to right,
  with c_pref = c_nonpref = c. The left y-axis is normalized response of the
  model neuron preferred for theta = 0. A paper-style rendering may overlay
  percent attentional modulation on a right axis; a protocol-style rendering
  may instead show the attend-pref / attend-nonpref ratio separately.
- **Panel C curve encoding:** the lower solid response curve is attention to
  the nonpreferred stimulus in the RF; the higher solid response curve is
  attention to the opposite hemifield. The dashed curve is percent attentional
  modulation.
- **Panel E curve encoding:** the higher solid response curve is attention to
  the preferred stimulus in the RF; the lower solid response curve is attention
  to the nonpreferred stimulus in the RF. The dashed curve is percent
  attentional modulation.
- **"Right-shifted"** means a curve reaches its inflection point or
  half-maximum at a higher x-axis contrast.
- **"Response-gain-like"** means two curves rise over similar x-axis contrast
  ranges, but one curve is vertically higher and saturates at a higher y-value.

---

## Overall generated figure structure

- [ ] The generated figure includes a model output corresponding to Figure 4C.
- [ ] The generated figure includes a model output corresponding to Figure 4E.
- [ ] The Figure 4C and Figure 4E model outputs are visually distinct panels or
      subplots.
- [ ] Each model output has contrast on the x-axis increasing from low contrast
      at left to high contrast at right.
- [ ] Each model output has normalized response or equivalent model response on
      the primary y-axis.
- [ ] Each model output includes two solid response curves for the two attention
      conditions.
- [ ] Each model output includes a dashed or otherwise clearly distinguished modulation curve, or a separate plotted ratio/modulation output if the implementation separates modulation from response curves. <!-- UNSURE: the protocol declares percent_modulation for 4C and ratio for 4E, so renderers may not place both on the same axes -->
- [ ] If the generated figure includes paper-context panels A, B, or D, those
      panels are visually secondary to the model-simulation outputs and are not
      required to reproduce empirical data point geometry.

---

## Panel A - Task Schematic Context

- [ ] If rendered, this panel is recognizable as a schematic/context panel
      rather than a model contrast-response curve.
- [ ] If rendered, the schematic shows two stimuli inside the recorded
      receptive field: one preferred-direction stimulus and one nonpreferred-
      direction stimulus.
- [ ] If rendered, the schematic indicates an attention condition aimed at the
      nonpreferred stimulus in the receptive field.
- [ ] If rendered, the schematic indicates an alternative attention condition
      away from the recorded receptive field.

---

## Panel B - Empirical Reference Context

- [ ] Panel B is either omitted from the generated model figure or clearly
      marked as empirical reference/context rather than a model-generated
      output.
- [ ] If Panel B is included, the reviewer does not need to check individual
      empirical point positions or error-bar lengths.
- [ ] If Panel B is included, it conveys only the coarse contrast-gain-like
      reference pattern: two rising response curves and a modulation curve.

---

## Panel C - Model Simulation: Preferred Contrast Varied, Nonpreferred Fixed

- [ ] The panel contains two solid sigmoidal model response curves.
- [ ] Both solid curves rise from low normalized response at low preferred
      contrast to higher normalized response at high preferred contrast.
- [ ] Both solid curves saturate or level off toward the high-contrast end.
- [ ] The attend-nonpreferred response curve is below the opposite-hemifield
      attention curve over the visible contrast range.
- [ ] The attend-nonpreferred curve is right-shifted relative to the opposite-
      hemifield curve: its steep rising portion occurs at higher preferred
      contrast.
- [ ] The opposite-hemifield curve begins rising earlier on the log-contrast
      axis than the attend-nonpreferred curve.
- [ ] The two solid curves are closest together at the far low-contrast end before either curve has risen substantially. <!-- UNSURE: the printed panel is small, and the low-contrast separation is hard to read -->
- [ ] The two solid curves remain separated through the rising portion of the
      contrast-response function.
- [ ] The high-contrast endpoints of the two solid curves are close but not perfectly identical in the paper panel. <!-- UNSURE: the curves nearly meet near the top-right corner, but the printed line thickness makes convergence ambiguous -->
- [ ] A dashed modulation curve is present or the same modulation quantity is
      plotted in a separate companion axis.
- [ ] The dashed modulation curve in the combined paper-style panel trends downward from left to right over most of the contrast range. <!-- UNSURE: the curve is low-amplitude and drawn close to the response curves in the printed panel -->
- [ ] The dashed modulation curve is lower at high contrast than at low or
      low-to-intermediate contrast.
- [ ] The dashed modulation curve does not form a high-contrast peak at the
      right side of the panel.
- [ ] The panel visually reads as contrast-gain-like: the main difference
      between solid curves is horizontal shift along the log-contrast axis, not
      a large high-contrast vertical separation.

---

## Panel D - Covarying-Contrast Schematic Context

- [ ] If rendered, this panel is recognizable as a schematic/context panel
      rather than a model contrast-response curve.
- [ ] If rendered, the schematic shows both the preferred-direction and
      nonpreferred-direction stimuli colocated within the recorded receptive
      field.
- [ ] If rendered, the schematic communicates that the two stimulus contrasts covary rather than showing one stimulus as the only varying contrast. <!-- UNSURE: covarying contrast is a trial/protocol property and may not be visually encoded in a static schematic -->

---

## Panel E - Model Simulation: Preferred and Nonpreferred Contrasts Covary

- [ ] The panel contains two solid sigmoidal model response curves.
- [ ] Both solid curves rise from low normalized response at low contrast to
      higher normalized response at high contrast.
- [ ] Both solid curves saturate or level off toward the high-contrast end.
- [ ] The attend-preferred response curve is above the attend-nonpreferred
      response curve at every visible contrast.
- [ ] The attend-preferred and attend-nonpreferred curves rise over similar
      log-contrast ranges rather than showing a large horizontal offset.
- [ ] The attend-preferred curve saturates at a higher normalized response than
      the attend-nonpreferred curve.
- [ ] The two solid curves remain visibly separated at the high-contrast
      endpoint.
- [ ] The high-contrast vertical separation in Panel E is larger than the
      high-contrast vertical separation in Panel C.
- [ ] The panel visually reads as response-gain-like: the main difference
      between solid curves is vertical scaling, not a rightward or leftward
      contrast shift.
- [ ] A dashed modulation curve is present or the same modulation/ratio
      quantity is plotted in a separate companion axis.
- [ ] In the paper-style combined panel, the dashed modulation curve is highest
      near the low-contrast side and lower near the high-contrast side.
- [ ] In the paper-style combined panel, the dashed modulation curve decreases
      gently rather than dropping all the way to the x-axis.
- [ ] The dashed modulation curve does not cross either solid response curve in a way that makes the attention-condition ordering ambiguous. <!-- UNSURE: dual-axis overlays may differ across renderers, so crossing is partly a plotting-style issue -->

---

## Cross-panel model checks

- [ ] Panel C shows a stronger horizontal contrast shift between the two solid
      response curves than Panel E.
- [ ] Panel E shows a stronger high-contrast vertical separation between the
      two solid response curves than Panel C.
- [ ] The attention condition associated with the nonpreferred stimulus lowers
      the preferred neuron's response in Panel C relative to opposite-
      hemifield attention.
- [ ] The attention condition associated with the preferred stimulus raises the
      preferred neuron's response in Panel E relative to nonpreferred
      attention.
- [ ] Both model panels use the same qualitative contrast range: low contrast
      at the left edge and high contrast at the right edge.
- [ ] Both model panels show high-contrast saturation of the solid response
      curves.
- [ ] Neither model panel shows a bell-shaped response curve with an interior
      peak; the solid response curves are monotonic increasing and saturating.
- [ ] Empirical reference content, if present, is visually separated from model
      output so a reviewer can evaluate the generated simulation curves without
      judging empirical pointwise reproduction.
