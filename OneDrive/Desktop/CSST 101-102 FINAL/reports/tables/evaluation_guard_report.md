# Evaluation guard report

**Decision: EVALUATION UNAVAILABLE.**

No model was fitted and no held-out predictions exist. Therefore no precision,
recall, F1, confusion matrix, ROC curve or precision-recall curve is reported.
Reporting such values would require fabricating results.

## Checks

| Check | Requirement | Status | Evidence |
|---|---|---|---|
| E1 | A labelled modelling dataset exists | fail | 0 rows in modeling_dataset.csv |
| E2 | A fitted model artifact exists | fail | models/model.joblib is missing |
| E3 | Held-out predictions exist | fail | data/outputs/test_predictions.csv is missing |

## What would be required

1. A reviewed 24-hour label file with positives and credible negatives.
2. A chronological train/validation/test split grouped by event.
3. A saved model and predictions for the untouched test period.
4. A pre-specified threshold and event-count reporting.

The R companion `r/model_evaluation.R` produces the same not-available status.

Status: `data/outputs/evaluation_status.csv`