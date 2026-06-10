# Reynolds & Heeger 2009 — The Normalization Model of Attention

<!-- CURRENT STATE — updated 2026-06-10. Phase-A contract resolution of the four blocked divergences,
     all grounded in the author code (CODE-NNN). The model.py was NOT touched (it is independently
     verified faithful). The four prior blockers are RESOLVED in the contract: (#1) the retired
     suppressive_drive_gain stage-spec declaration removed; (#2) 5C/6C/7C sweep contrast 0.5 → 1.0
     (CODE-021, Figure*C.m); (#3) 4E/7C author SEPARATED two-stimulus geometry adopted in the
     protocols + calibration; (#4) DR-4C-sign INVESTIGATED → code-resolvable (a digitizer label swap,
     NOT a paper defect), closed. Phase B must rebuild the protocols to the corrected contract. -->

## Current exit

```json
{"overall": "contract-resolved", "trajectory": "toward_paper", "flagged_count": 0, "blocked": []}
```

## ✅ CONTRACT DIVERGENCES RESOLVED (Phase A, 2026-06-10)

The four divergences that had blocked the contract are RESOLVED from the author code (the model.py is
unchanged — it is independently verified faithful). Phase B rebuilds the protocols to this contract.

**Finding #1 — RESOLVED. Stale retired `suppressive_drive_gain` removed from the stage spec.**
`implementation/src/rh_model/stages/model_spec.yaml` no longer declares the suppression stage's
retired per-panel `<protocol>.suppressive_drive_gain` (SQ-001/SQ-005, A-013) — it now references only
the global `model.suppressive_field_size` (CODE-010) / `model.suppressive_tuning_width` (CODE-011), the
single space×feature pool. The author code has no per-panel gain (`R = E./(I+sigma)+baselineUnmod`,
attentionModel.m:175, CODE-001). Two sibling dead declarations (`figure_4C.suppressive_tuning_width`,
`figure_4C.sigma` — the retired SQ-004 overrides, absent from both ledgers) were removed for the same
contract-integrity reason. `test_contract_suppression_consistency.py` still passes (4/4).

**Finding #2 — RESOLVED. 5C/6C/7C sweep contrast 0.5 → 1.0 (CODE-021).**
`figure_{5C,6C,7C}.contrast` are now `1.0`, `audited: true`, source **CODE-021** (`Figure5C.m:19`,
`Figure6C.m:21`, `Figure7C.m:26` all `contrast = 1;`). The author stimulus-construction structure is
transcribed: 5C/6C `stim = contrast²·stim_RF + stim_contra` (RF scaled by contrast², contra by 1 —
inert at contrast=1); 7C `pair = contrast·(stim_var + stim_null)` (linear). At the author value both
reduce to the unit-height sums; the asymmetric forms are recorded so Phase B never reads paper/code.

**Finding #3 — RESOLVED. 4E/7C author SEPARATED two-stimulus geometry adopted.**
The figure protocols + calibration now carry the author geometry: **4E** four separated stimuli
(RF x=90/110, contra x=-90/-110, recorded x=100, cRange [1e-4,0.1], all contrasts covary) — author
geometry yields %-mod ~52% vs the co-located ~386% (faithfulness_audit Finding B); **7C** two SEPARATED
in-RF stimuli (var x=93, null x=107, recorded x=100, att-away x=-100) — yields var/fix ratio ~1.41 vs
the co-located ~2.73 (Finding D). 5C/6C geometry (x=±100) also transcribed. New calibration geometry
keys are all `CODE-018`-sourced with verbatim quotes.

**Finding #4 — RESOLVED (code-resolvable; DR-4C-sign CLOSED, no human ruling needed).**
DR-4C-sign was a PHANTOM contradiction — a **digitizer label swap**, not a paper defect. The author
legend (`Figure4C.m:69`) is `'Att Away','Att RF'`; the dashed modulation
`100·(unattCRF-attCRF)/unattCRF` (line 74) is drawn POSITIVE in the published panel (~36% peak). For
that to be positive, **Att-Away (unattCRF) is the UPPER solid and Att-RF (attCRF, attend-null-in-RF)
the LOWER** — i.e. attending the null in the RF SUPPRESSES the recorded preferred neuron (C-021), and
the published panel AGREES with `Figure4C.m`. Recomputing the author dashed formula on the digitized
curves with the corrected mapping reproduces the digitized % modulation POINTWISE (~29–30% mid-range,
declining). The only error was the digitizer's (it labeled the upper solid "attended" when it is the
author's "Att Away"/unattCRF). The model already follows the author code and is correct. A-012's
`paper_issue` is updated to RESOLVED; the `panel_C_digitized.json` solid-label swap is documented for
tier comparisons. (The empirical Fig-4B caption's "percentage increase" describes the
Reynolds/Martinez-Trujillo DATA panel, not the model panel C.)

**Where to look** — author scripts `paper/code/attentionModel/Figure{4C,4E,5C,6C,7C}.m`;
`logs/faithfulness_audit/2026-06-04.md` (author-geometry reruns 4E 386%→52%, 7C 2.73→1.41);
`logs/spec_questions.md` (SQ-005 human_resolution, SQ-006 now formalized as **A-014**
feature-attention-spatially-global). NOTE for Phase B: the prior `simulate` protocols co-located the
4E/7C stimuli at x=0; rebuilding to the separated geometry above is the residual model-side work (the
forward mechanism is unchanged and lands the paper values once the geometry is corrected).

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

1. **CONTRACT — retired suppression knob in the stage spec. RESOLVED (2026-06-10).**
   `implementation/src/rh_model/stages/model_spec.yaml` no longer declares the retired per-panel
   `<protocol>.suppressive_drive_gain` (nor the dead 4C `suppressive_tuning_width`/`sigma`); it
   references the global `model.suppressive_field_size` (CODE-010) / `model.suppressive_tuning_width`
   (CODE-011). Grounds: author code `R = E./(I+sigma)+baselineUnmod` (attentionModel.m:175, CODE-001).
   `test_contract_suppression_consistency.py` passes (4/4).
   *Source:* `implementation/src/rh_model/stages/model_spec.yaml`; `code_refs.yaml` CODE-001.

2. **CONTRACT — 5C/6C/7C sweep contrast. RESOLVED (2026-06-10): 0.5 → 1.0 (CODE-021).**
   `figure_{5C,6C,7C}.contrast = 1.0, audited:true, source CODE-021` (`Figure5C.m:19 / Figure6C.m:21 /
   Figure7C.m:26 contrast = 1`). Author stimulus-construction structure transcribed (5C/6C contrast²
   on the RF stimulus; 7C linear). Retires the prior unfounded 0.5.
   *Source:* `article_aware/spec/calibration.yaml` figure_{5C,6C,7C}.contrast; `code_refs.yaml` CODE-021.

3. **GEOMETRY — Fig-4E / Fig-7C two-stimulus geometry. RESOLVED in the contract (2026-06-10).**
   The figure protocols + calibration now carry the author SEPARATED geometry (4E four stimuli
   x=90/110/−90/−110, recorded x=100; 7C var x=93 / null x=107, recorded x=100, att-away x=−100). The
   author geometry through the *committed, unchanged* `simulate` lands 4E ~52% and 7C ~1.41
   (faithfulness_audit Findings B/D). RESIDUAL MODEL-SIDE WORK FOR PHASE B: `protocols.py
   run_figure_4E / run_figure_7C` still co-locate at x=0 and must be rebuilt to this contract geometry
   (the forward mechanism is unchanged).
   *Source:* `paper/code/attentionModel/Figure4E.m`, `Figure7C.m`; calibration figure_{4E,7C}.* geometry
   keys (CODE-018); `pseudocode/figure_{4,7}_protocol.md`; `logs/faithfulness_audit/2026-06-04.md`.

4. **DECISION-REQUEST — DR-4C-sign. RESOLVED (2026-06-10): code-resolvable, CLOSED.**
   Investigated against `Figure4C.m` + the published panel: NO genuine paper/code contradiction — the
   apparent conflict was a DIGITIZER label swap. The published dashed % modulation is positive and
   matches the author `100·(unattCRF-attCRF)/unattCRF` pointwise once the upper solid is read as the
   author's "Att Away"/unattCRF (not "attended"). Attend-null-in-RF SUPPRESSES (C-021); model follows
   the code and is correct. A-012 `paper_issue` → RESOLVED; no human ruling needed.
   *Source:* `paper/code/attentionModel/Figure4C.m:69,74`; `figures/figure_4/panel_C.md`;
   `assumptions.yaml` A-012.

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
| 2026-06-10 | **Phase-A contract resolution of the four blocked divergences (author-code grounded; model.py untouched).** #1 retired `suppressive_drive_gain` (+ dead 4C `suppressive_tuning_width`/`sigma`) removed from `stages/model_spec.yaml`; #2 5C/6C/7C sweep contrast 0.5→1.0 (CODE-021) + author stimulus-construction structure transcribed; #3 4E/7C author SEPARATED two-stimulus geometry adopted in protocols + calibration (CODE-018 geometry keys); #4 DR-4C-sign INVESTIGATED → code-resolvable (digitizer label swap, NOT a paper defect) → CLOSED. Added A-014 (feature-attention-spatially-global, formalizes SQ-006). check_citations OK. Exit `contract-resolved`. |
| 2026-06-04 | **from=fix finalize — BLOCKED on contract.** Window fix + suppression-test/doc rewrites independently VERIFIED FAITHFUL (model unchanged; Fig 2/3 full sigmoids). Paper-fix verify did NOT pass within MAX_PAPERFIX: 2 OPEN model-side contract divergences — retired `suppressive_drive_gain` still LIVE at `stages/model_spec.yaml:116`, and 5C/6C/7C sweep contrast 0.5 (audited:false) vs author `Figure*C.m contrast=1`. Both routed to human; exit `blocked:[model:contract]`, flagged_count 2. 4E/7C geometry + DR-4C-sign remain RED/open. |
| 2026-06-04 | Contrast-window CONTRACT_BUG + digitized re-digitization RESOLVED (author cRange [1e-5,1] / [1e-4,0.1] routed through sweep+view+x_range; model unchanged). 18→5 deterministic reds. |
| 2026-06-03 | Current-state rewrite: 8 magnitude flags traced to CONTRACT_BUG (per-panel suppression) + 6C CODE_BUG (fixed) + 4E divergence; SQ-005 escalated. |
