# Spec/Contract Audit (paper-fix VERIFY) — reynolds_heeger_2009 — 2026-06-10

Independent, adversarial verification of the CORRECTED contract after the
F1/F2/F3 doc-vs-contract-drift fix (commit 0157325). Auditor did NOT author the
contract or the fix; read the author code (`paper/code/attentionModel/`) directly.

Verdict: **DIVERGENT** — the F1/F2/F3 corrections are faithfully applied and
verified against the author code, but the F4 residue the fix explicitly deferred
(`pseudocode/figure_2_protocol.md` + `figure_3_protocol.md`) is STILL a binding
`pseudocode/` contract artifact that contradicts both the author code and the
model's own corrected calibration — and figure_3_protocol.md additionally still
carries the SUPERSEDED A-007 0.05/0.05 baselines that F1/F3 retired everywhere
else, plus a stale A-013 rule (3) that now forbids the code-mandated 3C/3F
asymmetry.

## VERIFIED-FAITHFUL (the applied F1/F2/F3 fix)

- **F1 model_spec Fig-3 baselines** — VERIFIED against author code.
  Figure3C.m:5-6 `baselineMod=5e-7; baselineUnmod=5;`  Figure3F.m:5-6
  `baselineMod=5e-7; baselineUnmod=0;`. model_spec.yaml:490-491,504-505 now carry
  exactly these (3C 5e-7/5.0, 3F 5e-7/0.0), tagged CODE-017, A-007 marked
  superseded. calibration.yaml figure_3C/3F.baseline_* match. Application order in
  attentionModel.m:165-175 (`Eraw = conv(stim)+baselineMod; E=attnGain.*Eraw;
  R=E./(I+sigma)+baselineUnmod`) matches model_spec pipeline steps 2.5/5.5 and the
  figure_3.md prose operator-for-operator. baselineMod IS attention-modulated
  (added pre-attnGain), consistent with the spec name. FAITHFUL.

- **F3 figure_3.md** — VERIFIED. baseline table (37-38), Panel C/F prose
  (96-141), key-relationships (171-177) all rewritten to CODE-017 (5e-7 shared
  modulated; 5.0 for 3C / 0.0 for 3F unmodulated). No residual A-007 0.05. FAITHFUL.

- **F2 figure_4.md** — VERIFIED against Figure4C.m. Panel-C section now narrates
  the FOUR-separated-stimulus geometry (x=±90/±110), recorded preferred neuron at
  x=100, both conditions attend the null (θ=180), attend-null-in-RF SUPPRESSES
  (attended below unattended), c_nonpref=0.01 fixed, cRange [1e-4,0.1], %-mod =
  100·(unatt-att)/unatt. Matches Figure4C.m:14-21,24,28,51-54,74 exactly. The
  retired colocated-x=0 facilitation build is gone. 4D/4E corrected to the matching
  four-separated geometry. FAITHFUL.

- **DR-4C-sign (A-012) re-confirmation** — re-confirmed code-resolvable. Figure4C.m
  line 74 `100*(unattCRF-attCRF)./unattCRF` plotted on ylim[0 100] is positive ⇒
  unattCRF>attCRF ⇒ Att-RF (attend-null-in-RF) is the LOWER/suppressed curve, with
  legend (line 69) 'Att Away','Att RF'. Note the deliberate sign CONTRAST with
  Fig-3/2 (`100*(attCRF-unattCRF)/unattCRF`, facilitation sign) — the contract
  captures both signs correctly. Faithful to author code; no change required.

## Equation / mechanism fidelity — PASS
EQ-1/2/5/6 match attentionModel.m:165-175 (R=E./(I+sigma)+baselineUnmod;
I=conv2sepYcirc(E,IxKernel,IthetaKernel); E=attnGain.*Eraw). Separable
space×θ conv, unit-volume Gaussians, zero-pad x / circular θ. IthetaWidth=360
(CODE-011), sigma=1e-6 (CODE-014) resolved CODE-ALONE with the paper-tension
stated. No invented y axis. A-013 honored: no per-panel suppressive_drive_gain /
sigma_scale in the sanctioned calibration surface.

## FINDINGS

### F-A (model) figure_3_protocol.md still carries the SUPERSEDED A-007 0.05/0.05 baselines
`article_aware/pseudocode/figure_3_protocol.md:16-18` still binds
`baseline_modulated_by_attention = 0.05 / baseline_unmodulated = 0.05 (per A-007)`.
A-007 is SUPERSEDED BY CODE; CODE-017 (verified above) sets 3C=5e-7/5.0,
3F=5e-7/0.0. The F1/F3 fix updated model_spec.yaml and figure_3.md but left this
`pseudocode/` artifact untouched. A grep confirms this is the ONLY place a 0.05
baseline survives as an ACTIVE instruction (everywhere else it appears only in
"superseded/retired" narration). `pseudocode/` is a binding contract artifact
(audit-spec SKILL Inputs); a reader following figure_3_protocol.md step 2/6 builds
the wrong symmetric 0.05/0.05 baseline. Scope = model (the baseline value is the
model-level CODE-017 calibration, not a rendering choice).
FIX: rewrite figure_3_protocol.md Inputs (16-18) + Procedure step 2/6 to CODE-017
(baselineMod=5e-7 shared; baselineUnmod=5.0 for 3C, 0.0 for 3F), citing CODE-017
not A-007.

### F-B (figure) Fig-2/3 pseudocode geometry + sweep window contradict the author code and calibration.yaml
`pseudocode/figure_2_protocol.md:9,16,22` and `figure_3_protocol.md:12,21,29-30`
describe "single stimulus at x=0", unattended = "constant 1 (no modulation)",
sweep "[0.01,1] with 8 points". Author Figure2A/2B/3C/3F.m: TWO separated stimuli
at x=±100, recorded at x=+100 (i=find(x==stimCenter1)), BOTH conditions a real
attention field (attended Ax=+100 'Att RF' vs unattended Ax=-100 'Att Away', not
A=1), sweep cRange=[1e-5,1]. The [0.01,1] also contradicts the model's own
calibration.yaml/CODE-020 ([1e-5,1]). I VERIFIED the single-stim-x=0 reduction is
NUMERICALLY faithful at the recorded neuron: attend-away spatial gain at x=+100 =
2.2e-10 (≈ A=1; 6.7σ away) and the contralateral stimulus drive at x=+100 = 0.0,
so the contralateral stimulus and attend-away bump are invisible at the recorded
neuron — this is a contract-DESCRIPTION fidelity gap + stale sweep window, NOT a
figure-output divergence. Tracked open by the fix as SQ-002 pending human review.
Scope = figure (description of the per-panel experiment + render sweep window;
the recorded-neuron output is unchanged).
FIX: update Fig-2/3 pseudocode to the author two-separated-stimulus geometry
(attended Ax=+100 / unattended attend-away Ax=-100, recorded x=+100), sweep
[1e-5,1]; OR document the x=0 single-stim reduction as an explicit justified
equivalence (with the verified bit-identity) so the pseudocode stops contradicting
calibration.yaml and the author experiment.

### F-C (model) A-013 rule (3) now contradicts the resolved CODE-017 contract
`article_aware/spec/assumptions.yaml:411-413` — A-013's forbidden-knob list rule
(3) still reads: "per-panel baseline_modulated_by_attention / baseline_unmodulated
values that DIFFER across Fig-3 panels (use the single A-007 0.05·α)". But CODE-017
(now binding, verified) establishes that 3C and 3F baselines DO legitimately differ
(unmod 5.0 vs 0.0) — these are the authors' own per-figure code values, not a
figure-fit. As written, A-013(3) would forbid the very per-panel asymmetry the
author code mandates and the rest of the corrected contract encodes. A-007 head
(182-224) was updated to acknowledge CODE-017, but the A-013(3) cross-reference was
not. Internal contract contradiction (binding rule vs binding calibration).
Scope = model (the rule governs the model-level suppression/baseline calibration).
FIX: amend A-013(3) so it forbids per-panel baselines TUNED-to-fit-a-curve while
permitting the authors' own per-figure code values (CODE-017: 3C 5e-7/5.0, 3F
5e-7/0.0); drop the "use the single A-007 0.05·α" clause.

## Notes (no finding)
- check_citations: `neuromodels` not importable from this path (same environment
  limitation the 2026-06-10 audit noted); could not run the static resolver.
- Code-alone honesty preserved: CODE-011/013/014/017/020/021 flagged code_alone
  with the 360°-vs-180°, σ≈0-vs-semisaturation, 0.05-vs-CODE tensions stated.
- F1/F2/F3 applied corrections are CLEAN; no figure-fitting introduced.
