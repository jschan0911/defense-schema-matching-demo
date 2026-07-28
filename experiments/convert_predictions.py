#!/usr/bin/env python3
"""Convert the official SCHEMORA rank artifact to the public Top-K CSV."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def selected_ids(value: Any, top_k: int) -> list[int]:
    if isinstance(value, (str, bytes)):
        raise ValueError(f"unexpected selected_columns: {value!r}")
    return [int(item) for item in list(value)[:top_k]]


def score_for(group: Any, doc_id: int, method: str) -> str:
    rows = group[(group["doc_id"] == doc_id) & group["q_type"].str.contains(method)]
    if rows.empty:
        return ""
    return f"{float(rows['score'].max()):.8f}"


def grade(rank: int, retrieval_methods: set[str]) -> str:
    semantic = any("embedding" in item for item in retrieval_methods)
    lexical = any("bm25" in item for item in retrieval_methods)
    if rank == 1 and semantic and lexical:
        return "High"
    if rank <= 3 or (semantic and lexical):
        return "Medium"
    return "Low"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "predictions.csv",
    )
    args = parser.parse_args()
    import pandas as pd

    frame = pd.read_parquet(args.artifact)
    required = {
        "query_ind",
        "query_table_name",
        "query_column_name",
        "query_column_desc",
        "doc_id",
        "table_name",
        "column_name",
        "target_column_desc",
        "q_type",
        "score",
        "selected_columns",
        "selected_table_names",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"artifact missing columns: {missing}")

    rows: list[dict[str, str | int]] = []
    for _, group in frame.groupby("query_ind", sort=True):
        source_table = str(group["query_table_name"].iloc[0])
        source_column = str(group["query_column_name"].iloc[0])
        source_desc = str(group["query_column_desc"].iloc[0])
        selections = {
            tuple(selected_ids(value, args.top_k))
            for value in group["selected_columns"]
        }
        if len(selections) != 1:
            raise ValueError(
                f"inconsistent selection for {source_table}.{source_column}"
            )
        target_lookup = (
            group[["doc_id", "table_name", "column_name", "target_column_desc"]]
            .drop_duplicates()
            .set_index("doc_id")
        )
        for rank, doc_id in enumerate(next(iter(selections)), start=1):
            if doc_id not in target_lookup.index:
                raise ValueError(f"selected doc_id missing from candidates: {doc_id}")
            target = target_lookup.loc[doc_id]
            method_set = set(
                str(value)
                for value in group.loc[group["doc_id"] == doc_id, "q_type"].tolist()
            )
            vector_score = score_for(group, doc_id, "embedding")
            bm25_score = score_for(group, doc_id, "bm25")
            target_desc = str(target["target_column_desc"])
            explanation = (
                f"SCHEMORA ranked this candidate #{rank} after "
                f"{', '.join(sorted(method_set)) or 'retrieval'} and table/column "
                "ranking. The source and target definitions were supplied to the "
                "official ranking prompt; this sentence is a deterministic display "
                "summary, not an additional model judgment."
            )
            rows.append(
                {
                    "run_id": "defense_usaspending_ocds_gpt5_nano_v1",
                    "source_table": source_table,
                    "source_column": source_column,
                    "rank": rank,
                    "target_object_type": str(target["table_name"]),
                    "target_property": str(target["column_name"]),
                    "retrieval_methods": "|".join(sorted(method_set)),
                    "vector_score": vector_score,
                    "bm25_score": bm25_score,
                    "selected_table": "true",
                    "llm_rank": rank,
                    "rank_grade": grade(rank, method_set),
                    "explanation": explanation,
                    "explanation_generator": "deterministic_template_v1",
                    "source_definition": source_desc,
                    "target_definition": target_desc,
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "artifact": str(args.artifact),
        "rows": len(rows),
        "queries_with_predictions": len(
            {(row["source_table"], row["source_column"]) for row in rows}
        ),
        "top_k": args.top_k,
        "grade_rule": {
            "High": "rank 1 and supported by both embedding and BM25 retrieval",
            "Medium": "rank <= 3 or supported by both retrieval families",
            "Low": "all other returned candidates",
        },
    }
    (args.output.parent / "prediction_conversion.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
