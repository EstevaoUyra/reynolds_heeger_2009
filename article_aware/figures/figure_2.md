# Figure 2 — Contrast Gain vs Response Gain: Two Attentional Regimes

## Role in the paper

Figure 2 is the paper's central quantitative demonstration that the normalization model
produces two qualitatively different forms of attentional modulation depending on the
relative sizes of the stimulus and attention field. Panel A shows the contrast gain regime
(small stimulus, large attention field): the attended contrast-response function is shifted
leftward on the log-contrast axis. Panel B shows the response gain regime (larger stimulus,
smaller attention field): the attended CRF is shifted upward without a lateral shift. Both
panels use identical model parameters except for stimulus size and attention field size,
establishing that the parameter ratio — not the model structure — determines which regime
is observed. This is the paper's primary reconciliation of apparently contradictory
experimental findings.

---

## Verbatim caption

> "The Normalization Model of Attention Exhibits Qualitatively Different Forms of
> Attentional Modulation, Depending on the Stimulus Size and the Size of the Attention
> Field. Each panel shows contrast-response functions for a simulated neuron, when
> attending to a stimulus within the neuron's receptive field and when attending to a
> stimulus in the opposite hemifield. (A) Contrast gain for small stimulus size and large
> attention field. Red curve, simulated responses as a function of contrast when the
> stimulus in the receptive field was attended. Blue curve, responses when attending toward
> the opposite hemifield. Attentional modulation is indicated by the dashed gray curve,
> which quantifies the percentage increase in the responses when the stimulus within the
> neuron's receptive field was attended versus not. The stimulus was 0.6 times the size to
> the stimulation field and the attention field was six times the size of the stimulation
> field (not drawn to scale, see Table 1 for simulation parameters). (B) Response gain for
> larger stimulus size and smaller attention field. In comparison to (A), the stimulus size
> was 5/3 larger (i.e., equal to the size of the stimulation field) and the attention field
> was 10 times smaller (i.e., about 2/3 the size of the stimulation field). All other model
> parameters were identical in both panels (Table 1)."

---

## Simulation parameters

| Parameter                        | Panel A        | Panel B        | Citation |
|----------------------------------|----------------|----------------|----------|
| Stimulus size (σ, space)         | 3 (= 0.6 × 5)  | 5 (= stimulation field) | C-013 |
| Attention field size (σ, space)  | 30 (= 6 × 5)   | 3 (≈ 0.6 × 5)  | C-013    |
| Peak attention gain (γ)          | 2              | 2              | C-013    |
| Stimulation field size (σ)       | 5              | 5              | C-010    |
| Suppressive field size (σ)       | 20             | 20             | C-010    |

All other parameters identical between panels (C-013). Spatial sizes in arbitrary units;
only relative values are meaningful (C-010).

---

## Coordinate convention

Both panels share the same axis structure:

- **Horizontal axis (log contrast):** stimulus contrast on a logarithmic scale. No numeric
  labels appear on the axis. Tick marks along the bottom of each panel indicate the stimulus
  size(s) used in that panel — small tick marks in A (small stimulus), wider tick marks in
  B (larger stimulus).
- **Left vertical axis (Normalized Model Response):** output firing rate, normalized to
  range from 0 to 1.
- **Right vertical axis (Attentional Modulation %):** percentage increase in response when
  attending vs ignoring, ranging from 0 to 100%.
- **Curve encoding (grayscale print):** attended = solid dark/thick curve; ignored
  (unattended) = solid thin/lighter curve; percent modulation = dashed curve.
- **Inset schematic:** each panel contains a small diagram showing the relative sizes of
  the receptive field (solid circle), attention field (dashed circle), and stimulus (vertical
  bars). The inset encodes the size parameters, not a fixed depiction.

---

## Panel and expected behavior

### Panel A — Predominantly Contrast Gain

Governed by the contrast gain limiting case, Eq. 7 (C-007): when the attention field is
large relative to the stimulus (field size 30 >> stimulus size 3), the attention gain γ
acts approximately uniformly across the stimulus footprint, effectively scaling the
contrast: r(c) = α·c / (c + σ/γ). This produces a leftward shift of the CRF on the
log-contrast axis.

- **Inset schematic:** large dashed circle (attention field, size 30) encompasses a large
  solid circle (RF), with a small stimulus (small vertical bars) inside. Visually, the
  attention field is much larger than both the stimulus and the RF.
- **CRF curves:** both the attended and ignored curves are sigmoidal (contrast-response
  functions). The attended curve is shifted leftward — it reaches half-maximum at a lower
  contrast than the ignored curve. Both curves reach approximately the same maximum
  response (same response gain α; only the contrast at half-max changes). The two curves
  converge at high contrast. (C-007, C-019)
- **Percent modulation curve (dashed):** the percentage increase is largest at low-to-
  intermediate contrasts (on the rising portion of the CRF) and decreases toward high
  contrasts where both curves converge near saturation. The modulation curve peaks at or
  below the contrast at half-maximum and falls off at high contrasts. (C-019)

### Panel B — Predominantly Response Gain

Governed by the response gain limiting case, Eq. 8 (C-008): when the attention field is
small relative to the stimulus (field size 3 ≈ stimulus size 5), the gain γ multiplies
only the stimulus drive within the attention field footprint, not the suppressive drive
from the full stimulus surround. This produces an upward scaling of the CRF without a
lateral shift: r(c) = α·γ·c / (γ·c + β·c + σ).

- **Inset schematic:** small dashed circle (attention field, size 3) sits inside the solid
  circle (RF), with a larger stimulus (wider vertical bars) filling the RF. Visually, the
  attention field is smaller than the RF and comparable to or smaller than the stimulus.
- **CRF curves:** both curves are sigmoidal. The attended curve is shifted upward — higher
  response at all contrasts — with less lateral shift compared to panel A. The two curves
  maintain a roughly constant absolute separation across the contrast range rather than
  converging strongly at high contrast. The maximum response of the attended curve may be
  higher than that of the ignored curve. (C-008, C-019)
- **Percent modulation curve (dashed):** the percentage increase is large across a broader
  range of contrasts, including at high contrasts — it does not fall off as sharply at high
  contrast as in panel A. The modulation curve is flatter or shows its peak at higher
  contrast than in panel A. (C-019)

---

## Key inter-panel relationships

1. **Lateral shift in A, not in B:** the attended CRF in panel A is clearly shifted left
   relative to the ignored CRF on the log-contrast axis. In panel B the shift is primarily
   upward with little or no lateral displacement. This is the defining visual difference
   between the two panels. (C-007, C-008, C-019)

2. **Convergence at high contrast in A, not in B:** in panel A the attended and ignored
   curves converge toward the same maximum response at high contrast (same α, different
   effective σ). In panel B the curves maintain a larger separation at high contrast.
   (C-007, C-008)

3. **Modulation curve shape differs:** in panel A the dashed modulation curve peaks at
   low-to-intermediate contrast and falls at high contrast. In panel B the modulation
   curve is sustained at higher contrasts and falls off more slowly. (C-019)

4. **Inset encodes the parameter difference:** the relative sizes of RF, attention field,
   and stimulus in each inset directly reflect the parameter ratio that causes each regime.
   Panel A: large attention field > RF > stimulus. Panel B: RF ≥ stimulus > attention field.

5. **Both CRFs are sigmoidal:** in both panels, both the attended and ignored curves are
   monotonically increasing and saturating (sigmoidal shape). Neither curve decreases at
   high contrast. (C-003)

6. **Both panels use identical model parameters except stimulus and attention field size:**
   the difference in regime arises purely from changing two parameters (C-013). This is
   the paper's argument that the same model accounts for both regimes.
