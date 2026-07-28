# Methodology

The case study maps public USAspending Department of Defense contract-award
metadata to OCDS 1.1.5.

1. Fetch and hash the official USAspending data dictionary and canonical OCDS
   schema.
2. Select 55 USAspending properties in five logical source tables.
3. Extract and hash 108 target properties in ten OCDS object types.
4. Freeze the target hash before gold annotation.
5. Build complete draft gold with official definition evidence, including
   1:n and no-match cases.
6. Run the no-network dry-run cost gate.
7. Prepare the pinned SCHEMORA official-code adaptation.
8. Execute one `gpt-5-nano`/`text-embedding-3-large` run.
9. Convert the official rank artifact to the common Top-K format.
10. Evaluate, classify errors, calculate resources and efficiency, and load
    the same prediction CSV in the review UI.

No Matchmaker or G.E.R. call occurs. No LLM-generated source or target
description is used.

