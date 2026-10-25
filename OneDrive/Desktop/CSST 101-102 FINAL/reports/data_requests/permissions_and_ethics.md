# Permissions, ethics, and data-use record

**Status:** Framework prepared. One LLDA incident-records request has been acknowledged; LLDA requested professor approval letters. **No external data-sharing permission, licence, or formal approval has been recorded as of 2026-10-23.** No requested data have been received.

This file is the written control for task A6. It records what must be agreed before external files enter the project. It does **not** substitute for an agency's data-sharing agreement, terms of use, ethics approval, or institutional sign-off.

## 1. Scope

The project requests environmental, station, incident, and reporting-completeness data from LLDA, PAGASA, BFAR, and the Biñan and Pila local governments. The intended use is a student research feasibility assessment of whether environmental data can support a future fish-kill early-warning system. No model is trained, no warning is issued, and no data are redistributed while the model-readiness gate remains blocked.

## 2. Permission record

Complete one row per request when an agency responds. Leave fields blank until a written permission, terms document, or refusal is actually on file. Do not record "granted" from a verbal statement alone.

| Request ID | Data owner | Permission or terms | Reference | Effective date | Restrictions | Publication allowed? | Status |
|---|---|---|---|---|---|---|---|
| `LLDA-WQ-01` | LLDA | Not recorded | | | | | Not requested |
| `LLDA-ST-01` | LLDA | Not recorded | | | | | Not requested |
| `LLDA-QA-01` | LLDA | Not recorded | | | | | Not requested |
| `LLDA-INC-01` | LLDA | Not recorded | | | | | Pending — approval letters requested |
| `LLDA-COMP-01` | LLDA | Not recorded | | | | | Not requested |
| `LLDA-ZONE-01` | LLDA | Not recorded | | | | | Not requested |
| `PAGASA-WX-01` | PAGASA | Not recorded | | | | | Not requested |
| `BFAR-INC-01` | BFAR | Not recorded | | | | | Not requested |
| `LGU-INC-01` | Biñan / Pila LGU | Not recorded | | | | | Not requested |

**Definition of recorded:** a signed agreement, a written email approval, a published terms-of-use acceptance receipt, or a written refusal is stored with the source record and referenced above. The corresponding entry in `data_access_log.csv` must use the same reference.

LLDA's request for professor approval letters is a processing requirement. It is **not** a permission to use or publish data, and it does not mean LLDA holds the requested records. The row stays pending until LLDA releases files or states its terms.

## 3. Data-use commitments

These are project commitments, subject to any stricter agency terms:

- Use the data only for this research project and the stated feasibility assessment.
- Keep the original delivered file unchanged; store a byte-identical archival copy and record its SHA-256 hash.
- Keep raw and restricted files out of public repositories and out of third-party services that do not have an approved data-handling basis.
- Limit access to the project owner, faculty adviser, and named reviewers who need the data for this project.
- Publish findings only at the level the agency permits: aggregate results, methods, and source citations unless written permission allows more.
- Attribute the agency and source in every table, figure, and report that uses the data.
- Do not sell, license, or redistribute the data.
- Do not use during-event or post-event measurements as predictors.
- Do not treat a missing report as a confirmed negative unless reporting completeness is documented.
- Report errors or inconsistencies back to the data owner before publishing a correction.
- Follow the agency's requested citation, retention, and review conditions.

## 4. Privacy and minimization

The requested environmental and incident data are not intended to identify private individuals. However, incident reports and correspondence may contain names, signatures, phone numbers, addresses, or other personal information.

- Request only the fields needed for the research.
- Ask the agency to redact personal information that is not necessary.
- Do not copy personal information into the dashboard, public report, or Git history.
- If an interview or human-participant activity is added later, prepare a separate consent form and obtain the required institutional ethics review before collecting it.
- Do not publish barangay-level blame, individual operator identities, or unverified loss claims.

## 5. Security and retention

- Keep raw files in a restricted project folder with access limited to named roles.
- Record file hashes and receipt dates in the source register.
- Keep the access log current; do not rely on memory or email search.
- Retain data only as long as needed for the research, the agency terms, and the institution's records policy; record the chosen retention point.
- Before deleting a restricted file, confirm that the agency terms and the institutional record-retention rule allow deletion.
- If a device or account is lost, record the incident and notify the adviser and data owner as required.

## 6. Publication review

Before submitting a paper, poster, dashboard release, or public repository update:

- [ ] Confirm every dataset's permission and publication condition.
- [ ] Confirm that no restricted raw file is included.
- [ ] Confirm that no personal information is included.
- [ ] Check that aggregate incident statements were not expanded into events.
- [ ] Check that missing values remain blank, not zero.
- [ ] Check that no model metric or risk level is shown without a passed gate.
- [ ] Record the adviser's approval.
- [ ] Send the agency any review copy or acknowledgement required by its terms.

## 7. Outstanding approvals and documents

- [ ] Project owner full names and institutional contact completed in `roles_and_decisions.md`.
- [ ] Faculty adviser confirmed and recorded in `roles_and_decisions.md`.
- [ ] Signed professor/adviser approval letter prepared on university letterhead for LLDA.
- [ ] Data custodian assigned.
- [ ] Remaining request letters reviewed by the adviser.
- [ ] PAGASA supporting documents assembled, if that request is submitted.
- [ ] Official recipient and channel confirmed for the remaining requests.
- [x] LLDA incident request entered in `data_access_log.csv` as `acknowledged`, with the submitted text preserved.
- [ ] LLDA approval documents sent; send date, channel, and recipient recorded.
- [ ] No data file accepted until its source, hash, terms, fields, units, and QA flags are documented.

## 8. Sign-off record

| Role | Name | Signature | Date | Scope approved |
|---|---|---|---|---|
| Project owner | | | | |
| Faculty adviser | | | | |
| Data custodian | | | | |

Leave blank until the named person signs. Do not prefill a name or date.

## 9. Change control

Any change to this file that weakens a permission, privacy, retention, or publication control must be recorded in the workplan's decision log with the reason and the approving role. The most restrictive applicable agency term controls.
