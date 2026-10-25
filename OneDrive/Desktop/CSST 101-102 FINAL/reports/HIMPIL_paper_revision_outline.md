# HIMPIL paper revision outline

**Source document:** `C:\Users\miran\Downloads\Group-3-HIMPIL_REVISED.docx`  
**Prepared:** 24 October 2026  
**Status:** Planning outline; Sections 3-7, a provisional reference list, and the real descriptive trend are drafted in `reports/HIMPIL_paper_draft.md` (P8-3 through P8-5). Final formatting remains pending.  
**Working thesis:** HIMPIL is feasible today as an evidence dashboard and a simulation testbed, but not as a validated real fish-kill early-warning system. The binding constraint is data, not software.

> **SIMULATION ONLY - NOT EVIDENCE** applies to every synthetic result discussed below. The real dashboard must continue to show **risk assessment unavailable**.

---

## 1. What the current document is

The revised file is a **Research Topic Discovery & Regrouping** concept canvas. It contains:

- Parts I-V and VII-IX;
- the SDG and Hack4aProgress track;
- an individual research-interest card;
- the group research concept;
- a title formula; and
- a two-minute pitch.

It is **not yet a paper**. It has no methodology, data section, results, discussion, limitations, or reference list. It still describes HIMPIL in the future tense as a system that "will show risk levels, warnings, how to prepare, and suggested actions."

Part IV is present. It contains the preliminary research title, research problem, and RQ1-RQ3 table shown above. Part VI is absent from the extracted document: the sequence jumps from Part V to Part VII. The team confirmed that there is no Part VI content, so the paper treats it as intentionally skipped rather than an unresolved blocker.

The official group authors are **Jillian Rose O. Formeloza, Timothy John R. Kaharian, and Irene A. Miranda**. Part V is an individual card for **Valentin Howell A. Doñasales**; it is excluded from the group paper, and he is not an author.

---

## 2. Proposed title and abstract

### 2.1 Title

**Development of HIMPIL: A Feasibility and Simulation Study Toward a Machine-Learning Early-Warning System for Fish-Kill Events in Laguna de Bay**

**Authors:** Jillian Rose O. Formeloza, Timothy John R. Kaharian, Irene A. Miranda

Why this title works:

- "Development" keeps continuity with the original concept.
- "Feasibility and Simulation Study" states the actual contribution.
- "Toward" avoids claiming that a validated early-warning system exists.
- "Fish-Kill Events" is more precise than "Fish Kill Event Warning and Advisory System."

Avoid:

- "An Early Warning System for Laguna de Bay" (claims a system that does not exist).
- "Predicting Fish Kills" (claims real prediction).
- "Risk and Advisory System" (claims an advisory function that was not built or evaluated).

### 2.2 Draft abstract

Fish-kill events in Laguna de Bay threaten fish-pen operators, fisherfolk, and lake-dependent communities and are associated with low dissolved oxygen and other water-quality and weather conditions. The HIMPIL concept proposes a machine-learning early-warning system, but its feasibility depends on data that are rarely assembled at the needed temporal and spatial resolution. This study audits the available evidence, defines a model-readiness gate, and builds a transparent dashboard that reports the current evidence state without issuing risk predictions. The audit covers 14 sources, 15 lake stations, and 150 station-years, of which 111 are complete across six water-quality variables. It finds only one reported fish-kill event, zero independently verified events, zero dated station-monitoring water-quality rows, zero dated pre-event observations, no credible negative windows, and no authoritative station-to-zone crosswalk. The readiness gate therefore remains unmet, and the dashboard reports risk assessment unavailable. To test the proposed pipeline without misrepresenting synthetic results as evidence, we constructed a calibrated synthetic base dataset on the real station/year frame and a separate synthetic event overlay. Chronological random-forest experiments, a post hoc lead-time policy, and a five-input presentation demo show that the workflow can be implemented and evaluated. All synthetic results are labeled simulation only and are excluded from the dashboard. HIMPIL is feasible as an evidence-and-simulation system, not yet as a validated early-warning system; the next step is daily water-quality data, verified event records, negative windows, and station coordinates.

**Keywords:** Laguna de Bay; fish kill; dissolved oxygen; machine learning; early warning; data readiness; feasibility study; simulation

The abstract is approximately 230 words. Adjust to the course limit.

---

## 3. Proposed paper structure

### 1. Introduction

**Purpose:** Explain the local problem, the HIMPIL concept, and why the paper reports a feasibility study rather than a deployed model.

**1.1 Context and beneficiaries**
- Laguna de Bay as a fisheries and livelihood system.
- Fish-kill events and their effects on fish pens, fisherfolk, families, and LGUs.
- SDG 6 (Clean Water and Sanitation) and SDG 14 (Life Below Water).
- Track 4 (AI for Environmental Sustainability).
- Keep this section short; the current canvas repeats the same beneficiaries in several tables.

**1.2 The HIMPIL concept**
- Water-quality and weather data combined in one evidence and decision-support interface.
- Original ambition: risk levels, warnings, preparation advice, and SMS alerts.
- State clearly which parts are implemented and which remain requirements.

**1.3 The evidence problem**
- Data are spread across agencies and reports.
- Real water-quality data are annual station summaries; weather data are monthly.
- One reported event, zero verified events.
- No dated pre-event observations and no credible negative reporting.
- No coordinates or authoritative zone crosswalk.
- This is why a real supervised model cannot be trained or validated.

**1.4 Research questions and objectives**
Replace the original accuracy-first questions with feasibility questions:

- **RQ1:** What real data are available, and do they satisfy the requirements for supervised fish-kill risk modeling?
- **RQ2:** What evidence and readiness state can be represented transparently in a dashboard without inventing a risk score?
- **RQ3:** Can the proposed machine-learning pipeline be implemented and evaluated on a synthetic event overlay, and what does that demonstrate about feasibility rather than real predictability?
- **RQ4:** What data, validation, and governance steps are required before a real HIMPIL risk model can be validated?

Objectives:

1. Audit the available real data and incident evidence.
2. Define and apply a model-readiness gate.
3. Build a dashboard that reports the evidence state honestly.
4. Build and evaluate a quarantined synthetic pipeline.
5. Derive a data-collection and validation agenda.

**1.5 Contributions**
- An evidence audit for the Laguna de Bay fish-kill use case.
- A model-readiness gate that separates data sufficiency from software capability.
- A reproducible synthetic testbed with explicit quarantine rules.
- A dashboard that communicates uncertainty instead of a false risk score.
- A demonstration that the five proposed inputs can be used end-to-end.

**1.6 Scope and non-claims**
- This is not a real early-warning system.
- This is not a real fish-kill prediction model.
- This is not a zone risk map or advisory protocol.
- Synthetic metrics are not real performance.
- The 2019 report is a reported event, not an independently verified event.

**Sources:** current Parts I-IV, VII-IX; `README.md` Sections 1-3; `reports/tables/feasibility_report.md`.

---

### 2. Related work and conceptual framework

**Purpose:** Situate HIMPIL in fish-kill science, machine learning, and warning-system design. The current canvas has no related-work section.

**2.1 Fish-kill drivers in lake and aquaculture systems**
- Low dissolved oxygen as a proximate cause.
- Temperature, stratification, pH, rainfall/runoff, wind, and nutrient loading as contributing conditions.
- Why a single variable is insufficient.
- Keep the claim modest: the synthetic generator encodes low DO and high temperature; that does not establish the same relationship in Laguna de Bay.

**2.2 Machine learning for water-quality and early-warning applications**
- Supervised classification and imbalanced event prediction.
- Temporal validation and leakage prevention.
- Event-level evaluation versus row-level metrics.
- Lead time and false-alarm burden.
- Why accuracy is misleading when events are rare.

**2.3 Data readiness and feasibility assessment**
- ML feasibility depends on label quality, temporal resolution, spatial joins, negative windows, and governance.
- A readiness gate is a useful contribution when a model cannot yet be trained.
- Distinguish "no model" from "no data."

**2.4 Warning communication and uncertainty**
- False precision can harm trust.
- "Risk assessment unavailable" is a legitimate interface state.
- The difference between a simulation demo and an operational advisory.
- User-centered warning design is future work; no fisherfolk or LGU user study was conducted.

**2.5 Gap addressed by this study**
- HIMPIL's local context lacks a curated event and monitoring dataset.
- Most ML papers assume data that HIMPIL does not have.
- This paper documents the gap and tests the pipeline under explicitly synthetic assumptions.

**Reference plan:** use real, verifiable sources only. Do not cite the synthetic reports as external literature. Do not invent citations to fill this section.

---

### 3. Data and evidence audit

**Purpose:** Establish the real-data baseline before any modeling claim. This is the paper's strongest and most defensible contribution.

**3.1 Sources inspected**
- 14 sources (S01-S14).
- LLDA annual water-quality summaries.
- PAGASA monthly rainfall and wind summaries.
- BFAR/LGU/academic reports and the 2019 event article.
- Table: source, resolution, geographic key, time coverage, valid use.

**3.2 Coverage and completeness**
- 15 lake stations; 150 station-years (2016-2025).
- 111 station-years complete across six water-quality variables.
- 711 numeric lake water-quality values.
- Missing values must remain missing; do not convert missing to zero.
- Weather data are monthly, not daily.

**3.3 Incident evidence**
- 1 accepted report: Biñan/Pila, May 2019.
- 0 independently verified events.
- 0 official investigation reports.
- 0 dated station-monitoring water-quality rows.
- 4 during-event context measurements, but only one 29 May 2019 sample.
- 0 dated pre-event observations.
- 0 real 24-hour positive labels; 0 real 24-hour negative labels.
- The 135 non-2019 station-years cannot be treated as confirmed non-events.

**3.4 Model-readiness gate**
- Present the 10 checks: 1 pass, 1 partial, 8 fail.
- Explain why each failed check blocks real supervised training.
- Table: requirement, current status, evidence, consequence.

**3.5 Data-request status**
- 9 requests total: 1 acknowledged, 8 planned.
- 0 received files; 0 permissions.
- `LLDA-INC-01` remains acknowledged, not received or closed.
- Outreach is paused under decision D-009; do not describe it as actively pending.

**3.6 Implication**
- A real risk model cannot be trained, validated, or deployed with the current evidence.
- The dashboard must show risk assessment unavailable.
- The synthetic work is a separate feasibility exercise, not a substitute.

**Sources:** `dashboard/src/data/dashboard.json`; `reports/tables/feasibility_report.md`; `reports/tables/system_gaps_and_todo.md`; `reports/data_requests/data_access_log.csv`.

---

### 4. Methods

**Purpose:** Describe what was actually built and evaluated. Keep real and synthetic methods visibly separate.

**4.1 Study design**
- A feasibility-and-simulation design with four parts:
  1. evidence audit;
  2. dashboard and readiness gate;
  3. synthetic pipeline and chronological models;
  4. simulation-only experiments and presentation demo.
- Figure: study design flow.

**4.2 Evidence dashboard**
- Five pages: Overview, Water, Evidence, Model, Sources.
- Real-data-only bundle.
- "Risk assessment unavailable" state.
- No synthetic marker, risk score, zone map, or advisory.
- Explain that the dashboard is a reporting instrument, not a prediction interface.

**4.3 Synthetic base dataset**
- 15 real station labels, 2016-2025.
- 54,795 daily station-days.
- Six water-quality variables.
- Three synthetic weather zones.
- 900 annual anchor rows; calibration to real annual means.
- `data_origin = synthetic_base_v1`.
- The base dataset contains environmental values only; it does not contain fish-kill labels.

**4.4 Synthetic event overlay**
- 20 synthetic events and 10 stress-only periods.
- Four-day pre-event ramp, three-day event, five-day recovery.
- Separate from the base dataset.
- No May 2019 event date.
- 53,950 model-eligible rows.
- `data_origin = synthetic_base_v1_event_overlay`.

**4.5 Chronological models**
- 24-, 48-, and 72-hour event labels.
- Train before 2023; validation 2023; test 2024-2025.
- Random forest, logistic regression, and majority-class baseline.
- Backward-looking features only; no post-event leakage.
- Metrics: precision, recall, F1, PR-AUC, ROC-AUC, Brier, confusion counts, event detection.
- Why PR-AUC and event-level detection matter more than accuracy.

**4.6 Lead-time policy experiment (P6)**
- Post hoc analysis of the saved 24-hour model.
- Raw alerts classified as target-day, early pre-event, or stress-only.
- Four confirmation/cooldown policies compared.
- Selected illustrative policy: two stations confirm on the same day; 72-hour cooldown.
- This policy was chosen after inspecting the test error profile, so it is optimistic by construction.

**4.7 Five-input presentation model (P7)**
- Five inputs: DO, water temperature, pH, rainfall, wind speed.
- Target: synthetic 72-hour event label.
- Random forest; train/validation/test split as above.
- Illustrative bands: Low < 0.25; Medium 0.25 to < 0.50; High >= 0.50.
- The bands are communication labels, not validated thresholds.
- The model is deliberately simpler than the full synthetic model.

**4.8 Evaluation and quarantine rules**
- Real and synthetic artifacts cannot mix.
- No synthetic data in `data/processed/`.
- No synthetic model at `models/model.joblib`.
- No synthetic marker in `dashboard.json`.
- Every synthetic artifact carries **SIMULATION ONLY - NOT EVIDENCE**.
- Contract tests verify the separation.

**4.9 Ethics and governance**
- No real advisory was issued.
- No user data were collected.
- Data access is paused; permissions are not assumed.
- Synthetic examples are fictional and must be labeled as such.

**Sources:** `README.md` Sections 4-8; `sandbox/synthetic/README.md`; `models/synthetic/README.md`; `reports/tables/synthetic_base_report.md`; `reports/tables/synthetic_base_model_report.md`; `reports/tables/synthetic_lead_time_policy_report.md`; `reports/tables/synthetic_presentation_model_report.md`.

---

### 5. Results

**Purpose:** Report the real evidence first, then the synthetic results under a clear quarantine boundary. Do not blend them.

**5.1 Real evidence state**
- 14 sources; 15 stations; 150 station-years; 111 complete.
- 1 reported event; 0 verified; 0 dated water rows; 0 pre-event observations; 0 real labels.
- Readiness: 1 pass, 1 partial, 8 fail.
- Requests: 9 total, 1 acknowledged, 8 planned, 0 received, 0 files.
- Table: evidence counts.
- Figure: dashboard Overview showing **risk assessment unavailable**.

**5.2 Dashboard behavior**
- Five-page navigation works.
- Evidence boundary and readiness states are visible.
- Weather context and analysis plates are descriptive, not predictive.
- No risk score, zone risk map, or advisory.
- No synthetic marker in the production bundle.

**5.3 Real descriptive annual trend model**
- Balanced nine-station panel, 2016-2025; station fixed effects and common year term.
- DO: -0.111861 mg/L/year (95% CI -0.141078 to -0.082643; cluster bootstrap -0.137933 to -0.087157); n=90.
- Temperature: +0.056015 °C/year (95% CI -0.012883 to 0.124912; cluster bootstrap -0.009302 to 0.109758); n=81.
- Interpret as descriptive association only; not causal; not a fish-kill model; not a 72-hour model.
- Dashboard panel: **What the annual data can support**, marked **Descriptive only**.

**5.4 Synthetic base dataset**
- 54,795 station-days; 15 stations; 2016-2025.
- Calibration to annual anchors.
- Missingness and coverage summary.
- Label this subsection with a visible warning banner.

**5.5 Full synthetic base model**
- 24-hour: precision 0.4545, recall 1.0, F1 0.625, PR-AUC 0.568 on test.
- 48-hour: precision 0.5970, recall 1.0, F1 0.748, PR-AUC 0.957 on test.
- 72-hour: precision 0.6705, recall 0.9833, F1 0.797, PR-AUC 0.947 on test.
- 4/4 synthetic test events detected by the 24-hour model.
- Emphasize: these results reflect the injected synthetic event process.
- Do not compare them to real performance.

**5.6 Lead-time policy experiment**
- Raw test alerts: 44 (20 target-day, 23 early pre-event, 1 stress-only).
- Two-station / 72-hour cooldown: 4 episodes, 4/4 events, 0 false episodes, 2-3 day leads.
- Validation: 2 episodes, 2/2 events, 0 false, 1-2 day leads.
- One-station policy: 5 episodes, 4/4 events, 1 stress-only false episode.
- Three-station policy: 4 episodes, 4/4 events, 0 false, 2-day leads.
- State clearly: post hoc, small event count, simulation only.

**5.7 Five-input presentation model**
- Test: precision 0.4032, recall 0.8333, F1 0.5435, PR-AUC 0.6947, Brier 0.006542.
- 124 alerts: 50 true positives, 74 false positives, 10 missed positives.
- 4/4 synthetic test events detected.
- Validation: precision 0.8571, recall 0.6000, F1 0.7059, PR-AUC 0.7451; 2/2 events.
- Feature importance: DO 0.6262; water temperature 0.2494; pH 0.0462; wind 0.0397; rainfall 0.0385.
- Six fictional examples; five of six match the team's illustrative bands; not an accuracy check.
- The five-input model is weaker than the full 72-hour model by design.

**5.8 Summary of evidence status**
- Real fish-kill model: none.
- Real fish-kill metrics: none.
- Real descriptive trend model: fitted; annual association only.
- Real risk score: none.
- Synthetic pipeline: implemented and evaluated.
- Validation gate: not met.
- Operational readiness: not established.

---

### 6. Discussion

**Purpose:** Interpret the results without upgrading synthetic evidence into real evidence.

**6.1 What the study demonstrates**
- The data are the binding constraint for fish-kill prediction.
- The workflow can be implemented reproducibly.
- The dashboard can communicate missing evidence honestly.
- A narrow descriptive annual trend can be estimated on a balanced panel.
- Synthetic experiments can test design choices before real data arrive.
- A five-input interface is technically feasible.

**6.2 What the synthetic results mean and do not mean**
- They test the pipeline under assumed event effects.
- They do not estimate real predictability.
- Feature importance is partly circular because the generator injects the event effect through DO and temperature.
- The lead-time policy is post hoc and based on four test events.
- The five-input demo is a communication aid, not a replacement for the full model.

**6.3 Why no real risk score is shown**
- One reported event is not a training set.
- Annual water quality cannot support a 24-, 48-, or 72-hour label.
- Monthly weather cannot be aligned to daily events.
- Non-event years are not verified negatives.
- No coordinates or zone crosswalk means no station-to-zone risk map.
- A risk score would therefore be false precision.

**6.4 Implications for HIMPIL**
- Shift the near-term goal from "train a model" to "build the evidence infrastructure."
- Prioritize daily water-quality observations, verified event records, negative windows, and coordinates.
- Treat the dashboard as the current product and the synthetic pipeline as a testbed.
- Resume outreach only when the team decides to; do not imply that data are pending.

**6.5 Limitations**
- Real water quality is annual, not daily.
- The real trend is a descriptive annual association, not a causal or event model.
- Weather is monthly, not daily.
- One reported event; zero verified events.
- No dated pre-event observations.
- No credible negative windows.
- No station coordinates or authoritative zone crosswalk.
- Synthetic event process is assumed, not estimated from the lake.
- Small synthetic event count: 4 test events, 2 validation events.
- Post hoc policy selection is optimistic.
- Five-input model uses only five fields and loses lag/rolling context.
- Display bands are arbitrary communication labels.
- No user study with fisherfolk, fish-pen operators, or LGUs.
- No advisory protocol or field evaluation.
- Data access is paused; permissions are not established.

**6.6 Ethical and communication implications**
- Do not present a synthetic probability on a real map.
- Do not show synthetic results next to real evidence without a visible boundary.
- Do not call the demo an operational warning.
- Do not use the 2019 event as a validated test case.
- Report uncertainty and missingness plainly.

---

### 7. Conclusion and next steps

**7.1 Conclusion**
- HIMPIL is feasible as an evidence dashboard, a descriptive annual-trend instrument, and a simulation testbed.
- It is not yet a validated early-warning system.
- The real fish-kill model is blocked by evidence, not by software.
- The responsible next step is data collection and verification, not more synthetic tuning.

**7.2 Next steps**
1. Obtain daily or sub-daily DO, temperature, pH, rainfall, and wind data.
2. Obtain a verified fish-kill incident log with dates, sites, zones, and causes.
3. Build a reporting-completeness record for negative windows.
4. Obtain station coordinates and an authoritative lake-zone crosswalk.
5. Re-run the readiness gate.
6. Only after the gate passes, train and validate a real fish-kill model.
7. Conduct a user study before any advisory or SMS feature is deployed.

**7.3 Closing claim**
> HIMPIL's most important current output is not a risk score. It is a defensible answer to the question: what would it take to build one responsibly?

---

## 4. Mapping from the current concept canvas

| Current part or table | Current content | Action | New location |
|---|---|---|---|
| Part I - Explore the SDGs | SDG 6 and SDG 14 checkboxes and rationale | Keep, condense | 1.1 |
| Part II - Hack4aProgress | Track 4 rationale | Keep one short paragraph | 1.1-1.2 |
| Part III - SDG + local problem + technology | Problem statement and proposed technology | Rewrite as problem statement; remove future-tense system claims | 1.1-1.4 |
| Part IV - The Study That Interests Me the Most | Preliminary research title, problem statement, and RQ1-RQ3 table | Use the problem statement; rewrite the RQs; move the preliminary title to the title page | 1.3-1.4, title page |
| Part V - Research interest card | Individual card for Valentin | Exclude from the group paper; do not list him as an author | None |
| Part VII - Group research concept | Group problem, beneficiaries, data, output | Use as source material, not as final prose | 1.2, 3.1, 4.2 |
| Part VIII - Research title formula | Original long title | Replace with proposed title | Title page |
| Part IX - 2-minute pitch | Six pitch questions | Rewrite as abstract and elevator pitch | Abstract, 1.5 |
| Final Group Output canvas | Group details and expected output | Use for intro and objectives; do not paste | 1.2-1.4 |
| "Expected Output" row | Risk levels, warnings, advice | Move to future work or system requirements | 1.6, 7.2 |
| "Research Questions" row | Accuracy, factors, warnings | Replace with RQ1-RQ4 | 1.4 |
| "Possible Data" row | DO, temperature, rainfall, wind, events, zones | Convert into evidence audit and data request table | 3.1, 3.5 |
| "Proposed Technology" row | AI/ML, data analytics, prototype dashboard | Describe what was actually built; label the rest as future work | 4.2, 4.7, 7.2 |

---

## 5. Claims to rewrite

| Current claim or implication | Why it is a problem | Replacement |
|---|---|---|
| "Machine learning-based early warning system" | Implies a validated operational system | "Feasibility and simulation study toward a machine-learning early-warning system" |
| "Predict possible fish kill events and other risks" | No real fish-kill model; "other risks" is undefined; a descriptive annual trend exists separately | "Assess the feasibility of machine-learning-assisted fish-kill risk estimation" |
| "Show risk levels, warnings, how to prepare, and suggested actions" | Not implemented; would be an advisory | "Specify these as future requirements; the current dashboard shows risk assessment unavailable" |
| "Classify fish kill risk for selected lake zones" | No authoritative zone crosswalk | "Zone-level output is future work and depends on a station-to-zone crosswalk" |
| "Test the model using available historical records" | Not possible with one reported event | "Real evaluation is blocked; synthetic evaluation is reported separately" |
| "The accuracy and warnings will depend on the data collected" | There is no real accuracy to report | "No real-model accuracy can be reported; the gate remains unmet" |
| "SMS alerts are a proposed feature" | Not implemented | "SMS alerts remain a future feature and were not evaluated" |
| "Data access to be checked" | Understates the current status | "Nine requests prepared; one acknowledged; none received; outreach paused under D-009" |
| "Early warnings may help fisherfolk prepare" | Plausible but untested | "This is a hypothesis that requires user research; it was not evaluated in this study" |
| "Fish kill" / "fishkill" / "Fish Kill" inconsistency | Inconsistent terminology | Use "fish kill" as a noun and "fish-kill" as an adjective; standardize throughout |
| "Lagna de Bay" typo | Obvious error | "Laguna de Bay" |
| "Fishfolk" | Nonstandard | "Fisherfolk" |

---

## 6. Where the P5/P6/P7 results go

| Result | Location in paper | Required label | What to say |
|---|---|---|---|
| P5 dashboard refresh and real counts | Results 5.1-5.2 | Real evidence | 14 sources; 15 stations; 150 station-years; 111 complete; 1 reported event; 0 verified; 9 requests, 1 acknowledged, 0 received |
| Readiness gate | Methods 3.4 and Results 5.1 | Real evidence | 1 pass, 1 partial, 8 fail; gate not met |
| Synthetic base dataset | Methods 4.3 and Results 5.3 | **SIMULATION ONLY - NOT EVIDENCE** | 54,795 station-days; 15 stations; 2016-2025; calibrated to annual anchors |
| Full synthetic base model | Results 5.4 | **SIMULATION ONLY - NOT EVIDENCE** | 24h F1 0.625; 48h F1 0.748; 72h F1 0.797; 4/4 synthetic test events |
| P6 lead-time policy | Results 5.5; detailed tables in appendix | **SIMULATION ONLY - NOT EVIDENCE** | 44 raw alerts; 2-station/72h policy: 4 episodes, 4/4 events, 0 false; post hoc |
| P7 five-input demo | Results 5.6; example table in appendix | **SIMULATION ONLY - NOT EVIDENCE** | Test F1 0.5435; PR-AUC 0.6947; 124 alerts (50 TP, 74 FP, 10 FN); 4/4 events; bands illustrative |
| P7 feature importance | Results 5.6 or appendix | **SIMULATION ONLY - NOT EVIDENCE** | DO 0.6262; temperature 0.2494; synthetic effect, not a real lake finding |
| Six fictional example rows | Appendix D | **FICTIONAL INPUTS** | Interface illustration only; five of six match team labels; not accuracy |
| Test suite and build | Methods 4.8 or appendix | Reproducibility | 16/16 contract tests; dashboard build passes; no synthetic marker in dashboard |

---

## 7. Tables and figures plan

### Tables

1. **Table 1 - Data sources and resolution.** Source, period, spatial key, resolution, valid use.
2. **Table 2 - Coverage and completeness.** 15 stations, 150 station-years, 111 complete, 711 values.
3. **Table 3 - Incident evidence.** Reported events, verified events, dated water rows, pre-event observations, negative labels.
4. **Table 4 - Model-readiness gate.** 10 checks with pass/partial/fail and consequence.
5. **Table 5 - Data-request status.** 9 requests, 1 acknowledged, 8 planned, 0 received, 0 files.
6. **Table 6 - Synthetic dataset design.** 15 stations, 2016-2025, 54,795 station-days, 20 events, 10 stress-only periods.
7. **Table 7 - Synthetic model metrics.** 24/48/72-hour precision, recall, F1, PR-AUC, event detection.
8. **Table 8 - Lead-time policy results.** Raw alerts and four policies; test and validation.
9. **Table 9 - Five-input demo metrics.** Test and validation metrics, confusion counts, feature importance.
10. **Table 10 - Claims and evidence status.** What can be claimed, what cannot, and why.

### Figures

1. **Figure 1 - Study design.** Evidence audit -> readiness gate -> dashboard -> synthetic testbed -> data agenda.
2. **Figure 2 - Dashboard Overview.** Must show **risk assessment unavailable**.
3. **Figure 3 - Evidence boundary.** Real evidence versus simulation-only artifacts.
4. **Figure 4 - Synthetic data pipeline.** Base dataset -> event overlay -> labels -> chronological models.
5. **Figure 5 - Precision-recall or event timeline.** Synthetic only; visible warning banner.
6. **Figure 6 - Lead-time episodes.** Synthetic event timeline with early alerts and cooldown.
7. **Figure 7 - Five-input demo.** Example probabilities and bands; fictional inputs only.

Every synthetic figure or table must carry a visible **SIMULATION ONLY - NOT EVIDENCE** banner in the caption or figure itself. Do not place a synthetic probability on a real map.

---

## 8. Reference plan

A provisional APA 7th-edition reference list is now in `reports/HIMPIL_paper_draft.md`. It contains only verified sources that are cited in the text. The final course style and any additional sources remain to be confirmed.

**Data and context**
- LLDA water-quality reports and workbooks actually used.
- PAGASA rainfall and wind sources actually used.
- BFAR, LGU, and academic reports actually used.
- 2019 event article (UPD or other) actually used.
- Philippine Statistics Authority or other fishery context sources, if used.

**SDG and policy**
- Official SDG 6 and SDG 14 descriptions.
- Laguna de Bay management or policy sources, if used.

**Fish-kill science**
- Peer-reviewed work on dissolved oxygen, temperature, stratification, and fish kills.
- Aquaculture and lake case studies, where relevant.
- Do not overgeneralize from marine or temperate systems.

**Machine learning and evaluation**
- Random forest and logistic regression methods.
- Class imbalance, precision-recall AUC, and event-level evaluation.
- Temporal validation and leakage prevention.
- Calibration and Brier score, if discussed.

**Warning communication**
- Uncertainty communication and false-alarm research.
- Human-centered early-warning design.
- If no user study is conducted, say so rather than citing user needs as established.

**Rule:** every reference must be cited in the text; every citation must be in the reference list. Do not cite the synthetic reports as external literature. They are project artifacts.

---

## 9. Writing order

1. **Freeze the title, abstract, and RQ1-RQ4.** Do not write results before the claims are fixed.
2. **Build Tables 1-5 from the repository.** These are the real-evidence backbone.
3. **Write Section 3 (evidence audit).** This is the strongest section and sets the tone.
4. **Write Section 4 (methods).** Use the actual scripts and reports; do not add methods that were not run.
5. **Write Section 5 (results).** Copy exact numbers from the reports; label every synthetic subsection.
6. **Write Section 6 (discussion) and Section 7 (limitations).** Keep the negative result central.
7. **Write Section 1 (introduction) last.** It is easier after the evidence and results are clear.
8. **Write Section 2 (related work) and the references.** Use real sources only.
9. **Write Section 8 (conclusion and next steps).**
10. **Internal review.** Check every number, label, and claim against the repository.
11. **Format to the course template.** Check word count, headings, table numbering, and citation style.

---

## 10. Quality checklist

### Evidence integrity
- [ ] Every real-data number matches `README.md`, `dashboard.json`, or the feasibility report.
- [ ] Every synthetic number is labeled **SIMULATION ONLY - NOT EVIDENCE**.
- [ ] The 2019 event is described as reported, not verified.
- [ ] Missing data are not converted to zero.
- [ ] No real fish-kill model or real fish-kill metric is claimed.
- [ ] The descriptive annual trend model is labeled descriptive only, not a fish-kill model.
- [ ] No zone map, risk score, or advisory is claimed.
- [ ] LLDA is not described as having provided data.
- [ ] Outreach is described as paused under D-009, not pending.

### Argument integrity
- [ ] The paper reports a feasibility study, not a validated system.
- [ ] The negative result is stated early and clearly.
- [ ] Synthetic results are used to test the pipeline, not to estimate real predictability.
- [ ] The limitations section is specific and complete.
- [ ] The conclusion follows from the evidence.
- [ ] The title matches the content.

### Presentation integrity
- [ ] All acronyms are defined on first use.
- [ ] Fish-kill terminology is consistent.
- [ ] Tables and figures are numbered and cited in the text.
- [ ] Synthetic figures carry a visible warning.
- [ ] References are real, complete, and consistently formatted.
- [ ] The paper follows the course template and word limit.

### Reproducibility
- [ ] `16/16` contract tests pass.
- [ ] `npm run build` passes.
- [ ] The dashboard still shows **risk assessment unavailable**.
- [ ] `models/model.joblib` remains absent.
- [ ] No synthetic marker appears in `dashboard/src/data/dashboard.json`.

---

## 11. Decisions and open questions

### Resolved

- **Authors:** Jillian Rose O. Formeloza, Timothy John R. Kaharian, and Irene A. Miranda. Valentin Howell A. Doñasales is not an author, and his Part V individual card is excluded from the paper.
- **Part V:** Excluded from the group paper. Do not include it as an appendix either.
- **Part VI:** The source canvas has no Part VI heading or content. It is intentionally skipped, not unresolved.

### Open

1. **Paper length and template:** What is the required word count, citation style, and section format?
2. **P6 in main text or appendix:** The lead-time experiment is a strong feasibility result, but it is post hoc and based on four test events. Main text with a short table, details in appendix, is recommended.
3. **P7 in main text or appendix:** The five-input demo is useful for the presentation. Main text as a short demonstration, full metrics in appendix, is recommended.
4. **Dashboard screenshots:** Include the Overview and evidence boundary; show the risk assessment unavailable state. Do not include a synthetic probability on a real map.
5. **Team example labels:** Describe them as illustrative and fictional. Do not call them ground truth.
6. **Data-request wording:** Use "outreach paused under D-009"; do not imply active negotiations.
7. **Reference style:** Choose APA, IEEE, or the course style before drafting the reference list.

---

## 12. What not to do

- Do not paste the concept-canvas tables into the paper as if they were results.
- Do not describe HIMPIL as a working early-warning system.
- Do not report synthetic metrics as real performance.
- Do not put a synthetic probability on a real map of Laguna de Bay.
- Do not add a risk score, zone risk map, or advisory to the dashboard.
- Do not claim that the 2019 event is independently verified.
- Do not claim that LLDA provided data or permission.
- Do not claim that SMS alerts were implemented.
- Do not claim that fisherfolk or LGUs evaluated the warnings.
- Do not use "accuracy" as the main metric for a rare-event problem.
- Do not hide the negative result in the limitations section; it is the main finding.
- Do not invent citations, data, or agency permissions.
- Do not treat the synthetic presentation model as a substitute for the real fish-kill model.

---

## 13. One-paragraph summary for the team

The revised concept canvas proposes HIMPIL as a machine-learning early-warning system, but the repository shows that the real evidence is not yet sufficient to train or validate one. The paper should therefore report a feasibility-and-simulation study: an evidence audit, a readiness gate, a real-data-only dashboard, a quarantined synthetic pipeline, a post hoc lead-time experiment, and a five-input presentation demo. The central finding is that HIMPIL is feasible as an evidence system and simulation testbed, not yet as an operational warning system. The next step is to collect daily water-quality data, verified event records, negative windows, and coordinates, then re-run the gate before claiming any real predictive performance.

> **SIMULATION ONLY - NOT EVIDENCE**
