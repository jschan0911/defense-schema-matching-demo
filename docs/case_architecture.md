# Three-case architecture

## Decision

Keep one private project and one review application. Isolate each case under
`cases/` and reuse only the UI, review-state API, and metric definitions.

| Case | Purpose | Data status | Result status |
|---|---|---|---|
| USAspending → OCDS | English international-standard baseline | Public schema metadata | UI fixture; live run remains separate |
| Synthetic C2 reconstruction | Observable reference workflow | Screenshot-transcribed synthetic rows | 16 deterministic reference recommendations |
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

The reconstruction therefore implements:

1. the five visible synthetic tables;
2. exact-value and bounded semantic link rules;
3. a 16-item candidate list;
4. human approve, ignore, reset, search, and filtering interactions; and
5. explicit raw evidence and heuristic score labels.

It does not reuse or distribute the original screenshots, brand, code, or
assets. It must be described as a `screenshot-guided reference
reconstruction`, never an original-system reproduction.

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

A pipeline comparison is valid only when both systems receive the same case
pack and are evaluated against the same frozen gold file. The reconstructed
demo's screenshot-derived scores must not be compared numerically with
SCHEMORA retrieval scores as if they were calibrated probabilities.

The common comparison table should report:

- Recall@1, Recall@3, Recall@5;
- Precision@K and pair F1@K;
- no-match false recommendations;
- model calls, input/output tokens, elapsed time, and cost; and
- human review decisions and review duration.

Until the Korean run exists, its UI state is `schema-ready-not-run`.
