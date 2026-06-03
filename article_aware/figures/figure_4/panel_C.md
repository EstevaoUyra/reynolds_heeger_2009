# Figure 4 — Panel C (MODEL, reproduced)

**Role:** Model CRF panel — two stimuli colocated in RF; attend the nonpreferred
stimulus vs attend away. Preferred-stimulus contrast swept.
**Reproduced:** yes (model panel).

## Axis limits (read from the paper figure_4.jpg)

- **x:** Log Contrast. Scale **log**. Model sweep contrast ∈ [0.01, 1.0];
  `xlim = (0.01, 1.0)`.
- **y-left:** "Normalized Response". Linear. **ylim = (0.0, 1.0)** (paper ticks 0..1).
- **y-right (twin):** "Attentional Modulation (%)". Linear. **ylim = (0.0, 100.0)**
  (paper ticks 0 at bottom, 100 at top).

## Binding qualitative claims (model curves only)

- Two solid CRFs, both sigmoidal, rendered on the **Figure-4 shared response
  scale** (with 4E; NOT per-pair-renormalized to 1.0 — see
  `model_spec.yaml rendering_conventions.crf_shared_response_scale`).
- **Facilitation / contrast gain (Finding 2):** the attend-nonpreferred-in-RF
  (attended) CRF sits **ABOVE** attend-away, separated by a visible gap (~0.10 of
  full scale at mid-contrast, narrowing to ~0.04 near saturation; merging only in
  the low-contrast toe x < ~0.025), and is **left-shifted** (smaller half-max
  contrast). Attended saturates ~0.80, unattended ~0.77 of full scale.
- Dashed "% Attentional modulation" curve is **positive**, peaks ~+36% at low
  contrast and **declines** to a few % at high contrast, staying within [0, 100].
- Mechanism: a SPATIAL attention cue to the RF boosts both colocated stimuli
  (M&T 2002 task), reaching the recorded θ=0 neuron's numerator. Referent: the
  Fig-4 caption + C-019; panel_C_digitized.json. C-021 (the 4E suppression prose)
  is NOT the referent for 4C.
