# Observable reference versus SCHEMORA implementation

## Correction

The earlier implementation created 16 local heuristic candidates and evaluated
six relations against that same constructed list. Those values were only an
internal consistency check. They were not SCHEMORA performance, original-demo
performance, or a valid reproduction metric. The heuristic prediction file and
its metric file have been removed from the active case.

## Frozen evidence

- five screenshots contain 18 explicitly synthetic rows across operation
  orders, friendly units, enemy units, rules, and terrain;
- one recommendation screenshot reports 16 total candidates;
- only nine candidate rows are fully visible and are recorded;
- visible scores, order, link names, confidence labels, and truncated
  explanation fragments are preserved without completing hidden text; and
- screenshot filenames and SHA-256 hashes are recorded without redistributing
  the images.

## SCHEMORA transformation

The five datasets yield 27 schema fields. A single all-versus-all run would
mostly retrieve trivial same-ontology matches, so the adapter creates five
pairwise benchmarks:

1. each ontology becomes the Source once;
2. the other four ontologies form that run's Target;
3. all 27 fields are processed as Source across the five runs;
4. record values are not passed in the primary metadata-only configuration;
5. the same official commit and the same three-file compatibility/telemetry
   patch as the frozen English case are required; and
6. the five real rank artifacts are combined into
   `outputs/reference_demo/predictions.csv`.

SCHEMORA ranks schema correspondences. The reference page appears to recommend
named ontology relations. Candidate-pair overlap can therefore be compared,
but relation-name generation parity cannot be claimed.

The executable boundary is fixed as follows:

- official commit:
  `1339fedf8113fc3746d5664f1453248e47ee310c`;
- locally adapted files: `utils/llm.py`, `utils/embedding.py`, and
  `schema_matching/column_rank.py`; and
- combined adapter patch SHA-256:
  `491efc93e9672ed13387ccba6feedbfa6014886a4239de6dccfa38cdd663f7d0`.

The adapter and runner both reject a different commit or patch. This is an
official-code adaptation, not an assertion that the upstream repository runs
unmodified.

## Current execution status

The dry-run passed without network or model calls:

| Estimate | Value |
|---|---:|
| Pairwise benchmarks | 5 |
| Unique schema fields | 27 |
| Estimated LLM calls | 344 |
| Estimated total tokens | 613,183 |
| Estimated elapsed time | 1,188.21 seconds |
| Estimated API cost | USD 0.073933 |

No API key is present, so SCHEMORA was not executed and no SCHEMORA accuracy or
candidate-overlap result is reported.

The cost estimate uses standard per-million-token prices verified on
2026-07-28 from the
[official OpenAI pricing page](https://developers.openai.com/api/docs/pricing):
USD 0.05 input and USD 0.40 output for `gpt-5-nano`, and USD 0.13 input for
`text-embedding-3-large`. Actual billed usage and future prices may differ.

## Comparison definitions

After real output exists:

- `visible-reference recovery@K`: visible reference pairs found within
  SCHEMORA Top-K for the same Source field;
- `Jaccard@K`: intersection over union between the nine visible pairs and
  SCHEMORA Top-K candidates restricted to those visible Source fields;
- within-Source rank correlation: computed only where at least two common
  candidates exist;
- Recall@1/3/5, Precision@K, and pair F1@K: released only after all 27 Source
  fields have complete, independently reviewed gold including no-match; and
- UI feature parity: reported separately from candidate similarity.

Original-demo scores such as 95 and 47 are never numerically compared with
SCHEMORA vector or BM25 scores.
