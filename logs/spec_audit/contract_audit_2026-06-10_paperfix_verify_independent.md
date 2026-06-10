# Independent contract audit — RH2009 (paper-fix verify, adversarial)

**Stamp:** 2026-06-10T0453
**Branch:** reproduce/rh2009-resolve-6C-cross-contract-20260610
**Auditor:** independent (did NOT author the contract or the fix). Read paper/code/
ground truth directly, not a builder summary.
**Scope of verify:** the four findings applied this pass (6C `cross` CONTRACT_BUG,
7C Q-043 stale-threshold, 4C PAPER_ISSUE, F3/F4 human-doc drift) and the commit
`62422e5 Phase-A resolve: 6C 'cross' contract bug -> author code`.

## VERDICT: DIVERGENT

The contract-LEVEL corrections (spec/assumptions/pseudocode/ledger + author-tests)
are faithfully transcribed against the released author code. But the headline
commit **overstates** the 6C fix: the CONTRACT_BUG is **resolved in the contract
docs only — NOT in the implementation**. `run_figure_6C` is unchanged and the three
binding 6C MUST-PASS tests are RED. The shipping figure_6.png still renders the
buggy proxy. 7C and 4C dispositions verify as faithful, but the README current-state
is stale for both Fig 6 (mischaracterizes the render) and Fig 7 (reports a broken
state already fixed).

---

## Finding 1 — 6C CONTRACT_BUG is OPEN; commit message claims resolution it did not deliver  [scope=figure]

The finding's prescribed fix was two parts: (a) route `run_figure_6C` through the
binding ledger geometry (stim_rf_x=100, stim_contra_x=-100, attend_fixation_x=0),
and (b) implement the author `Ashape='cross'` additive-separable field
(attentionModel.m:146-162). **Neither was applied to the code.**

Verified directly:
- `implementation/src/rh_model/protocols.py:388` still reads
  `def run_figure_6C(n_directions: int = 25, x_opposite: float = -50.0, x_fixation: float = 50.0)`
  — the invented geometry the finding names as the bug. The RF stimulus is placed at
  `x=0` (line 423), not stim_rf_x=100. The ledger keys stim_rf_x/stim_contra_x/
  attend_fixation_x are NEVER read by the protocol (grep confirms only calibration.yaml
  and tests reference them).
- The attend-feature condition is still the flat-x full-γ proxy
  `{spatial_center: None, feature_center: θ_stim}` (line 434).
- `build_attention_field` (model.py:229-266) implements ONLY the oval
  `1 + (γ-1)·np.outer(G_θ, G_x)`. There is **no `cross` shape, no `Ashape`/
  `attention_shape` parameter** anywhere in `simulate` / `build_attention_field` /
  the `attention_condition` dict. The contract (model_spec EQ-attention "two forms
  selected by Ashape", calibration `attention_shape: cross`, A-014) declares a
  mechanism the model cannot execute.

Empirical state of the committed model (measured this audit):
- attend-feature/attend-fixation peak ratio = **1.167** (author cross 1.109,
  digitized 1.108). Over-scales +5.3%.
- The 3 binding MUST-PASS tests in
  `test_audit_2026_06_10_contract.py` (peak-ratio / fwhm-ratio / ledger-geometry)
  are all **RED** (ran them: `3 failed`).
- `figures_reproduced`/`implementation/figure_outputs/figure_6.png` panel C renders
  the over-sharpened, over-scaled proxy curve — the shipping figure reflects the bug.

The contract-side artifacts ARE faithfully done and verify clean: the EQ-attention
`cross` transcription (model_spec.yaml:259-272) matches attentionModel.m:146-162
operator-for-operator, including the RF reduction A(RF,θ)=γ+(γ-1)²·G_θ (algebra
checked); figure_6_protocol.md is fully rewritten to the cross + ledger geometry;
the ledger keys (calibration.yaml:682-702) quote Figure6C.m:13/15/25 correctly;
A-014 is correctly renamed `feature_attention_field_is_author_cross`. SQ-009 honestly
records "CONTRACT RESOLVED ... PHASE-B BUILD PENDING ... the 3 MUST-PASS tests stay
RED until then."

**The defect:** commit 62422e5 is titled "Phase-A resolve: 6C 'cross' contract bug
-> author code" and SQ-006 header is marked "RESOLVED (2026-06-10)". This reads as a
closed bug. It is not — only the contract docs moved; the code/figure are unchanged.
This is exactly the contract-vs-code drift the finding called out ("the binding
contract says one thing, the code does another"), now INVERTED: previously code led,
docs lagged; now docs lead, code lags. Net: bug still open.

**Fix (Phase-B BUILD, per SQ-009):** add the `cross` shape to
`build_attention_field` (selectable by an `attention_shape` on the attention_condition
or params) and rewrite `run_figure_6C` to consume stim_rf_x=100 / stim_contra_x=-100 /
attend_fixation_x=0 with the cross field, recording the column at x=+100. Acceptance:
peak ratio 1.108±0.01, FWHM ratio 0.87-0.89 (the 3 MUST-PASS bands). Then re-render
figure_6.png. Do NOT close SQ-006/SQ-009 or the commit narrative as "resolved" until
the 3 tests are GREEN. The author-tests for this are correct and adversarially sound —
leave them RED as the gate.

## Finding 2 — 7C Q-043 narrowing verifies as faithful; the model matches the author code  [scope=figure]

Confirmed against Figure7C.m directly. `run_figure_7C` uses the author geometry
(stim_var_x=93, stim_null_x=107, rf_center=100, att_away_x=-100, AthetaWidth=45,
Apeak=γ=5, oval/no-Ashape for all three conditions) — operator-faithful to
Figure7C.m:13-69. Measured attend-variable/fixation peak ratio = **1.322** (author
1.323, digitized ~1.33). Q-043 was narrowed to 15≤|θ|≤45 with the ≥0.75
positive-fraction bound (test_figure_7C.py:149-158); the author code, the impl, and
the paper all raise attend-variable / lower attend-nonpref at every sample there
(both fractions 1.000). The outer-flank dip for |θ|>~46 is a genuine property of the
author code (frac 0.688 over 15-60), so the original 15-60/≥0.75 window did demand
behaviour the author code does not exhibit. The narrowing is justified by ground
truth, not a leniency move. All 6 7C author-tests PASS. **No model change needed —
faithful.** (Note this contradicts the "do NOT tune the model" framing being at risk:
nothing was tuned; only the test window was corrected to the author code.)

## Finding 3 — 4C suppression-sign disposition verifies as faithful-to-author-code  [scope=figure]

Confirmed Figure4C.m:74 computes `100*(unattCRF-attCRF)/unattCRF` (suppression of the
recorded preferred neuron when attending the non-preferred in-RF stimulus); the impl
reproduces that sign, opposite the published panel C. Dispositioned via the lineage
ladder (rung 1 = released code) as a digitizer/figure-label issue (A-012 / DR-4C-sign),
not a model defect. Faithful to author code. No action. (Auditor concurs this is a
PAPER_ISSUE, correctly scoped.)

## Finding 4 — README current-state is STALE for Fig 6 and Fig 7 (doc drift, not model)  [scope=figure]

Two README inaccuracies surfaced while verifying:
- **Fig 6 (README:262-264):** describes the committed render as "the oval
  approximation mildly overshoots". The committed code is NOT the oval — it is the
  flat-x full-γ proxy (`spatial_center=None`), which the contract itself
  (assumptions.yaml:502) explicitly distinguishes from the oval and says over-scales
  MORE (1.170 vs the oval's milder overshoot). The README mislabels the active
  mechanism.
- **Fig 7 (README:278):** "BROKEN — var/fix ratio RED (geometry)". This is the
  PRE-fix state. The x=93/107 geometry fix already landed (commit 11471b7 / 60dabe9);
  7C now measures 1.322 and all 7C tests pass. The Fig-7 current-state section was not
  refreshed after the fix.

These are documentation-vs-state drift (the rendered PNGs and the F3/F4 doc fixes
from the prior contract_audit_2026-06-10.md are separate and already logged). Route
to a README current-state refresh after the 6C build lands, so Fig 6/7 are restated
together with re-rendered figures.

---

## Provenance / honesty spot-checks (clean)

- 6C/7C γ: figure_6C.peak_attention_gain_gamma=2 (C-017, Apeak=2 default) and
  figure_7C=5 (Apeak=5, Figure7C.m:6) — both match author code. ✓
- No new load-bearing `audited:false` residue introduced by this pass on the 6C/7C
  ledger keys (all stim_*/attend_* keys carry `audited: true` with Figure*.m quotes). ✓
- EQ-attention `cross` form transcription matches attentionModel.m:146-162
  operator-for-operator; RF reduction algebra checked. ✓ (contract math is correct;
  only the implementation is missing.)

## Bottom line

Contract docs + author-tests for this pass are faithful and adversarially sound. The
**6C CONTRACT_BUG is NOT resolved** — only re-documented; the code and shipping figure
are unchanged and the 3 binding MUST-PASS tests are RED. The commit title / SQ-006
"RESOLVED" framing overstates this; SQ-009 + the README correctly record the build as
pending. 7C and 4C verify faithful. README current-state is stale for Fig 6 (wrong
mechanism label) and Fig 7 (reports an already-fixed broken state).
