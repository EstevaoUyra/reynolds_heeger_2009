# Spec/Contract Audit — reynolds_heeger_2009 — 2026-06-10

Independent, adversarial Phase-A contract audit of the CORRECTED model vs the
paper + author code (`paper/code/attentionModel/`). Auditor did NOT author the
contract. Verdict: **DIVERGENT** — the *binding* implementation is faithful to
the author code (verified by running it), but the contract's documentation
layer (`model_spec.yaml` Fig-3 overrides + `article_aware/figures/*.md` +
Fig-2/3 pseudocode) is STALE and internally contradicts the corrected
`calibration.yaml` / `code_refs.yaml` / pseudocode-4..7 / the live model.

## Equation/mechanism fidelity — PASS
EQ-1/2/5/6 match attentionModel.m:166-175 operator-for-operator
(R=E./(I+sigma); I=conv2sepYcirc(E,IxKernel,IthetaKernel); E=attnGain.*Eraw).
Separable space×θ conv, unit-volume Gaussian kernels (makeGaussian no-height =
normpdf), zero-pad x / circular θ (conv2sepYcirc.m:18-19). IthetaWidth=360 and
sigma=1e-6 correctly resolved CODE-ALONE (CODE-011/CODE-014). No invented y axis.

## Applied finding re-confirmation (DR-4C-sign) — FAITHFUL
Re-ran run_figure_4C: %-mod peak 37.92% at lowest contrast, declining;
attended ≤ unattended everywhere (suppression). Matches Figure4C.m
(legend 'Att Away','Att RF'; 100*(unattCRF-attCRF)/unattCRF positive). 4E ratio
~1.54 (~54% mod), consistent with the author 4-separated-stimulus geometry. The
applied disposition stands.

## FINDINGS

### F1 (model) model_spec Fig-3 baselines contradict calibration.yaml + superseded A-007
`article_aware/spec/model_spec.yaml:490-491,504-505` set
`baseline_modulated_by_attention: 0.05 / baseline_unmodulated: 0.05  # per A-007`
for figure_3C AND figure_3F. But: (a) A-007 is marked "SUPERSEDED BY CODE"; (b)
`calibration.yaml` carries the binding CODE-017 values — 3C: mod=5e-7, unmod=5.0;
3F: mod=5e-7, unmod=0.0 (asymmetric, per-panel-different); (c) the live
implementation (protocols.py:167-168) reads the calibration values. So the
model_spec overrides are dead-but-wrong: a reader trusting model_spec builds the
wrong symmetric 0.05/0.05 baseline. Internal contract inconsistency.
FIX: replace the 0.05/0.05 model_spec overrides with the CODE-017 values
(3C 5e-7/5.0, 3F 5e-7/0.0) or delete them and point to calibration.yaml.

### F2 (figure) figures/figure_4.md documents the RETIRED facilitation build, contradicting A-012
`article_aware/figures/figure_4.md:35,112,116-119` still narrate the OVERTURNED
4C build: "two colocated stimuli at x=0", "fixed contrast c_nonpref = 0.5",
"facilitation, not suppression", sweep "0.01 to 1". A-012 (RESOLVED) and the
live implementation run the OPPOSITE: FOUR separated stimuli (x=±90/±110),
c_nonpref=0.01, attend-the-null, SUPPRESSION (attended below unattended), sweep
[1e-4,0.1]. figure_4.md:207 even references "the retired C-021 mis-citation"
yet the body still teaches the retired mechanism/sign/contrast. Human-facing doc
contradicts the binding contract.
FIX: rewrite figure_4.md Panel-C section to the A-012 / Figure4C.m separated-
stimulus suppression build (c_nonpref=0.01, cRange [1e-4,0.1]).

### F3 (figure) figures/figure_3.md documents the superseded A-007 0.05 baselines
`figure_3.md:37-38,41-42,91,95` state Fig-3 baselines = 0.05/0.05 (A-007),
contradicting calibration.yaml CODE-017 (5e-7; 5.0 for 3C / 0.0 for 3F).
FIX: update figure_3.md to the CODE-017 baselines and cite CODE-017, not A-007.

### F4 (figure) Fig-2 & Fig-3 pseudocode describe a different experiment than the author code
`pseudocode/figure_2_protocol.md` & `figure_3_protocol.md`: "Single stimulus at
x=0", unattended = "constant 1 (no modulation)", sweep "[0.01,1] with 8 points";
fig-3 also cites A-007 0.05 baselines. Author Figure2A/2B/3C/3F.m: TWO separated
stimuli at x=±100, recorded at x=+100, attended=Ax+100 vs unattended=attend-away
Ax-100 (a real attention field, not A=1), sweep [1e-5,1]. The [0.01,1] in the
pseudocode also contradicts the model's own calibration.yaml/CODE-020 ([1e-5,1]).
NUMERICALLY this reduction is faithful for the recorded neuron: I verified the
impl single-stim-x=0 3C build is BIT-IDENTICAL to a two-separated-stimuli
author-geometry build (the 200-unit / 10σ_IxWidth separation makes the
contralateral stimulus and the attend-away bump invisible at the recorded
neuron). So this is a contract-DESCRIPTION fidelity gap + a stale sweep window
in the pseudocode, not a figure-output divergence. Tracked open as SQ-002
("left article_aware/spec unchanged pending human review") — never folded into
the SQ-005/4C–7C correction wave that fixed the other panels.
FIX: update Fig-2/3 pseudocode to the author two-separated-stimulus geometry
(attended Ax=+100 / unattended attend-away Ax=−100, recorded x=+100), sweep
[1e-5,1], and the CODE-017 baselines; OR document the x=0 single-stim reduction
as an explicit, justified equivalence (with the verified bit-identity) so the
pseudocode stops contradicting calibration.yaml and the author experiment.

## Notes (no finding)
- Code-alone honesty: CODE-011 (360°), CODE-014 (1e-6), CODE-013 (60°),
  CODE-017/020/021 correctly flagged code_alone:true and the 360°-vs-paper-180°
  / σ≈0-vs-paper-semisaturation tensions are stated. Good.
- No per-panel suppressive_drive_gain / sigma_scale in the sanctioned
  calibration surface (A-013 honored).
- Could not run `check_citations` (neuromodels not importable from this path).
