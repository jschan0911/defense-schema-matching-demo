# Defense Schema Matching Case Lab

A single human-in-the-loop workbench with three strictly isolated case packs:

1. **USAspending → OCDS** — the preserved English baseline.
2. **Synthetic C2 reference reconstruction** — five screenshot-transcribed,
   seminar-only datasets and a deterministic 16-link review flow.
3. **D2B → Korean contract open standard** — an official Korean-to-Korean
   schema case, prepared but not yet run.

The common UI and evaluator make the cases inspectable without mixing their
data, gold mappings, status, or claims. See
[`docs/case_architecture.md`](docs/case_architecture.md).

This repository reports bounded, public or synthetic metadata case studies. It
is not validation across the entire defense domain and contains no operational
unit, mission, location, personnel, or contract records.

## Status

The data, licensing, sensitivity, target design, and estimated run budget are
fixed in [`docs/execution_plan.md`](docs/execution_plan.md). No Matchmaker or
G.E.R. run is part of this repository.

The Korean case has no model output yet. Its gold mapping is a draft that
requires independent procurement-domain review. The reconstructed demo is not
a reproduction of the original product or algorithm.
