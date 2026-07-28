# Five-dataset to SCHEMORA transformation

## Evidence boundary

`datasets.json` contains only headers and cells fully visible in the five
dataset screenshots. `source_images_manifest.json` records the corresponding
filenames and SHA-256 hashes. No operational record or hidden screenshot value
is introduced.

The data-preview screenshots expose Korean display headers, while the link page
exposes some English machine keys. `ontology_schema.csv` distinguishes:

- `observed_in_link_page`: the English key is directly visible;
- `normalized_from_observed_korean_header`: the English key was created for the
  adapter and is not claimed to come from the original system; and
- `inferred_from_observed_values`: the data type is inferred from the visible
  three or six sample rows.

## Input contract

SCHEMORA's official pipeline consumes table and column metadata rather than
record tables. The primary run therefore uses:

| SCHEMORA field | Case source |
|---|---|
| `TableName` | normalized ontology name |
| `TableDesc` | Korean dataset-level description |
| `ColumnName` | visible or normalized machine key |
| `ColumnDesc` | Korean semantic description |
| `ColumnType` | type inferred from visible values |

Cardinality is frozen in `ontology_schema.csv` but is not passed because the
fixed official input schema has no cardinality field.

Visible record values are retained for provenance, UI preview, and later gold
annotation. They are **not passed** to the primary SCHEMORA run. Appending
sample values to descriptions would be a separate adaptation and is outside
this fixed comparison.

## Pairwise strategy

The same five ontologies cannot be placed unchanged on both sides of one run:
trivial same-table/same-field candidates would dominate retrieval. The adapter
therefore prepares five benchmarks. Each ontology is Source once and the other
four ontologies are its Target. This processes all 27 Source fields while
excluding same-ontology candidates without modifying retrieval code.

| Source ontology | Source fields | Target fields |
|---|---:|---:|
| 작전명령 | 7 | 20 |
| 아군 부대 | 4 | 23 |
| 적군 부대 | 4 | 23 |
| 교전규칙 | 6 | 21 |
| 지형 정보 | 6 | 21 |

## Fixed implementation

- repository: `https://github.com/schemorapaper/schemora`
- commit: `1339fedf8113fc3746d5664f1453248e47ee310c`
- adapted files: `utils/llm.py`, `utils/embedding.py`,
  `schema_matching/column_rank.py`
- adapter patch SHA-256:
  `491efc93e9672ed13387ccba6feedbfa6014886a4239de6dccfa38cdd663f7d0`
- LLM: `gpt-5-nano`
- embedding: `text-embedding-3-large`
- candidate count per retrieval method: `3`
- query enrichment: enabled
- document enrichment: enabled
- non-similarity prompt: enabled
- embedding and BM25 retrieval: enabled
- table selection: enabled
- LLM workers: `2`
- embedding workers: `1`

The adapter and runner reject any different commit or patch. The patch is the
same compatibility and telemetry layer used for the frozen English case; this
is therefore an official-code adaptation rather than an unmodified-upstream
execution.

## Exact preparation and run sequence

Use the same local pinned checkout and its Python environment previously used
for the English case:

```bash
python3 experiments/estimate_reference_demo.py

<SCHEMORA_PYTHON> adapters/reference_demo_adapter.py \
  --upstream-root <PINNED_SCHEMORA_ROOT>

python3 experiments/run_reference_demo.py \
  --upstream-root <PINNED_SCHEMORA_ROOT> \
  --python <SCHEMORA_PYTHON>
```

The runner stops before any model call unless the dry-run gate passed and
`API_KEY` exists in the process environment or the pinned checkout's ignored
`.env`. The key must never be stored in this repository or passed in the
command line.

After the five runs, supply the five actual `column_rank` parquet artifacts:

```bash
<SCHEMORA_PYTHON> experiments/convert_reference_predictions.py \
  --artifact <OPERATION_ORDER_RANK_PARQUET> \
  --artifact <FRIENDLY_UNIT_RANK_PARQUET> \
  --artifact <ENEMY_UNIT_RANK_PARQUET> \
  --artifact <RULES_RANK_PARQUET> \
  --artifact <TERRAIN_RANK_PARQUET>

python3 experiments/compare_reference_schemora.py
```

Only the converter creates `outputs/reference_demo/predictions.csv`, which the
UI recognizes as real SCHEMORA output.
