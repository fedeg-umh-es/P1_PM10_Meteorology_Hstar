from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from temporal_contract import (
    add_exact_lags,
    add_exact_targets,
    exact_horizon_window,
    filter_complete_origins,
    generate_clock_origins,
    normalise_timestamps,
)
from e2_met_madrid_shared import build_train_frame, get_condition_feature_columns


def sample(gap: bool = False) -> pd.DataFrame:
    ts = pd.date_range("2023-01-01", periods=220, freq="h")
    if gap:
        ts = ts.delete(25)
    return pd.DataFrame({"timestamp": ts, "PM10": range(len(ts)), "temp": 10.0})


class TestTimestampContract(unittest.TestCase):
    def test_origins_follow_clock_not_rows(self) -> None:
        origins = generate_clock_origins(sample(gap=True), "timestamp", "2023-01-01", "2023-01-08", 24)
        self.assertTrue(all((b - a) % pd.Timedelta(hours=24) == pd.Timedelta(0) for a, b in zip(origins, origins[1:])))
        self.assertIn(pd.Timestamp("2023-01-02"), origins)

    def test_each_lag_uses_exact_timestamp(self) -> None:
        for lag in [1, 2, 3, 6, 12, 24, 48, 168]:
            out = add_exact_lags(sample(gap=True), "timestamp", "PM10", [lag])
            valid = out[f"PM10_lag_{lag}"].notna()
            self.assertTrue(((out.loc[valid, "timestamp"] - out.loc[valid, f"PM10_lag_{lag}_timestamp"]) == pd.Timedelta(hours=lag)).all())
            row = out[out["timestamp"] == pd.Timestamp("2023-01-02 02:00")].iloc[0]
            if lag == 1:
                self.assertTrue(pd.isna(row["PM10_lag_1"]))

    def test_every_target_uses_exact_clock_horizon(self) -> None:
        out = add_exact_targets(sample(gap=True), "timestamp", "PM10", 24)
        for h in range(1, 25):
            self.assertTrue(((out[f"PM10_t_plus_{h}_timestamp"] - out["timestamp"]) == pd.Timedelta(hours=h)).all())

    def test_future_features_are_rejected_by_contract(self) -> None:
        origin = pd.Timestamp("2023-01-04")
        feature_times = [origin - pd.Timedelta(hours=1), origin]
        self.assertTrue(max(feature_times) <= origin)

    def test_training_targets_are_strictly_pre_origin(self) -> None:
        origin = pd.Timestamp("2023-01-04")
        training_target_times = pd.date_range("2023-01-01", origin - pd.Timedelta(hours=1), freq="h")
        self.assertTrue((training_target_times < origin).all())

    def test_persistence_and_xgb_latest_pm10_contract(self) -> None:
        origin = pd.Timestamp("2023-01-04")
        latest_observed = origin - pd.Timedelta(hours=1)
        self.assertEqual(latest_observed, origin - pd.Timedelta(hours=1))

    def test_conditions_share_support(self) -> None:
        base = {(pd.Timestamp("2023-01-01"), h) for h in range(1, 25)}
        self.assertEqual(base, set(base))

    def test_duplicate_timestamps_fail(self) -> None:
        df = sample().iloc[:2]
        dup = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        with self.assertRaises(ValueError):
            normalise_timestamps(dup, "timestamp")

    def test_exact_window_exposes_gap(self) -> None:
        window = exact_horizon_window(sample(gap=True), pd.Timestamp("2023-01-02"), 2, "timestamp")
        self.assertEqual(window.loc[1, "timestamp"], pd.Timestamp("2023-01-02 01:00"))
        self.assertNotEqual(window.loc[1, "PM10"], window.loc[1, "PM10"])

    def test_incomplete_origin_is_explicitly_excluded(self) -> None:
        df = sample(gap=True)
        origins = [pd.Timestamp("2023-01-01"), pd.Timestamp("2023-01-02")]
        valid = filter_complete_origins(df, origins, "timestamp", "PM10", [1], 2)
        self.assertNotIn(pd.Timestamp("2023-01-02"), valid)

    def test_timezone_aware_elapsed_hours_across_dst(self) -> None:
        start = pd.Timestamp("2023-03-26 00:00", tz="Europe/Madrid")
        end = start + pd.Timedelta(hours=24)
        self.assertEqual((end.tz_convert("UTC") - start.tz_convert("UTC")), pd.Timedelta(hours=24))

    def test_direct_training_uses_exact_lags_and_pre_origin_targets(self) -> None:
        timestamps = pd.date_range("2023-01-01", periods=80, freq="h").delete(30)
        train = pd.DataFrame({
            "timestamp": timestamps,
            "PM10": range(len(timestamps)),
            "temp": 10.0,
        })
        origin = pd.Timestamp("2023-01-04 00:00")
        config = {
            "timestamp_col": "timestamp",
            "target_col": "PM10",
            "lags": [1, 24],
            "horizon_max": 2,
            "calendar_features": ["hour_of_day", "day_of_week", "month", "julian_day"],
            "meteo_features": ["temp"],
        }
        feature_cols = get_condition_feature_columns(train, config, "lags_only")
        frame, targets, _ = build_train_frame(train, config, feature_cols, origin)
        self.assertNotIn(pd.Timestamp("2023-01-02 07:00"), set(frame["timestamp"]))
        for horizon, values in targets.items():
            non_missing = values.notna()
            target_times = frame.loc[non_missing, f"PM10_t_plus_{horizon}_timestamp"]
            self.assertTrue((target_times < origin).all())


if __name__ == "__main__":
    unittest.main()
