# Public Defense Data Case Study — Fixed Execution Plan

Date fixed: 2026-07-28

## 1. Scope guardrails

- Matchmaker remains fixed as `matchmaker_synthea_gpt5_nano_v1`, `full1`,
  `n=1`, described as `paper-guided reconstruction, not exact reproduction`.
- Matchmaker `full2` is interrupted without a final artifact; `full3` is not
  run. No additional Matchmaker, G.E.R., or model/API call is authorized by
  this plan.
- The new case study is limited to public, non-sensitive contract-award
  metadata. It excludes raw operational records, unit locations, military
  facilities, personnel data, media, and current mission information.
- The result must be described as a case study on the selected public defense
  dataset and fixed target schema, not validation over the defense domain.

## 2. Candidate comparison

| Candidate | License/reuse | Metadata | Case-study value | Gold feasibility | Sensitivity | Decision |
|---|---|---|---|---|---|---|
| USAspending DoD contract-award metadata | USAspending repository and data dictionary: CC0 1.0 | Official 457-row crosswalk with field definitions, source files, and domain values | Acronyms, codes, nested organization/location/value concepts, DoD-only fields and no-match cases | Strong: maps to a versioned procurement standard | Low when only schema metadata and non-record domain examples are retained | **Selected** |
| DVIDS media metadata | Many U.S. Government works are public domain, but item-level copyright, publicity, privacy, trademark, and endorsement conditions vary | API metadata exists | Rich media context and abbreviations | Moderate | Higher: unit, location, personnel, and current-event metadata can appear | Rejected |
| DoD budget justification books | U.S. Government publications are generally reusable | Official publications, but heterogeneous PDF/table structures and no single stable field dictionary for the proposed subset | Defense-specific financial context | Moderate to weak without substantial manual extraction | Low to moderate | Rejected |

Primary evidence:

- USAspending public dataset catalog:
  <https://catalog.data.gov/dataset/usaspending-gov-federal-award-subaward-and-account-data>
- USAspending data dictionary API:
  <https://api.usaspending.gov/api/v2/references/data_dictionary/>
- USAspending CC0 license:
  <https://github.com/fedspendingtransparency/usaspending-api/blob/master/LICENSE>
- USAspending data sources and dictionary description:
  <https://www.usaspending.gov/data/data-sources-download.pdf>
- DVIDS limitations:
  <https://www.dvidshub.net/about/copyright>
- DoD budget materials:
  <https://comptroller.defense.gov/Budget-Materials/>

## 3. Selected source

The source schema is a deliberately bounded subset of
`Contracts_PrimeAwardSummaries.csv` fields from USAspending, logically divided
into five source tables:

1. `ContractAward`
2. `AwardingOrganization`
3. `RecipientOrganization`
4. `PlaceOfPerformance`
5. `ProcurementClassification`

Fixed size: **55 source properties**. All field names and descriptions come
from the official USAspending data dictionary. Official domain values are used
as sample values where available. When the official dictionary does not state
a data type, `ColumnType` remains empty and its status is `missing`; it is not
silently inferred.

No raw recipient records, street addresses, contact details, vendor names, or
award descriptions are checked in. The defense scope is established by the
Department of Defense agency filter and DoD-specific procurement fields, while
the reproducible evaluation artifact remains schema metadata.

## 4. Fixed target schema

Target: **OCDS 1.1.5 release schema**, canonical JSON Schema:

<https://standard.open-contracting.org/schema/1__1__5/release-schema.json>

The target is fixed before gold annotation. It is a public procurement
standard rather than a defense-specific model. NIEM Military Operations was
reviewed as a higher-priority defense ontology, but rejected for this source
because it does not provide the procurement lifecycle semantics needed for
objective contract-award gold mappings.

The fixed subset contains **10 object types and 108 properties**:
`Release`, `Tender`, `Award`, `Contract`, `Organization`, `Address`, `Item`,
`Classification`, `Value`, and `Period`. Nested properties are represented as
paths, for example `Award.value.amount`. Names, definitions, and types are
derived without LLM enrichment from the canonical schema. The generated CSV
and its SHA-256 are fixed before gold annotation.

OCDS source:
<https://standard.open-contracting.org/latest/en/schema/release/>

OCDS license:
<https://github.com/open-contracting/standard/blob/1.1-dev/LICENSE>

## 5. Gold construction and review

- Complete gold is created for every selected source property.
- Required fields: source, target, mapping type, rationale, primary evidence,
  evidence location, annotation status, and review status.
- Mapping types are `1:1`, `1:n`, `no-match`, and `ambiguous`.
- At least five DoD/FPDS-specific fields without an OCDS 1.1.5 core equivalent
  are retained as verified no-match cases.
- The draft is produced only from official USAspending and OCDS definitions.
  A second deterministic validation checks target existence, source coverage,
  duplicate pairs, allowed mapping types, and evidence presence.
- Because only one human annotator is presently available, the repository will
  distinguish `draft_complete` from `independently_reviewed`. It will not claim
  independent subject-matter review unless that actually occurs.
- Final source, target, and gold SHA-256 values are recorded in the manifest.

## 6. SCHEMORA dry-run estimate

Reused implementation:

- Official repository: <https://github.com/schemorapaper/schemora>
- Pinned upstream commit:
  `1339fedf8113fc3746d5664f1453248e47ee310c`
- Reporting label: `official-code adaptation`
- LLM: `gpt-5-nano`
- Embedding: `text-embedding-3-large`
- Retrieval candidates per method: 3
- Vector threshold: 0.50
- BM25 threshold: 1.0
- Enrichment, hybrid retrieval, table selection, and column ranking: enabled
- Workers: embedding 1, LLM 2
- Temperature: unsupported by `gpt-5-nano`; malformed-output retries repeat
  without the upstream temperature escalation
- Planned executions: 1

For 55 source and 108 target properties:

| Estimate | Value |
|---|---:|
| Source queries | 55 |
| Base enrichment calls | `2 × (55 + 108) = 326` |
| Table-selection/ranking calls | up to 110 before retries |
| Estimated LLM calls | **436 base; 458 conservative** |
| Estimated embedding calls | **approximately 514** |
| Estimated input tokens | **approximately 0.66M** |
| Estimated output tokens | **approximately 0.16M** |
| Estimated elapsed time | **approximately 26 minutes** |
| Estimated API cost | **approximately USD 0.10** |

Reference ceiling (`Synthea SCHEMORA full1`): 992 LLM calls, 1,428,541
measured tokens, 2,741.17 seconds, USD 0.1944.

The conservative estimate is below the Synthea ceiling in calls, tokens, time,
and cost. A dry-run script must recompute counts and hashes from the final CSVs
before any model call. The live run must stop before sending requests if:

- source properties exceed 80 or target properties exceed 150;
- projected LLM calls exceed 992;
- projected tokens exceed 1,428,541;
- projected cost exceeds USD 0.1944;
- projected elapsed time exceeds 2,741.17 seconds;
- required hashes, license records, or sensitivity checks are missing;
- an unexpected raw-record or secret-bearing file enters the run directory.

## 7. Evaluation

The complete-gold evaluator reports HitRate, macro recall, any-hit, micro pair
recall, precision, pair F1 at K=1/3/5, nDCG@5, MAP@5, no-match false
recommendations, no-match detection, and breakdowns by difficulty and mapping
type. Error analysis uses the requested fixed taxonomy.

SCHEMORA does not directly emit a no-match decision. A query with no returned
candidate after the upstream retrieval thresholds is treated as no-match; any
candidate returned for a gold no-match source counts as a false recommendation.
This rule is fixed before the run.

## 8. UI plan

Name: **Human-in-the-loop Ontology Property Mapping Review Interface**

Stack:

- Python standard-library HTTP server and SQLite persistence
- Static HTML, CSS, and browser JavaScript
- CSV-backed import of the real `outputs/predictions.csv`
- JSON API for search, status filters, approve/ignore, bulk approval, raw
  evidence, reload, and summary counts

The UI labels model output as rank and `High / Medium / Low`, never as a
calibrated probability. The deterministic grade rule is documented in code and
UI documentation. Ontology application is a separate mock interface.

## 9. Repository/publication scope

Included:

- public source/target metadata and license records;
- processed source schema, fixed target schema, complete gold and hashes;
- adapter, dry-run, evaluation, error, and cost code;
- one SCHEMORA run's Top-K predictions, usage summary, metrics, errors, and
  manifest;
- UI source, tests, screenshots, and methodology/limitations documentation.

Excluded:

- Matchmaker/G.E.R. code, traces, caches, and partial runs;
- SCHEMORA upstream source and runtime caches;
- API keys, endpoints containing credentials, `.env`, local absolute paths;
- raw DoD award rows, recipient contact/address data, operational/unit/facility
  locations, and internal product assets.

The repository will initially be private. A later public release requires a
fresh secret scan, path scan, license audit, and sensitivity review.
