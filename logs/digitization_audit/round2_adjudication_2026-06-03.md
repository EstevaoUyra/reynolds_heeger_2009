# Digitization re-trial — round-2 closure & adjudication (2026-06-03)

Round 1 = digitizer agent → critic agent per figure (reports `figure_<N>_2026-06-03.md`).
Round 2 = targeted re-digitize of each divergent panel (provenance now in the JSONs) +
organizer adjudication with the tools. Final state below; digitizer ≠ critic ≠ organizer.

| Panel | Round-1 finding | Round-2 outcome (adjudicated) | Final |
|---|---|---|---|
| 2B | %-mod ~80% vs paper ~43% | re-traced descending dashed: 99%→42% (matches (att−ign)/ign≈43%) | faithful |
| 3C/3F | "c50/rising-flank too high" | **FALSE POSITIVE.** Round-1 critic calibrated left edge at col 41 (tick-label edge); the axis line is col 56–57 (verified: longest vertical dark run = 179/246 px at col 56–57, none at 41). With correct calibration the round-1 solids match the pixels; only a 3C dashed-bump kink (duplicated points) was a real fix. | faithful |
| 4C | gap understated 3–5× | re-traced both solids separately: gap 0.097@x0.25, 0.046@x0.85; attended plateau 0.78 (matches round-1 critic's independent trace) | faithful |
| 5C | fabricated symmetry + `unattended=attended×0.857` | re-traced independently: attended NOT symmetric; unatt/att ratio spread 0.06 (not a baked constant). Asymmetry magnitude milder than round-1 claimed (round-1 measured about the wrong apex col). | faithful |
| 6C | **critical** — flank crossing missing (identity transposed past ~60°) | re-digitized with the crossing: peak gap +0.097 (contra higher), −0.032 @120° (fixation higher); contra σ≈53 < fixation σ≈61. Crossing reproduced. Caveat: left flank mirrored from right (defensible for a symmetric direction-tuning bell; flagged in provenance). | faithful¹ |
| 4E, 7C | faithful round-1 | unchanged | faithful |

¹ The 6C left-flank mirror is an assumption, not a pixel read; a human may want to confirm the
left flank against the paper if 6C's exact left-side shape becomes load-bearing.

## Process lessons recorded (already actioned)
- **Calibration drives verdict correctness.** The one false positive (3) came from a critic
  calibrating off label text. `detect_plot_box` now scores axis lines by longest *run* (not
  dark density), returning col 56 for fig-3 3C; and `digitize-figure` instructs verifying the
  axis line vs label. Both digitizer and critic must calibrate off the axis LINE.
- **Provenance.** Round-1 digitizers wrote no tool-trail (critics flagged it). Round-2 JSONs
  carry a `provenance` block (figure-type → tools → calibration → per-curve method → caveats);
  `digitize-figure` now requires it and `audit-digitization` reads it.
- **Round-2 digitizers were a different agent than round-1**, so a digitizer disputing a prior
  finding is not self-defense; the organizer adjudicated each with the tools, not by trust.
