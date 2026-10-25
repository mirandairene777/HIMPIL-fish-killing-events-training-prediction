# HIMPIL Living Workplan

**Last updated:** 2026-10-24  
**Current phase:** External data outreach is paused by team decision. The active work includes simulation-based learning, the dashboard refresh (complete, including the real Tanay rainfall context), the lead-time experiment (complete), the five-input presentation demo (complete), the real-data alignment and descriptive annual trend model (complete, P9), and the synthetic gap-filled database plus 24/48/72-hour training run (complete, P10). Paper work is paused by user request. Synthetic artifacts remain quarantined; the real **fish-kill** model is still blocked.  
**Current milestone:** M1 paused; P5 complete (including P5-5); P6 first experiment complete (lead-time policy); P7 presentation demo complete; P8 paper revision paused by user request; P9 real-data alignment complete (descriptive annual trend model; real 72-hour fish-kill model still blocked); P10 synthetic gap-filled database and training run complete  
**Overall status:** The original ML early-warning goal is **not met**. The delivered system is a scientifically defensible evidence dashboard, a descriptive annual water-quality trend model, and a feasibility study, plus a quarantined synthetic base dataset, a separate synthetic base model, a gap-filled synthetic database and trained model, a five-input presentation demo, and a generic synthetic prototype. All synthetic artifacts remain separate from the real evidence bundle.

> **This file is the single source of truth for project work.**
> Update it before starting a task and again after finishing it. Record the date, what changed, the evidence, the result, and the next action. Do not mark a task complete without an artifact or command output to point to.

---

## 1. Original goal and current verdict

The concept document `data/raw/source_documents/HIMPIL.docx` (source S12) states:

> “Develop HIMPIL, a machine learning-based early warning system that uses data from the weather and water quality to predict possible fish kill events and other risks in Laguna de Bay.”
>
> “The system will show risk levels, warnings, how to prepare, and suggested actions to do.”

Its expected output is:

> “A prototype that will show fish kill risk events by certain zones with simple warnings and suggested actions.”

### Verdict

**The original operational goal is not met.**

What exists now is a defensible **Phase 1–9 foundation**: source audit, cleaned annual/monthly data, descriptive analysis, one reported event, a feasibility gate, a working evidence dashboard, and a descriptive annual trend model. It does not provide:

- a trained **real-data fish-kill** model;
- a real fish-kill risk level;
- a real zone-level risk output;
- 24-, 48-, or 72-hour predictions;
- validated warnings or preparation advice;
- SMS notifications;
- a beneficiary usability evaluation;
- fish-kill model accuracy or factor-importance results.

The descriptive annual trend model is real, but it is not a fish-kill model and does not change the verdict. The project must not be presented as a working early-warning system until the gate in Section 6 is passed.

A synthetic base dataset now exists in `data/synthetic/base/`, a separate event-overlay model exists in `data/synthetic/base_model/` and `models/synthetic/base_model/`, a synthetic gap-filled database and 24/48/72-hour models exist in `data/synthetic/gap_fill/` and `models/synthetic/gap_filled/`, and a generic model prototype exists in `sandbox/synthetic/`. All four are software demonstrations only. They do not provide any of the missing real-data items above, and none can be used as a real model or evidence.

### Working scope decision

Provisional decision: **pursue the original goal only by closing the data and validation gaps in this plan**. If the required data cannot be obtained, the scope must be explicitly reframed as a feasibility study and the title/abstract changed accordingly. A fake real-world model, invented real risk score, or real labels presented without evidence is not an acceptable fallback.

**Synthetic-only exception (D-006):** quarantined synthetic artifacts are permitted for software demonstration, testing, onboarding, and UI discussion. They must remain under `sandbox/synthetic/`, `data/synthetic/`, and `models/synthetic/`; every artifact must carry a clear synthetic label in its manifest or report, while UI panels use one compact **Synthetic gap-fill** badge; they must not feed the evidence dashboard; and they cannot satisfy the Section 6 gate. This exception does not change the verdict on the original goal.

**Synthetic base dataset scope (D-007):** the requested base dataset may use the real 15 lake station labels, 2016-2025 calendar, six variables, units, and real annual station-year anchors for calibration, provided every daily value is marked `data_origin = synthetic_base_v1`, missing annual cells are flagged, no fish-kill labels or real event dates are added, and the dataset remains separate from `data/processed/` and the evidence dashboard.

**Synthetic base model scope (D-008):** the team may train a model on a **separate event-overlay copy** of the synthetic base panel for software demonstration only. The overlay may inject synthetic events and stress-only periods, but it must remain in `data/synthetic/base_model/` and `models/synthetic/base_model/`, every row must be marked `data_origin = synthetic_base_v1_event_overlay`, and the metrics must not be described as real performance. The base dataset itself must remain unchanged.

**Pause decision (D-009):** on 2026-10-23 the team paused external data acquisition, including the LLDA follow-up, to focus on simulation-based learning, dashboard work, and paper revision. `LLDA-INC-01` remains `acknowledged`; nothing is marked received, granted, or closed. The Section 6 gate is unchanged, and the original goal remains unmet until every gate item passes on real data.

---

## 2. What is already delivered

| Area | Delivered state | Evidence |
|---|---|---|
| Source audit | 14 sources inspected, hashed, and documented | `reports/tables/source_manifest.md`, `reports/tables/source_inventory.csv` |
| Water quality | 3,400 long rows; 15 lake stations; 150 station-years; 111 complete across six variables | `data/processed/water_quality_long.csv`, `data/processed/water_quality_lake_annual.csv` |
| Weather | 7,008 rainfall rows; 7,260 wind rows | `data/processed/rainfall_monthly.csv`, `data/processed/wind_monthly.csv` |
| Event evidence | 1 accepted report; 0 independently verified events | `data/processed/historical_fish_kill_events.csv`, `data/processed/incident_evidence_audit.csv` |
| Matching audit | 0 usable pre-event predictive matches; 4 during-event context measurements | `reports/tables/matching_report.md` |
| Feasibility | 1 pass, 1 partial, 8 fails across 10 readiness checks | `reports/tables/feasibility_report.md` |
| Real fish-kill model | No real fish-kill model, no real fish-kill labels, no real fish-kill metrics | `data/processed/modeling_dataset.csv` is header-only; `models/model.joblib` is absent |
| Real descriptive trend model | Station fixed-effects annual trend; DO **-0.111861 mg/L/year** (95% CI **-0.141078 to -0.082643**), temperature **+0.056015 °C/year** (95% CI includes zero); descriptive only | `reports/tables/real_trend_model.json`, `real_trend_model_card.md`, `real_data_alignment_report.md` |
| Guards | Training and evaluation scripts refuse with exit code 2 | `data/outputs/training_status.csv`, `data/outputs/evaluation_status.csv` |
| Analysis | R descriptive tables and 13 figures | `reports/tables/r_*.md`, `reports/figures/` |
| Dashboard | Five-section evidence dashboard with a refreshed decision-support Overview; no risk prediction; synthetic data not connected | `dashboard/`, `http://127.0.0.1:4173/` |
| Synthetic base dataset | 15 real labels, 2016-2025, 54,795 daily station-days, 6 variables; 10,959 weather rows; 900 anchors; CSV + SQLite; synthetic only | `data/synthetic/base/`, `reports/tables/synthetic_base_*`, `sandbox/synthetic/build_base_dataset.py` |
| Synthetic base model | 20 synthetic events, 10 stress-only periods, 53,950 model-eligible rows; 24/48/72-hour models, metrics, event detection, diagnostics, model card, report; synthetic only | `data/synthetic/base_model/`, `models/synthetic/base_model/`, `reports/tables/synthetic_base_model_*`, `sandbox/synthetic/train_base_model.py` |
| Synthetic gap-filled database and model | 15 stations; 54,795 station-days; 20 exact-dated events; 1,700 non-event windows; 40 corroboration records; 15 coordinates/zones; 10/10 synthetic checks; 24/48/72-hour models; 72h F1 0.797; synthetic only | `data/synthetic/gap_fill/`, `models/synthetic/gap_filled/`, `reports/tables/synthetic_gap_fill_*`, `sandbox/synthetic/build_gap_filled_database.py`, `sandbox/synthetic/train_gap_filled_model.py` |
| Synthetic prototype | Quarantined generator, models, metrics, report, and model card; synthetic only | `sandbox/synthetic/`, `data/synthetic/`, `models/synthetic/`, `reports/tables/synthetic_prototype_*` |
| Data requests | 1 acknowledged (`LLDA-INC-01`); 8 planned; 0 data files; 0 permissions recorded | `reports/data_requests/` |
| Tests | 17/17 contract tests pass | `tests/test_pipeline.py` |
| Documentation | Consolidated Phase 1-8 report with P9 addendum, living workplan, and full team README | `reports/HIMPIL_phase_1_8_report.md`, `README_WORKPLAN.md`, `README.md` |

### Known blockers in the current dataset

- LLDA water quality is annual station summaries, not dated daily observations.
- PAGASA weather is monthly station summaries, not daily or sub-daily observations.
- A real 72-hour fish-kill model is not supported: there are zero dated water-quality rows, zero pre-event observations, one reported event, and zero verified negative windows.
- Only one reported fish-kill period exists, and it is not independently verified.
- No pre-event environmental observation exists for that event.
- The 2019 article’s sample was collected during/near the end of the event, not before it.
- No credible negative windows exist because no incident-reporting completeness record was supplied.
- No station coordinates or authoritative station-to-zone crosswalk were supplied.
- Only 5 of 15 lake station labels contain a zone name.
- The DO workbook note saying “2014 water quality data is only from January to June” is unresolved and likely refers to 2024.
- PAGASA 2025 data are partial and provisional: seven stations have all 12 months; the rest have January–June values only.

---

## 3. Milestone board

| ID | Milestone | Status | Exit criterion |
|---|---|---|---|
| M0 | Reconcile scope and preserve current evidence | **DONE** | This workplan, current README, and report agree on the delivered state |
| P1 | Clean the repository and professionalize the evidence dashboard | **DONE** | Safe deletions are logged, the build is clean, the five sections are visually coherent, and responsive checks pass |
| P2 | Build a quarantined synthetic prototype for software demonstration | **DONE** | Synthetic generator, chronological models, metrics, model card, report, and quarantine tests exist; every artifact is labeled simulation only |
| P3 | Build a synthetic base dataset on the real station/year/schema frame | **DONE** | 15 real labels, 2016-2025, six variables, weather, 900 anchors, CSV + SQLite, data dictionary, calibration audit, and report exist; every daily value is marked synthetic |
| P4 | Train a quarantined synthetic base model on a separate event overlay | **DONE** | 20 synthetic events, 10 stress-only periods, 24/48/72-hour models, metrics, event detection, diagnostics, model card, report, and quarantine test exist; every row and model is marked simulation only |
| M1 | Secure data that can support validated prediction | **PAUSED — TEAM DECISION (2026-10-23)** | Daily observations, coordinates, multiple event periods, credible negatives, and incident reports are actually in hand |
| P5 | Refresh the evidence dashboard in a denser decision-support visual language | **DONE (2026-10-23; real rainfall extension 2026-10-24)** | The dashboard looks clearer and more usable, uses only real coverage/readiness/provenance numbers, includes the descriptive Tanay rainfall panel, and still says "risk assessment unavailable" |
| P6 | Run and document quarantined synthetic ML learning experiments | **DONE (2026-10-23, one experiment; 72-hour retrain 2026-10-24)** | At least one experiment is reproducible, labeled simulation only, and recorded in the workplan; synthetic rows never enter the real evidence bundle, and the separate Model-page panel is explicitly labeled |
| P7 | Build a five-input synthetic presentation demo for team demos | **DONE (2026-10-24)** | The demo is trained, reproducible, labeled simulation only, and not connected to the evidence dashboard |
| P8 | Revise the concept paper into a feasibility-and-simulation paper | **PAUSED BY USER REQUEST (Sections 3-7 and provisional references complete, 2026-10-24)** | Resume only if explicitly requested; then finish front matter, consistency review, and formatting |
| P9 | Align the system with the real-data resolution and fit the defensible real model | **DONE (2026-10-24)** | A descriptive annual trend model is reproducible, labeled, and separate from the unavailable fish-kill risk state; no fake 72-hour model is trained |
| P10 | Build a synthetic gap-filled database and train the full pipeline end to end | **DONE (2026-10-24)** | 15 coordinates, 15 zone assignments, 20 exact-dated events, 400 pre-event rows, 1,700 negative windows, 40 corroboration records, 15 aggregation rules, 10/10 synthetic checks, 24/48/72-hour models, reports, and dashboard payload exist; real gate remains 2 pass and 8 fail |
| M2 | Rebuild the dataset at the required resolution | **NOT STARTED** | Versioned dataset passes schema, leakage, missingness, and event-mapping checks |
| M3 | Pass or fail the model-readiness gate | **NOT STARTED** | Every gate item in Section 6 has a documented result |
| M4 | Train and evaluate the **real-data** model | **NOT STARTED** | Chronological train/validation/test results and a real-data model card exist |
| M5 | Build zone-level risk and advisory prototype | **NOT STARTED** | Risk output, uncertainty, advisory text, and audit trail exist |
| M6 | Validate with beneficiaries and finalize defense | **NOT STARTED** | Usability results, limitations, and final report are complete |

---

## 4. Full task list

### A. Scope, governance, and data access

- [x] **A1 — Confirm the original goal from `data/raw/source_documents/HIMPIL.docx`.** — DONE — Goal and expected output quoted in Section 1.
- [x] **A2 — Record the gap between the concept goal and the current deliverable.** — DONE — Section 1 verdict.
- [x] **A3 — Establish this living workplan and update protocol.** — DONE — This file.
- [ ] **A4 — Decide whether to pursue new data or formally reframe the study.** — IN PROGRESS — D-009 pauses external acquisition and reframes the paper as a feasibility-and-simulation study for the current scope. The real-data gate stays documented; reframing does not lower it.
- [x] **A5 — Create a data-request package.** — DONE — Nine field-level requests, four ready-to-complete letters, an adviser approval template, a matrix, access log, permissions record, and decision-rights document in `reports/data_requests/`. One LLDA incident request has since been submitted and acknowledged; no data have been received.
- [ ] **A6 — Record data-sharing permissions and ethical constraints.** — PARTIAL — `permissions_and_ethics.md` defines the permission record, privacy rules, retention controls, and publication review. No external permission, agreement, or refusal has been recorded yet.
- [ ] **A7 — Define authors, reviewers, and decision owner for data/model changes.** — PARTIAL — Roles, the authorship/acknowledgement policy, and decision rights are defined in `roles_and_decisions.md`; named assignments and adviser approval are still blank and must be completed before the first request.
- [x] **A8 — Maintain a source/data access log.** — DONE — `data_access_log.csv` tracks all nine requests: one is `acknowledged` and eight are `planned`; no files or permissions are recorded.

### B. Data acquisition

> **Paused under D-009 (2026-10-23).** These tasks remain open and are not cancelled. Do not mark a request sent, received, or granted without a recorded date, recipient, channel, and file inspection. Reopen this section only if the team resumes outreach.

- [x] **B1 — Inspect all currently supplied files.** — DONE — 14 sources documented in `reports/tables/source_manifest.md`.
- [ ] **B2 — Request LLDA daily or sub-daily water-quality observations.** — PAUSED / EXTERNAL — Required fields: timestamp, station ID/name, DO, water temperature, pH, nutrients, BOD, QA flag, unit, method.
- [ ] **B3 — Request LLDA station metadata and coordinates.** — PAUSED / EXTERNAL — Required: latitude, longitude, station status, waterbody/lake zone, station description.
- [ ] **B4 — Request LLDA aggregation and QA/QC rules.** — PAUSED / EXTERNAL — Needed to understand how annual summaries were produced and how flags work.
- [ ] **B5 — Request PAGASA daily weather data.** — PAUSED / EXTERNAL — Required: daily rainfall, air temperature, wind speed, wind direction, station metadata, completeness flags.
- [ ] **B6 — Request fish-kill incident reports and investigation records.** — PAUSED / EXTERNAL — LLDA incident request submitted and acknowledged; LLDA requested professor approval letters. No files received. Outreach paused under D-009. BFAR and LGU sources not yet contacted.
- [ ] **B7 — Build an incident-reporting completeness log.** — PAUSED / EXTERNAL — Needed to justify negative windows. Absence of a news report is not a negative label.
- [ ] **B8 — Request or reconstruct an authoritative station-to-zone crosswalk.** — PAUSED / EXTERNAL — No zone mapping may be guessed from station names alone.
- [ ] **B9 — Check for high-frequency sensor or buoy data.** — PAUSED / EXTERNAL — Prefer timestamped DO and temperature from fixed stations.
- [ ] **B10 — Resolve the 2014/2024 DO workbook note with LLDA.** — PAUSED / EXTERNAL — Do not treat 2024 as complete until confirmed.
- [ ] **B11 — Record every received file with hash, date, source, and restriction.** — NOT STARTED — Add to the source register.

### C. Data engineering

- [x] **C1 — Preserve original source files unchanged.** — DONE — Hash checks in `tests/test_pipeline.py`.
- [x] **C2 — Build current annual/monthly processed tables.** — DONE — See `data/processed/`.
- [x] **C3 — Keep missing values missing; never use zero as a substitute.** — DONE — Tested in `test_missing_measurements_remain_missing`.
- [ ] **C4 — Define the daily observation schema.** — NOT STARTED — `observation_id`, station, timestamp, variable, value, unit, QA flag, source, ingestion date.
- [ ] **C5 — Define the verified incident schema at event, municipality, and station/zone levels.** — PARTIAL — Current 17-column event schema exists, but only one reported event and no verified events.
- [ ] **C6 — Define the negative-window schema.** — NOT STARTED — Must include evidence that reporting was complete for the window, not merely that no article was found.
- [ ] **C7 — Build the station metadata table.** — NOT STARTED — Coordinates, zone, waterbody, active period, source, and coordinate precision.
- [ ] **C8 — Build a documented station-to-zone crosswalk.** — NOT STARTED — Requires official map or source-approved mapping.
- [ ] **C9 — Define temporal alignment rules.** — PARTIAL — Current No post-event leakage rule is tested; daily lead-time rules still need definition.
- [ ] **C10 — Define unit, timezone, and date-precision rules.** — PARTIAL — Current units are documented; daily timestamps and event-time precision still need a formal contract.
- [ ] **C11 — Build a versioned data release process.** — NOT STARTED — Never overwrite a released dataset; record source hashes and processing version.
- [ ] **C12 — Add automated schema and leakage tests for the new dataset.** — NOT STARTED — Must run before any model training.

### D. Analysis and feasibility

- [x] **D1 — Complete descriptive annual water-quality analysis.** — DONE — Python and R outputs.
- [x] **D2 — Complete descriptive monthly rainfall/wind analysis.** — DONE — R outputs.
- [x] **D3 — Complete the current feasibility and label audit.** — DONE — 10 readiness checks, 8 fail.
- [x] **D4 — Audit post-event leakage in the only available event report.** — DONE — 0 usable pre-event matches; 4 during-event context measurements.
- [ ] **D5 — Re-run feasibility after new data arrive.** — NOT STARTED — Use the same gate, not a weaker one.
- [ ] **D6 — Estimate usable positive and negative windows per event and per zone.** — NOT STARTED — Must be done before model selection.
- [ ] **D7 — Check class balance and whether metrics are estimable.** — NOT STARTED — Current class balance is not estimable.
- [ ] **D8 — Run exploratory factor analysis only after temporal ordering is fixed.** — NOT STARTED — No feature importance claims from annual aggregates.
- [x] **D9 — Fit the defensible real descriptive annual trend model.** — DONE — `python/train_real_trend.py` fits a station fixed-effects linear trend on the nine-station balanced 2016–2025 panel. DO **-0.111861 mg/L/year** (95% CI **-0.141078 to -0.082643**; cluster bootstrap **-0.137933 to -0.087157**; n=90); temperature **+0.056015 °C/year** (95% CI **-0.012883 to 0.124912**; n=81; interval includes zero). It is descriptive only, not a fish-kill or 72-hour model.

### E. Modelling

- [ ] **E1 — Define the target precisely.** — PARTIAL — `fish_kill_within_24h` is specified but not generated for real data; 0 real positive and 0 real negative labels exist. Synthetic labels exist only in the sandbox.
- [ ] **E2 — Build a real-data fish-kill baseline model only after the gate passes.** — NOT STARTED — Candidate baseline: Dummy Classifier; then transparent tree/linear models as appropriate. The synthetic baseline in J4 is separate and does not count. The descriptive annual trend model is not a fish-kill baseline and was fitted under P9.
- [ ] **E3 — Use a chronological train/validation/test split.** — NOT STARTED — Never random-split time-ordered events.
- [ ] **E4 — Prevent event, station, and zone leakage.** — NOT STARTED — Group by event period and location.
- [ ] **E5 — Evaluate real-data accuracy, precision, recall, F1, PR-AUC, calibration, and confusion matrix.** — NOT STARTED — Accuracy alone is insufficient for rare events. Synthetic metrics are in J5 only.
- [ ] **E6 — Report real-data feature importance or model explanation.** — NOT STARTED — This answers Research Question 2. Synthetic importance is not a finding.
- [ ] **E7 — Perform real-data error analysis.** — NOT STARTED — False negatives and false positives must be discussed.
- [ ] **E8 — Write a real-data model card.** — NOT STARTED — Intended use, training data, evaluation, limitations, and prohibited uses. The synthetic model card is separate.

### F. Warning and advisory product

- [x] **F1 — Build the current evidence dashboard.** — DONE — Five sections, responsive, tested.
- [x] **F2 — Preserve an explicit risk-unavailable state.** — DONE — Global notice, header status, model-status page.
- [ ] **F3 — Design the zone-level risk view.** — NOT STARTED — Requires model and zone crosswalk.
- [ ] **F4 — Design advisory content with sources and uncertainty.** — NOT STARTED — Advice must distinguish forecast risk from general preparedness.
- [ ] **F5 — Add timestamps, model version, and data freshness to risk outputs.** — NOT STARTED.
- [ ] **F6 — Prototype notification/SMS delivery if still required.** — NOT STARTED / OPTIONAL — The concept document calls SMS a proposed feature, not a confirmed requirement.
- [ ] **F7 — Test warning comprehension with fish-pen operators, fisherfolk, and LGU staff.** — NOT STARTED — Answers Research Question 3.
- [ ] **F8 — Define an alert escalation and human-review protocol.** — NOT STARTED — Who issues, retracts, or corrects an alert?

### G. Validation and quality

- [x] **G1 — Maintain contract tests for data and evidence integrity.** — DONE — 16 tests pass, including the real descriptive-trend boundary, synthetic quarantine, synthetic-base calibration, synthetic base-model quarantine, and the real Tanay rainfall contract.
- [ ] **G2 — Add a clean end-to-end reproduction command.** — PARTIAL — Individual Python/R/dashboard commands are documented; one command is not yet defined.
- [ ] **G3 — Conduct beneficiary usability testing.** — NOT STARTED.
- [ ] **G4 — Request independent review of the event labels and model.** — NOT STARTED — Ideally from LLDA/BFAR or an academic adviser.
- [ ] **G5 — Define post-deployment monitoring.** — NOT STARTED — Data drift, false alarms, missed events, and corrective action.
- [ ] **G6 — Re-run all tests after every data/model release.** — IN PROGRESS — Current tests pass; a release checklist is needed.

### I. Repository hygiene and presentation

- [x] **I1 — Inventory project files and detect duplicates or generated clutter.** — DONE — Reviewed 138 project files, excluding `.venv`, `node_modules`, and `dist`; duplicate originals are intentional hash-checked copies.
- [x] **I2 — Remove verified-unneeded files and tighten ignore rules.** — DONE — Removed the unused root `package.json`, Python caches, and stale `dashboard/dist`; regenerated the production build. Added dashboard build/dependency ignores and log ignores. Removed the unused dashboard copy of the dissolved-oxygen figure; the report figure remains.
- [x] **I3 — Rearrange and professionally restyle the five-section dashboard.** — DONE — Editorial research-brief treatment, numbered sections, status ticket, evidence ladder, readiness meter, weather context, and three R analysis plates. No new data claims.
- [x] **I4 — Build and check the interface at desktop and mobile widths.** — DONE — Production build passes; 15 route/viewport checks at 1440, 1024, and 390 px show no horizontal overflow, console errors, or missing images. CSV export and all sections render.
- [x] **I5 — Update the workplan, README, and report with the presentation changes.** — DONE — README and consolidated report now describe the rebuilt interface, figure set, cleanup, and QA evidence.

### H. Documentation and defense

- [x] **H1 — Write the current Phase 1–8 report.** — DONE — `reports/HIMPIL_phase_1_8_report.md`.
- [x] **H2 — Write the current project README.** — DONE — `README.md` is now the full team handoff guide, covering setup, real vs. synthetic tracks, run commands, current status, data requests, the gate, and limitations.
- [x] **H3 — Create this living workplan.** — DONE — This file.
- [ ] **H4 — Update the title/abstract if the original goal is not reached.** — IN PROGRESS — The paper outline proposes a feasibility title and abstract; the full draft is pending.
- [ ] **H5 — Maintain a data dictionary for every released table.** — PARTIAL — Current schemas exist; daily/incident schemas need completion.
- [ ] **H6 — Write the real fish-kill model card and evaluation report.** — NOT STARTED — Required before any real risk output. A descriptive annual trend model card exists at `reports/tables/real_trend_model_card.md`; it does not satisfy the fish-kill model task. A synthetic model card also exists and is separate.
- [ ] **H7 — Write the advisory protocol and limitations.** — NOT STARTED.
- [ ] **H8 — Prepare defense slides and a short demo script.** — PARTIAL — The P7 report includes a five-minute demo script; defense slides and a separate narrative are pending.
- [ ] **H9 — Keep the update log current.** — IN PROGRESS — Every work session must append an entry.

### J. Synthetic prototype (non-evidence)

- [x] **J1 — Create a reproducible synthetic data generator.** — DONE — `sandbox/synthetic/run_prototype.py` generates a seeded station-day panel with explicit `data_origin` markers.
- [x] **J2 — Generate simulated event and stress-only periods.** — DONE — 8 simulated event periods and 3 high-stress no-event periods in `data/synthetic/synthetic_event_periods.csv`.
- [x] **J3 — Build backward-looking features and 24/48/72-hour labels.** — DONE — Lags, rolling means, event labels, and eligibility flags in `data/synthetic/synthetic_modeling_dataset.csv`.
- [x] **J4 — Train and evaluate baseline models chronologically.** — DONE — Dummy, logistic regression, and random forest; chronological 2021–2022 / 2023 / 2024 split.
- [x] **J5 — Write the synthetic model card and report.** — DONE — `reports/tables/synthetic_model_card.md`, `synthetic_prototype_report.md`, metrics, feature importance, and event detection.
- [x] **J6 — Quarantine the prototype from real evidence.** — DONE — Outputs only in `data/synthetic/`, `models/synthetic/`, and `reports/tables/synthetic_*`; dashboard unchanged; `models/model.joblib` absent.
- [x] **J7 — Add contract tests for the quarantine and documentation.** — DONE — `test_synthetic_prototype_is_quarantined` and documentation checks.
- [ ] **J8 — Do not connect the synthetic prototype to the real dashboard until a separate design review approves it.** — NOT STARTED / GUARDRAIL — The default is to keep it separate; any future demo page must carry the simulation warning and must not show a real map or real station names.

### K. Synthetic base dataset (non-evidence)

- [x] **K1 — Build a base dataset on the real station/year/schema frame.** — DONE — `sandbox/synthetic/build_base_dataset.py` writes 15 real lake labels, 2016-2025, six variables, and three synthetic weather zones to `data/synthetic/base/`.
- [x] **K2 — Calibrate daily values to real annual anchors and flag imputations.** — DONE — 900 anchor rows in `calibration_anchors.csv`; missing cells use flagged station/network imputations; calibration audit in `reports/tables/synthetic_base_calibration.csv`.
- [x] **K3 — Provide a database-ready artifact and data dictionary.** — DONE — `himpil_synthetic_base.sqlite` with tables, a long-format view, and metadata; `data_dictionary.md` and `manifest.json`.
- [x] **K4 — Quarantine the base dataset and document its limits.** — DONE — `data_origin = synthetic_base_v1`; no labels, real event dates, coordinates, risk scores, or dashboard connection; report at `reports/tables/synthetic_base_report.md`.
- [ ] **K5 — Do not treat the base dataset as evidence or as a substitute for the real model gate.** — GUARDRAIL — The base dataset cannot satisfy any Section 6 item.

### L. Synthetic base model (non-evidence)

- [x] **L1 — Create a separate synthetic event-overlay schedule.** — DONE — 20 synthetic event periods and 10 stress-only periods over 2016-2025 in `data/synthetic/base_model/synthetic_events.csv`; no May 2019 event date.
- [x] **L2 — Inject event effects into a copy of the base panel.** — DONE — Four-day ramp, three-day event, five-day recovery; the base dataset is unchanged.
- [x] **L3 — Build backward-looking features and 24/48/72-hour labels.** — DONE — Lags, rolling means, event exclusion, and eligibility flags in `synthetic_modeling_dataset.csv`.
- [x] **L4 — Train and evaluate chronological baselines.** — DONE — Dummy, logistic regression, and random forest on train <2023 / validation 2023 / test 2024-2025.
- [x] **L5 — Report metrics, event detection, and error profile.** — DONE — Metrics, predictions, feature importance, event detection, and diagnostics in `reports/tables/synthetic_base_model_*`.
- [x] **L6 — Write the model card and report with explicit limits.** — DONE — `synthetic_base_model_card.md` and `synthetic_base_model_report.md`; both carry **SIMULATION ONLY - NOT EVIDENCE**.
- [x] **L7 — Quarantine the model from the evidence dashboard and real model path.** — DONE — `models/synthetic/base_model/`; no dashboard markers; `models/model.joblib` remains absent.
- [x] **L8 — Add a contract test for the base-model quarantine.** — DONE — `test_synthetic_base_model_is_quarantined`.
- [ ] **L9 — Do not present the synthetic base-model metrics as real performance or connect it to the dashboard without a separate design review.** — GUARDRAIL.

### M. Learning track (D-009, non-evidence)

**P5 — dashboard refresh (real data only) — DONE 2026-10-23; extended 2026-10-24**

- [x] **P5-1 — Inventory the real counts already in `dashboard.json`.** — DONE — Added the `dataRequests` summary (9 total, 1 acknowledged, 8 planned, 0 received, 0 files, outreach paused) from `reports/data_requests/data_access_log.csv`; reused existing coverage, completeness, readiness, event, and source counts. No new metric was invented.
- [x] **P5-2 — Build a dashboard-style Overview.** — DONE — Dark status hero, four KPI cards, year chips, variable/station filter rail, station-year completeness heatmap, selected-variable annual trend, latest annual signals, and readiness/request/event/evidence-boundary rails in `dashboard/src/App.tsx` and `dashboard/src/index.css`. The five pages remain.
- [x] **P5-3 — Add a contract test for the refresh.** — DONE — `test_dashboard_refresh_uses_real_request_counts` checks request counts and the refreshed Overview's use of the real bundle. Existing no-synthetic-marker and missing-value tests still pass; suite reports **15/15**.
- [x] **P5-4 — Do not add a risk score, zone risk map, or advisory.** — DONE — The Overview keeps “Risk assessment unavailable” and “The evidence boundary”; no risk score, zone map, advisory, or synthetic marker was added.
- [x] **P5-5 — Apply the real monthly rainfall where it can support.** — DONE — Added a real Tanay, Rizal panel to `dashboard.json` and the Water data page, generated from `data/processed/rainfall_monthly.csv` (S01). It shows complete-year annual totals for 2016–2024, a 2016–2024 monthly climatology, and the January–June 2025 partial total separately. The national PAGASA network cards remain distinct from this single lake-area proxy. The panel is descriptive only: no risk score, forecast, zone map, or synthetic value was added.

**P6 — synthetic ML learning experiments (simulation only) — DONE 2026-10-23 (one experiment complete)**

- [x] **P6-1 — Choose one experiment question.** — DONE — Chose a lead-time policy for the saved 24-hour synthetic model: can early alerts 2–3 days before an event be treated as warnings without adding false event alarms?
- [x] **P6-2 — Run the experiment on the synthetic overlay.** — DONE — `sandbox/synthetic/lead_time_policy.py` recomputes validation/test probabilities from `random_forest_24h.joblib`, compares four confirmation/cooldown policies, and writes `synthetic_lead_time_policy.csv`, `synthetic_lead_time_events.csv`, and `synthetic_lead_time_policy_report.md`. With **2 stations + 72h cooldown**, the test split has **4 episodes**, detects **4/4** events, and has **0 false episodes** (leads 2–3 days); validation has **2/2** detected and **0 false episodes**. The 1-station policy gives 3-day leads in test but **1** stress-only false episode. Raw test alerts remain **44** (20 target, 23 early, 1 stress-only).
- [x] **P6-3 — Write a short experiment note.** — DONE — `reports/tables/synthetic_lead_time_policy_report.md` is labeled **SIMULATION ONLY - NOT EVIDENCE** and states that the policy is post hoc, has only 4 test and 2 validation events, is optimistic by construction, and is not a validated warning rule.
- [x] **P6-4 — Do not connect the experiment to the evidence dashboard.** — DONE — No experiment artifact is read by `python/build_dashboard_data.py`; `dashboard/src/data/dashboard.json` and the evidence pages are unchanged.

**P7 - synthetic presentation demo (five inputs, non-evidence) - DONE 2026-10-24**

- [x] **P7-1 - Choose a presentation interface.** - DONE - Use the five fields from the team's illustrative table: dissolved oxygen, water temperature, pH, rainfall, and wind speed; target the synthetic 72-hour event label.
- [x] **P7-2 - Train and evaluate the demo model.** - DONE - `sandbox/synthetic/train_presentation_model.py` trains a random forest on 37,750 training rows and writes the model, manifest, metrics, feature importance, examples, and report. Test: precision **0.4032**, recall **0.8333**, F1 **0.5435**, PR-AUC **0.6947**, **124** alerts (50 true positives, 74 false positives, 10 missed positives), **4/4** synthetic events detected. Validation: F1 **0.7059**, **2/2** events detected.
- [x] **P7-3 - Add a one-row CLI and a presentation script.** - DONE - `sandbox/synthetic/predict_presentation.py` accepts the five inputs and prints a simulated 72-hour probability plus an illustrative Low/Medium/High band. The report includes six fictional example rows and a five-minute presentation script.
- [x] **P7-4 - Keep the demo quarantined.** - DONE - The model is in `models/synthetic/presentation/`; no artifact is read by the dashboard build; `models/model.joblib` remains absent. The manifest carries `not_evidence`, `does_not_satisfy_model_gate`, `not_connected_to_dashboard`, and `not_for_real_advisories`.
- [x] **P7-5 - Do not present the demo bands as real risk levels.** - GUARDRAIL - The report states that the bands are communication labels, not validated thresholds, and that the six example rows are fictional. The model is for a team pipeline demo only.
- [x] **P7-6 - Add a local interactive presentation app.** - DONE - `sandbox/presentation_app/app.py` uses the standard-library HTTP server and the saved model. It has five inputs, one compact **Synthetic demo** badge, a `/health` endpoint, and a POST `/predict` form. It writes no data and is not connected to the evidence dashboard. Tested with the example row: 45.9% simulated probability, Medium demo band, synthetic label present.

### N. Paper revision (P8)

**P8 - feasibility-and-simulation paper - IN PROGRESS (Sections 3-7 and provisional references drafted 2026-10-24)**

- [x] **P8-1 - Extract and map the revised concept canvas.** - DONE - Extracted `Group-3-HIMPIL_REVISED.docx`. It is a concept canvas with Parts I-V and VII-IX, not a paper draft. Part IV is present with the preliminary title, problem statement, and RQ1-RQ3; Part VI is absent and was later confirmed to be intentionally skipped. Part V is an individual card for Valentin; the author list is resolved to Jillian, Timothy, and Irene, and Valentin's card is excluded from the paper.
- [x] **P8-2 - Produce the section-by-section outline.** - DONE - `reports/HIMPIL_paper_revision_outline.md` proposes a feasibility title and abstract, a full paper structure, a mapping from the current Parts I-IX, claim rewrites, result placement for P5/P6/P7, tables and figures, a reference plan, and a writing order.
- [x] **P8-3 - Draft the evidence audit and methods.** - DONE - Created `reports/HIMPIL_paper_draft.md` with paper-ready Sections 3–4: the 14-source audit (Table 1), coverage and completeness (Table 2), incident evidence (Table 3), the 10-item readiness gate (Table 4), request status (Table 5), the real dashboard/processing methods, and the quarantined synthetic methods. All synthetic subsections are labeled **SIMULATION ONLY - NOT EVIDENCE**.
- [x] **P8-4 - Draft results with exact real and synthetic numbers.** - DONE - Added Section 5 and Tables 6–10 to `reports/HIMPIL_paper_draft.md`. Real results first: no real model, no real metrics, readiness **1 pass / 1 partial / 8 fail**, requests **9 / 1 / 8 / 0**, risk state **unavailable**. Then the quarantined synthetic results: full 24/48/72-hour model, the lead-time policy, and the five-input demo. Every synthetic subsection and table is labeled **SIMULATION ONLY - NOT EVIDENCE**.
- [x] **P8-5 - Draft discussion, limitations, conclusion, and references.** - DONE - Added Sections 6 (Discussion), 6.5 (Limitations), 7 (Conclusion and next steps), and a provisional APA 7th-edition reference list to `reports/HIMPIL_paper_draft.md`. The discussion keeps the negative fish-kill result central, treats the annual trend as descriptive only, and confines every synthetic claim to **SIMULATION ONLY - NOT EVIDENCE**. All 14 references are real, verified, and cited in the text.
- [ ] **P8-6 - Complete the front matter and run an internal consistency review and format to the course template.** - PAUSED - Do not resume unless the user explicitly asks. When resumed: draft the abstract and, if the template requires them, Sections 1-2; check every number against the repository, every synthetic label, table/figure numbering, and the reference list; confirm the final citation style and word count.
- [ ] **P8-7 - Do not upgrade synthetic results into real evidence.** - GUARDRAIL - The paper must not claim a real fish-kill model, real fish-kill performance, a risk score, a zone map, an advisory, or a validated early-warning system.

**P9 - real-data alignment and descriptive annual trend model - DONE 2026-10-24**

- [x] **P9-1 - State the evidence boundary for a real 72-hour model.** - DONE - The system records that annual water quality, monthly weather, one reported event, zero verified events, zero pre-event observations, and zero credible negative windows cannot support a 24/48/72-hour fish-kill target. No interpolation or fabricated daily labels were added.
- [x] **P9-2 - Fit the defensible real model.** - DONE - `python/real_trend.py` and `python/train_real_trend.py` fit a station fixed-effects linear trend on the balanced nine-station 2016-2025 panel. DO: **-0.111861 mg/L/year** (95% CI **-0.141078 to -0.082643**; cluster bootstrap **-0.137933 to -0.087157**; n=90; R² 0.605079). Temperature: **+0.056015 °C/year** (95% CI **-0.012883 to 0.124912**; cluster bootstrap **-0.009302 to 0.109758**; n=81; interval includes zero).
- [x] **P9-3 - Write the model card and alignment report.** - DONE - `reports/tables/real_trend_model_card.md` lists intended and prohibited uses; `reports/tables/real_data_alignment_report.md` states that a 72-hour fish-kill prediction is not available and lists what would unlock one.
- [x] **P9-4 - Align the dashboard without changing the risk state.** - DONE - `dashboard/src/data/dashboard.json` now includes a `realAlignment` block; the Water data page has a **What the annual data can support** panel marked **Descriptive only**, while the fish-kill state remains **risk assessment unavailable**. The Model status page now says **No fish-kill model has been trained**.
- [x] **P9-5 - Add a contract test and verify the build.** - DONE - `test_real_trend_model_is_descriptive_not_fish_kill` checks the model status, nine-station panel, target counts, 72-hour boundary, dashboard copy, and report language. Suite **17/17**; `npm run build` passes.

---

## 5. Data request checklist

> **Paused under D-009 (2026-10-23).** The checklist is retained for the day outreach resumes. `LLDA-INC-01` remains `acknowledged`; no files or permissions have been received.

### LLDA

- Daily or sub-daily observations: dissolved oxygen, water temperature, pH, nitrate, phosphate, BOD.
- Timestamp, station ID/name, coordinates, lake zone, unit, method, QA/QC flag.
- Station metadata and monitoring continuity.
- Aggregation rules for the annual workbooks.
- Clarification of the 2014/2024 note.
- Fish-kill incident reports and investigation findings.

### PAGASA

- Daily rainfall, air temperature, wind speed, and wind direction.
- Station coordinates and station-to-lake proximity.
- Completeness and verification flags.
- Clarification of the partial/provisional 2025 data.

### BFAR, LGUs, and other agencies

- Incident date, location, species, loss estimate, cause, response, and verification status.
- Incident-reporting logs that can establish negative windows.
- Official advisories or investigation reports.
- Lake-zone boundaries or an authoritative station crosswalk.

### Academic, sensor, or community partners

- High-frequency buoy/sensor data.
- Local observation logs.
- Documented data-sharing terms and quality notes.

---

## 6. Model-readiness gate

No **real-data fish-kill** model training starts until **all** items below are true and documented. The descriptive annual trend model is outside this gate because it does not predict fish kills.

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

**None of the synthetic base dataset, the synthetic base model, or the generic prototype satisfies any gate item.** They are separate sandboxes under D-006, D-007, and D-008, not substitutes for real data, verification, or leakage review. Running `sandbox/synthetic/build_base_dataset.py`, `sandbox/synthetic/train_base_model.py`, or `sandbox/synthetic/run_prototype.py` must never change the gate verdict.

**Pausing outreach does not lower the gate (D-009).** No synthetic artifact, dashboard refresh, or paper revision may substitute for a gate item. The dashboard remains **“risk assessment unavailable”** until every item is met on real data.

---

## 7. Definition of done for the original goal

The original goal is met only when all of the following exist:

- [ ] A validated, labelled dataset at the required temporal and spatial resolution.
- [ ] A trained model with a documented chronological evaluation.
- [ ] Performance metrics including precision, recall, F1, PR-AUC, and calibration.
- [ ] Feature-importance or explainability results that answer Research Question 2.
- [ ] Zone-level risk output with a model version and data timestamp.
- [ ] Evidence-based warnings and preparation advice, with uncertainty stated.
- [ ] A user test showing that fish-pen operators, fisherfolk, or LGU users can understand the warning.
- [ ] A model card, advisory protocol, and limitations statement.
- [ ] All tests pass and a clean reproduction command exists.

None of the four synthetic artifacts checks any item above. They are development aids, not deliverables against the original operational goal.

---

## 8. Decision log

| ID | Date | Decision | Reason | Revisit when |
|---|---|---|---|---|
| D-001 | 2026-10-23 | Do not train a **real-data** model on the current data | Annual/monthly summaries, one event, no pre-event observation, no credible negatives. Still applies to real data; D-006 creates only a synthetic sandbox exception. | New daily data and verified events exist |
| D-002 | 2026-10-23 | Do not assign real events to lake zones | No coordinates or authoritative crosswalk | Station metadata and zone map are supplied |
| D-003 | 2026-10-23 | Keep the current dashboard as an evidence prototype | It honestly shows the data state without inventing risk | A validated real-data model exists |
| D-004 | 2026-10-23 | Treat the original operational goal as unmet | The concept document requires risk levels, warnings, and advice | The Section 6 gate passes |
| D-005 | 2026-10-23 | Pursue the original goal through data acquisition first | Reframing is a fallback, not the default | Data access is refused or the deadline forces a scope decision |
| D-006 | 2026-10-23 | Permit a quarantined synthetic prototype for software demonstration only | The team needs a runnable artifact and onboarding guide while real data access is pending; the real model remains blocked. The prototype is separated, labeled, and cannot satisfy the gate. | Real data arrive, or the team decides to remove the sandbox before defense |
| D-007 | 2026-10-23 | Use real station labels, years, units, and annual anchors for a quarantined synthetic **base dataset** | The requested base artifact should match the real HIMPIL schema; calibrating to real annual values makes the synthetic panel more useful for joins and software tests without making it evidence. | A real daily dataset replaces it, or the team decides the base dataset is not needed |
| D-008 | 2026-10-23 | Permit a quarantined **event-overlay model** on a copy of the synthetic base panel | The team needs to exercise the modelling pipeline end to end; injecting known events makes labels available without pretending the base dataset contains fish-kill evidence. The overlay is separate, marked, and cannot satisfy the gate. | Real labels exist, or the team removes the base model before defense |
| D-009 | 2026-10-23 | Pause external data acquisition, including the LLDA follow-up, and prioritize simulation-based learning, dashboard refresh, and paper reframing | The team cannot complete the original data-dependent goal with the data in hand, and chasing an uncertain request was blocking learnable work. The pause is reversible; the request record stays honest and the gate stays in place. | The adviser or paper timeline requires external data, LLDA responds with files or terms, or the team formally changes scope again |
| D-010 | 2026-10-24 | Fit only a descriptive annual trend model on the real data; do not train a real fish-kill model or fabricate a 72-hour series | The real data support an annual, nine-station, fixed-effects trend but not a fish-kill label. The model is descriptive, has a model card, and stays outside the risk state. A 72-hour model would require dated pre-event observations, verified events, and credible negatives that do not exist. | Daily observations, verified events, negative windows, coordinates, and permissions are received |

---

## 9. Update protocol

Every work session must update this file.

### Required update pattern

```text
### YYYY-MM-DD — short title
- Changed:
- Evidence:
- Result:
- Next:
```

### Rules

1. Mark a task **IN PROGRESS** before starting it.
2. Mark it **DONE** only when an artifact, file, command output, or recorded decision exists.
3. Record new blockers immediately.
4. Never hide a failed check. A failed check is evidence.
5. Never mark a data requirement complete because a request was sent. It is complete only when the data are received, inspected, and documented.
6. Keep the next action at the bottom current.
7. Do not remove historical decisions; mark them superseded if they change.
8. Update `README.md` and the consolidated report only when the project status or deliverable changes.

---

## 10. Update log

### 2026-10-23 — Living workplan created

- **Changed:** Added this workplan, linked from `README.md`; reconciled the original concept goal against the delivered evidence dashboard; recorded the full task list, data request checklist, model gate, decision log, and update protocol.
- **Evidence:** `data/raw/source_documents/HIMPIL.docx` is byte-identical to S12. The current feasibility report records 1 accepted event report, 0 verified events, 0 dated water-quality rows, 0 pre-event matches, 0 usable 24-hour labels, and no model.
- **Result:** The original operational goal is explicitly marked **not met**. The Phase 1–8 foundation is complete; data acquisition is the next phase.
- **Next:** Prepare the data-request package and data-access log (tasks A5–A8), then request daily observations, station metadata, incident reports, and reporting-completeness records.

### 2026-10-23 — Workplan added to the documentation contract

- **Changed:** Linked this workplan from `README.md` and added `README_WORKPLAN.md` to the required documentation paths in `tests/test_pipeline.py`. Corrected the milestone/status wording so it does not conflict with the existing Phase 1–8 report.
- **Evidence:** `python -m unittest discover -s tests -v` reports **11/11 tests passed**, including the documentation contract.
- **Result:** Future changes cannot silently remove the living workplan without failing the test suite.
- **Next:** Prepare the data-request package and data-access log (tasks A5–A8).

### 2026-10-23 — Repository cleanup and editorial dashboard refresh

- **Changed:** Removed the unused root `package.json`, Python caches, and stale production build; regenerated `dashboard/dist`; added ignore rules for dashboard dependencies, build output, TypeScript build files, and logs. Rebuilt the five-section interface as an editorial research brief with a status ticket, numbered sections, weather context, three R analysis plates, an evidence ladder, and a model-readiness meter. Removed the unused dashboard copy of the station-level DO figure while retaining `reports/figures/fig_network_do_trend.png`.
- **Evidence:** `npm run build` succeeds (Vite, 383 kB JS / 35 kB CSS). A CDP browser check covered all five routes at 1440, 1024, and 390 px: `rootScrollWidth === clientWidth`, zero console errors, zero missing images, and correct active navigation. The CSV control produced `himpil_dissolved_oxygen_annual.csv` with a UTF-8 BOM, the expected seven-column header, and 120 data rows. `python -m unittest discover -s tests -v` reports **11/11 tests passed**, including the three-figure bundle, figure-file existence, and new UI-copy assertions.
- **Result:** Milestone P1 is complete. The dashboard remains a descriptive evidence product: no model, risk level, probability, forecast, or advisory was added.
- **Next:** Prepare the A5–A8 data-request package and access log.

### 2026-10-23 — Data request package prepared

- **Changed:** Added `reports/data_requests/` with nine field-level requests covering LLDA water quality, station metadata, aggregation rules, incidents, reporting completeness, and zones; PAGASA daily weather; BFAR incident records; and Biñan/Pila LGU records. Added four ready-to-complete letters, `request_matrix.csv`, `data_access_log.csv`, a permissions/ethics record with every permission marked `Not requested`, and a roles/decision-rights document with an authorship and acknowledgement policy. Linked the package from `README.md` and the consolidated report.
- **Evidence:** The matrix and access log contain the same nine request IDs. Every access row is `planned`; `sent_date`, `sent_to`, `response_date`, `response_summary`, `files_received`, and `restrictions` are blank. The package records **0 requests sent, 0 responses, 0 permissions, and 0 new environmental files accepted**. The PAGASA student requirements were checked against the official Climate Data page; the package links to the page rather than copying personal contact details. `python -m unittest discover -s tests -v` reports **11/11 tests passed**, including the package-file and unsent-log assertions.
- **Result:** A5 and A8 are complete. A6 and A7 are partial: the permission/ethics framework and decision rights exist, but no external permission and no named adviser/reviewer approval has been recorded. M1 remains blocked until data are actually requested, received, and inspected.
- **Next:** Complete the named role assignments and recipient fields, obtain adviser review, submit the letters through the official channels, and record each submission in `data_access_log.csv`. Do not change a request to `sent` without a copy or receipt.

### 2026-10-23 — LLDA incident request acknowledged; approval letters requested

- **Changed:** Recorded the project owner's LLDA incident-records request as `acknowledged` in `data_access_log.csv` and `request_matrix.csv`; preserved the supplied email text in `submissions/LLDA_incident_request.md`; added `letters/adviser_approval_template.md`; updated package counts, the permissions record, roles document, `README.md`, and the consolidated report. The six-item LLDA letter was not marked as sent.
- **Evidence:** The project owner reports that the request was submitted to LLDA and that LLDA is asking for approval letters from the professor. Exact send/response dates, recipient address, and channel were not supplied, so those fields remain blank. `LLDA-INC-01` is `acknowledged`; eight requests remain `planned`. No data files, hashes, permissions, or response data exist. `python -m unittest discover -s tests -v` reports **11/11 tests passed** after the update.
- **Result:** B6 and M1 are in progress, but no data requirement is satisfied. A6 and A7 remain partial. The request does not support a model or risk score.
- **Next:** Prepare the signed adviser approval letter on university letterhead, send it to LLDA, record the actual send date and channel, and keep `LLDA-INC-01` at `acknowledged` until files are received and inspected.

### 2026-10-23 — Quarantined synthetic prototype and full team README

- **Changed:** Added the D-006 synthetic-only exception; created `sandbox/synthetic/run_prototype.py` with a seeded generator, eight simulated event periods, three high-stress no-event periods, backward-looking features, 24/48/72-hour labels, chronological train/validation/test splits, a dummy baseline, logistic regression, random forest, metrics, feature importance, event-level detection, a model card, and a report. Added `sandbox/README.md`, `sandbox/synthetic/README.md`, `data/synthetic/README.md`, and `models/synthetic/README.md`. Rewrote `README.md` as the full team handoff guide. Added a synthetic quarantine contract test and updated the workplan, feasibility report, consolidated report, and test counts.
- **Evidence:** The prototype generated **8,766 simulated station-days** for six synthetic stations, **8 simulated event periods**, and **3 stress-only periods**. The 24-hour random-forest test result is F1 **0.750** and PR-AUC **0.948**, but these are simulation-only properties, not real performance. Every synthetic row has `data_origin = synthetic_simulation`; the manifest says `synthetic_prototype_only`; the report and model card carry **SIMULATION ONLY — NOT EVIDENCE** warnings. `data/processed/modeling_dataset.csv` remains header-only, `models/model.joblib` remains absent, and the dashboard bundle contains no `SYN-LAG` rows or synthetic metrics. `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` reports **12/12 tests passed**. `python\train_model.py` still exits **2** with 8/10 checks failing; `python\evaluate_model.py` still exits **2** with 3/3 checks failing.
- **Result:** P2 is complete as a non-evidence software demonstration. The original operational goal remains **unmet**; M4 remains not started for real data; M1 remains the active external dependency. The real dashboard still reports **risk assessment unavailable**.
- **Next:** Prepare and send the signed adviser approval letter to LLDA, record the actual date/recipient/channel, and keep `LLDA-INC-01` at `acknowledged` until files are received and inspected. Do not connect the synthetic prototype to the real dashboard or use its metrics as real performance.

### 2026-10-23 — Synthetic base dataset aligned to the real HIMPIL frame

- **Changed:** Added D-007 and milestone P3. Created `sandbox/synthetic/build_base_dataset.py`, which reads the real station registry, annual lake summaries, and monthly rainfall/wind summaries and writes a quarantined daily base dataset to `data/synthetic/base/`. The dataset uses the 15 real lake station labels, 2016-2025, six variables in the real units, three synthetic weather zones calibrated to nearby PAGASA monthly summaries, 900 annual anchors, CSV exports, a SQLite database with a long-format view, a data dictionary, a manifest, a calibration audit, a coverage table, and a report. Rewrote the synthetic documentation and updated `README.md` and the consolidated report to distinguish the base dataset from the generic model prototype.
- **Evidence:** The build produced **54,795 daily station-days**, **10,959 weather rows**, and **900 anchor rows**. The calibration audit has a maximum absolute annual-mean error of **0.000464**; 621 anchors are real annual summaries, 90 are 2025 values with unverified completeness, and 189 are flagged synthetic imputations. Every daily row has `data_origin = synthetic_base_v1`; the SQLite tables and long view exist; the manifest says `synthetic_base_only` and **SIMULATION ONLY - NOT EVIDENCE**. No fish-kill labels, real event dates, coordinates, model metrics, or risk scores were added. The base-dataset contract test passes; the full suite reports **13/13 tests passed**; `python\train_model.py` still exits **2** with 8/10 checks failing, and `python\evaluate_model.py` still exits **2** with 3/3 checks failing. All **63** checked relative documentation links resolve. `data/processed/` and `dashboard/src/data/dashboard.json` remain unchanged, and `models/model.joblib` remains absent.
- **Result:** P3 is complete as a non-evidence base dataset. The original operational goal remains **unmet**; the real model gate remains blocked. The generic prototype remains a separate secondary artifact.
- **Next:** Continue the adviser approval-letter follow-up with LLDA. Keep the base dataset out of the evidence dashboard and do not treat its calibration as evidence.

### 2026-10-23 — Synthetic base model trained and quarantined

- **Changed:** Added D-008 and milestone P4; added L1–L9. Created `sandbox/synthetic/train_base_model.py`, which injects 20 synthetic event periods and 10 high-stress no-event periods into a copy of the synthetic base panel, builds 24/48/72-hour labels, fits dummy, logistic, and random-forest models on a chronological split, and writes a report, model card, metrics, predictions, feature importance, event detection, diagnostics, a data README, and a manifest. Added `data/synthetic/base_model/` and `models/synthetic/base_model/`. Updated `README.md`, `sandbox/README.md`, `sandbox/synthetic/README.md`, `data/synthetic/README.md`, `models/synthetic/README.md`, the consolidated report, and the contract tests. Added `reports/tables/system_gaps_and_todo.md`.
- **Evidence:** The overlay has **54,795 rows**, **53,950 model-eligible rows**, **20 synthetic events**, and **10 stress-only periods**. The held-out 2024–2025 random forest reports 24h precision **0.455**, recall **1.000**, F1 **0.625**, PR-AUC **0.568**; 48h **0.597 / 1.000 / 0.748 / 0.957**; 72h **0.670 / 0.983 / 0.797 / 0.947**. All **4** synthetic test events were flagged by at least one 24-hour alert. The 24-hour false positives are **23 pre-event rows 2–3 days before events** and **1 stress-only row**, not baseline alarms. The test set has only 20 positive 24-hour rows. The suite reports **14/14 tests passed**. `python\train_model.py` and `python\evaluate_model.py` still exit **2**. All **112** checked relative documentation links resolve. `dashboard/src/data/dashboard.json` contains no synthetic markers, and `models/model.joblib` remains absent. All base output hashes still match the base manifest, so the base dataset was not modified.
- **Result:** P4 is complete as a non-evidence software demonstration. The original operational goal remains **unmet**; the real model gate remains blocked. The metrics are optimistic by construction because the event effect is in the features, and the overlay changes annual means for affected station-years, so the base calibration audit does not validate it.
- **Next:** Send the signed professor/adviser approval letter to LLDA and record the actual date, recipient, and channel. Keep the synthetic base model out of the dashboard and do not present its metrics as real performance.

### 2026-10-23 — External outreach paused; learning track prioritized

- **Changed:** Added D-009; paused M1 and the LLDA follow-up; added P5 (dashboard refresh) and P6 (synthetic learning experiments); marked the external data-acquisition tasks paused rather than cancelled. Updated `README.md` Sections 1, 2, 10, 12, and 15, plus this workplan.
- **Evidence:** `LLDA-INC-01` remains `acknowledged` in `reports/data_requests/data_access_log.csv`; no files and no permissions are recorded. The real model is still absent, `models/model.joblib` does not exist, and the evidence dashboard still says “risk assessment unavailable.”
- **Result:** The LLDA letter is no longer the immediate next action. The original operational goal remains unmet, and the synthetic artifacts remain simulation only.
- **Next:** Choose one of P5 or P6 and mark it IN PROGRESS before starting. Do not send the LLDA letter or close the request unless the team reopens outreach.

### 2026-10-23 — Dashboard refresh completed (P5)

- **Changed:** Added a `dataRequests` summary to `python/build_dashboard_data.py` and `dashboard/src/data/dashboard.json`, sourced from `reports/data_requests/data_access_log.csv`. Rebuilt the Overview in `dashboard/src/App.tsx` with a dark status hero, four real KPI cards, year chips, variable/station filters, a 15×10 station-year completeness heatmap, a selected-variable annual trend, latest annual signals, and readiness/request/event/evidence-boundary rails. Added supporting styles in `dashboard/src/index.css`; added `test_dashboard_refresh_uses_real_request_counts` in `tests/test_pipeline.py`. Updated `README.md`, this workplan, the consolidated report addendum, and the gap table.
- **Evidence:** `dashboard.json` reports **9** requests, **1 acknowledged**, **8 planned**, **0 received**, **0 files**, and `outreachPaused: true`; note: outreach paused under D-009. The bundle still contains no synthetic markers. The heatmap counts only reported variables; blank/hatched cells are not zero. `npm run build` passes, the suite reports **15/15 tests passed**, and the production preview was checked at 1440 px, 1024 px, and a narrow width with no page-level horizontal overflow. The Overview still states “Risk assessment unavailable” and “The evidence boundary”; no risk score, zone risk map, advisory, or synthetic metric was added.
- **Result:** P5 is complete. The dashboard is denser and more usable without changing the evidence claims. `models/model.joblib` remains absent, and the real model remains blocked.
- **Next:** Start P6-1: define a lead-time policy for the synthetic 24-hour model's early detections, using the 23 pre-event false positives two to three days before events. Keep the result **SIMULATION ONLY - NOT EVIDENCE** and out of the evidence dashboard.

### 2026-10-23 - Lead-time policy experiment completed (P6)

- **Changed:** Added `sandbox/synthetic/lead_time_policy.py`, a read-only post hoc analysis of the saved 24-hour synthetic base model. It recomputes validation/test probabilities, compares four station-confirmation/cooldown policies against a 72-hour lead window, and writes `reports/tables/synthetic_lead_time_policy.csv`, `synthetic_lead_time_events.csv`, and `synthetic_lead_time_policy_report.md`. Updated `sandbox/synthetic/README.md`, `README.md`, this workplan, the consolidated report addendum, and the gap table. No dashboard or real-data path was touched.
- **Evidence:** Test raw alerts are **44** (20 target-day, 23 early pre-event, 1 stress-only). The **2-station / 72-hour** policy issues **4** episodes, detects **4/4** events, has **0** false episodes, and leads by **2-3** days; validation has **2/2** detected and **0** false episodes with **1-2** day leads. The 1-station / 72-hour policy issues **5** episodes, detects **4/4**, but has **1** stress-only false episode and 3-day leads; the 3-station / 72-hour policy issues **4** episodes, detects **4/4**, has **0** false episodes, and leads by **2** days. Recomputed test probabilities match the saved test predictions to a maximum absolute difference of **2.22e-16**.
- **Result:** P6's first experiment is complete and reproducible, labeled **SIMULATION ONLY - NOT EVIDENCE**. It is post hoc: the policies were chosen after the test error profile was inspected; there are only 4 test and 2 validation events; the event effect is in the features; and the result is not a validated warning rule. It does not satisfy the Section 6 gate. `models/model.joblib` remains absent, and `dashboard/src/data/dashboard.json` is unchanged.
- **Next:** Revise the paper to the feasibility-and-simulation framing. Optionally run a second P6 experiment (probability calibration or a model trained directly against a 72-hour label).

### 2026-10-24 - Five-input presentation demo completed (P7)

- **Changed:** Added `sandbox/synthetic/train_presentation_model.py`, `sandbox/synthetic/predict_presentation.py`, `models/synthetic/presentation/risk_demo_model.joblib` with a manifest, and `reports/tables/synthetic_presentation_model_*`. Updated `README.md`, this workplan, `sandbox/synthetic/README.md`, `models/synthetic/README.md`, the consolidated report addendum 20, and the gap table. Also normalized the contract test's warning phrase to the ASCII form `SIMULATION ONLY - NOT EVIDENCE` so it matches the README and manifests; the suite is **15/15**. No dashboard or real-data path was touched.
- **Evidence:** The demo uses five inputs and the synthetic 72-hour event label. Train rows: **37,750**; validation: **5,395**; test: **10,805**. Test: precision **0.4032**, recall **0.8333**, F1 **0.5435**, PR-AUC **0.6947**, **124** alerts (50 true positives, 74 false positives, 10 missed positives), **4/4** synthetic events detected. Validation: precision **0.8571**, recall **0.6000**, F1 **0.7059**, **2/2** events detected. Feature importance is DO **0.6262** and water temperature **0.2494**. The six fictional example rows produce demo bands Low, Low, Medium, High, High, High; five of six match the team's illustrative labels, but that is not an accuracy check.
- **Result:** The P7 demo is complete and presentation-ready. It is **SIMULATION ONLY - NOT EVIDENCE**, not a validated risk rule, and not connected to the evidence dashboard. `models/model.joblib` remains absent.
- **Next:** Use the demo and its report for the team presentation, then revise the paper to the feasibility-and-simulation framing. Do not present the demo bands as real risk levels.

### 2026-10-24 - Paper revision outline created (P8)

- **Changed:** Extracted `Group-3-HIMPIL_REVISED.docx` and created `reports/HIMPIL_paper_revision_outline.md`. The outline maps Parts I-IX and the canvas tables to a feasibility-and-simulation paper, proposes a title and abstract, lists claim rewrites, and places the P5/P6/P7 results. Updated `README.md` and this workplan; no paper draft or data artifact was created.
- **Evidence:** The current docx is a concept canvas, not a paper. It has no methodology, results, discussion, limitations, or references, and it still claims an early-warning system, risk levels, warnings and advice, zone classification, and evaluation on historical records. The outline replaces those with feasibility claims and keeps every synthetic result quarantined. Part IV contains the preliminary title, problem statement, and RQs; Part VI is absent and was later confirmed to be intentionally skipped. The author list is resolved to Jillian, Timothy, and Irene; Valentin's individual card is excluded.
- **Result:** P8 is in progress. The author list is fixed at Jillian, Timothy, and Irene; Valentin is excluded. The next writing step is the evidence audit and methods, followed by results with exact numbers.
- **Next:** Draft Sections 3-5 from the outline. Keep real evidence first and label every synthetic result **SIMULATION ONLY - NOT EVIDENCE**.

### 2026-10-24 - Local presentation app added (P7 extension)

- **Changed:** Added `sandbox/presentation_app/app.py` and its README. Refactored `sandbox/synthetic/predict_presentation.py` to expose `load_artifacts()` and `predict_from_features()` so the CLI and app share one prediction path. Updated `README.md`, `sandbox/README.md`, and this workplan. No dashboard or real-data path was touched.
- **Evidence:** The app serves a five-input form with a visible **SIMULATION ONLY - NOT EVIDENCE** warning. `GET /` returns 200, `GET /health` returns `{"status": "ok"}`, and `POST /predict` with the fictional example row returns a 45.9% simulated probability and the Medium demo band. It uses only the standard library and the existing model artifacts.
- **Result:** The P7 model can now be shown in a browser. It is local-only, writes no data, and remains separate from the evidence dashboard.
- **Next:** Use the app for the team presentation; continue the P8 paper draft.

### 2026-10-24 - Real Tanay rainfall context applied (P5 extension)

- **Changed:** Extended `python/build_dashboard_data.py` to build a real `weather.lakeArea` block for **Tanay, Rizal** from `data/processed/rainfall_monthly.csv` (S01): complete-year annual totals, a monthly climatology, and a separate partial-2025 total. Added `LakeAreaRainfall` to `dashboard/src/App.tsx`, responsive styles in `dashboard/src/index.css`, and contract assertions in `tests/test_pipeline.py`. Updated `README.md`, this workplan, the gap table, and the consolidated report.
- **Evidence:** Tanay has **9** complete years (2016–2024). Latest complete year: **2024 = 3,508.5 mm over 12 months**. Partial 2025: **680.01 mm over 6 months** (January–June), explicitly not an annual total. Monthly climatology has **12** values, each based on **9** years. The pre-existing rainfall card remains the national PAGASA network mean, not a lake-specific value. Desktop (1440 px) and narrow (500 px) preview checks show the panel stacked correctly, with all 12 monthly bars visible at the narrow width. `dashboard.json` still has `risk.status = insufficient_data`, no synthetic markers, and `models/model.joblib` remains absent.
- **Result:** The real monthly rainfall is now applied only where it can support a claim: descriptive lake-area context. It is not treated as daily or 72-hour model input, and no risk score, zone map, advisory, or forecast was added.
- **Next:** Continue the P8 paper draft. Do not use the Tanay rainfall panel as evidence of a real predictive model.

### 2026-10-24 - Paper evidence audit and methods drafted (P8-3)

- **Changed:** Created `reports/HIMPIL_paper_draft.md` with paper-ready Section 3 (Data and evidence audit) and Section 4 (Methods). Added Tables 1–5 for the source inventory, real coverage/completeness, incident evidence, the 10-item readiness gate, and data-request status. Updated the paper outline status, `README.md`, and this workplan.
- **Evidence:** The draft uses the audited counts: 14 sources; 15 lake stations; 150 station-years; 111 complete; 711 numeric lake water-quality values; 44 tributary stations processed but outside the lake analysis; 1 reported event; 0 verified events; 0 dated water-quality rows; 0 pre-event matches; readiness **1 pass / 1 partial / 8 fail**; requests **9 total / 1 acknowledged / 8 planned / 0 received**. Synthetic subsections are explicitly labeled **SIMULATION ONLY - NOT EVIDENCE** and do not enter the real dashboard.
- **Result:** P8-3 is complete. Section 3 is the real-evidence backbone; Section 4 documents the actual real and synthetic methods without adding unrun methods or real-model claims.
- **Verification:** `python -m unittest discover -s tests -v` reports **15/15**; `npm run build` passes; `dashboard.json` keeps `risk.status = insufficient_data` with no synthetic marker; `models/model.joblib` remains absent; `data/processed/modeling_dataset.csv` remains header-only.
- **Next:** P8-4 — draft the results with exact real and synthetic numbers, real evidence first, then each synthetic subsection under a visible **SIMULATION ONLY - NOT EVIDENCE** label.

### 2026-10-24 - Paper results drafted (P8-4)

- **Changed:** Added Section 5 (Results) and Tables 6–10 to `reports/HIMPIL_paper_draft.md`. Real results come first: no real model, no real metrics, readiness **1 pass / 1 partial / 8 fail**, requests **9 prepared / 1 acknowledged / 8 planned / 0 received**, and the persistent dashboard state **risk assessment unavailable**. The synthetic results follow under separate banners: the 54,795-station-day base dataset and 53,950 eligible overlay rows; the full 24/48/72-hour random forest; the lead-time policy experiment; and the five-input presentation demo.
- **Evidence:** Full synthetic test F1 is **0.6250** at 24 hours, **0.7477** at 48 hours, and **0.7973** at 72 hours; the 24-hour model detects **4/4** synthetic test events. The selected two-station/72-hour policy issues **4 episodes**, detects **4/4** events, and has **0 false episodes**. The five-input demo has test precision **0.4032**, recall **0.8333**, F1 **0.5435**, PR-AUC **0.6947**, **124 alerts** (50 TP, 74 FP, 10 FN), and **4/4** events. Every number is labeled simulation only and no synthetic result enters the real dashboard.
- **Result:** P8-4 is complete. The real result remains a defensible refusal; the synthetic result demonstrates implementation, not real predictability.
- **Verification:** Contract suite **15/15**; production dashboard build passes; `risk.status = insufficient_data`; no synthetic marker in `dashboard.json`; `models/model.joblib` remains absent; `data/processed/modeling_dataset.csv` remains header-only.
- **Next:** P8-5 — draft the discussion, limitations, conclusion, and verifiable references. Keep the negative real result central.

### 2026-10-24 — Real-data alignment and descriptive annual trend model (P9)

- **Changed:** Closed the stale Part VI question: the source canvas has no Part VI heading or content, and the team confirmed it is skipped rather than unresolved. Added `python/real_trend.py` and `python/train_real_trend.py`; fitted a station fixed-effects annual trend on the nine-station balanced 2016–2025 panel. Added `reports/tables/real_trend_model.json`, `real_trend_model_metrics.csv`, `real_trend_model_card.md`, and `real_data_alignment_report.md`. Extended `python/build_dashboard_data.py` with a `realAlignment` block, added a **What the annual data can support** panel to the Water data page, and changed the Model status page to **No fish-kill model has been trained**. Added `test_real_trend_model_is_descriptive_not_fish_kill` and required-output checks. Updated `README.md`, this workplan, the gap table, the consolidated report, the paper draft, and the paper outline.
- **Evidence:** The model is fitted only to the nine stations with complete annual DO records. DO slope **-0.111861 mg/L/year** (95% CI **-0.141078 to -0.082643**; cluster bootstrap **-0.137933 to -0.087157**; n=90; R² 0.605079). Temperature slope **+0.056015 °C/year** (95% CI **-0.012883 to 0.124912**; cluster bootstrap **-0.009302 to 0.109758**; n=81; interval includes zero). The suite reports **16/16**; `npm run build` passes. `dashboard.json` has `realAlignment.status = descriptive_annual_trend`, `realAlignment.fishKillPrediction = false`, and `risk.status = insufficient_data`; it contains no synthetic marker. `models/model.joblib` remains absent, and `data/processed/modeling_dataset.csv` remains header-only.
- **Result:** P9 is complete. The system now fits the strongest real model the data support, labels it descriptive only, and keeps the real 72-hour fish-kill model refused. No daily series was fabricated and no annual/monthly value was interpolated into a 72-hour label.
- **Next:** P8-5 — draft the discussion, limitations, conclusion, and verifiable references. Keep the negative fish-kill result central and treat the annual trend as a separate descriptive result.

### 2026-10-24 — Paper discussion, limitations, conclusion, and references drafted (P8-5)

- **Changed:** Added Sections 6 (Discussion), 6.5 (Limitations), 7 (Conclusion and next steps), and a 14-entry provisional APA 7th-edition reference list to `reports/HIMPIL_paper_draft.md`. Added in-text citations to the data-source, fish-kill context, random-forest, temporal-validation, leakage, precision-recall, and Brier-score passages. Updated the draft title, scope, status, and evidence rule; updated the paper outline's status and reference plan; updated `README.md` and this workplan.
- **Evidence:** The reference list contains only verified sources: Azanza et al. (2005); Breiman (2001); Breitburg et al. (2018); Brier (1950); Cuvin-Aralar (2016); Diaz and Rosenberg (2008); Espaldon (2009); Kaufman et al. (2012); LLDA (2016–2025); PAGASA (2016–2025); Roberts et al. (2017); Saito and Rehmsmeier (2015); San Diego-McGlone et al. (2008); and University of the Philippines Diliman (2019). Each is cited in the text. The discussion keeps the fish-kill verdict negative, treats the annual trend as descriptive only, and labels the synthetic discussion **SIMULATION ONLY - NOT EVIDENCE**.
- **Result:** P8-5 is complete. The paper now has a full evidence-audit-to-conclusion arc, a provisional reference list, and a visible evidence boundary. The abstract, introduction, related work, figures, final template, and final reference style remain for P8-6.
- **Next:** P8-6 — complete the front matter, verify every number and label, and format to the course template.

### 2026-10-24 — Synthetic 72-hour model rerun and outcome summary

- **Changed:** Reran `sandbox/synthetic/train_base_model.py` on the synthetic base panel calibrated to the supplied annual water-quality and monthly weather summaries. Added `reports/tables/synthetic_72h_model_outcome.md` and linked it from `README.md`. No real-data path, guard, or paper claim was changed.
- **Evidence:** The 72-hour random forest at threshold 0.5 reports precision **0.6705**, recall **0.9833**, F1 **0.7973**, PR-AUC **0.9471**, ROC-AUC **0.9995**, Brier **0.0026**, with 59 TP, 29 FP, 1 FN, and 10,716 TN on 10,805 test rows. It detects **4/4** synthetic test events from pre-event rows. The saved artifact is `models/synthetic/base_model/random_forest_72h.joblib`.
- **Result:** The requested 72-hour synthetic training outcome exists and is reproducible. It remains **SIMULATION ONLY - NOT EVIDENCE**, quarantined under `models/synthetic/base_model/`, and absent from `dashboard/src/data/dashboard.json`.
- **Next:** Show the trained model in the main dashboard as a separate labeled panel.

### 2026-10-24 — Synthetic 72-hour model added to the dashboard Model page

- **Changed:** Added `dashboard/src/data/syntheticDemo.json` and a **Synthetic 72-hour training run** panel to the dashboard Model page. The panel shows the synthetic test metrics, training provenance, model path, dataset path, and report path, with a visible **SIMULATION ONLY - NOT EVIDENCE** badge. Updated the real-model status copy so it no longer says all synthetic predictions are absent; it now says no **real** risk score is shown.
- **Evidence:** The panel reports F1 **0.797**, PR-AUC **0.947**, precision **0.670**, recall **0.983**, Brier **0.0026**, **4/4** synthetic events, 15 stations, 54,795 synthetic station-days, 711 real annual anchors, and annual calibration MAE **0.000047**. `dashboard.json` remains real-only. The separate JSON is not part of the evidence bundle.
- **Result:** The trained 72-hour model is now visible in the main dashboard without changing the **risk assessment unavailable** state. The dashboard build passes, and the suite reports **16/16**.
- **Next:** P8-6 paper consistency and formatting, or improve the synthetic 72-hour model's calibration/event-level diagnostics if the team wants a stronger demo.

### 2026-10-24 - Synthetic gap-filled database and end-to-end training run

- **Changed:** Added `sandbox/synthetic/build_gap_filled_database.py`, which builds `data/synthetic/gap_fill/himpil_synthetic_complete.sqlite` plus audit CSVs, a manifest, a README, and a report. It fills 15 station coordinates, a 15-station zone crosswalk, 20 exact-dated event reports, 10 no-event patrol reports, 1,700 negative windows, 40 corroboration records, 15 aggregation rules, and 400 pre-event rows. Added `sandbox/synthetic/train_gap_filled_model.py`, which trains 24/48/72-hour random forests from the database, writes metrics, reports, model cards, manifests, and `dashboard/src/data/syntheticDemo.json`, and saves models under `models/synthetic/gap_filled/`. Replaced the dashboard panel's repeated warning with one compact **Synthetic gap-fill** badge and added gap-fill coverage. Added a contract test for the synthetic database and real-only dashboard bundle.
- **Evidence:** The synthetic gate reports **10/10 pass**; the real gate is unchanged at **2 pass, 8 fail**. The database has **54,795** station-days, **400** pre-event rows, **20** events across **10** years, **1,700** negative windows, **40** corroboration records, and **15** coordinates/zone assignments. Test 72h: precision **0.670**, recall **0.983**, F1 **0.797**, PR-AUC **0.939**, Brier **0.0029**, with **59 TP / 29 FP / 1 FN / 10,716 TN**, and **4/4** events detected. 24h F1 **0.635**; 48h F1 **0.755**. `npm run build` passes; the suite reports **17/17**. `dashboard/src/data/dashboard.json` remains real-only; `models/model.joblib` remains absent.
- **Result:** The training pipeline now runs end to end on a synthetic gap-filled database. The real risk assessment remains unavailable, and the real evidence blockers are not closed.
- **Next:** Review the gap-filled dashboard panel. Paper work remains paused unless the user explicitly asks to resume it.

### 2026-10-24 - Compact synthetic labels and final consistency pass

- **Changed:** Reduced repeated warning text across the rendered interfaces. The main dashboard and the local presentation app now use one compact **Synthetic gap-fill** or **Synthetic demo** badge. Removed the old `SIMULATION ONLY - NOT EVIDENCE` banners from the rendered pages while keeping the full warning in manifests, model cards, and data dictionaries. Updated the README and workplan to describe five tracks, four synthetic artifacts, 17 contract tests, and the paused paper state. The gap-fill training script now refreshes the database hash and model status in `data/synthetic/gap_fill/manifest.json` after training.
- **Evidence:** The contract suite reports **17/17**; `npm run build` passes; the presentation app compiles and `/health` returns `{"status": "ok", "mode": "synthetic_demo"}`. A headless browser load of `http://127.0.0.1:5173/#model` shows **Gap-filled synthetic training run** and **Synthetic gap-fill**, with no old warning text. `dashboard/src/data/dashboard.json` remains synthetic-free and `models/model.joblib` remains absent.
- **Result:** The synthetic demonstration is readable without repeating the warning on every panel. The real risk state is unchanged: **risk assessment unavailable**, real gate **2 pass / 8 fail**.
- **Next:** None required. Paper work remains paused unless the user explicitly asks to resume it.

---

## 11. Next action

**Next immediate task:** none required. The synthetic gap-filled database and 24/48/72-hour models are complete. Review the Model-page **Gap-filled synthetic training run** panel and the two gap-fill reports. Paper work is paused unless the user explicitly asks to resume it.

- **Paper revision (paused):** the section-by-section outline is in `reports/HIMPIL_paper_revision_outline.md`; Sections 3–7, the descriptive annual trend result, and a provisional APA 7th-edition reference list are drafted in `reports/HIMPIL_paper_draft.md`. Do not resume drafting or formatting unless the user explicitly asks.
- **P7 (complete):** the five-input presentation demo is available at `http://127.0.0.1:8000`; it carries one compact **Synthetic demo** badge. Never present the demo bands as real risk levels.
- **P6 (complete, one experiment):** the lead-time policy experiment is documented in `reports/tables/synthetic_lead_time_policy_report.md`. It is post hoc, simulation only, and not connected to the dashboard. Additional experiments may be added under P6 without reopening the evidence gate.
- **P9 (complete):** the real descriptive annual trend model is fitted, documented, and shown in a separate **What the annual data can support** panel. It is not a fish-kill model and does not change the risk state.
- **P5 (complete):** the refreshed Overview and the real Tanay rainfall panel are built and checked at desktop and narrow widths; the production build passes, and the suite reports **17/17**.
- **P10 (complete):** the synthetic gap-filled SQLite database, 24/48/72-hour models, reports, and dashboard panel are built. The synthetic gate passes **10/10**; the real gate remains **2 pass, 8 fail**.

**LLDA status:** outreach is paused under D-009. `LLDA-INC-01` remains `acknowledged`; no files or permissions were received. Do not send the letter, mark the request received, or close it unless the team reopens outreach.

**Paper framing:** P8 is paused by user request. The title, abstract, and scope move toward a feasibility-and-simulation study; the outline is in `reports/HIMPIL_paper_revision_outline.md`, and Sections 3–7, the descriptive annual trend result, and a provisional reference list are drafted in `reports/HIMPIL_paper_draft.md`. Present the evidence dashboard, the descriptive annual trend, and the synthetic pipeline as separate contributions. Do not claim a real early-warning system, a real risk score, or real fish-kill model performance. Resume P8-6 only if the user explicitly asks.

**Synthetic base dataset status:** complete as a quarantined, non-evidence daily dataset. It must stay separate from `data/processed/` and the evidence dashboard. It contains no fish-kill labels, coordinates, real event dates, or risk scores and cannot satisfy the Section 6 gate.

**Synthetic gap-filled status:** complete as a quarantined database and 24/48/72-hour training run. It fills all ten structural checks in the synthetic scope, but the real gate remains **2 pass, 8 fail**. It must stay separate from `data/processed/`, `models/model.joblib`, and the real evidence bundle.

**Synthetic base model status:** complete as a quarantined event-overlay demonstration. It must stay separate from `data/processed/`, `models/model.joblib`, and the evidence dashboard. Its metrics are not real performance and cannot satisfy the Section 6 gate. The 24-hour false positives are mostly early detections, so any future real evaluation needs an explicit lead-time policy.

**Synthetic presentation model status:** complete as a quarantined five-input demo for team presentations. It is in `models/synthetic/presentation/` and `reports/tables/synthetic_presentation_model_*`. Its Low/Medium/High bands are communication labels, not validated risk thresholds. It must stay separate from `data/processed/`, `models/model.joblib`, and the evidence dashboard.

**Synthetic prototype status:** complete as a quarantined software demonstration. It must stay separate from `data/processed/`, `models/model.joblib`, and the evidence dashboard. Its metrics are not real performance and cannot satisfy the Section 6 gate.

**Decision needed from the project owner:** whether and when to reopen external data acquisition. The current working scope is the **feasibility-and-simulation** framing under D-009: evidence audit, readiness gate, descriptive annual trend, and quarantined synthetic pipeline as separate contributions. Do not train a **real-data fish-kill** model or add a **real** risk score until the Section 6 gate passes. The descriptive annual trend model is outside that gate and must remain descriptive only.
