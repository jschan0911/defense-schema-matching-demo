# Human-in-the-loop C2 Demonstration

The UI exposes one synthetic C2 case from `cases/catalog.json` and persists
SCHEMORA review state to SQLite. It never labels an uncalibrated score as a
probability.

```bash
python3 ui/backend/server.py
```

Open <http://127.0.0.1:8765>.

## Reference display

- The score is copied from the observable demo screenshot.
- The visible bands are `High >= 90`, `Medium 70–89`, and `Low < 70`.
- The original score formula and calibration are unknown.
- The nine fully visible rows are read-only observations, not complete gold.

## SCHEMORA display

- Candidate order follows the global review priority derived from equal-weight
  RRF (`k=60`) over query-local LLM, vector, and BM25 ranks.
- The large display value is the RRF score normalized by its theoretical
  three-signal maximum. It is not probability or calibrated confidence.
- Raw vector/BM25 scores and all three query-local ranks remain visible in the
  evidence detail.
- SCHEMORA rows display `링크명 미지정`; the UI does not infer a link name or
  `relatedTo`/`symmetric` type from field names.

## Signal agreement

The `3/3`, `2/3`, or `1/3` badge reports how many of the LLM, vector, and BM25
rank lists contributed to RRF. Missing retrieval signals contribute zero.
Signal count is not a correctness vote or confidence estimate.

Approval, ignore, reset-to-pending, search, status filtering, multi-select
approval, case switching, five-dataset preview, raw evidence display, and
result reload are implemented. The `OntologySink` interface is separate, and
the current sink is intentionally a mock that performs no ontology mutation.

The two result surfaces are intentionally separate:

- `Reference · 관찰값` reads the nine fully visible screenshot candidates from
  `observable_reference.json` and is read-only.
- `SCHEMORA 결과` reads only
  `outputs/reference_demo/predictions_global_priority.csv`, a deterministic
  derivative of the pinned pipeline output.

The displayed original-demo score, RRF priority, and raw SCHEMORA vector/BM25
scores are labeled as different scales. The UI never copies one into another.
