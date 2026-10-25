# HIMPIL Phase 1–8 consolidated report

**Project:** HIMPIL — A Machine Learning-Based Early Warning and Advisory System for Fish Kill Events in Laguna de Bay

**Prepared:** 23 October 2026

**Status:** Data, statistical analysis, dashboard, and evidence audit complete. Real-data supervised fish-kill prediction is **blocked** because the supplied evidence is insufficient. A quarantined synthetic base dataset mirrors the real station/year/schema frame, a separate synthetic base model exercises an event overlay, and a generic prototype demonstrates the software pipeline; all three are **not evidence**.

---

## 1. Executive summary

The supplied files were inspected without modifying them. They contain:

- six LLDA water-quality workbooks with **annual station summaries** for 2016–2025;
- two PAGASA workbooks with **monthly station summaries** for 2016–2025;
- two PDF reports, two Word proposal documents, one React UI archive, and one archived 2019 university news article.

The project produced:

- a documented inventory of 14 sources;
- a 3,400-row long water-quality table;
- a 150-row lake station-year table, of which 111 are complete across six variables;
- 7,008 rainfall rows and 7,260 wind rows;
- one accepted fish-kill event report covering Biñan and Pila in May 2019;
- a matching audit showing that no observation can be used as a pre-event predictor;
- a blocked label specification and a header-only real modelling schema;
- guarded real training and evaluation scripts that refuse to produce a real model or real metrics;
- three R analysis scripts with descriptive tables and figures;
- a five-section React/Vite dashboard built from the supplied interface shell and rebuilt as an evidence-first research brief;
- a contract test suite;
- a quarantined synthetic base dataset on the real 15-station/2016–2025 frame: 54,795 daily station-days, 10,959 weather rows, 900 annual anchors, CSV + SQLite, a data dictionary, and a calibration report;
- a separate quarantined synthetic base model with an event overlay, 20 synthetic events, 10 stress-only periods, chronological 24/48/72-hour models, metrics, event detection, diagnostics, model card, and report;
- a separate quarantined generic synthetic prototype with a generator, chronological models, metrics, model card, and report.

All three synthetic artifacts are **simulation only — not evidence**.

No real-data model was trained. No real probability, risk category, accuracy, precision, recall, F1, confusion matrix, ROC curve, or PR-AUC value exists. The only model artifacts and metrics are synthetic, live in `models/synthetic/` and `reports/tables/synthetic_*`, and are not connected to the dashboard. The synthetic base dataset itself contains no labels and no model; the base model is a separate event overlay.

---

## 2. Phase 1 — Source inspection

The full manifest is in [`reports/tables/source_manifest.md`](tables/source_manifest.md); the machine-readable inventory is [`reports/tables/source_inventory.csv`](tables/source_inventory.csv). SHA-256 values are recorded for every source.

| ID | Source | Organization / date | Reporting period | Content | Incident or label value |
|---|---|---|---|---|---|
| S01 | Rainfall workbook | PAGASA/DOST; data as of 2026-07-09 | 2016–2025; 2025 incomplete | Monthly station totals | No labels |
| S02 | Nitrate workbook | LLDA/DENR; data as of 2026-07-28 | 2016–2025 | Annual station summaries | No labels |
| S03 | Phosphate workbook | LLDA/DENR; data as of 2026-07-28 | 2016–2025 | Annual station summaries | No labels |
| S04 | BOD workbook | LLDA/DENR; data as of 2026-07-28 | 2016–2025 | Annual station summaries | No labels |
| S05 | pH workbook | LLDA/DENR; data as of 2026-07-28 | 2016–2025 | Annual station summaries | No labels |
| S06 | Temperature workbook | LLDA/DENR; data as of 2026-07-28 | 2016–2025 | Annual station summaries | No labels |
| S07 | DO workbook | LLDA/DENR; data as of 2026-07-28 | 2016–2025 | Annual station summaries | No labels |
| S08 | Wind workbook | PAGASA/DOST; data as of 2026-07-09 | 2016–2025; 2025 incomplete | Monthly station values | No labels |
| S09 | `AWQR_2009-2012.pdf` | LLDA/DENR; report 2009–2012; PDF created 2013-11-29 | 2009–2012 | Annual water-quality report | Background only |
| S10 | `sustainability-16-10521.pdf` | *Sustainability*; 2024-11-30 | Review of 1972–2023 | Narrative review and event tables | Aggregate and conflicting Laguna evidence; no usable event rows |
| S11 | `PROPOSAL_-HIMPIL-1.docx` | Undated; metadata 2026-10-19 | Not applicable | Research proposal | No data |
| S12 | `HIMPIL.docx` | Undated; AY 2026–2027 stated | Not applicable | Topic-discovery form | No data |
| S13 | `himpil-ui.zip` | Not stated | Not applicable | React/TypeScript prototype | Design only |
| S14 | Archived UPD article | UP Diliman; byline 2019-06-10; page also shows 13 June | 2019-05-04 to about 2019-05-31 | Institutional news report with LLDA interview and sample table | One reported event; not independent verification |

### Critical findings from inspection

1. The LLDA workbooks are **not daily observations**. Each row is a station-year summarised value. The source does not state whether the annual value is a mean, maximum, or another statistic.
2. PAGASA rainfall and wind are **monthly station summaries**, not daily records. The 2025 sheets are provisional and incomplete: seven stations have all 12 months, while the rest have January–June values only. The source says remaining synoptic data are still undergoing verification.
3. No source contains station coordinates, a station-to-zone crosswalk, or an authoritative lake-zone boundary layer.
4. Only 5 of the 15 lake station labels contain an explicit bay name. The other 10 have no zone label in the supplied data.
5. The review's 1972–1998 Laguna statement is an aggregate. It was not expanded into invented individual incidents.
6. The review's 2021 "Laguna de Bay" row cites an article about Sampaloc Lake, a different waterbody. It was excluded pending verification.
7. The 2019 UPD article supplies one event report, not a formal LLDA/BFAR investigation report.

The Word documents are proposals, not data. The ZIP is an interface design. The 2009–2012 report is outside the main 2016–2025 period and contains annual summaries.

### Water-quality coverage

| Variable | Lake station-years with numeric value | Missing | Missing % |
|---|---:|---:|---:|
| Nitrate | 120 | 30 | 20.0 |
| Phosphate | 120 | 30 | 20.0 |
| BOD | 120 | 30 | 20.0 |
| pH | 120 | 30 | 20.0 |
| DO | 120 | 30 | 20.0 |
| Water temperature | 111 | 39 | 26.0 |

There are 150 lake station-years and 111 are complete across all six variables. Water temperature is missing for 2017 for the nine long-running stations because the source uses the undefined `...` marker. Missing cells remain blank and are flagged; they are never replaced with zero.

### Weather coverage

| Variable | Numeric station-month cells | Total cells | Missing % | Note |
|---|---:|---:|---:|---|
| Rainfall | 6,282 | 7,008 | 10.36 | 2025 partial and provisional; 7 stations complete |
| Wind speed | 6,288 | 7,260 | 13.39 | 2025 partial and provisional; 7 stations complete |

The weather rosters contain 57–64 stations per year. They are nationwide PAGASA stations, not a lagoon-wide sample. No weather station has coordinates in the source.

### Station-label issue

There are 59 distinct water-quality station labels: 15 lake and 44 tributary. pH/temperature omit four tributary sites, and nutrients/BOD use "Angono" where pH/temperature/DO use "Angono River". These labels were not merged automatically. A documented crosswalk is required before any combined station analysis.

---

## 3. Phase 2 — Documented fish-kill events

The event table is [`data/processed/historical_fish_kill_events.csv`](../data/processed/historical_fish_kill_events.csv). It uses the 17 supported columns requested in the task. Unknown fields are blank.

### Accepted record

**One report, stored as one event to avoid double-counting:**

- **Event ID:** `HIMPIL-FK-2019-001`
- **Location:** Biñan and Pila, Laguna (Laguna de Bay)
- **Start:** 2019-05-04 (Biñan); Pila/Linga began 2019-05-12
- **End:** approximately 2019-05-31; the source only says "until the end of May"
- **Lake zone:** blank — the source gives no zone label or coordinates
- **Species:** tilapia; bangus (milkfish)
- **Losses:** approximately 500,000 fish reported dead in Biñan (fisherman's estimate); in Barangay Linga, Pila, 60% of tilapia and 80% of bangus in cages were reported killed. No complete count.
- **Economic loss:** blank — no peso value is reported
- **Cause wording:** "Green tide (freshwater algal bloom) causing oxygen deficiency/asphyxia; attributed to an LLDA senior science research specialist quoted in the article."
- **Verification:** one institutional news report with named LLDA attribution and a water-quality table; not a formal LLDA investigation and not independently corroborated in the supplied files.

The 29 May 2019 Biñan sample is stored separately as **during-event context**:

| Variable | Value | Unit |
|---|---:|---|
| Dissolved oxygen | 4.7 | mg/L |
| Ammonia | 0.16 | mg/L |
| Nitrate | 0.4 | mg/L |
| Phosphate | 1.00 | mg/L |

It is not a pre-event measurement and is never used as a predictor.

### Evidence audit

| Candidate | Decision | Reason |
|---|---|---|
| "Fish kills in Laguna de Bay were reported in the 1930s" | excluded | No year, date, location within the lake, count, loss, or cause |
| "From 1972 to 1998, 60% ... low DO; 80% ... May–September" | excluded | Aggregate statement; cannot become individual events |
| Table 3 row "2021 Jan. Laguna de Bay / Tilapia / Low DO" | excluded pending verification | The row's citation concerns Sampaloc Lake, a different waterbody |
| "Massive fish kill in Biñan and Pila ... 2019" | accepted as reported event | Dated, located, sourced; verification limits recorded |

The aggregate 1972–1998 statement was not converted into 27 annual records or dozens of incidents.

---

## 4. Phase 3 — Environmental matching

Reports:

- [`reports/tables/matching_report.md`](tables/matching_report.md)
- [`data/processed/incident_environmental_matches.csv`](../data/processed/incident_environmental_matches.csv)
- [`data/processed/incident_context_measurements.csv`](../data/processed/incident_context_measurements.csv)

### Result

| Match question | Result |
|---|---|
| Accepted event records | 1 |
| Context observation rows | 4 |
| Events with any matched observation | 1 |
| Events with a pre-event environmental observation | 0 |
| Predictive matches usable now | 0 |
| Successfully matched pre-event incident | None |

The 29 May sample matches the event municipality and falls inside the event period. It is a **during-event** observation. The LLDA 2019 annual summaries overlap the event year but have no observation dates and no Biñan/Pila station. The May 2019 PAGASA monthly summaries overlap the event month but have no linked station and no daily resolution. Neither can establish what was known before 4 May 2019.

### Temporal relationship

| Observation | Relationship to event | Usable as a predictor? |
|---|---|---|
| 29 May 2019 Biñan sample | during event | No |
| LLDA 2019 annual station summaries | annual period contains event | No |
| PAGASA May 2019 monthly values | monthly period contains event | No |

No post-event value was used as if it were available earlier.

### Geographic mismatch

No LLDA lake station is labelled Biñan or Pila. No PAGASA station is named Biñan or Pila. Five of 15 lake stations carry a bay name; ten do not. With no coordinates and no authoritative crosswalk, choosing a "nearest" station would be an assumption, not a documented match.

---

## 5. Phase 4 — Supervised learning feasibility

The generated readiness assessment is in [`reports/tables/feasibility_report.md`](tables/feasibility_report.md). Ten checks were run: eight failed, one was partial, and one passed.

| Check | Result | Evidence |
|---|---|---|
| At least two independent event periods | Fail | One event period (May 2019) |
| Independent corroboration | Partial | One institutional news report |
| Exact event start date | Pass | Biñan 4 May; Pila 12 May |
| Dated station-monitoring observations | Fail | 0 dated monitoring rows; annual summaries only. The article supplies one during-event sample, not a pre-event series. |
| Pre-event environmental match | Fail | 0 usable pre-event matches |
| Station coordinates and zone mapping | Fail | 0 coordinates; 5/15 zone labels |
| Credible non-event windows | Fail | No incident-reporting completeness log |
| Class-imbalance-aware evaluation | Fail | 1 event period; no 24-hour negatives |
| 24-hour horizon supported by sampling frequency | Fail | Annual water; monthly weather |
| Enough observations for chronological validation | Fail | One event period and one event year |

### Why the event year does not create negatives

There are 135 lake station-years outside 2019, but they cannot be called non-events. No supplied file establishes that fish kills were monitored and absent in those windows. Absence of a published report is not evidence of absence.

### Class imbalance

Class balance cannot be estimated because there are **0 usable positive labels and 0 usable negative labels** at the proposed 24-hour horizon. Reporting a class ratio would be an invented result.

### Conclusion

Supervised classification is not scientifically defensible with the current evidence. The blocker is not software or computing capacity; it is the absence of dated observations, event labels, spatial linkage, and reporting completeness.

---

## 6. Phase 5 — Prediction target

The target specification is [`reports/tables/label_specification.md`](tables/label_specification.md). It is marked **NOT ACTIVE**.

`fish_kill_within_24h` was **not generated**. The intended definition would be:

- one station-zone observation at timestamp `t`;
- positive if a documented incident starts in the same zone in `(t, t + 24 hours]`, or if a verified incident is already ongoing;
- negative only when a dated incident-reporting log covers the same zone and window and records no incident;
- ambiguous cases excluded;
- one event contributes one positive window per prediction timestamp, not one per article;
- every feature's source timestamp must be no later than `t`.

This cannot be applied because:

- water quality is annual;
- weather is monthly;
- there is one event period;
- no observation is dated before the event;
- no event-to-zone mapping exists;
- no reporting-completeness record supports negatives.

The modelling schema [`data/processed/modeling_dataset.csv`](../data/processed/modeling_dataset.csv) is header-only. It contains 17 columns, including `fish_kill_within_24h` and `label_status`, but **zero data rows** and zero label values.

A 48- or 72-hour target is even less supported. Moving to an annual target would not fix the problem because there is still one event year and no credible negative reporting.

---

## 7. Phase 6 — Python machine-learning pipeline

Required scripts exist:

| Script | Purpose | Current result |
|---|---|---|
| `python/inspect_data.py` | Workbook inventory and quality checks | Complete |
| `python/extract_incidents.py` | Conservative event extraction | 1 accepted reported event |
| `python/clean_data.py` | Source-preserving cleaning | 3,400 water-quality rows; 14,268 weather rows |
| `python/match_environmental_data.py` | Date/location/unit matching and temporal audit | 0 predictive matches |
| `python/prepare_labels.py` | Feasibility and guarded label schema | Labels blocked |
| `python/train_model.py` | Guarded training entry point | Refused; 8/10 checks fail |
| `python/evaluate_model.py` | Guarded evaluation entry point | Unavailable; 3/3 checks fail |

`train_model.py` imports scikit-learn and records the available candidate estimators (Dummy Classifier, Decision Tree, Random Forest), but it does not fit any of them. The T1 and T3 checks pass only because the empty schema file and target column exist; the other eight checks fail.

`evaluate_model.py` checks for:

1. a labelled modelling dataset;
2. `models/model.joblib`;
3. `data/outputs/test_predictions.csv`.

All three are absent. No real-data precision, recall, F1, confusion matrix, ROC, or PR-AUC value is reported. `models/model.joblib` does not exist.

The separate `sandbox/synthetic/build_base_dataset.py` produces a daily synthetic base dataset on the real 15-station/2016–2025 frame, calibrated to the real annual anchors and included in `data/synthetic/base/`. It contains no fish-kill labels and trains no model. The separate `sandbox/synthetic/train_base_model.py` injects known synthetic events into a copy of that panel and trains 24/48/72-hour models in `data/synthetic/base_model/` and `models/synthetic/base_model/`. The separate `sandbox/synthetic/run_prototype.py` demonstrates the modelling mechanics on a generic synthetic world and writes to `data/synthetic/synthetic_*`, `models/synthetic/`, and `reports/tables/synthetic_prototype_*`. None of these scripts can satisfy the real-data gate or change the verdict above.

### Chronological design reserved for future data

- Sort by known observation timestamp.
- Train on earlier periods, validate on a later period, test on the latest untouched period.
- Group all observations from one event and adjacent windows into the same split.
- Compare a majority-class baseline with a Decision Tree and Random Forest.
- Report precision, recall, F1, confusion matrix, PR-AUC, false alarms, and missed events.
- Report event counts and uncertainty, not only point estimates.

This design was not executed because there are no labelled rows.

---

## 8. Phase 7 — R statistical analysis

R 4.6.1 is installed. The analysis uses documented CSVs from Python, not the Excel files.

Scripts:

- [`r/exploratory_analysis.R`](../r/exploratory_analysis.R)
- [`r/environmental_trends.R`](../r/environmental_trends.R)
- [`r/model_evaluation.R`](../r/model_evaluation.R)
- [`r/install_packages.R`](../r/install_packages.R)

### Exploratory analysis

Outputs include [`reports/tables/r_eda_summary.md`](tables/r_eda_summary.md) and 13 figures in `reports/figures/`.

Key descriptive facts:

- numeric DO values range from **6.25 to 9.10 mg/L** across annual lake station-years;
- median DO is **7.70 mg/L**;
- 120 DO station-years are numeric;
- 111 lake station-years are complete across six variables;
- rainfall is strongly seasonal in the PAGASA network, but the stations are not a probability sample of Laguna de Bay;
- water temperature is absent for 2017 for every long-running lake station.

These are annual summaries, not daily conditions.

### Environmental trends

Method:

- ordinary least squares of value on year for stations with at least five numeric annual values;
- Kendall tau also reported;
- Benjamini–Hochberg adjustment within each variable;
- unweighted station-network means;
- weather trends restricted to station-years with 12 numeric months, 2016–2024.

| Variable | Stations tested | Raw p < 0.05 | BH q < 0.05 |
|---|---:|---:|---:|
| BOD | 15 | 0 | 0 |
| DO | 15 | 6 | 4 |
| Nitrate | 15 | 2 | 0 |
| Phosphate | 15 | 0 | 0 |
| Water temperature | 15 | 0 | 0 |
| pH | 15 | 3 | 0 |

Four DO stations had a BH-adjusted negative slope below 0.05:

| Station | Slope (mg/L per year) | BH q |
|---|---:|---:|
| Stn XVI - Sta. Rosa | −0.174 | 0.0011 |
| Stn IV - Central Bay | −0.156 | 0.0342 |
| Stn XV - San Pedro | −0.152 | 0.0342 |
| Stn I - West Bay | −0.128 | 0.0011 |

This is a descriptive statistical result. It is based on at most 10 annual points per station and does not model serial correlation, sampling changes, or within-year timing. It is not a fish-kill mechanism and not a model-evaluation result.

### Model evaluation in R

`r/model_evaluation.R` writes [`reports/tables/r_model_evaluation_notes.md`](tables/r_model_evaluation_notes.md) with status **not available**. It will only create a confusion matrix or PR curve if a real `data/outputs/test_predictions.csv` exists with both `y_true` and `y_score`. No evaluation figure was fabricated.

---

## 9. Phase 7 — Dashboard

The interface started from the supplied `himpil-ui.zip` shell after removing its unused Figma deployment configuration. It was then rebuilt as an editorial research brief with five evidence-first sections. The old sidebar, decorative lake map, disabled risk controls, advisory placeholder, settings page, and empty performance widgets were removed. The explicit “risk assessment unavailable” state remains visible in the persistent notice, the overview status ticket, the header status pill, and the model-status section.

The visual hierarchy now uses a warm paper palette, serif display headings, numbered sections, tabular metadata, and dark green status surfaces. The overview opens with a status ledger showing the model, verified-event, and dated-observation counts before any descriptive content. The water page adds a monthly weather-context panel and a three-plate gallery of outputs from the R workflow. The evidence page includes a four-step verification ladder. The model page adds a readiness meter above the ten checks.

### Sections implemented

| Section | Connected content |
|---|---|
| Overview | Coverage, latest annual DO/temperature/rainfall/wind summaries, the evidence boundary, and the reported 2019 event |
| Water data | Six annual water-quality measures, network mean and station range, station-by-year table, missing-value display, CSV export, annual weather context, and three supporting R figures |
| Fish-kill evidence | The single reported event, source wording, date/location precision, a four-step verification ladder, verification limits, and the four-claim audit |
| Model status | No-model status, three blocking counts, a readiness meter, 10 readiness checks, guarded-code refusals, absent-metrics statement |
| Sources | All 14 source records, periods, contents, label suitability, data-quality notes, and provenance limits |

Navigation uses direct hash routes (`#overview`, `#water`, `#evidence`, `#model`, `#sources`). Refresh and browser history therefore work without a routing library. The responsive layout was checked at 1440, 1024, and 390 px emulated widths across every route with no horizontal page overflow, console errors, or missing figures.

### Data connection

`python/build_dashboard_data.py` reads the cleaned CSVs and guard statuses and writes `dashboard/src/data/dashboard.json`. The bundle contains:

- 15 lake stations and 150 station-years;
- 711 numeric lake station-year-variable values;
- one reported event and zero independently verified events;
- 14 source records;
- three supporting R figures (completeness, nutrient/BOD distributions, and rainfall);
- model status “Not trained — training and evaluation guards refused”.

The dashboard does **not** display a risk level, probability, confidence score, fake live reading, fake incident count, or fake metric. It does not assign events to stations or lake zones because no coordinates or authoritative crosswalk were supplied.

### Build

```powershell
.\.venv\Scripts\python.exe python\build_dashboard_data.py
cd dashboard
npm install
npm run build
```

The production build and preview were verified locally. A browser check exercised all five hash routes at 1440, 1024, and 390 px emulated widths with no horizontal page overflow, console errors, or missing figures. The UI shows blank values as blanks and keeps the risk-unavailable state visible on every section. The station-level dissolved-oxygen plate remains in `reports/figures/` and is intentionally not duplicated in the interface.

---

## 10. Phase 8 — Tests and validation

The test suite is [`tests/test_pipeline.py`](../tests/test_pipeline.py).

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests cover:

- byte-identical copies of the eight original workbooks;
- exact event CSV schema and blank unknown values;
- rejection of aggregate and conflicting incident claims;
- missing values retained as blanks and flags;
- provisional, incomplete 2025 weather;
- no during-event observation used as a predictor;
- blocked real 24-hour labels and an empty real modelling schema;
- real training and evaluation guard refusals;
- dashboard-to-evidence agreement, the refreshed Overview's real request counts, the three-figure bundle, and absence of absolute user paths;
- presence of the data-request package and its unsent status;
- presence of required reports and R outputs;
- synthetic quarantine: base-dataset and prototype data-origin markers, the simulation-only warning, the synthetic model card, and the absence of synthetic rows in the real dashboard and real model path;
- synthetic-base calibration: 15 real station labels, 2016-2025 coverage, 54,795 daily station-days, 10,959 weather rows, 900 anchors, the SQLite tables, and a maximum annual-mean calibration error below `0.01`;
- synthetic base-model quarantine: 20 event periods, 10 stress-only periods, 54,795 overlay rows, 24/48/72-hour metrics, event detection, diagnostics, model artifacts, and the absence of overlay markers in the real dashboard.

Final verification: the suite reports **15/15 tests passed**. The dashboard build completes successfully, and the browser check finds no console errors or runtime exceptions.

---

## 11. What the project can and cannot claim

### Can claim

- The 2019 UPD article reports a fish kill in Biñan and Pila during May 2019.
- The supplied LLDA data are annual station summaries, not daily observations.
- The supplied PAGASA data are monthly station summaries.
- Lake water-quality station-years cover 2016–2025 and are incomplete for some variables.
- One during-event sample exists; no pre-event sample exists.
- No scientifically valid 24-hour supervised target can be constructed from the current real files.
- No real-data model was trained and no real performance metric exists.
- A synthetic base dataset can exercise daily joins and schema work, but every daily value is generated.
- A synthetic base model can exercise an event-overlay modelling pipeline, but its labels and metrics describe the injection only.
- A synthetic prototype can exercise the software pipeline, but its metrics describe the simulation only.
- Descriptive annual trends can be calculated with explicit uncertainty and aggregation caveats.

### Cannot claim

- That a fish kill definitely occurred or did not occur in any unrecorded window.
- That the 2019 cause was formally established by an investigation.
- That any station, zone, or weather station is the correct spatial match for Biñan/Pila.
- That the annual values are daily, monthly, or event-window conditions.
- That the system can predict fish kills within 24, 48, or 72 hours.
- That any real risk category, probability, accuracy, precision, recall, F1, or AUC is valid.
- That the synthetic base model’s metrics, feature importances, or event dates are real.
- That the synthetic base model satisfies the model-readiness gate or supports a public warning.
- That the synthetic prototype’s metrics, feature importances, or event dates are real.
- That the synthetic prototype satisfies the model-readiness gate or supports a public warning.
- That the absence of a news report proves a safe period.
- That the dashboard is an official warning service.

---

## 12. Required data before the next phase

A field-level request package is available in [`reports/data_requests/`](data_requests/README.md). It contains nine requests, four ready-to-complete letters, an adviser approval template, a request matrix, a permissions-and-ethics record, decision rights, and an access log. **One LLDA incident-records request has been submitted and acknowledged; LLDA requested professor approval letters. No data have been received and no data-sharing permission has been recorded.** The submitted request text is preserved in [`submissions/LLDA_incident_request.md`](data_requests/submissions/LLDA_incident_request.md); eight requests remain planned. Receipt will be logged separately from preparation; no new file will enter the processed data until its hash, fields, units, QA flags, station identity, and permission conditions are documented.

1. **Dated incident log** from LLDA/BFAR with site, zone, start/end, species, losses, investigation status, and source.
2. **Dated water-quality observations** at daily or finer resolution, with station coordinates.
3. **Daily/hourly weather** from PAGASA or another documented source, linked to each station or zone.
4. **Authoritative lake-zone boundaries and a station-to-zone crosswalk.**
5. **Reporting-completeness records** covering both event and non-event windows.
6. **At least two independent event periods** for a chronological split; substantially more for credible validation.
7. **Confirmation of the 2024 DO note** in the source workbook, which currently says “2014 water quality data is only from January to June” and is probably a typo.

After those arrive, the sequence is: inspect the new sources → update the station/zone dictionary → regenerate dated observations → write a new label specification → re-run the readiness checks → only then fit a baseline, Decision Tree, and Random Forest.

None of the three synthetic artifacts shortens this sequence. They are separate sandboxes and cannot supply any of the seven real-data items.

---

## 13. Deliverable index

| Deliverable | Location |
|---|---|
| Incident CSV | `data/processed/historical_fish_kill_events.csv` |
| Evidence audit | `data/processed/incident_evidence_audit.csv` |
| Source inventory | `reports/tables/source_inventory.csv`, `source_manifest.md` |
| Data-quality report | `reports/tables/cleaning_report.md`, `data_quality_report.csv` |
| Matching report | `reports/tables/matching_report.md` |
| Feasibility report | `reports/tables/feasibility_report.md` |
| Label specification | `reports/tables/label_specification.md` |
| Python pipeline | `python/*.py` |
| R analysis | `r/*.R`; `reports/tables/r_*.csv`; `reports/figures/fig_*.png` |
| Dashboard | `dashboard/` |
| Data request package | `reports/data_requests/` |
| Synthetic base dataset | `data/synthetic/base/`; `reports/tables/synthetic_base_*`; `sandbox/synthetic/build_base_dataset.py` |
| Synthetic base model | `data/synthetic/base_model/`; `models/synthetic/base_model/`; `reports/tables/synthetic_base_model_*`; `sandbox/synthetic/train_base_model.py` |
| Synthetic prototype | `sandbox/synthetic/`; `data/synthetic/synthetic_*`; `models/synthetic/`; `reports/tables/synthetic_prototype_*` |
| Tests | `tests/test_pipeline.py` |
| Run instructions | `README.md` |

The original workbooks in `datasets/` remain unchanged. Real processed data are stored separately in `data/processed/`. No real model artifact was created. Synthetic model artifacts are isolated in `models/synthetic/` and are explicitly marked simulation only.

---

## 14. Addendum — synthetic prototype (non-evidence)

> **SIMULATION ONLY — NOT EVIDENCE**

The team added a quarantined synthetic prototype because real data access is still pending. It exists so the pipeline can be tested, reviewed, and explained without pretending the evidence gap is closed.

| Item | Synthetic prototype |
|---|---|
| Generator | `sandbox/synthetic/run_prototype.py` |
| Simulated panel | 8,766 station-days, 6 synthetic stations, 2021–2024 |
| Simulated event periods | 8, with 3 additional high-stress no-event periods |
| Targets | Simulated event start within 24, 48, or 72 hours |
| Split | Chronological: train 2021–2022, validation 2023, test 2024 |
| Models | Majority-class baseline, logistic regression, random forest |
| Report | `reports/tables/synthetic_prototype_report.md` |
| Model card | `reports/tables/synthetic_model_card.md` |
| Quarantine | `data/synthetic/` and `models/synthetic/`; not connected to the dashboard |
| Gate status | Does **not** satisfy any Section 6 item |

The prototype’s metrics are properties of the generator. They must not be quoted as real HIMPIL performance, used to justify an advisory, or placed on a real Laguna de Bay map. The real-data dashboard continues to show **risk assessment unavailable**, and the real guard scripts still refuse with exit code 2.

---

## 15. Addendum — synthetic base dataset (non-evidence)

> **SIMULATION ONLY — NOT EVIDENCE**

The requested synthetic base dataset is in `data/synthetic/base/`. It uses the real station/year/variable frame so the team can test daily joins, schema handling, database queries, and dashboard prototypes without pretending the evidence gap is closed.

| Item | Synthetic base dataset |
|---|---|
| Generator | `sandbox/synthetic/build_base_dataset.py` |
| Stations | 15 real lake station labels |
| Calendar | 2016-01-01 to 2025-12-31 |
| Daily water-quality rows | 54,795 station-days |
| Variables | Nitrate, phosphate, BOD, pH, water temperature, dissolved oxygen |
| Weather | 10,959 daily rows across three synthetic weather zones |
| Annual anchors | 900 station-year-variable rows; 621 real, 90 provisional 2025, 189 flagged imputations |
| Calibration | Maximum absolute annual-mean error **0.000464** in the current build |
| Formats | CSV, SQLite with a long-format view, data dictionary, manifest |
| Report | `reports/tables/synthetic_base_report.md` |
| Quarantine | `data_origin = synthetic_base_v1`; no dashboard connection |
| Labels | None; no fish-kill labels, real event dates, coordinates, or risk scores |
| Gate status | Does **not** satisfy any Section 6 item |

The base dataset is not an input to the generic model prototype and must not be presented as a real Laguna de Bay dataset. Its daily values are generated even where the station labels and annual anchors are real.

---

## 16. Addendum — synthetic base model (non-evidence)

> **SIMULATION ONLY — NOT EVIDENCE**

The synthetic base model is a separate event-overlay exercise built from the base panel. It exists to test the modelling pipeline end to end, not to make a claim about Laguna de Bay. The base dataset itself is unchanged.

| Item | Synthetic base model |
|---|---|
| Script | `sandbox/synthetic/train_base_model.py` |
| Panel | 54,795 rows; 53,950 model-eligible rows |
| Events | 20 synthetic event periods; 10 high-stress no-event periods |
| Event shape | Four-day pre-event ramp, three-day event, five-day recovery |
| Targets | Event start within 24, 48, or 72 hours at the same station |
| Split | Train <2023, validation 2023, test 2024–2025 |
| Models | Majority-class baseline, logistic regression, random forest |
| Test 24h random forest | Precision 0.455; recall 1.000; F1 0.625; PR-AUC 0.568; Brier 0.0020 |
| Test 48h random forest | Precision 0.597; recall 1.000; F1 0.748; PR-AUC 0.957; Brier 0.0021 |
| Test 72h random forest | Precision 0.670; recall 0.983; F1 0.797; PR-AUC 0.947; Brier 0.0026 |
| Event detection | All 4 synthetic test events flagged by at least one 24-hour alert |
| Report | `reports/tables/synthetic_base_model_report.md` |
| Model card | `reports/tables/synthetic_base_model_card.md` |
| Gaps and to-do | `reports/tables/system_gaps_and_todo.md` |
| Quarantine | `data_origin = synthetic_base_v1_event_overlay`; no dashboard connection |
| Gate status | Does **not** satisfy any Section 6 item |

The metrics are optimistic by construction because the event effect is injected into the same variables used as features. The event overlay changes annual means for affected station-years, so the base calibration audit does not apply to the overlay. The 24-hour model's false positives are mostly early detections two to three days before synthetic events, which the 24-hour label counts as negative. The test period has only four synthetic events and 20 positive 24-hour rows. The output cannot be used as real performance, a real lead time, a real risk score, or an advisory.

---

## 17. Addendum - external outreach paused (2026-10-23)

> **Scope update, not a new result.**

The team has paused external data acquisition, including the LLDA follow-up, to concentrate on simulation-based learning, dashboard work, and paper revision. This is decision **D-009** in `README_WORKPLAN.md`.

| Item | Status after the pause |
|---|---|
| `LLDA-INC-01` | `acknowledged`; no files, no permissions, not closed |
| Other eight requests | `planned`; not sent |
| Real model | Still not trained; `models/model.joblib` absent |
| Evidence dashboard | Still **“risk assessment unavailable”** |
| Synthetic artifacts | Unchanged; simulation only |
| Model-readiness gate | Unchanged; pausing outreach does not lower it |

The paper must be revised to a **feasibility-and-simulation** framing if the team keeps this scope. It should present the evidence audit, the readiness gate, and the synthetic pipeline as separate contributions, and it must not claim a real early-warning system, a real risk score, or real model performance. The pause is reversible; if outreach resumes, the original request record and gate remain in place.

---

## 18. Addendum - dashboard refresh completed (2026-10-23)

> **Presentation update, not a new evidence result.**

The five-page evidence dashboard was refreshed into a denser decision-support layout without changing any evidence claim.

| Item | Status after the refresh |
|---|---|
| Overview | Dark status hero, four KPI cards, year chips, variable/station filters, station-year completeness heatmap, selected-variable annual trend, latest annual signals, and status rails |
| Data-request rail | Reads the access log: **9** total, **1 acknowledged**, **8 planned**, **0 received**, **0 files**; outreach paused under D-009 |
| Heatmap | Counts distinct reported variables per station-year; blank/hatched cells are not zero |
| Risk state | Still **“risk assessment unavailable”**; no risk score, zone risk map, or advisory was added |
| Synthetic data | Still absent from the evidence dashboard and bundle |
| Verification | `npm run build` passes; **15/15** contract tests pass; production preview checked at 1440, 1024, and 500 px; heatmap scrolls inside its panel at narrow widths |
| Next work | P6-1: completed in addendum 19 (lead-time policy for the synthetic 24-hour model); labeled **SIMULATION ONLY - NOT EVIDENCE** |

The refresh is a communication improvement only. It does not satisfy the Section 6 gate, does not provide a real prediction, and does not change the verdict that the original operational goal is unmet.

---

## 19. Addendum - synthetic lead-time policy experiment (2026-10-23)

> **SIMULATION ONLY - NOT EVIDENCE**

The first P6 learning experiment asks whether the saved 24-hour synthetic model's early alerts can be treated as a 2-3 day warning without adding false event alarms. It is a post hoc policy exercise on the synthetic event-overlay model, not a study of Laguna de Bay and not a validated warning rule.

| Item | Result |
|---|---|
| Script | `sandbox/synthetic/lead_time_policy.py` |
| Input model | `models/synthetic/base_model/random_forest_24h.joblib` |
| Threshold | `0.5`; inherited from the saved model, not tuned |
| Lead window | 72 hours before a synthetic event start |
| Test raw alerts | **44** station-days: 20 target-day, 23 early pre-event, 1 stress-only |
| Recommended illustrative policy | **2 stations** confirm on the same day; **72-hour cooldown** |
| Test result | **4** episodes; **4/4** events detected; **0** false episodes; leads **2-3** days |
| Validation result | **2** episodes; **2/2** events detected; **0** false episodes; leads **1-2** days |
| 1-station / 72h test | **5** episodes; **4/4** detected; **1** stress-only false episode; **3**-day leads |
| 3-station / 72h test | **4** episodes; **4/4** detected; **0** false episodes; **2**-day leads |
| Raw alert burden | Unchanged at **44**; confirmation reduces issued episodes, not the underlying station-day errors |
| Outputs | `synthetic_lead_time_policy.csv`, `synthetic_lead_time_events.csv`, `synthetic_lead_time_policy_report.md` |
| Dashboard | Unchanged; no lead-time field, synthetic metric, risk score, or advisory was added |
| Gate status | Does **not** satisfy any Section 6 item |

The 23 pre-event rows are errors under a strict 24-hour label but are early signals under a 72-hour warning window. The experiment shows that the label horizon and the intended advisory lead time must match. It does not show that those alerts are correct warnings. A future real system should define the advisory lead time first, then train and evaluate against that horizon.

The policy was selected after inspecting the test error profile, so it is **post hoc**. The validation split is not an independent confirmation of the selected policy. There are only four synthetic test events and two validation events. The event effect is injected into the same variables used as features, so the probabilities are optimistic by construction. No confidence interval, threshold tuning, probability calibration, operational cost analysis, real daily observations, verified events, coordinates, or station-to-zone crosswalk was used. The result cannot be quoted as real performance or used for a real advisory.

The suite remains **15/15** contract tests; the dashboard build still passes. The experiment is quarantined from `data/processed/`, `models/model.joblib`, and `dashboard/src/data/dashboard.json`. Next: revise the paper to the feasibility-and-simulation framing, or optionally run a second P6 experiment (probability calibration or a model trained directly against a 72-hour label).

> **SIMULATION ONLY - NOT EVIDENCE**

---

## 20. Addendum - five-input synthetic presentation model (2026-10-24)

> **SIMULATION ONLY - NOT EVIDENCE**

The team asked for a trained model that can be shown in a presentation. This addendum documents a separate, presentation-only model built in the synthetic sandbox. It uses the five fields from the team's illustrative training-data table: dissolved oxygen, water temperature, pH, rainfall, and wind speed. It predicts the synthetic 72-hour event label and is not evidence about Laguna de Bay.

| Item | Result |
|---|---|
| Script | `sandbox/synthetic/train_presentation_model.py` |
| One-row demo | `sandbox/synthetic/predict_presentation.py` |
| Model | `models/synthetic/presentation/risk_demo_model.joblib` |
| Manifest | `models/synthetic/presentation/manifest.json` |
| Target | Synthetic event start within 72 hours at the same station |
| Inputs | DO, water temperature, pH, rainfall, wind speed |
| Train / validation / test rows | 37,750 / 5,395 / 10,805 |
| Test metrics | Precision **0.4032**, recall **0.8333**, F1 **0.5435**, PR-AUC **0.6947** |
| Test alerts | **124** station-days: 50 true positives, 74 false positives, 10 missed positive rows |
| Event detection | **4/4** synthetic test events; **2/2** validation events |
| Validation metrics | Precision **0.8571**, recall **0.6000**, F1 **0.7059**, PR-AUC **0.7451** |
| Display bands | Low `p < 0.25`; Medium `0.25 <= p < 0.50`; High `p >= 0.50` - communication labels only |
| Dashboard | Unchanged; no synthetic model, metric, band, risk score, or advisory was added |
| Gate status | Does **not** satisfy any Section 6 item |

### Example interface

These six rows are **fictional values from the team's slide**, not measurements. The team's example bands are also illustrative. The model uses a 72-hour horizon; the slide does not define its horizon.

| DO | Temp | pH | Rain | Wind | Simulated p(72h) | Demo band | Team example band |
|---:|---:|---:|---:|---:|---:|---|---|
| 7.2 | 27 | 7.5 | 2 | 12 | 0.0033 | Low | Low |
| 6.5 | 28 | 7.2 | 5 | 10 | 0.0811 | Low | Low |
| 4.8 | 30 | 7.0 | 15 | 8 | 0.4588 | Medium | Medium |
| 3.9 | 31 | 6.8 | 20 | 5 | 0.6366 | High | Medium |
| 2.1 | 33 | 6.5 | 30 | 3 | 0.7730 | High | High |
| 1.5 | 34 | 6.2 | 25 | 4 | 0.6699 | High | High |

The model agrees with five of the six illustrative bands. That is **not** an accuracy check: the team's labels were not derived from a validated rule, and changing the band thresholds changes the output label. The table is included only to show the interface.

### What the demo can and cannot do

It can show that the five requested inputs can be used in a reproducible machine-learning pipeline, and it can produce a simulated probability for a hypothetical row during a team presentation. It cannot predict real fish kills, provide a real risk level, justify an advisory, or satisfy the model-readiness gate.

Dissolved oxygen (`0.6262`) and water temperature (`0.2494`) dominate the synthetic feature importance. That is consistent with the project's hypothesis, but it is also built into the synthetic event effect. It is not a real Laguna de Bay finding.

The demo is a simplified model: its test F1 is **0.5435**, compared with **0.797** for the full-feature synthetic 72-hour random forest. The full model uses lags, rolling DO features, and weather context. The five-input demo is for an understandable presentation, not to replace the full synthetic model.

### Use

Read `reports/tables/synthetic_presentation_model_report.md` for the full metrics, feature importance, example table, and a five-minute presentation script. Run one hypothetical row with:

```powershell
.\.venv\Scripts\python.exe sandbox\synthetic\predict_presentation.py --do 4.8 --temp 30 --ph 7.0 --rain 15 --wind 8
```

For a browser version, run `sandbox/presentation_app/app.py` and open `http://127.0.0.1:8000`. It is a local-only standard-library app that loads the same saved model and writes no data. The first start may take a few seconds.

The output is a simulated 72-hour probability and an illustrative demo band. Every output must be labeled **SIMULATION ONLY - NOT EVIDENCE**. Do not add this model or its bands to the evidence dashboard.

The suite remains **15/15** contract tests; the dashboard build still passes. The model is quarantined from `data/processed/`, `models/model.joblib`, and `dashboard/src/data/dashboard.json`.

> **SIMULATION ONLY - NOT EVIDENCE**

---

## 21. Addendum - real Tanay rainfall context (2026-10-24)

The monthly PAGASA rainfall workbook (S01) supports a descriptive lake-area view, not a daily or 72-hour model. The evidence dashboard now shows **Tanay, Rizal**, the only supplied station clearly in the Laguna de Bay watershed. It is a regional proxy, not a lake measurement.

| Item | Value |
|---|---|
| Source | S01, `data/processed/rainfall_monthly.csv` |
| Complete years | **9** (2016–2024) |
| Latest complete annual total | **3,508.5 mm** in 2024 over 12 months |
| Partial 2025 | **680.01 mm** over 6 months (January–June); not an annual total |
| Monthly climatology | **12** months, each based on 9 complete years |
| Wettest monthly mean | July, **489.3 mm** |
| Driest monthly mean | March, **18.7 mm** |
| Dashboard location | Water data > Weather context > Lake-area station |
| Risk status | **Risk assessment unavailable**; no score, zone map, or advisory |
| Model input | **No.** Monthly station rainfall cannot support the required 72-hour resolution. |

The national PAGASA network cards remain separate: they are mean summaries across the supplied network, not lake-specific values. The Tanay panel is descriptive context only. It does not change the Section 6 gate, and it is not connected to the synthetic pipeline.

The contract suite remains **15/15**; the production dashboard build passes. Preview checks at **1440 px** and **500 px** show the panel stacked correctly, with all 12 monthly bars visible at the narrow width. `dashboard.json` keeps `risk.status = insufficient_data`, contains no synthetic marker, and `models/model.joblib` remains absent.

---

## 22. Addendum - paper evidence audit and methods drafted (P8-3, 2026-10-24)

The first paper draft covers Sections 3–4 in `reports/HIMPIL_paper_draft.md`. It is a feasibility-and-simulation draft, not a complete paper.

| Item | Content |
|---|---|
| Section 3 | Data and evidence audit: 14 sources, real coverage, completeness, incident evidence, readiness gate, and request status |
| Section 4 | Methods: real dashboard and processing, synthetic base data, event overlay, chronological models, lead-time policy, five-input demo, quarantine, ethics, and reproducibility |
| Tables 1–5 | Source inventory; coverage/completeness; incident evidence; 10-item readiness gate; data-request status |
| Real-evidence count | 15 lake stations; 150 station-years; 111 complete; 711 numeric lake values; 1 reported event; 0 verified; 0 dated water-quality rows; 0 pre-event matches |
| Readiness gate | **1 pass, 1 partial, 8 fail**; real model remains refused |
| Data requests | **9 total, 1 acknowledged, 8 planned, 0 received, 0 files**; outreach paused under D-009 |
| Synthetic boundary | Every synthetic method is labeled **SIMULATION ONLY - NOT EVIDENCE**; no synthetic number is presented as real evidence |
| Verification | Contract suite **15/15**; production dashboard build passes; no new data or model artifact was created |

The source canvas has no Part VI heading or content; the team confirmed that it is intentionally skipped, not an open question. The draft does not add formal citations yet. The next writing step is P8-4: results with exact real and synthetic numbers, real evidence first.

---

## 23. Addendum - paper results drafted (P8-4, 2026-10-24)

Section 5 (Results) and Tables 6–10 were added to `reports/HIMPIL_paper_draft.md`. The real result comes first; the synthetic results follow under separate **SIMULATION ONLY - NOT EVIDENCE** banners.

| Item | Content |
|---|---|
| Section 5.1–5.2 | Real evidence state and dashboard behavior: no real model, no real metrics, readiness **1 pass / 1 partial / 8 fail**, requests **9 / 1 / 8 / 0**, persistent **risk assessment unavailable**, no synthetic marker |
| Section 5.3 | Synthetic base dataset and event overlay: **54,795** station-days; 900 annual anchors; 20 events; 10 stress-only periods; **53,950** eligible rows |
| Section 5.4 | Full synthetic model test F1: **0.6250** at 24 hours, **0.7477** at 48 hours, **0.7973** at 72 hours; **4/4** synthetic test events detected by the 24-hour model |
| Section 5.5 | Lead-time policy: **44** raw test alerts; selected two-station/72-hour policy issues **4 episodes**, detects **4/4** events, and has **0 false episodes** |
| Section 5.6 | Five-input demo: test precision **0.4032**, recall **0.8333**, F1 **0.5435**, PR-AUC **0.6947**; **124 alerts** (50 TP, 74 FP, 10 FN); **4/4** events |
| Section 5.7 | Claims and evidence status table; no real risk score, zone map, advisory, or operational claim |
| Tables 6–10 | Synthetic design; full-model metrics; lead-time policies; five-input metrics; claims/evidence status |
| Verification | Contract suite **15/15**; production dashboard build passes; `risk.status = insufficient_data`; no synthetic marker; `models/model.joblib` remains absent |

The results do not upgrade any synthetic metric into real evidence. The full synthetic scores remain properties of the injected event process, the lead-time policy remains post hoc with four test events, and the five-input demo remains a communication aid. The next writing step is P8-5: discussion, limitations, conclusion, and verifiable references.

---

## 24. Addendum - Real-data alignment and descriptive annual trend model (P9, 2026-10-24)

The system is now aligned to the resolution of the supplied data. A real 72-hour fish-kill model remains unsupported: the water quality is annual, the weather is monthly, there are zero dated water-quality rows, zero pre-event observations, one reported event, zero verified events, and zero credible negative windows. No daily series was fabricated and no annual or monthly value was interpolated into a 72-hour label.

The real model that the data can support is a **descriptive annual trend**. It is fitted only to the nine lake stations with complete 2016-2025 dissolved-oxygen records, using station fixed effects, a common linear year term, HC3 standard errors, and a 1,000-replicate cluster bootstrap by station.

| Item | Result |
|---|---|
| Model | Station fixed-effects linear trend; descriptive only |
| Panel | **9** stations; **2016-2025**; DO n=**90** station-years; temperature n=**81** |
| Dissolved oxygen | **-0.111861 mg/L/year**; 95% CI **-0.141078 to -0.082643**; cluster bootstrap **-0.137933 to -0.087157**; R² **0.605079** |
| Water temperature | **+0.056015 °C/year**; 95% CI **-0.012883 to 0.124912**; cluster bootstrap **-0.009302 to 0.109758**; R² **0.165484**; interval includes zero |
| Fish-kill prediction | **Not supported**; the model is not a fish-kill classifier or a 72-hour model |
| Dashboard | New **What the annual data can support** panel on Water data, marked **Descriptive only**; fish-kill state remains **risk assessment unavailable** |
| Model status copy | **No fish-kill model has been trained** |
| Artifacts | `reports/tables/real_trend_model.json`, `real_trend_model_metrics.csv`, `real_trend_model_card.md`, `real_data_alignment_report.md` |
| Contract test | `test_real_trend_model_is_descriptive_not_fish_kill` |
| Verification | Suite **16/16**; `npm run build` passes; `risk.status = insufficient_data`; no synthetic marker; `models/model.joblib` absent; `data/processed/modeling_dataset.csv` header-only |

The trend is a descriptive association, not a causal finding. It does not use observation dates, does not detect the May 2019 event in annual averages, and does not control for changes in monitoring practice. It is presented separately from the fish-kill risk state and cannot produce a risk score, zone map, advisory, or warning.

Part VI of the source canvas is absent and is treated as intentionally skipped. The next writing step remains P8-5: discussion, limitations, conclusion, and verifiable references, with the negative fish-kill result central and the trend kept descriptive.

---

## 25. Addendum - Paper discussion, limitations, conclusion, and references (P8-5, 2026-10-24)

`reports/HIMPIL_paper_draft.md` now contains Sections 6 and 7 and a provisional APA 7th-edition reference list. Section 6 discusses what the study demonstrates, what the synthetic results mean and do not mean, why no real risk score is shown, implications for HIMPIL, limitations, and ethical and communication issues. Section 7 states the conclusion, next steps, and closing claim.

The 14 references are real, verified, and cited in the text: Azanza et al. (2005); Breiman (2001); Breitburg et al. (2018); Brier (1950); Cuvin-Aralar (2016); Diaz and Rosenberg (2008); Espaldon (2009); Kaufman et al. (2012); LLDA (2016-2025); PAGASA (2016-2025); Roberts et al. (2017); Saito and Rehmsmeier (2015); San Diego-McGlone et al. (2008); and University of the Philippines Diliman (2019).

The discussion preserves the evidence boundary: the fish-kill model remains untrained, the readiness gate remains at **1 pass / 1 partial / 8 fail**, the dashboard remains at **risk assessment unavailable**, the annual trend remains descriptive only, and every synthetic claim remains **SIMULATION ONLY - NOT EVIDENCE**. The abstract, introduction, related work, figures, final template, and final reference style remain for P8-6. The next writing step is P8-6: front matter, consistency review, and course-template formatting.
