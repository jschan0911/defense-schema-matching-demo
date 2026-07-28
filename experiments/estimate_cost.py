#!/usr/bin/env python3
"""No-network dry run and conservative SCHEMORA cost gate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = {
    "source_queries": 111,
    "target_properties": 267,
    "llm_calls": 992,
    "input_tokens": 1_054_446,
    "output_tokens": 344_735,
    "total_measured_tokens": 1_428_541,
    "embedding_calls": 1_134,
    "embedding_tokens": 29_360,
    "elapsed_seconds": 2_741.17,
    "cost_usd": 0.1944331,
}
LIMITS = {
    "source_properties": 80,
    "target_properties": 150,
    "llm_calls": 992,
    "total_tokens": 1_428_541,
    "elapsed_seconds": 2_741.17,
    "cost_usd": 0.1944,
}


def count_rows(path: Path) -> int:
    with path.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def estimate(source_count: int, target_count: int) -> dict[str, object]:
    base_calls = 2 * (source_count + target_count) + 2 * source_count
    llm_calls = math.ceil(base_calls * 1.05)
    input_per_call = BASELINE["input_tokens"] / BASELINE["llm_calls"]
    output_per_call = BASELINE["output_tokens"] / BASELINE["llm_calls"]
    # Official source and target definitions are longer than the Synthea
    # metadata on average, so input tokens receive a 35% safety multiplier.
    input_tokens = math.ceil(llm_calls * input_per_call * 1.35)
    output_tokens = math.ceil(llm_calls * output_per_call)
    total_tokens = input_tokens + output_tokens
    schema_ratio = (source_count + target_count) / (
        BASELINE["source_queries"] + BASELINE["target_properties"]
    )
    embedding_calls = math.ceil(BASELINE["embedding_calls"] * schema_ratio * 1.05)
    embedding_tokens = math.ceil(BASELINE["embedding_tokens"] * schema_ratio * 1.05)
    chat_cost = input_tokens / 1_000_000 * 0.05 + output_tokens / 1_000_000 * 0.40
    embedding_cost = embedding_tokens / 1_000_000 * 0.13
    cost = chat_cost + embedding_cost
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
        "pricing_assumption_usd_per_million": {
            "gpt-5-nano_input": 0.05,
            "gpt-5-nano_output": 0.40,
            "text-embedding-3-large_input": 0.13,
        },
        "method": (
            "official stage call formula plus 5% retry allowance; Synthea "
            "per-call tokens with 35% input-length safety multiplier"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "dry_run_estimate.json",
    )
    args = parser.parse_args()
    source_path = ROOT / "data" / "source_schema.csv"
    target_path = ROOT / "data" / "target_ontology.csv"
    gold_path = ROOT / "data" / "gold_mapping.csv"
    result = estimate(count_rows(source_path), count_rows(target_path))
    result.update(
        {
            "dry_run": True,
            "network_or_model_calls_made": False,
            "api_key_present": bool(os.getenv("API_KEY")),
            "input_sha256": {
                "source_schema.csv": sha256(source_path),
                "target_ontology.csv": sha256(target_path),
                "gold_mapping.csv": sha256(gold_path),
            },
            "environment": {
                "os": platform.platform(),
                "python": sys.version.split()[0],
                "architecture": platform.machine(),
            },
            "reference_baseline": BASELINE,
            "limits": LIMITS,
        }
    )
    violations: list[str] = []
    comparisons = {
        "source_properties": result["source_queries"],
        "target_properties": result["target_properties"],
        "llm_calls": result["estimated_llm_calls"],
        "total_tokens": result["estimated_total_tokens"],
        "elapsed_seconds": result["estimated_elapsed_seconds"],
        "cost_usd": result["estimated_cost_usd"],
    }
    for key, value in comparisons.items():
        if float(value) > LIMITS[key]:
            violations.append(f"{key}: {value} > {LIMITS[key]}")
    result["gate_passed"] = not violations
    result["violations"] = violations
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if violations:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
