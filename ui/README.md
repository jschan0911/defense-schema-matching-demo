# Human-in-the-loop Case Lab

The UI exposes three isolated cases from `cases/catalog.json` and persists
review state to SQLite. It never labels an uncalibrated score as a probability.
If `outputs/predictions.csv` exists, it replaces the English UI fixture only;
the reconstructed and Korean cases remain isolated.

```bash
python3 ui/backend/server.py
```

Open <http://127.0.0.1:8765>.

To force the English development fixture:

```bash
python3 ui/backend/server.py --demo --db /tmp/defense-schema-demo-review.db
```

## Rank grade

- **High**: rank 1 and supported by both embedding and BM25 retrieval.
- **Medium**: rank 1–3, or supported by both retrieval families.
- **Low**: every other returned candidate.

This grade is a deterministic display heuristic. It is not calibrated
confidence.

Approval, ignore, reset-to-pending, search, status filtering, multi-select
approval, case switching, five-dataset preview, raw evidence display, and
result reload are implemented. The `OntologySink` interface is separate, and
the current sink is intentionally a mock that performs no ontology mutation.
