# Figure 3 — Panel F (MODEL, reproduced)

**Role:** Model CRF panel — spatial attention, smaller attention field (row 2),
title "Mixed Attention Effect".
**Reproduced:** yes (model panel).

## Axis limits (read from the paper figure_3.jpg)

- **x:** Log Contrast. Scale **log**. Model sweep contrast ∈ [1e-5, 1.0];
  `xlim = (1e-5, 1.0)` — the author Figure3F.m `cRange = [1e-5 1]` (CODE-020),
  not the prior guessed [0.01, 1].
- **y-left:** "Normalized Model Response". Linear. **ylim = (0.0, 1.0)**.
- **y-right (twin):** "Attentional Modulation (%)". Linear. **ylim = (0.0, 100.0)**.

## Binding qualitative claims (model curves only)

- Two solid CRFs (attend-in-RF vs attend-contralateral), both sigmoidal, peak
  normalized to 1.0.
- Dashed "% Attentional modulation" curve is **largest at low contrast** and
  declines toward high contrast (contrast-gain-weighted), within [0, 100].
