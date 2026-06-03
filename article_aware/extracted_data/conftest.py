"""Pytest setup for article-aware figure claim tests.

Adds the three-tier figure-test gating (WORKFLOW.md §3b):

  - ``qualitative`` + ``hard`` tests GATE the build (a fail is a real fail).
  - ``soft`` tests are MEASURED and REPORTED but NEVER block: a failing soft
    test is reported as an ``xfail`` (outcome "xfailed"), so the suite stays
    green while the soft fail is still visible per-test. A human promotes a
    soft test to hard with a one-line tier flip in the test source.

This is what lets an imperfect digitization give real quantitative power
without spurious build failures.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


EXTRACTED_DATA_ROOT = Path(__file__).resolve().parent
MODEL_ROOT = EXTRACTED_DATA_ROOT.parents[1]
REPO_ROOT = EXTRACTED_DATA_ROOT.parents[3]
IMPLEMENTATION_SRC = MODEL_ROOT / "implementation" / "src"

for path in (REPO_ROOT, IMPLEMENTATION_SRC, EXTRACTED_DATA_ROOT):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers", "tier(name): figure-test tier — qualitative|hard|soft (WORKFLOW §3b)"
    )
    config.addinivalue_line(
        "markers", "soft: a soft (non-blocking) figure test — reported, never gates"
    )


def pytest_collection_modifyitems(config: pytest.Config, items) -> None:
    """Make soft tests non-blocking by attaching a non-strict xfail.

    A soft test that PASSES shows as ``xpassed`` (still green, non-strict); a
    soft test that FAILS shows as ``xfailed`` — recorded and visible, but it
    does not fail the suite. qualitative/hard tests are untouched and gate.
    """
    for item in items:
        if item.get_closest_marker("soft") is not None:
            item.add_marker(
                pytest.mark.xfail(
                    reason="soft tier — measured & reported, never blocks (WORKFLOW §3b)",
                    strict=False,
                )
            )
