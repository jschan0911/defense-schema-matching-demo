# Three-case architecture

## Decision

Keep one private project and one review application. Isolate each case under
`cases/` and reuse only the UI, review-state API, and metric definitions.

| Case | Purpose | Data status | Result status |
|---|---|---|---|
| USAspending → OCDS | English international-standard baseline | Public schema metadata | UI fixture; live run remains separate |
| Synthetic C2 comparison | Observable reference workflow | Screenshot-transcribed synthetic rows | 9 visible reference rows; SCHEMORA not run |
| D2B → Korean contract standard | Korean domestic standardization | Official API schema metadata | Not run |

## Claim boundaries

### English baseline

The existing files remain at their original paths so earlier manifests and
scripts remain valid. The case catalog points to those files rather than
copying or translating them.

### Screenshot-guided reconstruction

Six screenshots establish the observable scope: five dataset previews and one
link-review page. They do not disclose the original parser, graph builder,
validator, planner, LLM prompt, calibration rule, or ontology mutation logic.

The case therefore implements three explicitly separated layers:

1. an evidence layer containing the five visible synthetic tables and the nine
   candidate rows fully visible in the recommendation screenshot;
2. a SCHEMORA layer that accepts all 27 frozen schema fields and reads only
   converted output from five real pinned-pipeline runs; and
3. a UI layer that keeps the reference rows read-only while enabling search,
   filtering, approval, ignore, reset, and evidence inspection for actual
   SCHEMORA results.

It does not invent the seven hidden candidates or reuse and distribute the
original screenshots, brand, code, or assets. It must be described as a
`screenshot-guided observable baseline versus SCHEMORA implementation`, never
an original-system reproduction.

### Korean case

The Source is the DAPA D2B domestic contract response schema. The Target is the
Korean nationwide contract-information open standard schema. Both sides retain
their official Korean labels and system keys.

The case currently stops before model execution:

- official Source and Target fields are recorded;
- a 13-source draft gold mapping is recorded;
- ambiguous institutional-role mappings are labeled contextual;
- no score, prediction, runtime, token, or cost claim is emitted.

An independent procurement-domain reviewer must approve the gold before
precision or F1 is reported.

## Common-comparison rule

A pipeline comparison is valid only when SCHEMORA receives the frozen five
ontology schemas and is evaluated against the same independently reviewed gold
file. Original-demo screenshot scores must not be compared numerically with
SCHEMORA retrieval scores as if they were calibrated probabilities.

The common comparison table should report:

- Recall@1, Recall@3, Recall@5;
- Precision@K and pair F1@K;
- no-match false recommendations;
- model calls, input/output tokens, elapsed time, and cost; and
- human review decisions and review duration.

Until the Korean run exists, its UI state is `schema-ready-not-run`.
