#!/usr/bin/env python3
"""Prepare five cross-ontology SCHEMORA benchmarks from observed demo schemas."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "reference_demo_reconstruction"
EXPECTED_COMMIT = "1339fedf8113fc3746d5664f1453248e47ee310c"
EXPECTED_ADAPTER_PATCH_SHA256 = (
    "491efc93e9672ed13387ccba6feedbfa6014886a4239de6dccfa38cdd663f7d0"
)
ADAPTER_MODIFIED_FILES = [
    "utils/llm.py",
    "utils/embedding.py",
    "schema_matching/column_rank.py",
]
TABLES = ["작전명령", "아군_부대", "적군_부대", "교전규칙", "지형_정보"]
SLUGS = {
    "작전명령": "operation-order",
    "아군_부대": "friendly-unit",
    "적군_부대": "enemy-unit",
    "교전규칙": "rules",
    "지형_정보": "terrain",
}
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


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OFFICIAL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upstream_commit(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def adapter_patch(path: Path) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(path), "diff", "--", *ADAPTER_MODIFIED_FILES],
    )


def official_row(row: dict[str, str]) -> dict[str, str]:
    return {
        "TableName": row["TableName"],
        "TableDesc": row["TableDescription"],
        "ColumnName": row["ColumnName"],
        "ColumnDesc": row["ColumnDescription"],
        "ColumnType": row["ColumnType"],
    }


def config_text(benchmark: str) -> str:
    return f"""[experiment]
overwrite = true
n_candidates = 3
query_enrichment = true
document_enrichment = true
non_sim_prompt = true
embedding_search = true
full_text_search = true
table_selection = true

[data]
benchmark_name = "{benchmark}"
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
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path, required=True)
    args = parser.parse_args()
    upstream = args.upstream_root.resolve()
    actual_commit = upstream_commit(upstream)
    if actual_commit != EXPECTED_COMMIT:
        raise SystemExit(
            f"upstream commit mismatch: {actual_commit} != {EXPECTED_COMMIT}"
        )
    actual_patch_sha256 = hashlib.sha256(adapter_patch(upstream)).hexdigest()
    if actual_patch_sha256 != EXPECTED_ADAPTER_PATCH_SHA256:
        raise SystemExit(
            "SCHEMORA adapter patch mismatch: "
            f"{actual_patch_sha256} != {EXPECTED_ADAPTER_PATCH_SHA256}"
        )

    schema_rows = load_csv(CASE / "ontology_schema.csv")
    try:
        import pandas as pd
    except ImportError as error:
        raise SystemExit(
            "pandas and pyarrow from the pinned SCHEMORA environment are required"
        ) from error

    prepared: list[dict[str, object]] = []
    for source_table in TABLES:
        benchmark = f"defense-reference-{SLUGS[source_table]}-v1"
        raw_root = upstream / "raw_data" / benchmark
        source_path = raw_root / "source" / "source.csv"
        target_path = raw_root / "target" / "target.csv"
        mapping_path = raw_root / "mapping" / "mapping.parquet"
        source_rows = [
            official_row(row) for row in schema_rows if row["TableName"] == source_table
        ]
        target_rows = [
            official_row(row) for row in schema_rows if row["TableName"] != source_table
        ]
        write_csv(source_path, source_rows)
        write_csv(target_path, target_rows)

        mapping_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [],
            columns=["SRC_ENT", "SRC_ATT", "TGT_ENT", "TGT_ATT"],
        ).to_parquet(mapping_path, index=False)
        config_path = upstream / f"config_{benchmark}.toml"
        config_path.write_text(config_text(benchmark), encoding="utf-8")
        prepared.append(
            {
                "benchmark": benchmark,
                "source_table": source_table,
                "source_properties": len(source_rows),
                "target_properties": len(target_rows),
                "config": config_path.name,
                "inputs": {
                    str(source_path.relative_to(upstream)): sha256(source_path),
                    str(target_path.relative_to(upstream)): sha256(target_path),
                    str(mapping_path.relative_to(upstream)): sha256(mapping_path),
                },
            }
        )

    manifest = {
        "run_id": "defense_reference_demo_schemora_gpt5_nano_v1",
        "claim": (
            "pinned official-code adaptation for this demonstration; execution "
            "status is recorded separately in run_manifest.json"
        ),
        "official_repository": "https://github.com/schemorapaper/schemora",
        "official_commit": actual_commit,
        "adapter_patch_sha256": actual_patch_sha256,
        "adapter_modified_upstream_files": ADAPTER_MODIFIED_FILES,
        "adapter_patch_purpose": [
            "gpt-5-nano request compatibility and token-usage telemetry",
            "embedding client robustness and telemetry",
            "rank-stage artifact/usage handling required by the frozen runner",
        ],
        "dependency_lock": {
            "file": "requirements.txt",
            "sha256": sha256(upstream / "requirements.txt"),
        },
        "model": "gpt-5-nano",
        "embedding_model": "text-embedding-3-large",
        "input_policy": {
            "schemas": (
                f"all {len(schema_rows)} observed/normalized fields across five "
                "ontologies"
            ),
            "record_values": "not passed to the primary SCHEMORA run",
            "same_ontology_candidates": "excluded by five pairwise benchmarks",
            "gold": (
                "zero-row mapping parquet; saved-link positives are external "
                "evaluation-only data"
            ),
        },
        "benchmarks": prepared,
        "limitations": [
            "SCHEMORA ranks schema correspondences, while the reference UI proposes named ontology relations",
            "the original demo model, prompt, score calibration, and hidden seven candidates are unavailable",
            "precision and F1 are withheld until independent complete-gold review",
        ],
    }
    output = ROOT / "outputs" / "reference_demo" / "adapter_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
