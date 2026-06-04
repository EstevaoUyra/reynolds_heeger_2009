# Changelog — reynolds_heeger_2009

Newest first. The README "Changelog" table carries the one-line summaries; this file carries the
full detail.

## 2026-06-03 — Current-state README rewrite (update-state skill, model HEAD c8ea505)

**Summary line (mirrored in README):** Current-state rewrite: 8 magnitude flags traced to
CONTRACT_BUG (per-panel suppression) + 6C CODE_BUG (fixed, sharpening restored) + 4E
GENUINE_DIVERGENCE; fresh VLM at HEAD c8ea505 (Fig 1 pass, 2/4/5/6/7 fail, 3 needs_review);
SQ-005 escalated.

**Exit:** `{"overall":"partial","trajectory":"toward_paper","flagged_count":8,"blocked":[]}`.

**What this pass did (state refresh only — no model code, no spec, no test edits):**

- Regenerated `implementation/figure_outputs/figure_*.png` from the current tree (`python -m
  rh_model.views`) so the VLM compared HEAD behavior, including the 6C CODE_BUG fix.
- Ran a fresh **parent direct-read VLM** over all 7 figures (paper vs regenerated output) and
  persisted verdicts at HEAD `c8ea505`:
  `logs/figure_comparisons/figure_*_20260604T012601Z.json`. The prior verdicts were all stale
  (recorded against 885f10b / 3a008a7). The May-2018 "Fig 1 broken" adjudications are superseded:
  the current Fig-1 render is faithful (correct hemifield structure, attention bump over the
  attended stimulus, attended band enhanced).
- Rewrote `README.md` as the current state in the prescribed order: current-exit block at top +
  queued human decisions, model description, per-figure three-view + tier tables, a "potential
  sources of the issues" section from the findings' source hints, and this changelog pointer.

**Figure verdicts of record (deterministic + fresh VLM):**

| Figure | Deterministic | VLM (c8ea505) | State |
|---|---|---|---|
| 1 | 10/10 pass | pass | ✅ FAITHFUL |
| 2 | 25/30 (2B ceiling RED) | fail | ❌ broken — 2A under-saturates (~0.34 vs ~0.62), 2B ceiling off |
| 3 | 24/27 (soft skips only) | needs_review | ❌ broken — residual over-separation (soft shape) |
| 4 | 22/32 (4C/4E RED) | fail | ❌ broken — 4E ~390% overflow, 4C +101% |
| 5 | 10/13 (peak ratio RED) | fail | ❌ broken — peak ratio ~1.59 vs ~1.2 |
| 6 | 12/14 (peak ratio RED) | fail | ❌ broken — sharpening now present, ratio ~1.31 vs ~1.11 |
| 7 | 9/12 (ratio RED) | fail | ❌ broken — variable/fixation ~3.3 vs ~1.4 |
| cross | 0/5 (contract MUST-PASS RED) | n/a | suppression-consistency invariant gating red |

**Root-cause triage (8 flags → 3 mechanism causes):**

1. CONTRACT_BUG — 1D suppression under-normalizes, patched with per-panel
   `suppressive_drive_gain` (2A 12 / 2B 6 / 3C 8 / 3F 12 / 4C 8 / 4E 8; tuning panels none) and
   `suppressive_spatial_sigma_scale` (0.55 / 1.0 / 0.45 / 0.7) + Fig-3 baselines 0.005.
   `test_contract_suppression_consistency.py` (MUST-PASS) RED, 4 tests. Origin of 2A/3C/3F/4C/5C/7C.
   Empirical: unifying the gain to 12 drops 5C 1.586→1.215 (paper value).
2. CODE_BUG (6C) — feature attention was spatially confined at x=−50 so `G_x≈0` at the recorded
   neuron and the curves overlapped; **fixed at HEAD c8ea505** (feature-global in x), restoring
   sharpening (1.01→1.31 peak, 133°→104° FWHM). Same structure pending for 7C attend-nonpref (SQ-006).
3. GENUINE_DIVERGENCE (4E) — γ=5 two-stimulus feature competition drives %-mod to ~390%; survives
   even gain 40. Not a suppression-gain issue.

**Open / escalated:** SQ-005 (the contract's 2D-plane suppression fix is empirically falsified —
makes S smaller, not larger; escalated to Phase A with three options), SQ-006 (formalize
"feature attention is spatially global"), SQ-001/002 (per-panel gains/baselines `audited:false`).
SQ-003 resolved; SQ-004 retired (4C 75° override deleted, retirement encoded MUST-PASS).
