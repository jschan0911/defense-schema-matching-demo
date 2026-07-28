#!/usr/bin/env python3
"""Produce deterministic, reviewable error categories from Top-K output."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from evaluate import load_gold, load_predictions


ROOT = Path(__file__).resolve().parents[1]


def ref(value: tuple[str, str]) -> str:
    return f"{value[0]}.{value[1]}"


def classify(
    source: tuple[str, str],
    gold: set[tuple[str, str]],
    ranked: list[tuple[str, str]],
) -> str:
    name = source[1].lower()
    if not gold and ranked:
        return "forced_match_on_no_match"
    found = set(ranked) & gold
    if len(gold) > 1 and found and found != gold:
        return "partial_multi_target_recall"
    if any(token in name for token in ("code", "uei", "cage", "naics", "piid")):
        return "abbreviation_failure"
    if any(
        target[1].split(".")[-1] in {"id", "name", "description", "details"}
        for target in ranked
    ):
        return "overly_generic_property"
    if ranked and gold and ranked[0][0] not in {target[0] for target in gold}:
        return "wrong_object_context"
    if any(token in name for token in ("date", "amount", "value", "code")):
        return "datatype_mismatch"
    if ranked:
        return "lexical_confusion"
    return "insufficient_description"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=ROOT / "data" / "gold_mapping.csv")
    parser.add_argument(
        "--predictions", type=Path, default=ROOT / "outputs" / "predictions.csv"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "error_analysis.csv",
    )
    args = parser.parse_args()
    truth, metadata = load_gold(args.gold)
    predictions = load_predictions(args.predictions)
    rows: list[dict[str, str]] = []
    for source, gold in sorted(truth.items()):
        ranked = predictions.get(source, [])[:5]
        found = set(ranked) & gold
        correct_no_match = not gold and not ranked
        if (gold and found == gold) or correct_no_match:
            continue
        error_type = classify(source, gold, ranked)
        rows.append(
            {
                "source": ref(source),
                "gold": "|".join(sorted(map(ref, gold))) or "NO_MATCH",
                "top_k": "|".join(map(ref, ranked)) or "EMPTY",
                "error_type": error_type,
                "cause_analysis": (
                    "Deterministic first-pass category based on gold coverage, "
                    "source naming, and target object context; requires human review."
                ),
                "improvement_potential": (
                    "Review metadata descriptions, target coverage, retrieval "
                    "thresholds, and no-match policy before changing the model."
                ),
                "difficulty": metadata[source]["difficulty"],
                "mapping_type": metadata[source]["mapping_type"],
                "review_status": "machine_categorized_pending_human_review",
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "source",
        "gold",
        "top_k",
        "error_type",
        "cause_analysis",
        "improvement_potential",
        "difficulty",
        "mapping_type",
        "review_status",
    ]
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} error rows to {args.output}")


if __name__ == "__main__":
    main()
