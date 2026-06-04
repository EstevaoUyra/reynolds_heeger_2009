# Figure 1 — Visual Checklist

Each item is a binary pass/fail visual claim against the rendered figure. No paper access is
required — all context is in the item. Items tagged `<!-- UNSURE -->` were difficult to read
from the paper figure and deserve extra attention. The faith-audit VLM-compares the four
**rendered field panels** (Stimulus Drive, Attention Field, Suppressive Drive, Population
Response) to `figure_1.jpg`.

**These four panels are RENDERED MODEL OUTPUTS, not cartoons.** Only the far-left "Stimulus"
box is a true schematic.

---

## Coordinate and colormap convention

All four field panels share the same 2D layout (axis labels printed on each box):

- **Horizontal axis = "Receptive field center":** left side = left hemifield (x ≈ −100),
  right side = right hemifield (x ≈ +100). The two stimuli sit at x = ±100 on a grid that
  spans roughly [−200, 200], i.e. each stimulus is at the **half-way point between center and
  edge** on its side (not flush against the edge). **The attended stimulus is on the RIGHT.**
- **Vertical axis = "Orientation preference":** vertical orientation (θ = 0) is at the
  **vertical center** of the panel; the axis spans the full orientation range.
- **Colormap for Stimulus Drive, Suppressive Drive, Population Response:** black = 0, white =
  that panel's own maximum (per-panel min–max grayscale).
- **Colormap for Attention Field only:** 0 = black, **1 = midgray**, **2 = white**. The
  baseline gain (1) is midgray; the peak (2) is white. This panel contains **no pure black** —
  its minimum value is 1 (midgray).

---

## Panel: Stimulus (true schematic — context, low-priority)

This box encodes parameters visually; it is not a model render. (Low-priority — the audit
focuses on the four field renders.)

- [ ] Two grating patches are shown, one on the left and one on the right, with a gap between.
- [ ] Both gratings have a vertical orientation (stripes run top to bottom).
- [ ] A small black dot (fixation) is at the center, between the two gratings.
- [ ] A solid circle marks the right-side grating (the RF of the model neuron).
- [ ] A dashed circle marks the right-side grating (the attention field, centered right).

---

## Panel: Stimulus Drive (E) — rendered `Eraw` (PRE-attention)

This panel renders the stimulus drive **before** the attention field is applied, so it is
**left/right symmetric** — the attention asymmetry has NOT entered yet.

- [ ] The background is black (or near-black) everywhere except at the two stimulus locations.
- [ ] Exactly **two** bright vertical stripes are present — one in the left half, one in the
      right half. <!-- forbids a single merged blob or extra stripes -->
- [ ] Both stripes are **narrow** in the horizontal (RF-center) direction, occupying a small
      fraction of the panel width. <!-- width is binding: a stripe as wide as the S band fails -->
- [ ] Each stripe is a **vertically-centered band** that tapers toward the top and bottom — it
      does NOT fill the full height of the panel (it occupies roughly the central ~half). <!-- UNSURE: exact vertical extent is hard to read; the band is clearly bounded, not full-height -->
- [ ] The two stripes are **equal in peak brightness** — neither the left nor the right is
      brighter. (E is `Eraw`, before attention; a render where the RIGHT E stripe is already
      brighter has shown the wrong quantity, `attnGain·Eraw` instead of `Eraw`.) <!-- binding: E must be symmetric -->
- [ ] A clear dark gap separates the two stripes; they do not touch or merge.

---

## Panel: Attention Field (A) — rendered `attnGain`

- [ ] The panel contains **no pure black** region — the minimum brightness is midgray, not
      black. (Midgray = gain 1; black would imply gain 0.)
- [ ] The **right** half of the panel is visibly brighter (toward white) than the left half.
- [ ] The **left** half is uniform **midgray** (baseline gain 1) — not white, not black.
- [ ] The bright region is a **smooth Gaussian bump**, not a sharp step or a thin localized
      line. Its brightest point is in the right half, over the right stimulus (x ≈ +100), and
      brightness drops back toward midgray before the right edge (a Gaussian, not a ramp to the
      edge).
- [ ] The panel is **uniform along the entire vertical (orientation) axis** — every horizontal
      row is the same shade at a given x. No vertical banding or orientation gradient. (The
      attention field is flat in orientation.) <!-- binding: A must be flat in theta -->

---

## Panel: Suppressive Drive (S) — rendered `I`

- [ ] **Two** broad bands of elevated brightness are visible, one over the left stimulus and
      one over the right.
- [ ] Each band is **substantially wider** in the horizontal direction than the corresponding
      Stimulus-Drive stripe — the spatial pooling has smeared each drive peak. <!-- binding: S must be visibly broader than E in x -->
- [ ] A darker region is visible between the two bands — they are distinguishable as two
      separate structures, not one uniform blob. <!-- UNSURE: bands are broad; gap is present but shallow -->
- [ ] The **right band is clearly brighter** than the left band. (Attention multiplies the
      right drive by ~2 before pooling, so the right band is enhanced.) <!-- binding: attention asymmetry must appear in S -->
- [ ] Each band spans the **full vertical (orientation) extent** of the panel and is nearly
      uniform top-to-bottom — there is no narrow horizontal banding in θ. (The θ-pool is
      near-flat, σ_θ = 360°.) <!-- binding signature of the broad-theta suppressive pool -->
- [ ] The background outside the bands is dark but not necessarily pure black (broad pooling
      tails leave a low floor).

---

## Panel: Population Response (R) — rendered

- [ ] The background is black (or near-black) everywhere except at the two stimulus locations.
- [ ] Exactly **two** narrow bright stripes are present — at the same horizontal positions as
      the Stimulus-Drive stripes (x ≈ ±100).
- [ ] Both stripes are **narrow** in x — comparable in width to the Stimulus-Drive stripes,
      **NOT** broadened to the width of the Suppressive-Drive bands. <!-- binding: R width ≈ E width, not S width -->
- [ ] The **right stripe (attended) is noticeably brighter** than the left stripe. <!-- binding: attention asymmetry must appear in R -->
- [ ] The **left stripe (unattended) is present and visible**, just dimmer than the right — it
      is NOT suppressed to near-zero (no winner-take-all). <!-- binding: left stripe must survive -->
- [ ] A clear dark gap separates the two stripes; they do not merge.

---

## Cross-panel structural checks (binding inter-panel claims)

- [ ] **E is symmetric, S and R are right-biased.** The two Stimulus-Drive stripes are equal
      in brightness; the right band/stripe is brighter than the left in BOTH the Suppressive
      Drive and the Population Response. (The asymmetry is introduced by attention via
      `E = attnGain·Eraw`, which feeds S and R but not the rendered E.) <!-- binding: asymmetry in S&R, absent in E -->
- [ ] **S is wider than E and R in x.** The Suppressive-Drive bands are visibly wider in the
      RF-center direction than both the Stimulus-Drive stripes and the Population-Response
      stripes.
- [ ] **R width ≈ E width.** The Population-Response stripes and the Stimulus-Drive stripes are
      about the same width in x — normalization did not broaden R to the S band width.
- [ ] **A has a different floor.** The Attention-Field panel's minimum is midgray, whereas the
      Stimulus Drive, Suppressive Drive, and Population Response panels have a black (≈0)
      floor — this floor difference is visible when comparing panels.
- [ ] **Panel layout: exactly four field renders** (Stimulus Drive, Attention Field,
      Suppressive Drive, Population Response) plus the left Stimulus schematic, arranged as a
      flow diagram. The pipeline operators are present: a multiplication symbol (×) joining
      Stimulus Drive and Attention Field, a "pool over space and orientation" label on the
      path to the Suppressive Drive, and a division symbol (÷) before the Population Response.
      No additional field panels are present. <!-- forbids spurious extra panels -->

---

## Sufficiency demonstration (a deliberately-wrong figure must FAIL)

The checklist is constructed so each of the following known-bad renders fails at least one
binding item — it does not merely pass the correct figure:

1. **E rendered as `attnGain·Eraw` (post-attention) instead of `Eraw`** → its right stripe is
   brighter than its left → fails "the two Stimulus-Drive stripes are equal in peak
   brightness" and "E is symmetric."
2. **Attention asymmetry dropped (γ = 1, or attention not applied)** → S bands equal, R stripes
   equal → fails "right S band brighter," "right R stripe brighter," and the cross-panel
   asymmetry item.
3. **Narrow θ suppressive pool (e.g. σ_θ = 30° instead of 360°)** → S bands show a
   vertically-bounded band that does NOT fill the full orientation height → fails "each S band
   spans the full vertical extent and is nearly uniform top-to-bottom."
4. **R not divided by S (R ∝ E or R ∝ A·E only)** → R stripes as broad as S bands, or no left
   stripe survives → fails "R stripes narrow, comparable to E (not S width)" and/or "left R
   stripe present."
5. **Attention field rendered with a 0-floor / per-max scale so baseline → black** → A panel
   shows black on the left → fails "A contains no pure black; left half is midgray."
6. **Attention field given orientation tuning (not flat)** → A shows vertical banding/gradient
   → fails "A is uniform along the entire orientation axis."
7. **A spurious extra field panel (e.g. an `E = attnGain·Eraw` panel added)** → fails "exactly
   four field renders … no additional field panels."
