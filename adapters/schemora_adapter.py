#!/usr/bin/env python3
"""Prepare fixed case-study inputs for the pinned SCHEMORA checkout."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMIT = "1339fedf8113fc3746d5664f1453248e47ee310c"
BENCHMARK = "defense-usaspending-ocds-v1"
OFFICIAL_FIELDS = [
    "TableName",
    "TableDesc",
    "ColumnName",
    "ColumnDesc",
    "ColumnType",
]


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def commit(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def adapter_patch_hash(path: Path) -> str:
    patch = subprocess.check_output(
        [
            "git",
            "-C",
            str(path),
            "diff",
            "--",
            "utils/llm.py",
            "utils/embedding.py",
            "schema_matching/column_rank.py",
        ]
    )
    return hashlib.sha256(patch).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path, required=True)
    args = parser.parse_args()
    upstream = args.upstream_root.resolve()
    actual_commit = commit(upstream)
    if actual_commit != EXPECTED_COMMIT:
        raise SystemExit(
            f"upstream commit mismatch: {actual_commit} != {EXPECTED_COMMIT}"
        )

    source_rows = load_csv(ROOT / "data" / "source_schema.csv")
    target_rows = load_csv(ROOT / "data" / "target_ontology.csv")
    gold_rows = load_csv(ROOT / "data" / "gold_mapping.csv")
    raw_root = upstream / "raw_data" / BENCHMARK
    source_path = raw_root / "source" / "source.csv"
    target_path = raw_root / "target" / "target.csv"
    mapping_path = raw_root / "mapping" / "mapping.parquet"

    write_csv(
        source_path,
        [
            {
                "TableName": row["TableName"],
                "TableDesc": row["TableDescription"],
                "ColumnName": row["ColumnName"],
                "ColumnDesc": row["ColumnDescription"],
                "ColumnType": row["ColumnType"],
            }
            for row in source_rows
        ],
        OFFICIAL_FIELDS,
    )
    write_csv(
        target_path,
        [
            {
                "TableName": row["ObjectType"],
                "TableDesc": row["ObjectTypeDescription"],
                "ColumnName": row["PropertyName"],
                "ColumnDesc": row["PropertyDescription"],
                "ColumnType": row["PropertyType"],
            }
            for row in target_rows
        ],
        OFFICIAL_FIELDS,
    )

    try:
        import pandas as pd
    except ImportError as error:
        raise SystemExit(
            "pandas and pyarrow from the SCHEMORA environment are required"
        ) from error

    grouped: dict[tuple[str, str], tuple[list[str], list[str]]] = {}
    for row in gold_rows:
        key = (row["source_table"], row["source_column"])
        target_tables, target_columns = grouped.setdefault(key, ([], []))
        if row["target_object_type"]:
            target_tables.append(row["target_object_type"])
            target_columns.append(row["target_property"])
    mapping_rows = [
        {
            "SRC_ENT": table,
            "SRC_ATT": column,
            "TGT_ENT": target_tables,
            "TGT_ATT": target_columns,
        }
        for (table, column), (target_tables, target_columns) in sorted(grouped.items())
    ]
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(mapping_rows).to_parquet(mapping_path, index=False)

    config_path = upstream / f"config_{BENCHMARK}.toml"
    config_path.write_text(
        f"""[experiment]
overwrite = true
n_candidates = 3
query_enrichment = true
document_enrichment = true
non_sim_prompt = true
embedding_search = true
full_text_search = true
table_selection = true

[data]
benchmark_name = "{BENCHMARK}"
run_only_for_annotated = false

[embedding.client]
type = "openai"

[llm.client]
type = "openai"

[embedding.client.args]
nthreads = 1
model_name = "text-embedding-3-large"

[llm.client.args]
nthreads = 2
model_name = "gpt-5-nano"
""",
        encoding="utf-8",
    )
    manifest = {
        "run_id": "defense_usaspending_ocds_gpt5_nano_v1",
        "claim": "official-code adaptation",
        "official_repository": "https://github.com/schemorapaper/schemora",
        "official_commit": actual_commit,
        "adapter_patch_sha256": adapter_patch_hash(upstream),
        "adapter_modified_upstream_files": [
            "utils/llm.py",
            "utils/embedding.py",
            "schema_matching/column_rank.py",
        ],
        "config": config_path.name,
        "inputs": {
            str(source_path.relative_to(upstream)): sha256(source_path),
            str(target_path.relative_to(upstream)): sha256(target_path),
            str(mapping_path.relative_to(upstream)): sha256(mapping_path),
        },
        "limitations": [
            "gpt-5-nano replaces the paper model",
            "temperature escalation is unsupported",
            "common complete-gold evaluator is authoritative",
        ],
    }
    output = ROOT / "outputs" / "adapter_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
