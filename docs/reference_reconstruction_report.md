# Reference reconstruction report

## What was reconstructed

- five screenshot-visible, explicitly synthetic datasets;
- 18 total synthetic rows across operation orders, friendly units, enemy units,
  rules of engagement, and terrain;
- 16 deterministic link candidates;
- dataset preview, ranked recommendation, evidence expansion, search, status
  filter, bulk selection, approve, ignore, and reset interactions; and
- per-case SQLite review state.

## What was not reconstructed

- the original AgentOS code or visual assets;
- the parser, graph builder, ROE validator, or COA planner implementation;
- the displayed on-premise model or its prompt;
- the original score calibration and candidate-generation method; and
- mutation of an operational ontology or knowledge graph.

## Sanity-check evaluation

The six screenshot-verifiable gold relationships appear at rank 1 in the
deterministic reference output.

| Metric | @1 | @3 | @5 |
|---|---:|---:|---:|
| Pair recall | 1.00 | 1.00 | 1.00 |
| Pair precision | 1.00 | 0.60 | 0.60 |
| Pair F1 | 1.00 | 0.75 | 0.75 |

These values only confirm that the reconstruction encodes its six
screenshot-derived relationships. They are not evidence of the original
demo's accuracy and must not be presented as an independent benchmark.

## Future common comparison

For an apples-to-apples result, run SCHEMORA on the same five schema tables,
freeze the six-pair gold, and compare both candidate lists with the same
evaluator. The reference output uses no external LLM call, so its model-call,
token, API-cost, and model-runtime values are zero; implementation and human
review effort remain separate costs.
