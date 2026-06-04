# Figure 2 — Panel B (MODEL, reproduced)

**Role:** Model CRF panel — "predominantly response gain" regime.
**Reproduced:** yes (model panel).

## Axis limits (read from the paper figure_2.jpg)

- **x:** Log Contrast. Scale **log**. Model sweep contrast ∈ [1e-5, 1.0];
  `xlim = (1e-5, 1.0)` — the author Figure2B.m `cRange = [1e-5 1]` (CODE-020),
  not the prior guessed [0.01, 1]. No numeric x ticks in the paper (stimulus glyphs).
- **y-left:** "Normalized Model Response". Linear. **ylim = (0.0, 1.0)**.
- **y-right (twin):** "Attentional Modulation (%)". Linear. **ylim = (0.0, 100.0)**.

## Binding qualitative claims (model curves only)

- Two solid CRFs (Ignored, Attended); the Attended curve is **scaled up**
  (response gain) relative to Ignored, with little/no left shift — the curves do
  **not** converge at high contrast (contrast with Panel A).
- Dashed "% Attentional modulation" curve here is comparatively **flatter / rises
  toward high contrast** relative to Panel A, and stays within [0, 100].

## Not-reproduced inset elements

- The RF/attention-field ring schematic inset is configuration, not model data —
  not reproduced.
