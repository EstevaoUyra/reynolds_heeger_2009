# Figure 4C direction-of-effect — escalation-ladder investigation

**Date:** 2026-06-03
**Model:** reynolds_heeger_2009
**Finding under investigation:** model's Fig 4C comes out the opposite sign from the
paper's 4C panel.
**Auditor posture:** report only; edited nothing.

---

## Verdict

**MIS-MAPPING-BUG (DIVERGENT, severity: critical).**

The R&H paper resolves the direction *within itself* — Fig 4C is **facilitation /
contrast gain / left-shift** (attend-nonpreferred-in-RF curve ABOVE attend-away). The
lineage (Martinez-Trujillo & Treue 2002 as cited by pestilli, ghose_maunsell_2008,
ni_maunsell_2017) is unanimous in the same direction. The model produces **suppression
/ right-shift** because its 4C attention condition is mapped as a *narrow feature-tuned
gain on the nonpreferred direction only* — which is the Fig **4E** mechanism (C-021),
not the Fig 4C recorded-neuron readout. This is a fixable condition/attention-field
mis-mapping, **not** a genuine paper issue. The wrong sign was then *laundered into the
spec* (pseudocode + tests rewritten to assert suppression, citing C-021).

This is a textbook Step-4 "laundered paper-contradiction": a test rewritten to assert
the **opposite** of the paper's stated direction because the faithful version was "not
buildable-to-green" (see SQ-004).

---

## Ladder Step 1 — Resolve from the R&H paper itself  → RESOLVES to facilitation

The paper is **not** ambiguous about 4C. Four independent in-paper signals agree the
attended (attend-nonpreferred-in-RF) curve is the **upper / left-shifted** one:

1. **Fig 4 caption, panel B (the empirical referent 4C reproduces)** —
   *"(B) Attention caused predominantly a change in **contrast gain**. Red curve … when
   attention was directed to the nonpreferred stimulus in the receptive field. Blue
   curve … when attending the opposite hemifield. Dashed gray curve, **percentage
   increase** in firing rate at each contrast."* (extracted_text.md:187)
   "Contrast gain" + "percentage increase" = leftward shift + positive modulation =
   **facilitation**. 4C is *"Model simulation exhibiting results similar to those
   observed experimentally."*

2. **The panel images themselves.**
   - `article_aware/figures/figure_4/panel_C.jpg` (paper's model panel): the upper
     solid CRF (attended) sits clearly **above** the lower (unattended); dashed
     %-modulation curve runs on the right axis from ~36 % at low contrast down toward 0
     — a *positive, declining* modulation.
   - `article_aware/figures/figure_4/panel_B.jpg` (M&T 2002 empirical data): the
     attend-nonpreferred curve is **left-shifted / above** attend-away.
   - `panel_C_digitized.json`: attended above unattended (~+0.10 gap mid-contrast),
     `percent_modulation` peaks **+36 %** at low contrast and declines — positive.

3. **C-019 (qualitative regime claim)** — *"Contrast gain regime predicts a **leftward
   shift** of the contrast-response function … with the largest percentage modulation
   at intermediate contrasts."* (citations.yaml C-019). The caption calls 4C "contrast
   gain"; contrast gain ⇒ leftward shift ⇒ facilitation.

**The lone dissenting passage is C-021's last clause** — *"Attending to nonpreferred
shifts the balance in favor of the nonpreferred stimulus, increasing its suppressive
effect and yielding a smaller output firing rate."* This passage is located in
*"Section: Attentional Modulation of the Contrast-Response Function with Two Stimuli"*
and describes the **general two-stimulus mechanism / Fig 4E** condition (attend
*preferred* vs attend *nonpreferred*, contrasts **covarying**, readout = the recorded
neuron). It is **not** a statement about the Fig 4C panel (attend-nonpreferred vs
attend-**away**, only the preferred contrast swept). The test/pseudocode mis-applied
4E's prose to 4C.

**Conclusion of Step 1:** the paper internally resolves to **facilitation** for 4C. The
single dissenting clause (C-021) is about a *different* panel (4E). No genuine
intra-paper contradiction → not a paper issue.

---

## The code mis-mapping (the locus of the bug)

`implementation/src/rh_model/protocols.py::run_figure_4C` (lines 208–216):

```python
stim = lambda c_pref: [
    {"x": 0.0, "theta": 0.0,   "contrast": c_pref},     # preferred (swept)
    {"x": 0.0, "theta": 180.0, "contrast": c_nonpref},  # nonpreferred (fixed)
]
attended   = lambda c_pref: {"spatial_center": 0.0, "feature_center": 180.0}
unattended = lambda c_pref: {"spatial_center": None, "feature_center": None}
```

Recorded neuron = `recorded_x=0.0, recorded_theta=0.0` (model.py:71-72,325-328) — i.e.
it prefers the **swept (θ=0) stimulus**. The condition *labels* are correct
(recorded-neuron preference, attended stimulus = nonpreferred-in-RF, unattended = away),
so this is **not** a label swap.

The defect is the **attention-field structure**: `feature_center=180.0` with
`feature_tuning_width=20°` builds a *narrowly feature-selective* gain on the
**nonpreferred direction only**. `build_attention_field` (model.py:166-201) multiplies
the stimulus drive by this field *before* the suppressive pool is computed, so the gain
lands almost entirely on the θ=180 population. That θ=180 boost (a) contributes **nothing**
to the θ=0 recorded-neuron numerator but (b) **adds to the suppressive drive** of the
θ=0 neuron → net **suppression**. That is precisely the C-021 / Fig-4E mechanism, applied
to the 4C panel.

**Measured model output (re-run 2026-06-03, `run_figure_4C()`):**

| contrast | attended | unattended | % mod |
|---|---|---|---|
| 0.010 | 0.081 | 0.125 | −35.2 |
| 0.139 | 0.734 | 0.953 | −23.0 |
| 1.000 | 1.595 | 1.714 | −7.0 |

mean % mod = **−23.4 %**, attended **below** unattended at every contrast (right-shift).
Opposite sign to the paper panel (+36 % peak, attended above).

**Diagnostic confirming the cause:** replacing the narrow feature-tuned field with a
*spatial location* attention field (`feature_center=None`, attend the RF location, which
boosts **both** colocated stimuli — the M&T-2002 spatial-attention task) flips the model
to **facilitation**: mean % mod = **+86 %**, attended above unattended at every contrast,
left-shift. So the sign is controlled entirely by the attention-field mapping, confirming
this is a mis-mapping rather than an equation/parameter defect.

### Corroborating laundering evidence (Step-4 pattern)

- `article_aware/pseudocode/figure_4_protocol.md` (lines 52-57) asserts, citing C-021,
  that 4C should produce *"a suppressive contrast-gain change. The attended curve is
  rightward-shifted relative to unattended (unattended curve is the higher one)…"* —
  i.e. the spec was written to the **inverted** direction.
- `extracted_data/test_figure_4C.py` `test_attending_nonpreferred_decreases_response`
  (Q-026, cites C-021) asserts `attended <= unattended` and
  `test_attended_crf_is_right_shifted` (Q-027) asserts the attended half-max is *larger*
  (right-shifted). Both encode the wrong sign.
- `logs/.../spec_questions.md` **SQ-004** documents the build fighting the model: the
  attend-nonpreferred CRF "never saturates and never recovers … directly contradicting
  the contrast-gain recovery/saturation the figure claims," forcing an unsanctioned
  per-protocol 75° suppressive-tuning override. That whole struggle exists only because
  the model was driven into the suppression regime; under the facilitation mapping it
  does not arise.

---

## Ladder Step 2 — Lineage cross-check (defensive; Step 1 already resolved it)

The task named `reynolds_chelazzi_desimone_1999`, which is **not present** in the corpus.
The available two-stimulus-attention siblings all corroborate **facilitation** for
attending the nonpreferred/null of two stimuli in the RF:

- **pestilli_ling_carrasco_2009** (extracted_text.md:793) — explicitly classifies the
  effect as *"…manifested by **contrast gain** (Martinez-Trujillo & Treue, 2002;
  Reynolds…)."* Contrast gain = leftward shift = facilitation.
- **ghose_maunsell_2008** (extracted_text.md:515-536, Fig 5/6) — measures
  *(Attend-In-**Null** Response / Attend-Out Response)*; the median modulation is
  *"significantly larger than 1"* with a multiplicative gain term *"significantly
  different from unity"* (>1). Attending the null/nonpreferred-in-RF **increases** the
  response.
- **ni_maunsell_2017** (extracted_text.md:208) — the canonical
  normalization-of-attention model: *"The β parameter multiplies **both the excitatory
  and suppressive drives of the attended stimulus**, regardless of whether it is the
  preferred or null stimulus."* Spatial attention to the in-RF (nonpreferred) stimulus
  raises the recorded neuron's response (their Fig 1D spatial-attention measurement).

No sibling supports the model's suppression direction for the 4C task. Lineage is
**unanimous: facilitation.**

---

## Exact spec-level fix (MIS-MAPPING-BUG)

The 4C "attend nonpreferred-in-RF" condition must be a **spatial** attention cue to the
in-RF location (the M&T-2002 task: attend that patch to detect a target), which boosts
the drives of **both** colocated stimuli — not a narrow feature gain isolated on the
nonpreferred direction. Concretely:

- In `run_figure_4C`, the `attended` condition should apply spatial gain at the RF
  (`spatial_center=0.0`) with an attention field whose feature coverage **includes the
  recorded neuron's preferred direction**, so the gain reaches the θ=0 stimulus drive
  (numerator), yielding contrast-gain facilitation. The minimal, mechanistically clean
  form is a spatial (location) attention field at the RF
  (`feature_center=None` → flat over θ), giving the paper's **+, declining %-modulation,
  left-shifted attended CRF**. (Diagnostic above: this produces facilitation.)
- If the Phase-A spec must retain Table-1's "tuning width = 20°" as a *feature*-tuned
  field, then the faithful reading is that the attended feature gain is centered such
  that it covers the recorded neuron's response to the **swept preferred** stimulus
  (the readout the panel plots), not isolated on θ=180 in a way that only feeds
  suppression. Either way the **sign must be facilitation** (attended above unattended;
  `percent_modulation` positive, peaking ~+36 % at low contrast and declining).
- Correspondingly: re-author `pseudocode/figure_4_protocol.md` lines 52-57 to the
  facilitation/contrast-gain direction, and re-author the inverted assertions in
  `test_figure_4C.py` (Q-026 `attended <= unattended`; Q-027 right-shift) to assert
  `attended >= unattended` / left-shift. C-021 should **not** be cited for 4C (it is the
  4E mechanism); cite the Fig-4 caption + C-019 (contrast-gain regime) instead.
- SQ-004's 75° suppressive-tuning override for 4C is a symptom of the wrong regime and
  should be revisited once the mapping is corrected.

These are spec/condition-mapping changes (and the dependent test/pseudocode re-author),
routed to the organizer/builder. The auditor edits nothing.

---

## Refute pass

- *"Maybe the panel was mis-digitized and the model's suppression is right."* Refuted: I
  read `panel_C.jpg` and `panel_B.jpg` directly — both show the attended curve above /
  left-shifted, with a *positive* declining %-modulation. The digitization matches the
  image.
- *"Maybe C-021 governs 4C and the panel is the outlier."* Refuted: C-021's section and
  content (attend preferred **vs** nonpreferred, covarying contrasts, "smaller output")
  describe Fig 4E, not 4C; the 4C caption independently says "contrast gain / percentage
  increase," and the lineage agrees with the panel.
- *"Maybe it's an equation or parameter error, not a mapping."* Refuted: the equations
  reproduce the paper's saturation/CRF shape elsewhere; the *only* thing that flips the
  4C sign is the attention-field mapping (spatial-location vs narrow-feature-on-θ=180),
  as the diagnostic re-run shows.

Finding **survives** refutation.
