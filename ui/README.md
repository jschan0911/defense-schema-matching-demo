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

- The large display score is `round(vector_score * 100)`.
- It is a readability transform, not a probability or calibrated confidence.
- Candidate order follows the final SCHEMORA LLM rank, not the display score.
- Raw vector and BM25 values remain visible in the evidence detail.

## Rule-based rank grade

- **High**: rank 1 and supported by both embedding and BM25 retrieval.
- **Medium**: rank 1–3, or supported by both retrieval families.
- **Low**: every other returned candidate.

This grade is a deterministic display heuristic. It is not calibrated
confidence and does not affect the saved SCHEMORA rank.

Approval, ignore, reset-to-pending, search, status filtering, multi-select
approval, case switching, five-dataset preview, raw evidence display, and
result reload are implemented. The `OntologySink` interface is separate, and
the current sink is intentionally a mock that performs no ontology mutation.

The two result surfaces are intentionally separate:

- `Reference · 관찰값` reads the nine fully visible screenshot candidates from
  `observable_reference.json` and is read-only.
- `SCHEMORA 결과` reads only
  `outputs/reference_demo/predictions.csv`. It stays empty until the pinned
  pipeline has actually run and its artifacts have been converted.

The displayed original-demo score and SCHEMORA vector/BM25 scores are labeled
as different scales. The UI never copies one into the other.
