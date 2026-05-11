# Figure 1 — Visual Checklist

Each item is a binary pass/fail visual claim. Check the box if the generated figure
satisfies it; leave unchecked if not. No paper access is required — all context is
provided within each item. Items tagged `<!-- UNSURE -->` were difficult to read from
the paper figure and deserve extra attention during review.

---

## Coordinate convention

All population panels (Stimulus Drive, Attention Field, Suppressive Drive, Population
Response) share the same 2D layout:

- **Horizontal axis (RF center):** left side = left hemifield; right side = right
  hemifield. The attended stimulus is on the right. Positions are described as "left
  stimulus location" and "right stimulus location" — no numeric values appear on the
  paper's axes; these refer to the left and right bright features.
- **Vertical axis (orientation preference):** spans all orientation preferences. The
  stimuli are vertical gratings, so maximum drive falls at the center of the vertical
  axis (vertical orientation preference).
- **Colormap for Stimulus Drive, Suppressive Drive, Population Response:** black = zero;
  brighter/whiter = larger value.
- **Colormap for Attention Field only:** midgray = 1 (baseline, no attentional gain).
  White = value greater than 1 (attentional enhancement). This panel should contain no
  pure black — the minimum value is 1 (midgray) everywhere.

---

## Panel: Stimulus (schematic)

- [ ] Two grating patches are shown, one on the left side and one on the right side of
      the panel, with a visible gap between them.
- [ ] Both gratings have a vertical orientation (stripes run top to bottom).
- [ ] A small black dot (fixation point) is visible at the center of the panel, between
      the two gratings.
- [ ] A solid circle is drawn around the right-side grating, marking the receptive field.
- [ ] A dashed circle is drawn around the right-side grating, marking the attention field.
- [ ] Both gratings appear equal in contrast (same stripe brightness and spacing on both
      sides).

---

## Panel: Stimulus Drive (E)

- [ ] The panel background is black (or near-black) everywhere except at the two stimulus
      locations.
- [ ] Exactly two bright vertical stripes are present — one in the left half and one in
      the right half of the panel.
- [ ] Both stripes are narrow in the horizontal direction, occupying a small fraction of
      the total panel width. <!-- UNSURE: the paper figure is small and JPEG-compressed; the stripes look thin but the exact fraction is hard to judge -->
- [ ] Both stripes are tall in the vertical direction, extending across a substantial
      portion of the orientation axis. <!-- UNSURE: stripes appear to taper toward top and bottom rather than being fully uniform top-to-bottom; the exact extent is not clearly readable from the figure -->
- [ ] The two stripes are equal in peak brightness — neither is visibly brighter than
      the other.
- [ ] A clear dark gap (black or near-black) separates the two stripes; they do not
      touch or merge.

---

## Panel: Attention Field (A)

- [ ] The panel contains no pure black region — the minimum brightness throughout is
      midgray, not black. (Midgray encodes a gain value of 1; black would incorrectly
      imply gain < 1.)
- [ ] The right half of the panel is visibly brighter than the left half.
- [ ] The left half of the panel appears as midgray (not white, not black), reflecting
      the baseline attention gain of 1.
- [ ] The brightness transition from left (midgray) to peak (bright) is gradual and
      smooth — not a sharp step or a narrow localized peak.
- [ ] The brightest point of the panel is located in the right half of the x-axis,
      roughly in the middle of the right half — not flush against the rightmost edge.
- [ ] The brightness drops back toward midgray before reaching the rightmost edge of
      the panel — the peak is a Gaussian, not a ramp that continues to the edge. <!-- UNSURE: hard to read precisely in the JPEG; the right-edge falloff may be subtle -->
- [ ] The panel is uniform along the entire vertical (orientation) axis — every horizontal
      row is the same shade at any given x position. No vertical banding or gradient is
      present.

---

## Panel: Suppressive Drive (S)

- [ ] Two distinct broad bands of elevated brightness are visible, one centered at the
      left stimulus location and one at the right stimulus location.
- [ ] Each band is substantially wider in the horizontal direction than the corresponding
      stripe in the Stimulus Drive panel — the convolution with the large suppressive
      field has spatially smeared the drive.
- [ ] A dark region is visible between the two bands — they remain distinguishable as
      two separate structures and have not merged into a single uniform blob. <!-- UNSURE: the boundary between the bands and the gap is visually subtle in the paper figure; this is the most commonly misread feature of this panel -->
- [ ] The right band is brighter than the left band, reflecting that the attention field
      amplified the right stimulus drive before pooling. <!-- UNSURE: the brightness difference is present but subtle; the JPEG compression makes it difficult to quantify -->
- [ ] Both bands extend across the full vertical extent of the panel (full orientation
      axis), consistent with the broad orientation tuning of the suppressive field.
- [ ] The background outside the two bands (far left, far right, and between) is dark,
      though not necessarily pure black — the pooling kernel tails produce a low-level
      non-zero floor.

---

## Panel: Population Response (R)

- [ ] The panel background is black (or near-black) everywhere except at the two stimulus
      locations.
- [ ] Exactly two bright vertical stripes are present — one in the left half and one in
      the right half, at the same horizontal positions as the stripes in the Stimulus
      Drive panel.
- [ ] Both stripes are narrow in the horizontal direction, comparable in width to the
      Stimulus Drive stripes — they have not been broadened by the normalization.
- [ ] The right stripe (attended location) is noticeably brighter than the left stripe.
- [ ] The left stripe (unattended location) is present and clearly visible — it is dimmer
      than the right but not suppressed to near-zero. <!-- UNSURE: the left stripe is visibly present in the paper figure but its brightness relative to the right is hard to quantify precisely -->
- [ ] A clear dark gap separates the two stripes; they do not merge.

---

## Cross-panel structural checks

- [ ] The Stimulus Drive stripes and Population Response stripes are approximately the
      same width in x — normalization does not broaden them.
- [ ] The Suppressive Drive bands are visibly wider in x than both the Stimulus Drive
      stripes and the Population Response stripes.
- [ ] The two Stimulus Drive stripes are equal in brightness; the two Population Response
      stripes are unequal (right brighter). This asymmetry is introduced by attention and
      must be present in R but absent in E.
- [ ] The Attention Field panel has a different minimum brightness (midgray) than the
      Stimulus Drive, Suppressive Drive, and Population Response panels (black) — this
      difference in floor value is visible when comparing panels.
- [ ] The pipeline operators are visible in the figure layout: a multiplication symbol
      (×) between Stimulus Drive / Attention Field and the next step, a division symbol
      (÷) before Population Response, and a "pool over space and orientation" label on
      the path to Suppressive Drive.
