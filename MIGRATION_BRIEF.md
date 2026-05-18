# Migration brief — reynolds_heeger_2009 → ARCHITECTURE shape

You are migrating the **already-green** Reynolds & Heeger 2009 reproduction
in this nested repo to the structure in `../../ARCHITECTURE.md`. This is a
**structure migration, not a model change.** The science is correct and
must stay byte-for-behavior identical; only the *shape* changes.

Use the parent `.venv` (`/Users/estevaouyra/dev/model_agent/.venv`) and the
`neuromodels` CLI. Commit milestones inside *this* repo on a branch named
`arch-migration` (do NOT commit to `main`, do NOT touch the parent repo,
never `git add -A` outside this repo).

## Read first

1. `../../STATUS.md` — what is actually built.
2. `../../ARCHITECTURE.md` — the target shape. §1 (stages, **and the
   "depend only on primitive stages, never a calibrated protocol" rule**),
   §2 (protocol→measurement→view), §3 (the **two-ledger split**), §5
   (acceptance incl. modification smoke test).
3. `../../ARCHITECTURE_WATCHLIST.md` — the hermann2010 run finding that
   motivates this: a dependent reusing R&H's *calibrated 1D-CRF protocol*
   had to carry 22 unauditable knobs + a regime-conditional in stage code.
   Eliminating that is the point of this migration.

## Required deliverables

1. **`implementation/src/rh_model/stages/`** — formalize the existing
   forward functions in `model.py` into named, typed-contract stages
   (e.g. `stimulus_drive`, `attention_field`, `suppression`,
   `normalization`, `readout`). Each: declared `consumes`/`produces` with
   shapes **and units**, citation/assumption, and the ledger param names it
   reads (no tunable numeric literals in stage code). R&H is feedforward —
   no ODE integrator stage needed; say so explicitly in `model_spec.yaml`.
2. **`implementation/src/rh_model/measurements.py`** — pure, side-effect-
   free functions producing the typed, schema-versioned measurement record
   that BOTH the deterministic tests and the figures consume (CRF arrays,
   half-max, ratio, abs-diff, **and spatial-layout positions** — the
   Figure-1 layout must be in the record). Single source of truth.
3. **`implementation/src/rh_model/views.py`** — refactor `figures.py` into
   declarative renderers that only read the measurement record. No
   recomputation in the view.
4. **Two-ledger split (§3):**
   - `article_aware/spec/calibration.yaml` — paper-derived params only
     (`source: C-NNN`). This is the *only* permitted change under
     `article_aware/` and only because it is the organizer-designated
     migration; **do not change any test semantics or claims**.
   - `implementation/calibration.yaml` — the implementation-side knobs
     currently scattered in `protocols.py` dicts: the per-protocol
     `suppressive_spatial_sigma_scale`, `suppressive_drive_gain`,
     `baseline_*`, `sigma` overrides, the SQ-001/002/004 class. Namespaced
     per stage/protocol, each with `source: A-NNN|SQ-NNN`, `audited:false`.
5. **A formalized calibrated 1D-CRF entry point** — the deliverable that
   actually fixes the hermann leak. Expose a clean function (e.g.
   `rh_model.crf_protocol.run_crf(stimulus_size, attention_field_size,
   gamma, regime, contrasts)`) that runs the forward stages at the recorded
   neuron over a contrast sweep and **applies the per-protocol
   implementation-side calibration internally** from
   `implementation/calibration.yaml`. A dependent calls it with only the
   scientific parameters and gets a calibrated CRF **without ever seeing or
   carrying** `suppressive_spatial_sigma_scale` etc., and with no
   regime-conditional in the dependent's code. This is the success
   criterion — design it so hermann2010 could depend on it cleanly.

## Behavior-preservation contract (the safety net — gate to merge)

At every milestone commit and before declaring done, ALL must hold:

- `pytest article_aware/extracted_data/` → **64/64**, identical pass set to
  pre-migration (no test semantics changed).
- Generated figures regenerate; the VLM status for Figures 3, 5, 6, 7 is
  unchanged (still pass) and Figures 1, 2, 4 are no better/worse than the
  committed README state — this migration must not change model outputs.
  Re-run the VLM via the honed update-state Step 1b (2 subagents for any
  figure whose verdict you refresh) and persist verdicts.
- The §5(4) **modification smoke test** passes: a config-only stage swap
  (e.g. swap the normalization stage for a trivial variant via
  `implementation/calibration.yaml`/config) regenerates pipeline + record +
  figure with zero unrelated edits.
- `update-state` rewrites `README.md`; the calibration sections reflect the
  two ledgers and the unaudited count.

If behavior changes, you broke the migration — revert that step, don't
adjust the tests.

## What the organizer needs back (≤500 words, signal not transcript)

Whether the formalized 1D-CRF entry point is genuinely clean (could
hermann depend on it with zero carried knobs / zero regime-conditional?);
where the existing code resisted the stage decomposition; the final
two-ledger entry counts (paper-derived vs implementation-side, audited:false);
the behavior-preservation result (64/64? VLM unchanged? smoke test?); and
any ARCHITECTURE.md contract that chafed during a *migration* (vs a
greenfield build). Branch left at `arch-migration` for organizer review;
do not merge to main.
