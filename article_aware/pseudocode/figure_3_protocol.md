# Figure 3 Protocol — Reynolds 2000 vs Williford & Maunsell 2006

## Purpose
Reconcile two empirical V4 attention patterns within a single model by
varying stimulus / attention sizes and adding baseline activity.
- 3C (Reynolds 2000): largest percent modulation at low contrast (apparent
  contrast gain).
- 3F (Williford & Maunsell 2006): percent modulation largest at low contrast,
  but largest absolute attended-minus-unattended difference at high contrast.

## Geometry note — x = 0 single-stimulus reduction (justified equivalence to the author two-stimulus setup)

The author scripts (Figure3C.m / Figure3F.m) place TWO separated preferred
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
  the stimulus drive at the recorded neuron (its Gaussian, σ = stimulus_size ≤ 7,
  is negligible 200 units away), so dropping it changes the recorded drive by ~0; and
- the ATTEND-AWAY attention field (Ax = −100, AxWidth = 30) evaluated at x = +100
  has gain ≈ 2.2e-10 ≈ 1·(no boost) — it is ~6.7σ away — so the "attend away"
  unattended field is indistinguishable from a flat (A = 1) field at the recorded
  neuron. Re-centring the single stimulus at x = 0 (rather than +100) is a pure
  coordinate shift of an isolated stimulus and changes nothing at the recorded
  neuron.
So the x = 0 single-stimulus reduction reproduces the author two-separated-
stimulus geometry at the recorded neuron exactly, while being simpler to drive.
(Author geometry: Figure3C.m / Figure3F.m; contrast window: CODE-020.)

## Inputs
- Single stimulus at x = 0, θ = 0 (preferred) — the justified reduction of the
  author two-stimulus geometry above (recorded neuron at the attended stimulus).
- Per panel:
  - 3C: stimulus_size = 5, attention_field_size = 30, γ = 2.
  - 3F: stimulus_size = 7, attention_field_size = 7, γ = 2.
- Baselines per CODE-017 (Figure3C.m:5-6 / Figure3F.m:5-6), superseding the
  earlier A-007 single-shared 0.05·α assumption. The modulated baseline is tiny
  and SHARED; the per-panel difference is in the UNMODULATED post-normalization
  baseline:
  - baseline_modulated_by_attention = 5e-7 (BOTH panels; added to E before
    attention/normalization).
  - baseline_unmodulated = 5.0 for 3C, 0.0 for 3F (added after normalization).

## Sweep
- Contrast c logarithmically across [1e-5, 1] (CODE-020; the published panel has
  no numeric x ticks, so the window is set only by the author scripts' cRange).
- Attention condition ∈ {attended, unattended}.

## Procedure
Application order per attentionModel.m:165-175 (Eraw = conv(stim) + baselineMod;
E = attnGain · Eraw; I = conv(E); R = E/(I + σ) + baselineUnmod):
For each (c, attention_condition):
1. Construct the raw stimulus drive E_raw(x, θ) for the stimulus at contrast c
   per EQ-stim, then add the attention-modulated baseline (CODE-017):
       E_raw_with_baseline(x, θ) = E_raw(x, θ) + baseline_modulated_by_attention
   with baseline_modulated_by_attention = 5e-7 (BOTH panels).
2. Construct A(x, θ): Gaussian centered at the recorded stimulus, peak γ for
   attended; for unattended, the attention field directed AWAY from the recorded
   neuron (≈ flat A = 1 at the recorded location — see the geometry note; the
   author "attend away" field at the recorded neuron is ≈ 2.2e-10 ≈ 1).
3. Form the attention-modulated drive E(x, θ) = A(x, θ) · E_raw_with_baseline(x, θ).
4. Compute S(x, θ) per EQ-6, convolving E (the attention-modulated drive,
   including the modulated baseline) with the suppressive field.
5. Compute R(x, θ) per EQ-5: R = E / (S + σ).
6. Add the unmodulated post-normalization baseline (CODE-017):
       R_obs(x, θ) = R(x, θ) + baseline_unmodulated
   with baseline_unmodulated = 5.0 for 3C and 0.0 for 3F.
7. Record R_obs at the recorded neuron (x = 0, θ = 0 under the reduction;
   = the attended stimulus at x = +100, θ = 0 in the author geometry).

## Outputs
- Per panel: attended_CRF[c], unattended_CRF[c], percent_modulation[c],
  absolute_difference[c] = attended - unattended.

## Expected behavior (citations)
- C-014, C-019 / 3C: percent modulation peaks at low contrast (contrast-gain
  flavor); attended curve leftward-shifted.
- C-014 / 3F: percent modulation still peaks at low contrast, but absolute
  difference largest at high contrast (mixed pattern).
- C-020: Both saturate as c → 1.
- C-021: attended ≥ unattended at every contrast for both.
