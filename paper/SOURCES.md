# Sources — Reynolds & Heeger 2009, "The Normalization Model of Attention", Neuron 61:168-185 · acquired 2026-06-04

## Obtained
- main article (text) — paper/extracted_text.md — (pre-existing in repo)
- **original code** — paper/code/attentionModel/ — https://snl.salk.edu/~reynolds/Normalization_Model_of_Attention/attentionModel.zip — 2026-06-04 — 304,717 bytes.
  Authors: David Heeger & John Reynolds (2009). Contents: core model `attentionModel.m`
  (`R = E./(I+sigma)+baselineUnmod`, separable 2D suppressive convolution via `conv2sepYcirc`),
  driver `createFigures.m`, per-figure scripts `Figure{2A,2B,3C,3F,4C,4E,5C,6C,7C}.m`, and bundled
  Simoncelli matlabPyrTools helpers (`rconv2`, `upConv`, `conv2sepYcirc`, `makeGaussian`,
  `notDefined`). This is the concrete source of the normalization parameters the paper leaves
  qualitative (defaults: ExWidth=5, EthetaWidth=60, IxWidth=20, IthetaWidth=360, Apeak=2, Abase=1,
  sigma=1e-6; per-figure overrides in the Figure*.m scripts).

## Exists but NOT obtained (KNOWN GAP)
- Supplemental Data (NIHMS107478-supplement.pdf) — supplemental text / limiting-case derivations +
  main-text Table 1 of parameters. Mirror: https://www.cns.nyu.edu/heegerlab/content/publications/Reynolds-Neuron2009-suppl.pdf
  — not fetched this pass (cns.nyu.edu unreachable from the acquisition environment). Impact: the
  parameter Table 1 corroborates the code defaults; the code is the authoritative numeric source.

## Confirmed absent
- (none asserted)

## Searched
- snl.salk.edu (Reynolds mirror — code CONFIRMED, downloaded), www.cns.nyu.edu/heegerlab
  (NYU mirror — listed, unreachable this session), PMC2752446 (article + supplement metadata).
