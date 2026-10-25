# HIMPIL paper draft — Sections 1–7

**Working title:** Development of HIMPIL: A Feasibility and Simulation Study Toward a Machine-Learning Early-Warning System for Fish-Kill Events in Laguna de Bay

**Authors:** Jillian Rose O. Formeloza, Timothy John R. Kaharian, Irene A. Miranda

**Draft scope:** P8-3 to P8-5, with front matter drafted for P8-6 — Abstract, Sections 1–7 (introduction, related work, data and evidence audit, methods, results, discussion, limitations, and conclusion), and references.

**Status:** Working draft, 24 October 2026. Abstract, Introduction, Related Work, Discussion, Limitations, Conclusion, and a provisional APA 7th-edition reference list are drafted. Final course template, reference style, figures, and formatting are pending. Part VI is absent from the source canvas and is treated as intentionally skipped.

**Planning document:** `reports/HIMPIL_paper_revision_outline.md`

> **Evidence rule.** Sections 1–7 draw on real project evidence and documented methods only; no synthetic result is presented as real. The synthetic methods and results in Sections 4 and 5 are explicitly labeled **SIMULATION ONLY - NOT EVIDENCE**. Source identifiers such as S01 refer to the project source manifest and Table 1; formal literature citations are listed in the References section.

---

## Abstract

Fish-kill events in Laguna de Bay threaten fish-pen operators, fisherfolk, and lake-dependent communities and are associated with low dissolved oxygen and other water-quality and weather conditions. The HIMPIL concept proposes a machine-learning early-warning system, but its feasibility depends on data that are rarely assembled at the needed temporal and spatial resolution. This study audits the available evidence, defines a model-readiness gate, and builds a transparent dashboard that reports the current evidence state without issuing risk predictions. The audit covers 14 sources, 15 lake stations, and 150 station-years, of which 111 are complete across six water-quality variables. It finds one reported fish-kill event, zero independently verified events, zero dated station-monitoring water-quality rows, zero pre-event observations, no credible negative windows, and no authoritative station-to-zone crosswalk. The readiness gate remains at 1 pass, 1 partial, and 8 fail, and the dashboard reports risk assessment unavailable. A separate descriptive annual trend model on a balanced nine-station panel estimates a dissolved-oxygen change of **-0.111861 mg/L per year** (95% CI **-0.141078 to -0.082643**), but it is not a fish-kill predictor. To test the proposed pipeline without misrepresenting synthetic results as evidence, we constructed a calibrated synthetic base dataset on the real station/year frame and a separate synthetic event overlay. Chronological random-forest experiments, a post hoc lead-time policy, and a five-input presentation demo show that the workflow can be implemented and evaluated. All synthetic results are labeled simulation only and excluded from the dashboard. HIMPIL is feasible as an evidence-and-simulation system, not yet as a validated early-warning system; the next step is daily water-quality data, verified event records, negative windows, and station coordinates.

**Keywords:** Laguna de Bay; fish kill; dissolved oxygen; machine learning; early warning; data readiness; feasibility study; simulation

---

## 1. Introduction

### 1.1 Context and beneficiaries

Laguna de Bay is the largest inland lake in the Philippines and a major fishery and aquaculture resource. It supports capture fisheries, fish-pen and fish-cage operations, and the livelihoods of communities around its shoreline (Cuvin-Aralar, 2016; Espaldon, 2009). Fish-kill events in the lake can destroy a substantial share of a producer's stock within days, and they create uncertainty for fisherfolk, fish-pen operators, consumers, and local government units. The May 2019 kill in Biñan and Pila, Laguna, is one reported example: a single university news article described dead tilapia and bangus, attributed the kill to a green tide and oxygen deficiency, and reported that a during-event water sample had dissolved oxygen below the applicable standard (University of the Philippines Diliman, 2019).

The broader policy context is supplied by Sustainable Development Goal 6 (clean water and sanitation) and Goal 14 (life below water) (United Nations, 2015). HIMPIL is framed as an artificial-intelligence contribution to environmental sustainability: the original concept proposed combining water-quality and weather data in a decision-support interface, using machine learning to estimate fish-kill risk, and eventually issuing warnings, preparation advice, and SMS alerts. Those ambitions define the problem, but they are not a description of what currently exists. This paper separates the original vision from the implemented system.

The intended beneficiaries are fish-pen operators, fisherfolk, their families, and the local government units responsible for monitoring and response. No beneficiary was interviewed for this study, and no user study was conducted. The paper therefore treats the beneficiary analysis as a design rationale, not as evidence that a warning would be understood, trusted, or acted upon.

### 1.2 The HIMPIL concept

HIMPIL was conceived as an integrated early-warning and advisory system for fish kills in Laguna de Bay. The proposed inputs were dissolved oxygen, water temperature, pH, rainfall, and wind; the proposed output was a risk level with preparation advice and, eventually, an SMS alert. The concept assumed that historical water-quality and weather observations could be combined with incident records to train and validate a predictive model.

The implemented system is narrower. It contains a five-page evidence dashboard built from real annual and monthly summaries, a descriptive annual trend model on a balanced nine-station panel, a quarantined synthetic base dataset and event overlay, chronological synthetic model experiments, a post hoc lead-time policy experiment, and a five-input presentation demo. It does not contain a trained real fish-kill model, a real risk score, a zone risk map, an advisory protocol, or an SMS service. The dashboard reports **risk assessment unavailable** rather than filling that gap with an unsupported number.

### 1.3 The evidence problem

The central obstacle is not the absence of machine-learning software. It is the absence of evidence at the resolution the proposed task requires. The supplied water-quality data are annual station summaries, the weather data are monthly station summaries, and the incident record contains one reported event period. There are no dated station-monitoring water-quality rows, no pre-event observations, no credible negative windows, and no station coordinates or authoritative lake-zone crosswalk. The 2019 sample was collected during the event, not before it, and the 135 non-2019 lake station-years are not confirmed non-events.

This is a data-readiness problem of the kind that repeatedly emerges in high-stakes applied machine learning, where data work, documentation, and governance determine whether a model can be used at all (Sambasivan et al., 2021). A team can write a classifier from the current files, but it cannot defend the labels, the temporal split, or the spatial assignment. The result would be a number without a valid target. The study therefore asks what can be built responsibly with the available evidence, and what would be required to move from a feasibility study to a validated system.

### 1.4 Research questions and objectives

The study is organized around four feasibility questions:

- **RQ1:** What real data are available, and do they satisfy the requirements for supervised fish-kill risk modeling?
- **RQ2:** What evidence and readiness state can be represented transparently in a dashboard without inventing a risk score?
- **RQ3:** Can the proposed machine-learning pipeline be implemented and evaluated on a synthetic event overlay, and what does that demonstrate about feasibility rather than real predictability?
- **RQ4:** What data, validation, and governance steps are required before a real HIMPIL risk model can be validated?

The corresponding objectives are to: (1) audit the available real data and incident evidence; (2) define and apply a model-readiness gate; (3) build a dashboard that reports the evidence state honestly; (4) build and evaluate a quarantined synthetic pipeline; and (5) derive a data-collection and validation agenda.

### 1.5 Contributions

The study makes five contributions. First, it provides an evidence audit for the Laguna de Bay fish-kill use case, including source resolution, coverage, incident evidence, and data-request status. Second, it defines and applies a 10-item model-readiness gate that separates data sufficiency from software capability. Third, it implements an evidence dashboard that communicates missingness and uncertainty instead of a false risk score. Fourth, it fits a descriptive annual trend model on the balanced real panel and states its limits. Fifth, it builds a reproducible synthetic testbed and a five-input demonstration with explicit quarantine rules, so that the pipeline can be exercised without being mistaken for real evidence.

### 1.6 Scope and non-claims

This is a feasibility-and-simulation study. It is not a real early-warning system, a real fish-kill prediction model, a zone risk map, or an advisory protocol. The synthetic metrics are not estimates of Laguna de Bay predictability. The May 2019 event is a reported event, not an independently verified incident. The descriptive annual trend is an association, not a causal finding, and it is not a substitute for a 72-hour model. No fisherfolk, fish-pen operator, or local government user study was conducted, and no permission from LLDA, PAGASA, BFAR, or an LGU is assumed.

---

## 2. Related work and conceptual framework

### 2.1 Fish-kill drivers in lake and aquaculture systems

Fish kills are usually endpoints of interacting stressors rather than the result of a single variable. Low dissolved oxygen is a proximate cause because fish require oxygen for metabolism and may avoid or fail to survive hypoxic water (Kramer, 1987). Oxygen depletion can arise from eutrophication, organic loading, algal blooms, stratification, and warming, and it is a documented driver of dead zones and fish mortality in coastal and inland waters (Breitburg et al., 2018; Diaz & Rosenberg, 2008). Nutrient enrichment and algal blooms can create strong day-night oxygen swings, especially in shallow, productive systems (Smith, 2003).

In Philippine aquaculture areas, fish kills have been linked to eutrophic conditions, algal blooms, and oxygen depletion (Azanza et al., 2005; San Diego-McGlone et al., 2008). Laguna de Bay is a shallow, eutrophic tropical lake with extensive aquaculture, and its water quality and fish community are shaped by both catchment pressures and fish-pen operations (Cuvin-Aralar, 2016; Espaldon, 2009). Temperature, pH, rainfall and runoff, wind, and nutrient loading can all modify the timing and severity of a kill, which is why a single variable is an incomplete predictor.

The synthetic generator used in this study encodes low dissolved oxygen and high water temperature as the main event effects. That design choice is consistent with the literature on oxygen stress, but it does not establish that the same relationship holds in Laguna de Bay. The real data needed to estimate that relationship—dated, pre-event, station-level observations with verified events and credible negatives—are not available.

### 2.2 Machine learning for water-quality and early-warning applications

Machine learning has been applied widely to water-quality evaluation and prediction, including classification, regression, and anomaly detection (Zhu et al., 2022). The HIMPIL task is a rarer event-prediction problem: the positive class is a fish kill within a fixed horizon, the events are sparse, and the observations are temporally and spatially dependent. These features change the evaluation strategy. A random forest is a reasonable tabular baseline because it can capture nonlinear interactions without a strong parametric form (Breiman, 2001), but it cannot compensate for missing labels or a leaking split.

When events are rare, overall accuracy is misleading because a model that never predicts a positive can score well. Precision-recall analysis and the precision-recall AUC are more informative than ROC analysis in this setting (Saito & Rehmsmeier, 2015). Probability calibration and the Brier score matter when the output is a risk level rather than a hard class (Brier, 1950). Temporal validation is also essential: random cross-validation can mix future and past observations and inflate apparent performance (Roberts et al., 2017). Leakage can enter through repeated events, post-event measurements, or features that would not be available at prediction time (Kaufman et al., 2012).

For a warning system, event-level detection and lead time are at least as important as row-level precision and recall. A model that detects every event but raises many false alerts imposes a different burden from one that misses events but rarely alarms. The synthetic experiments in this study therefore report both row-level metrics and event-level detection, and the lead-time policy experiment treats repeated station-day alerts as episodes rather than independent successes. These methods are implemented only in the synthetic testbed; no real fish-kill model was trained.

### 2.3 Data readiness and feasibility assessment

Applied machine-learning feasibility depends on label quality, temporal resolution, spatial joins, negative windows, documentation, and governance, not only on model choice. Data cascades—compounding data problems that surface late in a project—are a recognized failure mode in high-stakes AI (Sambasivan et al., 2021). In environmental settings, the problem is compounded by inconsistent monitoring schedules, changing laboratory methods, missing coordinates, and incident records that were not designed for prediction.

A readiness gate is a useful contribution when a model cannot yet be trained. It makes the gap explicit, separates data sufficiency from software capability, and gives a concrete target for future collection. It also prevents a common substitution: reporting a synthetic or proxy result as if it answered the real question. This study treats the gate as a result, not as a preliminary formality. The distinction between "no model" and "no data" is central: the project has a working pipeline, but it does not have the evidence the pipeline needs.

### 2.4 Warning communication and uncertainty

A warning system is a social intervention as well as a technical one. Risk communication research shows that information is interpreted through prior beliefs, trust, and social processes, and that false precision can amplify concern or erode credibility (Fischhoff, 1995; Kasperson et al., 1988). An interface that displays a probability or a colored risk level implies a calibration and an operational protocol that may not exist. In a data-poor setting, the honest state may be **risk assessment unavailable**, not a low or moderate risk label.

The difference between a simulation demo and an operational advisory is therefore not cosmetic. A demo can use fictional inputs and illustrative bands; an advisory must specify who issues it, for which place and time, with what uncertainty, and with what action the recipient can take. No such protocol was developed or evaluated here. User-centered warning design, trust, access, and the costs of false alarms remain future work.

### 2.5 Gap addressed by this study

The local HIMPIL context lacks a curated, dated event and monitoring dataset of the kind assumed by most applied prediction studies. The contribution of this paper is not a new algorithm. It is an evidence-first feasibility assessment: an audit of what exists, a gate that states what is missing, a dashboard that reports the current state, a descriptive trend that is defensible at the available resolution, and a quarantined synthetic testbed that tests the pipeline under explicit assumptions. That combination is useful precisely because it refuses to convert a plausible mechanism into an unsupported prediction.

---

## 3. Data and evidence audit

### 3.1 Sources inspected

The audit covers 14 sources, S01–S14. Eight are environmental workbooks: six annual water-quality tables from the Laguna Lake Development Authority (LLDA, 2016–2025) and two monthly weather tables from the Philippine Atmospheric, Geophysical and Astronomical Services Administration (PAGASA, 2016–2025). The remaining six are reports, proposals, a research-topic form, a static user-interface archive, and one news report of a fish kill. The sources are not interchangeable. A source was accepted for a use only when its resolution, geographic key, and reporting period matched that use. Table 1 summarizes the inventory.

**Table 1. Sources inspected, resolution, and valid use.**

| ID | Source and type | Resolution | Geographic key | Period | Valid use in this study |
|---|---|---|---|---|---|
| S01 | PAGASA rainfall workbook | Monthly station total | PAGASA station name | 2016–2025; 2025 partial | Descriptive weather context; Tanay lake-area panel |
| S02 | LLDA nitrate workbook | Annual station summary | Lake station or tributary | 2016–2025 | Descriptive water-quality context |
| S03 | LLDA phosphate workbook | Annual station summary | Lake station or tributary | 2016–2025 | Descriptive water-quality context |
| S04 | LLDA BOD workbook | Annual station summary | Lake station or tributary | 2016–2025 | Descriptive water-quality context |
| S05 | LLDA pH workbook | Annual station summary | Lake station or tributary | 2016–2025 | Descriptive water-quality context |
| S06 | LLDA water-temperature workbook | Annual station summary | Lake station or tributary | 2016–2025 | Descriptive water-quality context |
| S07 | LLDA dissolved-oxygen workbook | Annual station summary | Lake station or tributary | 2016–2025 | Descriptive water-quality context |
| S08 | PAGASA wind workbook | Monthly station value | PAGASA station name | 2016–2025; 2025 partial | Descriptive weather context |
| S09 | AWQR 2009–2012 report | Annual report and tables | Station | 2009–2012 | Background only; outside the 2016–2025 analysis window |
| S10 | Sustainability review | Narrative and aggregate table | Lake | Events 1972–2023 | Background only; no usable individual Laguna de Bay event |
| S11 | HIMPIL proposal | Narrative | Not applicable | Undated | Context only; contains no observations |
| S12 | Research-topic discovery form | Narrative and planning tables | Not applicable | AY 2026–2027 | Context only; contains no observations |
| S13 | HIMPIL user-interface archive | Static prototype | Not applicable | Not stated | Not used as evidence |
| S14 | UPD 2019 fish-kill article | Event report and one during-event sample | Municipality | May 2019 | Event audit and during-event context only |

The six LLDA workbooks contain 59 station labels: 15 lake stations and 44 tributary stations. The lake-station analysis and dashboard use the 15 lake stations. The tributary series are processed and retained in the working data—440 station-years and 1,948 numeric values—but they are outside the lake-station analysis in this paper. This distinction matters because a tributary measurement is not a lake measurement and cannot be assigned to a lake zone without a documented crosswalk.

The two PAGASA workbooks are national station networks, not lake measurements. S01 and S08 provide monthly station summaries for 2016–2025, with 2025 incomplete and still undergoing verification. No supplied source provides daily water-quality observations.

### 3.2 Coverage and completeness

The real lake-water-quality baseline is 15 stations observed over 10 years, or 150 station-years. Of these, 111 station-years are complete across all six water-quality variables. The lake subset contains 711 numeric annual values. Missing cells remain missing; they are not converted to zero and are not imputed in the dashboard.

**Table 2. Real-data coverage and completeness.**

| Measure | Value | Note |
|---|---:|---|
| Sources inspected | 14 | S01–S14 |
| Lake stations | 15 | Station labels from the LLDA workbooks |
| Lake station-years | 150 | 15 stations × 10 years, 2016–2025 |
| Complete across six water-quality variables | 111 | 39 station-years have at least one missing variable |
| Numeric lake water-quality values | 711 | Missing values remain blank |
| Lake stations with a zone label in the station name | 5 of 15 | No coordinates are supplied |
| Tributary stations processed but outside the lake analysis | 44 | 440 station-years; 1,948 numeric values |
| Rainfall numeric station-months | 6,282 | 6,282 of 7,008 station-months; 57–61 stations per year; 2025 partial |
| Wind numeric station-months | 6,288 | 6,288 of 7,260 station-months; 58–64 stations per year; 2024 is the latest complete network year |
| Latest complete rainfall network year | 2024 | 54 stations with 12 numeric months |
| Latest complete wind network year | 2024 | 53 stations with 12 numeric months |
| Reported event periods | 1 | May 2019 |
| Independently verified events | 0 | No second source or formal investigation report |
| Dated station-monitoring water-quality rows | 0 | LLDA workbooks are annual summaries |
| Pre-event predictive matches | 0 | The 2019 sample was collected during the event |

The monthly weather record cannot be treated as daily data. In 2025, most stations have January–June values only, while some have twelve months; the source states that remaining synoptic data are still undergoing verification. The dashboard therefore excludes 2025 from annual totals and reports it as provisional.

The rainfall workbook also supports one descriptive lake-area view (PAGASA, 2016–2025). Tanay, Rizal is the only station in the supplied PAGASA list that is clearly in the Laguna de Bay watershed. Complete-year Tanay totals range from 2,452.3 mm to 3,508.5 mm over 2016–2024, with 3,508.5 mm in 2024. The 2025 record covers January–June only and totals 680.01 mm; it is never treated as an annual total. The monthly climatology, based on nine complete years, ranges from a mean of 18.7 mm in March to 489.3 mm in July. These values describe one regional station; they are not a lake measurement, and no station coordinates or lake-zone link are supplied.

### 3.3 Incident evidence

One event report was accepted after the source audit: HIMPIL-FK-2019-001, a fish kill reported in Biñan and Pila, Laguna, in May 2019 (University of the Philippines Diliman, 2019). The report gives exact start dates for the two municipalities—4 May 2019 for Biñan and 12 May 2019 for Pila—but the end date is only described as “until the end of May.” The report is a single university news article with an LLDA interview and a water-quality table. It is not a formal LLDA investigation report and is not independently corroborated in the supplied files.

**Table 3. Incident evidence audit.**

| Evidence item | Value | Interpretation |
|---|---:|---|
| Accepted event reports | 1 | UPD article, S14 |
| Unique event periods | 1 | May 2019 |
| Municipalities represented | 2 | Biñan and Pila, Laguna |
| Exact start dates | 2 | 4 May 2019 (Biñan); 12 May 2019 (Pila) |
| Exact end date | 0 | “Until the end of May”; approximate boundary only |
| Independently verified events | 0 | No second source or formal investigation report |
| Official investigation reports | 0 | None supplied |
| Dated station-monitoring water-quality rows | 0 | LLDA workbooks are annual summaries |
| During-event context measurements | 4 | One sample date: 29 May 2019 |
| Pre-event observations | 0 | The 29 May sample was collected during the event |
| Usable 24-hour positive labels | 0 | No dated pre-event series |
| Usable 24-hour negative labels | 0 | No credible non-event windows |
| Non-2019 lake station-years | 135 | Not confirmed non-events |

The 29 May 2019 sample reports dissolved oxygen at 4.7 mg/L, ammonia at 0.16 mg/L, nitrate at 0.4 mg/L, and phosphate at 1.00 mg/L. These are during-event context measurements. They cannot be used as pre-event predictors, and they cannot establish a 24-, 48-, or 72-hour lead time. The report provides no coordinates or lake-zone designation.

The remaining 135 annual lake station-years outside 2019 cannot be treated as negative labels. The supplied files contain no incident-reporting log that would establish the absence of a fish kill. Absence of a published report is not evidence of absence. Consequently, the single event cannot be expanded into a training set by repeating its dates, municipalities, or weekly windows; doing so would create leakage and false precision.

### 3.4 Model-readiness gate

The study applies a 10-item readiness gate before any real supervised model is trained. The gate separates data sufficiency from software capability. Each item has a status, the evidence used, and the consequence of failure. The current result is **1 pass, 1 partial, and 8 fail**.

**Table 4. Real-data model-readiness gate.**

| Check | Requirement | Status | Evidence | Consequence |
|---|---|---|---|---|
| L1 | At least two independent documented event periods for a chronological split | Fail | 1 event period; 1 accepted report; event year 2019 | Events cannot be placed in both training and test periods |
| L2 | Independently corroborated event records | Partial | One institutional news report; no second source or formal incident report | Event is plausible but not independently verified |
| L3 | Exact event start date for a 24-hour window | Pass | Biñan start 2019-05-04; Pila start 2019-05-12; end only approximate | A start-day window is possible, but only for one event |
| L4 | Dated water-quality observations at daily or sub-daily resolution | Fail | 0 rows have a full observation timestamp; 2,659 numeric annual station-year-variable values exist across all stations | No pre-event water-quality feature vector can be constructed |
| L5 | A pre-event environmental match at a known lead time | Fail | 0 usable pre-event matches; the article sample is during-event | No observation is known to have been available before the event |
| L6 | Documented station coordinates and lake-zone mapping | Fail | 0 coordinates; 5 of 15 lake stations have a zone label in the name | Events cannot be assigned to a station or zone defensibly |
| L7 | Credible non-event windows with documented incident reporting | Fail | 135 annual station-years fall outside 2019; no incident-reporting log | Absence of a published report cannot be treated as a negative label |
| L8 | Enough events for class-imbalance-aware evaluation | Fail | 1 event period; no 24-hour negatives; class balance cannot be estimated | Precision, recall, and F1 would be undefined or meaningless |
| L9 | A 24-hour prediction horizon supported by sampling frequency | Fail | Water quality is annual; weather is monthly | The proposed 24-hour target is not supported |
| L10 | Sufficient independent observations for chronological validation and a held-out period | Fail | One event period, one location pair, one event year | No honest train/validation/test evaluation is possible |

L3 passes only because a start date exists for one event. That single pass does not rescue the other requirements. The gate blocks real supervised training, real performance metrics, a real risk score, a zone risk map, and any advisory. The dashboard must therefore remain in the **risk assessment unavailable** state.

### 3.5 Data-request status

Nine data requests were prepared. `LLDA-INC-01` (LLDA incident records) is acknowledged. The other eight remain planned: daily water quality, station metadata, aggregation rules, reporting completeness, lake zones, PAGASA daily weather, BFAR incident records, and Biñan/Pila LGU records. No files or permissions have been received. Outreach is paused under decision D-009, so the requests are not described as actively pending.

**Table 5. Data-request status.**

| Status | Count | Note |
|---|---:|---|
| Total requests prepared | 9 | Field-level request package |
| Acknowledged | 1 | `LLDA-INC-01` |
| Planned | 8 | Remain planned; outreach paused |
| Received | 0 | No files received |
| Files inspected | 0 | No new source files |
| Permissions granted | 0 | No permission is assumed |
| Outreach status | Paused | D-009, 23 October 2026 |

### 3.6 Implication

The real evidence does not support a supervised fish-kill model. The binding constraint is not the availability of machine-learning software; it is the absence of dated water-quality observations, verified events, credible negative windows, station coordinates, and an authoritative zone crosswalk. A model trained on the current data would produce numbers without a defensible target. Temporal leakage and repeated-event leakage are well-documented failure modes in applied machine learning (Kaufman et al., 2012; Roberts et al., 2017).

The evidence audit therefore establishes two separate tracks for the rest of the paper. The first is the real-data dashboard, which reports what is known and explicitly withholds a risk assessment. The second is a quarantined synthetic testbed, which tests whether the proposed pipeline can be implemented under explicit assumptions. The synthetic track is not a substitute for the missing evidence and does not change the gate verdict.

---

## 4. Methods

### 4.1 Study design

The study uses a feasibility-and-simulation design with four parts:

1. an evidence audit of the supplied sources;
2. a real-data dashboard and a model-readiness gate;
3. a quarantined synthetic base dataset and event overlay;
4. chronological model experiments and a presentation-only demonstration.

The design is sequential. The evidence audit defines what can be claimed. The readiness gate converts that audit into a training decision for the fish-kill target. The dashboard reports the resulting evidence state. The descriptive annual trend model is fitted separately, outside the fish-kill gate. The synthetic testbed is built only after the real fish-kill model is refused, and it never feeds back into the real dashboard.

> **Figure 1 (to be produced).** Study design. The flow moves from the 14-source evidence audit to the readiness gate, then to the real-data dashboard and, separately, to the synthetic base dataset, event overlay, chronological models, and presentation demo. The synthetic branch is enclosed by a visible **SIMULATION ONLY - NOT EVIDENCE** boundary.

### 4.2 Evidence dashboard

The dashboard is a five-page reporting instrument: Overview, Water data, Fish-kill evidence, Model status, and Sources. It is built from a static real-data bundle, `dashboard/src/data/dashboard.json`, generated by `python/build_dashboard_data.py`. The bundle contains coverage, completeness, readiness, event, source, and data-request counts. It contains no synthetic data, no synthetic metric, no risk score, no zone risk map, and no advisory.

The persistent interface state is **risk assessment unavailable**. The dashboard also displays the exact phrase **No risk prediction** and exposes the evidence boundary. The model-status page reports the refused training and evaluation guards rather than a fitted model. The Water data page contains the six annual water-quality measures, the station table, the network rainfall and wind cards, and the separate Tanay rainfall panel. The Tanay panel is descriptive context; it does not feed a prediction.

The dashboard is intentionally a reporting instrument, not a prediction interface. It reports annual and monthly summaries at the resolution supplied by the sources. It does not resample monthly weather to daily values or convert annual water-quality summaries into event observations.

### 4.3 Real-data processing

The real-data path begins with `python/clean_data.py`, which reads the supplied workbooks and writes documented CSV outputs to `data/processed/`. The outputs include annual water-quality long and wide tables, monthly rainfall and wind tables, a combined monthly weather table, a station registry, and coverage summaries. Units, source identifiers, quality flags, and the 2025 provisional flag are retained. Missing values are preserved as blanks.

The dashboard build reads only the processed CSV outputs; it does not reach into the original workbooks. `python/build_dashboard_data.py` computes the real counts, annual water-quality trends, network weather summaries, and the Tanay rainfall panel. The real modelling dataset, `data/processed/modeling_dataset.csv`, remains header-only because the label-generation step is blocked by the readiness gate.

One real statistical model is fitted separately from the fish-kill gate. `python/train_real_trend.py` estimates a station fixed-effects linear trend on the nine lake stations with complete 2016-2025 dissolved-oxygen records. The model uses a common linear year term, station intercepts, HC3 standard errors, and a 1,000-replicate cluster bootstrap by station. It estimates annual change in mean dissolved oxygen (n = 90 station-years) and water temperature (n = 81 station-years). It is a descriptive annual trend model, not a fish-kill classifier, not a 24/48/72-hour model, and not a basis for a risk score. Its estimates and prohibited uses are recorded in `reports/tables/real_trend_model_card.md`.

This separation is deliberate. It prevents a later dashboard change from silently altering the source data and prevents a synthetic artifact from entering the real-data path.

### 4.4 Synthetic base dataset

> **SIMULATION ONLY - NOT EVIDENCE**

A separate synthetic base dataset was built to test the software pipeline on the real station/year frame without pretending that synthetic values are observations. It uses the 15 real lake-station labels, a daily calendar from 1 January 2016 to 31 December 2025, six water-quality variables, and three synthetic weather zones. It contains 54,795 daily station-days, 10,959 weather rows, and 900 annual station-year-variable anchors.

The annual anchors include 711 real numeric values, 189 synthetically imputed values, and 90 values for 2025 whose completeness is not documented. The daily series are calibrated to the annual anchors. The mean absolute annual-mean error is 0.000047 and the maximum absolute error is 0.000464; exact equality is not guaranteed because values are clipped to plausible bounds and rounded.

The synthetic base dataset contains no fish-kill labels, no event dates, no station coordinates, and no tributary stations. Every row carries the data origin `synthetic_base_v1`. The dataset is environmental only and is not connected to the evidence dashboard.

### 4.5 Synthetic event overlay

> **SIMULATION ONLY - NOT EVIDENCE**

The event overlay adds 20 synthetic event periods and 10 high-stress no-event periods to a copy of the synthetic base panel. The base dataset itself is left unchanged. The event effect is a four-day pre-event ramp, a three-day event, and a five-day recovery. Affected stations receive lower dissolved oxygen, higher water temperature, higher nutrients, higher BOD, and slightly lower pH. The overlay contains 53,950 model-eligible rows after event and recovery windows are excluded from fitting and evaluation.

The overlay does not use the May 2019 event date or any real incident date. Every row carries the data origin `synthetic_base_v1_event_overlay`. The synthetic events are a controlled test of the pipeline, not a reconstruction of historical fish kills.

### 4.6 Chronological models

> **SIMULATION ONLY - NOT EVIDENCE**

The synthetic models use 24-, 48-, and 72-hour event labels. The split is chronological: training data are before 1 January 2023, validation data are the 2023 calendar year, and test data are 2024–2025, so that later observations are never used to predict earlier ones (Roberts et al., 2017). The model-eligible partition sizes are 37,750 training rows, 5,395 validation rows, and 10,805 test rows. The target is the start of a synthetic event within the stated horizon at the same station.

The comparison includes a majority-class baseline, logistic regression, and a random forest (Breiman, 2001). Features are backward-looking: current conditions, lags, rolling means, and rolling rainfall, wind, and nutrient summaries. No future values are used. The evaluation reports precision, recall, F1, precision-recall AUC, ROC-AUC, Brier score, confusion counts, and event-level detection. Precision-recall AUC is emphasized because the positive class is rare, and the Brier score is reported because threshold-free probability error matters for a warning system (Brier, 1950; Saito & Rehmsmeier, 2015). Event-level detection is reported separately because row-level counts can hide whether a whole event was missed.

The test partition contains four synthetic event periods and the validation partition contains two. These counts are too small for a defensible real-world evaluation. The results therefore describe the behavior of the synthetic pipeline, not the predictability of Laguna de Bay fish kills.

### 4.7 Lead-time policy experiment

> **SIMULATION ONLY - NOT EVIDENCE**

A post hoc experiment examines whether the saved 24-hour synthetic model can support an earlier warning. The raw test alerts are classified as target-day, early pre-event, or stress-only. Four confirmation and cooldown policies are compared: one station with a 72-hour cooldown; two stations with no cooldown; two stations with a 72-hour cooldown; and three stations with a 72-hour cooldown. An issued episode requires the stated number of distinct stations to alert on the same date, subject to the cooldown.

The illustrative policy uses two stations and a 72-hour cooldown. This policy was selected after inspecting the test error profile, so it is optimistic by construction. The experiment is a decision-layer analysis on an existing model, not a newly trained 72-hour objective, and it is not a validated warning rule.

### 4.8 Five-input presentation model

> **SIMULATION ONLY - NOT EVIDENCE**

A separate presentation model uses the five fields from the team’s illustrative input table: dissolved oxygen, water temperature, pH, rainfall, and wind speed. It is trained on the synthetic 72-hour event label with a random forest of 300 trees, `min_samples_leaf=5`, a balanced subsample, and the same chronological split and seed as the synthetic base model. The model outputs a simulated 72-hour event probability and maps it to illustrative Low, Medium, and High communication bands: Low below 0.25, Medium from 0.25 to below 0.50, and High at or above 0.50.

The bands are communication labels, not validated thresholds. The five-input model is deliberately simpler than the full synthetic model because it omits lags, rolling dissolved-oxygen features, and much of the weather context. The example input rows used in the presentation are fictional values from the team’s slide; they are not measurements. A local browser application at `sandbox/presentation_app/app.py` exposes the same saved model for demonstration and writes no data.

### 4.9 Evaluation and quarantine

The real and synthetic tracks are separated by contract tests in `tests/test_pipeline.py`. The suite verifies that synthetic data are absent from `data/processed/`, that no synthetic model exists at `models/model.joblib`, that `dashboard/src/data/dashboard.json` contains no synthetic marker, that the real trend model is descriptive only, and that the synthetic artifacts remain labeled. The suite reports **16/16** passing tests, and the production dashboard build passes.

Every synthetic report and model card carries the warning **SIMULATION ONLY - NOT EVIDENCE**. Synthetic data rows carry the `data_origin` marker, and every synthetic artifact stays outside the real dashboard path. The quarantine is part of the method, not an afterthought: it prevents a synthetic result from being read as a real observation, a real performance estimate, or a real risk level.

### 4.10 Ethics and governance

The study did not issue a real advisory, operate an SMS service, or collect user data. No fisherfolk, fish-pen operator, or LGU user study was conducted, so the paper cannot claim that warnings are understandable or actionable. Data access is paused under D-009, and no permission from LLDA, PAGASA, BFAR, or an LGU is assumed. The 2019 report is described as a reported event, not an independently verified incident. Synthetic example rows are fictional and are labeled as such.

### 4.11 Reproducibility and code availability

The main real-data entry points are `python/clean_data.py` and `python/build_dashboard_data.py`. The synthetic pipeline is implemented in `sandbox/synthetic/build_base_dataset.py`, `sandbox/synthetic/train_base_model.py`, `sandbox/synthetic/lead_time_policy.py`, and `sandbox/synthetic/train_presentation_model.py`. The local presentation app is `sandbox/presentation_app/app.py`. The contract suite is `tests/test_pipeline.py`.

The commands and artifact paths are documented in `README.md`. The real and synthetic paths are deliberately separate, so reproducing the synthetic results cannot alter the evidence dashboard or the model-readiness verdict.

---

## 5. Results

### 5.1 Real evidence state

The real-data result is negative and unambiguous: the supplied evidence does not support a supervised fish-kill model. The audit identified 14 sources, 15 lake stations, 150 lake station-years, and 111 station-years complete across all six water-quality variables. The lake subset contains 711 numeric annual values. Only five of the 15 stations carry a lake-zone label in the station name, and no station coordinates are supplied.

The incident audit found one reported event period, zero independently verified events, zero dated station-monitoring water-quality rows, zero pre-event observations, and zero usable 24-hour positive or negative labels. The reported May 2019 event remains a single university news report with an LLDA interview; its 29 May 2019 sample was collected during the event, not before it. The 135 station-years outside 2019 are not confirmed non-events.

The readiness gate therefore remains at **1 pass, 1 partial, and 8 fail** (Table 4). The data-request status remains **9 prepared, 1 acknowledged, 8 planned, 0 received, and 0 files** (Table 5). No real fish-kill classifier was trained, no real fish-kill prediction was generated, and no real fish-kill precision, recall, F1, PR-AUC, calibration, or risk score exists. This is not a missing result; it is the result of the evidence audit. A separate descriptive annual trend model is reported in Section 5.3; it does not change the fish-kill verdict.

The 2019 event cannot be converted into a test case by repeating its dates or municipality labels. Doing so would place the same event in training and evaluation, create leakage, and give a false impression of validation. The defensible real-data claims are descriptive: the dashboard can report what the supplied annual and monthly summaries contain, the trend model can summarize long-term change on a balanced panel, and both can report what the data cannot support.

### 5.2 Dashboard behavior

The production dashboard renders all five pages—Overview, Water data, Fish-kill evidence, Model status, and Sources—and keeps the persistent state **Risk assessment unavailable**. The Overview shows **No risk prediction**, the readiness meter (**1 pass, 1 partial, 8 fail**), the request counts (**9 / 1 / 8 / 0**), and **The evidence boundary**. The Water data page keeps the national rainfall and wind network cards separate from the Tanay, Rizal lake-area card.

The Tanay card renders complete-year totals for 2016–2024 and a separate January–June 2025 partial total. The partial total is never displayed or described as an annual total. The annual water-quality views preserve missing cells as blanks; they do not impute values or convert missingness to zero. These are descriptive reporting results, not model outputs.

The production bundle contains no risk score, zone risk map, advisory, SMS function, or synthetic marker. `dashboard.json` retains `risk.status = insufficient_data`. The production build passes, the five-page navigation renders, and the contract suite reports **16/16** passing tests. The dashboard therefore succeeds at its limited purpose: it makes the evidence state and the missing evidence visible rather than hiding them behind a prediction.

### 5.3 Real descriptive annual trend model

The only real model supported by the supplied data is a descriptive annual trend estimate on the balanced nine-station panel. For dissolved oxygen, the fitted slope is **-0.111861 mg/L per year** (95% CI **-0.141078 to -0.082643**; cluster bootstrap 95% interval **-0.137933 to -0.087157**) across **90 station-years**, with an R² of **0.605079**. For water temperature, the slope is **+0.056015 °C per year** (95% CI **-0.012883 to 0.124912**; cluster bootstrap **-0.009302 to 0.109758**) across **81 station-years**, with an R² of **0.165484**. The dissolved-oxygen interval excludes zero under both standard-error and station-cluster resampling; the temperature interval includes zero, so no clear temperature trend is established.

These estimates describe within-station change in annual station summaries. They do not use observation dates, do not identify a cause, and do not detect the May 2019 event, whose signal is not visible in annual averages. The panel is small, the stations are not a probability sample, and the analysis does not control for changes in monitoring practice. The model is therefore reported as **descriptive only**. It is not a fish-kill classifier, not a 72-hour model, and not a source for a risk score, zone map, or advisory. Its model card records these prohibited uses in `reports/tables/real_trend_model_card.md`.

The dashboard presents the estimate in a separate **What the annual data can support** panel on the Water data page. The panel is marked **Descriptive only**, reports the confidence intervals and the nine-station panel, and states that the 72-hour fish-kill target remains unavailable. The persistent fish-kill state remains **risk assessment unavailable**.

### 5.4 Synthetic base dataset and event overlay

> **SIMULATION ONLY - NOT EVIDENCE**
>
> The results in Sections 5.4–5.7 describe a synthetic event process injected into a synthetic base dataset. They are not estimates of Laguna de Bay fish-kill predictability, not real model performance, and not a real risk assessment.

The synthetic base dataset contains 54,795 station-days for the 15 real lake-station labels over 2016–2025, six water-quality variables, three synthetic weather zones, and 10,959 weather rows. Its 900 annual station-year-variable anchors comprise 711 real numeric values, 189 synthetically imputed values, and 90 values for 2025 whose completeness is not documented. The daily series are calibrated to the annual anchors, with a mean absolute annual-mean error of **0.000047** and a maximum absolute error of **0.000464**.

The event overlay contributes 20 synthetic event periods and 10 high-stress no-event periods. After event and five-day recovery windows are excluded from fitting and evaluation, 53,950 rows remain eligible. The eligible panel contains 100 positive 24-hour labels, 200 positive 48-hour labels, and 300 positive 72-hour labels, split chronologically into 37,750 training rows, 5,395 validation rows, and 10,805 test rows. Table 6 summarizes the design.

**Table 6. Synthetic base dataset and event-overlay design. SIMULATION ONLY - NOT EVIDENCE.**

| Item | Value | Note |
|---|---:|---|
| Synthetic calendar | 2016-01-01 to 2025-12-31 | Daily |
| Lake stations | 15 | Real station labels; synthetic values |
| Water-quality variables | 6 | DO, temperature, pH, nitrate, phosphate, BOD |
| Synthetic weather zones | 3 | Generated, not mapped to lake zones |
| Station-days | 54,795 | Daily water-quality panel |
| Weather rows | 10,959 | Synthetic daily weather |
| Annual anchors | 900 | 711 real; 189 imputed; 90 for 2025 |
| Calibration error | 0.000047 mean; 0.000464 max | Absolute annual-mean error |
| Synthetic event periods | 20 | Generated dates |
| Stress-only periods | 10 | No event |
| Model-eligible rows | 53,950 | Event and recovery rows excluded |
| Train / validation / test rows | 37,750 / 5,395 / 10,805 | Chronological split |
| Positive labels, 24 / 48 / 72 hours | 100 / 200 / 300 | Eligible panel |

The synthetic design is an implementation test, not an estimate of event frequency or ecological realism. The 20 events were generated to create a learnable process, and the event effect was injected into the same variables used as features. A high score therefore demonstrates that the pipeline can recover the injected process; it does not demonstrate that the process resembles Laguna de Bay.

### 5.5 Full synthetic base model

> **SIMULATION ONLY - NOT EVIDENCE**

The full synthetic model was evaluated on the 2024–2025 test partition with a fixed 0.5 threshold. Table 7 reports the random forest at the three horizons. At 24 hours, the model achieved precision **0.4545**, recall **1.0000**, F1 **0.6250**, PR-AUC **0.5678**, ROC-AUC **0.9991**, and Brier **0.0020**, with 20 true positives, 24 false positives, no false negatives, and 10,761 true negatives. At 48 hours, it achieved precision **0.5970**, recall **1.0000**, F1 **0.7477**, PR-AUC **0.9572**, ROC-AUC **0.9998**, and Brier **0.0021**, with 40 true positives, 27 false positives, no false negatives, and 10,738 true negatives. At 72 hours, it achieved precision **0.6705**, recall **0.9833**, F1 **0.7973**, PR-AUC **0.9471**, ROC-AUC **0.9995**, and Brier **0.0026**, with 59 true positives, 29 false positives, one false negative, and 10,716 true negatives. The 24-hour event-level audit detected **4/4** synthetic test events.

**Table 7. Full synthetic base model, test partition, random forest. SIMULATION ONLY - NOT EVIDENCE.**

| Horizon (h) | Precision | Recall | F1 | PR-AUC | ROC-AUC | Brier | TP | FP | FN | TN |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 24 | 0.4545 | 1.0000 | 0.6250 | 0.5678 | 0.9991 | 0.0020 | 20 | 24 | 0 | 10,761 |
| 48 | 0.5970 | 1.0000 | 0.7477 | 0.9572 | 0.9998 | 0.0021 | 40 | 27 | 0 | 10,738 |
| 72 | 0.6705 | 0.9833 | 0.7973 | 0.9471 | 0.9995 | 0.0026 | 59 | 29 | 1 | 10,716 |

The 24-hour result needs a qualification that the headline F1 obscures. Of the 24 false positives, 23 are pre-event rows two to three days before a synthetic event and one is the stress-only alert; none are baseline rows. Under a strict 24-hour label they are errors; under a 72-hour warning objective the early rows are signals. This label-timing effect explains why the 24-hour PR-AUC (0.568) is lower than the 48-hour (0.957) and 72-hour (0.947) values, and why a 24-hour F1 should not be presented as the quality of a 72-hour warning.

The 24-hour logistic regression comparator had precision **0.5128**, recall **1.0000**, F1 **0.6780**, PR-AUC **0.9228**, and Brier **0.0016**, while the majority-class baseline had F1 **0.0000** because it never predicts a positive. The random forest’s lower 24-hour F1 is consistent with its larger early-alert tail; it is not evidence that the random forest is generally worse. The 48- and 72-hour comparisons are reported for the random forest; the saved 24-hour model is the one reused in the lead-time experiment, while the five-input presentation model is trained separately on the 72-hour label.

The validation split shows the same direction: random-forest F1 was **0.8333** at 24 hours, **0.8889** at 48 hours, and **0.9063** at 72 hours. The validation partition contains only two synthetic events, so these values do not provide independent confirmation. All of these metrics are properties of the injected synthetic process. They are not estimates of real fish-kill predictability, and they cannot be transferred to Laguna de Bay.

### 5.6 Lead-time policy results

> **SIMULATION ONLY - NOT EVIDENCE**

The saved 24-hour model produced 44 raw alert rows in the synthetic test period: 20 within the 24-hour target, 23 early pre-event rows two to three days before an event, and one stress-only row. There were no baseline alerts. The 23 early rows are the reason a strict 24-hour label and a 72-hour warning objective disagree.

Table 8 compares the four confirmation and cooldown policies. The two-station, 72-hour cooldown policy issued **4 episodes**, detected **4/4** synthetic test events, and produced **0 false episodes**. The first episode arrived a median of **3.0 days** before the synthetic event, with a range of 2–3 days. On validation, the same policy issued **2 episodes**, detected **2/2** events, and produced **0 false episodes**, with a median lead of **1.5 days** and a range of 1–2 days.

**Table 8. Synthetic lead-time policy results. SIMULATION ONLY - NOT EVIDENCE.**

| Split | Policy | Episodes | Events detected | False episodes | Median lead (days) | Raw alerts |
|---|---|---:|---:|---:|---:|---:|
| Validation | 1 station, 72h cooldown | 2 | 2/2 | 0 | 2.0 | 14 |
| Validation | 2 stations, no cooldown | 3 | 2/2 | 0 | 1.5 | 14 |
| Validation | 2 stations, 72h cooldown | 2 | 2/2 | 0 | 1.5 | 14 |
| Validation | 3 stations, 72h cooldown | 2 | 2/2 | 0 | 1.5 | 14 |
| Test | 1 station, 72h cooldown | 5 | 4/4 | 1 | 3.0 | 44 |
| Test | 2 stations, no cooldown | 11 | 4/4 | 0 | 3.0 | 44 |
| Test | 2 stations, 72h cooldown | 4 | 4/4 | 0 | 3.0 | 44 |
| Test | 3 stations, 72h cooldown | 4 | 4/4 | 0 | 2.0 | 44 |

The one-station policy detects all four test events but issues five episodes and one false episode, the stress-only period. The three-station policy also detects all four events with no false episodes, but its median lead falls to 2.0 days. Removing the cooldown does not improve event detection and increases test episodes from 4 to 11; the cooldown reduces repeated alerts, not the underlying station-day alert burden.

The selected two-station, 72-hour policy is the most balanced result in this small sample, but it was selected after inspecting the test error profile. It is a post hoc policy, not a pre-registered rule, and validation is not an independent confirmation. The test set contains only four synthetic events, and no confidence interval, significance test, or operational cost analysis was performed. The result supports a design lesson—match the label horizon to the intended warning lead time—not an operational warning claim.

### 5.7 Five-input presentation model results

> **SIMULATION ONLY - NOT EVIDENCE**

The five-input presentation model uses dissolved oxygen, water temperature, pH, rainfall, and wind speed to predict the synthetic 72-hour event label. On the test partition it achieved precision **0.4032**, recall **0.8333**, F1 **0.5435**, PR-AUC **0.6947**, and Brier **0.006542**. It issued 124 alerts: 50 true positives, 74 false positives, and 10 missed positive rows, and it detected **4/4** synthetic test events. On validation it achieved precision **0.8571**, recall **0.6000**, F1 **0.7059**, PR-AUC **0.7451**, and Brier **0.002491**, with 21 alerts (18 true positives, 3 false positives, 12 false negatives) and **2/2** events detected.

**Table 9. Five-input presentation model results. SIMULATION ONLY - NOT EVIDENCE.**

| Split | Rows | Positives | Alerts | TP | FP | FN | Precision | Recall | F1 | PR-AUC | Brier | Events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Validation | 5,395 | 30 | 21 | 18 | 3 | 12 | 0.8571 | 0.6000 | 0.7059 | 0.7451 | 0.002491 | 2/2 |
| Test | 10,805 | 60 | 124 | 50 | 74 | 10 | 0.4032 | 0.8333 | 0.5435 | 0.6947 | 0.006542 | 4/4 |

The test result is high-recall and low-precision: the model finds most positive rows and all four events, but it raises 74 false alerts for 50 true positives. This is not suitable for a real warning. The test F1 of **0.5435** is lower than the full 72-hour model’s **0.7973**, as expected from a deliberately smaller input set that omits lags, rolling dissolved-oxygen features, and most weather context.

Feature importance is dominated by dissolved oxygen (**0.6262**) and water temperature (**0.2494**), followed by pH (**0.0462**), wind speed (**0.0397**), and rainfall (**0.0385**). This ordering is circular as an ecological finding because the synthetic generator injected the event effect mainly through low dissolved oxygen and high water temperature. The six fictional example rows produce five matches with the team’s illustrative bands, but that is a communication check, not an accuracy result. The bands are illustrative thresholds and were not validated against real fish kills.

### 5.8 Summary of evidence status

Table 10 separates what the study can support from what it cannot. The real dashboard is implemented and reports its limits. The real descriptive trend model is implemented and reported as an annual association. The synthetic pipeline is implemented and evaluated, but only under an injected event process. No real fish-kill model, real fish-kill performance metric, real risk score, zone risk map, advisory, or operational warning exists.

**Table 10. Claims and evidence status. Synthetic claims are simulation only and are not evidence.**

| Claim | Status | Evidence |
|---|---|---|
| A real fish-kill model was trained | Not supported | 0 real labels; 1 reported event; 0 verified events; readiness gate 1 pass / 1 partial / 8 fail |
| A descriptive annual trend model was fitted | Supported as descriptive only | 9-station balanced panel; DO -0.111861 mg/L/year (95% CI -0.141078 to -0.082643); temperature interval includes zero |
| Real fish-kill performance can be reported | Not supported | No real fish-kill model, predictions, or metrics |
| A real risk score, zone map, or advisory is available | Not supported | No fish-kill model; 0 coordinates; 5 of 15 lake stations with a zone label |
| The evidence dashboard is implemented | Supported as a descriptive instrument | Five pages; risk assessment unavailable; no synthetic marker; 16/16 contract tests |
| A synthetic pipeline can be implemented and evaluated | Supported only as simulation | 24/48/72-hour models; lead-time policies; five-input demo |
| Synthetic results estimate Laguna de Bay predictability | Not supported | Injected event process; 4 synthetic test events; no real observations |
| HIMPIL is operationally ready | Not supported | No daily data, verified events, negative windows, coordinates, user study, or advisory protocol |

The real and synthetic results answer different questions. The real results show that the evidence base is insufficient for fish-kill prediction, that the dashboard can report that insufficiency without inventing a risk level, and that a narrow annual trend can still be estimated descriptively. The synthetic results show that the proposed software pipeline can be implemented and evaluated under explicit assumptions. Neither result supports a claim that HIMPIL can predict real fish kills today.

Figures 1–7 remain to be produced. They must show the study design, the dashboard’s unavailable state, the evidence boundary, the synthetic pipeline, and the synthetic precision-recall or event timelines with visible **SIMULATION ONLY - NOT EVIDENCE** labels. No synthetic probability should be placed on a real map.

---

> **SIMULATION ONLY - NOT EVIDENCE** applies to Sections 4.4–4.8 and 5.4–5.7 and to every synthetic artifact referenced in this draft. Sections 3, 4.1–4.3, 4.9–4.11, 5.1–5.3, and 5.8 describe real evidence, the real dashboard, the descriptive annual trend model, quarantine rules, or an evidence-status summary. Table 10 explicitly separates real from synthetic claims.

---

## 6. Discussion

### 6.1 What the study demonstrates

The study set out to test whether a machine-learning early-warning system for fish kills in Laguna de Bay could be built from the supplied evidence. It could not. That negative result is the central finding, and it is not a software failure. The evidence audit found one reported event, no independently verified event, no dated station-monitoring water-quality observations, no pre-event observation, no credible negative window, and no station coordinates or authoritative lake-zone crosswalk. Under those conditions, a supervised fish-kill classifier would have no defensible target, no honest temporal split, and no meaningful held-out evaluation. The readiness gate formalizes that conclusion: 1 pass, 1 partial, and 8 fail.

The negative result matters because Laguna de Bay is a large, shallow, eutrophic tropical lake subject to aquaculture pressure and multiple catchment stressors (Cuvin-Aralar, 2016; Espaldon, 2009). Fish kills in Philippine aquaculture areas have been linked to eutrophic conditions, algal blooms, and oxygen depletion (Azanza et al., 2005; San Diego-McGlone et al., 2008), and oxygen decline is a global concern in coastal and inland waters (Breitburg et al., 2018; Diaz & Rosenberg, 2008). Those general processes make the HIMPIL question scientifically plausible. They do not, by themselves, supply the station-level, pre-event observations needed to predict a particular kill 72 hours in advance. The gap between a plausible mechanism and a validated prediction is exactly where the project's evidence audit sits.

The study still produces four defensible contributions. First, it provides a reproducible evidence audit and a readiness gate that can be reused when new data arrive. Second, it provides an evidence dashboard that reports annual and monthly summaries at their true resolution, with missing values left missing and the risk state left unavailable. Third, it fits the strongest real model the data can support: a descriptive annual trend on a balanced nine-station panel. Fourth, it provides a quarantined synthetic testbed that exercises the software pipeline, chronological validation, alert aggregation, and a five-input interface without presenting any of those results as real evidence.

The real trend result is narrow but informative. On the nine stations with complete 2016–2025 dissolved-oxygen records, the fitted station fixed-effects slope is **-0.111861 mg/L per year** (95% CI **-0.141078 to -0.082643**; cluster bootstrap **-0.137933 to -0.087157**), with an R² of **0.605079** across 90 station-years. The water-temperature slope is **+0.056015 °C per year** (95% CI **-0.012883 to 0.124912**), but its interval includes zero, so the direction is not established. The dissolved-oxygen interval is consistent with a decline in the annual station summaries, but the estimate is an association, not a causal effect. It does not use observation dates, does not identify the May 2019 event, and cannot be downscaled to a 72-hour warning. Its value is that it is defensible at the resolution the data actually have.

The dashboard is therefore not a stopgap for a missing model. It is the current product. It makes the evidence state inspectable: which station-years are complete, which variables are missing, which event is only reported, which readiness checks fail, and which data requests remain unanswered. It also makes the absence of a risk score explicit rather than filling the interface with a placeholder. That design choice follows from the audit: a risk number would be an invention, while a missing-value map, a readiness gate, and a descriptive trend are auditable claims.

### 6.2 What the synthetic results mean and do not mean

> **SIMULATION ONLY - NOT EVIDENCE**

The synthetic results demonstrate implementation, not predictability. The event overlay injects a known effect into a synthetic daily panel, and the models are then trained to recover that effect. The high test scores—F1 **0.6250** at 24 hours, **0.7477** at 48 hours, and **0.7973** at 72 hours, with ROC-AUC above **0.999**—are properties of the injected process. They show that the pipeline can learn a signal when the signal is present and the labels are well defined. They do not estimate how well a real fish kill can be predicted from real Laguna de Bay observations, because the real observations do not exist at the required resolution.

The feature-importance result illustrates the circularity. Dissolved oxygen (**0.6262**) and water temperature (**0.2494**) dominate the five-input model, but the synthetic generator injects the event effect mainly through low dissolved oxygen and high water temperature. The ordering is therefore a check that the model recovered the generator's design, not an ecological finding about the lake. A real feature-importance analysis would require real pre-event variation, a defensible negative class, and a model that was not trained on a process the analysts themselves specified.

The lead-time experiment is useful as a design lesson but not as a warning rule. The selected two-station, 72-hour cooldown policy issued four test episodes, detected all four synthetic test events, and produced no false episodes. Those counts are too small for confidence, and the policy was chosen after inspecting the test error profile. The result supports a specific point: the label horizon should match the intended warning lead time, and a confirmation rule can reduce repeated alerts. It does not show that the same rule would work on real events, where reporting delays, spatial correlation, and false-alarm costs are different.

The five-input presentation model is a communication aid. Its test F1 of **0.5435** and PR-AUC of **0.6947** are weaker than the full synthetic 72-hour model, as expected from a deliberately reduced input set. Its 124 test alerts—50 true positives, 74 false positives, and 10 false negatives—would not be acceptable for a real warning service. The Low, Medium, and High bands are illustrative interface labels, not validated risk thresholds. The demo is valuable because it shows that the proposed five fields can be wired into a reproducible pipeline and explained to an audience; it is not evidence that those fields are sufficient in the lake.

The synthetic work is nevertheless worth reporting. It tests the data contract, the temporal split, the evaluation code, the alert-aggregation logic, and the interface before real data arrive. It also exposes design issues that would otherwise remain hidden, such as the disagreement between a strict 24-hour label and a 72-hour warning objective. Those are engineering and methodological contributions. They must remain visibly separated from the real evidence, and they do not move the readiness gate.

### 6.3 Why no real risk score is shown

A real risk score would require a defined spatial unit, a defined time window, a calibrated probability, and a validation set that resembles the setting where the score would be used. None of those conditions is met. The water-quality record is annual, the weather record is monthly, the event record contains one reported period, and the station geography is incomplete. A score produced under those conditions would be false precision, not a cautious estimate.

The event record cannot be expanded into a training set by repeating its dates or municipalities. Repeating the same event across rows would place the same information in training and evaluation, a form of leakage that can inflate apparent performance (Kaufman et al., 2012). A chronological split would help if there were multiple dated events and a continuous pre-event series, but there is only one event period and no dated water-quality observations before it (Roberts et al., 2017). The 135 non-2019 lake station-years are not verified negatives; the files contain no incident-reporting log that would establish the absence of a fish kill. Absence of a published report is not evidence of absence.

The same logic applies to a zone risk map. Only five of the 15 lake stations carry a zone label in the station name, and no coordinates or authoritative crosswalk were supplied. Assigning stations to zones by guesswork would create a map that looks authoritative without being traceable. The dashboard therefore withholds the map, the score, the advisory, and the 24-hour forecast. The phrase **risk assessment unavailable** is not a placeholder for a model that is about to be trained; it is the correct statement about the current evidence.

The descriptive annual trend is not an exception. It is reported on a balanced panel, with uncertainty, and with an explicit prohibition on risk use. It describes change in annual station summaries; it does not estimate the probability of an event, identify a cause, or support a zone-level warning. Keeping that boundary visible is part of the result, not a disclaimer added after the fact.

### 6.4 Implications for HIMPIL

The near-term implication is a change of goal. Instead of treating "train a model" as the next milestone, the project should treat "build the evidence infrastructure" as the next milestone. That means daily or sub-daily dissolved oxygen, temperature, pH, rainfall, and wind observations; a verified incident log with dates, sites, zones, and causes; a reporting-completeness record that can support negative windows; station coordinates and an authoritative lake-zone crosswalk; documented aggregation rules; and permissions that allow the data to be used and shared. Those items are the path to the original goal, and they are more valuable than additional tuning of a synthetic model.

The current product should remain the evidence dashboard, with the descriptive trend as a separate, clearly labeled panel. The synthetic pipeline should remain a testbed for software and study-design questions. The five-input interface can remain a presentation and teaching tool. None of these should be described as an operational warning service, and none should be placed on a real map as if it were a risk estimate.

The governance implication is equally important. The readiness gate, the model card, the quarantine tests, and the visible simulation banner are not bureaucratic extras; they are the mechanism that keeps a plausible-looking demo from becoming an unsupported claim. If the project resumes external outreach, the request log should be updated with dates, recipients, and received files, and the gate should be re-run before any real model is trained. If outreach remains paused under D-009, the paper should say so plainly and should not imply that data are pending.

Finally, the project should plan for evaluation beyond model metrics. A warning system is a human and institutional intervention, not only a classifier. False alarms, missed events, trust, access, timing, and the capacity of fisherfolk, fish-pen operators, and local governments to act all matter. No user study or field evaluation was conducted here, so the paper cannot claim that a warning would be understood or acted upon. That work should precede any advisory or SMS feature.

### 6.5 Limitations

The real-data limitations are structural. Water quality is annual, weather is monthly, and the lake panel contains 15 stations over 10 years, with 111 complete station-years and 711 numeric values. Missing cells were not imputed. The trend model uses only the nine stations with complete 2016–2025 dissolved-oxygen records, so it is a balanced-panel result, not a lake-wide census. The panel is small, the stations are not a probability sample, and the analysis does not control for changes in monitoring practice, sampling depth, laboratory methods, or other time-varying confounders. The trend is descriptive and should not be read as a causal effect or as an event predictor.

The incident evidence is thin. There is one reported event, not an independently verified one. The 29 May 2019 sample was collected during the event, not before it, so it cannot serve as a pre-event predictor. There are no credible negative windows, no incident-reporting log, and no station coordinates or zone crosswalk. The May 2019 event is therefore a case for evidence audit, not a validated test case. The non-2019 station-years are not confirmed non-events.

The synthetic limitations are equally important. The daily values are generated, the event effect is assumed, and the annual calibration does not reproduce real daily variability. The overlay contains 20 synthetic events, but only four fall in the test period and two in validation. The lead-time policy was selected after inspecting the test error profile, so it is optimistic by construction. The five-input model omits lags, rolling oxygen features, and most weather context, and its communication bands are arbitrary. The synthetic metrics have no confidence intervals, no significance tests, and no operational cost analysis. They cannot be transferred to the lake.

The evaluation is also limited by what was not done. There was no user study with fisherfolk, fish-pen operators, or local government units; no field trial; no advisory protocol; no SMS deployment; no benefit-cost analysis; and no independent audit of the source extraction. Data access is paused under D-009, and no permission from LLDA, PAGASA, BFAR, or an LGU is assumed. The paper therefore reports a feasibility study and a software demonstration, not an operational evaluation.

### 6.6 Ethical and communication implications

The main ethical risk in a project like this is false assurance. A polished interface with a probability, a colored map, or a "High risk" badge can be read as an official warning even when the underlying model is synthetic. The project therefore keeps the simulation boundary visible, avoids placing synthetic probabilities on a real map, and does not present the demo as an advisory. The 2019 event is described as a reported event, not as a validated test case, and the limitations are stated in the same document as the results.

A future real system would need a model card that states intended use, prohibited use, training period, spatial coverage, performance by zone and season, known failure modes, and the evidence behind each threshold. It would need drift monitoring, a process for retiring the model when conditions change, and human oversight before any message is sent. It would also need a plan for false alarms and missed events, because both impose costs on the people the system is meant to help. Those requirements are not satisfied here, and they should not be implied by the current interface.

The project also has a responsibility to report the negative result clearly. It is tempting to present the synthetic pipeline as a success and leave the evidence gate in an appendix. That would invert the finding. The most important result is that the data cannot support the original claim yet, and the most useful contribution is a transparent account of what would be needed to change that.

---

## 7. Conclusion and next steps

### 7.1 Conclusion

HIMPIL is feasible today as an evidence dashboard, a descriptive annual-trend instrument, and a simulation testbed. It is not a validated early-warning system. The real fish-kill model is blocked by evidence, not by software: there are no dated pre-event water-quality observations, no verified events beyond one reported period, no credible negative windows, and no station coordinates or authoritative zone crosswalk. The readiness gate remains at 1 pass, 1 partial, and 8 fail, and the dashboard correctly reports **risk assessment unavailable**.

The descriptive trend adds a real but narrow result. On the nine-station balanced panel, annual mean dissolved oxygen changed by **-0.111861 mg/L per year** (95% CI **-0.141078 to -0.082643**), while the water-temperature interval included zero. The estimate is an association, not a cause, and it is not a fish-kill predictor. The synthetic experiments show that the pipeline can be implemented and evaluated under explicit assumptions, but their metrics are properties of the injected process, not estimates of Laguna de Bay predictability.

The responsible next step is data collection and verification, not more synthetic tuning. A model trained on the current evidence would produce a number without a defensible target. A dashboard that says so is more useful, and more honest, than a prediction that cannot be defended.

### 7.2 Next steps

1. Obtain daily or sub-daily dissolved oxygen, temperature, pH, rainfall, and wind observations at station level.
2. Obtain a verified fish-kill incident log with dates, sites, zones, causes, and reporting completeness.
3. Build a negative-window record that can support credible non-event periods.
4. Obtain station coordinates and an authoritative lake-zone crosswalk.
5. Document aggregation rules, sampling depth, laboratory methods, and data-sharing permissions.
6. Re-run the readiness gate against the new evidence before training any real fish-kill model.
7. Conduct a user study with fisherfolk, fish-pen operators, and local government units before any advisory or SMS feature is deployed.

### 7.3 Closing claim

> HIMPIL's most important current output is not a risk score. It is a defensible answer to the question: what would it take to build one responsibly?

---

## References

> **Citation style:** Provisional APA 7th edition. The final course template and reference style remain to be confirmed.

Azanza, R. V., Fukuyo, Y., Yap, L. G., & Takayama, H. (2005). *Prorocentrum minimum* bloom and its possible link to a massive fish kill in Bolinao, Pangasinan, Northern Philippines. *Harmful Algae, 4*(3), 519–524. https://doi.org/10.1016/j.hal.2004.08.006

Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324

Breitburg, D., Levin, L. A., Oschlies, A., Grégoire, M., Chavez, F. P., Conley, D. J., Garçon, V., Gilbert, D., Gutiérrez, D., Isensee, K., Jacinto, G. S., Limburg, K. E., Montes, I., Naqvi, S. W. A., Pitcher, G. C., Rabalais, N. N., Roman, M. R., Rose, K. A., Seibel, B. A., Telszewski, M., Yasuhara, M., & Zhang, J. (2018). Declining oxygen in the global ocean and coastal waters. *Science, 359*(6371), eaam7240. https://doi.org/10.1126/science.aam7240

Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review, 78*(1), 1–3. https://doi.org/10.1175/1520-0493(1950)078<0001:VOFEIT>2.0.CO;2

Cuvin-Aralar, M. L. A. (2016). Impacts of aquaculture on fish biodiversity in the freshwater lake Laguna de Bay, Philippines. *Lakes & Reservoirs: Science, Policy and Management for Sustainable Use, 21*(1), 31–39. https://doi.org/10.1111/lre.12118

Diaz, R. J., & Rosenberg, R. (2008). Spreading dead zones and consequences for marine ecosystems. *Science, 321*(5891), 926–929. https://doi.org/10.1126/science.1156401

Espaldon, M. V. O. (2009). Laguna de Bay: A tropical lake under pressure. In R. C. Ferrier & A. Jenkins (Eds.), *Handbook of catchment management* (pp. 389–406). Wiley-Blackwell. https://doi.org/10.1002/9781444307672.ch17

Fischhoff, B. (1995). Risk perception and communication unplugged: Twenty years of process. *Risk Analysis, 15*(2), 137–145. https://doi.org/10.1111/j.1539-6924.1995.tb00308.x

Kasperson, R. E., Renn, O., Slovic, P., Brown, H. S., Emel, J., Goble, R., Kasperson, J. X., & Ratick, S. (1988). The social amplification of risk: A conceptual framework. *Risk Analysis, 8*(2), 177–187. https://doi.org/10.1111/j.1539-6924.1988.tb01168.x

Kaufman, S., Rosset, S., Perlich, C., & Stitelman, O. (2012). Leakage in data mining: Formulation, detection, and avoidance. *ACM Transactions on Knowledge Discovery from Data, 6*(4), 1–21. https://doi.org/10.1145/2382577.2382579

Kramer, D. L. (1987). Dissolved oxygen and fish behavior. *Environmental Biology of Fishes, 18*(2), 81–92. https://doi.org/10.1007/BF00002597

Laguna Lake Development Authority. (2016–2025). *Annual water quality monitoring data for Laguna de Bay* [Data set]. Unpublished.

Philippine Atmospheric, Geophysical and Astronomical Services Administration. (2016–2025). *Monthly rainfall and wind station data* [Data set]. Unpublished.

Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881

Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLOS ONE, 10*(3), e0118432. https://doi.org/10.1371/journal.pone.0118432

Sambasivan, N., Kapania, S., Highfill, H., Akrong, D., Paritosh, P., & Aroyo, L. M. (2021). "Everyone wants to do the model work, not the data work": Data cascades in high-stakes AI. In *Proceedings of the 2021 CHI Conference on Human Factors in Computing Systems* (Article 39, pp. 1–15). Association for Computing Machinery. https://doi.org/10.1145/3411764.3445518

San Diego-McGlone, M. L., Azanza, R. V., Villanoy, C. L., & Jacinto, G. S. (2008). Eutrophic waters, algal bloom and fish kill in fish farming areas in Bolinao, Pangasinan, Philippines. *Marine Pollution Bulletin, 57*(6–12), 295–301. https://doi.org/10.1016/j.marpolbul.2008.03.028

Smith, V. H. (2003). Eutrophication of freshwater and coastal marine ecosystems: A global problem. *Environmental Science and Pollution Research, 10*(2), 126–139. https://doi.org/10.1065/espr2002.12.142

United Nations. (2015). *Transforming our world: The 2030 Agenda for Sustainable Development* (A/RES/70/1). https://sdgs.un.org/2030agenda

University of the Philippines Diliman. (2019, June 10). *Seasonal fish kill incident leaves thousands of unprofitable commodity fish in Laguna de Bay*. https://upd.edu.ph/seasonal-fish-kill-incident-leaves-thousands-of-unprofitable-commodity-fish-in-laguna-de-bay/

Zhu, M., Wang, J., Yang, X., Zhang, Y., Zhang, L., Ren, H., Wu, B., & Ye, L. (2022). A review of the application of machine learning in water quality evaluation. *Eco-Environment & Health, 1*(2), 107–116. https://doi.org/10.1016/j.eehl.2022.06.001
