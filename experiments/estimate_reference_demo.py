#!/usr/bin/env python3
"""No-network estimate for five pairwise reference-demo SCHEMORA runs."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import sys
from collections import Counter
from pathlib import Path

from estimate_cost import LIMITS, estimate

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "reference_demo_reconstruction"
OUTPUT = ROOT / "outputs" / "reference_demo" / "dry_run_estimate.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    schema_path = CASE / "ontology_schema.csv"
    gold_path = CASE / "draft_partial_gold_mapping.csv"
    with schema_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    counts = Counter(row["TableName"] for row in rows)
    total = len(rows)
    per_benchmark = []
    for table, source_count in counts.items():
        value = estimate(source_count, total - source_count)
        value["source_table"] = table
        per_benchmark.append(value)
    summed_keys = [
        "base_llm_calls",
        "estimated_llm_calls",
        "estimated_embedding_calls",
        "estimated_input_tokens",
        "estimated_output_tokens",
        "estimated_total_tokens",
        "estimated_embedding_tokens",
        "estimated_elapsed_seconds",
        "estimated_cost_usd",
    ]
    totals = {
        key: round(sum(float(item[key]) for item in per_benchmark), 6)
        for key in summed_keys
    }
    result = {
        "dry_run": True,
        "network_or_model_calls_made": False,
        "api_key_present": bool(os.getenv("API_KEY")),
        "strategy": "five pairwise runs; each source ontology is matched against the other four",
        "primary_input_policy": "schema metadata only; observed record values are not passed",
        "pricing_reference": {
            "url": "https://developers.openai.com/api/docs/pricing",
            "verified_on": "2026-07-28",
            "standard_usd_per_million_tokens": {
                "gpt-5-nano_input": 0.05,
                "gpt-5-nano_output": 0.40,
                "text-embedding-3-large_input": 0.13,
            },
            "warning": "actual billed usage and prices at execution time may differ",
        },
        "ontology_count": len(counts),
        "unique_schema_properties": total,
        "per_benchmark": per_benchmark,
        "totals": totals,
        "input_sha256": {
            "ontology_schema.csv": sha256(schema_path),
            "draft_partial_gold_mapping.csv": sha256(gold_path),
        },
        "environment": {
            "os": platform.platform(),
            "python": sys.version.split()[0],
            "architecture": platform.machine(),
        },
        "limits_inherited_from_english_case": LIMITS,
    }
    violations = []
    if totals["estimated_llm_calls"] > LIMITS["llm_calls"]:
        violations.append("llm_calls")
    if totals["estimated_total_tokens"] > LIMITS["total_tokens"]:
        violations.append("total_tokens")
    if totals["estimated_cost_usd"] > LIMITS["cost_usd"]:
        violations.append("cost_usd")
    result["gate_passed"] = not violations
    result["violations"] = violations
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if violations:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
