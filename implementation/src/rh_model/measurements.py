"""Pure measurement functions → the typed, schema-versioned record.

ARCHITECTURE.md §2: measurement is the contract and the **single source
of truth**. These functions are side-effect-free; they turn a raw
protocol sweep into the small typed record that BOTH the deterministic
tests and the view read. No model recomputation happens in the view.

The record is a *superset* of the legacy protocol-output dict: every key
the pre-migration ``run_figure_*`` returned is preserved with byte-for-
behavior-identical values (this is a structure migration), plus:
  - ``schema_version`` and ``resolved_ledger_hash`` (§3 traceability),
  - structural facts the figure shows but a curve test alone cannot
    guard: half-max contrasts, ratios, abs-diff, and — for Figure 1 —
    the **spatial-layout positions** (peak x of each population field,
    half-height stripe regions). Putting layout IN the record is what
    structurally prevents the Figure-1 class (deterministically perfect,
    visually broken): a deterministic test now guards what the plot
    shows.

Pure: no I/O, no plotting, no global state.
"""

from __future__ import annotations

import numpy as np

from .calibration import calibration_hash

SCHEMA_VERSION = 1


# --- shared scalar measurements -------------------------------------------

def _half_max_contrast(response: np.ndarray, contrast: np.ndarray) -> float:
    """Contrast where a CRF first reaches half its max (log-contrast interp).

    Matches article_aware/extracted_data/rh_claim_helpers.half_max_contrast
    so the record's half-max is the SAME quantity the tests compute.
    """
    response = np.asarray(response, dtype=float)
    contrast = np.asarray(contrast, dtype=float)
    target = 0.5 * float(response.max())
    above = np.flatnonzero(response >= target)
    if len(above) == 0:
        return float("nan")
    idx = int(above[0])
    if idx == 0:
        return float(contrast[0])
    c0, c1 = np.log(contrast[idx - 1]), np.log(contrast[idx])
    r0, r1 = response[idx - 1], response[idx]
    if r1 == r0:
        return float(contrast[idx])
    t = (target - r0) / (r1 - r0)
    return float(np.exp(c0 + t * (c1 - c0)))


def _safe_pm(attended: np.ndarray, unattended: np.ndarray) -> np.ndarray:
    """Percent modulation, guarded against div-by-near-zero (== legacy)."""
    denom = np.where(np.abs(unattended) > 1e-9, unattended, 1e-9)
    return 100.0 * (attended - unattended) / denom


def _regions_above_fraction(
    x_grid: np.ndarray, values: np.ndarray, fraction: float
) -> list[tuple[float, float, float]]:
    """Contiguous (x_start, x_end, width) regions ≥ fraction·max.

    Same algorithm the Figure-1 test uses; here it lives in the record so
    spatial structure is a first-class measured quantity.
    """
    x_grid = np.asarray(x_grid, dtype=float)
    values = np.asarray(values, dtype=float)
    threshold = float(fraction) * float(np.max(values))
    above = np.flatnonzero(values >= threshold)
    if len(above) == 0:
        return []
    regions: list[tuple[int, int]] = []
    start = prev = int(above[0])
    for idx in map(int, above[1:]):
        if idx != prev + 1:
            regions.append((start, prev))
            start = idx
        prev = idx
    regions.append((start, prev))
    return [
        (float(x_grid[s]), float(x_grid[e]), float(x_grid[e] - x_grid[s]))
        for s, e in regions
    ]


def _provenance() -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "resolved_ledger_hash": calibration_hash(),
    }


# --- per-figure records ----------------------------------------------------

def figure_1_record(raw: dict) -> dict:
    """Figure 1 record: legacy fields + spatial-layout positions.

    `raw` is the population-field output of the Figure-1 protocol
    (x_grid, E/A/S/R slices and fields, recorded responses). The added
    ``spatial_layout`` block records WHERE the fields sit so a
    deterministic test guards the layout the schematic shows
    (Figure-1-class prevention, §2).

    Citation: C-005, C-006, C-009, C-012 ; Assumption: A-006
    """
    x = np.asarray(raw["x_grid"], dtype=float)
    rec = dict(raw)  # preserve every legacy key byte-for-behavior identically

    def _peak_x(slice_: np.ndarray) -> float:
        return float(x[int(np.argmax(np.asarray(slice_, dtype=float)))])

    rec["spatial_layout"] = {
        "x_min": float(x[0]),
        "x_max": float(x[-1]),
        "E_peak_x": _peak_x(raw["E_slice"]),
        "A_peak_x": _peak_x(raw["A_slice"]),
        "S_peak_x": _peak_x(raw["S_slice"]),
        "R_peak_x": _peak_x(raw["R_slice"]),
        "E_half_height_regions": _regions_above_fraction(x, raw["E_slice"], 0.5),
        "S_half_height_regions": _regions_above_fraction(x, raw["S_slice"], 0.5),
        "R_half_height_regions": _regions_above_fraction(x, raw["R_slice"], 0.5),
        "R_at_attended": float(raw["R_at_attended"]),
        "R_at_unattended": float(raw["R_at_unattended"]),
    }
    rec.update(_provenance())
    return rec


def crf_pair_record(
    contrast: np.ndarray,
    attended: np.ndarray,
    unattended: np.ndarray,
    *,
    contrast_key: str = "c",
    with_absolute_difference: bool = False,
) -> dict:
    """Record for an attended/unattended CRF pair (Figs 2, 3, 4C).

    Keeps the legacy keys (attended_CRF, unattended_CRF,
    percent_modulation, [absolute_difference], <contrast_key>) byte-
    identical, and adds half-max contrasts as measured structural facts.

    Citation: C-013, C-014, C-015 ; Assumption: A-006
    """
    attended = np.asarray(attended, dtype=float)
    unattended = np.asarray(unattended, dtype=float)
    contrast = np.asarray(contrast, dtype=float)
    rec: dict = {
        "attended_CRF": attended,
        "unattended_CRF": unattended,
        "percent_modulation": _safe_pm(attended, unattended),
        contrast_key: contrast,
    }
    if with_absolute_difference:
        rec["absolute_difference"] = attended - unattended
    rec["half_max"] = {
        "attended": _half_max_contrast(attended, contrast),
        "unattended": _half_max_contrast(unattended, contrast),
    }
    rec.update(_provenance())
    return rec


def crf_ratio_record(
    contrast: np.ndarray,
    attend_pref: np.ndarray,
    attend_nonpref: np.ndarray,
) -> dict:
    """Record for the Figure-4E attend-pref / attend-nonpref ratio pair.

    Citation: C-015 ; Assumption: A-006
    """
    attend_pref = np.asarray(attend_pref, dtype=float)
    attend_nonpref = np.asarray(attend_nonpref, dtype=float)
    contrast = np.asarray(contrast, dtype=float)
    rec = {
        "attend_pref_CRF": attend_pref,
        "attend_nonpref_CRF": attend_nonpref,
        "ratio": attend_pref / np.where(attend_nonpref > 1e-9, attend_nonpref, 1e-9),
        "c": contrast,
    }
    rec.update(_provenance())
    return rec


def tuning_record(fields: dict) -> dict:
    """Record for a tuning-curve protocol (Figs 5C, 6C, 7C).

    `fields` is the legacy output dict; this preserves every key and
    attaches provenance. (The tuning figures have no extra structural
    facts beyond the curves; FWHM is computed in the test/view helper.)

    Citation: C-016, C-017, C-018 ; Assumption: A-006
    """
    rec = dict(fields)
    rec.update(_provenance())
    return rec


__all__ = [
    "SCHEMA_VERSION",
    "figure_1_record",
    "crf_pair_record",
    "crf_ratio_record",
    "tuning_record",
]
