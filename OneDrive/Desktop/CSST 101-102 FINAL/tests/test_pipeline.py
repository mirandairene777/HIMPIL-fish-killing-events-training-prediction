"""Contract tests for the HIMPIL research pipeline.

Run after the Python/R/dashboard build:
    .venv\\Scripts\\python.exe -m unittest discover -s tests -v

These tests verify that generated outputs preserve the documented evidence
limits. They verify that the one real fit is a descriptive annual trend model,
not a fish-kill model. They also verify that the separate synthetic base
dataset, synthetic base model, and generic prototype remain quarantined,
labeled, and separate from the evidence dashboard.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "data" / "outputs"
TABLES = ROOT / "reports" / "tables"
SYNTHETIC_BASE = ROOT / "data" / "synthetic" / "base"
SYNTHETIC_BASE_MODEL = ROOT / "data" / "synthetic" / "base_model"
SYNTHETIC_BASE_MODEL_DIR = ROOT / "models" / "synthetic" / "base_model"
SYNTHETIC_GAP_FILL = ROOT / "data" / "synthetic" / "gap_fill"
SYNTHETIC_GAP_FILL_MODEL_DIR = ROOT / "models" / "synthetic" / "gap_filled"
DASHBOARD_JSON = ROOT / "dashboard" / "src" / "data" / "dashboard.json"
SYNTHETIC_DEMO_JSON = ROOT / "dashboard" / "src" / "data" / "syntheticDemo.json"

EVENT_COLUMNS = [
    "event_id",
    "event_start_date",
    "event_end_date",
    "location",
    "municipality",
    "lake_zone",
    "fish_species",
    "estimated_fish_losses",
    "estimated_economic_loss",
    "reported_cause",
    "source_title",
    "source_url",
    "publication_date",
    "date_precision",
    "location_precision",
    "verification_status",
    "notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def read_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return next(csv.reader(handle))


class PipelineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        required = [
            PROCESSED / "historical_fish_kill_events.csv",
            PROCESSED / "water_quality_long.csv",
            PROCESSED / "modeling_dataset.csv",
            PROCESSED / "labeling_summary.csv",
            OUTPUTS / "training_status.csv",
            OUTPUTS / "evaluation_status.csv",
            TABLES / "source_inventory.csv",
            DASHBOARD_JSON,
            ROOT / "data" / "synthetic" / "synthetic_manifest.json",
            TABLES / "synthetic_prototype_report.md",
            TABLES / "synthetic_model_card.md",
            ROOT / "models" / "synthetic" / "random_forest_24h.joblib",
            SYNTHETIC_BASE / "stations.csv",
            SYNTHETIC_BASE / "calibration_anchors.csv",
            SYNTHETIC_BASE / "water_quality_daily.csv",
            SYNTHETIC_BASE / "weather_daily.csv",
            SYNTHETIC_BASE / "himpil_synthetic_base.sqlite",
            SYNTHETIC_BASE / "data_dictionary.md",
            SYNTHETIC_BASE / "manifest.json",
            SYNTHETIC_BASE / "README.md",
            TABLES / "synthetic_base_report.md",
            TABLES / "synthetic_base_calibration.csv",
            TABLES / "synthetic_base_coverage.csv",
            SYNTHETIC_BASE_MODEL / "synthetic_events.csv",
            SYNTHETIC_BASE_MODEL / "synthetic_modeling_dataset.csv",
            SYNTHETIC_BASE_MODEL / "synthetic_test_predictions.csv",
            SYNTHETIC_BASE_MODEL / "manifest.json",
            SYNTHETIC_BASE_MODEL / "README.md",
            SYNTHETIC_BASE_MODEL_DIR / "random_forest_24h.joblib",
            SYNTHETIC_GAP_FILL / "himpil_synthetic_complete.sqlite",
            SYNTHETIC_GAP_FILL / "manifest.json",
            SYNTHETIC_GAP_FILL / "stations.csv",
            SYNTHETIC_GAP_FILL / "incident_reports.csv",
            SYNTHETIC_GAP_FILL / "corroboration.csv",
            SYNTHETIC_GAP_FILL / "negative_windows.csv",
            SYNTHETIC_GAP_FILL / "aggregation_rules.csv",
            SYNTHETIC_GAP_FILL / "readiness_checks.csv",
            SYNTHETIC_GAP_FILL / "pre_event_observations.csv",
            SYNTHETIC_GAP_FILL_MODEL_DIR / "random_forest_24h.joblib",
            SYNTHETIC_GAP_FILL_MODEL_DIR / "random_forest_48h.joblib",
            SYNTHETIC_GAP_FILL_MODEL_DIR / "random_forest_72h.joblib",
            SYNTHETIC_GAP_FILL_MODEL_DIR / "manifest.json",
            SYNTHETIC_DEMO_JSON,
            TABLES / "synthetic_gap_fill_database_report.md",
            TABLES / "synthetic_gap_filled_model_report.md",
            TABLES / "synthetic_gap_filled_model_card.md",
            TABLES / "synthetic_gap_filled_model_metrics.csv",
            TABLES / "synthetic_gap_filled_test_predictions.csv",
            TABLES / "synthetic_gap_filled_validation_predictions.csv",
            TABLES / "synthetic_gap_filled_event_detection.csv",
            TABLES / "synthetic_gap_filled_feature_importance.csv",
            TABLES / "synthetic_base_model_report.md",
            TABLES / "synthetic_base_model_card.md",
            TABLES / "synthetic_base_model_metrics.csv",
            TABLES / "synthetic_base_model_predictions.csv",
            TABLES / "synthetic_base_model_feature_importance.csv",
            TABLES / "synthetic_base_event_detection.csv",
            TABLES / "synthetic_base_model_diagnostics.csv",
            TABLES / "real_trend_model.json",
            TABLES / "real_trend_model_metrics.csv",
            TABLES / "real_trend_model_card.md",
            TABLES / "real_data_alignment_report.md",
            TABLES / "system_gaps_and_todo.md",
        ]
        missing = [str(path) for path in required if not path.exists()]
        if missing:
            raise unittest.SkipTest(
                "Run the Python/R/dashboard build first. Missing: " + ", ".join(missing)
            )

    def test_source_copies_are_byte_identical(self) -> None:
        original = sorted((ROOT / "datasets").glob("*.xlsx"))
        copied = sorted((ROOT / "data" / "raw").glob("*.xlsx"))
        self.assertEqual(len(original), 8)
        self.assertEqual([path.name for path in original], [path.name for path in copied])
        for left, right in zip(original, copied):
            left_hash = hashlib.sha256(left.read_bytes()).hexdigest()
            right_hash = hashlib.sha256(right.read_bytes()).hexdigest()
            self.assertEqual(left_hash, right_hash, left.name)

    def test_event_csv_has_exact_supported_columns(self) -> None:
        path = PROCESSED / "historical_fish_kill_events.csv"
        self.assertEqual(read_header(path), EVENT_COLUMNS)
        rows = read_rows(path)
        self.assertEqual(len(rows), 1)
        event = rows[0]
        self.assertEqual(event["event_start_date"], "2019-05-04")
        self.assertEqual(event["event_end_date"], "2019-05-31")
        self.assertIn("Biñan", event["location"])
        self.assertEqual(event["lake_zone"], "")
        self.assertEqual(event["estimated_economic_loss"], "")
        self.assertIn("approximate", event["date_precision"].lower())
        self.assertIn("not a formal", event["verification_status"].lower())
        self.assertTrue(event["source_url"].startswith("https://upd.edu.ph/"))

    def test_aggregate_claims_were_not_converted_to_events(self) -> None:
        audit = read_rows(PROCESSED / "incident_evidence_audit.csv")
        decisions = {row["candidate_id"]: row["decision"] for row in audit}
        self.assertEqual(decisions["CAND-01"], "excluded")
        self.assertEqual(decisions["CAND-02"], "excluded")
        self.assertEqual(decisions["CAND-03"], "excluded_pending_verification")
        self.assertEqual(decisions["CAND-04"], "accepted_as_reported_event")
        self.assertEqual(len(read_rows(PROCESSED / "historical_fish_kill_events.csv")), 1)

    def test_missing_measurements_remain_missing(self) -> None:
        rows = read_rows(PROCESSED / "water_quality_long.csv")
        self.assertEqual(len(rows), 3400)
        temperature_2017 = [
            row
            for row in rows
            if row["station_name"] == "Stn I - West Bay"
            and row["year"] == "2017"
            and row["variable"] == "Water temperature"
        ]
        self.assertEqual(len(temperature_2017), 1)
        self.assertEqual(temperature_2017[0]["value"], "")
        self.assertNotEqual(temperature_2017[0]["quality_flag"], "ok")
        self.assertGreater(sum(row["value"] == "" for row in rows), 0)

    def test_2025_weather_is_provisional_and_incomplete(self) -> None:
        for filename in ("rainfall_monthly.csv", "wind_monthly.csv"):
            rows = [row for row in read_rows(PROCESSED / filename) if row["year"] == "2025"]
            self.assertGreater(len(rows), 0)
            self.assertTrue(all(row["provisional_2025"] == "yes" for row in rows))

            months_by_station: dict[str, set[int]] = {}
            for row in rows:
                if row["value"] != "":
                    months_by_station.setdefault(row["station_name"], set()).add(
                        int(row["month_number"])
                    )
            complete = [months for months in months_by_station.values() if len(months) == 12]
            january_to_june = [
                months for months in months_by_station.values() if months == set(range(1, 7))
            ]
            self.assertEqual(len(complete), 7, filename)
            self.assertGreater(len(january_to_june), 0, filename)
            self.assertTrue(
                all(months <= set(range(1, 13)) for months in months_by_station.values())
            )

    def test_no_post_event_value_is_used_as_predictor(self) -> None:
        matches = read_rows(PROCESSED / "incident_environmental_matches.csv")
        self.assertGreater(len(matches), 0)
        self.assertTrue(all(row["usable_as_pre_event_predictor"] == "no" for row in matches))
        context = read_rows(PROCESSED / "incident_context_measurements.csv")
        self.assertGreater(len(context), 0)
        self.assertTrue(all(row["temporal_relation_to_event"] == "during_event" for row in context))

    def test_24_hour_labels_are_not_generated(self) -> None:
        summary = {row["metric"]: row["value"] for row in read_rows(PROCESSED / "labeling_summary.csv")}
        self.assertEqual(summary["label_generation_status"], "blocked")
        self.assertEqual(summary["usable_24h_positive_labels"], "0")
        self.assertEqual(summary["usable_24h_negative_labels"], "0")
        self.assertEqual(summary["independent_event_periods"], "1")
        modeling = read_rows(PROCESSED / "modeling_dataset.csv")
        self.assertEqual(len(modeling), 0)
        header = read_header(PROCESSED / "modeling_dataset.csv")
        self.assertIn("fish_kill_within_24h", header)
        self.assertIn("event_group", header)

    def test_training_and_evaluation_guards_refuse(self) -> None:
        training = read_rows(OUTPUTS / "training_status.csv")
        self.assertEqual(len(training), 10)
        self.assertEqual(sum(row["status"] == "fail" for row in training), 8)
        t1 = next(row for row in training if row["check"] == "T1")
        self.assertEqual(t1["evidence"], "data/processed/modeling_dataset.csv")
        evaluation = read_rows(OUTPUTS / "evaluation_status.csv")
        self.assertTrue(all(row["status"] == "fail" for row in evaluation))
        self.assertFalse((ROOT / "models" / "model.joblib").exists())
        self.assertFalse((OUTPUTS / "test_predictions.csv").exists())

    def test_synthetic_prototype_is_quarantined(self) -> None:
        synthetic_dir = ROOT / "data" / "synthetic"
        panel = read_rows(synthetic_dir / "synthetic_station_day.csv")
        self.assertGreater(len(panel), 0)
        self.assertTrue(
            all(row["data_origin"] == "synthetic_simulation" for row in panel)
        )

        events = read_rows(synthetic_dir / "synthetic_event_periods.csv")
        self.assertTrue(
            all(row["data_origin"] == "synthetic_simulation" for row in events)
        )
        self.assertTrue(
            any(row["period_type"] == "synthetic_event" for row in events)
        )
        self.assertTrue(
            any(
                row["period_type"] == "synthetic_stress_without_event"
                for row in events
            )
        )

        manifest = json.loads(
            (synthetic_dir / "synthetic_manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["status"], "synthetic_prototype_only")
        self.assertEqual(manifest["warning"], "SIMULATION ONLY - NOT EVIDENCE")
        self.assertEqual(manifest["data_origin"], "synthetic_simulation")
        self.assertTrue(manifest["quarantine"]["does_not_satisfy_model_gate"])
        self.assertTrue(manifest["quarantine"]["not_connected_to_dashboard"])

        report = (TABLES / "synthetic_prototype_report.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("SIMULATION ONLY", report)
        self.assertIn("NOT EVIDENCE", report)
        self.assertIn("does **not** pass the Section 6 gate", report)
        self.assertIn("risk assessment unavailable", report)

        model_card = (TABLES / "synthetic_model_card.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("SIMULATION ONLY", model_card)
        self.assertIn(
            "not a model card for a real Laguna de Bay risk model", model_card
        )
        self.assertIn("Prohibited uses", model_card)

        dashboard_text = DASHBOARD_JSON.read_text(encoding="utf-8")
        self.assertNotIn("SYN-LAG", dashboard_text)
        self.assertNotIn("synthetic_prototype", dashboard_text)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for phrase in (
            "five separate tracks",
            "Synthetic base model",
            "Synthetic gap-filled database and model",
            "How to tell real from synthetic",
            "Synthetic gap-fill",
            "risk assessment unavailable",
            "## 11. The real model-readiness gate",
        ):
            self.assertIn(phrase, readme)

        # The real schema and model path must remain untouched.
        self.assertEqual(len(read_rows(PROCESSED / "modeling_dataset.csv")), 0)
        self.assertFalse((ROOT / "models" / "model.joblib").exists())
        self.assertTrue(
            (ROOT / "models" / "synthetic" / "random_forest_24h.joblib").exists()
        )

    def test_synthetic_base_is_quarantined_and_calibrated(self) -> None:
        manifest = json.loads(
            (SYNTHETIC_BASE / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["status"], "synthetic_base_only")
        self.assertEqual(manifest["warning"], "SIMULATION ONLY - NOT EVIDENCE")
        self.assertEqual(manifest["data_origin"], "synthetic_base_v1")
        self.assertTrue(manifest["quarantine"]["not_evidence"])
        self.assertTrue(manifest["quarantine"]["does_not_satisfy_model_gate"])
        self.assertTrue(manifest["quarantine"]["not_connected_to_dashboard"])
        self.assertFalse(manifest["quarantine"]["contains_fish_kill_labels"])
        self.assertTrue(manifest["quarantine"]["contains_real_station_labels"])
        self.assertTrue(manifest["quarantine"]["contains_real_annual_anchors"])
        self.assertFalse(manifest["quarantine"]["contains_real_daily_measurements"])
        self.assertFalse(manifest["quarantine"]["contains_station_coordinates"])

        stations = read_rows(SYNTHETIC_BASE / "stations.csv")
        registry_lake = [
            row
            for row in read_rows(PROCESSED / "station_registry.csv")
            if row["station_type"] == "lake"
        ]
        self.assertEqual(len(stations), 15)
        self.assertEqual(
            {row["station_name"] for row in stations},
            {row["station_name"] for row in registry_lake},
        )
        self.assertTrue(all(row["coordinates_available"] == "no" for row in stations))
        self.assertTrue(all(row["values_synthetic"] == "yes" for row in stations))

        daily = read_rows(SYNTHETIC_BASE / "water_quality_daily.csv")
        self.assertEqual(len(daily), 54795)
        self.assertEqual(len({row["station_id"] for row in daily}), 15)
        self.assertEqual({row["year"] for row in daily}, {str(year) for year in range(2016, 2026)})
        self.assertEqual(min(row["date"] for row in daily), "2016-01-01")
        self.assertEqual(max(row["date"] for row in daily), "2025-12-31")
        self.assertTrue(all(row["data_origin"] == "synthetic_base_v1" for row in daily))
        self.assertTrue(all(row["quality_flag"] == "synthetic_ok" for row in daily))
        self.assertEqual(
            sum(row["reported_lake_zone"] == "" for row in daily),
            10 * 3653,
            "Ten stations without a supplied zone label should remain blank.",
        )
        for column in (
            "nitrate_mg_l",
            "phosphate_mg_l",
            "bod_mg_l",
            "ph",
            "water_temp_c",
            "do_mg_l",
        ):
            self.assertIn(column, daily[0])
            self.assertTrue(all(float(row[column]) > 0 for row in daily), column)

        header = read_header(SYNTHETIC_BASE / "water_quality_daily.csv")
        self.assertNotIn("fish_kill", " ".join(header).lower())
        self.assertNotIn("risk", " ".join(header).lower())

        anchors = read_rows(SYNTHETIC_BASE / "calibration_anchors.csv")
        self.assertEqual(len(anchors), 900)
        statuses = {}
        for row in anchors:
            statuses[row["anchor_status"]] = statuses.get(row["anchor_status"], 0) + 1
        self.assertEqual(statuses["real_annual_summary"], 621)
        self.assertEqual(statuses["real_annual_summary_2025_completeness_unverified"], 90)
        self.assertEqual(statuses["synthetic_station_mean_imputed"], 189)

        calibration = read_rows(TABLES / "synthetic_base_calibration.csv")
        self.assertEqual(len(calibration), 900)
        max_error = max(float(row["absolute_error"]) for row in calibration)
        self.assertLess(max_error, 0.01)
        self.assertLessEqual(len(read_rows(TABLES / "synthetic_base_coverage.csv")), 60)

        weather = read_rows(SYNTHETIC_BASE / "weather_daily.csv")
        self.assertEqual(len(weather), 10959)
        self.assertEqual(len({row["weather_zone_id"] for row in weather}), 3)
        self.assertTrue(all(row["data_origin"] == "synthetic_base_v1" for row in weather))
        self.assertTrue(any(row["provisional_2025"] == "synthetic_fill" for row in weather))

        with sqlite3.connect(SYNTHETIC_BASE / "himpil_synthetic_base.sqlite") as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            self.assertTrue(
                {"stations", "calibration_anchors", "water_quality_daily", "weather_daily", "metadata"}
                <= tables
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM water_quality_daily").fetchone()[0],
                54795,
            )
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM water_quality_daily_long").fetchone()[0],
                328770,
            )
            metadata = dict(connection.execute("SELECT key, value FROM metadata"))
            self.assertEqual(metadata["warning"], "SIMULATION ONLY - NOT EVIDENCE")
            self.assertEqual(metadata["status"], "synthetic_base_only")
        connection.close()

        data_dictionary = (SYNTHETIC_BASE / "data_dictionary.md").read_text(encoding="utf-8")
        self.assertIn("SIMULATION ONLY", data_dictionary)
        self.assertIn("NOT EVIDENCE", data_dictionary)
        self.assertIn("No fish-kill labels", data_dictionary)

        base_readme = (SYNTHETIC_BASE / "README.md").read_text(encoding="utf-8")
        self.assertIn("SIMULATION ONLY", base_readme)
        self.assertIn("NOT EVIDENCE", base_readme)
        self.assertIn("risk assessment unavailable", base_readme)

        report = (TABLES / "synthetic_base_report.md").read_text(encoding="utf-8")
        self.assertIn("SIMULATION ONLY", report)
        self.assertIn("NOT EVIDENCE", report)
        self.assertIn("does **not** pass the Section 6 gate", report)
        self.assertIn("risk assessment unavailable", report)

        dashboard_text = DASHBOARD_JSON.read_text(encoding="utf-8")
        self.assertNotIn("LAG-LAKE-", dashboard_text)
        self.assertNotIn("synthetic_base_v1", dashboard_text)
        self.assertFalse((ROOT / "models" / "model.joblib").exists())

    def test_synthetic_base_model_is_quarantined(self) -> None:
        manifest = json.loads(
            (SYNTHETIC_BASE_MODEL / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["status"], "synthetic_model_only")
        self.assertEqual(manifest["warning"], "SIMULATION ONLY - NOT EVIDENCE")
        self.assertEqual(manifest["data_origin"], "synthetic_base_v1_event_overlay")
        self.assertTrue(manifest["quarantine"]["not_evidence"])
        self.assertTrue(manifest["quarantine"]["does_not_satisfy_model_gate"])
        self.assertTrue(manifest["quarantine"]["not_connected_to_dashboard"])
        self.assertTrue(manifest["quarantine"]["contains_real_station_labels"])
        self.assertFalse(manifest["quarantine"]["contains_real_daily_measurements"])
        self.assertTrue(manifest["quarantine"]["contains_synthetic_event_labels"])
        self.assertFalse(manifest["quarantine"]["contains_real_event_dates"])

        events = read_rows(SYNTHETIC_BASE_MODEL / "synthetic_events.csv")
        self.assertEqual(len(events), 30)
        event_rows = [row for row in events if row["period_type"] == "synthetic_event"]
        stress_rows = [
            row
            for row in events
            if row["period_type"] == "synthetic_stress_without_event"
        ]
        self.assertEqual(len(event_rows), 20)
        self.assertEqual(len(stress_rows), 10)
        self.assertTrue(
            all(row["data_origin"] == "synthetic_base_v1_event_overlay" for row in events)
        )
        self.assertFalse(
            any(row["event_start_date"].startswith("2019-05") for row in events),
            "Synthetic events must not reuse the real May 2019 incident month.",
        )

        panel = read_rows(SYNTHETIC_BASE_MODEL / "synthetic_modeling_dataset.csv")
        self.assertEqual(len(panel), 54795)
        self.assertEqual(len({row["station_id"] for row in panel}), 15)
        self.assertTrue(
            all(
                row["data_origin"] == "synthetic_base_v1_event_overlay"
                for row in panel
            )
        )
        self.assertIn("synthetic_event_id", read_header(SYNTHETIC_BASE_MODEL / "synthetic_modeling_dataset.csv"))
        self.assertNotIn(
            "synthetic_event_id",
            read_header(SYNTHETIC_BASE / "water_quality_daily.csv"),
            "The base dataset itself must remain unchanged.",
        )

        predictions = read_rows(SYNTHETIC_BASE_MODEL / "synthetic_test_predictions.csv")
        self.assertGreater(len(predictions), 0)
        self.assertTrue(
            all(
                row["data_origin"] == "synthetic_base_v1_event_overlay"
                for row in predictions
            )
        )
        self.assertTrue(all(row["date"] >= "2024-01-01" for row in predictions))
        self.assertTrue(
            all(0.0 <= float(row["probability_24h"]) <= 1.0 for row in predictions)
        )
        self.assertTrue(all(row["alert_24h"] in {"0", "1"} for row in predictions))

        metrics = read_rows(TABLES / "synthetic_base_model_metrics.csv")
        test_rf = [
            row
            for row in metrics
            if row["split"] == "test" and row["model"] == "random_forest"
        ]
        self.assertEqual(
            {int(row["horizon_hours"]) for row in test_rf}, {24, 48, 72}
        )
        self.assertEqual(
            {int(row["n_positive"]) for row in test_rf}, {20, 40, 60}
        )
        self.assertTrue(
            all(0.0 <= float(row["brier"]) <= 1.0 for row in test_rf)
        )

        detection = read_rows(TABLES / "synthetic_base_event_detection.csv")
        self.assertEqual(len(detection), 4)
        self.assertTrue(all(row["alerted"] == "1" for row in detection))

        report = (TABLES / "synthetic_base_model_report.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "SIMULATION ONLY",
            "NOT EVIDENCE",
            "Section 6 model-readiness gate",
            "risk assessment unavailable",
            "not evidence that real fish kills are predictable",
        ):
            self.assertIn(phrase, report)

        model_card = (TABLES / "synthetic_base_model_card.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("SIMULATION ONLY", model_card)
        self.assertIn("Prohibited use", model_card)
        self.assertIn("Do not load these artifacts into the evidence dashboard", model_card)

        gaps = (TABLES / "system_gaps_and_todo.md").read_text(encoding="utf-8")
        self.assertIn("T01", gaps)
        self.assertIn("The synthetic model is not evidence", gaps)

        for artifact in (
            "random_forest_24h.joblib",
            "random_forest_48h.joblib",
            "random_forest_72h.joblib",
            "logistic_24h.joblib",
            "dummy_24h.joblib",
        ):
            self.assertTrue((SYNTHETIC_BASE_MODEL_DIR / artifact).exists(), artifact)

        dashboard_text = DASHBOARD_JSON.read_text(encoding="utf-8")
        self.assertNotIn("synthetic_base_v1_event_overlay", dashboard_text)
        self.assertNotIn("SYN-BASE", dashboard_text)
        self.assertFalse((ROOT / "models" / "model.joblib").exists())

    def test_gap_filled_database_is_synthetic_and_trains_end_to_end(self) -> None:
        manifest = json.loads(
            (SYNTHETIC_GAP_FILL / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["status"], "synthetic_gap_fill_only")
        self.assertEqual(manifest["data_origin"], "synthetic_gap_fill_v1")
        self.assertEqual(manifest["readiness"]["checks"], 10)
        self.assertEqual(manifest["readiness"]["passed"], 10)
        self.assertEqual(manifest["real_gate"]["passed"], 2)
        self.assertEqual(manifest["real_gate"]["failed"], 8)
        self.assertEqual(manifest["model_status"], "trained_synthetic_gap_fill")
        self.assertFalse(manifest["quarantine"]["real_gate_satisfied"])

        connection = sqlite3.connect(
            SYNTHETIC_GAP_FILL / "himpil_synthetic_complete.sqlite"
        )
        try:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM stations").fetchone()[0], 15
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM stations "
                    "WHERE latitude IS NOT NULL AND longitude IS NOT NULL "
                    "AND lake_zone <> ''"
                ).fetchone()[0],
                15,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM incident_reports WHERE reported_fish_kill = 1"
                ).fetchone()[0],
                20,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT COUNT(*) FROM negative_windows WHERE fish_kill_reports = 0"
                ).fetchone()[0],
                1700,
            )

            checks = connection.execute(
                'SELECT "check", synthetic_status, real_status '
                'FROM readiness_checks ORDER BY "check"'
            ).fetchall()
            self.assertEqual(len(checks), 10)
            self.assertTrue(all(row[1] == "pass" for row in checks))
            self.assertEqual(sum(row[2] == "pass" for row in checks), 2)

            event_ids = [
                row[0]
                for row in connection.execute(
                    "SELECT event_id FROM incident_reports WHERE reported_fish_kill = 1"
                )
            ]
            self.assertEqual(len(event_ids), 20)
            for event_id in event_ids:
                corroboration = connection.execute(
                    "SELECT COUNT(*) FROM corroboration WHERE event_id = ?",
                    (event_id,),
                ).fetchone()[0]
                self.assertGreaterEqual(corroboration, 2, event_id)
                pre_event = connection.execute(
                    "SELECT COUNT(*) FROM pre_event_observations "
                    "WHERE synthetic_event_id = ?",
                    (event_id,),
                ).fetchone()[0]
                self.assertGreaterEqual(pre_event, 4, event_id)
                post_start = connection.execute(
                    "SELECT COUNT(*) FROM pre_event_observations p "
                    "JOIN incident_reports r ON p.synthetic_event_id = r.event_id "
                    "WHERE p.synthetic_event_id = ? AND p.date >= r.start_date",
                    (event_id,),
                ).fetchone()[0]
                self.assertEqual(post_start, 0, event_id)

            origins = {
                row[0]
                for row in connection.execute(
                    "SELECT DISTINCT data_origin FROM modeling_dataset"
                )
            }
            self.assertEqual(origins, {"synthetic_gap_fill_v1"})

            metric = connection.execute(
                "SELECT precision, recall, f1, pr_auc, brier "
                "FROM model_metrics "
                "WHERE model = 'random_forest' AND horizon_hours = 72 "
                "AND split = 'test'"
            ).fetchone()
            self.assertIsNotNone(metric)
            self.assertGreater(metric[0], 0.60)
            self.assertGreater(metric[1], 0.90)
            self.assertGreater(metric[2], 0.70)
            self.assertGreater(metric[3], 0.90)
            self.assertLess(metric[4], 0.01)

            detection = connection.execute(
                "SELECT COUNT(*) FROM model_event_detection WHERE alerted = 1"
            ).fetchone()[0]
            self.assertEqual(detection, 4)
        finally:
            connection.close()

        dashboard_text = DASHBOARD_JSON.read_text(encoding="utf-8")
        self.assertNotIn("synthetic_gap_fill", dashboard_text)
        self.assertNotIn("SYN-BASE", dashboard_text)

        demo_text = SYNTHETIC_DEMO_JSON.read_text(encoding="utf-8")
        self.assertNotIn("SIMULATION ONLY - NOT EVIDENCE", demo_text)
        demo = json.loads(demo_text)
        self.assertEqual(demo["status"], "synthetic_gap_fill_only")
        self.assertEqual(demo["badge"], "Synthetic gap-fill")
        self.assertEqual(demo["gapFill"]["readinessMet"], 10)
        self.assertEqual(
            demo["eventDetection"]["detected"], demo["eventDetection"]["total"]
        )
        self.assertFalse((ROOT / "models" / "model.joblib").exists())

    def test_dashboard_bundle_matches_evidence(self) -> None:
        text = DASHBOARD_JSON.read_text(encoding="utf-8")
        self.assertNotIn("C:\\Users", text)
        bundle = json.loads(text)
        self.assertEqual(bundle["coverage"]["lakeStations"], 15)
        self.assertEqual(bundle["coverage"]["lakeStationYears"], 150)
        self.assertEqual(bundle["coverage"]["completeStationYears"], 111)
        self.assertEqual(bundle["coverage"]["eventReports"], 1)
        self.assertEqual(bundle["coverage"]["verifiedEvents"], 0)
        self.assertEqual(bundle["coverage"]["lakeStationsWithZoneLabel"], 5)
        self.assertEqual(bundle["risk"]["status"], "insufficient_data")
        self.assertFalse(bundle["governance"]["metricsAvailable"])
        alignment = bundle["realAlignment"]
        self.assertEqual(alignment["status"], "descriptive_annual_trend")
        self.assertFalse(alignment["fishKillPrediction"])
        self.assertEqual(alignment["panel"]["stations"], 9)
        self.assertEqual(alignment["targets"]["do"]["n"], 90)
        self.assertLess(alignment["targets"]["do"]["slopePerYear"], 0)
        self.assertEqual(alignment["targets"]["temperature"]["n"], 81)
        self.assertIn("72-hour", alignment["unsupported"]["target"])
        self.assertEqual(len(bundle["events"]), 1)
        self.assertEqual(len(bundle["sources"]), 14)
        do_metric = next(metric for metric in bundle["metrics"] if metric["id"] == "do")
        self.assertAlmostEqual(do_metric["value"], 7.227778, places=5)
        t1 = next(row for row in bundle["governance"]["trainingChecks"] if row["check"] == "T1")
        self.assertEqual(t1["evidence"], "data/processed/modeling_dataset.csv")
        lake_area = bundle["weather"]["lakeArea"]
        self.assertEqual(lake_area["stationName"], "Tanay, Rizal")
        self.assertEqual(lake_area["sourceId"], "S01")
        self.assertEqual(len(lake_area["years"]), 9)
        self.assertNotIn(2025, {year["year"] for year in lake_area["years"]})
        self.assertEqual(lake_area["latest"]["year"], 2024)
        self.assertAlmostEqual(lake_area["latest"]["total"], 3508.5, places=1)
        self.assertEqual(lake_area["partial2025"]["year"], 2025)
        self.assertEqual(lake_area["partial2025"]["months"], 6)
        self.assertAlmostEqual(lake_area["partial2025"]["total"], 680.01, places=2)
        self.assertEqual(len(lake_area["monthly"]), 12)
        self.assertEqual({month["years"] for month in lake_area["monthly"]}, {9})
        self.assertIn("not a lake station", lake_area["role"])
        self.assertEqual(len(bundle["figures"]), 3)
        for figure in bundle["figures"]:
            self.assertTrue(
                (ROOT / "dashboard" / "public" / figure["file"]).exists(),
                figure["file"],
            )
        self.assertFalse(
            (
                ROOT
                / "dashboard"
                / "public"
                / "figures"
                / "fig_network_do_trend.png"
            ).exists()
        )

    def test_real_trend_model_is_descriptive_not_fish_kill(self) -> None:
        model = json.loads(
            (TABLES / "real_trend_model.json").read_text(encoding="utf-8")
        )
        self.assertEqual(model["status"], "descriptive_annual_trend")
        self.assertFalse(model["fishKillPrediction"])
        self.assertEqual(model["modelType"], "station_fixed_effects_linear_trend")
        self.assertEqual(model["panel"]["stations"], 9)
        self.assertEqual(model["targets"]["do"]["n"], 90)
        self.assertEqual(model["targets"]["temperature"]["n"], 81)
        self.assertEqual(model["unsupported"]["status"], "not_supported")
        self.assertIn("72-hour", model["unsupported"]["target"])

        card = (TABLES / "real_trend_model_card.md").read_text(encoding="utf-8")
        self.assertIn("fish-kill prediction", card.lower())
        self.assertIn("descriptive only", card.lower())
        self.assertIn("Not:**", card)

        report = (TABLES / "real_data_alignment_report.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("A 72-hour fish-kill prediction is not available", report)
        self.assertIn("risk assessment", report.lower())
        self.assertIn("not a fish-kill classifier", report)

        source = (ROOT / "dashboard" / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("What the annual data can support", source)
        self.assertIn("Descriptive annual trend only", source)
        self.assertIn("Synthetic model trained", source)
        self.assertIn("Real-data model remains unavailable", source)
        self.assertNotIn("No fish-kill model has been trained", source)

    def test_dashboard_refresh_uses_real_request_counts(self) -> None:
        bundle = json.loads(DASHBOARD_JSON.read_text(encoding="utf-8"))
        requests = bundle["dataRequests"]
        self.assertEqual(requests["total"], 9)
        self.assertEqual(requests["acknowledged"], 1)
        self.assertEqual(requests["planned"], 8)
        self.assertEqual(requests["received"], 0)
        self.assertEqual(requests["files"], 0)
        self.assertTrue(requests["outreachPaused"])
        self.assertIn("Outreach paused", requests["note"])

        source = (ROOT / "dashboard" / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn("dash-heatmap-panel", source)
        self.assertIn("data.dataRequests", source)
        self.assertIn("Synthetic model trained", source)
        self.assertIn("Real-data model remains unavailable", source)

    def test_dashboard_has_five_evidence_first_sections(self) -> None:
        source = (ROOT / "dashboard" / "src" / "App.tsx").read_text(encoding="utf-8")
        self.assertIn(
            'type PageId = "overview" | "water" | "evidence" | "model" | "sources"',
            source,
        )
        for label in (
            'label: "Overview"',
            'label: "Water data"',
            'label: "Fish-kill evidence"',
            'label: "Model run"',
            'label: "Sources"',
        ):
            self.assertIn(label, source)
        self.assertIn("Synthetic model trained", source)
        self.assertIn("Synthetic experiment", source)
        self.assertIn("Plates from the analysis workflow", source)
        self.assertIn("Weather context", source)
        self.assertIn("lakeArea", source)
        self.assertIn("Monthly climatology", source)
        self.assertIn("The evidence boundary", source)
        self.assertNotIn("Advisory Center", source)
        self.assertNotIn("History", source)
        self.assertNotIn("Settings", source)

    def test_required_documentation_and_r_outputs_exist(self) -> None:
        for relative in (
            "README.md",
            "README_WORKPLAN.md",
            "reports/HIMPIL_phase_1_8_report.md",
            "reports/tables/feasibility_report.md",
            "reports/tables/matching_report.md",
            "reports/tables/source_manifest.md",
            "reports/tables/r_eda_summary.md",
            "reports/tables/r_trends_summary.md",
            "reports/tables/r_model_evaluation_notes.md",
            "reports/data_requests/README.md",
            "reports/data_requests/request_matrix.csv",
            "reports/data_requests/data_access_log.csv",
            "reports/data_requests/permissions_and_ethics.md",
            "reports/data_requests/roles_and_decisions.md",
            "reports/data_requests/letters/LLDA_request.md",
            "reports/data_requests/letters/PAGASA_request.md",
            "reports/data_requests/letters/BFAR_request.md",
            "reports/data_requests/letters/LGU_request.md",
            "reports/data_requests/letters/adviser_approval_template.md",
            "reports/data_requests/submissions/LLDA_incident_request.md",
            "sandbox/README.md",
            "sandbox/synthetic/README.md",
            "sandbox/synthetic/build_base_dataset.py",
            "sandbox/synthetic/train_base_model.py",
            "sandbox/synthetic/run_prototype.py",
            "data/synthetic/README.md",
            "data/synthetic/base/README.md",
            "data/synthetic/base/data_dictionary.md",
            "data/synthetic/base/manifest.json",
            "data/synthetic/base/stations.csv",
            "data/synthetic/base/calibration_anchors.csv",
            "data/synthetic/base/water_quality_daily.csv",
            "data/synthetic/base/weather_daily.csv",
            "data/synthetic/base/himpil_synthetic_base.sqlite",
            "data/synthetic/base_model/README.md",
            "data/synthetic/base_model/synthetic_events.csv",
            "data/synthetic/base_model/synthetic_modeling_dataset.csv",
            "data/synthetic/base_model/synthetic_test_predictions.csv",
            "data/synthetic/base_model/manifest.json",
            "reports/tables/synthetic_base_model_report.md",
            "reports/tables/synthetic_base_model_card.md",
            "reports/tables/synthetic_base_model_metrics.csv",
            "reports/tables/synthetic_base_model_predictions.csv",
            "reports/tables/synthetic_base_model_feature_importance.csv",
            "reports/tables/synthetic_base_event_detection.csv",
            "reports/tables/synthetic_base_model_diagnostics.csv",
            "reports/tables/system_gaps_and_todo.md",
            "models/synthetic/README.md",
            "models/synthetic/base_model/README.md",
            "reports/tables/synthetic_base_report.md",
            "reports/tables/synthetic_base_calibration.csv",
            "reports/tables/synthetic_base_coverage.csv",
            "reports/tables/synthetic_prototype_report.md",
            "reports/tables/synthetic_model_card.md",
            "reports/tables/synthetic_prototype_metrics.csv",
            "reports/tables/synthetic_feature_importance.csv",
            "reports/tables/synthetic_event_detection.csv",
            "r/install_packages.R",
            "r/exploratory_analysis.R",
            "r/environmental_trends.R",
            "r/model_evaluation.R",
        ):
            self.assertTrue((ROOT / relative).exists(), relative)

        package = ROOT / "reports" / "data_requests"
        matrix = read_rows(package / "request_matrix.csv")
        access = read_rows(package / "data_access_log.csv")
        self.assertEqual(len(matrix), 9)
        self.assertEqual(
            [row["request_id"] for row in matrix],
            [row["request_id"] for row in access],
        )
        matrix_by_id = {row["request_id"]: row for row in matrix}
        access_by_id = {row["request_id"]: row for row in access}
        self.assertEqual(matrix_by_id["LLDA-INC-01"]["status"], "acknowledged")
        self.assertEqual(access_by_id["LLDA-INC-01"]["status"], "acknowledged")
        self.assertIn(
            "approval letters",
            access_by_id["LLDA-INC-01"]["response_summary"].lower(),
        )
        self.assertEqual(
            sum(row["status"] == "planned" for row in access),
            8,
        )
        self.assertEqual(
            sum(row["status"] == "acknowledged" for row in access),
            1,
        )
        for request_id, row in matrix_by_id.items():
            self.assertEqual(row["status"], access_by_id[request_id]["status"])
        for row in access:
            self.assertIn(row["status"], {"planned", "acknowledged"})
            self.assertEqual(row["files_received"], "")
            self.assertEqual(row["restrictions"], "")
            if row["status"] == "planned":
                self.assertEqual(row["sent_date"], "")
                self.assertEqual(row["sent_to"], "")
                self.assertEqual(row["response_date"], "")
                self.assertEqual(row["response_summary"], "")
        self.assertEqual(access_by_id["LLDA-INC-01"]["sent_date"], "")
        self.assertEqual(access_by_id["LLDA-INC-01"]["response_date"], "")
        self.assertEqual(access_by_id["LLDA-INC-01"]["files_received"], "")
        self.assertIn("not recorded", access_by_id["LLDA-INC-01"]["notes"])
        readme = (package / "README.md").read_text(encoding="utf-8")
        self.assertIn(
            "One LLDA incident-records request has been submitted and acknowledged",
            readme,
        )
        self.assertIn(
            "No data have been received and no data-sharing permission has been recorded",
            readme,
        )
        permissions = (package / "permissions_and_ethics.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("No external data-sharing permission", permissions)
        self.assertIn("approval letters requested", permissions)
        submission = (
            package / "submissions" / "LLDA_incident_request.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Request for Historical Fish Kill Incident Records", submission)
        self.assertIn("LLDA requested approval letters", submission)
        adviser = (
            package / "letters" / "adviser_approval_template.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Laguna State Polytechnic University", adviser)
        self.assertIn("[Professor name]", adviser)
        for letter in (
            "LLDA_request.md",
            "PAGASA_request.md",
            "BFAR_request.md",
            "LGU_request.md",
        ):
            text = (package / "letters" / letter).read_text(encoding="utf-8")
            self.assertIn("[Date]", text)
            self.assertIn("[Researcher name]", text)


if __name__ == "__main__":
    unittest.main()
