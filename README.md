# Reynolds & Heeger 2009 — The Normalization Model of Attention

<!-- CURRENT STATE — updated 2026-06-04 after a from=fix finalize. The just-applied window fix
     (author cRange routed through sweep/view/digitized-x_range; per-panel suppression knobs deleted)
     was independently VERIFIED FAITHFUL. But the paper-fix verify did NOT pass within MAX_PAPERFIX:
     two OPEN model-side contract divergences remain — a retired knob still declared LIVE in the
     stage spec, and 5C/6C/7C sweep contrast pinned to an audited:false 0.5 that the author scripts
     contradict (contrast=1). These BLOCK a clean contract; routed to human. -->

## Current exit

```json
{"overall": "blocked", "trajectory": "toward_paper", "flagged_count": 2, "blocked": ["model:contract"]}
```

## 👉 DECISION NEEDED

**Contract-blocked (paper-fix / audit-spec): the paper-fix verify did not pass within MAX_PAPERFIX.**
The forward model is faithful and the window fix was verified correct, but two model-side contract
divergences remain OPEN and a paper-blind builder cannot close them without a human ruling. Both are
provenance/contract integrity issues — neither touches the (faithful) `model.py` equations.

**Open finding #1 — stale retired knob declared LIVE in the stage spec (model:contract).**
`implementation/src/rh_model/stages/model_spec.yaml:116` still lists the suppression stage's
`params: ["<protocol>.suppressive_drive_gain"]  # impl ledger (SQ-001, 1D scale)`. That is the
RETIRED per-panel knob (SQ-001/SQ-005, A-013): no per-panel suppression gain exists in the author
code (`R = E./(I+sigma)+baselineUnmod`, attentionModel.m:175), `test_contract_suppression_consistency.py`
asserts it resolves `None` on every protocol, and `suppression.py`'s docstring says it is retired
and not read. A reader of the stage contract is told the stage consumes a gain that no longer exists
— same stale-residue antipattern the README/docstring fix targeted, left in the stage spec.
→ **Fix when ratified:** drop `<protocol>.suppressive_drive_gain` from line 116; reference the global
`model.suppressive_field_size` / `model.suppressive_tuning_width` (the single space×feature pool).

**Open finding #2 — 5C/6C/7C sweep contrast = 0.5 (audited:false) contradicts the author code (model:contract).**
`article_aware/spec/calibration.yaml` `figure_5C.contrast` / `figure_6C.contrast` / `figure_7C.contrast`
are all `0.5`, `audited: false`, noted "fixed sweep contrast (0.5) is an assumption, not a verbatim
paper value" (lines 559/594/629). But `Figure5C.m:19`, `Figure6C.m:21`, `Figure7C.m:26` all set
`contrast = 1;`. These are load-bearing — they scale the stimulus drive for the entire tuning sweep —
and are now resolvable from the SAME author-code lineage the just-applied c_range fix relied on. The
contract uses 0.5 where the author uses 1.0. (Also `Figure5C.m:20 stim = contrast*stim1*contrast + stim2`
scales stim1 by contrast², a structural difference only if 0.5 is kept.) Pre-existing contract bug,
surfaced by the acquired ground truth, not introduced this pass.
→ **Fix when ratified:** set 5C/6C/7C `contrast = 1.0`, source CODE-018 / lineage `Figure5C.m:19` /
`Figure6C.m:21` / `Figure7C.m:26`, `audited: true` with verbatim quote — OR, if 0.5 is a deliberate
display choice, state the author-code 1.0 contradiction explicitly (code-alone-honesty rule) and keep
it a named assumption rather than an unexplained `audited:false`.

**Where to look** — `logs/spec_audit/sq005_correction_audit_2026-06-04.md` (Phase-A contract audit,
VERDICT FAITHFUL for the mechanism); `logs/faithfulness_audit/2026-06-04.md` (independent re-render:
model faithful, all divergences figure/contract-scope, author-geometry reruns 4E 386%→52%, 7C 2.73→1.41);
the spec questions in `logs/spec_questions.md` (**SQ-007** GAP 1/2/3, **SQ-006** 7C factorization,
**SQ-005** human_resolution). The 4E/7C two-stimulus GEOMETRY divergence (still RED, separate from the
two contract findings above) and **DR-4C-sign** (the published-Fig-4C-vs-model sign decision-request,
owner=human, expiry 2026-07-15) also await human ratification.

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
per-panel suppression gain** (the SQ-001/SQ-002 knobs are deleted). **The equations map
operator-for-operator to the paper and the author code, and are faithful** (independent audits
2026-06-04: spec_audit VERDICT FAITHFUL, faithfulness_audit "model.py is FAITHFUL"). Every remaining
divergence is figure/contract-scope, not a transcription fault.

Scope: 7 figures. Fig 1 is the authors' own activity-map render; Figs 2–7 are live
`protocols.run_figure_*` → `measurements` → Phase-A `views`. Empirical/config sub-panels are explicit
"not reproduced" placeholders.

---

## Reproduced figures — paper · digitized · implementation

Each figure is shown three ways: **paper** (original panel), **digitized** (tool-grounded curves on
the paper pixels — the audited reference the tests compare against, `logs/digitization_audit/`), and
**implementation** (the live model through the same pinned-axis view). Two checks per figure: the
**digitization audit** (separate critic, paper vs digitization) and the **final-figure VLM**
(implementation vs paper). A figure is **green only if deterministic all-pass AND fresh VLM pass**.

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

Over the author Figure2A/2B.m window `[1e-5, 1]` (CODE-020, **verified faithful this pass**: sweep,
view xlim, and digitized x_range all resolve to the author window) the panels are full sigmoids: 2A is
contrast-gain — attended **left-shifted** (half-max c≈0.00128) below ignored (c≈0.00253), converging
to a shared plateau; 2B is response-gain — attended scaled UP above ignored with sustained ~42% %-mod.
Empirically confirmed via `rh_model.simulate` over the author window (unattended CRF rises 0.004→0.99
of max). All deterministic 2A/2B tests pass.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 2A | ✅ faithful | ✅ faithful — contrast-gain left-shift, shared plateau, %-mod falls |
| panel 2B | ✅ faithful | ✅ faithful — response-gain upward-shift, sustained ~42% %-mod |
| **figure** | ✅ **faithful** | ✅ **faithful** |

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
%-mod bump and high-contrast convergence (unmod=5 baseline lifts the foot, CODE-017; CRF rises
0.235→0.99); 3F sustained separation (attended ~0.74 above ignored ~0.61) with %-mod largest at low
contrast declining to a ~20% plateau. All deterministic 3C/3F tests pass. Empirical (B/E) and config
(A/D) panels correctly "not reproduced".

> **Residue (low-severity, figure-scope):** the digitized JSON `notes` arrays still carry stale prose
> asserting the OLD `[0.01,1.0]` window (`figure_3/panel_C_digitized.json:373`, `panel_F:352`;
> `figure_4/panel_C:322`, `panel_E:309`). The `x_range` FIELD (what tests read) is correct and the
> adjacent re-digitization note supersedes the prose — not a referent error, but the contradictory
> sentence could mislead a future digitizer into re-introducing the wrong floor. Update/delete to the
> author window ([1e-5,1] for 3C/3F, [1e-4,0.1] for 4C/4E).

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 3C | ✅ faithful | ✅ faithful — interior %-mod bump, converges at high contrast |
| panel 3F | ✅ faithful | ✅ faithful — sustained separation, %-mod largest at low contrast |
| **figure** | ✅ **faithful** | ✅ **faithful** |

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

Both panels render over the author Figure4C/4E.m window `[1e-4, 0.1]` (CODE-018/CODE-020, window
verified faithful). **4C** follows the authors' released `Figure4C.m` (line 74 plots
`100*(unattCRF-attCRF)/unattCRF` — suppression sign, attended BELOW unattended). This produces the
OPPOSITE curve order from the published Fig-4C panel + caption ("percentage increase", attended-above);
the contradiction is logged OPEN as **DR-4C-sign** (owner=human, expiry 2026-07-15) — the code is
authoritative and C-021 prose sides with it, but a human must ratify before 4C is called reproduced.
**4E is the residual RED:** %-modulation overflows the paper's 0–100 axis to **~386%**. This is a
**two-stimulus GEOMETRY CODE_BUG**, not a forward-model divergence — the protocol co-locates two
stimuli at x=0 where Figure4E.m uses FOUR SEPARATED stimuli (RF x=90/110, contra x=−90/−110). The
author geometry through the *committed, unchanged* `simulate` yields ~52% (faithfulness_audit Finding
B), matching the digitized ~54%. Left RED, out of this pass's scope.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 4C | ✅ faithful | ⚠️ dispositioned — author suppression sign; published-panel sign is DR-4C-sign (human) |
| panel 4E | ✅ faithful | ❌ %-mod ~386% off-axis (two-stimulus GEOMETRY CODE_BUG, not the window) |
| **figure** | ✅ **faithful** | ❌ **divergent** (4E geometry RED; 4C pending DR-4C-sign) |

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
against the current digitized reference. **Contract caveat (DECISION NEEDED #2):** the 5C sweep
contrast is the `audited:false` 0.5 the author `Figure5C.m:19` contradicts (`contrast = 1`) — a
load-bearing provenance divergence that must be ratified before 5C is certified.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 5C | ✅ faithful | ❌ divergent — peak-ratio tier RED |
| **figure** | ✅ **faithful** | ❌ **divergent** (peak ratio; contrast provenance OPEN) |

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

Feature-based attention is spatially global (CODE_BUG fix), so the directional gain reaches the
recorded neuron: attend-contralateral is both taller (peak 1.0 vs fixation ~0.76) **and narrower
(sharpening present)** — the prior overlapping-curves failure is gone. Magnitude ~1.17–1.31 vs
digitized ~1.11 keeps the magnitude-ratio tier red (the author `Ashape='cross'` field is not
implemented; the oval approximation mildly overshoots — do NOT tune it). The spatial-globality
convention needs a named ledger assumption (**SQ-006**). **Contract caveat (DECISION NEEDED #2):** 6C
sweep contrast 0.5 vs author `Figure6C.m:21 contrast = 1`.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 6C | ✅ faithful | ❌ divergent — sharpening present, magnitude overshoot |
| **figure** | ✅ **faithful** | ❌ **divergent** (magnitude; contrast provenance OPEN) |

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
four separated). The author four-stimulus geometry through the committed `simulate` lands ~1.41
(faithfulness_audit Finding D), matching the digitized ~1.4 — faithful once the geometry is corrected.
Panel C is the sole deliverable (SQ-003, human-resolved); A/B "not reproduced". **Contract caveat
(DECISION NEEDED #2):** 7C sweep contrast 0.5 vs author `Figure7C.m:26 contrast = 1`.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 7C | ✅ faithful | ❌ divergent — ratio ~2.73 vs ~1.4 (geometry) |
| **figure** | ✅ **faithful** | ❌ **divergent** (geometry RED; contrast provenance OPEN) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 7C peak ordering variable>fixation>nonpref | ✅ pass |
| hard | 7C variable/fixation ratio vs digitized | ❌ **FAIL** |
| soft | 7C variable/nonpref ratio / shape vs digitized | ⚠️ soft |

---

## Potential sources of the issues

The forward model (`model.py`, Eqs. 5–6) is FAITHFUL operator-for-operator to the authors' MATLAB
(`paper/code/attentionModel/attentionModel.m`) — confirmed by two independent 2026-06-04 audits. Every
divergence is **protocol / figure / contract-scope**.

1. **CONTRACT — retired suppression knob still LIVE in the stage spec. OPEN (blocks contract).**
   `implementation/src/rh_model/stages/model_spec.yaml:116` declares
   `params: ["<protocol>.suppressive_drive_gain"]` — the RETIRED per-panel knob. It contradicts the
   SQ-005 resolution (no per-panel gain in the author code), the rewritten
   `test_contract_suppression_consistency.py` (asserts it resolves None everywhere), and
   `suppression.py` (docstring: retired, not read). See DECISION NEEDED #1.
   *Source:* `implementation/src/rh_model/stages/model_spec.yaml:116`;
   `implementation/src/rh_model/stages/suppression.py`; `logs/spec_questions.md` SQ-005.

2. **CONTRACT — 5C/6C/7C sweep contrast = 0.5 (audited:false) vs author 1.0. OPEN (blocks contract).**
   `article_aware/spec/calibration.yaml` `figure_{5C,6C,7C}.contrast = 0.5, audited:false` contradicts
   `Figure5C.m:19 / Figure6C.m:21 / Figure7C.m:26 contrast = 1`. Load-bearing (scales the whole tuning
   sweep), now resolvable from the same author-code lineage the c_range fix used. See DECISION NEEDED #2.
   *Source:* `article_aware/spec/calibration.yaml:559/594/629`; `paper/code/attentionModel/Figure{5C,6C,7C}.m`.

3. **CODE_BUG — Fig-4E / Fig-7C two-stimulus geometry (co-located vs four separated). RESIDUAL (RED).**
   4E/7C co-locate two stimuli at x=0; the author scripts use FOUR SEPARATED stimuli (RF x=90/110,
   contra x=−90/−110). Co-location lets feature competition crush the nonpreferred response, inflating
   4E %-mod to ~386% and the 7C var/fix ratio to ~2.73. The author geometry through the *committed,
   unchanged* `simulate` lands 4E ~52% and 7C ~1.41 (faithfulness_audit Findings B/D) — the faithful
   mechanism reaches the paper values once the geometry is corrected.
   *Source:* `paper/code/attentionModel/Figure4E.m`, `Figure7C.m`;
   `implementation/src/rh_model/protocols.py run_figure_4E / run_figure_7C`; `logs/faithfulness_audit/2026-06-04.md`.

4. **DECISION-REQUEST — DR-4C-sign (published Fig-4C vs model sign). OPEN (owner=human, expiry 2026-07-15).**
   The model follows `Figure4C.m:74` (suppression sign, attended below) — the OPPOSITE order from the
   published Fig-4C panel/caption ("percentage increase", attended above). Honestly logged as an open
   human decision-request, not silently adopted; ratify before 4C is called reproduced.
   *Source:* `logs/spec_questions.md`; `figures/figure_4/panel_C.md`; `Figure4C.m:74`.

5. **CONTRACT_BUG — clipped CRF contrast window (2A/2B/3C/3F/4C/4E). RESOLVED & VERIFIED FAITHFUL.**
   The sweep/view/digitized-x_range had pinned contrast to `[0.01,1]` (2 decades) while the author
   scripts use `[1e-5,1]` (4C/4E `[1e-4,0.1]`), clipping the rising limb + contrast-gain left-shift
   below 0.01. Fixed (no model change) by routing the author cRange (CODE-020) through
   `protocols._contrast_sweep`, the view `PAPER_PANEL_LIMITS`, and the re-digitized panel x_range (a
   pure x-axis relabel — overlay ink unchanged). Independently re-verified this pass: c_range values,
   ledger routing, view xlim, and re-labeled curve points all confirmed correct; the suppression-test
   rewrite and doc rewrite also confirmed faithful.
   *Source:* `article_aware/spec/code_refs.yaml` CODE-020; `article_aware/spec/calibration.yaml`
   `figure_*.c_range_*`; `implementation/src/rh_model/protocols.py`; `article_aware/views.py`;
   the panel `*_digitized.json`.

6. **CODE_BUG — feature attention spatially confined away from the recorded neuron (6C). Fixed earlier.**
   `run_figure_6C` is now feature-tuned in θ and flat/global in x (C-023), restoring 6C elevation +
   FWHM sharpening. The same factorization is owed to 7C's attend-nonpref (**SQ-006** — needs a named
   ledger assumption). A residual magnitude overshoot is a soft tripwire (`Ashape='cross'` not modeled).
   *Source:* `implementation/src/rh_model/protocols.py run_figure_6C/7C`; Fig-6 caption; SQ-006.

---

## Changelog

One line here; full detail in [`logs/changelog.md`](logs/changelog.md).

| Date | Change |
|---|---|
| 2026-06-04 | **from=fix finalize — BLOCKED on contract.** Window fix + suppression-test/doc rewrites independently VERIFIED FAITHFUL (model unchanged; Fig 2/3 full sigmoids). Paper-fix verify did NOT pass within MAX_PAPERFIX: 2 OPEN model-side contract divergences — retired `suppressive_drive_gain` still LIVE at `stages/model_spec.yaml:116`, and 5C/6C/7C sweep contrast 0.5 (audited:false) vs author `Figure*C.m contrast=1`. Both routed to human; exit `blocked:[model:contract]`, flagged_count 2. 4E/7C geometry + DR-4C-sign remain RED/open. |
| 2026-06-04 | Contrast-window CONTRACT_BUG + digitized re-digitization RESOLVED (author cRange [1e-5,1] / [1e-4,0.1] routed through sweep+view+x_range; model unchanged). 18→5 deterministic reds. |
| 2026-06-03 | Current-state rewrite: 8 magnitude flags traced to CONTRACT_BUG (per-panel suppression) + 6C CODE_BUG (fixed) + 4E divergence; SQ-005 escalated. |
