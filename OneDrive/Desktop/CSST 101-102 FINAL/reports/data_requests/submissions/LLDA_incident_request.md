# LLDA incident-records request — submission record

**Recorded:** 2026-10-23  
**Request ID:** `LLDA-INC-01` (primary; the email also asks for associated water-quality measurements)  
**Agency:** Laguna Lake Development Authority (LLDA)  
**Status:** `acknowledged` — LLDA requested approval letters from the professor  
**Data received:** None  
**Permission recorded:** None  
**Sent date:** Not recorded  
**Recipient address / channel:** Not recorded  
**Response date:** Not recorded  

## Project-owner report

On 2026-10-23 the project owner reported that this request had been sent to LLDA and that LLDA was asking for approval letters from the project owner's professor. The project owner expects to comply next week. The exact submission date, recipient address, channel, and agency wording are not yet on file.

This record does **not** claim that LLDA holds the requested data, has granted permission, or has released any file. It also does not mean the six-item LLDA letter in [`../letters/LLDA_request.md`](../letters/LLDA_request.md) was sent. The request below is the text supplied by the project owner.

## Request text supplied by the project owner

> **Subject:** Request for Historical Fish Kill Incident Records in Laguna de Bay for Academic Research
>
> Good day,
>
> We are BSCS students conducting an academic research project titled “Development of HIMPIL: A Machine Learning-Based Early Warning and Advisory System for Fish Kill Events in Laguna de Bay.”
>
> We respectfully request access to available historical fish kill incident records in Laguna de Bay for academic and machine-learning research purposes.
>
> If available, we would like to obtain records containing the following information:
>
> - Date or approximate date of each reported fish kill incident.
> - Location, municipality, lake zone, or monitoring station affected.
> - Fish species affected.
> - Estimated number, weight, or economic value of fish losses.
> - Reported or investigated causes of each incident.
> - Associated water quality measurements, especially dissolved oxygen, water temperature, pH, and other available parameters.
> - Any available historical incident database, monitoring report, or tabulated records.
>
> We would prefer records in CSV, Excel, or another machine-readable format. If a complete dataset is unavailable, we would appreciate access to the available reports or records covering the earliest to the most recent documented incidents.
>
> The data will be used solely for academic research to investigate whether historical environmental conditions can help identify potential fish kill risks. We will properly acknowledge the data sources in our research.
>
> Thank you for your time and assistance. We look forward to your response.
>
> Respectfully,
>
> HIMPIL Research Group  
> BSCS Students  
> Laguna State Polytechnic University

## What this establishes

- One LLDA request exists and has received a response.
- LLDA's response is a document requirement, not a data release or a permission.
- The request covers incident records and associated water-quality measurements. It does not cover the separate LLDA requests for daily water-quality time series, station coordinates, aggregation rules, reporting completeness, or the zone crosswalk.
- Eight other requests remain `planned`.

## Coverage against the project's data needs

This request is the right first move because event-level incident records are the main blocker. It is not the whole data package.

| Project need | Covered by this email? | Gap |
|---|---|---|
| Fish-kill event labels | Partial | Date or approximate date, location, species, losses, and cause are requested. Exact time, date precision, station ID, and coordinates are not. |
| Associated water-quality measurements | Partial | Useful for event context. Measurements taken during or after an event cannot be used as pre-event predictors. |
| Routine dated water-quality time series | No | Covered by the separate `LLDA-WQ-01` request; needs daily or finest available observations, not only incident-linked samples. |
| Station coordinates and metadata | No | Covered by `LLDA-ST-01`; the email mentions a monitoring station but does not request coordinates or station identifiers. |
| Authoritative lake-zone crosswalk | No | Covered by `LLDA-ZONE-01`; zone names cannot be inferred from station names. |
| Reporting-completeness / negative windows | No | Covered by `LLDA-COMP-01`; an absence of reports is not a confirmed non-event. |
| Daily weather | No | Covered by `PAGASA-WX-01`. |
| Independent confirmation from BFAR/LGUs | No | Covered by `BFAR-INC-01` and `LGU-INC-01`. |
| Data dictionary, units, QA flags, missing codes | No | Should be requested explicitly in the follow-up or attached specification. |

The request should therefore be treated as **one critical component**, not as sufficient data for the original 24/48/72-hour prediction system.

## Next action

1. Prepare the adviser approval letter using [`../letters/adviser_approval_template.md`](../letters/adviser_approval_template.md). Print it on university letterhead and have the professor sign it.
2. Confirm with LLDA whether it needs one approval letter or additional endorsement from the department chair, dean, or research office.
3. Send the signed approval through the same LLDA thread or the channel LLDA specifies.
4. Record the actual send date, recipient, channel, and any reference number in [`../data_access_log.csv`](../data_access_log.csv).
5. Keep `LLDA-INC-01` at `acknowledged` until LLDA releases files. Do not change it to `received` based on the approval letter alone.
6. When files arrive, inspect them, record their hashes and terms, and then update the permissions record.

## Related records

- Access log: [`../data_access_log.csv`](../data_access_log.csv)
- Permission record: [`../permissions_and_ethics.md`](../permissions_and_ethics.md)
- Adviser approval template: [`../letters/adviser_approval_template.md`](../letters/adviser_approval_template.md)
