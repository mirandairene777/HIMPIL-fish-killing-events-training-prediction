# Roles and decision rights

**Status:** Role structure and decision rules defined. One LLDA incident-records request has been submitted and acknowledged; **named individual assignments and adviser approval are still incomplete.** These must be completed before data are accepted or further requests are sent.

This file implements task A7. It separates the person who prepares a request from the person who accepts data, approves a label change, or authorizes a model or publication decision. In a small student project one person may hold more than one role, but the overlap must be disclosed and the adviser must review the resulting decision.

## 1. Roles

| Role | Responsibility | Assigned to |
|---|---|---|
| Project owner / student researcher | Maintains the workplan, prepares requests, runs the analysis, documents decisions | HIMPIL Research Group; individual names `[To be recorded]` |
| Faculty adviser | Reviews the scientific design, event labels, model gate, and publication | `[To be recorded]` |
| Data custodian | Stores raw files, records hashes and permissions, controls access and retention | `[To be recorded]` |
| Analyst | Runs the documented pipeline and reports results without changing labels silently | `[To be recorded]` |
| Independent reviewer | Reviews event evidence, leakage controls, or model evaluation when available | `[To be assigned]` |
| Agency data owner | Owns the requested data and sets release, attribution, and publication conditions | External, per request |
| Institutional records or ethics contact | Advises on data agreements, privacy, or human-participant review when required | `[To be identified]` |

### Authorship and acknowledgement

Authorship follows substantive contribution to the research, analysis, and writing, not data ownership. The planned arrangement is:

| Output | Lead author | Required review | Acknowledgement |
|---|---|---|---|
| Thesis, report, or dashboard | Project owner | Faculty adviser | Data providers and reviewers as permitted |
| Methods or data note | Project owner | Faculty adviser and data custodian | Agency source and permission reference |
| Model card, if the gate later passes | Analyst | Project owner and faculty adviser | Independent reviewer if one participated |

Agency staff are acknowledged as data providers unless they meet authorship criteria, agree to authorship, and their agency's terms allow it. An independent reviewer is not automatically an author.

### Named assignment record

| Field | Value |
|---|---|
| Project owner / group | HIMPIL Research Group |
| Individual names | `[To be recorded]` |
| Institution / department | Laguna State Polytechnic University — BSCS program (campus/department to be recorded) |
| Institutional email | `[To be recorded]` |
| Faculty adviser name | `[To be recorded]` |
| Adviser email | `[To be recorded]` |
| Data custodian | `[To be recorded]` |
| Independent reviewer | `[To be assigned]` |
| Date assignments approved | `[To be recorded]` |

Do not prefill these fields with an inferred name, email address, or title.

## 2. Decision rights

| Decision | Prepares | Approves | Must be recorded in |
|---|---|---|---|
| Submit a data request | Project owner | Project owner; adviser notified | `data_access_log.csv` |
| Change a recipient, request scope, or requested field | Project owner | Adviser if the scope or ethics change | `request_matrix.csv`, workplan decision log |
| Accept a delivered file into the project | Data custodian | Project owner; adviser if restricted | Source register, hash record, `data_access_log.csv` |
| Reject or quarantine a file | Data custodian | Project owner | Access log and source notes |
| Record a permission or restriction | Project owner | Data custodian; adviser if publication is affected | `permissions_and_ethics.md`, access log |
| Accept or reject a fish-kill event label | Project owner | Adviser; independent reviewer when available | Event CSV, evidence audit, workplan decision log |
| Declare an event "independently verified" | Project owner | Adviser plus a second source or agency confirmation | Event CSV and evidence audit |
| Re-run the feasibility gate | Analyst | Project owner and adviser | Feasibility report, workplan |
| Train a model | Analyst | Project owner and adviser only after every gate item passes | Model card, training status, workplan |
| Publish a report, dashboard, or dataset | Project owner | Adviser; agency if its terms require review | Publication checklist, workplan update log |
| Delete or retain restricted data | Data custodian | Adviser and the agency terms | Retention note, access log |

## 3. Non-negotiable rules

1. **No model without the gate.** A failed gate item is a stop condition, not a prompt to weaken the gate.
2. **No invented evidence.** A request, draft, promise, or search result is not a delivered dataset.
3. **No silent label changes.** Event labels, station mappings, and variable definitions change only with a dated decision and a reason.
4. **No inferred geography.** A station is assigned to a lake zone only from an authoritative boundary or a source-approved crosswalk.
5. **No post-event leakage.** During-event and post-event measurements are context, not predictors.
6. **No public release of restricted data.** The most restrictive agency term controls.
7. **One record, one status.** The access log is the authoritative request status; the prose summary must match it.
8. **Disclose overlapping roles.** If the project owner also acts as data custodian or analyst, the adviser reviews data acceptance and publication.

## 4. Outstanding role actions

- [ ] Fill the individual names and institutional contact in the named assignment record.
- [ ] Confirm the faculty adviser and record the adviser's contact details.
- [ ] Assign the data custodian.
- [ ] Review `permissions_and_ethics.md` with the adviser.
- [x] Preserve the submitted LLDA request text in `submissions/LLDA_incident_request.md`.
- [ ] Prepare the signed professor/adviser approval letter for LLDA.
- [ ] Record the actual LLDA send date and channel; the current record says they were not supplied.
- [ ] Confirm who will sign the remaining request letters.
- [ ] Confirm who will review an incoming file before it enters the processed layer.

## 5. Change control

Changes to roles or decision rights are recorded in the workplan decision log. A temporary delegation must name the role, the scope, the start and end date, and the person accepting the delegation. Do not leave an approval implicit in an email thread.
