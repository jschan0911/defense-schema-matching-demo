#!/usr/bin/env python3
"""Run the five prepared reference-demo benchmarks after explicit key setup."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs" / "reference_demo"
STAGES = [
    "schema_matching/query_document_enrichment.py",
    "schema_matching/clean_and_embed.py",
    "schema_matching/index_and_retrieve.py",
    "schema_matching/table_selection.py",
    "schema_matching/column_rank.py",
]
ADAPTER_MODIFIED_FILES = [
    "utils/llm.py",
    "utils/embedding.py",
    "schema_matching/column_rank.py",
]


def dotenv_has_api_key(path: Path) -> bool:
    if not path.is_file():
        return False
    return any(
        line.strip().startswith("API_KEY=")
        and line.strip().removeprefix("API_KEY=").strip()
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def git_output(path: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(path), *args])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    args = parser.parse_args()
    upstream = args.upstream_root.resolve()
    estimate = json.loads(
        (OUTPUT / "dry_run_estimate.json").read_text(encoding="utf-8")
    )
    manifest = json.loads((OUTPUT / "adapter_manifest.json").read_text(encoding="utf-8"))
    actual_commit = git_output(upstream, "rev-parse", "HEAD").decode().strip()
    actual_patch = git_output(
        upstream, "diff", "--", *ADAPTER_MODIFIED_FILES
    )
    actual_patch_sha256 = hashlib.sha256(actual_patch).hexdigest()
    if actual_commit != manifest["official_commit"]:
        raise SystemExit("pinned SCHEMORA commit no longer matches adapter manifest")
    if actual_patch_sha256 != manifest["adapter_patch_sha256"]:
        raise SystemExit("SCHEMORA compatibility patch no longer matches manifest")
    if not estimate.get("gate_passed"):
        raise SystemExit("reference-demo dry-run gate did not pass")
    if not os.getenv("API_KEY") and not dotenv_has_api_key(upstream / ".env"):
        raise SystemExit(
            "API_KEY is absent. Configure it in the environment or the pinned "
            "upstream .env; never put it in this repository or a command argument."
        )
    if (OUTPUT / "run_manifest.json").exists():
        raise SystemExit("a completed reference-demo run already exists")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(upstream)
    runtime = OUTPUT / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    for benchmark in manifest["benchmarks"]:
        name = benchmark["benchmark"]
        config = upstream / benchmark["config"]
        if not config.is_file():
            raise SystemExit(f"missing adapter config: {config}")
        log_path = runtime / f"{name}.log"
        usage_path = runtime / f"{name}-usage.jsonl"
        env["SCHEMORA_USAGE_LOG"] = str(usage_path.resolve())
        with log_path.open("w", encoding="utf-8") as log:
            for stage in STAGES:
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
                    check=False,
                )
                if result.returncode:
                    raise SystemExit(f"{name} failed at {stage}; inspect {log_path}")
    run_manifest = {
        # datetime.UTC is unavailable in the frozen Python 3.9 environment.
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),  # noqa: UP017
        "official_commit": actual_commit,
        "adapter_patch_sha256": actual_patch_sha256,
        "benchmarks_completed": [
            benchmark["benchmark"] for benchmark in manifest["benchmarks"]
        ],
        "model": manifest["model"],
        "embedding_model": manifest["embedding_model"],
        "prediction_conversion_required": True,
    }
    (OUTPUT / "run_manifest.json").write_text(
        json.dumps(run_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("Five SCHEMORA runs completed. Convert their rank artifacts next.")


if __name__ == "__main__":
    main()
