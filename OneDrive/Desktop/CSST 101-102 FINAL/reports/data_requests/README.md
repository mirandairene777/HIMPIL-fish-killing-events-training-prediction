# HIMPIL data request package

**Prepared:** 2026-10-23  
**Status:** One LLDA incident-records request has been submitted and acknowledged. LLDA requested professor approval letters. **No data have been received and no data-sharing permission has been recorded.** **Outreach paused by team decision on 2026-10-23 (D-009); the request remains `acknowledged` and is not closed.**

This package implements tasks A5–A8 of the living workplan: a field-level request set, ready-to-complete letters, a permissions and ethics record, decision rights, and a tracking log. It does **not** claim that any agency holds the requested data, that any data have been released, or that any permission has been granted. The single submitted request is preserved in [`submissions/LLDA_incident_request.md`](submissions/LLDA_incident_request.md).

## Current request

The LLDA incident-records request (`LLDA-INC-01`) was submitted using the project owner's email text. LLDA responded by asking for approval letters from the project owner's professor. A signed adviser letter can be prepared from [`letters/adviser_approval_template.md`](letters/adviser_approval_template.md). The exact send date, recipient address, channel, and response date are not yet recorded. **Outreach is paused (D-009); do not send the letter or change the status unless the team reopens the data-acquisition track.**

This does **not** mean the six-item LLDA letter was sent, that LLDA holds the requested data, or that any data have been released. Eight requests remain `planned`.

## What is requested

| ID | Recipient | Request | Priority |
|---|---|---|---|
| `LLDA-WQ-01` | LLDA | Dated lake and tributary water-quality observations, ideally daily or finer | Critical |
| `LLDA-ST-01` | LLDA | Station registry, coordinates, waterbody and zone fields | Critical |
| `LLDA-QA-01` | LLDA | Aggregation and QA/QC rules for the published annual tables | High |
| `LLDA-INC-01` | LLDA | Event-level fish-kill incident records, investigation details, and associated water-quality measurements | Critical |
| `LLDA-COMP-01` | LLDA | Reporting-completeness and negative-window records | Critical |
| `LLDA-ZONE-01` | LLDA | Authoritative lake-zone boundary and station crosswalk | Critical |
| `PAGASA-WX-01` | PAGASA | Daily rainfall, air-temperature, and wind observations with station metadata | High |
| `BFAR-INC-01` | BFAR | Fish-kill reports, investigations, laboratory results, and response records | Critical |
| `LGU-INC-01` | Biñan and Pila LGUs | Fish-kill reports, response records, and reporting completeness | High |

The full field list, period, resolution, format, and acceptance criteria are in [`request_matrix.csv`](request_matrix.csv). The matrix is the authoritative specification; the letters summarize it.

## Contents

| File | Purpose |
|---|---|
| [`request_matrix.csv`](request_matrix.csv) | One row per request with fields, period, format, acceptance criteria, and status |
| [`letters/LLDA_request.md`](letters/LLDA_request.md) | Draft letter for water quality, stations, QA rules, incidents, completeness, and zones |
| [`letters/PAGASA_request.md`](letters/PAGASA_request.md) | Draft letter for daily weather observations |
| [`letters/BFAR_request.md`](letters/BFAR_request.md) | Draft letter for incident and investigation records |
| [`letters/LGU_request.md`](letters/LGU_request.md) | Draft letter for Biñan and Pila LGU records |
| [`letters/adviser_approval_template.md`](letters/adviser_approval_template.md) | Draft professor/adviser approval letter requested by LLDA |
| [`submissions/LLDA_incident_request.md`](submissions/LLDA_incident_request.md) | Preserved request text, response note, and LLDA next action |
| [`data_access_log.csv`](data_access_log.csv) | Request-by-request tracking log; one acknowledged, eight planned, no files received |
| [`permissions_and_ethics.md`](permissions_and_ethics.md) | Permission record and data-handling commitments; no permission is recorded yet |
| [`roles_and_decisions.md`](roles_and_decisions.md) | Role structure, authorship policy, decision rights, and change-control rules |

## How to use this package

1. **Complete the bracketed fields.** Add the researcher name, institution, adviser, institutional email, phone, date, and recipient details. Do not guess a recipient or an address.
2. **Confirm the current channel.** Check the agency's official page before sending. Requirements and contact routes change.
3. **Have the letter reviewed and signed.** For PAGASA, the published student route also requires the CADS-02A form and supporting documents.
4. **Send one request per agency and record it.** Enter the date, recipient, channel, and any reference number in `data_access_log.csv`. Change the status from `planned` to `sent` only after the message or form has actually been submitted. The LLDA incident request is already `acknowledged`; do not mark the other eight requests as submitted because they share an agency.
5. **Record the response, not the hope.** A document request or promise of data is `acknowledged`; it becomes `received` only after files are in hand and inspected. A written refusal or a statement that no record exists is also a result and must be logged.
6. **Do not merge or model the data yet.** New files must first be hashed, inspected, described in the source register, checked against the requested fields, and accepted into a separate processed layer.

**Current LLDA action (paused):** no letter is being sent while D-009 is in force. If the team reopens outreach, prepare the professor/adviser letter from the template, have it signed on university letterhead, send it through the LLDA thread or channel, and record the actual date and channel. The approval letter is a processing document, not permission to use the data.

## Status definitions

| Status | Meaning |
|---|---|
| `planned` | Draft prepared; no submission recorded |
| `sent` | Submission actually made; date and channel recorded |
| `acknowledged` | Agency has responded and confirmed receipt or routing |
| `partial` | Some files received; gaps documented |
| `received` | Files received and inspected; source record, hash, terms, and restrictions logged |
| `declined` | Agency declined or could not release; reason recorded |
| `no_record` | Agency states that no responsive record exists for a defined period |
| `closed` | Request fully resolved, including a written no-record response |

## Official channels to verify before sending

These are starting points, not guarantees of the correct records office. Confirm the current route on the agency's official page.

| Recipient | Starting point | Notes |
|---|---|---|
| LLDA | <https://www.llda.gov.ph/> | The incident request has been acknowledged; LLDA requested professor approval letters. Confirm the receiving office and whether a second endorsement is required. |
| PAGASA | <https://www.pagasa.dost.gov.ph/climate/climate-data> | The page publishes a student/academic route (CADS-02A), the Terms and Conditions of Use, and a formal-letter requirement. |
| BFAR | <https://www.bfar.da.gov.ph/> | Confirm whether the request belongs with the central office, the Region IV-A office, or the relevant records unit. |
| Biñan | <https://www.binan.gov.ph/> | Use the official records/environment/agriculture channel. Confirm the current office and recipient. |
| Pila | <https://elgu-pila-laguna.e.gov.ph/> | Use the official records/environment/agriculture channel. Confirm the current office and recipient. |
| FOI portal, if required | <https://www.foi.gov.ph/> | Use only if the agency directs the request there; record the reference number in the access log. |

### Current PAGASA student requirements

As published on the PAGASA Climate Data page at the time this package was prepared, the student/academic research route uses the **Researcher Climatological Raw Data Request Form (CADS-02A)** and asks for:

- a school ID or registration form;
- a copy of the approved research/thesis proposal;
- the Terms and Conditions of Use for Climatological Data;
- a formal request letter addressed to the PAGASA Administrator, signed and noted by the research adviser or a committee member.

Check the page again before submission. Do not treat this summary as a substitute for the agency's current instructions.

## Receipt and acceptance rules

A dataset is not accepted merely because a file arrived. Record all of the following before moving it into `data/processed/`:

- source file name, received date, agency, and permission reference;
- SHA-256 hash and byte-identical archival copy;
- data dictionary or field explanation;
- units, time zone, date precision, station identifiers, and QA flags;
- missing-value codes and confirmation that blanks are not zeros;
- restrictions on redistribution, publication, or retention;
- whether the file is event-level, an aggregate, or a derived product.

Reject or hold a file when the station identity is ambiguous, the time field is undocumented, the units cannot be established, or the file cannot be linked to an authoritative source. Do not repair those gaps by guessing.

## Do not

- Do not invent a recipient, office, address, email, or phone number.
- Do not mark a request `sent` because a draft exists.
- Do not mark the other eight requests as submitted because the LLDA incident request was sent.
- Do not mark data `received` because an agency promised a file or asked for an approval letter.
- Do not treat the absence of a news report as a confirmed non-event.
- Do not expand an aggregate incident statement into individual events.
- Do not use during-event or post-event measurements as predictors.
- Do not upload restricted files to a public repository or third-party service.
- Do not train a model or publish a risk score until the Section 6 gate in `README_WORKPLAN.md` passes.

## Current state

- Requests in package: **9**
- Requests submitted: **1** (`LLDA-INC-01`)
- Requests acknowledged: **1**
- Requests still planned: **8**
- Outreach status: **paused by team decision (D-009, 2026-10-23)**
- Responses with data files: **0**
- Data-sharing permissions recorded: **0**
- New environmental files accepted: **0**

These counts are also visible in [`data_access_log.csv`](data_access_log.csv), where one row is `acknowledged` and eight remain `planned`. The acknowledged row still has blank send/response dates because the exact dates were not supplied; it must not be treated as a data delivery.
