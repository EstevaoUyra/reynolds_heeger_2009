# Figure 7 Protocol — Two Stimuli in RF, Three Attention Conditions

## Purpose
Reproduce Treue & Martinez-Trujillo (1999): with two stimuli in the same RF
(one nonpreferred and fixed, one variable direction), spatial+feature
attention to one or the other shifts the tuning curve in opposite ways.

## Inputs
> **AUTHORS' Figure7C.m (CODE-018/CODE-021) — the authoritative 7C contract.**
> The two in-RF stimuli are at **SEPARATED** x positions (93 and 107), NOT
> co-located at x=0. Co-locating them lets feature competition crush the
> nonpreferred response and inflates the variable/fixation peak ratio to ~2.73;
> the author's separated geometry through the committed `simulate` lands ~1.41,
> matching the paper's ~1.4 (faithfulness_audit Finding D).

- **TWO separated stimuli**, both in the receptive field of the recorded MT
  neuron (RF centred at **x = 100** = round(mean(93,107))), contrast 1.0
  (CODE-021), spatial σ = stimWidth = 5:
  - **Variable stimulus**: x = 93, motion direction θ_var varied across trials.
  - **Nonpreferred/null stimulus**: x = 107, motion direction θ_np = 180°
    (opposite to the neuron's preferred), fixed.
  - Stimulus construction (CODE-021): each in-RF stimulus is scaled LINEARLY by
    contrast — `stim_var = contrast · G(x=93, θ_var)`,
    `stim_null = contrast · G(x=107, θ_np=180)`, `pair = stim_var + stim_null`.
    At contrast = 1.0 this is the unit-height pair. (7C has NO contralateral
    stimulus; "attend away" is a spatial field at x = -100.)
- Recorded neuron: preferred θ = 0, RF centre x = 100; response read at
  (θ = 0, x = 100).
- Three attention conditions (Panel C = the three "Pair" curves):
  - **Attend fixation** (`Pair Away`): spatial field away from the RF at
    `att_away_loc = -100` (AxWidth = 5), feature-flat (Atheta = NaN → flat in θ).
  - **Attend nonpreferred** (`Pair Null`): spatial field at the null stimulus
    `Ax = 107` (AxWidth = 5), feature-selective for θ_np = 180° (AthetaWidth = 45°).
  - **Attend variable** (`Pair Var`): spatial field at the variable stimulus
    `Ax = 93` (AxWidth = 5), feature-selective for the current θ_var (AthetaWidth = 45°).
- Parameters: stimulus_size (stimWidth) = 5, attention_field_size (AxWidth) = 5,
  tuning_width (AthetaWidth) = 45° (for the feature-selective conditions),
  γ (Apeak) = 5, contrast = 1.0 (CODE-021).

> **Scope (SQ-003, human-resolved):** Panel C is the sole model-output
> deliverable. The three Panel-C curves are the "Pair" conditions above; the
> author script also computes alone-stimulus controls (Var-var / Null-null /
> Var-away) that are not part of the reproduced Panel-C deliverable.

## Sweep
- θ_var across [-180°, 180°] (the author uses linspace(-180,180,numOrientations)).
- Stimulus contrast: **fixed at 1.0** (CODE-021).
- Attention condition ∈ {fixation, nonpreferred, variable}.

## Procedure
For each (θ_var, attention_condition):
1. Construct E(x, θ) from the separated pair:
   `pair = contrast·G(x=93, θ=θ_var) + contrast·G(x=107, θ=180°)`, contrast = 1.0.
2. Construct A(x, θ):
   - fixation: spatial Gaussian at x = -100 (AxWidth = 5), flat in θ.
   - nonpreferred: spatial Gaussian at x = 107, feature-selective at θ = 180°
     (σ_θ = 45°).
   - variable: spatial Gaussian at x = 93, feature-selective at θ = θ_var
     (σ_θ = 45°).
3. Compute S, R per EQ-6, EQ-5.
4. Record R(θ = 0, x = 100) — the recorded neuron at the RF centre.

## Outputs
- fixation_tuning[θ_var]       (= `Pair Away`)
- attend_nonpref_tuning[θ_var] (= `Pair Null`)
- attend_variable_tuning[θ_var](= `Pair Var`)

## Expected behavior (citations)
- C-018, C-021 / Tuning when attending the variable stimulus has larger
  responses near the preferred direction than the fixation baseline.
- C-018, C-021 / Tuning when attending the nonpreferred stimulus has smaller
  responses near the preferred direction than the fixation baseline.
- The two attention conditions (variable vs nonpreferred) shift the apparent
  tuning in opposite directions.
- Magnitude (author separated geometry): attend-variable/fixation peak ratio
  ≈ 1.41, matching the paper's ~1.4 (faithfulness_audit Finding D); ordering
  attend-variable > fixation > attend-nonpreferred near θ = 0.
