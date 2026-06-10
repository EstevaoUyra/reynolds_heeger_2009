"""RETIRED: Figure 6C feature-attention CODE_BUG tests (2026-06-03 audit) — SUPERSEDED.

These tests encoded the 2026-06-03 framing of the 6C divergence: that the attend-
opposite spatial Gaussian at x=-50 STRIPPED the feature gain from the recorded neuron
(x=0), so the two curves OVERLAPPED (peak ratio ~1.01, no sharpening), and the fix was
to make the feature component reach the RF. The must-pass bounds were:

    test_feature_attention_reaches_recorded_neuron_peak_enhancement : peak ratio >= 1.08
    test_feature_attention_sharpens_tuning_at_recorded_neuron       : sharpening >= 18 deg

WHY THEY ARE RETIRED (2026-06-10 contract audit)
------------------------------------------------
The model has since moved PAST that overlap state: the committed flat-x proxy now DOES
reach the RF and OVER-corrects, rendering peak ratio ~1.167 and FWHM ratio ~0.79. Against
that state the old bounds are both wrong:

  * ``peak ratio >= 1.08`` is satisfied by the OVER-scaled 1.167 — too loose / wrong
    direction; it lets the contract bug through (a faithful render is 1.108, NOT ">=1.08
    unbounded above").
  * ``sharpening >= 18 deg`` would REJECT the CORRECT author 'cross' mechanism (author
    sharpening is ~17 deg, FWHM ratio ~0.87-0.89) while ACCEPTING the over-sharpened
    proxy (~30 deg) — it points the wrong way.

The 2026-06-10 contract audit RE-ROOT-CAUSED 6C as a CONTRACT_BUG: ``run_figure_6C``
ignores the binding ledger geometry it already records (stim_rf_x=100, stim_contra_x=
-100, attend_fixation_x=0) and the documented Ashape='cross', using instead a hard-coded
-50/50 flat-x full-γ proxy that over-scales and over-sharpens. The correct, faithful
two-sided targets (peak ratio 1.108 ±0.01; FWHM ratio 0.87-0.89) are now encoded in
``test_audit_2026_06_10_contract.py`` as the authoritative 6C MUST-PASS, and the
proxy-≠-'cross' mechanism tripwire lives in ``test_audit_2026_06_10.py``. Per
skills/author-tests/SKILL.md ("if the finding's number looks off, flag it back — do not
encode a wrong target the implementer would then chase") these stale single-sided bounds
are retired rather than left to mis-certify the over-corrected state.

These tests are kept as explicit ``skip``s (not deleted) so the supersession is visible
in the suite and the claim-ids are not silently dropped.
"""

from __future__ import annotations

import pytest

_SUPERSEDED_BY = (
    "test_audit_2026_06_10_contract.py (T-A610C-6C-peak-ratio / -fwhm-ratio / "
    "-ledger-geometry) + test_audit_2026_06_10.py (6C proxy-≠-'cross' mechanism tripwire)"
)


@pytest.mark.skip(reason=f"RETIRED (2026-06-10 contract audit): stale single-sided "
                  f"peak-ratio>=1.08 bound certifies the over-scaled 1.167 contract bug; "
                  f"superseded by {_SUPERSEDED_BY}.")
def test_feature_attention_reaches_recorded_neuron_peak_enhancement():
    """RETIRED — see module docstring. The faithful 6C peak ratio is 1.108 (±0.01), a
    TWO-sided band now pinned in test_audit_2026_06_10_contract.py; the old open-above
    >=1.08 bound let the over-scaled 1.167 contract bug pass."""


@pytest.mark.skip(reason=f"RETIRED (2026-06-10 contract audit): stale sharpening>=18deg "
                  f"bound REJECTS the correct author 'cross' (~17deg) and accepts the "
                  f"over-sharpened proxy; superseded by {_SUPERSEDED_BY}.")
def test_feature_attention_sharpens_tuning_at_recorded_neuron():
    """RETIRED — see module docstring. The faithful 6C sharpening is FWHM ratio
    0.87-0.89 (~17deg), now pinned in test_audit_2026_06_10_contract.py; the old
    >=18deg bound pointed the wrong way (rejecting the correct mechanism)."""
