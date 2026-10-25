# Training guard report

**Decision: TRAINING REFUSED.**

No model was fitted. No baseline was fitted. No accuracy, precision, recall, F1,
confusion matrix or AUC is reported because none exists.

## Checks

| Check | Requirement | Status | Evidence |
|---|---|---|---|
| T1 | A modelling dataset file exists | pass | data/processed/modeling_dataset.csv |
| T2 | The dataset contains real observations | fail | 0 data rows |
| T3 | The 24-hour target exists | pass | columns: observation_id, event_id, event_group, station_name, reported_lake_zone, observation_timestamp, dissolved_oxygen_mg_l, water_temperature_c... |
| T4 | Both classes are present | fail | positive=0, negative=0, missing=0 |
| T5 | Observations have valid timestamps | fail | 0 valid timestamps |
| T6 | Multiple independent event groups support a chronological split | fail | 0 non-empty event groups (minimum design requirement: 3) |
| T7 | Multiple years support train/validation/test periods | fail | 0 distinct year(s) |
| T8 | Pre-event features were measured before the event | fail | No dated pre-event water-quality observation exists; LLDA values are annual. |
| T9 | Station coordinates and a documented lake-zone mapping exist | fail | No coordinates; 5 of 15 lake stations carry a zone label in their name. |
| T10 | Credible non-event windows are documented | fail | No incident-reporting log; absence of a report is not evidence of absence. |

## Why this guard exists

The supplied sources contain one reported event period (May 2019), annual water-quality
summaries, and monthly weather summaries. A model trained on repeated rows from that one
event, or on annual values that include the event year, would leak information and would
not be a 24-hour early-warning system.

## Code path kept ready (not executed)

- scikit-learn 1.9.1
- Candidate estimators: DummyClassifier, DecisionTreeClassifier, RandomForestClassifier
- Required split: chronological train/validation/test by event group, never random.
- Required metrics after a real run: precision, recall, F1, confusion matrix and precision-recall curve.

## To unlock training

1. Obtain the dated incident log and dated observations described in `feasibility_report.md`.
2. Generate real 24-hour labels using `label_specification.md`.
3. Re-run `prepare_labels.py` and this guard.
4. Review every passing check manually before any fit.

Status: `data/outputs/training_status.csv`