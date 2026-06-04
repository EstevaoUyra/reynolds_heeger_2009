# Faithfulness audit — independent re-render — reynolds_heeger_2009 (2026-06-03)

- Role: post-build faithfulness auditor (report-only; edited no model/test/calibration/contract).
- Step 0: re-rendered all 7 model figures + 6 references myself via `python -m rh_model.views`
  (exit 0) inside the project `.venv`. Judged the fresh PNGs in `implementation/figure_outputs/`.
- Standard: `paper/extracted_text.md` (Eqs 1–8, Table 1, verbatim captions) + paper panel JPGs
  + `article_aware/figures/figure_<N>/panel_<X>_digitized.json` as the quantitative stand-in.
- Tests: 11 failed / 100 passed / 15 xfailed / 4 xpassed. Every red corresponds to a documented
  magnitude divergence; none asserts a paper-contradicting direction (no laundering).

## Equation & parameter layer — FAITHFUL
Operator-by-operator: Eq.5 `R=⌊A·E/(S+σ)⌋_T` (`model.compute_output` / `stages/normalization`),
Eq.6 `S=s∗(A·E)` (`compute_suppressive_drive`, pools the product A·E), Eq.2 `∫s=1`
(`build_suppressive_kernel`), `A=1+(γ−1)·G_x·G_θ` (`build_attention_field`). Table-1 sizes/γ in
`article_aware/spec/calibration.yaml` match the paper rows verbatim (audited:true with quotes).
Fig-1 schematic faithful (E×A÷S→R; attended/right stimulus enhanced).

## Structural root cause — CONTRACT_BUG
A-006 reduces space to **1D** (paper field is 2D). A 1D integral-normalized suppressive Gaussian
yields S ≪ A·E, so the CRFs do not saturate. The contract patches this with **per-panel
implementation-side knobs** — `suppressive_drive_gain` (4→12 for 2A, 6 for 2B, 8 for 3C/4C/4E,
12 for 3F), `suppressive_spatial_sigma_scale`, `baseline_modulated/unmodulated` — explicitly
**tuned to the paper's qualitative shape** (SQ-001/SQ-002), and SQ-001's note records *tests being
relaxed/tightened* to match (2A %-mod peak test relaxed to allow peak==0; saturation bounds
re-set so gain=4 fails and the tuned gain passes). The paper has ONE model, ONE σ, and only the
Table-1 field sizes — no per-panel suppression-gain. These knobs are the common Phase-A/contract
origin of the magnitude divergences below. Disclosed as audited:false (honest containment) but
**unbounded and figure-fitted** — a faithfulness hole for a normalization model whose magnitudes
*are* the claim. Spec-level fix: implement the 2D spatial field (retire A-006 for Figs 2–7) so a
single normalized suppressive field reproduces the magnitudes, OR promote one consistent
suppression normalization to the paper-derived ledger and require it to hold across all panels.

## Per-figure divergences (faithful direction, divergent magnitude/shape) — GENUINE
- 2A under-saturation: model attended plateau 0.338 vs digitized 0.615 (raw 2A 1.247 / 2B 3.161
  = 0.39; the 1D per-panel gains give 2A and 2B different ceilings, but the paper has both ~0.6–0.86).
- 3C %-mod: model 35%→5% (no clear interior bump) vs digitized 8%→bump→1.5%. 3F %-mod: model 41%→18%
  vs digitized 90%→20% (model far too muted at low contrast).
- 4C: %-mod +101% vs digitized ~34%; att/unatt 2.91/1.93 at c=1 (gap ~50% of unatt) vs digitized
  near-coincident 0.81/0.77. %-mod overflows the paper's 0–100 axis. Direction now FAITHFUL (A-012).
- 4E: %-mod ~310–390% vs paper ~36–54%; overflows 0–100 axis. Ordering faithful.
- 5C: attended/unattended peak ratio 1.59 vs digitized 0.968/0.837 = 1.16. Multiplicative, same width
  (faithful kind), gain too strong.
- 6C: feature sharpening near-absent — attend/fix peak ratio 1.009 (digitized 1.11), FWHM 133 vs 143
  (~7% narrowing). Right direction, far too weak.
- 7C: attend-variable/fixation peak ratio 3.28 vs digitized 1.002/0.756 = 1.33. Ordering faithful,
  gain ~2.5× too strong; fixation/nonpref crushed.

## De-laundering confirmed
4C's prior suppression-sign laundering (SQ-004 75° override + C-021 mis-map) is genuinely retired:
the 4C field is now spatial/flat-over-θ (A-012), producing facilitation matching the paper panel.
Verified by diff of the protocol and absence of the override in calibration. Direction FAITHFUL.

## Verdict
partial — equations + Fig 1 FAITHFUL; Figs 2–7 carry genuine magnitude/shape divergences rooted in
the contract's 1D reduction + per-panel suppression tuning (CONTRACT_BUG). No constructed stub
(every figure is a live protocol→measurement→view computation). No paper-issue earned.
