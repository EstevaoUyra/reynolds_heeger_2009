# Faithfulness Audit — Reynolds & Heeger (2009) — 2026-06-10 (re-render + author-code verify)

Independent re-render of the CURRENTLY committed `implementation/` (commit 11471b7,
the Finding-1 θ-stimulus fix), by an auditor who is NOT the builder. The authors'
released MATLAB (`paper/code/attentionModel/`) was re-implemented from scratch in
Python (`/tmp/author_sim.py`: `attentionModel.m` + `conv2sepYcirc.m` +
`makeGaussian.m`) and used as the lineage ground truth. Every number below was
measured by this auditor.

## Method
- Re-rendered all 7 figures from the committed model
  (`PYTHONPATH=implementation/src .venv/bin/python -m rh_model.views`).
- Ran each figure's protocol through BOTH the committed `rh_model` and the
  from-scratch author reproduction on the author 401×361 grid.
- Eq 1–8 mapped to code operator-by-operator; ledger `quote:` fields spot-checked
  against the author `.m` files.

## Verdict: PARTIAL

The forward model (Eq 5/6, stimulus drive, attention field, normalization, the
separable conv operator) is faithful, and Figs 1,2A,2B,3C,3F,4C,4E,5C,7C match
the author code to 3–4 significant figures. The prior same-day audit's Finding 1
(7C ratio 1.41) is now FIXED in the committed model — I measure 1.322 = author
1.323. Two real divergences remain, both figure-scope on Fig 6C, plus one
must-pass test threshold (Q-043) that contradicts the author code.

| Figure | impl | author repro | digitized | status |
|---|---|---|---|---|
| 2A att/un peak | 21.94 / 21.72 | 21.94 / 21.72 | — | FAITHFUL |
| 2B att/un peak | 25.90 / 18.26 | 25.90 / 18.26 | — | FAITHFUL |
| 3C att/un peak | 23.49 / 23.25 | 23.49 / 23.25 | — | FAITHFUL |
| 3F att/un peak | 18.54 / 15.41 | 18.54 / 15.41 | — | FAITHFUL |
| 4C mod max | 36.8% | 36.3% | — | FAITHFUL (suppression sign correct) |
| 4E mod range | 36.9–52.0% | 36.3–51.9% | — | FAITHFUL |
| 5C peak ratio / FWHM | 1.166 / 144=144 | 1.166 / 144=144 | — | FAITHFUL |
| 7C var/away ratio | 1.322 | 1.323 | ≈1.32 | FAITHFUL (Finding-1 fixed) |
| 1 R_right/R_left | 1.01 | 1.01 | — | FAITHFUL to code (schematic caveat) |
| **6C peak ratio** | **1.168** | **1.109** | **1.108** | **DIVERGENT** |
| **6C FWHM ratio** | **0.823** | **0.889** | **0.87** | **DIVERGENT** |

---

## Finding A — Fig 6C: protocol ignores its own ledger geometry + 'cross' shape; over-scales

**Tag: CONTRACT_BUG · scope=figure (Figure 6C) · severity=minor**

The calibration ledger encodes the AUTHOR `Figure6C.m` geometry as binding keys:
`figure_6C.stim_rf_x=100`, `figure_6C.stim_contra_x=-100`,
`figure_6C.attend_fixation_x=0`, and the `figure_6C.tuning_width` note documents
`Ashape='cross'` (calibration.yaml:638–702). But `run_figure_6C`
(protocols.py:388–436) does NOT read any of those keys — it hard-codes
`x_opposite=-50`, `x_fixation=50`, places the RF stimulus at x=0 (not x=100), and
builds the attend-feature field as `{spatial_center: None, feature_center: θ}` (a
flat-in-x, full-γ θ-selective proxy). No 'cross' (additive) attention shape is
implemented anywhere in the model (grep: zero hits for `cross`/`Ashape`/`Abase`).

Consequence (measured, both at finer sampling and at the rendered n=73):
- impl peak ratio (attend-feature / attend-fixation) = **1.168**;
  author 'cross' reproduction = **1.109**; digitized panel C = **1.108**.
- impl FWHM ratio = **0.823**; author = **0.889**; digitized = **0.87**.

The DIRECTION is faithful (sharpening + scaling), but the impl over-scales (+5.5%
on peak ratio) and over-sharpens, because the flat-x γ=2 θ-gain is applied at full
strength everywhere in x, whereas the author cross mixes a spatial-Gaussian-at-(-100)
term that is ≈Abase at the recorded x. This is the same defect the contract already
documents but the code does not honor — the binding ledger says one thing, the code
does another.

**Fix (spec-level):** route `run_figure_6C` through the ledger geometry it already
defines (stim_rf_x=100 recorded, stim_contra_x=-100, attend_fixation_x=0) and
implement the author 'cross' attention shape (`attentionModel.m:146-162`:
`attnGainX=(Apeak-Abase)·G_x+Abase`, `attnGainTheta=(Apeak-Abase)·G_θ+Abase`,
`attnGain=(Apeak-Abase)·conv2sepYcirc(impulse_at_Aθ·attnGainX,[1],attnGainTheta)+Abase`)
selected by config for 6C, with `Figure6C.m` params (AxWidth=30, AthetaWidth=60).
Acceptance: 6C peak ratio 1.108 (±0.01), FWHM ratio 0.87–0.89.

source_hint: `protocols.py:388-436` (hard-coded x_opposite=-50/x_fixation=50,
flat-x proxy) vs `calibration.yaml:638-702` (figure_6C.stim_rf_x=100/
stim_contra_x=-100/attend_fixation_x=0, note "Ashape='cross'") and
`Figure6C.m:3-25` + `attentionModel.m:146-162` (the 'cross' build).

---

## Finding B — Q-043 7C flank-sign must-pass threshold contradicts the author code

**Tag: CONTRACT_BUG · scope=figure (Figure 7C) · severity=major (blocks the green gate, SQ-008 OPEN)**

SQ-008 is OPEN: the contract-sanctioned Finding-1 fix leaves Q-043
(`test_attention_effects_have_opposite_signs_around_preferred_flanks`,
test_figure_7C.py) RED — it asserts attend-variable > attend-away at ≥75% of the
samples over 15≤|θ|≤60, but the corrected mechanism gives frac-positive 0.667.
Phase B correctly refused to tune the mechanism or edit the test and escalated.

I resolved the escalation via lineage rung-1 (released author code), which Phase B
could not read. The author `Figure7C.m` itself, run faithfully, produces the SAME
outer-flank dip: attend-variable falls BELOW attend-away for |θ| ≳ 46°, giving
**frac-positive = 0.688** over 15≤|θ|≤60 — itself < 0.75. The impl reproduces this
(0.677). Over 15≤|θ|≤45 both author and impl are 1.000.

Therefore Q-043's ≥0.75-over-±60° threshold is STALE: it was authored against the
buggy periodic-wrap θ profile and demands behavior the author code does not exhibit.
The digitized panel's apparent "no dip" is a digitization-resolution artifact at the
steep outer flanks; the released code is the higher rung and it dips. The faithful
mechanism is correct; the TEST is wrong.

**Fix (spec-level):** narrow Q-043's central-flank window to 15≤|θ|≤45 (where author
+ impl + paper agree the curve is raised), or lower the fraction threshold to ≈0.65
to match the author code's 0.688. Do NOT tune the model — it already matches the
author code (var/away 1.322 vs 1.323). Resolves SQ-008 escalation option (a)/(c).

source_hint: `Figure7C.m:9-60` (AthetaWidth=45 attend-variable curve dips for
|θ|≳46°, author frac=0.688) vs `test_figure_7C.py` Q-043 (≥0.75 over 15≤|θ|≤60) and
`logs/spec_questions.md` SQ-008 (OPEN). My author-repro flank table is in the audit
run; impl frac 0.677 over ±60°, 1.000 over ±45°.

---

## Finding C — Fig 1 Output panel shows no visible attended-side enhancement

**Tag: FAITHFUL (to code) / GENUINE_DIVERGENCE (to the schematic) · scope=figure (Figure 1) · severity=minor**

The rendered "Output firing rate" panel draws attended (right) and unattended
(left) bands at near-equal brightness (R_right/R_left ≈ 1.01). I confirmed the
author code produces EXACTLY 1.010 for the Fig-1 parameters (broad γ=2 attention on
an isolated stimulus: γ multiplies both E and the locally pooled S, nearly
cancelling at the recorded neuron). The paper's Fig-1 panel is a hand-drawn
schematic that exaggerates the enhancement; there is no `Figure1.m`. The impl is
faithful to the equations and to the author code. Reclassify as FAITHFUL-to-code;
the only divergence is from the illustrative schematic, which is not a code/contract
defect. No fix required.

source_hint: paper Fig 1 caption vs `run_figure_1` R_right/R_left=1.01 = author
code 1.010 (no Figure1.m exists).

---

## Finding D — Fig 4C published-panel sign (already dispositioned)

**Tag: PAPER_ISSUE · scope=figure (Figure 4C) · severity=minor · already-resolved (DR-4C-sign / A-012)**

The rendered 4C draws attend-nonpref-in-RF BELOW attend-away (suppression),
matching `Figure4C.m:74` (`100*(unattCRF-attCRF)/unattCRF`) and the suppression
prose, but opposite the *published* panel C. Resolved earlier via the lineage ladder
as a digitizer/figure label issue, not a model defect. Faithful to author code
(impl 4C att 6.636 vs author 6.642). Flagged for completeness.

source_hint: `Figure4C.m:53-74` + A-012 / SQ-007 RESOLVED.

---

## Finding E — figure_*.md human docs teach superseded values (contract drift, already-logged)

**Tag: CONTRACT_BUG · scope=figure (Figures 3,4 docs) · severity=minor · already-logged**

Per `logs/spec_audit/contract_audit_2026-06-10.md`: `figure_3.md` still documents
the retired A-007 baselines (0.05/0.05) instead of the binding CODE-017 (5e-7;
5.0/0.0), and `figure_4.md` Panel-C still teaches the retired C-021 mechanism. The
PNGs are faithful (re-rendered + checked); doc-vs-contract only. Fix is in that spec
audit (rewrite to CODE-017 / A-012).

source_hint: `logs/spec_audit/contract_audit_2026-06-10.md` F3/F4.

---

## Checked and FAITHFUL (with what I checked, all author-verified)

- **Eq 1,2,5,6 → code:** `compute_output` R=(A·E)/(S+σ) (Eq 5); S=conv(A·E) (Eq 6);
  A multiplies E before normalization. Operator-by-operator match.
- **Separable conv operator:** impl matches author `conv2sepYcirc` (upConv zero-pad
  rows / circular cols). Single-stimulus E matches to ≥4 dp.
- **Finding-1 fix verified present + correct:** θ grid is now 361 (arange(-180,181));
  stimulus θ profile is non-periodic `gaussian_1d`; 7C var/away = 1.322 = author 1.323.
- **Calibration ledger quotes:** σ=1e-6, baselineMod=5e-7, baselineUnmod=5(3C)/0(3F),
  sizes 5/20, tuning 60/360, per-figure stim/attn sizes — all match author `.m` + Table 1.
- **Figs 2A,2B,3C,3F,4C,4E,5C,7C:** numeric peaks/ratios/FWHM match the author code to
  3–4 sig figs (table above).

## Correction to the prior same-day audit
- Its Finding 1 (7C ratio 1.41, the periodic-wrap/360-grid bug) is RESOLVED in the
  committed model (commit 11471b7) — I measure 1.322. Carried no longer.
- Its Finding 2 (6C "faithful, GENUINE_DIVERGENCE minor, FWHM 0.875") is upgraded to
  CONTRACT_BUG: with finer sampling and the peak-ratio metric, the impl over-scales
  (1.168 vs author/digitized 1.108) AND the code ignores the ledger geometry keys it
  already defines. The mechanism gap is a contract violation, not just a proxy.
- New: Q-043 (Finding B) is a stale test threshold the author code refutes (frac
  0.688 < 0.75) — resolves the SQ-008 escalation toward "fix the test, not the model".
