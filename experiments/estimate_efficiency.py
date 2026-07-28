#!/usr/bin/env python3
"""Separate measured model resources from transparent human-effort estimates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "outputs" / "run_manifest.json"
    )
    parser.add_argument(
        "--metrics", type=Path, default=ROOT / "outputs" / "metrics.json"
    )
    parser.add_argument("--review-seconds-per-candidate", type=float, default=20.0)
    parser.add_argument("--human-hourly-cost-usd", type=float, default=50.0)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    source_count = int(metrics["scope"]["sources"])
    target_count = 108
    elapsed = float(manifest["resources"]["elapsed_seconds"])
    model_cost = float(manifest["usage"]["estimated_total_cost_usd"])
    at1 = metrics["at_k"]["1"]
    at5 = metrics["at_k"]["5"]
    full_pairs = source_count * target_count
    top1_candidates = int(at1["predicted_pairs"])
    top5_candidates = int(at5["predicted_pairs"])
    correct_pairs = int(at5["correct_pairs"])
    human_rate = args.human_hourly_cost_usd / 3600
    result = {
        "measured": {
            "source_properties": source_count,
            "target_properties": target_count,
            "elapsed_seconds": elapsed,
            "model_api_cost_usd": model_cost,
            "seconds_per_source_property": elapsed / source_count,
            "api_cost_per_source_property_usd": model_cost / source_count,
            "schema_scan_cost_usd": model_cost,
            "cost_per_correct_pair_at_5_usd": (
                model_cost / correct_pairs if correct_pairs else None
            ),
            "top_1_review_candidates": top1_candidates,
            "top_5_review_candidates": top5_candidates,
            "full_cartesian_pairs": full_pairs,
            "candidate_reduction_at_5": 1 - top5_candidates / full_pairs,
        },
        "estimated_not_measured": {
            "assumption_review_seconds_per_candidate": args.review_seconds_per_candidate,
            "assumption_human_hourly_cost_usd": args.human_hourly_cost_usd,
            "top_1_review_seconds": top1_candidates * args.review_seconds_per_candidate,
            "top_5_review_seconds": top5_candidates * args.review_seconds_per_candidate,
            "full_manual_review_seconds": full_pairs
            * args.review_seconds_per_candidate,
            "top_5_human_review_cost_usd": (
                top5_candidates * args.review_seconds_per_candidate * human_rate
            ),
            "full_manual_human_cost_usd": (
                full_pairs * args.review_seconds_per_candidate * human_rate
            ),
            "top_5_time_reduction_vs_full_manual": 1 - top5_candidates / full_pairs,
            "combined_model_plus_estimated_top_5_human_cost_usd": (
                model_cost
                + top5_candidates * args.review_seconds_per_candidate * human_rate
            ),
        },
        "unavailable": {
            "actual_ui_review_time": (
                "No human review session has been timed; estimates are not empirical."
            ),
            "data_research_and_annotation_labor": (
                "Not continuously timed; no fabricated duration is reported."
            ),
        },
    }
    output = ROOT / "outputs" / "efficiency.json"
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
