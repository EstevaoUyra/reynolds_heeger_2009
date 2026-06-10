# Reynolds & Heeger 2009 — The Normalization Model of Attention

<!-- CURRENT STATE — updated 2026-06-10. The Figure 6C CONTRACT_BUG correction (commit 862f4d7) is
     INDEPENDENTLY VERIFIED FAITHFUL: the new author `Ashape='cross'` field (model.py:284
     _build_attention_field_cross) was reproduced from scratch from the author MATLAB and is
     byte-identical to the impl (peak ratio 1.1088, FWHM ratio 0.8873). model.py is faithful and the
     'oval' default path (Figs 2/3/4/5/7) is untouched. BUT the paper-fix verify did NOT pass within
     MAX_PAPERFIX: the shipped/committed Figure 6 PNGs PREDATE the fix and still render the OLD
     over-scaled curve, contradicting the now-FAITHFUL header — a figure-scope divergence that cannot
     be re-rendered here (matplotlib absent). Exit = blocked on model:contract. -->

## Current exit

```json
{"overall": "blocked", "trajectory": "toward_paper", "flagged_count": 1, "blocked": ["model:contract"]}
```

## 👉 DECISION NEEDED

**Contract-blocked (paper-fix / audit-spec).** The paper-fix verify did NOT pass within
MAX_PAPERFIX. The Figure 6C CONTRACT_BUG fix (commit `862f4d7`) is **VERIFIED FAITHFUL** at the
model+numeric level (see below), and the 3 MUST-PASS contract tests are GREEN. The block is a single
**figure-scope** divergence: the **shipped/committed Figure 6 renders are STALE** — they predate the
fix and still show the OLD over-scaled curve, so a reader sees a FAITHFUL header over a divergent
image. **trajectory: toward_paper** (no leniency drift; the divergence was left RED, nothing
force-greened).

**The one open finding (flagged, not closed):**

- **F1 (figure) — STALE RENDERED ARTIFACT vs the now-FAITHFUL model.** The resolve commit `862f4d7`
  is 2026-06-10 05:52, but `implementation/figure_outputs/figure_6.png` is 04:57 (pre-commit), the
  README-displayed `figures_reproduced/figure_6.png` is Jun 4 13:57 (much older), and the overlay
  `article_aware/figures/figure_6/overlay_6C.png` is Jun 3 16:42. The committed panel C draws the
  attend-fixation gray curve peaking at ~0.855 under shared-max norm, i.e. peak ratio ~1/0.855 =
  **1.17 = the PRE-FIX over-scaled state**; the corrected model puts gray at ~1/1.108 = **0.903**
  (peak ratio 1.109). So the shipping image contradicts the README's FAITHFUL claim and the
  now-correct numeric text. The 2 panel-axes 6C tests (`test_panel_axes.py`) FAIL with
  `ModuleNotFoundError: No module named 'matplotlib'` — matplotlib is genuinely absent here, so the
  renders **cannot be regenerated in this environment**. The numeric contract is correct and the
  README TEXT is honest; only the displayed/committed PNGs are stale.
  *Fix:* re-render Figure 6 in an environment with matplotlib (`pip install matplotlib`, then
  regenerate `implementation/figure_outputs/figure_6.png`, `figures_reproduced/figure_6.png`, and
  `article_aware/figures/figure_6/overlay_6C.png`) and commit the refreshed artifacts so the panel
  shows the corrected curve (attend-fixation gray peak ~0.903, peak ratio 1.109). Verify by eye that
  the gray/blue peak ratio and widths match the digitized panel before re-asserting FAITHFUL. Until
  re-rendered, the FAITHFUL header is over-claimed relative to the shipped image.

**Where the model fix is verified (so the block is figure-only):** I independently reproduced
`Figure6C.m` + `attentionModel.m` + `makeGaussian.m` + `conv2sepYcirc.m` from scratch in standalone
Python — the author 'cross' field gives peak ratio 1.1088 / FWHM ratio 0.8873, and the impl
`run_figure_6C(n_directions=356)` returns **byte-identical** values (att-away peak 12.4528, att-RF
13.8076), matching digitized 1.108. `_build_attention_field_cross` (model.py:284) reduces to the
model_spec EQ-attention CROSS closed form to machine precision (max|Δ|=3.6e-15); the default 'oval'
path is allclose-identical with/without `shape:'cross'`, so Figs 2/3/4/5/7 are untouched. Provenance
is clean (ledger keys `figure_6C.stim_rf_x=100/stim_contra_x=-100/attend_fixation_x=0`, CODE-018,
all `audited:true`). SQ-006 and SQ-009 are genuinely RESOLVED.

**Where to look:**
- `logs/spec_audit/contract_audit_2026-06-10_paperfix_verify.md` — the paper-fix verify verdict.
- `logs/faithfulness_audit/2026-06-10-independent-rerender-v2.md`,
  `2026-06-10-rerender-and-author-verify.md` — the author-code reruns and 6C 'cross' verification.
- `logs/spec_questions.md` — **SQ-006** / **SQ-009** (6C 'cross' field, both RESOLVED).

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

### Figure 6 — Feature-based attention sharpening  ✅ model FAITHFUL · ⚠️ shipped render STALE (pre-fix curve)

<table>
<tr><th>Paper</th><th>Digitized</th><th>Implementation (STALE — pre-fix)</th></tr>
<tr><td><img src="article_aware/figures/figure_6.jpg" width="300"></td><td><img src="article_aware/figures/figure_6/overlay_6C.png" width="300"></td><td><img src="figures_reproduced/figure_6.png" width="300"></td></tr>
</table>

> **⚠️ The displayed Implementation panel is STALE (F1, DECISION NEEDED).** `figures_reproduced/figure_6.png`
> (Jun 4) and `implementation/figure_outputs/figure_6.png` (Jun 10 04:57) both PREDATE the resolve
> commit `862f4d7` (05:52) and still render the OLD over-scaled curve: attend-fixation gray peaks at
> ~0.855 (shared-max norm) → peak ratio ~1.17, the PRE-FIX state. The corrected model puts gray at
> ~0.903 (peak ratio 1.109). The MODEL is faithful (numbers below); only the PNGs are stale, and they
> cannot be regenerated here (matplotlib absent — re-render and commit, see DECISION NEEDED).

The 6C CONTRACT_BUG (2026-06-10) is **RESOLVED** via lineage rung 1 (this paper's own code). `run_figure_6C`
now honors the binding ledger geometry it already recorded — RF stimulus + recorded column at
`figure_6C.stim_rf_x=100`, contralateral / attend-opposite centre at `stim_contra_x=-100`, attend-fixation
at `attend_fixation_x=0` — and `build_attention_field` implements the author **`Ashape='cross'`** additive
separable spatial×feature field (`attentionModel.m:146-162`; `Figure6C.m` AxWidth=30, AthetaWidth=60,
CODE-018). The earlier flat-x full-γ proxy applied the θ-gain at full strength everywhere in x and
**over-scaled** (peak ratio ~1.167, FWHM ratio ~0.79). The faithful 'cross' field lands at the digitized /
author value with **no tuning**: peak ratio **1.109** (digitized 1.108, author 1.109) and FWHM ratio
**0.887** (digitized ~0.87 / author 'cross' 0.886–0.889), measured at the authors' native 1° sweep grid.
Sweep contrast is `1.0` (CODE-021, `Figure6C.m:21`).

> Note on the FWHM measurement: the FWHM helper is a simple grid-crossing measure; on the old coarse
> 25-point sweep both curves snapped to the same half-max sample. The model curve is resolution-independent
> (peak ratio 1.109 at every grid); the 6C tests measure on the authors' native 1° grid so the ~13°
> sharpening is resolved. This is a measurement-fidelity fix, not a model knob.

| | Digitization audit | Final figure (impl vs paper) |
|---|---|---|
| panel 6C (model/numeric) | ✅ faithful | ✅ faithful — author 'cross' field, peak 1.109 / FWHM ratio 0.887 |
| panel 6C (shipped render) | ✅ faithful | ⚠️ **STALE** — committed PNG shows pre-fix peak ratio ~1.17 (F1) |
| **figure** | ✅ **faithful** | ⚠️ **model faithful, render stale** (F1, re-render needed) |

| Tier | Check | Result |
|------|-------|--------|
| qualitative | 6C attended ≥ tall at peak · sharpening present | ✅ pass |
| MUST-PASS (CONTRACT_BUG) | 6C peak ratio 1.108±0.01 · FWHM ratio [0.87,0.89] · honors ledger geometry | ✅ pass (3/3) |
| soft | 6C 'cross' mechanism tripwire (proxy ≠ cross) | ✅ XPASS (resolved) |
| panel-axes (render) | 6C panel matches axis spec | ⚠️ FAIL — matplotlib absent (cannot re-render here) |

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
the 2026-06-10 paper-fix verify (the 6C 'cross' field was independently reproduced from author MATLAB,
byte-identical to the impl). Every open divergence is **figure-scope / contract-description**.

0. **FIGURE (F1) — STALE Figure 6 render vs the now-FAITHFUL model. THE CURRENT BLOCK (flagged_count 1).**
   `implementation/figure_outputs/figure_6.png` (Jun 10 04:57) and `figures_reproduced/figure_6.png`
   (Jun 4) PREDATE the resolve commit `862f4d7` (05:52) and render the OLD over-scaled curve (gray
   peak ~0.855, peak ratio ~1.17); the corrected model is peak ratio 1.109 (gray ~0.903). The PNGs
   cannot be regenerated here (matplotlib absent; `test_panel_axes.py` 6C tests FAIL with
   `ModuleNotFoundError`). *Fix:* re-render + commit Fig 6 (incl. `overlay_6C.png`) in a
   matplotlib env; verify by eye against the digitized panel. *Source:* `model.py:284`
   `_build_attention_field_cross`; `protocols.py run_figure_6C`; `Figure6C.m` / `attentionModel.m:146-162`;
   `code_refs.yaml` CODE-018; `logs/faithfulness_audit/2026-06-10-rerender-and-author-verify.md`.

The items below are **prior-pass contract findings, not re-litigated this pass** (they were the earlier
block; the current verify focused on 6C). They remain on record pending a fix-phase edit:

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

6. **MAGNITUDE — Fig-5 peak-ratio overshoot. Soft, structural, do NOT tune.**
   5C peak ratio ~1.17 vs ~1.2; mechanism faithful, oval-approximation residue. **6C is RESOLVED**
   (2026-06-10): the author `Ashape='cross'` field is now implemented in `build_attention_field` and
   `run_figure_6C` honors the binding ledger geometry (stim_rf_x=100 / stim_contra_x=-100 /
   attend_fixation_x=0), so 6C lands at the digitized/author peak ratio 1.109 and FWHM ratio 0.887 with
   no tuning (3 MUST-PASS contract tests green). Contrast provenance for 5C/6C/7C is resolved (CODE-021
   `contrast=1`). *Source:* `model.py _build_attention_field_cross`; `protocols.py run_figure_6C`;
   `Figure6C.m` / `attentionModel.m:146-162`; `code_refs.yaml` CODE-018/021.

---

## Changelog

One line here; full detail in [`logs/changelog.md`](logs/changelog.md).

| Date | Change |
|---|---|
| 2026-06-10 | **paper-fix verify — 6C model VERIFIED FAITHFUL, BLOCKED on stale render.** Commit `862f4d7` 'cross' field reproduced from scratch from author MATLAB, byte-identical to impl (peak 1.1088 / FWHM 0.8873; reduces to model_spec CROSS closed form, max\|Δ\|=3.6e-15; 'oval' path untouched, Figs 2/3/4/5/7 unaffected); 3 MUST-PASS contract tests GREEN; SQ-006/SQ-009 RESOLVED. Verify did NOT pass within MAX_PAPERFIX: F1 — the committed Figure 6 PNGs predate the fix (render OLD peak ratio ~1.17 vs corrected 1.109) and cannot be regenerated here (matplotlib absent). Exit `blocked:[model:contract]`, flagged_count 1, trajectory toward_paper. README refreshed: exit/DECISION/Fig-6 tables now flag the stale render; FAITHFUL header scoped to model+numeric. |
| 2026-06-10 | **Phase-A resolve — 6C CONTRACT_BUG RESOLVED (lineage rung 1, author code).** `build_attention_field` now implements the author `Ashape='cross'` additive separable spatial×feature field (`attentionModel.m:146-162`; default 'oval' path byte-identical, no other panel affected); `run_figure_6C` routed through the binding ledger geometry (RF/recorded column stim_rf_x=100, contra/attend-opposite stim_contra_x=-100, attend-fixation attend_fixation_x=0) instead of the invented -50/50 flat-x full-γ proxy. Peak ratio 1.167→**1.109** (digitized 1.108), FWHM ratio 0.79→**0.887** (band [0.87,0.89]) — no tuning. 3 MUST-PASS contract tests GREEN; soft 'cross' mechanism tripwire XPASS. 6C test FWHM measured at the authors' native 1° sweep grid (measurement-fidelity, not a model knob). 19 matplotlib-render test failures are a missing-dep environment issue, unrelated. |
| 2026-06-10 | **paper-fix verify — BLOCKED on contract.** F1/F2/F3 doc-vs-contract-drift fix VERIFIED FAITHFUL (model_spec Fig-3 baselines = CODE-017; figure_3.md/figure_4.md rewritten to author code; EQ-1/2/5/6 match attentionModel.m). Verify did NOT pass within MAX_PAPERFIX: 3 stale-contract findings remain DIVERGENT — **F-A** figure_3_protocol.md:16-18 still binds superseded A-007 0.05/0.05; **F-B** Fig-2/3 pseudocode describes a single-stim-x=0/[0.01,1] experiment vs author two-separated-stimulus/[1e-5,1] (SQ-002); **F-C** A-013(3) forbids the CODE-017 3C/3F baseline asymmetry. model.py untouched/faithful. DR-4C-sign RESOLVED (digitizer label swap; caption-authority carryover C1). Exit `blocked:[model:contract]`, flagged_count 3, trajectory toward_paper. |
| 2026-06-10 | Phase-A contract resolution of four blocked divergences (author-code grounded; model.py untouched): retired `suppressive_drive_gain` removed from stage spec; 5C/6C/7C sweep contrast 0.5→1.0 (CODE-021); 4E/7C author SEPARATED geometry adopted; DR-4C-sign investigated→code-resolvable. Added A-014. |
| 2026-06-04 | from=fix finalize — BLOCKED on contract. Window fix + suppression-test/doc rewrites VERIFIED FAITHFUL (Fig 2/3 full sigmoids). 2 OPEN model-side contract divergences routed to human. |
| 2026-06-04 | Contrast-window CONTRACT_BUG + digitized re-digitization RESOLVED (author cRange [1e-5,1] / [1e-4,0.1]; model unchanged). 18→5 deterministic reds. |
