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
  - 4E: **FOUR separated stimuli** (authors' Figure4E.m, CODE-018) — the SAME
    four-stimulus layout as 4C (RF pair at x=90 θ=0 / x=110 θ=180; contralateral
    pair at x=-90 θ=0 / x=-110 θ=180), recorded neuron RF at x=100. ALL FOUR
    contrasts covary together (`stim = c·(stim1+stim2+stim3+stim4)`; the null is
    NOT held fixed here, unlike 4C). Two attention conditions: attend preferred
    (Ax=90, Atheta=0) vs attend nonpreferred (Ax=110, Atheta=180).
- Parameters: stimulus_size = 5, attention_field_size = 5, tuning_width
  (AthetaWidth) = 20°, γ (Apeak) = 5.

## Sweep
- 4C: c_pref logarithmically across **[1e-4, 0.1]** with 8 points (Figure4C.m
  cRange); null contrast fixed = 0.01.
- 4E: c logarithmically across **[1e-4, 0.1]** with 8 points (Figure4E.m cRange,
  CODE-020); all four stimulus contrasts covaried.

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
> **DR-4C-sign — RESOLVED (code-resolvable, 2026-06-10). NO genuine paper/code
> contradiction.** The apparent contradiction was a DIGITIZER LABEL SWAP, not a
> paper defect. The author legend (Figure4C.m:69) is `'Att Away','Att RF'`:
> `unattCRF` = Att-Away (Ax=-110, contralateral), `attCRF` = Att-RF (Ax=110,
> attend null-in-RF). The dashed modulation is `100·(unattCRF-attCRF)/unattCRF`
> (Figure4C.m:74) and the published panel draws it POSITIVE (~36% peak,
> declining). For that to be positive, **Att-Away (unattCRF) must be the UPPER
> solid and Att-RF (attCRF) the LOWER** — i.e. attending the null in the RF
> SUPPRESSES the recorded preferred neuron. The published panel's upper solid is
> therefore the *contralateral/unattended* condition, NOT "attended". The
> digitizer mislabeled the upper solid "attended"; recomputing the author dashed
> formula with the CORRECTED mapping (upper=unattCRF, lower=attCRF) reproduces
> the digitized % modulation pointwise (~29–30% mid-range, declining), confirming
> the published panel and Figure4C.m AGREE. The model already follows the author
> code, so it is correct. (The empirical Fig-4B caption's "percentage increase"
> describes the Reynolds/Martinez-Trujillo data panel; the author MODEL panel C
> code is the authoritative spec source for the model and is internally
> consistent.) `panel_C_digitized.json`'s solid labels remain on the published
> convention and are SWAPPED relative to the author legend — tier comparisons
> account for the swap.

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

> **AUTHORS' Figure4E.m (CODE-018) — the authoritative 4E contract.** FOUR
> SEPARATED stimuli, NOT two co-located at x=0. Co-locating two stimuli at x=0
> lets feature competition crush the nonpreferred response and inflates the
> %-modulation to ~386%; the author's four-separated geometry through the
> committed `simulate` yields ~52%, matching the digitized ~54%
> (faithfulness_audit Finding B). All four contrasts covary (the "yoked
> contrast experiment").

For each (c, attention_condition):
1. Construct E(x, θ) from the FOUR stimuli, ALL at contrast c (covaried):
   preferred θ=0 at x=90 and x=-90; nonpreferred θ=180° at x=110 and x=-110.
   (`stim = c·(stim1 + stim2 + stim3 + stim4)`.)
2. Construct A(x, θ): an OVAL field — spatial Gaussian (σ_x = attention_field_size
   = 5) centred on the attended in-RF stimulus, times a feature Gaussian
   (σ_θ = tuning_width = 20°):
   - "Attend preferred": spatial centre x = 90, feature centre θ = 0.
   - "Attend nonpreferred": spatial centre x = 110, feature centre θ = 180°.
3. Compute S, R per EQ-6, EQ-5; record R(x = 100, θ = 0) — the recorded
   preferred neuron at the RF centre (= round(mean(90,110))).

## Outputs
- 4C: attended_CRF[c_pref] (= attend null-in-RF), unattended_CRF[c_pref]
  (= attend null contralateral), percent_modulation[c_pref]
  (= 100·(unattended-attended)/unattended, the suppression sign).
- 4E: attend_pref_CRF[c], attend_nonpref_CRF[c],
  ratio[c] (= attend_pref / attend_nonpref, the response-gain ratio),
  percent_modulation[c] (= 100·(attend_pref - attend_nonpref)/attend_nonpref,
  the author Figure4E.m:71 form — the curve the panel actually plots).

## Expected behavior (citations)
- C-015, C-021, CODE-018 / 4C: attending the **nonpreferred (null) stimulus in
  the RF SUPPRESSES** the recorded preferred neuron — the attended (in-RF) CRF
  sits **BELOW** the attend-away CRF (C-021: attending the nonpreferred
  "increasing its suppressive effect and yielding a smaller output firing rate").
  The suppression **percent modulation** `100·(unatt-att)/unatt` is **positive**,
  largest (~36%) at low contrast and **declining** toward high contrast.
  Verified: the author Figure4C.m configuration through rh_model.simulate gives a
  %-mod peak ~38%, matching the digitized panel_C %-modulation (~36%).
  **DR-4C-sign RESOLVED (code-resolvable):** no genuine paper/code contradiction —
  the published dashed % modulation is positive (~36%) and matches the author
  `100·(unattCRF-attCRF)/unattCRF` once the digitizer's solid-curve label swap is
  corrected (the published UPPER solid is the author's "Att Away"/unattCRF, the
  LOWER is "Att RF"/attCRF). The model follows the author code and is correct.
- C-015, C-021 / 4E: attending preferred yields larger response than
  attending nonpreferred across the full contrast range; the difference is
  approximately a multiplicative scaling (response gain). With the author's
  FOUR-separated geometry (CODE-018), the %-modulation
  `100·(attend_pref-attend_nonpref)/attend_nonpref` peaks ~52% (matching the
  digitized ~54%, faithfulness_audit Finding B) and stays within the paper's
  0–100 axis — NOT the ~386% that the prior two-co-located-stimulus geometry
  produced.
