# Reynolds & Heeger 2009 — The Normalization Model of Attention

<!-- CURRENT STATE — updated 2026-06-10. The doc-vs-contract-drift fix (F1/F2/F3, commit 0157325)
     is INDEPENDENTLY VERIFIED FAITHFUL: model_spec/figure_3/figure_4 docs now match the author code
     (CODE-017 Fig-3 baselines, Figure4C.m suppression build) operator-for-operator. The paper-fix
     verify did NOT pass within MAX_PAPERFIX: three stale-contract findings (F-A/F-B/F-C) survive in
     `pseudocode/` and `assumptions.yaml` and contradict the now-binding calibration. model.py is
     untouched and remains independently faithful. Exit = blocked on model:contract. -->

## Current exit

```json
{"overall": "blocked", "trajectory": "toward_paper", "flagged_count": 3, "blocked": ["model:contract"]}
```

## 👉 DECISION NEEDED

**Contract-blocked (paper-fix / audit-spec).** The paper-fix verify did NOT pass within
MAX_PAPERFIX. The F1/F2/F3 doc fix was applied and is **verified faithful** (see below), but the
verify pass found **three open contract findings** that still bind a reader to the WRONG, superseded
calibration. They are stale-doc divergences, not model-equation faults — but `pseudocode/` and
`assumptions.yaml` are **binding contract artifacts** (audit-spec skill), so a Phase-B reader
following them builds the wrong model. They need an EDIT in the fix phase, not another audit
re-confirming they are stale (process concern C2). **trajectory: toward_paper** (no leniency drift;
the new divergences were left RED, nothing force-greened).

**The three open findings (all logged DIVERGENT, none closed):**

- **F-A (model) — stale A-007 0.05/0.05 baselines survive in the Fig-3 pseudocode.**
  `article_aware/pseudocode/figure_3_protocol.md:16-18` still binds
  `baseline_modulated_by_attention = 0.05 / baseline_unmodulated = 0.05 (per A-007)`. A-007 is
  **superseded by CODE-017** (3C 5e-7/5.0; 3F 5e-7/0.0, verified against `Figure3C.m:5-6` /
  `Figure3F.m:5-6`). F1/F3 applied CODE-017 to `model_spec.yaml` and `figure_3.md` but NOT to this
  pseudocode. A grep confirms this is the **only** place a 0.05 baseline survives as an *active
  instruction* — a reader following step 2/6 builds the wrong symmetric 0.05/0.05 baseline.
  *Fix:* rewrite Inputs (16-18) + Procedure 2/6 to CODE-017, citing CODE-017 not A-007.

- **F-B (figure) — Fig-2/3 pseudocode describes a DIFFERENT experiment + a stale sweep window.**
  `figure_2_protocol.md:9,16,22` and `figure_3_protocol.md:12,21,29-30` describe "single stimulus at
  x=0", unattended = "constant 1 (no modulation)", sweep "[0.01,1], 8 points". Author
  Figure2A/2B/3C/3F.m use **TWO separated stimuli at x=±100, recorded at x=+100**, BOTH conditions a
  real attention field (attended Ax=+100 'Att RF' vs unattended attend-away Ax=−100, not A=1), sweep
  cRange=[1e-5,1] (also contradicts the model's own `calibration.yaml`/CODE-020). The x=0 single-stim
  reduction is numerically faithful AT THE RECORDED NEURON (attend-away gain at x=+100 = 2.2e-10 ≈
  A=1, 6.7σ; contra drive at x=+100 = 0.0), so this is a contract-**description** gap + stale window,
  not a figure-output divergence. Tracked open as **SQ-002** pending human review.
  *Fix:* update Fig-2/3 pseudocode to the two-separated-stimulus geometry + [1e-5,1], OR document the
  x=0 reduction as an explicit justified equivalence (with the verified recorded-neuron bit-identity).

- **F-C (model) — A-013 forbidden-knob rule (3) now contradicts the binding CODE-017.**
  `assumptions.yaml:411-413` still reads: "per-panel baselines that DIFFER across Fig-3 panels (use
  the single A-007 0.05·α)". But CODE-017 (now binding, verified) establishes that 3C and 3F
  baselines **do** legitimately differ (unmod 5.0 vs 0.0) — the authors' own per-figure code values.
  As written, A-013(3) forbids the exact per-panel asymmetry the author code mandates. A-007's head
  was updated to acknowledge CODE-017; this cross-reference was not (binding-rule vs binding-calibration).
  *Fix:* amend A-013(3) to forbid per-panel baselines **tuned-to-fit-a-curve** while permitting the
  authors' own per-figure code values (CODE-017); drop the "use the single A-007 0.05·α" clause.

**Where to look:**
- `logs/spec_audit/contract_audit_2026-06-10_paperfix_verify.md` — the verify verdict (DIVERGENT) with
  F-A/F-B/F-C and the VERIFIED-FAITHFUL F1/F2/F3 section.
- `logs/faithfulness_audit/2026-06-10-independent-rerender.md`, `2026-06-04.md` — author-code reruns
  (4E 386%→52%, 7C 2.73→1.41) backing the figure-scope geometry divergences.
- `logs/spec_questions.md` — **SQ-002** (the Fig-2/3 geometry/description gap, F-B); SQ-005 / SQ-006
  / SQ-007 human resolutions; DR-4C-sign **RESOLVED** (code-resolvable, digitizer label swap).

**Carryover process concern (C1, DR-4C-sign authority).** DR-4C-sign was closed (2026-06-10) on a
code re-run + caption re-reading. The published-caption-vs-model-panel *reading* is a human-owned
question (A-012, expiry 2026-07-15); a code re-run cannot adjudicate it. `panel_C_digitized.json`
still labels the upper solid 'attended' behind a per-test read-time swap. If the closure is to stand,
route the **caption-attribution** question to a faithfulness auditor WITH the paper / to the human
owner before expiry — not another code re-run.

---

## Model

Reynolds JH, Heeger DJ. **The Normalization Model of Attention.** *Neuron.* 2009 Jan 29;61(2):168–185.
doi:[10.1016/j.neuron.2009.01.002](https://doi.org/10.1016/j.neuron.2009.01.002) (PMCID PMC2752446).

The foundational **normalization model of attention**: one divisive-normalization circuit explains
contrast-gain vs response-gain modulation, multiplicative tuning-curve scaling, feature-based
sharpening, and tuning shifts with two stimuli in the receptive field. A population indexed by
RF center `x` and feature preference `θ` receives an excitatory **stimulus drive** `E(x,θ)`, is
gated by a multiplicative **attention field** `A(x,θ) ≥ 1`, and is divisively normalized by a pooled
**suppressive drive** `S(x,θ)`. The central claim: the *shape* of attentional modulation is not a free
parameter — it emerges from the relative size of the attention field and the stimulus.

Per neuron, the rectified divisive-normalization response (Eq. 5):

```
R(x,θ) = ⌊ A(x,θ)·E(x,θ) / (S(x,θ) + σ) ⌋_T
```

with the suppressive drive the suppressive field convolved with the *attention-modulated* drive
(Eq. 6), `S = s ∗ [A·E]`. Resolved from the authors' released MATLAB (`paper/code/attentionModel/`),
the suppression is a **separable space×feature** convolution — `conv2sepYcirc` (zero-pad x, circular θ)
of two unit-volume Gaussians (IxWidth=20, IthetaWidth=360 near-flat θ pool), σ=1e-6 — with **NO
per-panel suppression gain**. **The equations map operator-for-operator to the paper and the author
code, and are faithful** (independent audits: spec_audit VERDICT FAITHFUL, faithfulness_audit
"model.py is FAITHFUL"; the 2026-06-10 paper-fix verify re-confirmed EQ-1/2/5/6 against
attentionModel.m:165-175). Every open divergence is **figure / contract-scope**, not a transcription
fault.

Scope: 7 figures. Fig 1 is the authors' own activity-map render; Figs 2–7 are live
`protocols.run_figure_*` → `measurements` → Phase-A `views`. Empirical/config sub-panels are explicit
"not reproduced" placeholders.

---

## Reproduced figures — paper · digitized · implementation

Each figure is shown three ways: **paper** (original panel), **digitized** (tool-grounded curves on
the paper pixels — the audited reference the tests compare against, `logs/digitization_audit/`), and
**implementation** (the live model through the same pinned-axis view). Two checks per figure: the
**digitization audit** (paper vs digitization) and the **final-figure VLM** (implementation vs paper).
A figure is **green only if deterministic all-pass AND fresh VLM pass**.

### Figure 1 — Activity-map render  ✅ FAITHFUL (det all-pass · VLM pass)

<table><tr><th>Paper</th><th>Implementation</th></tr><tr><td><img src="article_aware/figures/figure_1.jpg" width="430"></td><td><img src="figures_reproduced/figure_1.png" width="430"></td></tr></table>

The `E × A ÷ S → R` pipeline rendered as the authors' four activity maps: stimulus drive (two bands)
× a localized attention field over the attended (right) stimulus, ÷ the pooled suppressive drive →
an output that **enhances the attended band relative to the left**. 10/10 must-pass; the R-asymmetry
tripwire correctly xfails. The faithful single-mechanism suppression is validated here (the authors'
own render reproduces exactly).

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| **figure** | n/a (activity map) | ✅ **faithful** — topology + attended-stimulus enhancement match |

### Figure 2 — Contrast gain vs response gain  ✅ FAITHFUL (det all-pass · CRFs full sigmoids)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_2.jpg" width="300"></td><td><img src="article_aware/figures/figure_2/overlay_2A.png" width="150"><img src="article_aware/figures/figure_2/overlay_2B.png" width="150"></td><td><img src="figures_reproduced/figure_2.png" width="300"></td></tr>
</table>

Over the author Figure2A/2B.m window `[1e-5, 1]` (CODE-020) the panels are full sigmoids: 2A is
contrast-gain — attended **left-shifted** (half-max c≈0.00128) below ignored (c≈0.00253), converging
to a shared plateau; 2B is response-gain — attended scaled UP above ignored with sustained ~42% %-mod.
All deterministic 2A/2B tests pass. **Contract caveat (F-B, open):** the Fig-2 pseudocode still
describes a single-stim-x=0 / [0.01,1] experiment that contradicts the author two-separated-stimulus
geometry and the binding [1e-5,1] window (numerically equivalent at the recorded neuron, but the
contract description must be reconciled — SQ-002).

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 2A | ✅ faithful | ✅ faithful — contrast-gain left-shift, shared plateau, %-mod falls |
| panel 2B | ✅ faithful | ✅ faithful — response-gain upward-shift, sustained ~42% %-mod |
| **figure** | ✅ **faithful** | ✅ **faithful** (pseudocode description F-B open) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 2A attended ≥ ignored / converges / %-mod falls | ✅ pass |
| qualitative | 2B attended above ignored / no convergence | ✅ pass |
| hard | 2A / 2B high-contrast separation vs digitized | ✅ pass |
| hard | 2A attended left-shifted (half-max) in author window | ✅ pass |
| shape | 2A/2B half-max & %-mod plateau vs digitized | ✅ pass |

### Figure 3 — Baseline shift across contrast  ✅ FAITHFUL (det all-pass · CRFs full sigmoids)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_3.jpg" width="300"></td><td><img src="article_aware/figures/figure_3/overlay_3C.png" width="150"><img src="article_aware/figures/figure_3/overlay_3F.png" width="150"></td><td><img src="figures_reproduced/figure_3.png" width="300"></td></tr>
</table>

Over the author Figure3C/3F.m window `[1e-5, 1]`: 3C attend-in-RF above contralateral with an interior
%-mod bump and high-contrast convergence (unmod=5.0 baseline lifts the foot, **CODE-017**); 3F
sustained separation (attended ~0.74 above ignored ~0.61) with %-mod largest at low contrast declining
to a ~20% plateau. All deterministic 3C/3F tests pass; `model_spec.yaml` and `figure_3.md` carry the
CODE-017 baselines (verified faithful, F1/F3). Empirical (B/E) and config (A/D) panels correctly "not
reproduced".

> **Contract caveats (open):** **F-A** — the Fig-3 *pseudocode* (`figure_3_protocol.md:16-18`) still
> binds the SUPERSEDED A-007 0.05/0.05 baselines (the only surviving active 0.05 instruction); a reader
> following it builds the wrong symmetric baseline. **F-C** — A-013 rule (3) still forbids the per-panel
> 3C/3F asymmetry that CODE-017 mandates. **Residue:** digitized JSON `notes` arrays still narrate the
> OLD `[0.01,1.0]` window (`panel_C:373`, `panel_F:352`); the `x_range` FIELD (what tests read) is
> correct, but the prose could mislead a future digitizer.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 3C | ✅ faithful | ✅ faithful — interior %-mod bump, converges at high contrast |
| panel 3F | ✅ faithful | ✅ faithful — sustained separation, %-mod largest at low contrast |
| **figure** | ✅ **faithful** | ✅ **faithful** (pseudocode F-A + rule F-C open) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 3C above/converge · 3F above/persist | ✅ pass |
| hard | 3C / 3F high-contrast separation vs digitized | ✅ pass |
| shape | 3C %-mod interior bump · 3F abs-diff above %-mod peak | ✅ pass |

### Figure 4 — Two-stimulus contrast-response modulation  ❌ 4E %-mod overflow (geometry, RED); 4C dispositioned

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_4.jpg" width="300"></td><td><img src="article_aware/figures/figure_4/overlay_4C.png" width="150"><img src="article_aware/figures/figure_4/overlay_4E.png" width="150"></td><td><img src="figures_reproduced/figure_4.png" width="300"></td></tr>
</table>

Both panels render over the author Figure4C/4E.m window `[1e-4, 0.1]` (CODE-018/CODE-020). **4C**
follows the authors' released `Figure4C.m` (line 74 plots `100*(unattCRF-attCRF)/unattCRF` — the
suppression sign: attend-null-in-RF SUPPRESSES the recorded preferred neuron, attended BELOW
unattended). `figure_4.md` Panel-C was rewritten to this four-separated-stimulus build and is
**verified faithful** (F2). DR-4C-sign is **RESOLVED** (code-resolvable: a digitizer label swap, not a
paper defect — the published positive %-modulation matches the author formula once the upper solid is
read as the author's "Att Away"/unattCRF). The deliberate sign CONTRAST with Fig-2/3 facilitation is
captured correctly. *Carryover (C1):* the caption-attribution authority question and the
`panel_C_digitized.json` label swap are noted in DECISION NEEDED.
**4E is the residual RED:** %-modulation overflows the paper's 0–100 axis to **~386%** — a two-stimulus
GEOMETRY CODE_BUG (the protocol co-locates two stimuli at x=0 where Figure4E.m uses FOUR SEPARATED
stimuli, RF x=90/110, contra x=−90/−110). The author geometry through the *committed, unchanged*
`simulate` yields ~52% (faithfulness_audit Finding B), matching the digitized ~54%. Left RED.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 4C | ✅ faithful | ⚠️ dispositioned — author suppression sign; DR-4C-sign RESOLVED (label swap) |
| panel 4E | ✅ faithful | ❌ %-mod ~386% off-axis (two-stimulus GEOMETRY CODE_BUG, not the window) |
| **figure** | ✅ **faithful** | ❌ **divergent** (4E geometry RED) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 4C suppression direction · 4E attend-pref above nonpref | ✅ pass |
| window | 4C / 4E sweep + xlim = author cRange [1e-4, 0.1] | ✅ pass |
| hard | 4E %-mod stays within paper 0–100 axis | ❌ **FAIL** — ~386% (co-located geometry) |
| hard | 4E author-geometry %-mod ~54% | ❌ **FAIL** — needs four-separated-stimulus fix |

### Figure 5 — Spatial attention as multiplicative scaling  ❌ BROKEN — peak ratio RED

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_5.jpg" width="300"></td><td><img src="article_aware/figures/figure_5/overlay_5C.png" width="300"></td><td><img src="figures_reproduced/figure_5.png" width="300"></td></tr>
</table>

The right *kind* of effect — multiplicative, same-width scaling (attend-in-RF and contralateral share
FWHM, no sharpening). The author-geometry rerun lands the peak ratio at ~1.17 vs the paper's ~1.2
(faithfulness_audit), so the mechanism is faithful; the remaining red is the peak-ratio tier check
against the current digitized reference. The 5C sweep contrast is now `1.0` (CODE-021, `Figure5C.m:19`)
— the prior `audited:false` 0.5 provenance divergence is **resolved** in calibration.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 5C | ✅ faithful | ❌ divergent — peak-ratio tier RED |
| **figure** | ✅ **faithful** | ❌ **divergent** (peak ratio) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 5C attended above unattended · same width, no sharpening | ✅ pass |
| hard | 5C peak ratio vs digitized | ❌ **FAIL** |
| soft | 5C shape / unattended peak vs digitized | ⚠️ soft (reported) |

### Figure 6 — Feature-based attention sharpening  ❌ BROKEN — sharpening PRESENT, magnitude overshoot

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_6.jpg" width="300"></td><td><img src="article_aware/figures/figure_6/overlay_6C.png" width="300"></td><td><img src="figures_reproduced/figure_6.png" width="300"></td></tr>
</table>

Feature-based attention is spatially global (A-014, formalizing SQ-006), so the directional gain reaches
the recorded neuron: attend-contralateral is both taller (peak 1.0 vs fixation ~0.76) **and narrower
(sharpening present)** — the prior overlapping-curves failure is gone. Magnitude ~1.17–1.31 vs
digitized ~1.11 keeps the magnitude-ratio tier red (the author `Ashape='cross'` field is not
implemented; the oval approximation mildly overshoots — do NOT tune it). The 6C sweep contrast is now
`1.0` (CODE-021, `Figure6C.m:21`) — the prior 0.5 divergence is **resolved** in calibration.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 6C | ✅ faithful | ❌ divergent — sharpening present, magnitude overshoot |
| **figure** | ✅ **faithful** | ❌ **divergent** (magnitude) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 6C attended ≥ tall at peak · sharpening present | ✅ pass |
| hard | 6C peak ratio vs digitized | ❌ **FAIL** |
| soft | 6C flank difference / shape vs digitized | ⚠️ soft |

### Figure 7 — Two stimuli in RF: combined attention shifts  ❌ BROKEN — var/fix ratio RED (geometry)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_7.jpg" width="300"></td><td><img src="article_aware/figures/figure_7/overlay_7C.png" width="300"></td><td><img src="figures_reproduced/figure_7.png" width="300"></td></tr>
</table>

Ordering faithful (attend-variable > ignored/fixation > attend-nonpref) but the variable/fixation peak
ratio is **~2.73 vs the paper's ~1.4** — the same two-stimulus GEOMETRY CODE_BUG as 4E (co-located vs
two separated). The author geometry (var x=93, null x=107, recorded x=100, att-away x=−100) through the
committed `simulate` lands ~1.41 (faithfulness_audit Finding D), matching the digitized ~1.4. Panel C
is the sole deliverable (SQ-003, human-resolved); A/B "not reproduced". The 7C sweep contrast is now
`1.0` (CODE-021, `Figure7C.m:26`) — the prior 0.5 divergence is **resolved** in calibration.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 7C | ✅ faithful | ❌ divergent — ratio ~2.73 vs ~1.4 (geometry) |
| **figure** | ✅ **faithful** | ❌ **divergent** (geometry RED) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 7C peak ordering variable>fixation>nonpref | ✅ pass |
| hard | 7C variable/fixation ratio vs digitized | ❌ **FAIL** |
| soft | 7C variable/nonpref ratio / shape vs digitized | ⚠️ soft |

---

## Potential sources of the issues

The forward model (`model.py`, Eqs. 5–6) is FAITHFUL operator-for-operator to the authors' MATLAB
(`paper/code/attentionModel/attentionModel.m`) — confirmed by independent audits and re-confirmed by
the 2026-06-10 paper-fix verify. Every open divergence is **contract-description / figure-scope**.

1. **CONTRACT (F-A) — stale A-007 baselines in the Fig-3 pseudocode. OPEN, fix-phase edit.**
   `article_aware/pseudocode/figure_3_protocol.md:16-18` binds the superseded `baseline_* = 0.05 (per
   A-007)`; the only surviving active 0.05 instruction. CODE-017 (3C 5e-7/5.0; 3F 5e-7/0.0) is binding
   everywhere else. *Source:* `figure_3_protocol.md:16-18`; `code_refs.yaml` CODE-017; `Figure3C.m:5-6`,
   `Figure3F.m:5-6`.

2. **CONTRACT (F-B) — Fig-2/3 pseudocode describes a different experiment + stale [0.01,1] sweep. OPEN (SQ-002).**
   `figure_2_protocol.md:9,16,22` / `figure_3_protocol.md:12,21,29-30` say "single stimulus at x=0",
   unattended="constant 1", sweep "[0.01,1]". Author scripts use TWO separated stimuli at x=±100,
   recorded x=+100, both with a real attention field, sweep [1e-5,1]. Numerically equivalent at the
   recorded neuron (verified) but a contract-description gap that contradicts `calibration.yaml`/CODE-020.
   *Source:* `figure_{2,3}_protocol.md`; `Figure2A/2B/3C/3F.m`; `calibration.yaml` figure_*.c_range_*; SQ-002.

3. **CONTRACT (F-C) — A-013 rule (3) forbids the per-panel asymmetry CODE-017 mandates. OPEN, fix-phase edit.**
   `assumptions.yaml:411-413` still says per-panel Fig-3 baselines that differ are forbidden ("use the
   single A-007 0.05·α"); CODE-017 makes 3C/3F unmodulated (5.0 vs 0.0) legitimately differ. A-007's
   head was updated; this cross-reference was not. *Source:* `assumptions.yaml:411-413`; `code_refs.yaml`
   CODE-017.

4. **GEOMETRY — Fig-4E / Fig-7C two-stimulus geometry. Contract carries author geometry; protocol code RESIDUAL.**
   Calibration + figure protocols carry the author SEPARATED geometry (4E four stimuli; 7C two
   in-RF). The author geometry through the *committed, unchanged* `simulate` lands 4E ~52% and 7C ~1.41
   (faithfulness_audit Findings B/D). RESIDUAL MODEL-SIDE WORK: `protocols.py run_figure_4E /
   run_figure_7C` still co-locate at x=0 and must be rebuilt to the contract geometry (forward
   mechanism unchanged). *Source:* `Figure4E.m`, `Figure7C.m`; calibration figure_{4E,7C}.* (CODE-018);
   `logs/faithfulness_audit/2026-06-04.md`.

5. **DECISION-REQUEST — DR-4C-sign. RESOLVED code-side (digitizer label swap); caption-authority carryover (C1).**
   The published positive %-modulation matches `Figure4C.m` once the upper solid is read as the
   author's "Att Away"/unattCRF; the model follows the code and is correct. The
   published-caption-vs-model-panel *reading* (A-012, owner=human, expiry 2026-07-15) and the
   `panel_C_digitized.json` solid-label swap should be ratified by a faithfulness auditor WITH the paper
   / the human owner, not another code re-run. *Source:* `Figure4C.m:69,74`; `figure_4/panel_C.md`;
   `assumptions.yaml` A-012.

6. **MAGNITUDE — Fig-5/6 peak-ratio overshoot. Soft, structural, do NOT tune.**
   5C peak ratio ~1.17 vs ~1.2; 6C ~1.17–1.31 vs digitized ~1.11. Mechanism faithful; the residue is
   the unimplemented author `Ashape='cross'` attention-field shape (oval approximation). Contrast
   provenance for 5C/6C/7C is now resolved (CODE-021 `contrast=1`). *Source:* `protocols.py
   run_figure_{5C,6C}`; Fig-6 caption; `code_refs.yaml` CODE-021.

---

## Changelog

One line here; full detail in [`logs/changelog.md`](logs/changelog.md).

| Date | Change |
|---|---|
| 2026-06-10 | **paper-fix verify — BLOCKED on contract.** F1/F2/F3 doc-vs-contract-drift fix VERIFIED FAITHFUL (model_spec Fig-3 baselines = CODE-017; figure_3.md/figure_4.md rewritten to author code; EQ-1/2/5/6 match attentionModel.m). Verify did NOT pass within MAX_PAPERFIX: 3 stale-contract findings remain DIVERGENT — **F-A** figure_3_protocol.md:16-18 still binds superseded A-007 0.05/0.05; **F-B** Fig-2/3 pseudocode describes a single-stim-x=0/[0.01,1] experiment vs author two-separated-stimulus/[1e-5,1] (SQ-002); **F-C** A-013(3) forbids the CODE-017 3C/3F baseline asymmetry. model.py untouched/faithful. DR-4C-sign RESOLVED (digitizer label swap; caption-authority carryover C1). Exit `blocked:[model:contract]`, flagged_count 3, trajectory toward_paper. |
| 2026-06-10 | Phase-A contract resolution of four blocked divergences (author-code grounded; model.py untouched): retired `suppressive_drive_gain` removed from stage spec; 5C/6C/7C sweep contrast 0.5→1.0 (CODE-021); 4E/7C author SEPARATED geometry adopted; DR-4C-sign investigated→code-resolvable. Added A-014. |
| 2026-06-04 | from=fix finalize — BLOCKED on contract. Window fix + suppression-test/doc rewrites VERIFIED FAITHFUL (Fig 2/3 full sigmoids). 2 OPEN model-side contract divergences routed to human. |
| 2026-06-04 | Contrast-window CONTRACT_BUG + digitized re-digitization RESOLVED (author cRange [1e-5,1] / [1e-4,0.1]; model unchanged). 18→5 deterministic reds. |
