# Phase-A RESOLVER pass — reynolds_heeger_2009 — 2026-06-10

Resolver for the four findings handed to this pass. Each resolved via the ladder
(1 = this paper's author code → CODE/A-NNN; 2 = lineage; 3 = human last-resort).
Corrections to `article_aware/` ONLY; no model code touched; no per-figure knob tuned.

## Finding 1 — Figure 6C CONTRACT_BUG (`run_figure_6C` ignores ledger geometry + no 'cross' shape)

RESOLVED at the contract level via ladder rung (1) — the authors' `Figure6C.m` +
`attentionModel.m:146-162`. NOT a blocked/open-contract item: the faithful mechanism
is available in the paper's own released code.

ROOT CAUSE (confirmed numerically, this pass). The committed model builds the 6C
attend-feature condition as a FLAT-IN-X full-γ θ proxy — operationally
`A(RF,θ) = 1 + (γ-1)·G_θ(θ)`, a 1.0→2.0 gain. The author field is `Ashape='cross'`
(additive separable): at the recorded RF (x=+100, spatial arm centred at -100, so
G_x≈0) it reduces to `A(RF,θ) = γ + (γ-1)²·G_θ(θ)`, a 2.0→3.0 gain at γ=2. Verified
reproduction of the exact code arithmetic on the 401×361 grid:

| quantity            | flat-x proxy (committed) | author 'cross' | digitized panel |
|---------------------|--------------------------|----------------|-----------------|
| peak ratio feat/fix | 1.170                    | 1.109          | 1.108           |
| FWHM ratio feat/fix | 0.831                    | 0.887          | ~0.87           |

The proxy OVER-scales (+5.5%) and OVER-sharpens — exactly the contract bug. The
'cross' lands on the digitized panel.

CONTRACT CORRECTIONS (article_aware only):
- `assumptions.yaml` A-014: RENAMED `feature_attention_is_spatially_global` →
  `feature_attention_field_is_author_cross`; rewritten to prescribe the author 'cross'
  field and RETIRE the flat-x full-γ proxy (named as the over-scaling bug). The
  originally-named property (feature gain reaches the RF when spatial attention is
  directed away) survives as a consequence of the cross's near-flat spatial arm at the
  RF. Corrected the earlier over-claim that Fig 7C uses the cross — Figure7C.m passes NO
  Ashape (default oval, spatially-local arms at x=93/107 ≈ recorded RF x=100).
- `model_spec.yaml` EQ-attention: added the 'cross' construction form alongside the oval;
  `simulation_protocols.figure_6C` gains `attention_shape: cross` and a binding note that
  the oval/flat-x proxy must not be substituted; `pipeline.build_attention_field` updated
  to require the 'cross' shape selectable per protocol.
- `pseudocode/figure_6_protocol.md`: Inputs note + Procedure step 2 rewritten to the author
  'cross' math; the prior "oval approximation mildly overshoots… do NOT tune it" note (which
  SANCTIONED the divergence) replaced with the binding-cross requirement.

REMAINING WORK = PHASE-B BUILD (no Phase-A decision left), tracked as SQ-009 (owner Phase B,
expiry 2026-07-15): implement `Ashape='cross'` in `build_attention_field` and route
`run_figure_6C` through the ledger keys (stim_rf_x=100 / stim_contra_x=-100 /
attend_fixation_x=0) instead of the hard-coded -50/50. The 3 MUST-PASS contract tests
(`test_audit_2026_06_10_contract.py`) + the soft mechanism tripwire stay RED until then —
the expected state of a correctly-specified-but-not-yet-built fix. Targets reachable by the
correct mechanism with NO tuning (verified 1.109/0.887).

## Finding 2 — Figure 7C CONTRACT_BUG / SQ-008 (Q-043 RED)

ALREADY RESOLVED in the test layer (commit predating this pass) per SQ-008 escalation
option (a); this pass closes the SQ. `test_figure_7C.py` Q-043
(`...opposite_signs_around_preferred_flanks`) is already narrowed from the central-flank
window `15<=|θ|<=60` (>=0.75 positive) to `15<=|θ|<=45`, the region where the released
`Figure7C.m`, the impl, and the paper panel all agree attend-variable is RAISED (author +
impl frac-positive = 1.000). The old `15..60` threshold was authored against the buggy
periodic-wrap profile and demanded behaviour the author code does not exhibit (author code
itself dips attend-variable below attend-away for |θ| > ~46°; author frac over 15..60 =
0.688 < 0.75). The model already matches the author var/away peak ratio (1.322 vs 1.323) —
the TEST was stale, not the model. VERIFIED GREEN this pass. SQ-008 → RESOLVED.

## Finding 3 — Figure 4C PAPER_ISSUE (rendered draws attend-nonpref-in-RF below attend-away)

NO ACTION NEEDED — already dispositioned CODE-RESOLVABLE via the lineage ladder (DR-4C-sign /
A-012): the rendered panel matches `Figure4C.m:74` (`100*(unattCRF-attCRF)/unattCRF`,
suppression sign); the apparent published-panel conflict was a DIGITIZER LABEL SWAP, not a
model or paper defect. Faithful to author code. Confirmed in the 2026-06-10 verify audit.
Flagged for completeness only.

## Finding 4 — figure_3.md / figure_4.md (+ pseudocode, A-013) doc-vs-contract drift

ALREADY RESOLVED by prior commits (0157325 + follow-up), confirmed this pass by direct read
and by the 2026-06-10 paper-fix VERIFY audit:
- `figure_3.md` baseline section → CODE-017 (baselineMod=5e-7 shared; baselineUnmod=5.0 for
  3C / 0.0 for 3F); no residual A-007 0.05.
- `figure_4.md` Panel-C → the A-012 four-separated-stimulus SUPPRESSION build (c_nonpref=0.01,
  cRange [1e-4,0.1]); the retired colocated-x=0 facilitation framing is gone.
- `pseudocode/figure_2_protocol.md` & `figure_3_protocol.md` → x=0 single-stim reduction
  documented as a JUSTIFIED, numerically-verified equivalence; sweep [1e-5,1] (CODE-020).
- `assumptions.yaml` A-013 rule (3) → forbids per-panel baselines TUNED-to-fit while PERMITTING
  the authors' own CODE-017 per-figure values.
No further doc edits required.

## Suite state after this pass

21 failures, all OUTSIDE the resolved contract surface:
- 3 = the 6C contract MUST-PASS (`test_audit_2026_06_10_contract.py`) — the expected-RED
  Phase-B-build-pending state (SQ-009).
- 18 = `test_panel_axes.py` — `ModuleNotFoundError: matplotlib` (rendering tests; the figure
  renderer needs matplotlib, unavailable + no pip in this environment). Environment limitation,
  not a contract/model fault; out of findings scope.
Everything else green (Q-043 included).
