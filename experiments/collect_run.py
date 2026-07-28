#!/usr/bin/env python3
"""Collect usage, resources, dependency state, hashes, and a portable manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize_usage(path: Path) -> dict[str, object]:
    totals: dict[tuple[str, str], dict[str, int | str]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            key = (str(row["kind"]), str(row["model"]))
            total = totals.setdefault(
                key,
                {
                    "kind": key[0],
                    "model": key[1],
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                },
            )
            for field in ("calls", "input_tokens", "output_tokens"):
                increment = 1 if field == "calls" else int(row.get(field, 0))
                total[field] = int(total[field]) + increment
    rows = sorted(totals.values(), key=lambda item: (item["kind"], item["model"]))
    cost = 0.0
    for row in rows:
        if row["kind"] == "chat" and row["model"] == "gpt-5-nano":
            cost += int(row["input_tokens"]) / 1_000_000 * 0.05
            cost += int(row["output_tokens"]) / 1_000_000 * 0.40
        elif row["kind"] == "embedding" and row["model"] == "text-embedding-3-large":
            cost += int(row["input_tokens"]) / 1_000_000 * 0.13
    return {"by_kind_model": rows, "estimated_total_cost_usd": cost}


def resources(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8", errors="replace")
    real = [float(value) for value in re.findall(r"(?m)^\s*([0-9.]+)\s+real\s*$", text)]
    rss = [
        float(value)
        for value in re.findall(
            r"(?m)^\s*([0-9]+)\s+maximum resident set size\s*$", text
        )
    ]
    return {
        "elapsed_seconds": sum(real),
        "stage_count_measured": len(real),
        "peak_rss_mb": max(rss) / (1024 * 1024) if rss else 0.0,
    }


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--usage-log", type=Path, required=True)
    parser.add_argument("--run-log", type=Path, required=True)
    parser.add_argument("--upstream-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    usage = summarize_usage(args.usage_log)
    resource_usage = resources(args.run_log)
    freeze = subprocess.check_output(
        [str(args.python.resolve()), "-m", "pip", "freeze"],
        text=True,
    )
    freeze_path = ROOT / "outputs" / "dependency_freeze.txt"
    freeze_path.write_text(freeze, encoding="utf-8")
    upstream_commit = subprocess.check_output(
        ["git", "-C", str(args.upstream_root), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    manifest = {
        "run_id": "defense_usaspending_ocds_gpt5_nano_v1",
        "claim": "official-code adaptation",
        "executions": 1,
        "official_repository": "https://github.com/schemorapaper/schemora",
        "official_commit": upstream_commit,
        "model": "gpt-5-nano",
        "embedding_model": "text-embedding-3-large",
        "usage": usage,
        "resources": resource_usage,
        "environment": {
            "os": platform.platform(),
            "python": subprocess.check_output(
                [str(args.python.resolve()), "--version"],
                text=True,
                stderr=subprocess.STDOUT,
            ).strip(),
        },
        "files": {
            "artifact": {
                "path": "not_distributed_upstream_runtime_artifact",
                "sha256": sha256(args.artifact),
            },
            "predictions": {
                "path": "outputs/predictions.csv",
                "sha256": sha256(ROOT / "outputs" / "predictions.csv"),
            },
            "usage_log": {
                "path": relative(args.usage_log),
                "sha256": sha256(args.usage_log),
            },
            "run_log": {"path": relative(args.run_log), "sha256": sha256(args.run_log)},
            "dependency_freeze": {
                "path": relative(freeze_path),
                "sha256": sha256(freeze_path),
            },
            "source_schema": {
                "path": "data/source_schema.csv",
                "sha256": sha256(ROOT / "data" / "source_schema.csv"),
            },
            "target_ontology": {
                "path": "data/target_ontology.csv",
                "sha256": sha256(ROOT / "data" / "target_ontology.csv"),
            },
            "gold_mapping": {
                "path": "data/gold_mapping.csv",
                "sha256": sha256(ROOT / "data" / "gold_mapping.csv"),
            },
        },
        "limitations": [
            "single run only",
            "gpt-5-nano replaces the paper model",
            "gold is complete draft but not independently reviewed",
            "SCHEMORA has no explicit no-match decision",
        ],
    }
    output = ROOT / "outputs" / "run_manifest.json"
    output.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (ROOT / "outputs" / "usage.json").write_text(
        json.dumps(usage, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
