#!/usr/bin/env python3
"""Run the already-prepared pinned SCHEMORA checkout exactly once."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = "defense-usaspending-ocds-v1"


def dotenv_has_api_key(path: Path) -> bool:
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if (
            stripped.startswith("API_KEY=")
            and stripped.removeprefix("API_KEY=").strip()
        ):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument(
        "--dry-run-estimate",
        type=Path,
        default=ROOT / "outputs" / "dry_run_estimate.json",
    )
    parser.add_argument(
        "--usage-log",
        type=Path,
        default=ROOT / "outputs" / "runtime" / "usage.jsonl",
    )
    parser.add_argument(
        "--run-log",
        type=Path,
        default=ROOT / "outputs" / "runtime" / "run.log",
    )
    args = parser.parse_args()

    estimate = json.loads(args.dry_run_estimate.read_text(encoding="utf-8"))
    if not estimate.get("gate_passed"):
        raise SystemExit("dry-run gate did not pass")
    upstream = args.upstream_root.resolve()
    if not os.getenv("API_KEY") and not dotenv_has_api_key(upstream / ".env"):
        raise SystemExit(
            "API_KEY is not set in the process environment or the upstream "
            ".env. Do not commit it or pass it as a command-line argument."
        )
    if (ROOT / "outputs" / "run_manifest.json").exists():
        raise SystemExit("a completed run manifest already exists; repeats are blocked")

    config = upstream / f"config_{BENCHMARK}.toml"
    if not config.exists():
        raise SystemExit("adapter output is missing; run schemora_adapter.py first")
    args.usage_log.parent.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(upstream)
    env["SCHEMORA_USAGE_LOG"] = str(args.usage_log.resolve())

    stages = [
        "schema_matching/query_document_enrichment.py",
        "schema_matching/clean_and_embed.py",
        "schema_matching/index_and_retrieve.py",
        "schema_matching/table_selection.py",
        "schema_matching/column_rank.py",
    ]
    with args.run_log.open("w", encoding="utf-8") as log:
        for stage in stages:
            command = [
                "/usr/bin/time",
                "-lp",
                str(args.python.resolve()),
                stage,
                "--config",
                config.name,
            ]
            log.write(f"STAGE {stage}\n")
            log.flush()
            result = subprocess.run(
                command,
                cwd=upstream,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
            if result.returncode:
                raise SystemExit(f"SCHEMORA stage failed: {stage}")
    print("SCHEMORA stages completed; collect and evaluate the artifact next.")


if __name__ == "__main__":
    main()
