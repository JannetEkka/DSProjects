## 5. Failures found and improvements made (development log)

Exact-match counts are on the 32 public sample cases; every change was also checked against the
full 518-case run through the contract validator (`code/audit/validate.py`).

| # | Failure observed | Root cause | Fix | Exact cases |
|---|---|---|---|---|
| 0 | First end-to-end run | - | Evidence normalizer + identity + latest-state + policy planner | 3/32 |
| 1 | Accounts and anonymized analytics never found for "already deleted" subjects | A scrubbed record (404 profile, all-null analytics row) carries no identifier, so evidence alone cannot tie it to anyone | **Workflow attribution**: the request's own deletion job is the `deletion_worker` account activity shortly before `reported_at` whose result mirrors the reported claim (COMPLETE->SUCCESS, PARTIALLY_COMPLETE->PARTIAL, NOT_STARTED->FAILED); only resources no evidence attributes to someone else are eligible | 16/32 |
| 2 | Same subject, two requests months apart: March evidence leaked into the September audit | Evidence was not partitioned per request | **Request eras**: evidence older than the subject's previous request's `audit_at` belongs to that request | 19/32 |
| 3 | Several requests share one `reported_at`; jobs were double-assigned | Greedy per-case choice | **Global one-to-one assignment** of workflow jobs (forced choices first, then earliest job per case id) | 20/32 |
| 4 | Support attachment in a PDF ignored | Artifacts were "mentions only" with no state | Artifact semantics: a record shown in a business artifact existed at capture time; category from artifact type | 20/32 |
| 5 | Connector screenshot listing several customers linked every connector to every customer | Whole-image context | **Row-level context** for multi-row screens; OCR-tolerant id regex (`1data_flow_9846`) | 21/32 |
| 6 | Catalog said `marketing_001` belonged to the subject; the screenshot showed a different person | Catalog link is a claim | **Artifact verification** of catalog links: rejected when the artifact shows someone else's contact details and none of the subject's | 21/32 (+ test-set decoy) |
| 7 | Validator: 29 rows with missing citations | Syslog dialect parsed with shifted fields, so every line shared one trace and a subject absorbed strangers' records; log exports are captured after their lines | Fixed RFC5424 field order; cite the observation's own timestamp when the export file post-dates `audit_at` | validator clean |
| 8 | Metamorphic test "upper-case duplicate submission" failed | Two submissions of one workflow competed for its job | Duplicate submissions share their workflow | 8/8 suite |
| 9 | Full run took 27 s | Linear scan of all observations per subject | Inverted identifier index + memoised linking (byte-identical output) | 9 s |

### Known limitations (left deliberately)

* **Anonymized analytics rows with no identifier** (cases 03, 04, 21, 25-28): the only link is a
  `deletion_worker` ANONYMIZE activity, and several requests' workflow windows overlap. We attribute
  such a row only when exactly one request's window contains it. Guessing would trade recall for
  wrong steps in other cases.
* `audit_record_6645` (case_18) and `audit_record_5569` (case_20) appear in no participant-visible file,
  so they cannot be derived.
* case_23: three NOT_STARTED requests share the same `reported_at` and three FAILED account jobs with
  no other distinguishing evidence; the one-to-one assignment is a principled guess.
