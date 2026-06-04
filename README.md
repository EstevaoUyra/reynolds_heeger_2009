# Reynolds & Heeger 2009 — The Normalization Model of Attention

<!-- CURRENT STATE — updated 2026-06-04 after the SQ-005 fix pass (faithful author-code suppression
     mechanism implemented; per-panel suppression knobs deleted). Per-figure VLM verdicts below
     PRE-DATE this pass (HEAD c8ea505) and are stale where they describe the old per-panel-gain CRFs;
     the deterministic test state in "Current exit" is current. -->

## Current exit

```json
{"overall": "partial", "trajectory": "toward_paper", "flagged_count": 3, "blocked": []}
```

**The SQ-005 suppression mechanism is now IMPLEMENTED from the original author code.** The model is
the authors' separable space×feature normalization — unit-volume (normpdf) suppressive kernels
(IxWidth=20, IthetaWidth=360 near-flat θ pool), `conv2sepYcirc` (zero-pad x, circular θ), σ=1e-6,
on the code grid (spacing 1) — with **NO per-panel suppression gain or width scale** (all the
SQ-001/SQ-002 per-figure knobs are deleted). Figure 1 (the authors' own activity-map render) is
**fully green** (10/10 must-pass; the R-asymmetry tripwire correctly xfails), and every CRF
**saturation** and **response-gain** must-pass passes — the faithful mechanism is validated.

Deterministic state: **116 passed / 19 failed** (was 127 failed before this pass). The 19 reds are
**three named contract-level gaps** (`logs/spec_questions.md` **SQ-007**), none fixable by a
paper-blind builder without forbidden tuning — left RED and escalated, not forced:

### Queued human decisions (route to Phase A / Faithfulness Auditor — not for a paper-blind builder)

1. **SQ-007 Gap 1 — CRF contrast-axis mismatch (14 reds: 2A/2B/3C/3F/4C half-max & left-shift,
   tier-shape).** The faithful mechanism's single-grating CRF half-saturates at c ≈ 0.002–0.005 — its
   contrast-gain left-shift is REAL but sits BELOW the digitized window [0.012, 1], where the curve is
   already a flat plateau; the digitized references put the rise at c ≈ 0.05–0.10 (~20–30× higher). No
   σ closes it (σ=1e-6 → half-max below window; σ≈0.1 → half-max ≈0.5 AND the left-shift collapses).
   Decide: the per-figure `Figure*.m` CRF scripts likely use a contrast/σ convention that is NOT the
   Fig-1 activity-map R1 config — SQ-005's σ=1e-6 may hold only for the activity maps, not the CRF
   panels. Phase B cannot read those scripts.
2. **SQ-007 Gap 2 — `test_contract_suppression_consistency.py` encodes the wrong shape of fix (5 reds).**
   It requires a single NON-None `suppressive_drive_gain` resolved on every panel ("promote ONE
   constant"); the SQ-005 resolution settled from code that NO per-panel gain exists at all, so the
   faithful model resolves None everywhere. The mechanism satisfies the test's INTENT (one global
   suppression normalization, identical on every panel) but not its LETTER. Rewrite the predicate to
   "no per-panel gain anywhere; the global suppressive σ/θ are identical across panels."
3. **SQ-007 Gap 3 — Fig-4E / Fig-7C over-modulation magnitude (3 reds, tier="hard").** The faithful
   2-stimulus-in-RF mechanism over-modulates (4E %-mod ~386% vs digitized ~54%; 7C ratio 2.73 vs
   1.33). Genuine divergences (the 7C test's own `paper_issue` says so) but tagged MUST-PASS rather
   than soft/xfail tripwires; reclassify or supply a verified faithful target.
4. **SQ-006 — "feature-based attention is spatially global" needs a named ledger assumption.** The
   Fig-6C CODE_BUG fix is applied and green-on-its-own-tests, but the convention is only *implied* by
   C-023; Phase A should formalize the assumption and apply the same factorization to 7C.
5. **Closed:** SQ-001/SQ-002 (per-panel suppression gains/baselines) — **RESOLVED this pass**: deleted,
   replaced by the single author-code mechanism. SQ-003 (Fig-7 = Panel C), SQ-004 (4C 75° override
   retired), SQ-005 (suppression mechanism resolved from code) — closed. Listed so a returning reader
   sees they are done.

---

## Model

Reynolds JH, Heeger DJ. **The Normalization Model of Attention.** *Neuron.* 2009 Jan 29;61(2):168–185. doi:[10.1016/j.neuron.2009.01.002](https://doi.org/10.1016/j.neuron.2009.01.002) (PMCID PMC2752446).

The foundational **normalization model of attention**: one divisive-normalization circuit explains
contrast-gain vs response-gain modulation, multiplicative tuning-curve scaling, feature-based
sharpening, and tuning shifts with two stimuli in the receptive field. A population indexed by
RF center `x` and feature preference `θ` receives an excitatory **stimulus drive** `E(x,θ)`, is
gated by a multiplicative **attention field** `A(x,θ) ≥ 1`, and is divisively normalized by a pooled
**suppressive drive** `S(x,θ)`. The central claim is that the *shape* of attentional modulation is
not a free parameter — it emerges from the relative size of the attention field and the stimulus.

Per neuron, the rectified divisive-normalization response (Eq. 5):

```
R(x,θ) = ⌊ A(x,θ)·E(x,θ) / (S(x,θ) + σ) ⌋_T
```

with the suppressive drive the suppressive field convolved with the *attention-modulated* drive (Eq. 6),
`S = s ∗ [A·E]`, the kernel `s` integral-normalized (Eq. 2, `∫ s dx dθ = 1`), and the attention field
a Gaussian bump `A = 1 + (γ−1)·G`, peak gain `γ`. Because the same product `A·E` sits in numerator and
(after pooling) denominator, growing the attention field relative to the stimulus moves the modulation
continuously from a contrast-gain to a response-gain signature. **The equations map operator-for-operator
to the paper and are faithful** (verified in `implementation/src/rh_model/model.py`); the divergences
below are in the model's *quantitative output* — realized gains and saturation — not the transcription.

Scope: 7 figures. Fig 1 is the schematic; Figs 2–7 are live `protocols.run_figure_*` → `measurements`
→ Phase-A `views` computations (no constructed stub). Empirical and config sub-panels are explicit
"not reproduced" placeholders.

---

## Reproduced figures — paper · digitized · implementation

Each figure is shown three ways: **paper** (the original panel), **digitized** (the tool-grounded
digitized curves drawn on the paper pixels — the audited reference the tests compare against,
`logs/digitization_audit/`), and **implementation** (the live model through the same pinned-axis view).
Two checks per figure: the **digitization audit** (separate critic, paper vs digitization) and the
**final-figure VLM** (implementation vs paper — fresh parent direct read at HEAD c8ea505, the verdict
of record). Then the deterministic **tier** tables (qualitative + hard *gate*; soft *reported, never
blocks*). A figure is **green only if deterministic all-pass AND fresh VLM pass**.

### Figure 1 — Pipeline schematic  ✅ FAITHFUL (det all-pass · VLM pass)

<table><tr><th>Paper</th><th>Implementation</th></tr><tr><td><img src="article_aware/figures/figure_1.jpg" width="430"></td><td><img src="figures_reproduced/figure_1.png" width="430"></td></tr></table>

The `E × A ÷ S → R` pipeline: stimulus drive (two bands) × a localized attention field over the
attended (right) stimulus, ÷ the pooled suppressive drive → an output that **enhances the attended
band relative to the left**. Topology and iconography match the Fig-1 caption. (Schematic: no data
curve to digitize.) The May-2018 "Fig 1 broken / fields compressed near center" adjudications are
**superseded** — the current render shows correct hemifield structure (parent direct read, recorded
in `logs/figure_comparisons/figure_1_20260604T012601Z.json`).

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| **figure** | n/a (schematic) | ✅ **faithful** — topology + attended-stimulus enhancement match |

### Figure 2 — Contrast gain vs response gain  ❌ BROKEN — 2A under-saturates; 2B ceiling RED

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_2.jpg" width="300"></td><td><img src="article_aware/figures/figure_2/overlay_2A.png" width="150"><img src="article_aware/figures/figure_2/overlay_2B.png" width="150"></td><td><img src="figures_reproduced/figure_2.png" width="300"></td></tr>
</table>

2A is contrast-gain (attended above ignored, %-mod falls toward high contrast) but the CRFs plateau
~0.34 against the paper's ~0.62 (**under-saturation**, surfaced once the shared-scale normalization
stopped pinning every panel to 1.0). 2B is response-gain (separation sustained, attended ~0.86 above
ignored ~0.60) but the attended ceiling diverges from the digitized reference (deterministic RED).

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 2A | ✅ faithful | ❌ divergent — plateau ~0.34 vs ~0.62 |
| panel 2B | ✅ faithful | ❌ divergent — attended ceiling off digitized (0.277 bound) |
| **figure** | ✅ **faithful** | ❌ **divergent** (VLM fail) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 2A attended ≥ ignored / converges / %-mod falls | ✅ pass |
| qualitative | 2B attended above ignored / no convergence | ✅ pass |
| hard | 2A / 2B high-contrast separation vs digitized | ✅ pass |
| hard | 2B attended ceiling matches digitized | ❌ **FAIL** — `0.277 < 0.15` false |
| soft | 2A / 2B shape & low-contrast modulation vs digitized | ⚠️ soft (skipped/reported) |

### Figure 3 — Baseline shift across contrast  ❌ BROKEN — residual over-separation (VLM needs_review)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_3.jpg" width="300"></td><td><img src="article_aware/figures/figure_3/overlay_3C.png" width="150"><img src="article_aware/figures/figure_3/overlay_3F.png" width="150"></td><td><img src="figures_reproduced/figure_3.png" width="300"></td></tr>
</table>

Direction faithful: 3C attend-in-RF above contralateral with an interior %-mod bump and high-contrast
convergence; 3F sustained separation, %-mod largest at low contrast. No hard deterministic fail — all
fig-3 failing rows are **skipped soft shape checks** — but the CRFs read over-separated through the
low/mid range vs the paper, so the figure is det-green-but-VLM-`needs_review`, not green. Empirical
(B/E) and config (A/D) panels correctly "not reproduced".

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 3C | ✅ faithful | ⚠️ over-separated low/mid; %-mod bump present |
| panel 3F | ✅ faithful | ⚠️ separation larger than paper |
| **figure** | ✅ **faithful** | ❌ **divergent** (VLM needs_review, soft shape) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 3C above/converge · 3F above/persist | ✅ pass |
| hard | 3C / 3F high-contrast separation vs digitized | ✅ pass |
| soft | 3C %-mod interior bump | ✅ pass |
| soft | 3C / 3F shape vs digitized; 3F %-mod-low | ⚠️ soft (skipped/reported) |

### Figure 4 — Two-stimulus contrast-response modulation  ❌ BROKEN — 4E 390% overflow + 4C +101% (RED)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_4.jpg" width="300"></td><td><img src="article_aware/figures/figure_4/overlay_4C.png" width="150"><img src="article_aware/figures/figure_4/overlay_4E.png" width="150"></td><td><img src="figures_reproduced/figure_4.png" width="300"></td></tr>
</table>

4C **direction is now faithful** (facilitation / left-shift, after the spatial-attention remap that
retired SQ-004) but its %-modulation pins near +101% vs the paper's ~36% and the CRFs do not converge
at high contrast. 4E is the headline divergence: attend-preferred ~0.85 above attend-nonpreferred
(crushed ~0.15), %-modulation overflowing the paper's 0–100 axis to **~390%** — a hard gate failure
the pinned-axis test catches (the old auto-scaled view hid it). 4E is a **GENUINE_DIVERGENCE**: it
survives even a unified suppression gain (stays ~360–390% at gain 40), emergent from γ=5 two-stimulus
feature competition driving the nonpreferred response near zero.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 4C | ✅ faithful | ❌ +101% mod / no convergence (direction faithful) |
| panel 4E | ✅ faithful | ❌ %-mod ~390% off-axis |
| **figure** | ✅ **faithful** | ❌ **divergent** (VLM fail) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 4C facilitation direction · 4E attend-pref above nonpref | ✅ pass |
| hard | 4C CRFs saturate / gap narrows at high contrast | ❌ **FAIL** — gap doesn't narrow |
| hard | 4C %-mod peak matches digitized | ❌ **FAIL** — `64.8 < 12` false |
| hard | 4C / 4E data within paper 0–100 axis | ❌ **FAIL** — right-axis overflow |
| hard | 4E %-mod stays within paper axis | ❌ **FAIL** — `389.9 < 73.8` false |
| soft | 4C / 4E shape & separation vs digitized | ⚠️ soft (skipped/reported) |

### Figure 5 — Spatial attention as multiplicative scaling  ❌ BROKEN — peak ratio 1.59× vs ~1.2 (RED)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_5.jpg" width="300"></td><td><img src="article_aware/figures/figure_5/overlay_5C.png" width="300"></td><td><img src="figures_reproduced/figure_5.png" width="300"></td></tr>
</table>

The right *kind* of effect — multiplicative, same-width scaling (attend-in-RF and contralateral share
FWHM, no sharpening) — but the attended/unattended **peak ratio is ~1.59 (1.0 vs ~0.63) against the
paper's ~1.2**: spatial-attention gain too strong. Empirically, unifying the suppressive gain to 12
drops this ratio 1.586→1.215 (the paper value) — direct evidence the cause is the per-panel
suppression inconsistency, since the tuning protocols (5/6/7) apply *no* gain while CRF panels apply 6–12.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 5C | ✅ faithful | ❌ divergent — ratio ~1.59 vs ~1.2 |
| **figure** | ✅ **faithful** | ❌ **divergent** (VLM fail) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 5C attended above unattended · same width, no sharpening | ✅ pass |
| hard | 5C peak ratio vs digitized | ❌ **FAIL** — `0.43 < 0.15` false |
| soft | 5C shape / unattended peak vs digitized | ⚠️ soft (skipped/reported) |

### Figure 6 — Feature-based attention sharpening  ❌ BROKEN — sharpening now PRESENT but 1.31× overshoot (RED)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_6.jpg" width="300"></td><td><img src="article_aware/figures/figure_6/overlay_6C.png" width="300"></td><td><img src="figures_reproduced/figure_6.png" width="300"></td></tr>
</table>

**Improved this pass (CODE_BUG fix, HEAD c8ea505).** Feature-based attention is now spatially global,
so the directional gain reaches the recorded neuron: attend-contralateral is both taller (peak 1.0 vs
fixation ~0.76) **and narrower (sharpening present)** — the prior overlapping-curves failure (ratio
~1.01, no sharpening) is gone. But the peak elevation **~1.31 overshoots the digitized ~1.11**, so the
magnitude ratio test stays red. Direction now faithful; magnitude divergent (not tuned — the overshoot
is what the intended-failure tripwire predicted).

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 6C | ✅ faithful | ❌ divergent — sharpening present, ratio ~1.31 vs ~1.11 |
| **figure** | ✅ **faithful** | ❌ **divergent** (VLM fail) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 6C attended ≥ tall at peak · sharpening present | ✅ pass (sharpening now passes) |
| hard | 6C peak ratio vs digitized | ❌ **FAIL** — `0.20 < 0.06` false |
| soft | 6C flank difference / shape vs digitized | ✅ pass / ⚠️ soft (skipped) |

### Figure 7 — Two stimuli in RF: combined attention shifts  ❌ BROKEN — variable/fixation 3.3× vs ~1.4 (RED)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation</th></tr>
<tr><td><img src="article_aware/figures/figure_7.jpg" width="300"></td><td><img src="article_aware/figures/figure_7/overlay_7C.png" width="300"></td><td><img src="figures_reproduced/figure_7.png" width="300"></td></tr>
</table>

Ordering faithful (attend-variable > ignored/fixation > attend-nonpreferred) but attend-variable peaks
1.0 while fixation peaks only ~0.30 → **variable/fixation ratio ~3.3 vs the paper's ~1.4**: combined
attention gain more than twice too strong. Same suppression-inconsistency family as 5C; the
attend-nonpref condition also inherits the 6C spatial-confinement structure (SQ-006). Panel C is the
sole deliverable (SQ-003, human-resolved); A/B "not reproduced".

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 7C | ✅ faithful | ❌ divergent — ratio ~3.3 vs ~1.4 |
| **figure** | ✅ **faithful** | ❌ **divergent** (VLM fail, Panel-C scoped) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 7C peak ordering variable>fixation>nonpref | ✅ pass |
| hard | 7C variable/fixation ratio vs digitized | ❌ **FAIL** — `1.95 < 0.3` false |
| soft | 7C variable/nonpref ratio / shape vs digitized | ⚠️ soft (skipped/reported) |

> **Test surface note.** The latest `logs/test_runs.jsonl` rows are stamped at `3a64105` (one commit
> behind HEAD `c8ea505`); the test surface still matches HEAD (the 6C CODE_BUG tests are present and
> the 6C sharpening row is green as the HEAD fix predicts), so this is stale-*metadata*, not
> stale-*data*. The model verdicts are unaffected.

---

## Potential sources of the issues

Built from the findings' `source_hint`s. The eight flags collapse to **three mechanism root causes**
plus two figure-specific issues.

1. **CONTRACT_BUG — under-normalizing 1D suppression, patched per-panel (the cross-figure root cause of
   2A, 3C, 3F, 4C, 5C, 7C).** The 1D suppressive pool under-normalizes, so CRFs/tuning curves do not
   saturate; the implementation compensates with **figure-fitted per-panel knobs**:
   `figure_*.suppressive_drive_gain` = 2A 12 / 2B 6 / 3C 8 / 3F 12 / 4C 8 / 4E 8 (tuning panels 5C/6C/7C
   apply *none*), and `suppressive_spatial_sigma_scale` 0.55 / 1.0 / 0.45 / 0.7, plus per-panel Fig-3
   baselines (0.005). The paper has ONE model, ONE σ, NO per-figure suppression gain. Filed in the
   contract (A-006/A-013) which forbids these knobs; `test_contract_suppression_consistency.py` encodes
   it MUST-PASS and is **RED today (4 tests)** — Phase B has *not* implemented the fix
   (`implementation/calibration.yaml` still carries every per-panel entry; `protocols.py` reads them).
   The CRF panels read `i['suppressive_drive_gain']`; `run_figure_5C/6C/7C` pass none — that
   inconsistency *is* the bug. Empirically, unifying the gain to 12 drops 5C's ratio 1.586→1.215 (the
   paper value).
   *Fix (A-006 binding spec):* compute S on the paper's 2D image plane (`s` integral-normalized over
   `dx dy dθ`, single cited `suppressive_field_size=20`, `suppressive_tuning_width=180°`) and DELETE
   every per-panel gain / sigma-scale / baseline; or, if a 1D stand-in is kept, promote ONE audited
   `model.suppression_normalization` constant identical across all panels — and apply it to the tuning
   protocols too. **Caveat (SQ-005):** Phase B falsified the 2D-plane geometry (it makes S *smaller*),
   so the binding spec itself needs Phase-A disposition before a builder can act.
   *Source:* `article_aware/spec/assumptions.yaml` A-006/A-013; `test_contract_suppression_consistency.py`;
   `implementation/calibration.yaml figure_*.suppressive_drive_gain`; `implementation/src/rh_model/protocols.py`.

2. **CODE_BUG — feature attention spatially confined away from the recorded neuron (6C, and 7C
   attend-nonpref).** `run_figure_6C` built the attend-opposite condition as a spatial Gaussian at
   x=−50 × a feature Gaussian; since `A = 1+(γ−1)·G_x·G_θ` and the recorded neuron is at x=0, `G_x≈0`
   there, so `A≈1` regardless of θ — feature attention never reached the neuron and the curves overlapped
   (ratio ~1.01, no sharpening). The paper's feature attention is spatially **global**. **Fixed this pass**
   (HEAD c8ea505): the condition is feature-tuned in θ, flat/global in x, restoring peak elevation
   1.01→1.31 and FWHM sharpening 133°→104°. The same spatial-confinement structure should be applied to
   7C's attend-nonpref (SQ-006 — still needs a named ledger assumption; `pseudocode/figure_6_protocol.md`
   still prescribes the confined build).
   *Source:* `implementation/src/rh_model/protocols.py run_figure_6C/7C`; Fig-6 caption; `article_aware/figures/figure_6/panel_C.jpg`.

3. **GENUINE_DIVERGENCE — 4E % modulation overflow (~310–390%).** With γ=5 (Table-1, faithful) and
   feature-tuned attention, attend-preferred vs attend-nonpreferred yields %-modulation far past the
   paper's 0–100 axis. Ordering is faithful. **NOT** resolved by the suppression-gain fix (stays
   ~360–390% even at gain 40) — emergent from γ=5 two-stimulus feature competition driving the
   attend-nonpref response near zero. Either the paper's readout/normalization differs or the
   two-stimulus feature mechanism is too strong here.
   *Source:* Table 1 (4E: γ=5, tuning width 20°); Fig-4E caption (0–100 %-mod axis); lineage
   Martinez-Trujillo & Treue 2002 / Treue & Martinez-Trujillo 1999; `run_figure_4E` (%-mod max = 390).

4. **2A under-saturation** and **3C/3F shape** are downstream of root cause #1 (the 1D pool not growing
   enough with contrast); they resolve when the single-suppression-normalization fix lands.
   **6C/5C/7C magnitude overshoots** are #1 (gain inconsistency) plus, for 6C/7C, the residual feature
   factorization of #2.

---

## Changelog

One line here; full detail in [`logs/changelog.md`](logs/changelog.md).

| Date | Change |
|---|---|
| 2026-06-03 | Current-state rewrite: 8 magnitude flags traced to CONTRACT_BUG (per-panel suppression) + 6C CODE_BUG (fixed, sharpening restored) + 4E GENUINE_DIVERGENCE; fresh VLM at HEAD c8ea505 (Fig 1 pass, 2/4/5/6/7 fail, 3 needs_review); SQ-005 escalated. |
