# Evaluation protocol

Primary scope: all 55 selected source properties against the target schema
whose pre-annotation SHA-256 is recorded in `data/schema_manifest.json`.

- `HitRate@K`: all-source success. For answerable sources it requires any gold
  hit; for no-match sources it requires an empty returned list.
- `Macro Recall@K`: mean fraction of gold target pairs found, answerable
  sources only.
- `Any-hit@K`: fraction of answerable sources with one or more gold hits.
- `Micro pair Recall@K`: recovered gold pairs divided by all answerable gold
  pairs.
- `Precision@K`: correct returned pairs divided by all returned pairs,
  including false candidates for no-match sources.
- `Pair F1@K`: harmonic mean of pair precision and micro pair recall.
- `nDCG@5` and `MAP@5`: binary-relevance ranking metrics over answerable
  sources.
- No-match false recommendations: gold no-match sources with any returned
  candidate.
- No-match detection: gold no-match sources with an empty candidate list.

SCHEMORA does not emit an explicit no-match label. An empty result after its
fixed vector/BM25 thresholds and ranking pipeline is treated as no-match. This
rule was fixed before the live run.

Primary numerical claims require `data/gold_mapping.csv` to remain complete.
Because the current gold has not received independent SME review, precision
and F1 must be labeled provisional case-study values.

