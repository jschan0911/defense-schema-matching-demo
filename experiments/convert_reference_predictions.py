#!/usr/bin/env python3
"""Combine five official SCHEMORA rank artifacts into one UI prediction CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from convert_predictions import grade, score_for, selected_ids

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "reference_demo" / "predictions.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def convert(frame: Any, top_k: int) -> list[dict[str, str | int]]:
    rows: list[dict[str, str | int]] = []
    for _, group in frame.groupby("query_ind", sort=True):
        source_table = str(group["query_table_name"].iloc[0])
        source_column = str(group["query_column_name"].iloc[0])
        source_desc = str(group["query_column_desc"].iloc[0])
        selections = {
            tuple(selected_ids(value, top_k)) for value in group["selected_columns"]
        }
        if len(selections) != 1:
            raise ValueError(f"inconsistent selection for {source_table}.{source_column}")
        target_lookup = (
            group[["doc_id", "table_name", "column_name", "target_column_desc"]]
            .drop_duplicates()
            .set_index("doc_id")
        )
        for rank, doc_id in enumerate(next(iter(selections)), start=1):
            if doc_id not in target_lookup.index:
                raise ValueError(f"selected doc_id missing from candidates: {doc_id}")
            target = target_lookup.loc[doc_id]
            methods = {
                str(value)
                for value in group.loc[group["doc_id"] == doc_id, "q_type"].tolist()
            }
            rows.append(
                {
                    "run_id": "defense_reference_demo_schemora_gpt5_nano_v1",
                    "source_table": source_table,
                    "source_column": source_column,
                    "rank": rank,
                    "target_object_type": str(target["table_name"]),
                    "target_property": str(target["column_name"]),
                    "retrieval_methods": "|".join(sorted(methods)),
                    "vector_score": score_for(group, doc_id, "embedding"),
                    "bm25_score": score_for(group, doc_id, "bm25"),
                    "selected_table": "true",
                    "llm_rank": rank,
                    "rank_grade": grade(rank, methods),
                    "explanation": (
                        "SCHEMORA의 고정된 검색·테이블 선택·열 순위화 단계가 "
                        f"이 후보를 #{rank}로 반환했습니다. 원 데모 점수와 같은 "
                        "척도가 아닙니다."
                    ),
                    "explanation_generator": "deterministic_schemora_trace_v1",
                    "source_definition": source_desc,
                    "target_definition": str(target["target_column_desc"]),
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, action="append", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if len(args.artifact) != 5:
        raise SystemExit("provide exactly five --artifact paths, one per benchmark")
    import pandas as pd

    rows: list[dict[str, str | int]] = []
    for artifact in args.artifact:
        rows.extend(convert(pd.read_parquet(artifact), args.top_k))
    if not rows:
        raise SystemExit("no SCHEMORA predictions found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    metadata = {
        "source": "five pinned SCHEMORA rank artifacts",
        "artifacts": [
            {
                "benchmark": path.parents[1].name,
                "file": path.name,
                "sha256": sha256(path),
            }
            for path in args.artifact
        ],
        "rows": len(rows),
        "top_k": args.top_k,
        "score_warning": "vector/BM25 scores are not original-demo scores",
    }
    (args.output.parent / "prediction_conversion.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
