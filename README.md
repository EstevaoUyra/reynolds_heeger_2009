# Reynolds & Heeger 2009 — Normalization Model of Attention Reproduction

## Model

Reproduction of Reynolds & Heeger (2009), "The Normalization Model of
Attention" (Neuron 61(2):168–185). The model treats attention as a
multiplicative gain on the stimulus drive that is then divisively normalized
by a pooled suppressive drive: `R = ⌊A·E / (S + σ)⌋_T`, with the suppressive
drive computed as `S = s ∗ (A·E)` (citations C-001, C-005, C-006). All four
population fields (stimulus drive `E`, attention field `A`, suppressive
drive `S`, output `R`) live on a shared `(x, θ)` grid (C-009).

Scope of this reproduction covers all seven figures in the paper:
Figure 1 (population pipeline schematic, C-012); Figures 2A/2B
(contrast- vs response-gain CRF regimes, C-013, C-019); Figures 3C/3F
(reconciling Reynolds 2000 and Williford & Maunsell 2006 via stimulus/
attention size ratio, C-014); Figures 4C/4E (two-stimulus CRFs from
Martinez-Trujillo & Treue 2002, C-015); Figure 5C (multiplicative tuning
scaling under spatial attention, C-016, C-022); Figure 6C (feature-attention
tuning sharpening, C-017, C-023); and Figure 7C (combined spatial+feature
shifts, C-018).

## Current state

On branch `arch-migration` (HEAD `3a008a7`; not merged to main). This is a
**structure migration to the ARCHITECTURE shape**, behavior-preserving by
construction: all 10 protocol outputs are byte-for-behavior identical to
pre-migration (hash match), and the 7 generated figures are **pixel-
identical** to the committed pre-migration state `5d3e751` (decoded-array
diff = 0 on every PNG). VLM verdicts are therefore unchanged by
construction; all 7 refreshed fresh at HEAD.

Conflict rule applied literally (det-red = loss; det-green + VLM-red/
needs_review = loss; green needs both, fresh):

- **Green: Figures 3, 5, 6, 7.** Deterministic 13/13, 6/6, 5/5, 6/6 plus
  fresh VLM `pass` (3a008a7). Figure 7 Panel-C-scoped per SQ-003. Unchanged
  from the pre-migration green state.
- **Broken: Figure 1.** Det 10/10 but VLM `fail` — E/S/R fields compressed
  near panel center, attention-field peak near-center not over the right
  stimulus. A Figure-1-specific 1D display/geometry issue, not the
  suppressive-pooling family. Unchanged this migration (Fig-1 geometry was
  relocated verbatim into the implementation ledger).
- **Broken: Figure 2.** Det 12/12 but VLM unanimous `fail` — 2A/2B CRFs do
  not visibly saturate; 2A/2B not visually distinct; no inset schematics.
  Unchanged.
- **Not green: Figure 4.** Det 12/12; VLM `needs_review` — 4C contrast-gain
  recovery good (SQ-004 fix), 4E attend-preferred CRF weak saturation.
  Unchanged.

**Calibration is now a §3 two-ledger split.** Paper-derived ledger
`article_aware/spec/calibration.yaml`: 51 entries, 0 `audited:false` (all
`C-NNN`/spec-fixed). Implementation-side ledger
`implementation/calibration.yaml`: 34 entries, **33 `audited:false`** — the
SQ-001/002/004 class + Figure-1 1D geometry, all relocated verbatim from
`protocols.py` literals. The ledger *contained* the prior 4-SQ sprawl in
one reviewable place; it did not eliminate it (soft blockers SQ-001/002/004
unchanged, green for Fig 3/4C still provisional).

## Next correction

**Target:** Figure 1 — the spatial-layout of `run_figure_1`. **Action:**
this is a human/Phase-A decision, not an agent fix: the Figure-1 1D display
geometry (`figure_1.*` in `implementation/calibration.yaml`:
`stim_left_x/right_x` ±10 on the default ±100 x-grid, the
`*_spatial_sigma_scale` values) places all four population panels near
panel center instead of in the left/right hemifields. **Symptom:** VLM
`fail` (3a008a7) — fields compressed at center; attention-field peak
near-center, suppressive drive one merged band. **Likely scope:**
`implementation/calibration.yaml` `figure_1.*` geometry and the figure-1
display window in `views.py::save_figure_1`. **Hypothesis:** widening the
stimulus separation or the plotted x-window spreads the fields into the two
hemifields; deterministic tests sample only the recorded neuron so they
stay green regardless (why this is VLM-only). Out of scope for the
migration (would change model outputs); flagged for a later
implementation/Phase-A pass.

## Test status

| Figure | Deterministic tests | VLM Test |
|---|---|---|
| Figure 1 | 10 total, 10 (100%) passing | fail (3a008a7) |
| Figure 2 | 12 total, 12 (100%) passing | fail (3a008a7) |
| Figure 3 | 13 total, 13 (100%) passing | pass (3a008a7) |
| Figure 4 | 12 total, 12 (100%) passing | needs review (3a008a7) |
| Figure 5 | 6 total, 6 (100%) passing | pass (3a008a7) |
| Figure 6 | 5 total, 5 (100%) passing | pass (3a008a7) |
| Figure 7 | 6 total, 6 (100%) passing | pass (3a008a7) |
| Unassigned | 17 total, 17 (100%) passing | — |

Deterministic **64/64**, identical pass set to pre-migration. The 17
"Unassigned" are the new ARCHITECTURE-shape implementation tests: stage
contracts (§5(1)), the calibrated-CRF entry-point contract, and the
§5(4) config-only modification smoke test. Figures 1, 2, 4 are
deterministic-green but VLM-red/needs_review → broken by the conflict
rule (unchanged vs pre-migration). Resolved-ledger hash:
`sha256:f00f97488280dc1f`.

Soft blockers (unchanged, now contained in the implementation ledger):
SQ-001/SQ-002 (Fig 2/3 calibration), SQ-004 (Fig 4C per-protocol
suppressive tuning width vs C-011) — `chosen_assumption`, `audited:false`;
Fig 3/4C green is provisional.

## Recent changes

No `logs/changelog.yaml` yet. Last 5 commits:

| Commit | Subject |
|---|---|
| `3a008a7` | arch-migration: stages/measurements/views, two-ledger split, calibrated CRF entry point |
| `5d3e751` | update-state round 2: 64/64 deterministic; re-VLM; Fig 3 green |
| `e88984f` | Fix deterministic CRF failures (2A, 3C/3F, 4C); log SQ-004 |
| `a1ba25b` | update-state: first VLM pass, Fig7 scope (SQ-003) |
| `dc4f838` | Update reproduction state |

## README generation

- 2026-05-12: Queried deterministic/VLM status with
  `/Users/estevaouyra/dev/model_agent/.venv/bin/neuromodels test-table`.
  Needed to embed the current test table verbatim.
- 2026-05-12: Queried latest nonpassing test details with
  `/Users/estevaouyra/dev/model_agent/.venv/bin/python /Users/estevaouyra/dev/model_agent/skills/update-state/scripts/failing_tests.py`.
  Needed exact failing test IDs and failure messages for the next correction.
- 2026-05-12: Queried log freshness with
  `/Users/estevaouyra/dev/model_agent/.venv/bin/python /Users/estevaouyra/dev/model_agent/skills/update-state/scripts/log_freshness.py`.
  Needed to check whether test-table rows were stale relative to the current test surface.
- 2026-05-18: First VLM pass over Figures 1-7; per-figure subagents,
  parent cross-checked Figures 1 and 4 by reading the images directly.
- 2026-05-18: One-shot bulk wrapper to stamp all 7 subagent verdicts with
  provenance (promoted to `skills/update-state/scripts/persist_verdict.py`).
- 2026-05-18: Per-figure verdict freshness via
  `python skills/update-state/scripts/verdict_status.py --model-dir models/reynolds_heeger_2009`.
- 2026-05-18 (round 2): Calibration sweeps for the deterministic CRF fixes
  (reusable sanity checks); re-ran the VLM (2 subagents Figs 1–4).
- 2026-05-18: Figure 7 scope resolved (SQ-003, human); persisted a
  Panel-C-scoped superseding verdict.
- 2026-05-18 (arch-migration): Behavior-preservation gate for the
  structure migration. Beyond the standard scripts I needed two custom
  verifications the helper set does not cover:
  Code:
  ```
  # 1. Byte-for-behavior fingerprint of every protocol output (legacy
  #    keys only) vs a pre-migration baseline — proves the refactor is
  #    behavior-identical, not just test-passing.
  python - <<'PY'
  # sha256 over np.ascontiguousarray bytes of each run_figure_*() dict
  # (filtered to pre-migration keys), incl. the figure-resolution variants
  # views.py uses; compared to /tmp/rh_baseline_fp.json captured at 5d3e751.
  PY
  # 2. Pixel-identity of all 7 generated PNGs vs the pre-migration
  #    committed state, via a throwaway git worktree at 5d3e751:
  git -C models/reynolds_heeger_2009 worktree add /tmp/rh_premig 5d3e751
  # generate figures from both trees, compare decoded matplotlib arrays
  # (np.array_equal) — all 7 PIXEL-IDENTICAL, max abs diff 0.
  git -C models/reynolds_heeger_2009 worktree remove --force /tmp/rh_premig
  ```
  Why: the migration's contract is "model outputs must not change"; the
  existing scripts check test color and verdict freshness but not
  output/figure byte-identity, which is the actual gate for a *structure*
  migration. Candidate future script:
  `scripts/behavior_fingerprint.py <ref>` (protocol-output + figure-pixel
  diff vs a git ref) — recurring need for any migration/refactor run.
