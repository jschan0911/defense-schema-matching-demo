# Screenshot-guided observable baseline versus SCHEMORA

This case transcribes the five synthetic datasets and the observable link-review
and saved-link workflows from seven user-supplied screenshots.

It does **not** claim to reproduce the original product, model, agent
orchestration, confidence calibration, or ontology engine. No original code,
brand asset, or screenshot is distributed in this repository.

The reference page reports 16 recommendations, but only nine rows are fully
visible. `observable_reference.json` records exactly those nine rows, in their
visible order, with the displayed scores and truncated text. The hidden seven
are not reconstructed.

No local heuristic candidate list is treated as a model result. Real SCHEMORA
output is loaded only from `outputs/reference_demo/predictions.csv`, which was
created from the five completed pinned rank artifacts.

The pipeline uses official SCHEMORA commit
`1339fedf8113fc3746d5664f1453248e47ee310c` plus the same fixed three-file
compatibility/telemetry patch as the frozen English case. Its patch SHA-256 is
`491efc93e9672ed13387ccba6feedbfa6014886a4239de6dccfa38cdd663f7d0`.
Both values are enforced before input generation and execution.

All records are explicitly synthetic seminar data. They must not be replaced
with operational unit, mission, terrain, personnel, or location records.

The primary SCHEMORA input contains all 28 observed or normalized schema fields
across the five ontologies. Record values remain available for provenance and
UI inspection but are not passed to the primary SCHEMORA metadata pipeline.

The saved-link management screenshot contributes four conceptual
evaluation-only positives (five directed rows). All five SCHEMORA mapping
parquets contain zero rows, so these positives are not supplied to retrieval,
table selection, ranking prompts, or annotations.
