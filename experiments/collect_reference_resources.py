#!/usr/bin/env python3
"""Collect reproducible resource totals without exposing prompts or credentials."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "reference_demo"
RUNTIME = OUTPUT / "runtime"
PRICES = {
    "gpt-5-nano_input": 0.05,
    "gpt-5-nano_output": 0.40,
    "text-embedding-3-large_input": 0.13,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    calls: Counter[str] = Counter()
    tokens: defaultdict[tuple[str, str], int] = defaultdict(int)
    usage_files = []
    for path in sorted(RUNTIME.glob("*-usage.jsonl")):
        records = 0
        for line in path.open(encoding="utf-8"):
            row = json.loads(line)
            records += 1
            kind = str(row["kind"])
            calls[kind] += 1
            for key, value in row.items():
                if key.endswith("_tokens") and isinstance(value, int):
                    tokens[(kind, key)] += value
        usage_files.append(
            {"file": path.name, "records": records, "sha256": sha256(path)}
        )

    elapsed_by_benchmark = {}
    logs = []
    for path in sorted(RUNTIME.glob("*.log")):
        text = path.read_text(encoding="utf-8", errors="replace")
        elapsed = sum(
            float(match.group(1))
            for match in re.finditer(r"^real ([0-9.]+)$", text, re.MULTILINE)
        )
        stages = sum(line.startswith("STAGE ") for line in text.splitlines())
        elapsed_by_benchmark[path.stem] = round(elapsed, 2)
        logs.append(
            {
                "file": path.name,
                "stages": stages,
                "traceback_detected": "Traceback" in text,
                "sha256": sha256(path),
            }
        )

    chat_input = tokens[("chat", "input_tokens")]
    chat_output = tokens[("chat", "output_tokens")]
    embedding_input = tokens[("embedding", "input_tokens")]
    cost = (
        chat_input / 1_000_000 * PRICES["gpt-5-nano_input"]
        + chat_output / 1_000_000 * PRICES["gpt-5-nano_output"]
        + embedding_input / 1_000_000 * PRICES["text-embedding-3-large_input"]
    )
    with (OUTPUT / "predictions.csv").open(encoding="utf-8", newline="") as handle:
        prediction_rows = sum(1 for _ in csv.DictReader(handle))
    run_manifest_path = OUTPUT / "run_manifest.json"
    run_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
    run_manifest.update(
        {
            "prediction_conversion_required": False,
            "postprocessing_completed": True,
            "prediction_rows": prediction_rows,
            "predictions_sha256": sha256(OUTPUT / "predictions.csv"),
            "comparison_sha256": sha256(OUTPUT / "comparison.json"),
        }
    )
    run_manifest_path.write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result = {
        "status": "completed",
        "model_calls": dict(calls),
        "tokens": {
            "chat_input": chat_input,
            "chat_output": chat_output,
            "embedding_input": embedding_input,
            "total": chat_input + chat_output + embedding_input,
        },
        "elapsed_seconds": round(sum(elapsed_by_benchmark.values()), 2),
        "elapsed_by_benchmark": elapsed_by_benchmark,
        "estimated_cost_usd_from_measured_tokens": round(cost, 6),
        "pricing_usd_per_million_tokens": PRICES,
        "pricing_reference": "https://developers.openai.com/api/docs/pricing",
        "prediction_rows": prediction_rows,
        "predictions_sha256": sha256(OUTPUT / "predictions.csv"),
        "comparison_sha256": sha256(OUTPUT / "comparison.json"),
        "run_manifest_sha256": sha256(run_manifest_path),
        "usage_files": usage_files,
        "logs": logs,
        "credential_recorded": False,
    }
    path = OUTPUT / "resource_summary.json"
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
