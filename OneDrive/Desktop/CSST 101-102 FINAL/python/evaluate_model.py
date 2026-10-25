"""HIMPIL Phase 6b - guarded evaluation entry point.

Evaluation requires a saved model and real held-out predictions. The current
project has neither. This script writes an explicit not-available status and
never invents metrics.

Run:
    .venv\\Scripts\\python.exe python\\evaluate_model.py
"""

from __future__ import annotations

import sys

import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)

from common import MODEL_DIR, OUTPUT_DIR, PROCESSED_DIR, TABLE_DIR, ensure_dirs, write_csv


def main() -> int:
    ensure_dirs()
    model_path = MODEL_DIR / "model.joblib"
    predictions_path = OUTPUT_DIR / "test_predictions.csv"
    dataset_path = PROCESSED_DIR / "modeling_dataset.csv"

    dataset_rows = 0
    if dataset_path.exists():
        try:
            dataset_rows = len(pd.read_csv(dataset_path))
        except pd.errors.EmptyDataError:
            dataset_rows = 0

    checks = [
        {
            "check": "E1",
            "requirement": "A labelled modelling dataset exists",
            "status": "pass" if dataset_rows > 0 else "fail",
            "evidence": f"{dataset_rows} rows in modeling_dataset.csv",
        },
        {
            "check": "E2",
            "requirement": "A fitted model artifact exists",
            "status": "pass" if model_path.exists() else "fail",
            "evidence": str(model_path) if model_path.exists() else "models/model.joblib is missing",
        },
        {
            "check": "E3",
            "requirement": "Held-out predictions exist",
            "status": "pass" if predictions_path.exists() else "fail",
            "evidence": str(predictions_path) if predictions_path.exists() else "data/outputs/test_predictions.csv is missing",
        },
    ]
    write_csv(OUTPUT_DIR / "evaluation_status.csv", checks)

    blocked = any(row["status"] == "fail" for row in checks)
    if blocked:
        lines = [
            "# Evaluation guard report",
            "",
            "**Decision: EVALUATION UNAVAILABLE.**",
            "",
            "No model was fitted and no held-out predictions exist. Therefore no precision,",
            "recall, F1, confusion matrix, ROC curve or precision-recall curve is reported.",
            "Reporting such values would require fabricating results.",
            "",
            "## Checks",
            "",
            "| Check | Requirement | Status | Evidence |",
            "|---|---|---|---|",
        ]
        for row in checks:
            lines.append(
                f"| {row['check']} | {row['requirement']} | {row['status']} | {row['evidence']} |"
            )
        lines += [
            "",
            "## What would be required",
            "",
            "1. A reviewed 24-hour label file with positives and credible negatives.",
            "2. A chronological train/validation/test split grouped by event.",
            "3. A saved model and predictions for the untouched test period.",
            "4. A pre-specified threshold and event-count reporting.",
            "",
            "The R companion `r/model_evaluation.R` produces the same not-available status.",
            "",
            "Status: `data/outputs/evaluation_status.csv`",
        ]
        (TABLE_DIR / "evaluation_guard_report.md").write_text("\n".join(lines), encoding="utf-8")
        print("Evaluation unavailable: no model and no held-out predictions.")
        print(f"Status: {OUTPUT_DIR / 'evaluation_status.csv'}")
        return 2

    predictions = pd.read_csv(predictions_path)
    required = {"y_true", "y_score"}
    if not required.issubset(predictions.columns):
        raise SystemExit("test_predictions.csv must contain y_true and y_score")

    predictions = predictions.dropna(subset=["y_true", "y_score"]).copy()
    predictions["y_true"] = predictions["y_true"].astype(int)
    predictions["y_score"] = predictions["y_score"].astype(float)
    if predictions["y_true"].nunique() < 2:
        raise SystemExit("Held-out predictions contain one class; metrics are undefined")

    y_true = predictions["y_true"].to_numpy()
    y_score = predictions["y_score"].to_numpy()
    y_pred = (y_score >= 0.5).astype(int)

    labels = [0, 1]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    metrics = [{
        "threshold": 0.5,
        "n": int(len(y_true)),
        "positives": int((y_true == 1).sum()),
        "negatives": int((y_true == 0).sum()),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "average_precision": float(average_precision_score(y_true, y_score)),
        "tn": int(matrix[0, 0]),
        "fp": int(matrix[0, 1]),
        "fn": int(matrix[1, 0]),
        "tp": int(matrix[1, 1]),
    }]
    write_csv(OUTPUT_DIR / "evaluation_metrics.csv", metrics)

    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    curve = []
    for index in range(len(precision)):
        curve.append({
            "threshold": "" if index == len(thresholds) else float(thresholds[index]),
            "precision": float(precision[index]),
            "recall": float(recall[index]),
        })
    write_csv(OUTPUT_DIR / "precision_recall_curve.csv", curve)

    lines = [
        "# Evaluation results",
        "",
        "These metrics come only from real held-out predictions.",
        "",
        f"- Observations: **{len(y_true)}**",
        f"- Positives: **{int((y_true == 1).sum())}**",
        f"- Negatives: **{int((y_true == 0).sum())}**",
        f"- Precision at 0.5: **{metrics[0]['precision']:.3f}**",
        f"- Recall at 0.5: **{metrics[0]['recall']:.3f}**",
        f"- F1 at 0.5: **{metrics[0]['f1']:.3f}**",
        f"- Average precision: **{metrics[0]['average_precision']:.3f}**",
        "",
        "Confusion matrix (rows actual 0/1, columns predicted 0/1):",
        "",
        f"```\n{matrix}\n```",
        "",
        "Operational warning performance still requires prospective validation; this is a",
        "retrospective held-out result only.",
    ]
    (TABLE_DIR / "evaluation_report.md").write_text("\n".join(lines), encoding="utf-8")
    print("Evaluation complete.")
    print(f"Metrics: {OUTPUT_DIR / 'evaluation_metrics.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
