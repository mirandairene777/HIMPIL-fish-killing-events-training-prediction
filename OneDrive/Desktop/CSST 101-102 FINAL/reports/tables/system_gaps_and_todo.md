# HIMPIL system gaps and to-do list

**Prepared:** 23 October 2026  
**Updated:** 24 October 2026  
**Scope:** the real HIMPIL evidence system, the synthetic base dataset, and the synthetic base-model and presentation demonstrations.

> **The synthetic model is not evidence.** Its event dates, event effects, labels,
> probabilities, and metrics are simulated. The real dashboard must continue to
> show **risk assessment unavailable** until the Section 6 gate passes.

---

## 1. Current position

| Item | Status |
|---|---|
| Real evidence dashboard | Complete as a Phase 1–9 foundation; risk assessment unavailable |
| Real fish-kill model | None |
| Real fish-kill metrics | None |
| Real descriptive model | Annual station fixed-effects trend on the nine-station balanced panel; descriptive only |
| Real descriptive trend metrics | DO **-0.111861 mg/L/year** (95% CI **-0.141078 to -0.082643**); temperature **+0.056015 °C/year** (95% CI **-0.012883 to 0.124912**, includes zero) |
| Synthetic base dataset | Complete; 15 stations, 2016–2025, 54,795 station-days; not evidence |
| Synthetic base model | Complete as a demonstration only; 20 synthetic events, 4 in the test period; a post hoc lead-time policy experiment is also complete and simulation only |
| Synthetic presentation model | Complete; five-input 72-hour demo; test F1 0.5435 / PR-AUC 0.6947; not evidence |
| LLDA incident request | `acknowledged`; professor approval letters requested; no files received |
| Other data requests | 8 planned; no files and no permissions recorded |
| Real fish-kill model gate | Blocked |

### Synthetic test output (simulation only)

Random forest on the chronological 2024–2025 test period:

| Horizon | Positives | Precision | Recall | F1 | PR-AUC | Brier |
|---:|---:|---:|---:|---:|---:|---:|
| 24 h | 20 | 0.455 | 1.000 | 0.625 | 0.568 | 0.0020 |
| 48 h | 40 | 0.597 | 1.000 | 0.748 | 0.957 | 0.0021 |
| 72 h | 60 | 0.670 | 0.983 | 0.797 | 0.947 | 0.0026 |

All 4 synthetic test events were flagged by at least one 24-hour alert. These are
properties of the injected event process, not evidence that real fish kills are
predictable. The 24-hour model had 24 false positives: 23 were pre-event rows 2–3
days before an event and 1 was a stress-only row. The 24-hour label counts the
early detections as negative.

---

## 2. System loopholes and problems

### 2.1 Blocking evidence gaps

1. **Annual summaries cannot support a daily early-warning model.**
   The supplied LLDA water-quality data are annual station summaries. The model
   needs daily or sub-daily observations before an event.

2. **One reported event is not enough.**
   The project has one accepted May 2019 report, zero independently verified
   events, and no official investigation report. There is no credible event
   sample for training or evaluation.

3. **There are no credible negative windows.**
   A fish-kill model needs periods where monitoring was active and no fish kill
   was reported. Without a reporting-completeness record, absence of a report
   cannot be treated as a negative label.

4. **There are no usable pre-event observations.**
   The four during-event context measurements in the 2019 article cannot be used
   as predictors. There are zero dated pre-event water-quality observations.

5. **There is no station geometry.**
   No station coordinates were supplied. Events cannot be assigned to stations or
   lake zones, and no map or spatial validation is defensible.

6. **There is no authoritative station-to-zone crosswalk.**
   Only five station labels state a zone. Ten lake stations have blank zones.
   A synthetic mapping must not be presented as a real one.

7. **2025 data are partial or unverified.**
   The 2025 weather source is incomplete, and the 2025 annual water-quality
   completeness is undocumented. These values must remain flagged.

8. **Permissions and ethics are incomplete.**
   LLDA requested professor approval letters. No data-sharing permission, ethics
   approval, or custodian assignment is recorded. A request being acknowledged is
   not the same as permission or receipt.

### 2.2 Synthetic model limitations

9. **The event process is injected, not observed.**
   The model sees a strong four-day pre-event ramp because the script puts it
   there. High recall is an artifact of that construction.

10. **The labels are synthetic and circular.**
    Event labels come from the same script that injects the event effect. The
    model is learning the simulator, not Laguna de Bay.

11. **The 24-hour label punishes early warnings.**
    An alert two or three days before an event is a false positive for the
    24-hour target. The real system needs a lead-time policy that states whether
    early warning is acceptable, how early, and how repeated alerts are counted.

12. **The test set is tiny.**
    Four synthetic event periods and 20 positive 24-hour rows are not enough for
    stable estimates or confidence intervals. One event can change the metrics.

13. **The threshold is fixed at 0.5.**
    No validation-based threshold selection, cost analysis, or alert-budget
    policy exists. Precision and recall will change substantially with a different
    threshold.

14. **Probabilities are not calibrated for operations.**
    Brier scores are reported, but there is no reliability diagram, calibration
    curve, or decision analysis. A probability is not an advisory.

15. **Annual-mean calibration is not daily realism.**
    The base generator matches annual station means, not daily distributions,
    extremes, autocorrelation, cross-variable dependence, or event mechanisms.
    The event overlay also changes the affected station-years’ annual means, so
    the base calibration audit does not apply to the overlay. A model trained on
    it cannot establish real predictability.

16. **Weather is a network mean of synthetic zones.**
    The model uses the mean of three synthetic weather zones because no real
    station-to-lake-zone mapping exists. This avoids inventing a mapping but is
    not a realistic weather exposure model.

17. **Feature importance is not causal evidence.**
    DO dominates the synthetic model because DO was the strongest injected
    signal. That is a simulator property, not proof that DO causes fish kills.

18. **No external or prospective validation.**
    There is no held-out site, future season, or independent dataset. The only
    test is a later slice of the same simulation.

### 2.3 Engineering and operational gaps

19. **No one-command end-to-end pipeline.**
    The Python, R, base-dataset, model, dashboard, and test steps are separate.
    A new teammate can run them in the wrong order.

20. **No continuous integration or environment lock.**
    Tests are run manually. `requirements.txt` is not a lockfile. The commands are
    Windows/PowerShell-oriented.

21. **No automated data validation layer.**
    Schema, units, date coverage, station identity, duplicate rows, and outlier
    checks are partly in scripts and tests, but not a reusable validator with
    machine-readable reports.

22. **SQLite is not integrated with the application.**
    The base dataset has a SQLite database and long-format view, but the dashboard
    and model scripts read CSVs. There is no single source of truth at runtime.

23. **No real-time ingestion or scheduling.**
    There is no PAGASA/LLDA connector, no ingestion queue, no freshness check, and
    no retry/alerting path.

24. **No deployment, API, authentication, or rate limiting.**
    The system is a local research repository. It is not a service.

25. **No monitoring or drift detection.**
    There is no plan for data drift, concept drift, false-alarm review, missed
    events, model retraining, or rollback.

26. **No release/versioning discipline for data and models.**
    Manifests exist for the synthetic artifacts, but there is no approved real
    data release, model registry, or change log tied to a deployment.

27. **The dashboard is deliberately disconnected from synthetic data.**
    That is correct for safety, but it means there is no end-to-end demonstration
    of synthetic predictions in a UI. Any future demo must be a separate,
    clearly labeled route.

28. **Tests verify contracts, not model quality.**
    The suite checks quarantine, labels, dashboard agreement, and calibration.
    It does not and cannot prove predictive validity.

### 2.4 Governance and presentation gaps

29. **No named project owner, data custodian, or model reviewer.**
    Roles and decision rights are documented as blanks. Accountability is unclear.

30. **No adviser/faculty sign-off recorded.**
    The LLDA reply specifically asks for professor approval letters.

31. **No approved advisory wording.**
    There is no reviewed message for fishers, LGUs, or the public. A probability
    must not become an emergency instruction without authority.

32. **No stakeholder usability testing.**
    Fishers, LGU staff, and LLDA/BFAR users have not tested the interface or the
    alert wording.

33. **No benefit/harm analysis.**
    False alarms, missed events, trust loss, and unequal access have not been
    assessed.

34. **The real goal remains unmet.**
    The synthetic demo can support a feasibility study and a software walkthrough.
    It cannot support the original operational claim.

---

## 3. To-do list

> **External evidence tasks are paused under D-009 (2026-10-23).** They remain the path to the original goal if outreach resumes, but they are not the current next action. The P5 dashboard refresh and the first P6 experiment (lead-time policy) are complete; the next active work is the paper revision in `README_WORKPLAN.md`.

### Priority 0 — unblock real evidence

| ID | Task | Exit criterion | Status |
|---|---|---|---|
| T01 | Send the signed professor approval letter to LLDA and record date, recipient, and channel | A dated access-log entry and a sent letter copy exist | Paused (D-009) |
| T02 | Obtain LLDA/BFAR dated incident records with verification status | At least 3 independent verified event periods with exact dates | Pending |
| T03 | Obtain daily or sub-daily water-quality observations | A dated, station-linked dataset with units and QA flags | Pending |
| T04 | Obtain daily/hourly weather linked to documented stations | A station-date weather table with coverage metadata | Pending |
| T05 | Obtain station coordinates and an authoritative zone crosswalk | Every station has a documented location and zone | Pending |
| T06 | Obtain a reporting-completeness record for negative windows | A documented basis for credible no-event labels | Pending |
| T07 | Record data-sharing permission and ethics approval | Signed permission or an approved data-use record | Pending |

### Priority 1 — real data and labels

| ID | Task | Exit criterion | Status |
|---|---|---|---|
| T08 | Build a real ingestion and QA pipeline | Versioned raw/processed outputs with validation report | Not started |
| T09 | Define the real fish-kill label and lead-time policy | A written, adviser-reviewed target definition | Not started |
| T10 | Verify and date every event; separate reported from verified | An event audit table with evidence links | Not started |
| T11 | Build negative windows from reporting completeness | A defensible no-event label table | Not started |
| T12 | Build station/zone features from the real crosswalk | No synthetic zone mapping in the real fish-kill model | Not started |
| T13 | Run leakage and temporal-order tests on real data | Tests show no future or post-event predictors | Not started |

### Priority 2 — real fish-kill model gate

| ID | Task | Exit criterion | Status |
|---|---|---|---|
| T14a | Fit a descriptive annual trend model on the balanced real panel | Model card and report exist; no fish-kill labels used | **Complete (P9)** |
| T14 | Re-run the Section 6 gate on real data | All gate items pass with evidence | Not started |
| T15 | Train a real fish-kill baseline and a tree-based model chronologically | Reproducible train/validation/test results | Not started |
| T16 | Evaluate real fish-kill precision, recall, F1, PR-AUC, calibration, and event detection | Report with confidence intervals and error analysis | Not started |
| T17 | Select an operating threshold using validation and an alert budget | Documented threshold and cost rationale | Not started |
| T18 | Obtain independent review of labels, features, and results | Reviewer sign-off recorded | Not started |

### Priority 3 — engineering and operations

| ID | Task | Exit criterion | Status |
|---|---|---|---|
| T19 | Add a one-command pipeline with stage checks | Clean checkout reproduces all artifacts | Not started |
| T20 | Add CI, a lockfile, and cross-platform commands | CI green on a clean environment | Not started |
| T21 | Add a reusable data validator with machine-readable output | Schema/unit/date/station checks fail loudly | Not started |
| T22 | Make SQLite or a database the runtime source of truth | Dashboard/model read one versioned store | Not started |
| T23 | Add freshness, drift, and retraining monitoring | Alerts and runbook exist | Not started |
| T24 | Add a separate synthetic demo route if needed | Route is clearly labeled and cannot show real risk | Not started |

### Priority 4 — evaluation and governance

| ID | Task | Exit criterion | Status |
|---|---|---|---|
| T25 | Conduct beneficiary and LGU usability testing | Written findings and changes | Not started |
| T26 | Complete a benefit/harm and false-alarm analysis | Reviewed risk register | Not started |
| T27 | Approve advisory wording and authority | Signed communication protocol | Not started |
| T28 | Release a real data dictionary and model card | Versioned public-facing documentation | Not started |
| T29 | Revisit the thesis title/abstract if data stay unavailable | Approved feasibility-study framing | In progress |

---

## 4. What can be shown now

- The real evidence dashboard and its “risk assessment unavailable” state.
- The real descriptive annual trend estimate: DO **-0.111861 mg/L/year** (95% CI **-0.141078 to -0.082643**) and temperature **+0.056015 °C/year** (95% CI **-0.012883 to 0.124912**) on the nine-station balanced panel. It is descriptive only, not a fish-kill model or a 72-hour model.
- The real Tanay, Rizal rainfall panel: complete-year annual totals (2016–2024), monthly climatology (2016–2024), and the January–June 2025 partial total shown separately. It is a single-station regional proxy, not a lake measurement, and is descriptive only.
- The synthetic base dataset and its calibration/coverage report.
- The synthetic base model as a **software demonstration only**.
- The post hoc synthetic lead-time policy experiment, clearly labeled **SIMULATION ONLY - NOT EVIDENCE**.
- The five-input synthetic presentation demo for a team walkthrough, clearly labeled **SIMULATION ONLY - NOT EVIDENCE**.
- The local browser demo at `sandbox/presentation_app/app.py` for the five-input model; it is local-only and separate from the evidence dashboard.
- The event-overlay audit, metrics, model card, and quarantine tests.
- The data-request package and current request status.
- The drafted paper Sections 3-7 (evidence audit, methods, results, discussion, limitations, conclusion, and provisional references) in `reports/HIMPIL_paper_draft.md`; all synthetic results remain labeled **SIMULATION ONLY - NOT EVIDENCE**.

## 5. What must not be claimed

- That HIMPIL can predict real fish kills.
- That the synthetic metrics are real performance.
- That 20 synthetic test positives establish reliability.
- That the synthetic event dates are historical incidents.
- That a station/zone mapping exists when it does not.
- That LLDA has granted permission or supplied data.
- That the Section 6 gate has passed.
- That the system is ready for public advisories.

---

## 6. Recommended next action

**Current learning track:** **P5, the first P6 experiment, the P7 presentation demo, and P9 real-data alignment are complete. The P8 paper revision is in progress (Sections 3-7 and provisional references drafted, including the real descriptive trend).** The real Tanay rainfall panel is part of the P5 dashboard (`weather.lakeArea`); it shows complete-year annual totals and monthly climatology from S01, with partial 2025 kept separate. The real trend model is in `reports/tables/real_trend_model.json` and `real_trend_model_card.md`; it is descriptive only. The lead-time policy experiment is in `reports/tables/synthetic_lead_time_policy_report.md`; the five-input demo is in `reports/tables/synthetic_presentation_model_report.md`; the paper outline is in `reports/HIMPIL_paper_revision_outline.md`, and the evidence-audit-to-conclusion draft is in `reports/HIMPIL_paper_draft.md`. All synthetic results are **SIMULATION ONLY - NOT EVIDENCE**. Next: complete the abstract and any required introduction/related work, run the consistency review, and format to the course template (P8-6). Do not train a real 72-hour fish-kill model until the gate passes; the annual data cannot support one. Optionally run a second P6 experiment (probability calibration or a model trained directly against a 72-hour label); keep every synthetic metric in the sandbox and label it simulation only.

**If outreach resumes:** finish **T01** first — send the signed professor approval letter to LLDA and log the actual date, recipient, and channel. In parallel, keep the real dashboard unchanged and use the synthetic base model only for internal software review. Do not connect it to the dashboard, and do not present its metrics as evidence.
