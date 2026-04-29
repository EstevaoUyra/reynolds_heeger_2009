"""Pytest setup for article-aware figure claim tests."""

from __future__ import annotations

import sys
from pathlib import Path


EXTRACTED_DATA_ROOT = Path(__file__).resolve().parent
MODEL_ROOT = EXTRACTED_DATA_ROOT.parents[1]
REPO_ROOT = EXTRACTED_DATA_ROOT.parents[3]
IMPLEMENTATION_SRC = MODEL_ROOT / "implementation" / "src"

for path in (REPO_ROOT, IMPLEMENTATION_SRC, EXTRACTED_DATA_ROOT):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)
