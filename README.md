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

Deterministic suite is **64/64** (was 59/64). VLM verdicts refreshed at
HEAD `e88984f` (all fresh). Conflict rule (any deterministic red = loss;
deterministic-green + VLM-red/needs_review = loss; green needs both):

- **Green: Figures 3, 5, 6, 7.** Deterministic 13/13, 6/6, 5/5, 6/6 plus
  fresh VLM `pass`. Figure 3 is **newly green**: the 3C suppressive-pooling
  fix made it converge; two independent subagents confirm
  attended-above-unattended, 3C convergence, 3F separation. 5/6:
  multiplicative scaling / feature sharpening. Figure 7 Panel-C-scoped per
  SQ-003 (Phase A checklist still needs trimming).
- **Broken: Figure 1.** Deterministic 10/10 but VLM `fail`
  (parent-adjudicated over a 1-pass/1-fail split; the pass run hallucinated
  pixel-measured "two bands"). E/S/R fields are compressed near panel
  center, not in the left/right hemifields (stimuli at x=±10); the
  attention-field peak is near-center, not over the attended right stimulus.
  `run_figure_1` was untouched this session — same broken figure.
- **Broken: Figure 2.** Deterministic now 12/12 but VLM **unanimous fail**:
  2A attended/ignored CRFs still don't visibly converge / look
  non-saturating (the deterministic slope test passes but at fls/mls≈0.918
  is a weak proxy), 2A/2B not visually distinct, inset schematics missing.
- **Not green: Figure 4.** Deterministic 12/12; VLM split → parent: the
  SQ-004 4C fix is verified good (contrast-gain recovery now visible), but
  4E's attend-preferred CRF saturates only weakly. The 2-subagent protocol
  surfaced this latent 4E issue.

Soft blockers: SQ-001/SQ-002 (Fig 2/3 calibration) and **SQ-004** (Fig 4C
per-protocol suppressive tuning width vs C-011) — `chosen_assumption`,
un-audited; Fig 3/4C green is provisional. `test_runs.jsonl` fresh at
`e88984f`.

## Next correction

**Target:** Figure 1 — `run_figure_1` in
`implementation/src/rh_model/protocols.py` (no deterministic red remains; a
VLM-fail with a specific visible discrepancy is the next signal).
**Action:** position the two stimuli / recorded / attended location so the
E/A/S/R fields render across the left and right hemifields (not compressed
at center), with the attention-field peak over the right (attended)
stimulus.
**Symptom:** parent-confirmed by direct image read — all population panels
show signal jammed near panel center; attention-field peak near-center, not
in the right half; suppressive drive one merged central structure rather
than two hemifield-separated bands.
**Likely scope:** `run_figure_1` x-grid extent / stimulus x-positions (±10)
vs the `*_spatial_sigma_scale` calibration, and the figure-1 display window
in `figures.py::save_figure_1` — ±10 on the default ±100 x-grid is too
close together for the plotted range.
**Hypothesis:** a Figure-1-specific display/geometry issue, **not** the
suppressive-pooling family fixed for 2A/3C/4C — deterministic tests sample
the recorded neuron, not the spatial layout, so they stay green regardless
(why this is VLM-only). Widening stimulus separation or the plotted
x-window should spread the fields into the two hemifields.

## Test status

| Figure | Deterministic tests | VLM Test |
|---|---|---|
| Figure 1 | 10 total, 10 (100%) passing | fail (e88984f) |
| Figure 2 | 12 total, 12 (100%) passing | fail (e88984f) |
| Figure 3 | 13 total, 13 (100%) passing | pass (e88984f) |
| Figure 4 | 12 total, 12 (100%) passing | needs review (e88984f) |
| Figure 5 | 6 total, 6 (100%) passing | pass (e88984f) |
| Figure 6 | 5 total, 5 (100%) passing | pass (e88984f) |
| Figure 7 | 6 total, 6 (100%) passing | pass (e88984f) |

Figures 1, 2, 4 are deterministic-green but VLM-red/needs_review → broken by
the conflict rule. Figure 4's `needs_review` is the parent-adjudicated
4C-good / 4E-weak-saturation split.

## Recent changes

No `logs/changelog.yaml` yet. Last 8 commits:

| Commit | Subject |
|---|---|
| `e88984f` | Fix deterministic CRF failures (2A, 3C/3F, 4C); log SQ-004 |
| `a1ba25b` | update-state: first VLM pass, Fig7 scope (SQ-003) |
| `dc4f838` | Update reproduction state |
| `56f5e40` | Strengthen figure article-aware tests |
| `c7bca39` | Refine figure 4-7 visual checklists |
| `43d71a8` | Extract figure 7: initial extraction pending review |
| `fa3dc1b` | Extract figure 6: initial extraction pending review |
| `060ae0f` | Extract figure 5: initial extraction pending review |

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
- 2026-05-18: First VLM pass over Figures 1-7. Drafted subagent context with
  the lib and spawned one VLM subagent per figure; parent cross-checked
  Figures 1 and 4 by reading the images directly.
  Code:
  ```
  for n in 1..7: neuromodels compare-figure-packet $n \
    --model-dir models/reynolds_heeger_2009 \
    --output-file /tmp/rh_figure_packets/figure_$n.json
  # then one subagent per packet, strict-JSON verdict
  ```
  Why: no VLM data existed; this run established the persistent verdict home.
- 2026-05-18: One-shot bulk wrapper to stamp all 7 subagent verdicts with
  provenance and write `logs/figure_comparisons/`.
  Code:
  ```
  python /tmp/persist_verdicts.py   # all 7 verdicts inline, one run
  ```
  Why: needed first-time bulk persistence. Pattern promoted to
  `skills/update-state/scripts/persist_verdict.py` (single-figure, reusable);
  future runs use that script, not ad-hoc Python.
- 2026-05-18: Per-figure verdict freshness / uncovered / adjudications.
  Code:
  ```
  python skills/update-state/scripts/verdict_status.py \
    --model-dir models/reynolds_heeger_2009
  ```
  Why: recurring VLM-side diagnostic for the reflection; added as a script.
- 2026-05-18: Re-ran `neuromodels test-table --model-dir
  models/reynolds_heeger_2009` after persistence to capture the
  now-populated VLM column verbatim.
- 2026-05-18 (round 2): Calibration sweeps for the deterministic CRF fixes
  (now reusable sanity checks).
  Code:
  ```
  python implementation/sanity_checks/check_fig2_saturation.py
  python implementation/sanity_checks/check_fig3_convergence.py
  python implementation/sanity_checks/check_fig4c_saturation.py
  ```
  Why: needed to find A-006/SQ-004 calibration values that satisfy each
  figure's full deterministic predicate set without regression; the fig4c
  sweep is also the SQ-004 evidence (only the C-011 width moves 4C).
- 2026-05-18 (round 2): Re-ran the VLM (2 subagents for Figs 1–4, 1 for
  5–7) after the model fixes; parent-adjudicated the Fig 1 and Fig 4 splits
  by direct image read; persisted via the helper.
  Code:
  ```
  for n in 1..7: neuromodels compare-figure-packet $n ...
  # subagents -> /tmp build script -> persist_verdict.py per figure
  ```
  Why: model changed (2A/3C/4C) so all verdicts had to refresh against the
  new HEAD; the 2-subagent protocol caught a Fig 1 hallucination and a
  latent Fig 4E weak-saturation the prior single run missed.
- 2026-05-18: Figure 7 scope resolved (SQ-003, human). Logged SQ-003 in
  `logs/spec_questions.md` and persisted a Panel-C-scoped superseding
  verdict.
  Code:
  ```
  python skills/update-state/scripts/persist_verdict.py \
    --model-dir models/reynolds_heeger_2009 --figure 7 \
    --packet /tmp/rh_figure_packets/figure_7.json \
    --verdict-file /tmp/figure_7_verdict_panelC.json \
    --adjudication "SQ-003 ... Panel C is the sole deliverable ..."
  ```
  Why: append-only re-verdict via the new helper; flips Figure 7 to green
  without editing article_aware/ (checklist trim deferred to Phase A).
