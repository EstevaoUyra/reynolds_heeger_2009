"""Modification smoke test — ARCHITECTURE.md §5(4).

The operational definition of "a scientist can change it": swap ONE
stage (the normalization stage) for a trivial variant *via config only*
and have the pipeline, measurement record, and figure regenerate with
ZERO edits to unrelated code (protocols, measurements, views, other
stages). If this needed any code change, the decomposition is wrong —
fix the contracts, not the test (§5).

The swap mechanism is pure config: the ``model.normalization_variant``
ledger key, or the ``RH_NORMALIZATION_VARIANT`` environment variable. The
SAME unchanged ``protocols`` / ``views`` code path is exercised; nothing
is keyed on the variant outside the normalization stage.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pytest

from rh_model import protocols, views
from rh_model.measurements import SCHEMA_VERSION
from rh_model.stages import normalization


@pytest.fixture()
def restore_env():
    """Restore RH_NORMALIZATION_VARIANT after the test (config isolation)."""
    prev = os.environ.get("RH_NORMALIZATION_VARIANT")
    yield
    if prev is None:
        os.environ.pop("RH_NORMALIZATION_VARIANT", None)
    else:
        os.environ["RH_NORMALIZATION_VARIANT"] = prev


@pytest.mark.parametrize("variant", normalization.VARIANTS)
def test_variant_swap_is_config_only(restore_env, variant):
    """Each normalization variant runs the UNCHANGED protocol pipeline,
    selected purely by config, and yields a valid measurement record.

    Zero code edits, no per-variant branch outside the normalization
    stage. This is the §5(4) proof.
    """
    os.environ["RH_NORMALIZATION_VARIANT"] = variant

    rec = protocols.run_figure_2A(n_contrasts=12)

    # Schema-versioned record comes back regardless of the swapped stage.
    assert rec["schema_version"] == SCHEMA_VERSION
    assert "resolved_ledger_hash" in rec
    for key in ("attended_CRF", "unattended_CRF", "percent_modulation", "c"):
        arr = np.asarray(rec[key], dtype=float)
        assert arr.ndim == 1 and arr.size == 12
        assert np.all(np.isfinite(arr))
    # Both CRFs are still non-negative responses for either variant.
    assert np.all(np.asarray(rec["attended_CRF"], float) >= -1e-9)
    assert np.all(np.asarray(rec["unattended_CRF"], float) >= -1e-9)


def test_default_variant_is_behavior_preserving(restore_env):
    """With no config override the default 'divisive' variant is the
    paper Eq. 5 path (the migration must not change model outputs)."""
    os.environ.pop("RH_NORMALIZATION_VARIANT", None)
    rec_default = protocols.run_figure_2A(n_contrasts=12)
    os.environ["RH_NORMALIZATION_VARIANT"] = "divisive"
    rec_explicit = protocols.run_figure_2A(n_contrasts=12)
    np.testing.assert_array_equal(
        np.asarray(rec_default["attended_CRF"], float),
        np.asarray(rec_explicit["attended_CRF"], float),
    )


def test_trivial_variant_changes_the_pipeline_output(restore_env):
    """The trivial swap variant ('identity_suppression', S→0) actually
    changes the pipeline output — proving the swap is real, not a no-op,
    while still going through the same unchanged protocol/view code."""
    os.environ["RH_NORMALIZATION_VARIANT"] = "divisive"
    base = np.asarray(protocols.run_figure_2A(n_contrasts=12)["attended_CRF"], float)
    os.environ["RH_NORMALIZATION_VARIANT"] = "identity_suppression"
    swapped = np.asarray(
        protocols.run_figure_2A(n_contrasts=12)["attended_CRF"], float
    )
    assert not np.allclose(base, swapped)


def test_figure_regenerates_under_config_swap(restore_env, tmp_path):
    """The figure regenerates from the SAME unchanged view code under the
    config-only stage swap — pipeline + record + figure, zero edits."""
    os.environ["RH_NORMALIZATION_VARIANT"] = "identity_suppression"
    out = views.save_figure_2(tmp_path)
    out = Path(out)
    assert out.exists() and out.stat().st_size > 0
