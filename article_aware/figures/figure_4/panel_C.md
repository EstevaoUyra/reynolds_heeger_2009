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
- **DR-4C-sign RESOLVED (code-resolvable, 2026-06-10; A-012) — NO genuine
  paper/code contradiction.** The apparent inconsistency was a DIGITIZER LABEL
  SWAP, not a paper defect. The author legend (Figure4C.m:69) is
  `'Att Away','Att RF'`, and the dashed modulation `100·(unattCRF-attCRF)/unattCRF`
  (line 74) is drawn POSITIVE in the published panel (~36% peak). For that to be
  positive, Att-Away (unattCRF) is the UPPER solid and Att-RF (attCRF, attend
  null-in-RF) is the LOWER — i.e. attending the null in the RF SUPPRESSES the
  recorded preferred neuron (C-021), and the published panel AGREES with the
  code. Recomputing the author dashed formula on the digitized curves with the
  corrected mapping reproduces the digitized % modulation pointwise. The model
  follows Figure4C.m and is correct. The digitized `panel_C_digitized.json`
  mislabeled the UPPER solid "attended" (it is the author's Att-Away/unattCRF);
  tier comparisons account for that swap.
