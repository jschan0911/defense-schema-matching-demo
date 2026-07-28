#!/usr/bin/env python3
"""Compare visible reference pairs with real SCHEMORA output without score conflation."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "reference_demo_reconstruction"
PREDICTIONS = ROOT / "outputs" / "reference_demo" / "predictions.csv"
OUTPUT = ROOT / "outputs" / "reference_demo" / "comparison.json"
Pair = tuple[str, str, str, str]
Source = tuple[str, str]


def reference_rows() -> list[dict[str, object]]:
    return json.loads(
        (CASE / "observable_reference.json").read_text(encoding="utf-8")
    )["candidates"]


def pair_from_reference(row: dict[str, object]) -> Pair:
    return (
        str(row["from_table"]),
        str(row["from_field"]),
        str(row["to_table"]),
        str(row["to_field"]),
    )


def load_schemora(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def pair_from_schemora(row: dict[str, str]) -> Pair:
    return (
        row["source_table"],
        row["source_column"],
        row["target_object_type"],
        row["target_property"],
    )


def rank_correlation(
    reference: list[dict[str, object]], schemora: list[dict[str, str]]
) -> dict[str, object]:
    ref_by_source: dict[Source, list[Pair]] = defaultdict(list)
    for row in reference:
        pair = pair_from_reference(row)
        ref_by_source[pair[:2]].append(pair)
    sch_rank = {pair_from_schemora(row): int(row["rank"]) for row in schemora}
    correlations = []
    eligible_sources = 0
    for pairs in ref_by_source.values():
        common = [pair for pair in pairs if pair in sch_rank]
        if len(common) < 2:
            continue
        eligible_sources += 1
        ref_ranks = list(range(1, len(common) + 1))
        sch_ranks = [sch_rank[pair] for pair in common]
        ref_mean = mean(ref_ranks)
        sch_mean = mean(sch_ranks)
        numerator = sum(
            (left - ref_mean) * (right - sch_mean)
            for left, right in zip(ref_ranks, sch_ranks)
        )
        left_norm = sum((value - ref_mean) ** 2 for value in ref_ranks) ** 0.5
        right_norm = sum((value - sch_mean) ** 2 for value in sch_ranks) ** 0.5
        if left_norm and right_norm:
            correlations.append(numerator / (left_norm * right_norm))
    return {
        "method": "Spearman correlation (Pearson correlation of within-source ordinal ranks)",
        "eligible_sources_with_two_or_more_common_candidates": eligible_sources,
        "mean_correlation": mean(correlations) if correlations else None,
        "warning": "global reference scores are not compared with per-query SCHEMORA scores",
    }


def main() -> None:
    reference = reference_rows()
    schemora = load_schemora(PREDICTIONS)
    feature_parity = json.loads(
        (CASE / "feature_parity.json").read_text(encoding="utf-8")
    )
    gold_manifest = json.loads(
        (CASE / "gold_manifest.json").read_text(encoding="utf-8")
    )
    result: dict[str, object] = {
        "comparison_claim": (
            "screenshot-guided observable baseline versus pinned SCHEMORA implementation"
        ),
        "reference_scope": {
            "visible_candidates": len(reference),
            "page_reported_total": 16,
            "hidden_candidates_reconstructed": 0,
        },
        "score_comparison": {
            "performed": False,
            "reason": (
                "original-demo scores and SCHEMORA vector/BM25 scores have unknown, "
                "different semantics"
            ),
        },
        "feature_parity": feature_parity,
        "gold_metrics": {
            "publishable": bool(
                gold_manifest["complete_for_all_27_source_fields"]
                and gold_manifest["independently_reviewed"]
            ),
            "recall_precision_f1": None,
            "reason": (
                "withheld until a complete, independently reviewed 27-source gold "
                "mapping is frozen"
            ),
        },
    }
    if not schemora:
        result["schemora_status"] = "not_run"
        result["candidate_similarity"] = None
        result["rank_similarity"] = None
    else:
        reference_set = {pair_from_reference(row) for row in reference}
        reference_sources = {pair[:2] for pair in reference_set}
        at_k: dict[str, object] = {}
        for k in (1, 3, 5):
            schemora_set = {
                pair_from_schemora(row)
                for row in schemora
                if int(row["rank"]) <= k
                and pair_from_schemora(row)[:2] in reference_sources
            }
            overlap = reference_set & schemora_set
            union = reference_set | schemora_set
            at_k[str(k)] = {
                "visible_reference_recovery": len(overlap) / len(reference_set),
                "jaccard": len(overlap) / len(union) if union else 0.0,
                "overlap_count": len(overlap),
                "reference_visible_count": len(reference_set),
                "schemora_candidates_for_visible_sources": len(schemora_set),
            }
        result["schemora_status"] = "loaded"
        result["candidate_similarity"] = {"at_k": at_k}
        result["rank_similarity"] = rank_correlation(reference, schemora)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
