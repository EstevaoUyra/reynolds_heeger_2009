# Faithfulness Audit — Reynolds & Heeger (2009) — 2026-06-10 (independent re-render v2)

Independent re-render + paper/lineage audit of the CURRENTLY committed
`implementation/` by an auditor who is NOT the builder. Author MATLAB
(`paper/code/attentionModel/`) was re-implemented from scratch in Python
(`/tmp/author_repro.py`) as the lineage ground truth. Every number below was
measured by this auditor (author repro on the 401×361 grid, impl via
`rh_model.protocols`).

## Method
- Re-rendered all 7 figures from the committed model (`rh_model.views`).
- Eq 1–8 mapped to `model.py` operator-by-operator; verified vs `attentionModel.m`.
- From-scratch `attentionModel.m` + `Figure6C.m` + `Figure7C.m` + `Figure4C.m`
  reproduction; impl protocols measured against it and the digitized panels.
- Full suite run: 138 passed, **3 MUST-PASS RED**, 11 xfailed, 18 xpassed, 2 skipped.

## Verdict: PARTIAL

The forward model (Eq 1/2/5/6, stimulus drive, oval attention field, separable
conv `conv2sepYcirc`) is FAITHFUL and Figs 2A/2B/3C/3F/4C/4E/5C/7C match the
author code to 3–4 sig figs. **One live, blocking divergence remains: Fig 6C**,
whose protocol ignores its own binding ledger geometry and the author 'cross'
attention shape, over-scaling and over-sharpening the tuning curve. The prior
same-day Q-043 (7C flank-sign) finding has since been RESOLVED in the committed
test (window narrowed to ±45°; suite green).

| Figure | impl | author repro | digitized | status |
|---|---|---|---|---|
| 2A/2B/3C/3F CRFs | — | match | — | FAITHFUL (contrast-gain / response-gain regimes correct) |
| 4C %-mod peak (suppression) | 36.8% | author code suppression | ~36% | FAITHFUL to author code |
| 4E %-mod | ~52% | match | ~54% | FAITHFUL |
| 5C peak ratio / FWHM | 1.17 / equal-width | match | — | FAITHFUL (pure multiplicative scaling) |
| 7C var/away peak ratio | 1.322 | 1.323 | ~1.33 | FAITHFUL |
| 1 R_right/R_left | 1.01 | 1.010 | — | FAITHFUL-to-code (schematic exaggerates) |
| **6C peak ratio (att/away)** | **1.168** | **1.109** | **1.108** | **DIVERGENT** |
| **6C FWHM ratio (att/away)** | **0.821** | **0.887** | **0.87** | **DIVERGENT** |

---

## Finding 1 — Fig 6C: protocol ignores its binding ledger geometry + author 'cross' shape

**Tag: CONTRACT_BUG · scope=figure (Figure 6C) · severity=major (3 MUST-PASS RED today)**

`run_figure_6C` (protocols.py:388–441) hard-codes `x_opposite=-50`, `x_fixation=50`,
places the RF stimulus at x=0, and builds the attend-opposite field as a
**flat-in-x, θ-selective oval proxy** (`{spatial_center: None, feature_center: θ}`).
But the calibration ledger encodes the AUTHOR `Figure6C.m` geometry as BINDING,
author-quoted keys (calibration.yaml:666–705): `figure_6C.stim_rf_x=100`,
`stim_contra_x=-100`, `attend_fixation_x=0`, and the `figure_6C.tuning_width` note
documents `Ashape='cross'`. The code reads NONE of these keys. No 'cross' attention
shape exists in the model (grep: zero hits for `cross`/`Ashape`/`Abase`).

Measured (author repro, impl at n=361):
- impl peak ratio (att-opposite / att-fixation) = **1.168**; author 'cross' = **1.109**; digitized = **1.108**.
- impl FWHM ratio = **0.821**; author = **0.887**; digitized = **0.87**.

Root mechanism (verified numerically): in the author 'cross' field the SPATIAL
multiplier at the recorded RF (x=100) is `attnGainX = (Apeak-Abase)·G_x(-100) + Abase
≈ Abase = 1.0` — the directional gain reaches the RF only through the θ-conv, NOT at
full γ. The impl proxy applies the full γ=2 θ-peak gain at x=100 everywhere in x
(`A = 1 + (γ-1)·G_θ`, flat in x), so it over-scales (+5.4% on peak ratio) and
over-sharpens. The DIRECTION (sharpening + scaling) is faithful; the magnitude is
not, and the binding contract is violated.

The rendered panel shows this: the attend-fixation (gray) peak sits at ~0.855
(impl) vs ~0.905 (digitized) and the blue curve is visibly narrower than the
reference. Note `A-014` ("feature gain spatially global") in the 6C ledger note is
the assumption the proxy leans on, but it contradicts the author 'cross' field,
which is spatial-Gaussian-at-(-100) — not global.

**Fix (spec-level):** route `run_figure_6C` through the ledger geometry it already
defines (RF stim + recorded column at x=100, contra stim + attend-opposite centre
at x=-100, attend-fixation at x=0) and implement the author 'cross' attention shape
(attentionModel.m:146–162: `attnGainX=(Apeak-Abase)·G_x+Abase`,
`attnGainTheta=(Apeak-Abase)·G_θ+Abase`,
`attnGain=(Apeak-Abase)·conv2sepYcirc(impulse_at_Atheta·attnGainX,[1],attnGainTheta)+Abase`)
selected by config for 6C, with `Figure6C.m` params (AxWidth=30, AthetaWidth=60).
Acceptance: 6C peak ratio 1.108 (±0.01), FWHM ratio 0.87–0.89 (the three RED
MUST-PASS tests in test_audit_2026_06_10_contract.py).

source_hint: `protocols.py:388-441` (hard-coded x_opposite=-50/x_fixation=50,
flat-x θ proxy) vs `calibration.yaml:666-705` (figure_6C.stim_rf_x=100/
stim_contra_x=-100/attend_fixation_x=0, note "Ashape='cross'") and
`paper/code/attentionModel/Figure6C.m:3-30` + `attentionModel.m:146-162`.

---

## Finding 2 — Fig 1 Output panel shows no visible attended-side enhancement

**Tag: GENUINE_DIVERGENCE (vs schematic) / FAITHFUL-to-code · scope=figure (Figure 1) · severity=minor**

The rendered "Output firing rate" draws attended (right) and unattended (left) at
near-equal brightness (R_right/R_left ≈ 1.01). The author code produces EXACTLY
1.010 for the Fig-1 parameters: broad γ=2 attention on an isolated stimulus scales
both A·E and the locally pooled S, nearly cancelling in R. The paper's Fig-1 panel
is a hand-drawn schematic that exaggerates the enhancement; there is no `Figure1.m`.
The impl is faithful to Eq 5/6 and to the author code. The contract's
`figure_1.md` relation #6 ("noticeably brighter") overstates the R asymmetry
relative to the CODE it cites — flagged as a contract-doc overstatement, encoded as
the xfail tripwire `test_population_response_right_noticeably_brighter_TRIPWIRE`.
No model fix required.

source_hint: paper Fig 1 caption / figure_1.md #6 vs `run_figure_1` R_right/R_left
= 1.01 = author code 1.010 (no Figure1.m exists).

---

## Finding 3 — Fig 4C published-panel sign (already dispositioned)

**Tag: PAPER_ISSUE · scope=figure (Figure 4C) · severity=minor · resolved (A-012 / DR-4C-sign)**

The rendered 4C draws attend-nonpref-in-RF (blue) BELOW attend-away (gray) =
suppression, %-mod positive ~36.8% declining with contrast — matching
`Figure4C.m:74` (`100*(unattCRF-attCRF)/unattCRF`, plotted positive) and the
suppression prose (C-021). This is OPPOSITE the *published* panel C, which draws
attend-nonpref above (facilitation). Resolved earlier via the lineage ladder
(released CODE rung 1 + C-021) as a digitizer/figure-panel sign issue, NOT a model
defect. impl 4C attended-CRF max 6.636 vs unattended 6.946 — author-faithful. Note:
my initial thumbnail read suggested blue-above; the zoomed render confirms
gray-above (suppression) — the model is correct.

source_hint: `Figure4C.m:53-74` + A-012 / DR-4C-sign RESOLVED.

---

## RESOLVED since the prior same-day audit (carried no longer)

- **Q-043 (7C flank-sign)** — the prior Finding B. The committed
  `test_figure_7C.py::test_attention_effects_have_opposite_signs_around_preferred_flanks`
  now uses the 15≤|θ|≤45 central-flank window (lines 149–158) instead of the stale
  ±60° / 0.75 threshold; it PASSES. Author repro confirms the outer-flank dip
  (var < away for |θ|≳50°, frac=0.700 over ±60°, 1.000 over ±45°) — the model
  matches the author code; the test was correctly narrowed. SQ-008 closed.
- **7C ratio (Finding 1, periodic-wrap bug)** — fixed in commit 11471b7; I measure
  var/away = 1.322 = author 1.323.

---

## Checked and FAITHFUL (with what I checked, author-verified)

- **Eq 1,2,5,6 → code:** `compute_output` R=(A·E)/(S+σ) (Eq 5); `compute_suppressive_drive`
  S=conv(A·E) (Eq 6); A multiplies E before normalization. Operator-by-operator match
  to attentionModel.m:166–175.
- **Oval attention field:** impl `A = 1 + (γ-1)·outer(G_θ, G_x)` is algebraically the
  author 'oval' build (Apeak=γ, Abase=1, impulse-at-Atheta conv). FAITHFUL for
  2A/2B/3C/3F/4C/4E/5C/7C (all use oval). Only 6C uses 'cross' and is the divergence.
- **Separable conv operator:** `_separable_conv` = `conv2sepYcirc` (zero-pad x via
  fftconvolve 'same'; circular θ via FFT). Matches.
- **Grid / kernels:** x∈[-200,200] step 1 (401), θ∈[-180,180] step 1 (361); unit-volume
  normpdf kernels, NOT integral-normalized — matches the author makeGaussian + the
  saturation mechanism (SQ-005). σ=1e-6 (CODE-014). ExWidth=5, EthetaWidth=60,
  IxWidth=20, IthetaWidth=360 all match attentionModel.m defaults.
- **Figs 2,3,5,7 rendered shapes:** contrast-gain (2A: left-shift, %-mod peaks low,
  curves converge high), response-gain (2B: up-shift, attended saturates higher),
  3C/3F baseline handling, 5C pure multiplicative scaling (equal width), 7C direction
  ordering (var>fixation>nonpref, ratio 1.322) — all match paper qualitative claims
  and author numbers.
