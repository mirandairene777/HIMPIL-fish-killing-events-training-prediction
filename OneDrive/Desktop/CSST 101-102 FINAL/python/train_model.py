"""HIMPIL Phase 6a - guarded training entry point.

This script refuses to train unless a real, labelled, chronologically splittable
dataset exists. It always writes an auditable status file. It never creates
synthetic rows and never reports metrics without a model.

Current status: BLOCKED. See reports/tables/feasibility_report.md.

Run:
    .venv\\Scripts\\python.exe python\\train_model.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

from common import MODEL_DIR, OUTPUT_DIR, PROCESSED_DIR, TABLE_DIR, ensure_dirs, write_csv

MIN_EVENT_PERIODS = 3
MIN_EVENT_GROUPS = 3


def main() -> int:
    ensure_dirs()
    dataset_path = PROCESSED_DIR / "modeling_dataset.csv"
    status_rows = []

    def add(check: str, requirement: str, passed: bool, evidence: str, consequence: str) -> None:
        status_rows.append({
            "check": check,
            "requirement": requirement,
            "status": "pass" if passed else "fail",
            "evidence": evidence,
            "consequence": consequence,
        })

    add(
        "T1",
        "A modelling dataset file exists",
        dataset_path.exists(),
        "data/processed/modeling_dataset.csv",
        "No features can be loaded.",
    )

    data = pd.DataFrame()
    if dataset_path.exists():
        try:
            data = pd.read_csv(dataset_path)
        except pd.errors.EmptyDataError:
            data = pd.DataFrame()

    add(
        "T2",
        "The dataset contains real observations",
        len(data) > 0,
        f"{len(data)} data rows",
        "There is nothing to train on.",
    )

    target = "fish_kill_within_24h"
    has_target = target in data.columns
    add(
        "T3",
        "The 24-hour target exists",
        has_target,
        f"columns: {', '.join(data.columns[:8])}{'...' if len(data.columns) > 8 else ''}",
        "Supervised learning is impossible.",
    )

    labels = pd.Series(dtype="float64")
    if has_target and len(data):
        labels = pd.to_numeric(data[target], errors="coerce")
    n_positive = int((labels == 1).sum())
    n_negative = int((labels == 0).sum())
    add(
        "T4",
        "Both classes are present",
        n_positive > 0 and n_negative > 0,
        f"positive={n_positive}, negative={n_negative}, missing={int(labels.isna().sum())}",
        "A classifier cannot be fitted or evaluated on one class.",
    )

    has_timestamp = "observation_timestamp" in data.columns
    parsed_time = pd.to_datetime(data["observation_timestamp"], errors="coerce") if has_timestamp else pd.Series(dtype="datetime64[ns]")
    add(
        "T5",
        "Observations have valid timestamps",
        has_timestamp and len(parsed_time) > 0 and parsed_time.notna().all(),
        f"{int(parsed_time.notna().sum())} valid timestamps" if has_timestamp else "column missing",
        "Chronological validation cannot be guaranteed.",
    )

    event_groups = pd.Series(dtype="object")
    if "event_group" in data.columns:
        event_groups = data["event_group"].astype("string").fillna("")
    n_event_groups = int(event_groups[event_groups != ""].nunique())
    add(
        "T6",
        "Multiple independent event groups support a chronological split",
        n_event_groups >= MIN_EVENT_GROUPS,
        f"{n_event_groups} non-empty event groups (minimum design requirement: {MIN_EVENT_GROUPS})",
        "All event examples would fall into one split, causing leakage or an untestable model.",
    )

    years = pd.to_datetime(parsed_time, errors="coerce").dt.year.dropna().unique() if len(parsed_time) else []
    n_years = len(years)
    add(
        "T7",
        "Multiple years support train/validation/test periods",
        n_years >= 3,
        f"{n_years} distinct year(s)",
        "A held-out period cannot be created.",
    )

    add(
        "T8",
        "Pre-event features were measured before the event",
        False,
        "No dated pre-event water-quality observation exists; LLDA values are annual.",
        "Every potential feature would leak information from the event period.",
    )

    add(
        "T9",
        "Station coordinates and a documented lake-zone mapping exist",
        False,
        "No coordinates; 5 of 15 lake stations carry a zone label in their name.",
        "Event and station cannot be spatially linked.",
    )

    add(
        "T10",
        "Credible non-event windows are documented",
        False,
        "No incident-reporting log; absence of a report is not evidence of absence.",
        "False labels would teach the model from unknown outcomes.",
    )

    write_csv(OUTPUT_DIR / "training_status.csv", status_rows)

    failed = [row for row in status_rows if row["status"] == "fail"]
    model_version = {
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "dataset_rows": len(data),
        "positive_labels": n_positive,
        "negative_labels": n_negative,
        "decision": "refused" if failed else "eligible_for_review",
    }
    write_csv(OUTPUT_DIR / "training_environment.csv", [model_version])

    report = [
        "# Training guard report",
        "",
        "**Decision: TRAINING REFUSED.**" if failed else "**Decision: eligible for manual review.**",
        "",
        "No model was fitted. No baseline was fitted. No accuracy, precision, recall, F1,",
        "confusion matrix or AUC is reported because none exists.",
        "",
        "## Checks",
        "",
        "| Check | Requirement | Status | Evidence |",
        "|---|---|---|---|",
    ]
    for row in status_rows:
        report.append(
            f"| {row['check']} | {row['requirement']} | {row['status']} | {row['evidence']} |"
        )
    report += [
        "",
        "## Why this guard exists",
        "",
        "The supplied sources contain one reported event period (May 2019), annual water-quality",
        "summaries, and monthly weather summaries. A model trained on repeated rows from that one",
        "event, or on annual values that include the event year, would leak information and would",
        "not be a 24-hour early-warning system.",
        "",
        "## Code path kept ready (not executed)",
        "",
        f"- scikit-learn {sklearn.__version__}",
        f"- Candidate estimators: {DummyClassifier.__name__}, {DecisionTreeClassifier.__name__}, {RandomForestClassifier.__name__}",
        "- Required split: chronological train/validation/test by event group, never random.",
        "- Required metrics after a real run: precision, recall, F1, confusion matrix and precision-recall curve.",
        "",
        "## To unlock training",
        "",
        "1. Obtain the dated incident log and dated observations described in `feasibility_report.md`.",
        "2. Generate real 24-hour labels using `label_specification.md`.",
        "3. Re-run `prepare_labels.py` and this guard.",
        "4. Review every passing check manually before any fit.",
        "",
        "Status: `data/outputs/training_status.csv`",
    ]
    (TABLE_DIR / "training_guard_report.md").write_text("\n".join(report), encoding="utf-8")
    (MODEL_DIR / "README.md").write_text(
        "# Models\n\nNo model artifact exists. Training is blocked by the label-feasibility guard.\n",
        encoding="utf-8",
    )

    print("Training refused: label/feature prerequisites are not met.")
    print(f"Rows: {len(data)}; positive: {n_positive}; negative: {n_negative}")
    print(f"Failed checks: {len(failed)} of {len(status_rows)}")
    print(f"Status: {OUTPUT_DIR / 'training_status.csv'}")
    return 2 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
