# Limitations and release checklist

## Scientific limitations

- This is one bounded U.S. defense procurement metadata case study.
- The target is a public procurement standard, not a comprehensive defense
  ontology.
- The gold is complete for the selected subset but has not received
  independent procurement-SME review.
- The planned SCHEMORA result is one run (`n=1`).
- `gpt-5-nano` replaces the model used in the SCHEMORA paper.
- SCHEMORA has no explicit no-match classifier; empty post-threshold output is
  the fixed proxy.
- Rank grades in the UI are deterministic heuristics, not calibrated
  probabilities.
- Manual review savings are estimates until an actual timed review session is
  performed.

## Required before changing GitHub visibility to public

- Run a secret scan and inspect every finding.
- Confirm there are no local absolute paths in tracked text files.
- Confirm no `.env`, key, endpoint credential, raw award record, cache, or
  upstream SCHEMORA source is tracked.
- Re-run license and NOTICE review.
- Re-check field definitions and screenshots for personal, operational, unit,
  facility, and precise-location information.
- Distinguish demo screenshot/fixture from real-run artifacts.
- Confirm all manifests use repository-relative paths.

