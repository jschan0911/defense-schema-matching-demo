# Presentation summary

## Case-study question

Can the pinned SCHEMORA official-code adaptation retrieve valid OCDS property
matches for a fixed subset of public DoD contract-award metadata, and can a
reviewer approve or ignore the actual Top-K output?

## Fixed design

| Item | Value |
|---|---:|
| Source tables | 5 |
| Source properties | 55 |
| Target object types | 10 |
| Target properties | 108 |
| Gold no-match sources | 17 |
| Gold 1:n sources | 19 |
| SCHEMORA runs | 1 planned |

## Dry-run budget

| Item | Conservative estimate | Synthea ceiling |
|---|---:|---:|
| LLM calls | 458 | 992 |
| Total tokens | 816,384 | 1,428,541 |
| Elapsed time | 1,581.98 s | 2,741.17 s |
| API cost | $0.0983 | $0.1944 |

The gate passed without a model or embedding request.

## Reporting language

Use: “case-study result on selected public defense contract metadata and a
fixed OCDS target.”

Do not use: “validated across the defense domain.”

## UI

The interface reads `outputs/predictions.csv`, stores approval state in
SQLite, supports search/status/bulk review, and shows rule-based rank grades.
The current screenshot is explicitly a demo fixture until the single live
SCHEMORA run is completed.

