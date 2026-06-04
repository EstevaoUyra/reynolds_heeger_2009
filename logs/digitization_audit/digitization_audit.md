# Digitization audit — current verdict (2026-06-03)

The single authoritative judgement on the figure digitizations (the references the
three-tier tests grade against). It supersedes the per-round reports from the iteration
(round-1 critics, round-2 loop-closing, the round-3 artifact fixes) — those live in git
history; this is the current state. Every panel's digitization is at
`article_aware/figures/figure_<N>/panel_<X>_digitized.json` with a `provenance` block, and
its overlay (digitized curves on the paper) at `…/overlay_<panel>.png`.

**Bottom line: all in-scope panels FAITHFUL-DIGITIZATION.** The normalization is the
paper's shared sub-1.0 scale on every figure (no per-panel pinning to 1.0). Verdicts below
state their **basis** — a separate-critic audit, or organizer tool-based adjudication during
loop-closing (the latter noted so a clean final critic pass can be requested if wanted).

| Fig·panel | Verdict | Basis | Key evidence |
|---|---|---|---|
| 2A | faithful | separate critic | curves sit on the paper ink at every zoom; tick-anchored calibration on the axis lines; plateau ~0.615 |
| 2B | faithful | adjudication | %-modulation descends to ~42% at high contrast (= (att−ign)/ign), not the earlier ~80% |
| 3C | faithful | separate critic | %-mod bump apex 24.8% @ x≈0.05 vs paper 24.9%, broad/rounded, no PCHIP overshoot; solids converge ~0.94 |
| 3F | faithful | adjudication | round-1 "c50 too low" was a **calibration artifact** (critic had used the tick-label edge col 41, not the axis line col 56); curves are faithful |
| 4C | faithful | adjudication | attended/ignored gap restored (~0.10 mid → ~0.05 high); attended plateau ~0.78 |
| 4E | faithful | separate critic | crossing wiggle gone, curves monotone; plot-box bottom confirmed row 165 (not the legend-box edge at 207); plateaus pref 0.68 / nonpref 0.50 |
| 5C | faithful | adjudication | both curves traced independently (no fold, no baked `attended×0.857`); genuine right-skew from pixels; peaks 0.97 / 0.83 |
| 6C | faithful | adjudication | feature-based sharpening **crossing recovered** — contralateral narrower (σ≈53 vs 61), higher at peak (+0.10), lower past ~60° |
| 7C | faithful | separate critic | peak ratio variable/fixation ≈1.32 (the old 1.4 refuted); ordering and honest tails |

**Normalization (the headline fix).** The first digitization pinned every curve to 1.0; the
paper uses a shared scale where 2A plateaus ~0.58–0.62 and 2B ~0.85 on the *same* axis (the
height difference is the contrast-gain-vs-response-gain claim). All panels now carry the
paper's scale.

**Method (most recent process).** Tool-grounded (axis calibration, guided tracer, overlay,
PCHIP, `crop_region`), validated by the **adversarial overlay check** (the eye is the arbiter
over the tools; zoom suspect regions), with a **separate critic** distinct from the digitizer.
Three reviewer-flagged overlay artifacts — 2A axis shift (a rendering/calibration bug; data
was faithful), 3C apex spike (a mis-trace), 4E crossing wiggle (tracer jumping curves) — were
caught with the zoom and independently re-verified.

**Honest gap.** The "adjudication" rows (2B, 3F, 4C, 5C, 6C) were settled by the organizer
with the tools during loop-closing, not by a fresh separate-critic audit on the final state.
They are tool-grounded, but a clean final critic pass over the promoted digitizations would
make every panel's current judgement critic-produced. Recommended before the references are
treated as fully binding for gating.

---

## 2026-06-04 — CONTRAST-WINDOW RE-DIGITIZATION (2A/2B/3C/3F/4C/4E)

The 2A/2B/3C/3F/4C/4E digitized `x_range` was the **digitizer's GUESS** ([0.01, 1] / [0.01, 1]);
the panels carry NO numeric x ticks, so the swept range is recoverable only from the author
`Figure*.m cRange` — `[1e-5, 1]` (single-grating 2A/2B/3C/3F) and `[1e-4, 0.1]` (4C/4E),
CODE-020. The prior guess placed the contrast-gain rise ~20–30× too high and clipped the
model's rising limb (half-saturation c≈0.002–0.005) off-window.

**This is a pure x-axis frame RELABEL, not a re-trace.** Each digitized point keeps its exact
pixel position; only its contrast LABEL is recomputed from the same log-fractional position
across the frame under the author window (`c_new = lo·(hi/lo)^f`). The `calibration.x`
pixel-col anchors were relabeled likewise. The traced curve INK on the paper is unchanged, so
the shipped `overlay_*.png` (ink-on-paper) remains pixel-faithful — only the x-axis tick labels
move. Each JSON carries a `provenance.re_digitization_2026_06_04` block recording this.

Result: the model's CRFs now land inside the digitized window and MATCH the digitized
reference (the re-rendered `figure_2_reference.png` / `figure_3_reference.png` over [1e-5,1]
agree with the implementation figures). This closed the 6 digitized-window PAPER_ISSUE
tripwires (`test_audit_2026_06_04_supplement.py`). Resolution authority: author code (Phase-A
resolver ladder rung 1). The relabel does not change any FAITHFUL-DIGITIZATION verdict above —
the curve shapes/values are identical; only the contrast axis is correctly scaled.
