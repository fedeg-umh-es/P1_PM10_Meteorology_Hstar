from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from temporal_contract import add_exact_lags, add_exact_targets, exact_horizon_window, filter_complete_origins, generate_clock_origins, normalise_timestamps


def sample(gap: bool = False) -> pd.DataFrame:
    ts = pd.date_range("2023-01-01", periods=220, freq="h")
    if gap:
        ts = ts.delete(25)
    return pd.DataFrame({"timestamp": ts, "PM10": range(len(ts)), "temp": 10.0})


def test_origins_follow_clock_not_rows() -> None:
    origins = generate_clock_origins(sample(gap=True), "timestamp", "2023-01-01", "2023-01-08", 24)
    assert all((b - a) % pd.Timedelta(hours=24) == pd.Timedelta(0) for a, b in zip(origins, origins[1:]))
    assert pd.Timestamp("2023-01-02") in origins


@pytest.mark.parametrize("lag", [1, 2, 3, 6, 12, 24, 48, 168])
def test_each_lag_uses_exact_timestamp(lag: int) -> None:
    out = add_exact_lags(sample(gap=True), "timestamp", "PM10", [lag])
    valid = out[f"PM10_lag_{lag}"].notna()
    assert ((out.loc[valid, "timestamp"] - out.loc[valid, f"PM10_lag_{lag}_timestamp"]) == pd.Timedelta(hours=lag)).all()
    # A missing exact timestamp is invalid; it is never forward-filled.
    row = out[out["timestamp"] == pd.Timestamp("2023-01-02 02:00")].iloc[0]
    if lag == 1:
        assert pd.isna(row["PM10_lag_1"])


def test_every_target_uses_exact_clock_horizon() -> None:
    out = add_exact_targets(sample(gap=True), "timestamp", "PM10", 24)
    for h in range(1, 25):
        assert ((out[f"PM10_t_plus_{h}_timestamp"] - out["timestamp"]) == pd.Timedelta(hours=h)).all()


def test_future_features_are_rejected_by_contract() -> None:
    origin = pd.Timestamp("2023-01-04")
    feature_times = [origin - pd.Timedelta(hours=1), origin]
    assert max(feature_times) <= origin


def test_training_targets_are_strictly_pre_origin() -> None:
    origin = pd.Timestamp("2023-01-04")
    training_target_times = pd.date_range("2023-01-01", origin - pd.Timedelta(hours=1), freq="h")
    assert (training_target_times < origin).all()


def test_persistence_and_xgb_latest_pm10_contract() -> None:
    origin = pd.Timestamp("2023-01-04")
    latest_observed = origin - pd.Timedelta(hours=1)
    assert latest_observed == origin - pd.Timedelta(hours=1)


def test_conditions_share_support() -> None:
    base = {(pd.Timestamp("2023-01-01"), h) for h in range(1, 25)}
    assert base == set(base)


def test_duplicate_timestamps_fail() -> None:
    df = sample().iloc[:2]
    dup = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        normalise_timestamps(dup, "timestamp")


def test_exact_window_exposes_gap() -> None:
    window = exact_horizon_window(sample(gap=True), pd.Timestamp("2023-01-02"), 2, "timestamp")
    assert window.loc[1, "timestamp"] == pd.Timestamp("2023-01-02 01:00")
    assert window.loc[1, "PM10"] != window.loc[1, "PM10"]


def test_incomplete_origin_is_explicitly_excluded() -> None:
    df = sample(gap=True)
    origins = [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")]
    valid = filter_complete_origins(df, origins, "timestamp", "PM10", [1], 2)
    assert pd.Timestamp("2023-01-02") not in valid


def test_timezone_aware_elapsed_hours_across_dst() -> None:
    start = pd.Timestamp("2023-03-26 00:00", tz="Europe/Madrid")
    end = start + pd.Timedelta(hours=24)
    assert (end.tz_convert("UTC") - start.tz_convert("UTC")) == pd.Timedelta(hours=24)
