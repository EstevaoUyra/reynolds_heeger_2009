# Faithfulness audit — improvement pass — reynolds_heeger_2009

- Date: 2026-06-03
- Role: post-build faithfulness auditor (report-only; edited no code/tests/contract; wrote no APPROVED)
- Standard: `paper/extracted_text.md` (Eqs 1–8, Table 1, verbatim captions) + paper panel JPGs `article_aware/figures/figure_<N>/panel_<X>.jpg` + the now-faithful digitized references `panel_<X>_digitized.json`
- Step 0 freshness: re-rendered ALL figures myself (`python -m rh_model.views`, exit 0); all 7 model PNGs + 6 reference PNGs regenerated. Judged the fresh renders.
- Builds on `audit-r2-2026-06-03.md`; **overturns one of its certifications** (Fig 4C direction) and **adds the headline normalization finding it missed**.

## Posture
Over-flagged by design. Two NEW high-leverage divergences the prior rounds missed or mis-certified, plus the standing magnitude concessions (already encoded as intended-failure tier tests). The core equation layer remains faithful.

---

## Equation & parameter layer — FAITHFUL (re-checked, not assumed)

Operator-by-operator against the paper:

| Paper eq | Code locus | Status |
|---|---|---|
| Eq.5 `R=⌊A·E/(S+σ)⌋_T` | `model.compute_output` / `stages/normalization.run` | FAITHFUL — A·E numerator, S+σ denom, half-wave rect T=0 |
| Eq.6 `S=s∗(A·E)` | `model.compute_suppressive_drive` | FAITHFUL — pools the product A·E; sep. x (zero-pad) + θ (circular, A-011) |
| Eq.2 `∫s dxdθ=1` | `model.build_suppressive_kernel` | FAITHFUL — each 1D factor `/(sum*d)` |
| Eq.7 contrast-gain (γ scales A·E in num+denom S) | full sim path | FAITHFUL — γ enters via A multiplying E before pooling |
| E (A-009), A=1+(γ−1)·G | `build_stimulus_drive`, `build_attention_field` | FAITHFUL to adopted assumptions |
| Eqs.3/4/8 closed forms (β; A-010) | not on sim path | OK |

Ledgers: spec-side `audited:true` entries all carry verbatim Table-1 `quote:` strings; σ/α/T/β/fixed-sweep-contrasts honestly `audited:false`. Impl-side 1D knobs honestly `audited:false` (SQ-001/002/004, A-006). No mis-transcription, no missing term, no wrong pool. This layer is not the problem.

---

## FINDING 1 — Per-pair-to-1.0 normalization erases the paper's response-gain claim (and corrupts the reference render) — **DIVERGENT, IMPLEMENTATION-BUG, MAJOR, OPEN**

**The single highest-leverage finding.** This is the normalization-convention defect the brief predicted.

**Paper convention (from the digitized references, which are the trustworthy quantitative stand-in):**
- `panel_A_digitized.json`: 2A attended & unattended both plateau **~0.615** on the left axis. Description: *"Shared scale with 2B (do NOT renormalize to 1.0)."*
- `panel_B_digitized.json`: 2B attended plateaus **~0.85**, unattended ~0.60. Description: *"2B's attended plateau (~0.85) is HIGHER than 2A's (~0.62) — that height difference is the figure's scientific claim."*

So Fig 2 lives on **one shared sub-1.0 axis**: response gain (2B) *lifts the ceiling* above the contrast-gain panel (2A). That ceiling difference is the entire point of the A-vs-B comparison.

**What the code does** — `views._normalized_pair` (views.py:210-218) and its mirror `rh_tier_helpers.norm_pair` (line 97-102): `scale = max(attended.max(), unattended.max())`, divide each pair by it. Every CRF panel is independently pinned so its top curve = 1.0.

**Measured corruption (verified):**
| | model raw max | view-rendered plateau (last point) |
|---|---|---|
| 2A attended | 1.247 | **1.000** |
| 2B attended | 3.161 | **1.000** |

The model's RAW output *correctly produces the claim* — 2B (3.16) sits far above 2A (1.25). The view then divides it away: both panels top out at 1.0, so the 2B>2A ceiling claim is **invisible in the rendered figure**.

**It also corrupts the digitized-reference render** (the supposed trustworthy stand-in). `render_figure_2_reference` feeds the shared-scale digitized curves (2A=0.615, 2B=0.85) through the SAME `_normalized_pair`, so the *reference* PNG also shows 2A→1.0 and 2B→0.99 — the reference figure contradicts its own JSON. Verified: rendered reference 2A plateau=1.000, 2B plateau=0.993, while the JSON says 0.615 / 0.852.

Same class affects **Fig 4C/4E** (each panel pinned to its own attended max, losing the absolute-scale comparison) and any cross-panel CRF claim.

**Why the tests never caught it:** the tier harness compares `norm_pair(model)` (renormalized to 1.0) against `ref_value_at(...)` which reads the digitized JSON **un-renormalized** (shared sub-1.0). The Fig-2 tier tests then only assert *separations* (att−una) and a couple of mid-point soft values — partly scale-invariant — so the cross-panel ceiling claim is structurally untestable. The bug is symmetric on both sides of the per-panel comparison, hiding it.

**Spec-level fix (paper-blind, for Phase B):** the Fig 2 (and 3/4 CRF) model panels must be drawn on a **single shared response scale across the panel group**, not per-pair-to-1.0. Concretely: normalize all CRF curves in a figure-group by **one common scale** (e.g. a fixed reference response, or the max across *all* panels in the group), so that 2B's attended ceiling renders visibly above 2A's. The digitized references on the shared sub-1.0 scale (0.615 vs 0.85) are the target. The same shared-scale rule must be applied to the reference render so reference and model line up. Do NOT pin each pair independently to 1.0. (Tuning panels 5/6/7 use shared-peak-within-panel via `_plot_tuning`/`norm_curves`, which is correct and unaffected.)

---

## FINDING 2 — Figure 4C reproduces the OPPOSITE sign from the paper's 4C panel (suppression vs facilitation), laundered into test Q-026 — **DIVERGENT, SUSPECTED-PAPER-ISSUE / condition-mapping, MAJOR, OPEN**

**Overturns `audit-r2`**, which certified 4C's direction as "the paper's stated direction." It is not — it is the inverse of the paper's 4C *panel*.

**Paper Fig 4C** (Martinez-Trujillo & Treue 2002; recorded neuron, preferred-stimulus contrast swept, nonpreferred fixed, attention to nonpreferred-in-RF vs opposite hemifield):
- Caption: *"Attention caused predominantly a change in **contrast gain**"*; 4C *"Model simulation exhibiting results **similar to those observed experimentally**"* (i.e. similar to 4B, which is facilitation).
- Paper JPG `panel_C.jpg` + `panel_C_digitized.json`: the **attended** (attend-nonpref-in-RF) solid CRF sits **ABOVE** the unattended (attend-away); attended saturates ~0.80, unattended ~0.77; dashed %-modulation is **POSITIVE**, peaking ~36% at low contrast (a leftward contrast-gain shift / facilitation).

**Implementation Fig 4C** (verified `run_figure_4C`): attended_CRF max **1.595** vs unattended_CRF max **1.714** — attended is **BELOW** unattended at every contrast; mean percent_modulation **−23.6%** (suppression). The rendered panel shows "attend nonpreferred" ~21% under "attend away" at mid-contrast. **Opposite sign from the paper panel.**

**The laundering:** `test_figure_4C.py::test_attending_nonpreferred_decreases_response` (Q-026) asserts `attended <= unattended` and `percent_modulation <= 0` — i.e. it asserts the *suppression* direction, and `test_attended_crf_is_right_shifted` (Q-027) asserts a **right**-shift (the paper's 4C is a **left**-shift). It cites C-021, but C-021 is the paper's **mechanism prose** — *"Attending to nonpreferred shifts the balance in favor of the nonpreferred stimulus … yielding a smaller output firing rate"* — which describes the readout of the **preferred** stimulus's drive, NOT the Fig-4C recorded-neuron measurement the panel plots. The test operationalizes the prose against the panel and gets the sign backwards relative to the figure.

This is the Step-4 laundered-contradiction pattern: a test rewritten to assert the panel-contradicting direction, justified by a paper passage that is about a *different* quantity, against the model's own synthetic output.

**Classification:** This is NOT a "tune a knob to flip the sign" target. Either (a) the model + the spec's condition mapping faithfully implement what the paper's *prose* says and the paper's own 4C *panel* disagrees with its prose (a genuine **SUSPECTED-PAPER-ISSUE**, a first-class finding for the human — "the paper's 4C panel and its mechanism text point in opposite directions"), or (b) the condition mapping for 4C is mis-specified (e.g. which stimulus is "recorded preferred" vs which is attended, or the readout neuron's preference) such that the model measures the suppression of the wrong cell. Phase B / the human must disposition which; do not silently re-green by flipping a threshold. At minimum, Q-026/Q-027's citation of C-021 as if it licenses the suppression+right-shift direction **for the 4C panel** is a faithfulness defect — the panel (digitized + JPG) is the binding referent and shows facilitation + left-shift.

---

## FINDING 3 — Figure 6C feature-based sharpening is present but far too weak — **GENUINE-DIVERGENCE, MINOR, already red (tier test), not a fix target**

Paper 6C: feature-based attention **sharpens** (narrows) direction tuning — a clearly visible narrowing, with attend-contralateral (feature-matched) ALSO scaled relative to attend-fixation.
Model (verified): FWHM 143.0° (attend-fixation) → 133.1° (attend-opposite) — only **~7% narrowing**; peak ratio 1.009 (essentially no scaling). The narrowing is in the right *direction* but visually negligible (the rendered curves nearly overlap).

Already caught by `test_tier_figure_6.py::test_6C_sharpening_present_at_peak` and `test_6C_peak_ratio_matches_digitized` (both RED, intended). This is a faithful-build-misses-figure result with the **cited** Table-1 params (stim 10, attn 30, γ2, tuning 60°). Correctly NOT tuned. Finding/record-it, don't fix.

---

## FINDING 4 — Figure 7C / 5C peak-ratio magnitudes off — **GENUINE-DIVERGENCE, MINOR, already red, not a fix target**

- 7C: attend-variable peak is **3.28×** fixation vs the paper/digitized **~1.4×** (`test_tier_figure_7.py` RED). Ordering (variable > fixation > nonpreferred) and the preferred-direction peak are faithful; only the magnitude is exaggerated.
- 5C: `test_5C_peak_ratio_matches_digitized` RED — multiplicative-scaling *shape* is faithful (clean scaled Gaussian, no width change), peak ratio magnitude off.

Both are honest intended-failure tier tests against the digitized references. Faithful direction, divergent magnitude with cited params. Record, don't tune.

---

## FINDING 5 — Figure 4E %-modulation overflows the paper's (0,100) axis — **GENUINE-DIVERGENCE, MINOR, already red & intentionally surfaced**

Paper 4E dashed %-modulation stays within 0–100 (~54%→~36%). Model overshoots to ~300–400%. Already pinned to the paper axis (overflow visible) and asserted by `test_panel_axes.py::test_figure_4E_modulation_within_paper_axis` + `test_tier_figure_4.py` (RED, intended per panel_E.md). Honestly surfaced; not a fix target.

---

## FINDING 6 — `model.normalization_variant: audited:true` without a `quote:` — **process nit, MINOR, not paper-distance**

Impl ledger. It is a categorical stage selector, not a paper value, so it cannot carry a paper quote; `audited:true` is arguably wrong-field-usage but not a faithfulness defect. Noted, not open. (Same as r2.)

---

## Things checked and found FAITHFUL (demonstrated, not assumed)
- Fig 1 schematic (A-006 1D): E×A÷S→R structure correct; output enhances the attended (right) stimulus. FAITHFUL (schematic).
- Fig 2A contrast-gain *signature* (curves converge at high c, %-mod falls to ~0) and Fig 2B response-gain *signature* (sustained separation) — both correct **in separation terms**; it is only the absolute-ceiling cross-panel claim that Finding 1 destroys.
- Fig 3C/3F: 3C %-mod peaks low & converges; 3F sustained with largest absolute gap at high c; both carry the dashed twin axis. FAITHFUL (qualitative).
- Fig 5C multiplicative scaling: clean scaled Gaussian, no width change. FAITHFUL (shape; magnitude per Finding 4).
- Fig 4E ordering: attend-pref multiplicatively above attend-nonpref. FAITHFUL (ordering).
- Eq layer, kernel normalization, ledger quotes: FAITHFUL.
- No result-bearing frozen-fit stub (every figure is a live `protocols→measurements→views` compute).
- `identity_suppression` variant is a config-only smoke-test path, off the default. FAITHFUL.

---

## Findings table (ranked)

| # | Ref | Status | Class | Severity | Open? | Locus |
|---|---|---|---|---|---|---|
| 1 | Per-pair→1.0 normalization erases 2B>2A ceiling; corrupts reference render | DIVERGENT | IMPLEMENTATION-BUG | **MAJOR** | **yes** | `views._normalized_pair` (views.py:210); `rh_tier_helpers.norm_pair` |
| 2 | Fig 4C sign inversion (suppression vs paper-panel facilitation), laundered into Q-026/Q-027 | DIVERGENT | SUSPECTED-PAPER-ISSUE / condition-mapping | **MAJOR** | **yes** | `run_figure_4C` + `test_figure_4C.py` Q-026/Q-027; vs `panel_C_digitized.json` |
| 3 | Fig 6C sharpening ~7% (too weak) | DIVERGENT | GENUINE-DIVERGENCE | minor | yes (red) | cited params; `test_tier_figure_6.py` |
| 4 | Fig 7C 3.3× / 5C peak ratios off | DIVERGENT | GENUINE-DIVERGENCE | minor | yes (red) | cited params; `test_tier_figure_5/7.py` |
| 5 | Fig 4E %-mod overflow >100 | DIVERGENT | GENUINE-DIVERGENCE | minor | yes (red, intended) | `panel_E.md`; `test_panel_axes.py` |
| 6 | `normalization_variant audited:true` no quote | (process nit) | — | minor | no | impl ledger |
| — | Eqs 5/6/2/7, kernel, stimulus/attention construction, ledger quotes, Figs 1/3/5-shape | FAITHFUL | — | — | no | — |

**Overall: has-divergences.** Two MAJOR open findings (1 IMPLEMENTATION-BUG in the view/measurement normalization, 1 SUSPECTED-PAPER-ISSUE/condition-mapping needing human disposition). The equation core is faithful; the divergences are in **presentation normalization** and in a **laundered direction-of-effect** — exactly the two classes this role exists to catch.
