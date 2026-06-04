# Figure 4 Protocol — Two Stimuli in RF, Attention by Direction

## Purpose
Show that the same model produces (4C) contrast-gain-like and (4E)
response-gain-like attentional modulation depending on which stimulus is
attended and how stimulus contrasts are configured.

## Inputs
- **FOUR separated stimuli** (authors' Figure4C.m, CODE-018). The recorded MT
  neuron prefers θ = 0 and its RF is centred at **x = 100** (= round(mean of the
  two RF-stimulus positions, 90 and 110)):
  - x = 90,  θ = 0   — "Preferred" stimulus in the RF (contrast c_pref, swept).
  - x = 110, θ = 180 — "Nonpreferred/null" stimulus in the RF (contrast fixed 0.01).
  - x = -90, θ = 0   — preferred stimulus in the opposite hemifield (swept).
  - x = -110,θ = 180 — null stimulus in the opposite hemifield (fixed 0.01).
- Per protocol:
  - 4C: contrast of the preferred stimulus c_pref varied; the null contrast
    fixed at 0.01. Two attention conditions, BOTH attending the NULL stimulus:
    attend null-in-RF vs attend null contralateral (opposite hemifield).
  - 4E: two stimuli colocated in RF, contrasts covary (c_pref = c_nonpref = c).
    Two attention conditions: attend preferred vs attend nonpreferred.
- Parameters: stimulus_size = 5, attention_field_size = 5, tuning_width
  (AthetaWidth) = 20°, γ (Apeak) = 5.

## Sweep
- 4C: c_pref logarithmically across **[1e-4, 0.1]** with 8 points (Figure4C.m
  cRange); null contrast fixed = 0.01.
- 4E: c logarithmically across [0.01, 1] with 8 points (covaried).

## Procedure (4C)

> **AUTHORS' Figure4C.m (CODE-018) — the authoritative 4C contract.** This is the
> Martinez-Trujillo & Treue (2002) "attend the NULL stimulus" task as the authors
> actually simulated it. The recorded neuron PREFERS θ = 0. Both conditions attend
> the **nonpreferred (θ = 180°) stimulus** via an **OVAL** attention field — a
> spatial Gaussian centred on the null stimulus (Ax = 110 for "in RF", Ax = -110
> for "contralateral") **times a θ = 180° feature Gaussian** (Atheta = 180,
> AthetaWidth = 20°). Attending the null boosts the θ = 180° population, which
> feeds ONLY the recorded θ = 0 neuron's **suppressive** pool, so attend-null-in-RF
> **LOWERS** its response → the attended (in-RF) CRF sits **BELOW** the attend-away
> CRF, a **suppression** (C-021). The authors report the modulation as the
> **suppression magnitude** `100·(unattended-attended)/unattended` — positive,
> peaking ~36% at low contrast and declining toward saturation.
>
> **PAPER/CODE SIGN INCONSISTENCY (DR-4C-sign, A-012).** The *published* Figure 4
> panel C draws the attend-nonpref-in-RF curve ABOVE attend-away and labels the
> dashed curve a "percentage INCREASE" (caption B/C). We follow the released
> CODE + C-021 (suppression). This is a documented paper defect, not a model
> fault; the human decision-request DR-4C-sign owns the convention call. The
> digitized panel_C JSON labels the UPPER solid "attended" (the published-panel
> convention), which is SWAPPED relative to this code convention.

For each (c_pref, attention_condition):
1. Construct E(x, θ) from the four stimuli above (preferred θ = 0 at contrast
   c_pref in both hemifields; null θ = 180° at contrast 0.01 in both hemifields).
2. Construct A(x, θ): an OVAL field — spatial Gaussian (σ_x = attention_field_size)
   centred on the null stimulus, times a θ = 180° feature Gaussian
   (σ_θ = tuning_width = 20°). "Attend null-in-RF": spatial centre x = 110.
   "Attend null contralateral": spatial centre x = -110.
3. Compute S, R per EQ-6, EQ-5.
4. Record R(x = 100, θ = 0) — the recorded preferred neuron at the RF centre.

## Procedure (4E)
For each (c, attention_condition):
1. Construct E(x, θ) with both stimuli at contrast c.
2. Construct A(x, θ): Gaussian centered at x = 0; feature-selective for
   θ = 0 ("attend preferred") OR θ = 180° ("attend nonpreferred"), σ_θ =
   tuning_width.
3. Compute S, R as above; record R(x = 0, θ = 0).

## Outputs
- 4C: attended_CRF[c_pref] (= attend null-in-RF), unattended_CRF[c_pref]
  (= attend null contralateral), percent_modulation[c_pref]
  (= 100·(unattended-attended)/unattended, the suppression sign).
- 4E: attend_pref_CRF[c], attend_nonpref_CRF[c], ratio[c] =
  attend_pref / attend_nonpref.

## Expected behavior (citations)
- C-015, C-021, CODE-018 / 4C: attending the **nonpreferred (null) stimulus in
  the RF SUPPRESSES** the recorded preferred neuron — the attended (in-RF) CRF
  sits **BELOW** the attend-away CRF (C-021: attending the nonpreferred
  "increasing its suppressive effect and yielding a smaller output firing rate").
  The suppression **percent modulation** `100·(unatt-att)/unatt` is **positive**,
  largest (~36%) at low contrast and **declining** toward high contrast.
  Verified: the author Figure4C.m configuration through rh_model.simulate gives a
  %-mod peak ~38%, matching the digitized panel_C %-modulation (~36%).
  **PAPER/CODE inconsistency (DR-4C-sign):** the published panel draws this the
  opposite way (attended above, "percentage increase"); we follow the released
  code + C-021. The digitized JSON's solid-curve labels (attended = upper) are
  swapped relative to this convention.
- C-015, C-021 / 4E: attending preferred yields larger response than
  attending nonpreferred across the full contrast range; the difference is
  approximately a multiplicative scaling (response gain).
