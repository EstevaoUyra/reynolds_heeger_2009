# Figure 2 — Panel A (MODEL, reproduced)

**Role:** Model CRF panel — "predominantly contrast gain" regime.
**Reproduced:** yes (model panel).

## Axis limits (read from the paper figure_2.jpg)

- **x:** Log Contrast. Scale **log**. The model sweep is contrast ∈ [0.01, 1.0]
  (log-spaced); set `xlim = (0.01, 1.0)`. The paper shows no numeric x ticks
  (stimulus glyphs only), so the discriminating axis facts are scale=log and the
  swept range.
- **y-left:** "Normalized Model Response". Scale linear. **ylim = (0.0, 1.0)**
  (paper ticks: 0 at bottom, 1 at top).
- **y-right (twin):** "Attentional Modulation (%)". Scale linear.
  **ylim = (0.0, 100.0)** (paper ticks: 0 at bottom, 100 at top).

## Binding qualitative claims (model curves only)

- Two solid CRFs (Ignored, Attended), both sigmoidal in log contrast, both
  normalized so the larger peak sits at 1.0.
- Attended curve is **left-shifted** of the Ignored curve (contrast gain); the
  two converge at high contrast.
- Dashed "% Attentional modulation" curve is **largest at low contrast** and
  **falls monotonically toward 0** at high contrast, staying within [0, 100].

## Not-reproduced inset elements

- The small RF (solid) / Attention-field (dashed) ring schematic inside the panel
  is a configuration inset, not model data — not reproduced.
