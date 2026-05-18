"""Resolved calibration ledger access (ARCHITECTURE.md §3).

Calibration is DATA, not constants. R&H has the §3 **two-ledger split**:

- ``article_aware/spec/calibration.yaml`` — *paper-derived* params (values
  the paper states or that follow from it). Phase A owns it; Phase B reads
  only. ``source: C-NNN``.
- ``implementation/calibration.yaml`` — *implementation-side* calibration:
  the 1D-discretization knobs and per-protocol overrides that used to be
  scattered as literals in ``protocols.py`` dicts (the SQ-001/002/004
  class). Phase B writes this. ``source: A-NNN | SQ-NNN``.

Model/stage code receives the **merged resolved** ledger and holds no
tunable numeric literals. The resolved-ledger hash is recorded in every
measurement record so a figure is always traceable to exact calibration.

Both ledgers are namespaced per stage/protocol:
``<ns>.<param>: { value, units, source, audited, note }``.
"""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_MODEL_ROOT = Path(__file__).resolve().parents[3]
_PAPER_LEDGER_PATH = _MODEL_ROOT / "article_aware" / "spec" / "calibration.yaml"
_IMPL_LEDGER_PATH = _MODEL_ROOT / "implementation" / "calibration.yaml"


def _load_one(path: Path) -> dict[str, dict[str, Any]]:
    """Load one namespaced ledger file as {dotted_key: entry}."""
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must be a mapping of namespaced entries")
    return data


@lru_cache(maxsize=1)
def _merged_ledger() -> dict[str, dict[str, Any]]:
    """Merge the paper-derived and implementation-side ledgers.

    A key must not be defined in both ledgers (the two ledgers have
    disjoint ownership; a collision is a contract error).
    """
    paper = _load_one(_PAPER_LEDGER_PATH)
    impl = _load_one(_IMPL_LEDGER_PATH)
    merged: dict[str, dict[str, Any]] = {}
    for src_name, src in (("article_aware/spec", paper), ("implementation", impl)):
        for key, entry in src.items():
            if key == "schema_version":
                continue
            if key in merged:
                raise ValueError(
                    f"calibration key {key!r} defined in both ledgers; "
                    "the two ledgers must have disjoint ownership (§3)"
                )
            merged[key] = entry
    return merged


def resolve(key: str) -> Any:
    """Return the resolved value for one namespaced ledger key.

    Looks across the merged two-ledger view.
    """
    ledger = _merged_ledger()
    if key not in ledger:
        raise KeyError(f"calibration key not in ledger: {key!r}")
    entry = ledger[key]
    if not isinstance(entry, dict) or "value" not in entry:
        raise ValueError(f"malformed ledger entry for {key!r}: {entry!r}")
    return entry["value"]


def resolve_namespace(prefix: str) -> dict[str, Any]:
    """Return {leaf_key: value} for every entry under ``<prefix>.``.

    e.g. ``resolve_namespace("figure_2A")`` -> the resolved per-protocol
    override dict that used to be a literal kwargs dict in protocols.py.
    """
    ledger = _merged_ledger()
    out: dict[str, Any] = {}
    dotted = prefix + "."
    for key, entry in ledger.items():
        if key.startswith(dotted):
            leaf = key[len(dotted):]
            if "." in leaf:
                continue
            out[leaf] = entry["value"]
    return out


@lru_cache(maxsize=1)
def calibration_hash() -> str:
    """Stable hash of the resolved merged ledger values.

    Recorded in every measurement record for calibration traceability
    (ARCHITECTURE.md §3).
    """
    ledger = _merged_ledger()
    resolved = {k: ledger[k].get("value") for k in sorted(ledger)}
    blob = json.dumps(resolved, sort_keys=True, default=str).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()[:16]


def audit_counts() -> dict[str, int]:
    """Count audited:false entries per ledger (for the state report).

    The human audits the *ledger*, not the code (§3). A high unaudited
    count is honest, not a defect — the point is containment.
    """
    paper = _load_one(_PAPER_LEDGER_PATH)
    impl = _load_one(_IMPL_LEDGER_PATH)

    def _count(d: dict[str, dict[str, Any]]) -> tuple[int, int]:
        total = unaud = 0
        for k, e in d.items():
            if k == "schema_version" or not isinstance(e, dict):
                continue
            total += 1
            if not e.get("audited", False):
                unaud += 1
        return total, unaud

    p_total, p_unaud = _count(paper)
    i_total, i_unaud = _count(impl)
    return {
        "paper_derived_total": p_total,
        "paper_derived_unaudited": p_unaud,
        "implementation_total": i_total,
        "implementation_unaudited": i_unaud,
    }


__all__ = [
    "resolve",
    "resolve_namespace",
    "calibration_hash",
    "audit_counts",
]
