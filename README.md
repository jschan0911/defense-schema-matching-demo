# Defense Schema Matching Case Lab

A single human-in-the-loop workbench with three strictly isolated case packs:

1. **USAspending → OCDS** — the preserved English baseline.
2. **Synthetic C2 observable comparison** — five screenshot-transcribed,
   seminar-only datasets, nine fully visible reference candidates, and a
   separately wired SCHEMORA pipeline.
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

The reference-demo case now contains one completed five-benchmark SCHEMORA run
and a positive-only recovery comparison against four conceptual saved links.
The Korean D2B case remains unrun. Neither case has complete independent gold,
so precision and F1 are not reported. The reference case is not a reproduction
of the original product or algorithm, and hidden candidates are not
reconstructed.
