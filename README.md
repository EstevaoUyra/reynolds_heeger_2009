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

A VLM pass now backs every figure; verdicts are in
`logs/figure_comparisons/` at commit `dc4f838` (fresh — matches HEAD).
Applying the conflict rule (any deterministic red = loss; deterministic-green
+ VLM-red = loss; green needs both):

- **Green: Figures 5, 6, 7.** Deterministic 6/6, 5/5, 6/6 plus fresh VLM
  `pass`. 5/6: multiplicative spatial scaling; feature-attention sharpening.
  Figure 7: SQ-003 was human-resolved 2026-05-18 — Panel C is the sole
  deliverable, so the prior `needs_review` (missing Panels A/B, labels,
  legend, arrow row) is superseded by a Panel-C-scoped `pass`; the Phase A
  checklist still needs trimming (SQ-003). First figures complete.
- **Broken: Figure 1.** Deterministic 10/10 but VLM `fail`,
  parent-confirmed by direct image read — the suppressive drive is a single
  merged bright blob (no two gap-separated bands) and the attention-field
  peak sits near-center, not over the right stimulus. Reclassified from the
  previous "uncovered".
- **Broken: Figures 2, 3, 4.** Deterministic-red; VLM agrees. Figure 4's
  lone VLM `pass` is overridden (parent: 4C does not saturate/converge,
  matching the red). Figure 3's VLM additionally flags the attended curve
  plotted below unattended in 3C/3F (possible swapped labels), internally
  inconsistent with its own positive abs-diff panels.
Deterministic failures unchanged: 2A non-saturating (final log-slope == max
`1.7336`); 3C convergence (`0.2894` !< `0.75·0.3115`); 3F vs 3C separation
(`0.28894` !> `0.28937`); 4C recovery + saturation. Soft blockers SQ-001 /
SQ-002 (`chosen_assumption`, un-audited) still prop up Figures 2/3
calibration. `test_runs.jsonl` is 6 days old but HEAD == `dc4f838`, so the
deterministic test surface still matches (not stale-data).

## Next correction

**Target:** `article_aware/extracted_data/test_figure_2A.py::test_figure_2A_crfs_are_monotonic_and_saturating`
(a deterministic-red test outranks the det-green/VLM-red Figure 1 for the
next-correction slot).
**Action:** make both 2A CRFs level off by the high-contrast endpoint
without losing the contrast-gain left shift.
**Symptom:** `assert 1.7336 < 0.95·1.7336` — final log-slope equals the
maximum log-slope; the CRF is still rising at the right edge.
**Starting point:** `implementation/src/rh_model/protocols.py`
(`run_figure_2A` / `_run_figure_2_panel`) and shared normalization in
`implementation/src/rh_model/model.py`.
**Likely scope:** 2A suppressive normalization strength / baseline
(SQ-001/SQ-002).
**Hypothesis (now cross-figure):** the VLM shows Figure 1's suppressive
drive as an over-diffuse merged blob. A weak or over-broad suppressive
denominator would also leave 2A, 3C and 4C CRFs in a rising, non-saturating
regime — one root cause (under-powered / over-broad suppressive pooling) may
explain both the merged blob and the 2A/3/4 non-saturation. Strengthening or
narrowing the suppressive drive should lower the 2A final log-slope and is
independently checkable against Figure 1's expected two-band structure.

## Test status

| Figure | Deterministic tests | VLM Test |
|---|---|---|
| Figure 1 | 10 total, 10 (100%) passing | fail (dc4f838) |
| Figure 2 | 12 total, 11 (92%) passing | fail (dc4f838) |
| Figure 3 | 13 total, 11 (85%) passing | fail (dc4f838) |
| Figure 4 | 12 total, 10 (83%) passing | pass (dc4f838) |
| Figure 5 | 6 total, 6 (100%) passing | pass (dc4f838) |
| Figure 6 | 5 total, 5 (100%) passing | pass (dc4f838) |
| Figure 7 | 6 total, 6 (100%) passing | pass (dc4f838) |

The Figure 4 cell reads `pass` but the verdict is overridden by a recorded
`parent_adjudication` (deterministic-red wins); the cell reports the raw
verdict, the conflict rule is applied in "Current state".

## Recent changes

No `logs/changelog.yaml` yet. Last 10 commits:

| Commit | Subject |
|---|---|
| `dc4f838` | Update reproduction state |
| `56f5e40` | Strengthen figure article-aware tests |
| `c7bca39` | Refine figure 4-7 visual checklists |
| `43d71a8` | Extract figure 7: initial extraction pending review |
| `fa3dc1b` | Extract figure 6: initial extraction pending review |
| `060ae0f` | Extract figure 5: initial extraction pending review |
| `c68d9fe` | Extract figure 4: initial extraction pending review |
| `959f55f` | Add figure=N markers to article-aware claim tests |
| `476b18d` | Add pytest.ini to scope rootdir per-model |
| `8529ed4` | Fix figure 1 model reproduction |

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
