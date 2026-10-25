# Synthetic prototype model card

> **SIMULATION ONLY — NOT EVIDENCE.** This model card describes a model trained
> on generated data. It is not a model card for a real Laguna de Bay risk model.
> The real model has not been trained and the real risk assessment remains
> unavailable.

## Model details

| Field | Value |
|---|---|
| Name | HIMPIL synthetic prototype — random forest |
| Version | `synthetic-2026-10-23` |
| Type | Random forest classifier, three horizon-specific fits |
| Target | Simulated fish-kill event start within 24, 48, or 72 hours |
| Training data | Synthetic station-day panel, seed `20261023` |
| Data origin | `synthetic_simulation` — no real observations |
| Features | 21 weather, water-quality, lag, and rolling features |
| Split | Chronological: train 2021–2022, validation 2023, test 2024 |
| Artifact | `models/synthetic/random_forest_24h.joblib` and horizon variants |
| Primary test F1 (24h) | 0.750 (simulation only) |
| Primary test PR-AUC (24h) | 0.948 (simulation only) |

## Intended use

- Demonstrate the modelling pipeline and rare-event evaluation code.
- Give the team a concrete artifact for code review, UI discussion, and onboarding.
- Test file layout, quarantine rules, and documentation.

## Prohibited uses

- Any real fish-kill prediction or public warning.
- Any claim about Laguna de Bay water quality, ecology, or risk.
- Any comparison with a real model, real station, real zone, or real event.
- Any defense, abstract, paper, or policy recommendation presented as evidence.
- Any use as a substitute for the Section 6 gate.

## Training data and labels

The generator creates a daily panel for six synthetic stations over four
synthetic calendar years. It injects eight simulated event periods and three
stress-only periods. Labels are derived from the simulation schedule. The model
sees only backward-looking features. Event and recovery windows are excluded from
fitting and evaluation.

## Evaluation

The test partition is the 2024 synthetic calendar. It contains two simulated
event periods. Metrics include precision, recall, F1, PR-AUC, ROC-AUC, Brier
score, and confusion-matrix counts. Positive counts are small; results are
unstable and are not estimates of real-world performance.

See [`synthetic_prototype_report.md`](synthetic_prototype_report.md) and
[`synthetic_prototype_metrics.csv`](synthetic_prototype_metrics.csv).

## Limitations

- The generator encodes a known pre-event signal; a model can learn it because
  the signal is in the simulation.
- The event schedule, station behavior, and stress periods are invented.
- No real missingness, sampling bias, measurement error, reporting delay, or
  sensor failure process is represented.
- No real spatial structure or zone crosswalk is represented.
- No real incident-reporting completeness process is represented.
- The test set is small and covers only two simulated event periods.
- Feature importance is not a causal finding.

## Ethical and operational notes

The artifact must remain in `models/synthetic/`. It must not be loaded by the real
dashboard, the real guard scripts, or any advisory service. Any screenshot or
slide that uses it must carry the “SIMULATION ONLY — NOT EVIDENCE” label.

## Maintenance

Regenerate with the fixed seed when the code changes. If the model is retained
for a demo, record the code version and seed. If real data arrive, do not
fine-tune this artifact; build a new real-data model under the Section 6 gate.
