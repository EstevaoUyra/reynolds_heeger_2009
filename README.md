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

The strengthened article-aware deterministic tests now cover Figures 1-7
with explicit figure metadata. The current test table has 64 deterministic
tests: Figures 1, 5, 6, and 7 are deterministic-pass; Figures 2, 3, and 4
are deterministic-red. There are no recent VLM verdicts in
`logs/figure_comparisons/`, so no figure is complete/green by the project
definition. Figures 1, 5, 6, and 7 are deterministic-pass but visually
uncovered; Figures 2, 3, and 4 are broken before VLM.

The active failures are concrete curve-content checks. Figure 2A fails
`test_figure_2A_crfs_are_monotonic_and_saturating`: the final log slope is
the maximum slope (`1.7336`), so the contrast-gain CRF is still rising at
the right edge. Figure 3C fails high-contrast convergence: final absolute
difference `0.2894` is not below `75%` of peak `0.3115`. Figure 3F fails
the cross-condition high-contrast separation check: final 3F separation
`0.2889` is slightly below 3C `0.2894`. Figure 4C fails both its
high-contrast recovery (`0.6020` is below `0.8 * 0.8733`) and saturation
check (final slope equals max slope `0.3014`).

Soft blockers remain: SQ-001 (`suppressive_drive_gain`) and SQ-002
(implementation-side Figure 2/3 baseline calibration) are
`chosen_assumption`-resolved but not human-audited. These assumptions affect
Figures 2A, 2B, 3C, and 3F and are plausible contributors to the lingering
CRF saturation/separation failures.

## Next correction

**Target:** `article_aware/extracted_data/test_figure_2A.py::test_figure_2A_crfs_are_monotonic_and_saturating`.
**Action:** fix the Figure 2A protocol/implementation so both CRFs visibly
level off by the high-contrast endpoint without losing the contrast-gain
left shift.
**Symptom:** the failure says `assert 1.7336052146980176 < (0.95 * 1.7336052146980176)`;
the final log-slope is also the maximum log-slope.
**Starting point:** inspect `implementation/src/rh_model/protocols.py`
(`run_figure_2A` / `_run_figure_2_panel`) and the shared normalization
parameters in `implementation/src/rh_model/model.py`.
**Likely scope:** the 2A suppressive normalization strength and/or baseline
calibration flagged by SQ-001/SQ-002.
**Hypothesis:** the current 2A denominator is too weak relative to stimulus
drive at high contrast, leaving the CRF in a rising, near-linear regime.
Increasing effective suppressive normalization or adjusting σ/baseline
should reduce the final log-slope while preserving attended >= unattended
and the lower attended half-max contrast.

## Test status

| Figure | Deterministic tests | VLM Test |
|---|---|---|
| Figure 1 | 10 total, 10 (100%) passing | — |
| Figure 2 | 12 total, 11 (92%) passing | — |
| Figure 3 | 13 total, 11 (85%) passing | — |
| Figure 4 | 12 total, 10 (83%) passing | — |
| Figure 5 | 6 total, 6 (100%) passing | — |
| Figure 6 | 5 total, 5 (100%) passing | — |
| Figure 7 | 6 total, 6 (100%) passing | — |

## Recent changes

No `logs/changelog.yaml` yet. Last 10 commits:

| Commit | Subject |
|---|---|
| `56f5e40` | Strengthen figure article-aware tests |
| `c7bca39` | Refine figure 4-7 visual checklists |
| `43d71a8` | Extract figure 7: initial extraction pending review |
| `fa3dc1b` | Extract figure 6: initial extraction pending review |
| `060ae0f` | Extract figure 5: initial extraction pending review |
| `c68d9fe` | Extract figure 4: initial extraction pending review |
| `959f55f` | Add figure=N markers to article-aware claim tests |
| `476b18d` | Add pytest.ini to scope rootdir per-model |
| `8529ed4` | Fix figure 1 model reproduction |
| `d45a20a` | Rename figures, refine figure_2 checklist with saturation estimate |

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
