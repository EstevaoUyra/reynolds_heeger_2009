# Figure 4 — Panel C (MODEL, reproduced)

**Role:** Model CRF panel — authors' Figure4C.m (CODE-018). Four separated
stimuli; the recorded preferred (θ=0) neuron is probed while attention is on the
NULL/nonpreferred (θ=180°) stimulus, either in the RF or contralateral.
Preferred-stimulus contrast swept.
**Reproduced:** yes (model panel).

## Axis limits

- **x:** Log Contrast. Scale **log**. Model sweep = the authors' Figure4C.m
  cRange ∈ [1e-4, 0.1] (the published panel has no numeric x ticks);
  `xlim = (1e-4, 0.1)`.
- **y-left:** "Normalized Response". Linear. **ylim = (0.0, 1.0)**.
- **y-right (twin):** "Attentional Modulation (%)". Linear. **ylim = (0.0, 100.0)**.

## Binding qualitative claims (model curves only)

- Two solid CRFs, both sigmoidal, rendered on the **Figure-4 shared response
  scale** (with 4E; NOT per-pair-renormalized to 1.0 — see
  `model_spec.yaml rendering_conventions.crf_shared_response_scale`).
- **Suppression (authors' Figure4C.m, CODE-018; C-021):** attending the NULL
  stimulus in the RF (`attended_CRF`) SUPPRESSES the recorded preferred neuron —
  it sits **BELOW** attend-away (`unattended_CRF`), because the boosted θ=180°
  population feeds only the recorded θ=0 neuron's suppressive pool (C-021:
  attending the nonpreferred "increasing its suppressive effect and yielding a
  smaller output firing rate"). The gap is largest at low/mid contrast and
  narrows toward the high-contrast plateau.
- Dashed "% Attentional modulation" = `100·(unattended-attended)/unattended`
  (suppression sign) is **positive**, peaks ~38% at low contrast and **declines**
  toward high contrast (matching the digitized panel_C %-modulation, ~36%),
  staying within [0, 100].
- **PAPER/CODE INCONSISTENCY (DR-4C-sign, A-012):** the *published* Figure 4
  panel C DRAWS the attend-nonpref-in-RF curve ABOVE attend-away and labels the
  dashed curve a "percentage INCREASE" (caption B/C, C-015) — i.e. facilitation —
  the OPPOSITE curve order/sign to the authors' released Figure4C.m and to C-021.
  We follow the released CODE + C-021 (suppression). This is a documented paper
  defect, owned by human decision-request DR-4C-sign, not a model fault. The
  digitized `panel_C_digitized.json` traced the UPPER solid as "attended"
  (published-panel convention), SWAPPED relative to this code convention — tier
  comparisons account for the swap.
