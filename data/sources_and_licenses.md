# Sources, licenses, and sensitivity review

## USAspending source metadata

- Publisher: U.S. Department of the Treasury, Bureau of the Fiscal Service
- Resource: USAspending data dictionary API
- URL: <https://api.usaspending.gov/api/v2/references/data_dictionary/>
- Accessed: 2026-07-28
- License: CC0 1.0 Universal, as stated by the USAspending API repository
- License URL:
  <https://github.com/fedspendingtransparency/usaspending-api/blob/master/LICENSE>
- Raw file: `data/public/usaspending_data_dictionary.json`
- SHA-256:
  `3d0f2e3a952297050db5c2a4addf40765460a49d499427da1b57ef3c7edea3c3`

The file is an official crosswalk/data dictionary. It contains field
definitions and domain values, not award rows.

## OCDS target metadata

- Publisher: Open Contracting Partnership
- Resource: OCDS 1.1.5 canonical release JSON Schema
- URL:
  <https://standard.open-contracting.org/schema/1__1__5/release-schema.json>
- Accessed: 2026-07-28
- License: Apache License 2.0
- License URL:
  <https://github.com/open-contracting/standard/blob/1.1-dev/LICENSE>
- Raw file: `data/public/ocds_release_schema_1_1_5.json`
- SHA-256:
  `bf701ac26180756de4c4ada8a94a86a24174f3025345a8b99fda9927de896f80`

## Sensitivity determination

The checked-in source data consists only of schema metadata and non-record
domain examples. It contains no raw award row, vendor name, contact detail,
street address, personnel record, facility coordinate, unit location, current
operation, or classified/CUI material.

Some source *field definitions* mention military operations because those
definitions explain procurement codes. No transaction value for such a field
is included.

Result: suitable for a private GitHub case-study repository. A transition to
public visibility still requires the final audit in `docs/limitations.md`.

