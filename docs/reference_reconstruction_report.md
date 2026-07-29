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
- a later link-management screenshot exposes four conceptual saved relations
  used only as positive evaluation evidence; and
- screenshot filenames and SHA-256 hashes are recorded without redistributing
  the images.

## SCHEMORA transformation

The five datasets and directly visible link-management keys yield 28 schema
fields. A single all-versus-all run would
mostly retrieve trivial same-ontology matches, so the adapter creates five
pairwise benchmarks:

1. each ontology becomes the Source once;
2. the other four ontologies form that run's Target;
3. all 28 fields are processed as Source across the five runs;
4. record values are not passed in the primary metadata-only configuration;
5. every mapping parquet has zero rows, keeping saved-link positives out of
   retrieval, prompts, and annotations;
6. the pinned official commit and the frozen three-file
   compatibility/telemetry patch are required; and
7. the five real rank artifacts are combined into
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

## Completed execution

All five pairwise benchmarks completed and produced 135 Top-5 prediction rows.

| Measured resource | Value |
|---|---:|
| Pairwise benchmarks | 5 |
| Unique schema fields | 28 |
| Chat calls | 346 |
| Embedding calls | 420 |
| Chat input tokens | 223,625 |
| Chat output tokens | 115,804 |
| Embedding input tokens | 8,824 |
| Total measured tokens | 348,253 |
| Measured stage elapsed time | 903.04 seconds |
| Estimated cost from measured tokens | USD 0.058650 |

The cost estimate uses standard per-million-token prices verified on
2026-07-28 from the
[official OpenAI pricing page](https://developers.openai.com/api/docs/pricing):
USD 0.05 input and USD 0.40 output for `gpt-5-nano`, and USD 0.13 input for
`text-embedding-3-large`. Actual billed usage and future prices may differ.

## Saved-link positive-only results

The saved-link page provides four conceptual positives. The bidirectional
friendly/enemy operation relation is also expanded into two directed rows,
giving five directional checks.

| Saved relation | SCHEMORA rank | Vector | BM25 | Top-1 | Top-3 | Top-5 |
|---|---:|---:|---:|:---:|:---:|:---:|
| `applies_rule → rule_id` | 1 | 0.59071583 | — | yes | yes | yes |
| `issued_to_unit → friendly unit_id` | 1 | 0.77413464 | 1.59374774 | yes | yes | yes |
| `target_terrain → terrain_id` | 2 | 0.62158549 | 1.13787580 | no | yes | yes |
| `friendly operation → enemy operation` | 5 | 0.67160642 | 2.08626938 | no | no | yes |
| `enemy operation → friendly operation` | not returned | — | — | no | no | no |

For `target_terrain`, SCHEMORA returned `key_terrain` first,
`terrain_id` second, `terrain_type` third, `name` fourth, and `elevation`
fifth. Thus the earlier recommendation-page alternative `name` did not outrank
the saved `terrain_id` relation in this run.

Positive-only recovery is:

| K | Conceptual any-direction | Conceptual all-directions | Directed |
|---:|---:|---:|---:|
| 1 | 2/4 (0.50) | 2/4 (0.50) | 2/5 (0.40) |
| 3 | 3/4 (0.75) | 3/4 (0.75) | 3/5 (0.60) |
| 5 | 4/4 (1.00) | 3/4 (0.75) | 4/5 (0.80) |

These are recovery figures, not full accuracy. Unobserved pairs are not
negative labels, so precision and F1 remain withheld.

## Other comparison definitions

- `visible-reference recovery@K`: visible reference pairs found within
  SCHEMORA Top-K for the same Source field;
- `Jaccard@K`: intersection over union between the nine visible pairs and
  SCHEMORA Top-K candidates restricted to those visible Source fields;
- within-Source rank correlation: computed only where at least two common
  candidates exist;
- complete-gold Recall@1/3/5, Precision@K, and pair F1@K: released only after all
  28 Source
  fields have complete, independently reviewed gold including no-match; and
- UI feature parity: reported separately from candidate similarity.

Original-demo scores such as 95 and 47 are never numerically compared with
SCHEMORA vector or BM25 scores.

## UI display semantics

The two UI surfaces use intentionally different display rules:

- Reference scores and confidence labels are copied from the observable
  screenshot. The visible bands are High `>=90`, Medium `70–89`, and Low
  `<70`; the original formula and calibration remain unknown.
- The SCHEMORA large-number display is the equal-weight RRF (`k=60`) review
  priority normalized by its theoretical three-signal maximum. Candidate order
  follows this derived priority.
- The SCHEMORA badge reports whether 3/3, 2/3, or 1/3 of the LLM, vector, and
  BM25 rank lists contributed. It is not a correctness vote.
- SCHEMORA rows show `링크명 미지정`; field names are not used to invent a
  linked term or `relatedTo`/`symmetric` type.

No UI score or signal badge is reported as a calibrated probability. The complete
Korean explanation is in `docs/ui_score_guide_ko.md`.
