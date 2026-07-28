#!/usr/bin/env python3
"""No-network estimate for five pairwise reference-demo SCHEMORA runs."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import sys
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "reference_demo_reconstruction"
OUTPUT = ROOT / "outputs" / "reference_demo" / "dry_run_estimate.json"
BASELINE = {
    "source_queries": 111,
    "target_properties": 267,
    "llm_calls": 992,
    "input_tokens": 1_054_446,
    "output_tokens": 344_735,
    "embedding_calls": 1_134,
    "embedding_tokens": 29_360,
    "elapsed_seconds": 2_741.17,
}
LIMITS = {
    "llm_calls": 500,
    "total_tokens": 800_000,
    "elapsed_seconds": 1_800,
    "cost_usd": 0.10,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def estimate(source_count: int, target_count: int) -> dict[str, object]:
    base_calls = 2 * (source_count + target_count) + 2 * source_count
    llm_calls = math.ceil(base_calls * 1.05)
    input_per_call = BASELINE["input_tokens"] / BASELINE["llm_calls"]
    output_per_call = BASELINE["output_tokens"] / BASELINE["llm_calls"]
    input_tokens = math.ceil(llm_calls * input_per_call * 1.35)
    output_tokens = math.ceil(llm_calls * output_per_call)
    total_tokens = input_tokens + output_tokens
    schema_ratio = (source_count + target_count) / (
        BASELINE["source_queries"] + BASELINE["target_properties"]
    )
    embedding_calls = math.ceil(BASELINE["embedding_calls"] * schema_ratio * 1.05)
    embedding_tokens = math.ceil(BASELINE["embedding_tokens"] * schema_ratio * 1.05)
    cost = (
        input_tokens / 1_000_000 * 0.05
        + output_tokens / 1_000_000 * 0.40
        + embedding_tokens / 1_000_000 * 0.13
    )
    elapsed = BASELINE["elapsed_seconds"] * llm_calls / BASELINE["llm_calls"] * 1.25
    return {
        "source_queries": source_count,
        "target_properties": target_count,
        "base_llm_calls": base_calls,
        "estimated_llm_calls": llm_calls,
        "estimated_embedding_calls": embedding_calls,
        "estimated_input_tokens": input_tokens,
        "estimated_output_tokens": output_tokens,
        "estimated_total_tokens": total_tokens,
        "estimated_embedding_tokens": embedding_tokens,
        "estimated_elapsed_seconds": round(elapsed, 2),
        "estimated_cost_usd": round(cost, 6),
        "method": (
            "official stage call formula plus 5% retry allowance and a 35% "
            "input-length safety multiplier"
        ),
    }


def main() -> None:
    schema_path = CASE / "ontology_schema.csv"
    positive_path = CASE / "observable_saved_positive_relations.csv"
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
            "observable_saved_positive_relations.csv": sha256(positive_path),
        },
        "environment": {
            "os": platform.platform(),
            "python": sys.version.split()[0],
            "architecture": platform.machine(),
        },
        "project_local_budget_gate": LIMITS,
    }
    violations = []
    if totals["estimated_llm_calls"] > LIMITS["llm_calls"]:
        violations.append("llm_calls")
    if totals["estimated_total_tokens"] > LIMITS["total_tokens"]:
        violations.append("total_tokens")
    if totals["estimated_cost_usd"] > LIMITS["cost_usd"]:
        violations.append("cost_usd")
    if totals["estimated_elapsed_seconds"] > LIMITS["elapsed_seconds"]:
        violations.append("elapsed_seconds")
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
