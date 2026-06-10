# Changelog — reynolds_heeger_2009

Newest first. The README "Changelog" table carries the one-line summaries; this file carries the
full detail.

## 2026-06-10 — paper-fix verify: F1/F2/F3 fix VERIFIED FAITHFUL, BLOCKED on three stale-contract findings (update-state)

**Summary line (mirrored in README):** paper-fix verify — BLOCKED on contract. The F1/F2/F3
doc-vs-contract-drift fix (commit 0157325) is independently verified faithful, but the verify pass
did NOT pass within MAX_PAPERFIX: three stale-contract findings (F-A/F-B/F-C) survive in `pseudocode/`
and `assumptions.yaml` and contradict the now-binding calibration. model.py untouched/faithful.

**Exit:** `{"overall":"blocked","trajectory":"toward_paper","flagged_count":3,"blocked":["model:contract"]}`.

**VERIFIED FAITHFUL this pass (the applied F1/F2/F3 fix; no further fix needed):**
- **F1** `model_spec.yaml:490-491,504-505` Fig-3 baselines now = CODE-017 (3C baselineMod=5e-7 /
  baselineUnmod=5.0; 3F 5e-7/0.0), matching `Figure3C.m:5-6` / `Figure3F.m:5-6` exactly. Application
  order matches `attentionModel.m:165-175` (Eraw=conv(stim)+baselineMod; E=attnGain·Eraw;
  R=E/(I+σ)+baselineUnmod) and pipeline steps 2.5/5.5.
- **F3** `figure_3.md` baseline table + Panel C/F prose + key-relationships rewritten to CODE-017; no
  residual A-007 0.05.
- **F2** `figure_4.md` Panel-C rewritten to the `Figure4C.m` four-separated-stimulus attend-null
  suppression build (x=±90/±110, c_nonpref=0.01, cRange[1e-4,0.1], %-mod=100·(unatt-att)/unatt).
  4D/4E corrected to the matching geometry.
- **DR-4C-sign** re-confirmed code-resolvable (`Figure4C.m:74` positive ⇒ Att-RF is the suppressed
  lower curve; deliberate sign contrast with Fig-2/3 facilitation captured correctly).
- **EQ-1/2/5/6** match the author code operator-for-operator; A-013 honored on the calibration surface
  (no per-panel suppressive gains).

**Three OPEN contract findings (logged DIVERGENT, need a fix-phase EDIT, not another audit):**
1. **F-A (model)** `pseudocode/figure_3_protocol.md:16-18` STILL binds the SUPERSEDED A-007 baselines
   (baseline_modulated_by_attention=0.05 / baseline_unmodulated=0.05, "per A-007"). A-007 is superseded
   by CODE-017 (3C 5e-7/5.0; 3F 5e-7/0.0). A grep confirms this is the ONLY place a 0.05 baseline
   survives as an active instruction. `pseudocode/` is a binding contract artifact — a reader following
   step 2/6 builds the wrong symmetric 0.05/0.05 baseline. *Fix:* rewrite Inputs (16-18) + Procedure
   2/6 to CODE-017, citing CODE-017 not A-007.
2. **F-B (figure)** `figure_2_protocol.md:9,16,22` and `figure_3_protocol.md:12,21,29-30` describe
   "single stimulus at x=0", unattended="constant 1 (no modulation)", sweep "[0.01,1] with 8 points".
   Author Figure2A/2B/3C/3F.m use TWO separated stimuli at x=±100, recorded at x=+100, BOTH conditions
   a real attention field (attended Ax=+100 'Att RF' vs unattended Ax=-100 'Att Away', not A=1), sweep
   cRange=[1e-5,1] (also contradicts calibration.yaml/CODE-020). Numerically verified equivalent AT THE
   RECORDED NEURON (attend-away gain at x=+100 = 2.2e-10 ≈ A=1, 6.7σ; contra drive at x=+100 = 0.0), so
   a contract-DESCRIPTION fidelity gap + stale sweep window, not a figure-output divergence. Tracked
   open as SQ-002. *Fix:* update to the two-separated-stimulus geometry + [1e-5,1], OR document the x=0
   reduction as an explicit justified equivalence.
3. **F-C (model)** `assumptions.yaml:411-413` A-013 rule (3) still reads "per-panel baselines that
   DIFFER across Fig-3 panels (use the single A-007 0.05·α)". CODE-017 (now binding) makes 3C/3F
   unmodulated (5.0 vs 0.0) legitimately differ — the authors' own per-figure code values. As written
   A-013(3) forbids the exact asymmetry the author code mandates. A-007's head was updated; this
   cross-reference was not. *Fix:* amend A-013(3) to forbid per-panel baselines TUNED-to-fit-a-curve
   while permitting the authors' own per-figure code values (CODE-017); drop the "use the single A-007
   0.05·α" clause.

**Process (trajectory toward_paper):**
- **C1 (DR-4C-sign authority, carryover).** DR-4C-sign was closed on a code re-run + caption
  re-reading. The published-caption-vs-model-panel reading is a human-owned question (A-012, owner=human,
  expiry 2026-07-15); a code re-run cannot adjudicate it. `panel_C_digitized.json` still labels the
  upper solid 'attended' behind a per-test read-time swap. Route the caption-attribution question to a
  faithfulness auditor WITH the paper / to the human owner before expiry — not another code re-run.
- **C2 (stale-doc findings).** F-A/F-B/F-C are correctly logged DIVERGENT and not closed — no leniency
  drift, but they need an edit in the fix phase, not another audit re-confirming they are stale, before
  they age into the next reader's ground truth.

**Where to look:** `logs/spec_audit/contract_audit_2026-06-10_paperfix_verify.md` (verify verdict);
`logs/faithfulness_audit/2026-06-10-independent-rerender.md`, `2026-06-04.md` (author-code reruns);
`logs/spec_questions.md` (SQ-002, SQ-005/006/007, DR-4C-sign RESOLVED).

## 2026-06-04 — from=fix finalize: window fix verified faithful, BLOCKED on two open contract divergences (update-state)

**Summary line (mirrored in README):** from=fix finalize — BLOCKED on contract. Window fix +
suppression-test/doc rewrites independently VERIFIED FAITHFUL (model unchanged; Fig 2/3 full sigmoids).
Paper-fix verify did NOT pass within MAX_PAPERFIX: 2 OPEN model-side contract divergences —
retired `suppressive_drive_gain` still LIVE at `stages/model_spec.yaml:116`, and 5C/6C/7C sweep
contrast 0.5 (audited:false) vs author `Figure*C.m contrast=1`. Both routed to human; exit
`blocked:[model:contract]`, flagged_count 2.

**Exit:** `{"overall":"blocked","trajectory":"toward_paper","flagged_count":2,"blocked":["model:contract"]}`.

**Verified faithful this pass (no fix needed):**
- The just-applied contrast-window fix: `figure_{2A,2B,3C,3F}.c_range_*` resolve to [1e-5,1] and
  `figure_4E` to [1e-4,0.1] (CODE-020, verbatim quotes match `Figure2A.m:5`/`Figure3C.m:7`/`Figure4E.m:7`).
  `protocols.py` routes them through the ledger; `views.py` xlim matches; digitized JSON `x_range` re-set
  and curve points actually relabeled into-window. Empirically reconfirmed via `rh_model.simulate`:
  2A unattended CRF 0.004→0.99 of max, attended half-max c≈0.00128 left of unattended 0.00253; 3C 0.235→0.99.
- The suppression-test rewrite: `test_contract_suppression_consistency.py` asserts no per-panel
  suppression knob resolves on any protocol (matches `attentionModel.m:89-93,175` — ONE separable
  conv2sepYcirc, no per-panel gain).
- The doc rewrite: no LIVE references to the retired per-panel gains/sigma-scales survive in
  calibration.yaml or protocol code (only explicit RETIRED/None notes).

**Two OPEN model-side contract divergences (why MAX_PAPERFIX did not pass):**
1. `implementation/src/rh_model/stages/model_spec.yaml:116` still declares the suppression stage
   `params: ["<protocol>.suppressive_drive_gain"]` — the retired knob, contradicting SQ-005, the
   rewritten suppression test, and `suppression.py`. Fix: drop it; reference global
   `model.suppressive_field_size` / `model.suppressive_tuning_width`.
2. `calibration.yaml figure_{5C,6C,7C}.contrast = 0.5 (audited:false)` contradicts
   `Figure5C.m:19 / Figure6C.m:21 / Figure7C.m:26 contrast = 1`. Load-bearing (scales the tuning sweep).
   Fix: set 1.0 (source CODE-018, audited:true with quote) or state the 1.0 contradiction explicitly
   and keep as a named assumption.

**Still RED / open (unchanged this pass):** 4E/7C two-stimulus GEOMETRY CODE_BUG (co-located vs four
separated; author geometry through committed `simulate` → 4E ~52%, 7C ~1.41); DR-4C-sign decision-request
(owner=human, expiry 2026-07-15); SQ-006 7C factorization; SQ-007 GAP 1/2/3.

**Low-severity figure residue (not blocking):** digitized JSON `notes` arrays still assert the OLD
`[0.01,1.0]` window (`figure_3/panel_C:373`, `panel_F:352`; `figure_4/panel_C:322`, `panel_E:309`);
the `x_range` field tests read is correct, so it is misleading prose, not a referent error.

**State refresh only — no model code, no spec, no test edits this pass.**

## 2026-06-03 — Current-state README rewrite (update-state skill, model HEAD c8ea505)

**Summary line (mirrored in README):** Current-state rewrite: 8 magnitude flags traced to
CONTRACT_BUG (per-panel suppression) + 6C CODE_BUG (fixed, sharpening restored) + 4E
GENUINE_DIVERGENCE; fresh VLM at HEAD c8ea505 (Fig 1 pass, 2/4/5/6/7 fail, 3 needs_review);
SQ-005 escalated.

**Exit:** `{"overall":"partial","trajectory":"toward_paper","flagged_count":8,"blocked":[]}`.

**What this pass did (state refresh only — no model code, no spec, no test edits):**

- Regenerated `implementation/figure_outputs/figure_*.png` from the current tree (`python -m
  rh_model.views`) so the VLM compared HEAD behavior, including the 6C CODE_BUG fix.
- Ran a fresh **parent direct-read VLM** over all 7 figures (paper vs regenerated output) and
  persisted verdicts at HEAD `c8ea505`:
  `logs/figure_comparisons/figure_*_20260604T012601Z.json`. The prior verdicts were all stale
  (recorded against 885f10b / 3a008a7). The May-2018 "Fig 1 broken" adjudications are superseded:
  the current Fig-1 render is faithful (correct hemifield structure, attention bump over the
  attended stimulus, attended band enhanced).
- Rewrote `README.md` as the current state in the prescribed order: current-exit block at top +
  queued human decisions, model description, per-figure three-view + tier tables, a "potential
  sources of the issues" section from the findings' source hints, and this changelog pointer.

**Figure verdicts of record (deterministic + fresh VLM):**

| Figure | Deterministic | VLM (c8ea505) | State |
|---|---|---|---|
| 1 | 10/10 pass | pass | ✅ FAITHFUL |
| 2 | 25/30 (2B ceiling RED) | fail | ❌ broken — 2A under-saturates (~0.34 vs ~0.62), 2B ceiling off |
| 3 | 24/27 (soft skips only) | needs_review | ❌ broken — residual over-separation (soft shape) |
| 4 | 22/32 (4C/4E RED) | fail | ❌ broken — 4E ~390% overflow, 4C +101% |
| 5 | 10/13 (peak ratio RED) | fail | ❌ broken — peak ratio ~1.59 vs ~1.2 |
| 6 | 12/14 (peak ratio RED) | fail | ❌ broken — sharpening now present, ratio ~1.31 vs ~1.11 |
| 7 | 9/12 (ratio RED) | fail | ❌ broken — variable/fixation ~3.3 vs ~1.4 |
| cross | 0/5 (contract MUST-PASS RED) | n/a | suppression-consistency invariant gating red |

**Root-cause triage (8 flags → 3 mechanism causes):**

1. CONTRACT_BUG — 1D suppression under-normalizes, patched with per-panel
   `suppressive_drive_gain` (2A 12 / 2B 6 / 3C 8 / 3F 12 / 4C 8 / 4E 8; tuning panels none) and
   `suppressive_spatial_sigma_scale` (0.55 / 1.0 / 0.45 / 0.7) + Fig-3 baselines 0.005.
   `test_contract_suppression_consistency.py` (MUST-PASS) RED, 4 tests. Origin of 2A/3C/3F/4C/5C/7C.
   Empirical: unifying the gain to 12 drops 5C 1.586→1.215 (paper value).
2. CODE_BUG (6C) — feature attention was spatially confined at x=−50 so `G_x≈0` at the recorded
   neuron and the curves overlapped; **fixed at HEAD c8ea505** (feature-global in x), restoring
   sharpening (1.01→1.31 peak, 133°→104° FWHM). Same structure pending for 7C attend-nonpref (SQ-006).
3. GENUINE_DIVERGENCE (4E) — γ=5 two-stimulus feature competition drives %-mod to ~390%; survives
   even gain 40. Not a suppression-gain issue.

**Open / escalated:** SQ-005 (the contract's 2D-plane suppression fix is empirically falsified —
makes S smaller, not larger; escalated to Phase A with three options), SQ-006 (formalize
"feature attention is spatially global"), SQ-001/002 (per-panel gains/baselines `audited:false`).
SQ-003 resolved; SQ-004 retired (4C 75° override deleted, retirement encoded MUST-PASS).

---

## 2026-06-10 — paper-fix verify: 6C model VERIFIED FAITHFUL, BLOCKED on stale Figure 6 render

**Exit:** `{"overall":"blocked","trajectory":"toward_paper","flagged_count":1,"blocked":["model:contract"]}`

**Model fix VERIFIED FAITHFUL (commit 862f4d7, lineage rung 1 = this paper's own author code).**
The Figure 6C CONTRACT_BUG correction is faithful. I independently reproduced `Figure6C.m` +
`attentionModel.m` + `makeGaussian.m` + `conv2sepYcirc.m` from scratch in standalone Python: the
author 'cross' field gives peak ratio 1.1088 and FWHM ratio 0.8873 (att-away peak 12.4528, att-RF
peak 13.8076), matching digitized 1.108 and the FWHM band [0.87,0.89]. The impl
`run_figure_6C(n_directions=356)` returns BYTE-IDENTICAL values, confirming both the 'cross'
transcription and sweep-equivalence (impl sweeps stim+attention θ recording the θ=0 neuron at x=100;
author fixes stim θ=0 and reads R(:,find(x==100)) — equivalent under θ shift-invariance).
`_build_attention_field_cross` (model.py:284) is a faithful transcription of attentionModel.m:146-162
(double baseline-lift, circular-θ impulse-conv) and reduces to the model_spec EQ-attention CROSS
closed form A=(γ-1)·attnGainX·attnGainθ+1 to machine precision (max|Δ|=3.6e-15). `_separable_conv`
faithfully implements conv2sepYcirc. The default 'oval' path is byte-identical with/without
shape:'cross' (allclose), so Figs 2/3/4/5/7 are untouched. Provenance clean: ledger keys
figure_6C.stim_rf_x=100 / stim_contra_x=-100 / attend_fixation_x=0 (calibration.yaml:682-702) sourced
CODE-018 with verbatim Figure6C.m line quotes; all audited:true. No per-panel knob tuned. SQ-006 and
SQ-009 genuinely RESOLVED. The 3 MUST-PASS contract tests (test_audit_2026_06_10_contract.py) are
GREEN (3 passed in 34.5s; numeric, need no matplotlib).

**The block (F1, figure-scope) — STALE RENDERED ARTIFACT vs the now-FAITHFUL model.** The verify did
NOT pass within MAX_PAPERFIX. The committed/displayed Figure 6 renders predate the 6C fix and still
show the OLD over-scaled curve while the README header asserts FAITHFUL. Timeline: resolve commit
862f4d7 is 2026-06-10 05:52; but `implementation/figure_outputs/figure_6.png` is 04:57 (pre-commit),
the README-displayed `figures_reproduced/figure_6.png` is Jun 4 13:57, and the overlay
`article_aware/figures/figure_6/overlay_6C.png` is Jun 3 16:42. Panel C draws the attend-fixation gray
curve peaking at ~0.855 (shared-max norm) → peak ratio ~1/0.855 = 1.17 = the PRE-FIX over-scaled
state; the corrected model would put gray at ~1/1.108 = 0.903. The shipping image contradicts the
FAITHFUL claim and the now-correct numeric text (peak 1.109 / FWHM 0.887). The 2 panel-axes 6C tests
(test_panel_axes.py) FAIL with ModuleNotFoundError: No module named 'matplotlib' — matplotlib is
genuinely absent in this environment, so the renders cannot be regenerated here. Per the
rendered-output-panels-are-reproduction-targets and VLM-eye-is-arbiter conventions this is a real
figure-scope divergence: a reader sees a FAITHFUL header over a divergent image.

**Fix (next pass, needs matplotlib env):** `pip install matplotlib`, then regenerate
`implementation/figure_outputs/figure_6.png`, `figures_reproduced/figure_6.png`, and
`article_aware/figures/figure_6/overlay_6C.png` and commit the refreshed artifacts so the panel shows
the corrected curve (attend-fixation gray peak ~0.903 under shared-max norm, peak ratio 1.109). Verify
by eye that the gray/blue peak ratio and widths match the digitized panel before re-asserting FAITHFUL.

**Process:** trajectory toward_paper. C1 (self-caught last pass, now resolved): SQ-006/commit title
'RESOLVED' over-claim is fixed — the build is DONE and verified. C2 (refuted, logged): Q-043 7C test
window narrowing was auditor-prescribed from released author code, not builder-grades-own-homework.
Carryover (not re-litigated): DR-4C-sign caption-attribution authority (A-012, expiry 2026-07-15) —
route to a paper-reading faithfulness auditor / human owner before expiry; F-A/F-B/F-C prior-pass
contract-doc findings remain on record for a fix-phase edit.

**README:** refreshed to current state — exit block (flagged_count 1), DECISION NEEDED rewritten to
the single stale-render block, Figure 6 header scoped to "model FAITHFUL · shipped render STALE",
audit/check tables flag the stale PNG and the matplotlib-absent panel-axes failures.
