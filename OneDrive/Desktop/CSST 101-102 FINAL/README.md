# HIMPIL

**A Machine Learning-Based Early Warning and Advisory System for Fish Kill Events in Laguna de Bay**

> **Living workplan:** [`README_WORKPLAN.md`](README_WORKPLAN.md) is the single source of truth for active tasks, blockers, data requests, the model-readiness gate, decisions, and the update history. Update it after every work session.
>
> **Team guide:** this README is the handoff document. It explains what exists, what is real, what is synthetic, how to run everything, and what is still missing.

HIMPIL is a student research project. It is **not** an official environmental monitoring service, emergency warning system, or source of regulatory advice.

---

## 1. The short version

There are **five separate tracks** in this repository. Do not mix them.

| Track | What it is | Current state |
|---|---|---|
| **Real-data evidence track** | The defensible study of the supplied Laguna de Bay sources, the evidence dashboard, and the feasibility gate | Complete as a Phase 1-9 foundation. No real **fish-kill** model is trained; a descriptive annual trend model is available separately. The real risk assessment is **unavailable**. |
| **Synthetic base dataset** | A quarantined daily dataset on the real 15-station/2016-2025 frame, calibrated to real annual anchors | Reproducible in `data/synthetic/base/`. **Synthetic only.** |
| **Synthetic base model** | A separate event-overlay model trained on a copy of the base panel | Runnable. It has 24/48/72-hour metrics, a model card, a report, and a five-input presentation demo. **Synthetic only.** |
| **Synthetic gap-filled database and model** | A quarantined SQLite database and 24/48/72-hour models that fill all ten training checks in a synthetic scope | Runnable. 20 exact-dated events, 1,700 non-event windows, 40 corroboration records, 15 coordinates/zones. 72h F1 **0.797**. **Synthetic only.** |
| **Synthetic model prototype** | A separate toy 6-station/2021-2024 world for testing the modelling pipeline | Runnable. It produces models, metrics, a model card, and a report. **Synthetic only.** |

**The honest headline:** the original operational goal is still unmet. We do not have enough real data to train or defend a fish-kill prediction model. The synthetic base dataset gives the team a realistic schema to build against; the base model, the gap-fill model, and the prototype prove that the pipeline works end to end. None of them proves that Laguna de Bay fish kills can be predicted.

**Direction update (23 October 2026):** the team has paused external data outreach, including the LLDA follow-up, to focus on what can be learned and finished now: the synthetic ML pipeline, the evidence dashboard, and the gap-filled training demonstration. Pausing does not change the verdict. The real fish-kill model remains unavailable, the descriptive annual trend estimate is reported separately, the synthetic artifacts remain synthetic-only, and `LLDA-INC-01` stays recorded as `acknowledged` - not received, not complete, and not closed. Paper work is paused unless explicitly requested.

The evidence dashboard continues to say **"risk assessment unavailable."** The real evidence bundle remains synthetic-free; the Model page now includes a separately labeled gap-filled synthetic training-run panel.

---

## 2. Current position at a glance

**Last updated:** 24 October 2026  
**Current milestone:** M1 paused by team decision (23 October 2026); P5 dashboard refresh complete; P6 first synthetic learning experiment complete (lead-time policy); P7 five-input presentation demo complete; P9 real-data alignment complete (descriptive annual trend model; real 72-hour fish-kill model still blocked); P10 synthetic gap-filled database and training run complete; paper work paused by user request  
**External data track:** paused — `LLDA-INC-01` remains `acknowledged`, with no files or permissions received

| Item | Current result |
|---|---|
| Sources inspected and documented | 14 (S01–S14) |
| Water-quality data | Annual station summaries, 2016–2025 |
| Weather data | Monthly station summaries, 2016–2025 |
| Lake stations | 15 |
| Lake station-years | 150 |
| Complete across six water-quality variables | 111 |
| Numeric lake water-quality values | 711 station-year-variable values |
| Accepted fish-kill event reports | 1 (Biñan/Pila, May 2019) |
| Independently verified fish-kill events | 0 |
| Dated station-monitoring observations | 0 |
| During-event context measurements (UPD article) | 4 (one 29 May 2019 sample) |
| Dated pre-event observations | 0 |
| Real 24-hour positive labels | 0 |
| Real 24-hour negative labels | 0 |
| Real fish-kill models | 0 |
| Real fish-kill metrics | None |
| Real descriptive annual trend model | 1: nine-station balanced panel, 2016-2025; DO and temperature slopes with 95% CIs |
| Real trend metrics | DO **-0.111861 mg/L/year** (95% CI **-0.141078 to -0.082643**); temperature **+0.056015 °C/year** (95% CI **-0.012883 to 0.124912**, interval includes zero) |
| Synthetic base dataset | 15 stations, 2016–2025, 54,795 daily station-days, 6 variables, 3 synthetic weather zones |
| Synthetic base rows | 10,959 weather rows; 900 annual anchor rows; SQLite + CSV; **synthetic only** |
| Synthetic base model | 20 synthetic events; 53,950 model-eligible rows; 24/48/72-hour random forest, logistic, and dummy baselines |
| Synthetic base test metrics | 24h F1 0.625 / PR-AUC 0.568; 48h F1 0.748 / PR-AUC 0.957; 72h F1 0.797 / PR-AUC 0.947 - **synthetic only** |
| Synthetic gap-filled database | 15 stations; 54,795 station-days; 20 exact-dated events; 1,700 non-event windows; 40 corroboration records; 15 coordinates/zones; 10/10 synthetic checks |
| Synthetic gap-filled test metrics | 24h F1 0.635; 48h F1 0.755; 72h F1 0.797 / PR-AUC 0.939 / Brier 0.0029; 4/4 synthetic events detected |
| Synthetic presentation demo | Five inputs; test F1 0.5435 / PR-AUC 0.6947; 4/4 synthetic events detected; local app available - **synthetic only** |
| Synthetic prototype | Generic 6-station/2021–2024 model demo; quarantined in `sandbox/synthetic/` |
| Evidence dashboard | Five sections; refreshed decision-support Overview; real risk assessment unavailable |
| Data requests | 1 acknowledged (`LLDA-INC-01`); 8 planned; 0 files; 0 permissions; **outreach paused (D-009)** |
| Tests | 17/17 contract tests pass |

The real evidence counts are deliberately blank where the source is blank. Missing is never converted to zero.

---

## 3. Read this before you touch anything

These rules protect the project from turning a software demo into a false scientific claim.

1. **Keep the tracks separate.** Real evidence lives in `data/processed/`, `reports/`, and the dashboard. Synthetic data lives in `data/synthetic/`, `models/synthetic/`, and `sandbox/synthetic/`.
2. **Never invent a real date, location, station, contact, measurement, incident, zone, metric, or result.** If a value is unknown, leave it blank and explain why.
3. **Never use a during-event or post-event measurement as a predictor.** The 29 May 2019 sample is context, not a pre-event feature.
4. **Never turn missing data into zero.** Blank, `**`, `…`, `...`, and undefined cells are flagged, not filled.
5. **Do not present a real risk score, probability, category, or advisory.** There is no real **fish-kill** model. A descriptive annual trend model exists separately and cannot produce a risk score. The dashboard must keep saying **"risk assessment unavailable."**
6. **Do not treat synthetic data as evidence.** The base dataset uses real station labels and annual anchors for calibration, but every daily value is generated. The prototype's dates, stations, events, metrics, and feature importances are also generated. Neither can satisfy the model gate.
7. **Do not claim a request was sent, data were received, or permission was granted without a record.** The access log is evidence; an intention is not.
8. **Update `README_WORKPLAN.md` after every work session.** Mark tasks in progress before starting, and complete only when an artifact or command output exists.
9. **Keep original source files unchanged.** The test suite checks the eight original workbooks for byte identity.
10. **When in doubt, report the limitation, not a guess.**

---

## 4. What exists

### 4.1 Real-data evidence pipeline

The Phase 1–9 foundation is complete:

- source inventory, hashes, and text extracts for 14 sources;
- cleaned annual lake water-quality tables, monthly rainfall and wind tables, and a station registry;
- one accepted 2019 event report with a full evidence audit;
- a match audit showing that no supplied observation is usable as a pre-event predictor;
- a blocked fish-kill label specification and a header-only real modelling schema;
- guarded real fish-kill training and evaluation scripts that refuse to run;
- a real descriptive annual trend model with confidence intervals and a model card;
- descriptive R analysis and figures;
- a five-section evidence dashboard;
- a data-request package with field-level specifications, letters, permissions, and an access log;
- a contract test suite.

### 4.2 Evidence dashboard

The React/Vite interface is a five-section decision-support dashboard built on an editorial research-brief system:

| Section | Purpose |
|---|---|
| Overview | Filterable station-year completeness map, four real KPI cards, selected-variable annual trend, latest annual signals, readiness/request rails, reported event, and the evidence boundary |
| Water data | Six annual water-quality measures, station table, CSV export, network weather context, the real Tanay rainfall panel, the descriptive annual-trend panel, and three R analysis plates |
| Fish-kill evidence | The single reported event, a four-step verification ladder, and the source-claim audit |
| Model status | The refusal state, a readiness meter, blocking requirements, the absence of real metrics, and a separately labeled gap-filled synthetic training-run panel |
| Sources | The 14-source register and data-quality/provenance notes |

The persistent top notice, hero status panel, and header pill keep the **"risk assessment unavailable"** state visible. The refreshed Overview uses only real coverage, readiness, event, source, and data-request counts. The dashboard does **not** contain a synthetic page, synthetic chart, or synthetic risk score. A separately labeled gap-filled synthetic training-run panel on the Model page reports simulation metrics; synthetic rows are not loaded into the evidence bundle.

The weather section now separates two real views:

- **PAGASA network cards** — rainfall and wind summaries averaged across the supplied stations. These are national-network context, not lake measurements.
- **Tanay, Rizal (S01)** — the only supplied station clearly in the Laguna de Bay watershed. It shows complete-year annual rainfall for 2016–2024, a 2016–2024 monthly climatology, and the partial 2025 total (January–June) as a partial figure, never as an annual total.

The Tanay panel is descriptive. It is a regional proxy, not a lake measurement, and it is not a forecast input, risk score, or model feature. The monthly rainfall record cannot support a 72-hour prediction.

#### Real descriptive annual trend model

The project now fits one real statistical model: a **station fixed-effects linear trend** on the nine lake stations with complete 2016-2025 dissolved-oxygen records. It uses a common linear year term, station intercepts, HC3 standard errors, and a 1,000-replicate cluster bootstrap by station. It estimates annual change in mean dissolved oxygen and water temperature.

| Target | n | Estimate | 95% CI | Cluster bootstrap 95% | Reading |
|---|---:|---|---|---|---|
| Dissolved oxygen | 90 | **-0.111861 mg/L/year** | -0.141078 to -0.082643 | -0.137933 to -0.087157 | Decline; interval excludes zero |
| Water temperature | 81 | **+0.056015 °C/year** | -0.012883 to 0.124912 | -0.009302 to 0.109758 | No clear trend; interval includes zero |

This is a **descriptive annual association**, not a fish-kill model, not a 24/48/72-hour model, and not a causal finding. The panel is small, the stations are not a probability sample, and the analysis does not control for changes in monitoring practice. The model cannot detect the May 2019 event in annual averages. Its model card explicitly prohibits using it for a risk score, zone map, advisory, or warning.

The Water data page shows the estimate in a **What the annual data can support** panel marked **Descriptive only**. The persistent fish-kill state remains **risk assessment unavailable**. Reproduce it with:

```powershell
.\.venv\Scripts\python.exe python\train_real_trend.py
```

Outputs: `reports/tables/real_trend_model.json`, `real_trend_model_metrics.csv`, `real_trend_model_card.md`, and `real_data_alignment_report.md`.

### 4.3 Synthetic base dataset

The requested base dataset is in [`data/synthetic/base/`](data/synthetic/base/README.md). It mirrors the real HIMPIL frame rather than the toy prototype:

- the **15 real lake station labels** from the supplied LLDA workbooks;
- **2016-01-01 to 2025-12-31**;
- six daily water-quality variables in the real units: nitrate, phosphate, BOD, pH, water temperature, and dissolved oxygen;
- three synthetic weather zones with daily rainfall, wind, and air temperature;
- real annual station-year anchors where available; missing annual cells are imputed and flagged;
- CSV files, a SQLite database, a data dictionary, a calibration audit, and a manifest.

Start here:

- [`data/synthetic/base/README.md`](data/synthetic/base/README.md) — dataset contents and regeneration;
- [`data/synthetic/base/data_dictionary.md`](data/synthetic/base/data_dictionary.md) — schema, units, and method;
- [`reports/tables/synthetic_base_report.md`](reports/tables/synthetic_base_report.md) — coverage, calibration, and limitations.

The base dataset contains **no fish-kill labels, no real event dates, no coordinates, and no risk scores**. It does not satisfy the model gate and is not loaded into the dashboard. Its base-model metrics appear only in the separately labeled Model-page panel.

### 4.4 Synthetic base model

A separate event-overlay exercise in [`data/synthetic/base_model/`](data/synthetic/base_model/README.md). It:

- injects 20 synthetic event periods and 10 high-stress no-event periods into a copy of the base panel;
- keeps the base dataset itself unchanged;
- builds backward-looking features and 24/48/72-hour labels;
- uses a chronological split: train before 2023, validation 2023, test 2024–2025;
- fits a majority-class baseline, a logistic regression, and a random forest;
- writes metrics, predictions, event detection, feature importance, a model card, and a report.

Start here:

- [`sandbox/synthetic/train_base_model.py`](sandbox/synthetic/train_base_model.py) — generator and training code;
- [`reports/tables/synthetic_base_model_report.md`](reports/tables/synthetic_base_model_report.md) — metrics and limits;
- [`reports/tables/synthetic_base_model_card.md`](reports/tables/synthetic_base_model_card.md) — intended and prohibited use;
- [`reports/tables/synthetic_72h_model_outcome.md`](reports/tables/synthetic_72h_model_outcome.md) — concise 72-hour outcome summary;
- [`reports/tables/system_gaps_and_todo.md`](reports/tables/system_gaps_and_todo.md) — system gaps and prioritized to-do list.

The saved **72-hour** random forest is at `models/synthetic/base_model/random_forest_72h.joblib`. On the synthetic test split at threshold 0.5 it reports precision **0.6705**, recall **0.9833**, F1 **0.7973**, PR-AUC **0.9471**, Brier **0.0026**, with 59 TP, 29 FP, 1 FN, and 10,716 TN; it detects **4/4** synthetic test events. These are simulation metrics, not real HIMPIL performance.

The scores are an artifact of the injected synthetic event process. The 24-hour model’s false positives are mostly early detections 2–3 days before events, which the 24-hour label counts as negative. That is a label-timing problem, not evidence of real predictability.

A follow-up P6 experiment tests one way to handle those early alerts. With **two stations confirming on the same day** and a **72-hour cooldown**, it issues 4 episodes, detects **4/4** synthetic test events, and has **0 false episodes**; the first alerts arrive 2-3 days before the synthetic event starts. Validation detects **2/2** events with **0 false episodes**. The raw station-day alert burden remains **44** in test (20 target-day, 23 early pre-event, 1 stress-only), so confirmation reduces issued episodes, not the underlying errors. The policy was chosen after inspecting the test error profile, so it is **post hoc and synthetic only**. See [`reports/tables/synthetic_lead_time_policy_report.md`](reports/tables/synthetic_lead_time_policy_report.md). It is not connected to the dashboard.

### 4.5 Synthetic gap-filled database and model

A synthetic gap-fill exercise in [`data/synthetic/gap_fill/`](data/synthetic/gap_fill/README.md). It starts from the supplied annual and monthly summaries and the existing synthetic base panel, then adds the structural records needed to train end to end:

- 54,795 dated station-days and 400 pre-event rows before 20 exact-dated events;
- 30 incident/patrol reports, 1,700 monthly no-event windows, and 40 independent corroboration records;
- 15 synthetic station coordinates, 15 zone assignments, and 15 per-station annual aggregation rules;
- all 10 readiness checks pass in the synthetic scope.

The database is `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite`; models are in `models/synthetic/gap_filled/`. The Model page shows a **Gap-filled synthetic training run** panel. The 72-hour test model reports precision **0.670**, recall **0.983**, F1 **0.797**, PR-AUC **0.939**, Brier **0.0029**, and detects **4/4** synthetic test events. The real evidence gate remains 2 pass and 8 fail, and the real dashboard still says **risk assessment unavailable**.

Start here:

- [`sandbox/synthetic/build_gap_filled_database.py`](sandbox/synthetic/build_gap_filled_database.py) - builds the synthetic database;
- [`sandbox/synthetic/train_gap_filled_model.py`](sandbox/synthetic/train_gap_filled_model.py) - trains the 24/48/72-hour models;
- [`reports/tables/synthetic_gap_fill_database_report.md`](reports/tables/synthetic_gap_fill_database_report.md) - gap-fill coverage and checks;
- [`reports/tables/synthetic_gap_filled_model_report.md`](reports/tables/synthetic_gap_filled_model_report.md) - training outcome and limits.

### 4.6 Synthetic model prototype

A separate toy demonstration in [`sandbox/synthetic/`](sandbox/synthetic/README.md). It:

- generates a daily synthetic station-day panel for six synthetic stations over 2021–2024;
- injects eight simulated event periods and three high-stress no-event periods;
- builds backward-looking features and 24/48/72-hour labels;
- uses a chronological train/validation/test split;
- fits a majority-class baseline, a logistic regression, and a random forest;
- writes metrics, feature importance, event-level detection, a model card, and a full report.

Start here:

- [`sandbox/synthetic/README.md`](sandbox/synthetic/README.md) — how all four synthetic artifacts work and how to run them;
- [`reports/tables/synthetic_prototype_report.md`](reports/tables/synthetic_prototype_report.md) — model-demo report;
- [`reports/tables/synthetic_model_card.md`](reports/tables/synthetic_model_card.md) — intended use and prohibited use.

Reports and model cards remain labeled synthetic; the dashboard uses one compact **Synthetic gap-fill** badge per panel. The model artifacts are in `models/synthetic/`, never `models/model.joblib`.

### 4.7 Synthetic presentation model (five inputs)

A separate, presentation-only demo built from the synthetic base model. It uses the five fields in the team's illustrative data table: dissolved oxygen, water temperature, pH, rainfall, and wind speed. It predicts a **simulated 72-hour event probability** and maps it to an illustrative Low/Medium/High band.

This is the model to use for a team demo if they want a live five-input example. It is **synthetic only**. In the synthetic test split: precision `0.4032`, recall `0.8333`, F1 `0.5435`, PR-AUC `0.6947`; 124 station-day alerts (50 true positives, 74 false positives, 10 missed positives); **4/4** synthetic events detected. Validation F1 is `0.7059` with **2/2** events detected. The bands are communication labels, not validated risk thresholds.

Start here:

- [`sandbox/synthetic/train_presentation_model.py`](sandbox/synthetic/train_presentation_model.py) - training code;
- [`sandbox/synthetic/predict_presentation.py`](sandbox/synthetic/predict_presentation.py) - one-row command-line demo;
- [`sandbox/presentation_app/app.py`](sandbox/presentation_app/app.py) - local interactive web demo;
- [`reports/tables/synthetic_presentation_model_report.md`](reports/tables/synthetic_presentation_model_report.md) - metrics, example inputs, and a five-minute presentation script.

Run the interactive version:

```powershell
.\.venv\Scripts\python.exe sandbox\presentation_app\app.py
```

Open `http://127.0.0.1:8000`. The first start may take a few seconds while the model loads. The app is local-only, uses the standard library, and is not connected to the evidence dashboard.

The six example rows in the report are fictional values from the team's slide. They show the interface, not real measurements or validated risk levels.

### 4.8 Data request package

The package in [`reports/data_requests/`](reports/data_requests/README.md) contains nine field-level requests covering:

- LLDA daily water-quality observations, station metadata, aggregation rules, incidents, reporting completeness, and zones;
- PAGASA daily weather;
- BFAR incident records;
- Biñan/Pila LGU records.

It includes four ready-to-complete letters, an adviser approval template, a request matrix, a permissions-and-ethics record, decision rights, and an access log.

**Current status:** one LLDA incident-records request is `acknowledged`; LLDA asked for professor approval letters. Eight requests remain `planned`. **No data have been received and no data-sharing permission has been recorded.** The exact send date, recipient, channel, and response date were not supplied, so those fields remain blank. **Outreach is paused under D-009 (23 October 2026); the package is retained, not withdrawn.**

### 4.9 Tests and documentation

- `tests/test_pipeline.py` - contract tests for source identity, evidence limits, missing values, temporal ordering, blocked real labels, guard refusals, dashboard/evidence agreement, the refreshed Overview's real request counts, the five-section navigation, data-request integrity, documentation presence, synthetic quarantine/calibration, and synthetic base-model quarantine.
- `reports/HIMPIL_phase_1_8_report.md` - consolidated Phase 1-8 write-up, extended with a P9 real-data alignment addendum.
- `README_WORKPLAN.md` — living task list, decisions, blockers, and update log.
- `reports/tables/feasibility_report.md` — why real supervised learning is blocked.

---

## 5. Repository map

```text
HIMPIL/
    data/
        raw/                    # working copies of the eight workbooks + source documents
        processed/              # real cleaned CSVs and evidence tables
        outputs/                # real guard statuses; no real fish-kill model output
        synthetic/              # QUARANTINED base/, base_model/, gap_fill/, and prototype
            base/               # 15 real labels, 2016-2025, daily synthetic values
            base_model/         # synthetic event overlay, labels, predictions, manifest
            gap_fill/           # synthetic gap-filled database, audit CSVs, readiness checks
    datasets/                   # untouched original workbooks
    models/
        synthetic/              # QUARANTINED synthetic model artifacts
            base_model/         # event-overlay models; synthetic only
            gap_filled/         # gap-filled 24/48/72-hour models
            presentation/       # five-input demo; synthetic only
        # models/model.joblib must remain absent
    python/
        common.py
        inspect_sources.py
        inspect_data.py
        extract_incidents.py
        clean_data.py
        match_environmental_data.py
        prepare_labels.py
        real_trend.py           # real descriptive annual trend model
        train_real_trend.py     # reproduction entry point
        train_model.py          # real fish-kill guard; expected to refuse
        evaluate_model.py       # real fish-kill guard; expected to refuse
        build_dashboard_data.py
        check_lake_coverage.py
    r/
        install_packages.R
        exploratory_analysis.R
        environmental_trends.R
        model_evaluation.R
    sandbox/
        README.md
        synthetic/              # base generator, base-model trainer, presentation demo, prototype
    dashboard/
        src/App.tsx
        src/index.css
        src/data/dashboard.json
        public/figures/
        package.json
        vite.config.ts
    reports/
        HIMPIL_phase_1_8_report.md
        data_requests/          # requests, letters, matrix, access log, permissions
        figures/
        tables/                 # real, synthetic-base, and synthetic-prototype tables
    tests/
        test_pipeline.py
    requirements.txt
    README.md
    README_WORKPLAN.md
```

### How to tell real from synthetic

| Question | Real evidence | Synthetic base dataset | Synthetic base model | Synthetic gap-fill | Synthetic model prototype |
|---|---|---|---|---|---|
| Where are the rows? | `data/processed/` | `data/synthetic/base/` | `data/synthetic/base_model/` | `data/synthetic/gap_fill/` | `data/synthetic/synthetic_*` |
| Where is the model? | Descriptive trend summary in `reports/tables/real_trend_model.json`; `models/model.joblib` must remain absent | No model is trained | `models/synthetic/base_model/*.joblib` | `models/synthetic/gap_filled/*.joblib` | `models/synthetic/*.joblib` |
| Where are labels? | `data/processed/labeling_summary.csv`, `modeling_dataset.csv` | None | `synthetic_events.csv`, `synthetic_modeling_dataset.csv` | `himpil_synthetic_complete.sqlite` (`incident_reports`, `modeling_dataset`) | `data/synthetic/synthetic_modeling_dataset.csv` |
| Where is it presented? | `dashboard/` and real `reports/` | `data/synthetic/base/` and `reports/tables/synthetic_base_*` | `reports/tables/synthetic_base_model_*`, `synthetic_lead_time_policy_*`, and `synthetic_presentation_model_*` | `dashboard/src/data/syntheticDemo.json` and `reports/tables/synthetic_gap_fill_*` | `sandbox/synthetic/` and `reports/tables/synthetic_prototype_*` |
| Marker | Source-backed rows and explicit blanks | `data_origin = synthetic_base_v1` | `data_origin = synthetic_base_v1_event_overlay` | `data_origin = synthetic_gap_fill_v1` | `data_origin = synthetic_simulation` |
| Claim status | Evidence, with limitations | Synthetic only | Synthetic only | Synthetic only | Synthetic only |

If a file does not have an obvious marker, stop and inspect it before using it.

---

## 6. Quick start

### 6.1 Python setup

Tested with Python 3.14.4.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If PowerShell blocks activation, keep calling `.\.venv\Scripts\python.exe` directly.

### 6.2 Run the real-data pipeline

Run from the project root in this order:

```powershell
.\.venv\Scripts\python.exe python\inspect_sources.py
.\.venv\Scripts\python.exe python\inspect_data.py
.\.venv\Scripts\python.exe python\extract_incidents.py
.\.venv\Scripts\python.exe python\clean_data.py
.\.venv\Scripts\python.exe python\match_environmental_data.py
.\.venv\Scripts\python.exe python\prepare_labels.py
.\.venv\Scripts\python.exe python\train_real_trend.py
.\.venv\Scripts\python.exe python\train_model.py
.\.venv\Scripts\python.exe python\evaluate_model.py
```

`train_real_trend.py` fits the real **descriptive annual trend model** and writes the model summary, metrics, model card, and alignment report to `reports/tables/`. It does not create a fish-kill model, labels, risk score, or `models/model.joblib`.

`train_model.py` and `evaluate_model.py` are **guards for the real fish-kill model**. They are expected to exit with code `2` and write explicit refusal reports. This is a scientific control, not an installation error. They refuse because there is no real labelled fish-kill dataset and no credible prediction window.

### 6.3 Build the synthetic base dataset

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\build_base_dataset.py
```

This writes only to `data/synthetic/base/` and the `reports/tables/synthetic_base_*` files. It reads the real processed inputs but does not modify `data/processed/`, `models/model.joblib`, or the dashboard.

### 6.4 Train the synthetic base model

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\train_base_model.py
```

This writes only to `data/synthetic/base_model/`, `models/synthetic/base_model/`, and `reports/tables/synthetic_base_model_*` plus the base-model card. It does not modify the base dataset, `data/processed/`, `models/model.joblib`, or the dashboard.

### 6.5 Run the synthetic model prototype

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\run_prototype.py
```

This writes only to `data/synthetic/synthetic_*`, `models/synthetic/`, and `reports/tables/synthetic_prototype_*` plus the model card. It does not touch `data/processed/`, `models/model.joblib`, or the dashboard.

### 6.6 Build and run the dashboard

```powershell
.\.venv\Scripts\python.exe python\build_dashboard_data.py
cd dashboard
npm install
npm run dev
```

Open the local URL printed by Vite (normally <http://127.0.0.1:5173>). For a production build:

```powershell
cd dashboard
npm run build
npm run preview
```

Navigation uses direct hash routes: `#overview`, `#water`, `#evidence`, `#model`, `#sources`.

### 6.7 Run the R analysis

R 4.6.1 is installed at `C:\Program Files\R\R-4.6.1`. Install the project packages once:

```powershell
& "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" r\install_packages.R
```

Run the analysis from the project root:

```powershell
& "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" r\exploratory_analysis.R
& "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" r\environmental_trends.R
& "C:\Program Files\R\R-4.6.1\bin\Rscript.exe" r\model_evaluation.R
```

R reads documented CSVs, not the Excel source files. Its outputs are `reports/tables/r_*.csv`, `r_*.md`, and `reports/figures/fig_*.png`. It writes an explicit not-available model-evaluation status; it does not fit a model.

### 6.8 Run the tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The tests are contract tests. They do not test a real-data model; they verify that the evidence limits, blocked guards, dashboard state, data-request records, synthetic quarantine, synthetic-base calibration, and synthetic base-model quarantine remain intact.

---

## 7. Real-data pipeline details

| Script | Main inputs | Main outputs |
|---|---|---|
| `inspect_sources.py` | All 14 source files | `source_inventory.csv`, `source_manifest.md`, text extracts |
| `inspect_data.py` | Eight Excel workbooks | `dataset_inventory.csv`, `data_quality_report.csv`, `station_inventory.csv` |
| `extract_incidents.py` | PDFs, proposal DOCX files, archived 2019 article | `historical_fish_kill_events.csv`, evidence audit, context measurements |
| `clean_data.py` | Eight Excel workbooks | Long and wide water-quality, rainfall, wind, registry, and coverage CSVs |
| `match_environmental_data.py` | Event and cleaned environmental CSVs | Matching audit and context table |
| `prepare_labels.py` | Events, matches, station coverage | Readiness checks, blocked label specification, empty modelling schema |
| `train_real_trend.py` | `water_quality_lake_annual.csv` | `real_trend_model.json`, `real_trend_model_metrics.csv`, model card, and alignment report; descriptive annual trend only |
| `train_model.py` | `modeling_dataset.csv` | `training_status.csv`, guard report; no real fish-kill model |
| `evaluate_model.py` | Real fish-kill model and held-out predictions | `evaluation_status.csv`, guard report; no fish-kill metrics |
| `build_dashboard_data.py` | Processed CSVs, R figures, guard statuses | `dashboard/src/data/dashboard.json` and dashboard figure copies |

The real fish-kill modelling schema is header-only. `data/outputs/training_status.csv` and `evaluation_status.csv` record the refusal checks. The descriptive annual trend model writes only summary JSON, CSV, and markdown reports; it does not create a fish-kill model artifact.

---

## 8. Synthetic datasets and prototype details

### 8.1 Synthetic base dataset

The base dataset is generated by `sandbox/synthetic/build_base_dataset.py` and written to `data/synthetic/base/`. It is the closest synthetic stand-in for the real schema:

- 15 real lake station labels, 2016–2025;
- 54,795 daily station-days across six water-quality variables;
- 10,959 daily weather rows across three synthetic weather zones;
- 900 annual station-year-variable anchors, split into real values, 2025 values with unverified completeness, and synthetic imputations;
- a SQLite database with a long-format view, plus CSV exports and a data dictionary.

The daily values are calibrated to the real annual anchors. The calibration audit is `reports/tables/synthetic_base_calibration.csv`; the maximum absolute annual-mean error is below `0.001` in the current build. This is a property of the generator, not evidence that the synthetic series are realistic in every respect.

What it does **not** contain: fish-kill labels, real event dates, station coordinates, model metrics, risk scores, or advisories.

### 8.2 Synthetic base model

The base model is generated by `sandbox/synthetic/train_base_model.py` and written to `data/synthetic/base_model/`. It is a **separate event-overlay exercise**, not a change to the base dataset.

- 20 synthetic event periods and 10 high-stress no-event periods over 2016–2025.
- A four-day pre-event ramp, three-day event, and five-day recovery.
- 54,795 panel rows, of which 53,950 are model-eligible.
- Chronological split: train before 2023, validation 2023, test 2024–2025.
- Majority-class, logistic-regression, and random-forest models for 24/48/72-hour targets.
- Held-out test: 24h F1 `0.625` / PR-AUC `0.568`; 48h F1 `0.748` / PR-AUC `0.957`; 72h F1 `0.797` / PR-AUC `0.947`.
- All four synthetic test events were flagged by at least one 24-hour alert.

The scores are optimistic by construction because the event effect is injected into the same variables used as features. The 24-hour model’s false positives are mostly early detections 2–3 days before events, which the 24-hour label counts as negative. That is a **label-timing problem**, not evidence of real predictability. The test set has only four synthetic event periods and 20 positive 24-hour rows. The event overlay also changes the affected station-years’ annual means, so the base calibration audit does not apply to the overlay.

Outputs:

| Output | Path |
|---|---|
| Synthetic events | `data/synthetic/base_model/synthetic_events.csv` |
| Event-overlay panel | `data/synthetic/base_model/synthetic_modeling_dataset.csv` |
| Test predictions | `data/synthetic/base_model/synthetic_test_predictions.csv` |
| Manifest | `data/synthetic/base_model/manifest.json` |
| Models | `models/synthetic/base_model/*.joblib` |
| Report | `reports/tables/synthetic_base_model_report.md` |
| Model card | `reports/tables/synthetic_base_model_card.md` |
| Metrics | `reports/tables/synthetic_base_model_metrics.csv` |
| Diagnostics | `reports/tables/synthetic_base_model_diagnostics.csv` |
| Event detection | `reports/tables/synthetic_base_event_detection.csv` |
| Lead-time policy report | `reports/tables/synthetic_lead_time_policy_report.md` |
| Lead-time policy comparison | `reports/tables/synthetic_lead_time_policy.csv` |
| Lead-time event detail | `reports/tables/synthetic_lead_time_events.csv` |
| Gaps and to-do | `reports/tables/system_gaps_and_todo.md` |

The lead-time policy analysis is a **post hoc, simulation-only** addendum to the base model. It does not change the model, does not add a validated warning rule, and is not connected to the evidence dashboard.

### 8.3 Generic model prototype

#### What it demonstrates

- A reproducible generator with a fixed seed.
- Station-day weather and water-quality variables.
- Known simulated events and high-stress no-event periods.
- Backward-looking lag and rolling features.
- 24-, 48-, and 72-hour labels.
- Chronological train/validation/test partitions.
- Rare-event metrics: precision, recall, F1, PR-AUC, ROC-AUC, Brier score, confusion matrix.
- Event-level detection at a 0.50 threshold.
- A model card and a quarantine manifest.

#### What it does not demonstrate

- Real Laguna de Bay fish-kill risk.
- Real station, zone, date, event, or measurement behavior.
- A real 24/48/72-hour forecast.
- Real fish-kill model performance or real fish-kill feature importance.
- That the Section 6 gate has passed.
- That a warning, advisory, or SMS should be issued.

#### Outputs

| Output | Path |
|---|---|
| Synthetic panel | `data/synthetic/synthetic_station_day.csv` |
| Event truth table | `data/synthetic/synthetic_event_periods.csv` |
| Modelling table | `data/synthetic/synthetic_modeling_dataset.csv` |
| Test predictions | `data/synthetic/synthetic_test_predictions.csv` |
| Manifest | `data/synthetic/synthetic_manifest.json` |
| Models | `models/synthetic/*.joblib` |
| Report | `reports/tables/synthetic_prototype_report.md` |
| Model card | `reports/tables/synthetic_model_card.md` |
| Metrics | `reports/tables/synthetic_prototype_metrics.csv` |
| Feature importance | `reports/tables/synthetic_feature_importance.csv` |
| Event detection | `reports/tables/synthetic_event_detection.csv` |

#### How to use it safely in a team demo

Use it to explain **how the pipeline will work**, not **what Laguna de Bay will do**. Every slide, screenshot, or spoken claim must carry a clear synthetic label. Do not put a synthetic probability on a map of Laguna de Bay. Do not show it next to the real dashboard without a visual quarantine boundary.

The synthetic report’s metrics are properties of the simulation. A high score means the generator put a learnable signal in the data; it does not mean the real system works.

---

### 8.4 Synthetic presentation model (five inputs)

The presentation demo is trained by `sandbox/synthetic/train_presentation_model.py` on the synthetic 72-hour event label, using only the five inputs from the team's illustrative table. It is deliberately simpler than the full synthetic base model.

| Split | Precision | Recall | F1 | PR-AUC | Alerts | Events detected |
|---|---:|---:|---:|---:|---:|---:|
| Validation (2023) | 0.8571 | 0.6000 | 0.7059 | 0.7451 | 21 | 2/2 |
| Test (2024-2025) | 0.4032 | 0.8333 | 0.5435 | 0.6947 | 124 | 4/4 |

The test alerts split into 50 true positives, 74 false positives, and 10 missed positive rows. Feature importance is dominated by dissolved oxygen (`0.6262`) and water temperature (`0.2494`), followed by pH (`0.0462`), wind (`0.0397`), and rainfall (`0.0385`). That pattern is built into the synthetic event effect; it is not a real Laguna de Bay finding.

Run the demo:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\train_presentation_model.py
.\.venv\Scripts\python.exe sandbox\synthetic\predict_presentation.py --do 4.8 --temp 30 --ph 7.0 --rain 15 --wind 8
```

The second command prints a simulated 72-hour probability and an illustrative Low/Medium/High band. The bands are not validated thresholds, and the model is not connected to the evidence dashboard. The full report, including the six fictional example rows and a five-minute presentation script, is [`reports/tables/synthetic_presentation_model_report.md`](reports/tables/synthetic_presentation_model_report.md).

For a browser-based version:

```powershell
.\.venv\Scripts\python.exe sandbox\presentation_app\app.py
```

Open `http://127.0.0.1:8000`. The app is local-only and writes no data. It is deliberately separate from the evidence dashboard.

## 9. Dashboard details

The interface is a five-section decision-support dashboard built on the editorial research-brief system. The supplied `himpil-ui.zip` shell is used as the application frame after removing its unused Figma deployment configuration.

- The persistent top notice, hero status panel, and header pill keep **“risk assessment unavailable”** visible.
- The Overview opens with a dark status hero. It shows the real fish-kill model, verified-event, and dated-observation counts, then a four-card KPI strip.
- The Overview uses year chips, a left rail for variable and station filters, and a station-year completeness heatmap. A hatched or blank cell means the variable was not reported; it never means zero.
- The annual trend follows the selected variable. The right rail shows the readiness gate, data-request status, the one reported event, and “The evidence boundary.”
- The old decorative lake map, disabled risk controls, advisory placeholder, settings page, and empty performance widgets remain removed.
- No coordinates were supplied; the interface does not assign events to stations or lake zones.
- The production build was checked with headless Edge at 1440 px, 1024 px, and a narrow width: the three-column layout collapses cleanly, the heatmap scrolls inside its panel, and there is no page-level horizontal overflow.
- The interface uses three supporting R figures. The station-level dissolved-oxygen plate remains in `reports/figures/` for the full report and is not duplicated in the interface.

`dashboard.json` is built from real processed CSVs, guard statuses, and the data-request access log only; it does not read `data/synthetic/` or `models/synthetic/`. The separate `syntheticDemo.json` powers the labeled gap-filled synthetic training-run panel on the Model page. No synthetic rows are loaded.

---

## 10. Data request status

The package is in [`reports/data_requests/`](reports/data_requests/README.md).

| Request | Status | Notes |
|---|---|---|
| `LLDA-INC-01` | `acknowledged` | LLDA asked for professor approval letters; no files received; outreach paused by team decision |
| Other eight requests | `planned` | Not yet sent; no data or permissions recorded |

**Outreach is paused (23 October 2026).** `LLDA-INC-01` is not closed and has not been received. The other eight requests remain `planned`. Reopen the package only if the team decides to resume external data acquisition; do not send a letter or change a status merely to keep the plan moving.

The submitted LLDA request text is preserved in [`submissions/LLDA_incident_request.md`](reports/data_requests/submissions/LLDA_incident_request.md). The package does not claim that any agency holds the requested data.

When outreach resumes, prepare the signed professor/adviser letter on university letterhead before responding to LLDA. For the remaining requests, complete the bracketed names, institution, adviser, and contact details; confirm the official channel; and have the adviser review the letter. The PAGASA student route requires its current CADS-02A form and supporting documents; the package links to the official page.

A file is not accepted until its hash, fields, units, QA flags, station identity, and permission conditions are recorded. A request being sent is not the same as data being received.

Named role assignments, the faculty adviser, data custodian, and reviewer fields remain blank in [`reports/data_requests/roles_and_decisions.md`](reports/data_requests/roles_and_decisions.md). They must be completed before the relevant submission or defense.

---

## 11. The real model-readiness gate

No real **fish-kill** model training starts until **all** of the following are true and documented. The descriptive annual trend model is outside this gate because it does not predict fish kills.

- [ ] At least three independent event periods are available, spanning multiple years, with exact dates.
- [ ] At least one event period can be held out chronologically for testing.
- [ ] Dated water-quality observations exist at daily or sub-daily resolution before each event.
- [ ] Weather observations resolve to the required lead time.
- [ ] Every event can be assigned to a station or documented lake zone.
- [ ] A station-to-zone crosswalk is sourced and versioned.
- [ ] Positive labels and credible negative windows are both generated.
- [ ] Negative windows are backed by an incident-reporting completeness record.
- [ ] No post-event measurement is used as a predictor.
- [ ] Class counts are sufficient to estimate the intended metrics.
- [ ] Leakage tests pass.
- [ ] The data dictionary and versioned dataset are released.

If any item fails, the output remains **“risk assessment unavailable.”**

None of the four synthetic artifacts - the base dataset, the base model, the gap-filled database/model, or the generic prototype - satisfies any of these items. They are separate sandboxes, not a substitute gate.

### What is needed before real supervised training

1. LLDA/BFAR dated fish-kill incident log with site, zone, start/end, losses, and investigation status.
2. LLDA dated water-quality observations at daily or finer resolution.
3. PAGASA daily/hourly rainfall, wind, and air temperature linked to documented stations.
4. Station coordinates and an authoritative lake-zone boundary map.
5. A reporting-completeness record covering negative windows.
6. At least two independent event periods for a chronological split, and preferably many more for credible held-out evaluation.

After those exist, the target and split must be re-approved, real labels generated, and only then may a baseline, Decision Tree, or Random Forest be fitted. The existing guard scripts will continue to refuse training until the checks pass.

---

## 12. What the team should do next

### First 30 minutes with this repository

1. Read this README and [`README_WORKPLAN.md`](README_WORKPLAN.md) Sections 1, 6, and 11.
2. Run the test suite and confirm 17/17 pass.
3. Open the real dashboard and find the **“risk assessment unavailable”** state.
4. Read the synthetic base README and data dictionary, then run the base generator and base-model trainer. Run the five-input presentation demo and read its report. Then open the gap-filled database README and the two synthetic gap-fill reports, and run the database builder and trainer if you need to regenerate them.
5. Read the data-request package and note that no data or permission has been received.
6. Use the P7 demo for a team walkthrough, or review the **Gap-filled synthetic training run** panel on the Model page. Paper work is paused unless explicitly requested.

### Current priority (24 October 2026)

External data outreach is paused. Do not send the LLDA letter for now, and do not mark `LLDA-INC-01` received, complete, or closed. The request remains `acknowledged` with no files and no permissions.

The dashboard refresh (P5), the first synthetic learning experiment (P6), the five-input presentation demo (P7), the real-data alignment (P9), and the gap-filled database and training run (P10) are complete. Paper work is paused by user request. Focus on the work that can be learned and finished with what is already here:

1. Use the five-input presentation demo for the team demo. Open [`reports/tables/synthetic_presentation_model_report.md`](reports/tables/synthetic_presentation_model_report.md) and follow its five-minute script, or run the local app at [`sandbox/presentation_app/app.py`](sandbox/presentation_app/app.py). Do **not** present the demo bands as real risk levels.
2. Review the **Gap-filled synthetic training run** panel on the Model page and the two gap-fill reports: [`reports/tables/synthetic_gap_fill_database_report.md`](reports/tables/synthetic_gap_fill_database_report.md) and [`reports/tables/synthetic_gap_filled_model_report.md`](reports/tables/synthetic_gap_filled_model_report.md). Keep the panel separate from the real risk state.
3. Optionally run another synthetic experiment, such as probability calibration or a model trained directly against a 72-hour label. Keep every result labeled **synthetic only**.
4. Extend the refreshed dashboard only with real fields and counts. A denser decision-support layout is fine; invented risk numbers are not.

### If and when outreach resumes

Prepare the signed professor/adviser approval letter on university letterhead, send it to LLDA through the official channel, and record the actual date, recipient, and channel in `data_access_log.csv`. Then follow up on `LLDA-INC-01`.

Do not mark `LLDA-INC-01` as received or complete until files arrive and are inspected. Do not mark permissions granted until terms are recorded.

### Parallel work that is safe

- Improve the synthetic base dataset's calibration checks without loading synthetic rows into the real evidence bundle.
- Improve the synthetic base model's event/label design and diagnostics without loading synthetic rows into the real evidence bundle.
- Run additional synthetic model experiments (for example, calibration or a model trained directly against a 72-hour label) and document them as synthetic only.
- Use the five-input presentation demo in a separate sandbox demo; never add its outputs or bands to the evidence dashboard.
- Maintain the refreshed evidence dashboard (P5 complete) using only real coverage, readiness, event, source, and request counts.
- Improve the synthetic prototype’s code quality without connecting it to the real dashboard.
- Add tests for synthetic quarantine, base calibration, and README guidance.
- Review the real dashboard for clarity and responsive behavior.
- Prepare a defense narrative that separates “what we built” from “what the data cannot support.”
- Draft the model card and evaluation plan for the future real **fish-kill** model, using the synthetic prototype as a dry run. A separate descriptive annual trend model card already exists at `reports/tables/real_trend_model_card.md`.

### Work that is not safe

- Training on the current real data.
- Quoting synthetic metrics as real performance.
- Presenting the five-input demo bands as real risk levels or an advisory.
- Adding a real risk score, zone risk map, or advisory.
- Filling station gaps with guessed coordinates or zones.
- Treating the absence of a news report as a confirmed non-event.
- Claiming a request was sent or data received without a record.

---

## 13. Known data limitations

- LLDA water quality is published as **annual station summaries**. The aggregation method is not stated.
- PAGASA rainfall and wind are **monthly station summaries**. 2025 is marked provisional and is incomplete: seven stations have all 12 months, while the rest have January–June values only. The source says remaining synoptic data are still undergoing verification.
- No supplied file provides station coordinates.
- Only 5 of 15 lake station labels contain an explicit bay name. The rest have no zone label.
- There are 59 distinct water-quality station labels (15 lake, 44 tributary). pH/temperature omit four tributary sites; nutrients/BOD use “Angono” where other tables use “Angono River”. They are not merged without a documented crosswalk.
- `**` means a station is no longer monitoring; `…` means no data; `...` is undefined in most notes. All are retained as missing flags, never zero.
- Water temperature is missing for 2017 for the nine long-running lake stations.
- A DO workbook note says “2014 water quality data is only from January to June”. This is likely a typo for 2024 but must be confirmed with LLDA before treating 2024 as a complete year.
- The 2019 article is one secondary source. Its cause attribution is an interview statement, not a formal investigation finding.
- Absence of a published fish-kill report cannot be interpreted as a confirmed non-event.
- The exploratory R trend tests are descriptive. Four of 15 lake stations had a Benjamini–Hochberg-adjusted negative DO slope below 0.05, based on at most 10 annual points per station. This does not establish causation, a lake-wide decline, or a fish-kill mechanism.
- The synthetic base model’s metrics are an artifact of an injected event process. Its 24-hour false positives are mostly early detections 2–3 days before synthetic events, which the 24-hour label counts as negative. This does not establish either real predictability or a real lead time.

---

## 14. Frequently asked questions

**Is there a trained model?**  
No real-data fish-kill model. There is a synthetic base model in `models/synthetic/base_model/`, a synthetic gap-filled database and 24/48/72-hour models in `data/synthetic/gap_fill/` and `models/synthetic/gap_filled/`, and a separate generic prototype in `models/synthetic/`. All are quarantined synthetic-only artifacts.

**Can we train a model on the synthetic base dataset?**  
Yes, but only as a clearly labeled software exercise. The base model does this by injecting synthetic events into a copy of the base panel. It is not a HIMPIL model, does not use real labels, and does not satisfy the Section 6 gate.

**Can we show the synthetic metrics in the defense?**  
Only as a software demonstration, with an explicit synthetic label. Never as HIMPIL?s real performance.

**Why not train on the annual data?**  
Annual station summaries cannot support a 24/48/72-hour prediction. There is one reported event, no pre-event observation, no credible negatives, and no station-to-zone mapping.

**Why not use the 2019 sample as a predictor?**  
It was collected during the event, on 29 May 2019. Using it as a pre-event feature would be leakage.

**Can we treat a year with no news report as a negative?**  
No. Absence of a published report is not evidence that reporting was complete. A negative label needs a reporting-completeness record.

**What is the fastest honest path to a real prototype?**  
Get daily observations, station metadata, multiple verified events, reporting completeness, and a zone crosswalk. Then generate real labels and pass the gate. The data requests are the current path.

**What if the data never arrive?**  
The workplan says the scope must be explicitly reframed as a feasibility study and the title/abstract changed. The evidence dashboard, synthetic base dataset, base model, gap-filled database/model, and prototype are already useful for that outcome, but the original operational claim must be withdrawn.

---

## 15. Definition of done for the original goal

The original goal is met only when all of the following exist:

- [ ] A validated, labelled dataset at the required temporal and spatial resolution.
- [ ] A trained real-data model with a documented chronological evaluation.
- [ ] Performance metrics including precision, recall, F1, PR-AUC, and calibration.
- [ ] Feature-importance or explainability results that answer Research Question 2.
- [ ] Zone-level risk output with a model version and data timestamp.
- [ ] Evidence-based warnings and preparation advice, with uncertainty stated.
- [ ] A user test showing that fish-pen operators, fisherfolk, or LGU users can understand the warning.
- [ ] A model card, advisory protocol, and limitations statement.
- [ ] All tests pass and a clean reproduction command exists.

None of the four synthetic artifacts checks any of these boxes. They are development aids.

**If the study is reframed (23 October 2026):** the operational definition above no longer applies. A feasibility-and-simulation paper must say plainly that the original goal was not met, present the evidence dashboard, the descriptive annual trend estimate, and the synthetic pipeline as separate contributions, and keep the Section 11 gate visible. It must not claim a real risk level, real fish-kill model performance, or a working warning service.

---

## 16. Consolidated report and key links

- [`README_WORKPLAN.md`](README_WORKPLAN.md) — living source of truth.
- [`reports/HIMPIL_paper_revision_outline.md`](reports/HIMPIL_paper_revision_outline.md) — paper structure, claim rewrites, and result placement.
- [`reports/HIMPIL_paper_draft.md`](reports/HIMPIL_paper_draft.md) - drafted Sections 3-7: evidence audit, methods, results, discussion, limitations, conclusion, and provisional references.
- [`reports/HIMPIL_phase_1_8_report.md`](reports/HIMPIL_phase_1_8_report.md) - consolidated Phase 1-8 report, extended with a P9 real-data alignment addendum.
- [`reports/tables/feasibility_report.md`](reports/tables/feasibility_report.md) — real-data feasibility gate.
- [`reports/tables/matching_report.md`](reports/tables/matching_report.md) — event-to-environment matching audit.
- [`reports/tables/source_manifest.md`](reports/tables/source_manifest.md) — 14-source register.
- [`reports/data_requests/README.md`](reports/data_requests/README.md) — request package and current status.
- [`data/synthetic/base/README.md`](data/synthetic/base/README.md) — synthetic base dataset.
- [`reports/tables/synthetic_base_report.md`](reports/tables/synthetic_base_report.md) — base dataset report.
- [`data/synthetic/base_model/README.md`](data/synthetic/base_model/README.md) — base-model data rules.
- [`reports/tables/synthetic_base_model_report.md`](reports/tables/synthetic_base_model_report.md) — base-model report.
- [`reports/tables/synthetic_base_model_card.md`](reports/tables/synthetic_base_model_card.md) — base-model card.
- [`reports/tables/synthetic_presentation_model_report.md`](reports/tables/synthetic_presentation_model_report.md) — five-input demo report.
- [`sandbox/presentation_app/README.md`](sandbox/presentation_app/README.md) — local interactive demo app.
- [`reports/tables/system_gaps_and_todo.md`](reports/tables/system_gaps_and_todo.md) — system gaps and prioritized to-do list.
- [`sandbox/synthetic/README.md`](sandbox/synthetic/README.md) — synthetic sandbox for all four artifacts.
- [`reports/tables/synthetic_prototype_report.md`](reports/tables/synthetic_prototype_report.md) — model-demo report.
- [`reports/tables/synthetic_model_card.md`](reports/tables/synthetic_model_card.md) — synthetic model card.

**Bottom line for the team:** the real evidence dashboard is honest about what the data cannot support. The descriptive annual trend model is a real but narrow result, not a fish-kill predictor. The synthetic base dataset, base model, gap-filled database/model, presentation demo, and prototype are safe places to test the software. None of them is a working early-warning system, and the project must not be presented as one until the real fish-kill model gate passes.
