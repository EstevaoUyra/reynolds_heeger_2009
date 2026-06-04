# Phase-A Contract Audit — SQ-005 suppression-saturation correction

- **Model:** reynolds_heeger_2009
- **Branch:** fix/sq005-from-code-20260604
- **Commit under review:** cfad355 ("Resolve SQ-005 suppression-saturation CONTRACT_BUG from original author code")
- **Auditor:** independent Phase-A contract auditor (did NOT author the correction)
- **Date:** 2026-06-04
- **Ground truth read:** paper/code/attentionModel/{attentionModel.m, conv2sepYcirc.m, makeGaussian.m, Figure2A/2B/3C/3F/4C/4E/6C/7C.m}

## VERDICT: FAITHFUL

The corrected contract matches the acquired author code operator-for-operator and
value-for-value. The two code-alone tensions (IthetaWidth=360°, σ=1e-6) are stated
HONESTLY as code-alone with the explicit paper-vs-code tension — not laundered as
paper-resolved. No figure-fitting snuck into the contract. Provenance is clean.
SQ-005 is genuinely resolved with a grounded `human_resolution`. One scope note
(non-blocking) below.

---

## Per-check results

### 1. Mechanism fidelity — PASS
`attentionModel.m:170-175` (read directly):
```
I = conv2sepYcirc(E,IxKernel,IthetaKernel);   % :171
R = E ./ (I + sigma) + baselineUnmod;          % :175
```
- `IxKernel = makeGaussian(x,0,IxWidth)`, `IthetaKernel = makeGaussian(theta,0,IthetaWidth)` (`:133-136`) — no `height` arg ⇒ unit-volume (`makeGaussian.m:15` = `normpdf`).
- `conv2sepYcirc` (`:18-19`): zero-pad rows (space x), CIRCULAR cols (feature θ).
- So I = separable 2D convolution of E=(A·Eraw) over space (IxKernel) AND feature/orientation (IthetaKernel); R = E/(I+σ). **Exactly** what the corrected `model_spec.yaml` EQ-suppressive_kernel / suppressive_field / pipeline steps 1,4,5 now say.
- The old orthogonal "y-plane" is gone: `y_grid` is deprecated to a null stub; `EQ-suppressive_kernel` rewritten to `s(x,θ)` separable, no `∫∫∫`; pipeline step-1/step-4 inputs dropped `y_grid`.
- **No per-figure suppressive gain anywhere in the contract.** Confirmed by grep of `article_aware/spec/` (below).

### 2. The two key code-alone values — PASS
- `IthetaWidth = 360` — `attentionModel.m:92-94` (verbatim verified). `sigma = 1e-6` — `attentionModel.m:116-118` (verbatim verified).
- **No Figure*.m overrides either.** Grepped all eight figure scripts for `IthetaWidth|sigma|IxWidth|ExWidth|EthetaWidth`: zero hits for IthetaWidth/sigma/IxWidth/ExWidth/EthetaWidth. The only per-figure overrides are AthetaWidth/Apeak/Ashape and Figure-3 baselineMod/baselineUnmod — matching the contract exactly.
- **Both tagged code-alone** in `code_refs.yaml` (CODE-011 `code_alone: true`, CODE-014 `code_alone: true`) and bucketed code-alone by `neuromodels provenance`. The paper-vs-code TENSION is stated in every place: calibration.yaml notes ("paper text we hold C-011 quotes 180° for V4 … code runs 360°"; "paper presents σ … the code sets σ≈0"), model_spec descriptions, assumptions A-001/A-006, and the SQ-005 human_resolution. **Honest, not laundered.**
- Verified the load-bearing empirical claim in numpy on the code grid (x∈[-200,200], θ∈[-180,180], spacing 1): IxKernel sum = 1.000, IthetaKernel sum = 0.3839 (matches the diff's "~0.384"), θ-kernel near-flat (0.00098–0.00111/sample). The 360° σ ≫ the 361-sample θ span really does produce the near-flat all-orientation pool the contract names as the saturation mechanism.

### 3. No figure-fitting snuck back into the CONTRACT — PASS
- Grep of `article_aware/spec/` for `suppressive_drive_gain|sigma_scale|spatial_sigma_scale|suppression_normalization|kappa`: the ONLY hit is a calibration.yaml comment line stating *no* such knob exists in the code. No κ added (the prior fallback is explicitly declared MOOT in A-013).
- The retired per-panel knobs (4/12/6/8 gains, 0.45–1.0 sigma-scales) live only in `implementation/calibration.yaml` (Phase-B side), which this commit deliberately did not touch; assumptions A-006/A-013 mark them **for DELETION by Phase B**. They are queued for removal, not promoted into the contract.

### 4. Provenance integrity — PASS
- `check_citations reynolds_heeger_2009` → OK (every CODE/C/A tag resolves). Exit 0.
- `neuromodels provenance` → 56 values; code-alone bucket = 7 (model.sigma, model.stimulation_tuning_width, model.suppressive_tuning_width, figure_3C/3F baselines ×4). Exit 0.
- Spot-checked against actual file:line — all verbatim-correct:
  - CODE-001 attentionModel.m:170-175 → `I = conv2sepYcirc(...)` / `R = E./(I+sigma)+baselineUnmod` ✓
  - CODE-011 attentionModel.m:92-94 → `IthetaWidth = 360` ✓
  - CODE-014 attentionModel.m:116-118 → `sigma = 1e-6` ✓
  - CODE-017 Figure3C.m:5-6 → `baselineMod=5e-7; baselineUnmod=5` ; Figure3F.m:5-6 → `baselineMod=5e-7; baselineUnmod=0` ✓
  - CODE-010 IxWidth=20, CODE-013 EthetaWidth=60, CODE-015 Apeak=2/Abase=1 ✓

### 5. SQ-005 disposition honesty — PASS
- Status flipped STUCK → `RESOLVED (2026-06-04) via original author code`. `human_resolution:` (spec_questions.md:84) is a full grounded block (mechanism, the two code-alone values, the falsification of the y-plane form S/AE 0.243→0.059, a numpy-verified saturation target), NOT `<pending>`. Does not overclaim: it correctly limits σ's symbolic role to the closed-form EQ-3/EQ-7 and attributes saturation to the pooled I.

### 6. audited:false residue — PASS (none load-bearing for SQ-005)
Seven remaining, all pre-existing assumption-tagged and unrelated to the suppression mechanism:
- `model.alpha`=1.0 (A-002), `model.threshold_T`=0.0 (A-003), `model.beta`=1.0 (A-010, closed-form only)
- `figure_4C/4E/6C/7C.contrast`=0.5 (fixed sweep contrast = assumption)
The two SQ-005 mechanism values are now `audited:true` on verbatim code lines (model.sigma flipped false→true legitimately; suppressive_tuning_width stays true, re-sourced to CODE-011). No suppression-mechanism value remains `audited:false`.

### 7. Scope — PASS (with one note)
- The correction is at the MODEL level: one mechanism in `model_spec.yaml` (EQ-suppressive_kernel + compute_suppressive_drive), model-level `model.sigma` and `model.suppressive_tuning_width`. Not figure-local. Figure-3 baselines are the authors' own per-figure values (read from Figure3C/3F.m), not curve-fit knobs — correctly distinguished from the forbidden per-panel suppression tuning.

---

## Divergences found

None at contract severity. One observation:

- **OBS-1 (informational, not a contract defect):** The fault's full remediation is split across two passes by design — the contract is corrected here, but the live per-panel `suppressive_drive_gain` / `suppressive_spatial_sigma_scale` knobs still exist in `implementation/calibration.yaml` and are consumed by `implementation/src/rh_model/protocols.py`. They are explicitly queued for deletion by the downstream Phase-B fix pass (A-006/A-013 "DELETED by Phase B"). Until that pass runs, the *rendered figures* still use the old figure-fitted mechanism; the contract and the implementation are intentionally out of sync. This is the stated plan, not a laundering — flagged only so the re-audit-after-model-change step verifies the Phase-B deletion actually happens and that the separable broad-θ mechanism is what greens the MUST-PASS saturation target (no per-panel knob, no test relaxation).

## Judgment on the 360°/σ=1e-6 code-alone tensions

**Stated honestly, not laundered.** Both are tagged `code_alone: true` in code_refs.yaml, bucketed code-alone by the provenance tool, and carry the explicit paper-contradiction in every surface (calibration notes, model_spec descriptions, A-001/A-006, SQ-005 resolution): the paper Table 1 we hold quotes 180° (V4) and presents σ as an O(0.1) semi-saturation contrast, while the running code uses 360° and σ≈0. The contract states the code value is binding for the full simulation, preserves σ's symbolic O(0.1) role for the closed-form CRFs, and never claims the paper resolved these. This is the correct code-alone disposition.
