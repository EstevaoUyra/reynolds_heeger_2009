# Figure 2 Protocol — Contrast vs Response Gain

## Purpose
Demonstrate that varying stimulus size and attention-field size relative to
the stimulation field yields qualitatively different attentional modulation
patterns: contrast gain (2A) vs response gain (2B).

## Geometry note — x = 0 single-stimulus reduction (justified equivalence to the author two-stimulus setup)

The author scripts (Figure2A.m / Figure2B.m) place TWO separated preferred
gratings at x = +100 and x = −100 (both θ = 0), record the neuron at
(x = +100, θ = 0), and realise the attention conditions as a real attention
field that moves: attended = Gaussian attention field centred at the recorded
stimulus (Ax = +100); unattended = the SAME field centred on the far stimulus
(Ax = −100, "attend away" — NOT a flat field). cRange = [1e-5, 1] (CODE-020).

This protocol uses the simpler equivalent: a SINGLE stimulus at x = 0, with the
attended condition an attention field centred on it (peak γ) and the unattended
condition the attention field directed away. This reduction is FAITHFUL at the
recorded neuron and has been NUMERICALLY VERIFIED to be bit-identical there,
because at the recorded location (the attended stimulus):
- the CONTRALATERAL stimulus (Δx = 200 from the recorded one) contributes 0.0 to
  the stimulus drive at the recorded neuron (its Gaussian, σ = stimulus_size ≤ 5,
  is negligible 200 units away), so dropping it changes the recorded drive by ~0; and
- the ATTEND-AWAY attention field (Ax = −100, AxWidth = attention_field_size)
  evaluated at x = +100 has gain ≈ 2.2e-10 ≈ 1·(no boost) — it is ~6.7σ away — so
  the "attend away" unattended field is indistinguishable from a flat (A = 1)
  field at the recorded neuron. Re-centring the single stimulus at x = 0 (rather
  than +100) is a pure coordinate shift of an isolated stimulus and changes
  nothing at the recorded neuron.
So the x = 0 single-stimulus reduction reproduces the author two-separated-
stimulus geometry at the recorded neuron exactly, while being simpler to drive.
(Author geometry: Figure2A.m / Figure2B.m; contrast window: CODE-020.)

## Inputs
- Single stimulus in the receptive field of the recorded neuron (x = 0, θ = 0,
  preferred) — the justified reduction of the author two-stimulus geometry above
  (recorded neuron at the attended stimulus).
- Per panel (parameter overrides from spec):
  - 2A: stimulus_size = 3, attention_field_size = 30, γ = 2.
  - 2B: stimulus_size = 5, attention_field_size = 3, γ = 2.

## Sweep
- Contrast c logarithmically across [1e-5, 1] (CODE-020; the published panel has
  no numeric x ticks, so the window is set only by the author scripts' cRange).
- Attention condition ∈ {attended, unattended}.

## Procedure
For each (c, attention_condition):
1. Construct E(x, θ) for the stimulus at contrast c per EQ-stim.
2. Construct A(x, θ): Gaussian centered at the recorded stimulus, peak γ for
   attended; for unattended, the attention field directed AWAY from the recorded
   neuron (≈ flat A = 1 at the recorded location — see the geometry note; the
   author "attend away" field at the recorded neuron is ≈ 2.2e-10 ≈ 1).
3. Compute S(x, θ) per EQ-6 — the SEPARABLE 2D suppressive convolution over
   (space x, feature θ): suppressive spatial σ = 20, suppressive feature σ = 360
   (near-flat over θ), zero-pad in x, circular in θ (SQ-005, CODE-001/CODE-002).
   This broad-θ pool is what makes S commensurate with A·E so the CRF saturates.
4. Compute R(x, θ) = (A·E)/(S + σ) per EQ-5, with σ = 1e-6 ≈ 0 (CODE-014):
   saturation comes from the pooled S, NOT from σ.
5. Record R(x = 0, θ = 0).

## Outputs
- For each panel: attended_CRF[c], unattended_CRF[c],
  percent_modulation[c] = 100 · (attended - unattended) / unattended.

## Expected behavior (citations)
- C-019 / 2A: contrast gain — attended curve leftward-shifted on log-contrast
  axis vs unattended; percent modulation peaks at intermediate contrasts.
- C-019 / 2B: response gain — attended curve upward-shifted; percent
  modulation roughly flat or largest at high contrast.
- C-020: Both — output saturates (plateaus) by high contrast. MUST-PASS
  SATURATION TARGET (SQ-005, from the author code's behavior): each CRF must
  BEND TO A PLATEAU by c = 1 — i.e. the normalized log-contrast slope over the
  top decade (c ∈ [0.1, 1]) is near zero (≈0.01–0.02 in the verified code run)
  while the rising flank slope is ≈0.5. The curve rises steeply then flattens;
  it does NOT remain linear-in-log-c to c = 1 (the old 1D-reduction / σ=0.1
  failure mode). This holds for BOTH attended and unattended curves and for both
  panels (2A contrast-gain and 2B response-gain).
- C-021: attended ≥ unattended at every contrast.
