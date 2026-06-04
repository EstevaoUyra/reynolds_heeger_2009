# Faithfulness audit — Reynolds & Heeger 2009 (2026-06-04, independent re-render)

Independent post-build faithfulness pass. Branch `fix/sq005-from-code-20260604`.
Figures re-rendered fresh from the committed model (`rh_model.views.main`). Audited
against the paper (`paper/extracted_text.md`, figure JPGs) AND the author's released
MATLAB (`paper/code/attentionModel/*.m`) — the decisive lineage resolver. Every
divergence was reproduced or refuted by re-running each `Figure*.m` geometry through
the committed `simulate`.

This pass independently re-derives and CONFIRMS `logs/faithfulness_audit/2026-06-04.md`.
The two passes were run separately and converge on the same conclusions; the
corroboration is recorded here, plus one additional README-staleness finding.

## Headline

**The forward model (`implementation/src/rh_model/model.py`) is FAITHFUL** —
operator-for-operator with Eqs. 5/6 and byte-faithful to `attentionModel.m`
(σ=1e-6, separable space×feature `conv2sepYcirc`, unit-volume normpdf kernels,
ExWidth=5/EthetaWidth=60/IxWidth=20/IthetaWidth=360, Apeak=2, 3C/3F baselines).
There is NO per-panel suppression knob (calibration.yaml confirms they are deleted).

Every paper panel is reproduced to its paper/digitized value when the model is run
with the AUTHOR'S exact per-figure geometry. All live divergences are **figure-scope
CONTRACT/CODE bugs in the protocols + view** (wrong contrast window, over-simplified
stimulus geometry), NOT model-mechanism faults, and NOT genuine divergences. The
README's "GENUINE_DIVERGENCE / over-modulates" framing for 4E and 7C is **REFUTED**
by the author code.

### Author-geometry reruns through the committed model (mine, independent)

| Panel | Impl protocol render (current) | Author-geometry rerun | Paper / digitized | Verdict |
|---|---|---|---|---|
| 2A | flat plateau in [0.01,1] | full sigmoid in [1e-5,1], att left of ign, %-mod 99→1 | contrast gain | model FAITHFUL; window bug |
| 2B | flat plateau in [0.01,1] | response-gain elevation, sustained | response gain | model FAITHFUL; window bug |
| 3C/3F | plateau in [0.01,1] | sigmoid rise in [1e-5,1] | sigmoid | model FAITHFUL; window bug |
| 4E %-mod | ~390% (off-axis) | **53.5%** | ~54% | CODE_BUG (geometry) |
| 5C ratio | 1.17 | 1.17 | ~1.16 | FAITHFUL |
| 6C ratio | 1.16 | ~1.17 (oval≈cross) | ~1.11 | mild overshoot |
| 7C var/fix | ~2.8 | **1.41** | ~1.4 (code) / ~1.32 (digitized) | CODE_BUG (geometry) |

## Finding 1 — CRF contrast window [0.01,1] vs author [1e-5,1] / [1e-4,0.1]  (CONTRACT_BUG, figure; recurs 2A/2B/3C/3F + 4E)

`protocols._contrast_sweep` (protocols.py:36) hardcodes `c_range=(0.01, 1.0)` and the
view pins x to (0.01, 1.0). Author scripts use `cRange = [1e-5 1]` (Figure2A.m,
Figure2B.m, Figure3C.m, Figure3F.m) and `[1e-4 0.1]` (Figure4C.m, Figure4E.m). The
model half-saturates at c≈0.0027 (verified: unattended R/Rmax = 0.43 at c=1.9e-3), so
the entire rising limb — the contrast-gain left-shift 2A/2B/3C/3F are ABOUT — lives
BELOW 0.01 and is clipped off-screen. Rendered CRFs look like flat plateaus; the paper
shows full sigmoids. Single cause of the 2A/2B/3C/3F left-shift / half-max test reds.
4C already uses [1e-4,0.1] in-protocol; **4E does not** (defaults to [0.01,1]).
**Fix:** per-panel contrast range from the author script (2A/2B/3C/3F → [1e-5,1];
4E → [1e-4,0.1]) for BOTH the sweep and the view xlim.
Source: `protocols.py:36`; `paper/code/attentionModel/Figure2A.m` line `cRange=[1e-5 1]`.

## Finding 2 — digitized reference traced over [0.01,1], not the author axis  (figure; 2A/2B/3C/3F/4C/4E)

`article_aware/figures/figure_2/panel_A_digitized.json x_range=[0.01,1.0]` and siblings;
`panel_A.md` asserts "model sweep is contrast ∈ [0.01, 1.0]". The paper has NO numeric
x ticks (panel_A.md confirms "paper shows no numeric x ticks"); the digitizer assumed
the left edge ≈ 0.01, but the author axis floor is 1e-5. The digitized "rise at
c≈0.05–0.10" is mis-placed ~20–30× too high. This is exactly what the README's SQ-007
Gap-1 misread as "the model's left-shift sits below the window / unresolvable forward-model
divergence." It is a digitization x-axis calibration error, settled by the author code.
**Fix:** re-digitize 2A/2B/3C/3F/4C/4E with x_range = author cRange; the model's
half-max c≈0.003 then lands inside the window.
Source: `figure_2/panel_A.md`; author `Figure2A.m cRange=[1e-5 1]`.

## Finding 3 — protocols co-locate / over-simplify stimulus geometry  (CODE_BUG, figure: 4E, 7C; 4C mapping)

The author's two-stimulus-in-RF panels place the stimuli at SEPARATED x positions and
record at the midpoint; the impl puts both at x=0 and records at x=0. With σ_stim=5 on
a unit grid, co-located stimuli overlap heavily, feature competition crushes the
nonpreferred response, and the modulation overflows.

- **4E** (`run_figure_4E`): impl = 2 stim both at x=0 (θ 0/180), default [0.01,1].
  Author Figure4E.m = 4 stim at x=90/110 (RF, θ 0/180) and x=−90/−110 (contralateral),
  RF_center=100, Apeak=5, AxWidth=5, AthetaWidth=20, cRange[1e-4,0.1], oval spatial+feature
  attention. Author-geometry rerun → %-mod **53.5%** (impl 386%; digitized 54%). **Fix:**
  use the four-stimulus separated layout + [1e-4,0.1] + oval spatial+feature attend-pref/null.
- **7C** (`run_figure_7C`): impl = 2 stim both at x=0, fixation at x=50. Author Figure7C.m =
  variable stim at x=93, null (θ=180) at x=107, RF_center=100, attend-away at x=−100,
  Apeak=5, AxWidth=5, AthetaWidth=45, oval. Author-geometry rerun → var/fix **1.41**
  (impl 2.8; digitized 1.32). **Fix:** use the x=93/107 separated layout + attend-away at −100.

## Finding 4 — `test_contract_suppression_consistency.py` encodes the retired per-panel-gain shape  (CONTRACT_BUG, model-scope test)

5 reds. The test requires a single NON-None `suppressive_drive_gain` /
`suppressive_spatial_sigma_scale` resolved on every CRF panel ("promote ONE constant").
The SQ-005 resolution settled from author code that NO per-panel suppression gain exists
at all; the faithful model resolves None everywhere, so the test fails on its LETTER while
the mechanism satisfies its INTENT (one global suppression normalization on every panel).
**Fix:** rewrite the predicate to "no per-panel suppression key resolves on any protocol;
the global suppressive σ_space/σ_θ are identical across panels."
Source: `article_aware/extracted_data/test_contract_suppression_consistency.py`; SQ-007 Gap 2.

## Finding 5 — 6C uses `Ashape='cross'` in author code; impl approximates with oval feature-global  (minor, figure)

Figure6C.m's attend-contralateral condition uses `Ashape='cross'` (additive separable
gain arms) at x=−100; the impl builds the feature gain spatially-global oval. Renders
sharpening in the right direction but peak ratio 1.16 vs digitized 1.11 — a mild residual
overshoot plausibly from oval-vs-cross. Low severity; route to Phase A (also SQ-006: name
the "feature-based attention is spatially global" assumption, or implement the cross shape).
Source: `Figure6C.m Ashape='cross'`; `protocols.run_figure_6C`.

## Finding 6 — README "Potential sources" section + protocol docstrings are STALE  (doc, not gating)

The README "Current exit" correctly states the per-panel suppression knobs are deleted,
but the README "Potential sources" section (root cause #1) and the `run_figure_2A` /
`run_figure_3C` docstrings still describe `suppressive_drive_gain` 12/6/8 and
`suppressive_spatial_sigma_scale` 0.55/0.45 knobs that `calibration.yaml` confirms no
longer exist. The README also frames 4E as a GENUINE_DIVERGENCE, which the author code
refutes. A reader is told two contradictory things. **Fix:** rewrite the README
"Potential sources" to the window/geometry CODE_BUG framing; strip the retired-knob
references from the protocol docstrings.
Source: `README.md` "Potential sources"; `protocols.run_figure_2A/3C` docstrings vs `calibration.yaml`.

## Equation / parameter check (model.py) — FAITHFUL

- `compute_output` R = (A·E)/(S+σ), ⌊⌋_T at 0 — Eq. 5. ✓
- `compute_suppressive_drive` S = conv2sepYcirc(A·E, s_x, s_θ), zero-pad x / circular θ,
  unit-volume normpdf kernels, NO ·dx·dθ — matches attentionModel.m + conv2sepYcirc.m. ✓
- `build_attention_field` A = 1 + (γ−1)·G_x·G_θ — matches oval `(Apeak−Abase)·G + Abase`,
  Abase=1, Apeak=γ. ✓ (cross shape not implemented — Finding 5.)
- kernels/σ/baselines all match author defaults. ✓
- grid x∈[−200,200], θ∈[−180,180) step 1 — matches author. ✓
- Fig 1 faithful (A bump peaks 2.0 at x=100, →1.0 elsewhere; E left/right symmetric pre-attention).

## Status

`partial`. Forward model FAITHFUL. Six panels (2A,2B,3C,3F,4E,7C) are figure-scope
divergent from three protocol/view causes (contrast window, digitization axis, stimulus
geometry) — all resolvable WITHOUT touching the forward model. Two stale-test/stale-doc
findings. No genuine divergence and no paper issue survive the author-code lineage check.
