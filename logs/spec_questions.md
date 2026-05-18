## SQ-001 — suppressive drive gain calibration
date: 2026-04-28
spec_ref: pipeline.compute_suppressive_drive
question: The full convolution implementation follows EQ-6 with an integral-normalized suppressive kernel, but in the 1D discretized protocols this makes S much smaller than A·E at the recorded neuron and leaves the contrast response functions too linear at high contrast. Should the spec include an explicit suppressive_drive_gain / normalization-strength parameter, and should it be per protocol?
chosen_assumption: Added an implementation-side suppressive_drive_gain with per-protocol values tuned only against deterministic qualitative claims; left article_aware/spec unchanged pending human review.

## SQ-002 — figure baseline calibration values
date: 2026-04-28
spec_ref: simulation_protocols.figure_2A; simulation_protocols.figure_2B; simulation_protocols.figure_3C
question: The qualitative claims for percent modulation and saturation require small unmodulated response baselines in Figures 2A/2B and adjusted baseline values in Figure 3C. Should these baseline values be part of the Phase A spec rather than implementation-local calibration?
chosen_assumption: Used small implementation-side baseline_unmodulated values for Figures 2A/2B and adjusted Figure 3C baseline overrides to satisfy deterministic qualitative claims; left article_aware/spec unchanged pending human review.

## SQ-003 — Figure 7 visual checklist scope
date: 2026-05-18
spec_ref: article_aware/figures/figure_7_visual_checklist.md
question: The Figure 7 visual checklist contains structural items for Panels A and B, the A/B/C panel labels, the bottom legend (RF circle / attention-field circles / arrow icons), and the motion-direction arrow row. The Phase B reproduction renders Panel C only. The VLM correctly reports those items as FAIL, dragging an otherwise-correct Figure 7 to needs_review. Is Panel C the sole model-output deliverable for Figure 7, and if so should the out-of-scope structural items be removed from / marked optional in the checklist?
human_resolution: 2026-05-18 — Panel C is the sole deliverable for Figure 7 (confirmed by the project owner). The Panel-A/B/legend/arrow-row items are out of scope. Phase A author should trim or mark-optional those items in figure_7_visual_checklist.md so future VLM runs evaluate only the Panel C content. Until the checklist is trimmed, the update-state VLM step records a parent_adjudication scoping Figure 7's verdict to Panel C (all in-scope items pass → figure is green).
