#!/usr/bin/env python3
"""Complete-gold, no-match-aware ranked evaluation."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
Source = tuple[str, str]
Target = tuple[str, str]


def load_gold(
    path: Path,
) -> tuple[dict[Source, set[Target]], dict[Source, dict[str, str]]]:
    truth: dict[Source, set[Target]] = defaultdict(set)
    metadata: dict[Source, dict[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source = (row["source_table"], row["source_column"])
            truth.setdefault(source, set())
            metadata[source] = {
                "mapping_type": row["mapping_type"],
                "difficulty": row["difficulty"],
            }
            if row["target_object_type"]:
                truth[source].add((row["target_object_type"], row["target_property"]))
    return dict(truth), metadata


def load_predictions(path: Path) -> dict[Source, list[Target]]:
    predictions: dict[Source, list[tuple[int, Target]]] = defaultdict(list)
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source = (row["source_table"], row["source_column"])
            target = (row["target_object_type"], row["target_property"])
            predictions[source].append((int(row["rank"]), target))
    return {
        source: [target for _, target in sorted(values)]
        for source, values in predictions.items()
    }


def dcg(relevances: list[int]) -> float:
    return sum(value / math.log2(index + 2) for index, value in enumerate(relevances))


def metrics_at_k(
    truth: dict[Source, set[Target]],
    predictions: dict[Source, list[Target]],
    k: int,
) -> dict[str, float | int]:
    answerable = [source for source, targets in truth.items() if targets]
    no_match = [source for source, targets in truth.items() if not targets]
    hit_rates: list[float] = []
    recalls: list[float] = []
    any_hits: list[float] = []
    correct_pairs = 0
    gold_pairs = sum(len(truth[source]) for source in answerable)
    predicted_pairs = 0
    ndcgs: list[float] = []
    aps: list[float] = []
    for source, gold in truth.items():
        ranked = predictions.get(source, [])[:k]
        predicted_pairs += len(ranked)
        if not gold:
            hit_rates.append(float(not ranked))
            continue
        relevant = [int(target in gold) for target in ranked]
        found = len(set(ranked) & gold)
        correct_pairs += found
        any_hit = float(found > 0)
        hit_rates.append(any_hit)
        any_hits.append(any_hit)
        recalls.append(found / len(gold))
        ideal = [1] * min(len(gold), k)
        ndcgs.append(dcg(relevant) / dcg(ideal) if ideal else 0.0)
        hits = 0
        precision_sum = 0.0
        for index, value in enumerate(relevant, start=1):
            if value:
                hits += 1
                precision_sum += hits / index
        aps.append(precision_sum / min(len(gold), k))
    precision = correct_pairs / predicted_pairs if predicted_pairs else 0.0
    micro_recall = correct_pairs / gold_pairs if gold_pairs else 0.0
    f1 = (
        2 * precision * micro_recall / (precision + micro_recall)
        if precision + micro_recall
        else 0.0
    )
    no_match_correct = sum(not predictions.get(source, [])[:k] for source in no_match)
    return {
        "k": k,
        "hit_rate": mean(hit_rates) if hit_rates else 0.0,
        "macro_recall": mean(recalls) if recalls else 0.0,
        "any_hit": mean(any_hits) if any_hits else 0.0,
        "micro_pair_recall": micro_recall,
        "precision": precision,
        "pair_f1": f1,
        "ndcg": mean(ndcgs) if ndcgs else 0.0,
        "map": mean(aps) if aps else 0.0,
        "correct_pairs": correct_pairs,
        "gold_pairs": gold_pairs,
        "predicted_pairs": predicted_pairs,
        "no_match_false_recommendations": len(no_match) - no_match_correct,
        "no_match_detection_rate": (
            no_match_correct / len(no_match) if no_match else 0.0
        ),
    }


def breakdown(
    truth: dict[Source, set[Target]],
    predictions: dict[Source, list[Target]],
    metadata: dict[Source, dict[str, str]],
    field: str,
) -> dict[str, dict[str, float | int]]:
    groups: dict[str, dict[Source, set[Target]]] = defaultdict(dict)
    for source, targets in truth.items():
        groups[metadata[source][field]][source] = targets
    result: dict[str, dict[str, float | int]] = {}
    for name, group_truth in sorted(groups.items()):
        values = metrics_at_k(group_truth, predictions, 5)
        result[name] = {
            "sources": len(group_truth),
            "macro_recall_at_5": values["macro_recall"],
            "any_hit_at_5": values["any_hit"],
            "no_match_detection_rate": values["no_match_detection_rate"],
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=ROOT / "data" / "gold_mapping.csv")
    parser.add_argument(
        "--predictions", type=Path, default=ROOT / "outputs" / "predictions.csv"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "outputs" / "metrics.json"
    )
    args = parser.parse_args()
    truth, metadata = load_gold(args.gold)
    predictions = load_predictions(args.predictions)
    metrics = {
        "scope": {
            "sources": len(truth),
            "answerable_sources": sum(bool(targets) for targets in truth.values()),
            "no_match_sources": sum(not targets for targets in truth.values()),
            "prediction_sources": len(predictions),
            "gold_status": "complete_draft_not_independently_reviewed",
        },
        "definitions": {
            "hit_rate": (
                "all-source success: any gold hit for answerable sources and "
                "no returned candidate for gold no-match sources"
            ),
            "macro_recall": "mean fraction of gold pairs found over answerable sources",
            "any_hit": "fraction of answerable sources with at least one gold hit",
            "precision": "correct gold pairs divided by all returned pairs",
            "no_match": (
                "SCHEMORA has no explicit abstention; an empty returned list after "
                "fixed upstream thresholds is treated as no-match"
            ),
        },
        "at_k": {str(k): metrics_at_k(truth, predictions, k) for k in (1, 3, 5)},
        "by_difficulty": breakdown(truth, predictions, metadata, "difficulty"),
        "by_mapping_type": breakdown(truth, predictions, metadata, "mapping_type"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(metrics, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
