# Figure 4 — Panel E (MODEL, reproduced) — KNOWN DIVERGENCE

**Role:** Model CRF panel — two stimuli colocated in RF, contrasts covary;
attend preferred vs attend nonpreferred. This is the panel where attending the
preferred stimulus **scales up** the response (a response-gain-like effect).
**Reproduced:** yes (model panel).

## Axis limits (read from the paper figure_4.jpg)

- **x:** Log Contrast. Scale **log**. Model sweep contrast ∈ [0.01, 1.0];
  `xlim = (0.01, 1.0)`.
- **y-left:** "Normalized Response". Linear. **ylim = (0.0, 1.0)**.
- **y-right (twin):** "Attentional Modulation (%)". Linear. **ylim = (0.0, 100.0)**.
  The paper's right axis runs 0 (bottom) to 100 (top) — same as every other model
  panel in Figs 2/3/4.

## Binding qualitative claims (model curves only)

- Two solid CRFs (attend-preferred above attend-nonpreferred), both sigmoidal,
  peak normalized to 1.0.
- Dashed "% Attentional modulation" curve in the paper stays within **[0, 100]**.

## ⚠️ Known divergence (intended FAILURE under pinned axes)

The current model reproduction computes a percent-attentional-modulation curve for
4E (= 100·(attend_pref − attend_nonpref)/attend_nonpref) whose magnitude **exceeds
100%** — it peaks at roughly 300–400%. Previously the view auto-scaled the right
axis up to ~400 to keep this curve "fully visible", silently hiding the divergence.

Under this panel's **paper-pinned** right axis `(0, 100)` with autoscale OFF, the
4E modulation curve **overflows the axis**, and the data-within-axis test
`test_figure_4E_modulation_within_paper_axis` **FAILS by design**. That failure is
the *intended, successful* outcome: the magnitude divergence from the paper is now
a visible, deterministic RED instead of a hidden auto-rescale. Do NOT "fix" it by
re-scaling the axis or clipping the curve.
