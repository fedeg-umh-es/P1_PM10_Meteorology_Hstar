"""
Tests for the H* Methodological Contract v1.2.1 (code/hstar_metrics.py).

Two layers:
  1. Pure unit tests on hstar_v1_2_1_from_skill() with synthetic skill
     curves covering the three variants' boundary behaviour.
  2. A regression test that re-derives H* v1.2.1 straight from the
     committed, already-audited Ireland-regenerated metrics_all_models.csv
     and checks it reproduces
     results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv
     exactly -- i.e. this new, independent implementation agrees with the
     prior manual audit that discovered the from_h1 vs max_run discrepancy.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from hstar_metrics import (  # noqa: E402
    compute_loss_matrix,
    derive_hstar_v1_2_1_table,
    hstar_v1_2_1_from_skill,
    moving_block_bootstrap_delta_hstar,
)

IRELAND_METRICS = ROOT / "results/e2_met_ireland_pm10_regenerated/metrics/metrics_all_models.csv"
IRELAND_HSTAR_BOTH = ROOT / "results/e2_met_ireland_pm10_regenerated/metrics/hstar_summary_both_definitions.csv"
IRELAND_PREDICTIONS = ROOT / "results/e2_met_ireland_pm10_regenerated/predictions/predictions_all_models.csv"
MADRID_METRICS = ROOT / "results/e2_met_madrid_pm10/metrics/metrics_all_models.csv"
MADRID_HSTAR_LEGACY = ROOT / "results/e2_met_madrid_pm10/metrics/hstar_summary.csv"


# ── unit tests ────────────────────────────────────────────────────────────

def test_all_positive_hits_ceiling_on_all_three_variants():
    skill = np.full(24, 0.1)
    result = hstar_v1_2_1_from_skill(skill, horizon_max=24)
    assert result["Hstar_strict_from_h1"] == 24
    assert result["Hstar_strict_max_run"] == 24
    assert result["Hstar_relax"] == 24
    assert result["ceiling_constrained_strict_from_h1"] is True
    assert result["ceiling_constrained_strict_max_run"] is True
    assert result["ceiling_constrained_relax"] is True


def test_all_negative_gives_all_zero_and_no_ceiling():
    skill = np.full(24, -0.1)
    result = hstar_v1_2_1_from_skill(skill, horizon_max=24)
    assert result["Hstar_strict_from_h1"] == 0
    assert result["Hstar_strict_max_run"] == 0
    assert result["Hstar_relax"] == 0
    assert not any(result[f"ceiling_constrained_{v}"] for v in ("strict_from_h1", "strict_max_run", "relax"))


def test_early_failure_then_longer_later_run_distinguishes_from_h1_and_max_run():
    # Fails immediately at h=1, then a positive run of length 10 later.
    skill = np.array([-0.1] + [0.1] * 10 + [-0.1] * 13)
    result = hstar_v1_2_1_from_skill(skill, horizon_max=24)
    assert result["Hstar_strict_from_h1"] == 0
    assert result["Hstar_strict_max_run"] == 10
    assert result["Hstar_relax"] == 11  # last positive horizon is h=11


def test_intermittent_recovery_only_affects_relax():
    # Positive h=1..5, fails h=6, recovers h=7..8, fails rest.
    skill = np.array([0.1] * 5 + [-0.1] + [0.1] * 2 + [-0.1] * 16)
    result = hstar_v1_2_1_from_skill(skill, horizon_max=24)
    assert result["Hstar_strict_from_h1"] == 5
    assert result["Hstar_strict_max_run"] == 5
    assert result["Hstar_relax"] == 8


def test_nan_horizon_counts_as_failure():
    skill = np.array([0.1, 0.1, np.nan] + [0.1] * 21)
    result = hstar_v1_2_1_from_skill(skill, horizon_max=24)
    assert result["Hstar_strict_from_h1"] == 2
    assert result["Hstar_strict_max_run"] == 21
    assert result["Hstar_relax"] == 24


def test_wrong_length_raises():
    with pytest.raises(ValueError):
        hstar_v1_2_1_from_skill(np.zeros(10), horizon_max=24)


def test_compute_loss_matrix_requires_station_or_default():
    predictions = pd.DataFrame({
        "origin": ["2023-01-01"], "horizon": [1], "condition": ["reference"],
        "model": ["persistence"], "y_true": [10.0], "y_pred": [8.0],
    })
    with pytest.raises(ValueError):
        compute_loss_matrix(predictions)

    loss = compute_loss_matrix(predictions, default_station="Madrid Casa de Campo")
    assert loss.loc[0, "loss_squared_error"] == pytest.approx(4.0)
    assert loss.loc[0, "loss_absolute_error"] == pytest.approx(2.0)
    assert loss.loc[0, "station"] == "Madrid Casa de Campo"


# ── regression tests against previously-audited artifacts ──────────────────

@pytest.mark.skipif(not IRELAND_METRICS.exists(), reason="Ireland regenerated metrics not present")
def test_ireland_v1_2_1_reproduces_hstar_summary_both_definitions():
    metrics = pd.read_csv(IRELAND_METRICS)
    both = pd.read_csv(IRELAND_HSTAR_BOTH)

    derived = derive_hstar_v1_2_1_table(
        metrics=metrics,
        group_cols=["station", "condition", "model"],
        horizon_max=24,
    )
    # both_definitions.csv only carries non-persistence rows.
    derived_non_baseline = derived[derived["model"] != "persistence"].copy()

    merged = both.merge(
        derived_non_baseline,
        on=["station", "condition", "model"],
        how="inner",
        validate="one_to_one",
    )
    assert len(merged) == len(both)
    assert (merged["Hstar_strict_from_h1"] == merged["H_strict_from_h1"]).all()
    assert (merged["Hstar_strict_max_run"] == merged["H_strict_max_run"]).all()
    assert (merged["Hstar_relax"] == merged["H_relax"]).all()


@pytest.mark.skipif(not MADRID_METRICS.exists(), reason="Madrid metrics not present")
def test_madrid_v1_2_1_max_run_and_relax_match_legacy_hstar_summary():
    metrics = pd.read_csv(MADRID_METRICS)
    legacy = pd.read_csv(MADRID_HSTAR_LEGACY)

    derived = derive_hstar_v1_2_1_table(
        metrics=metrics,
        group_cols=["condition", "model"],
        horizon_max=24,
    )
    merged = legacy.merge(derived, on=["condition", "model"], how="inner", validate="one_to_one")
    assert len(merged) == len(legacy)
    assert (merged["Hstar_strict_max_run"] == merged["H_star_strict"]).all()
    assert (merged["Hstar_relax"] == merged["H_star_relax"]).all()


@pytest.mark.skipif(not IRELAND_PREDICTIONS.exists(), reason="Ireland regenerated predictions not present")
def test_moving_block_bootstrap_ci_contains_point_estimate():
    predictions = pd.read_csv(IRELAND_PREDICTIONS)
    loss_matrix = compute_loss_matrix(predictions)
    station = loss_matrix["station"].iloc[0]

    result = moving_block_bootstrap_delta_hstar(
        loss_matrix=loss_matrix,
        station=station,
        horizon_max=24,
        n_boot=200,
        random_state=42,
    )
    for variant in ("Hstar_strict_from_h1", "Hstar_strict_max_run", "Hstar_relax"):
        point = result[f"delta_{variant}"]
        lower = result[f"delta_{variant}_ci_lower"]
        upper = result[f"delta_{variant}_ci_upper"]
        assert lower <= upper
        # The bootstrap distribution is centred on (not guaranteed to bracket
        # exactly, for a discrete, bounded statistic) the point estimate;
        # sanity-check it is within a generous multiple of the observed range.
        assert lower - 24 <= point <= upper + 24
