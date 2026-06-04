# Figure 3 — Panel C (MODEL, reproduced)

**Role:** Model CRF panel — spatial attention, single stimulus in RF (row 1),
title "Mixed Attention Effect".
**Reproduced:** yes (model panel).

## Axis limits (read from the paper figure_3.jpg)

- **x:** Log Contrast. Scale **log**. Model sweep contrast ∈ [1e-5, 1.0];
  `xlim = (1e-5, 1.0)` — the author Figure3C.m `cRange = [1e-5 1]` (CODE-020),
  not the prior guessed [0.01, 1].
- **y-left:** "Normalized Model Response". Linear. **ylim = (0.0, 1.0)**
  (paper ticks 0..1).
- **y-right (twin):** "Attentional Modulation (%)". Linear. **ylim = (0.0, 100.0)**.

## Binding qualitative claims (model curves only)

- Two solid CRFs (attend-in-RF vs attend-contralateral), both sigmoidal, peak
  normalized to 1.0; modest separation (a "mixed" contrast+response effect).
- Dashed "% Attentional modulation" curve has an interior bump at intermediate
  contrast then declines, staying within [0, 100].
