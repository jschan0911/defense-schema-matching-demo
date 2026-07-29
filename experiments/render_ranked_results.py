from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "reference_demo" / "predictions.csv"
GLOBAL_CSV = (
    ROOT / "outputs" / "reference_demo" / "predictions_global_priority.csv"
)
MARKDOWN = ROOT / "docs" / "schemora_ranked_results.md"
RRF_K = 60
SIGNAL_COUNT = 3


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def descending_average_ranks(
    rows: list[dict[str, str]],
    indices: list[int],
    field: str,
) -> dict[int, float]:
    """Return query-local descending ranks, preserving equal-score ties."""
    scored = [(index, float(rows[index][field])) for index in indices if rows[index][field]]
    scored.sort(key=lambda item: item[1], reverse=True)

    ranks: dict[int, float] = {}
    cursor = 0
    while cursor < len(scored):
        end = cursor + 1
        while end < len(scored) and scored[end][1] == scored[cursor][1]:
            end += 1
        average_rank = ((cursor + 1) + end) / 2
        for index, _ in scored[cursor:end]:
            ranks[index] = average_rank
        cursor = end
    return ranks


def format_rank(value: str) -> str:
    if not value:
        return "—"
    number = float(value)
    return str(int(number)) if number.is_integer() else f"{number:.1f}"


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        original_fields = reader.fieldnames

    if not rows or original_fields is None:
        raise SystemExit(f"No prediction rows found in {SOURCE}")

    query_groups: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        query_groups[(row["source_table"], row["source_column"])].append(index)

    vector_ranks: dict[int, float] = {}
    bm25_ranks: dict[int, float] = {}
    for indices in query_groups.values():
        vector_ranks.update(descending_average_ranks(rows, indices, "vector_score"))
        bm25_ranks.update(descending_average_ranks(rows, indices, "bm25_score"))

    theoretical_max = SIGNAL_COUNT / (RRF_K + 1)
    enriched: list[dict[str, str]] = []
    for index, row in enumerate(rows):
        llm_rank = float(row["rank"])
        signal_ranks = [llm_rank]
        if index in vector_ranks:
            signal_ranks.append(vector_ranks[index])
        if index in bm25_ranks:
            signal_ranks.append(bm25_ranks[index])

        rrf_raw = sum(1 / (RRF_K + rank) for rank in signal_ranks)
        priority_score = 100 * rrf_raw / theoretical_max
        enriched.append(
            {
                "_rrf_raw": f"{rrf_raw:.15f}",
                "global_priority_score": f"{priority_score:.6f}",
                "llm_query_rank": format_rank(str(llm_rank)),
                "vector_query_rank": format_rank(
                    str(vector_ranks[index]) if index in vector_ranks else ""
                ),
                "bm25_query_rank": format_rank(
                    str(bm25_ranks[index]) if index in bm25_ranks else ""
                ),
                "contributing_signals": str(len(signal_ranks)),
                **row,
            }
        )

    enriched.sort(
        key=lambda row: (
            -float(row["_rrf_raw"]),
            int(row["rank"]),
            -int(row["contributing_signals"]),
            row["source_table"],
            row["source_column"],
            row["target_object_type"],
            row["target_property"],
        )
    )

    previous_score: str | None = None
    for display_order, row in enumerate(enriched, start=1):
        score = row["_rrf_raw"]
        if score != previous_score:
            priority_rank = display_order
            previous_score = score
        row["display_order"] = str(display_order)
        row["global_priority_rank"] = str(priority_rank)

    metadata_fields = [
        "display_order",
        "global_priority_rank",
        "global_priority_score",
        "llm_query_rank",
        "vector_query_rank",
        "bm25_query_rank",
        "contributing_signals",
    ]
    with GLOBAL_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=metadata_fields + original_fields,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(enriched)

    lines = [
        "# SCHEMORA 전체 매칭 결과 — RRF 전역 검토 우선순위",
        "",
        f"실제 SCHEMORA 실행에서 반환된 후보 **{len(enriched)}건 전체**를 "
        "전역 검토 우선순위로 배열했다.",
        "이 순서는 정확도·관련도·신뢰도의 전역 확률이 아니라, 서로 다른 Source "
        "질의의 후보를 사람이 먼저 검토할 순서를 정하기 위한 파생 지표다.",
        "",
        "## 산정 방식",
        "",
        "Vector와 BM25의 원점수는 단위와 분포가 달라 직접 더하거나 min-max "
        "정규화하지 않았다. 각 Source 필드 질의 안에서 다음 세 순위만 사용했다.",
        "",
        "1. SCHEMORA 최종 LLM column-ranking 순위",
        "2. Vector score 내림차순의 질의 내 순위",
        "3. BM25 score 내림차순의 질의 내 순위",
        "",
        "세 순위는 동일 가중치의 Reciprocal Rank Fusion(RRF)으로 결합했다.",
        "원 논문의 고정값과 같은 `k=60`을 사용했다.",
        "",
        "```text",
        "RRF = Σ 1 / (60 + 질의 내 순위)",
        "전역 검토 우선순위 점수 = RRF / (3 / 61) × 100",
        "```",
        "",
        "해당 검색 경로에 후보가 없어서 Vector 또는 BM25 값이 비어 있으면 그 "
        "신호의 기여를 0으로 둔다. 이는 결측치를 평균값으로 보충하는 것보다 "
        "보수적이다. 학습된 가중치나 저장 링크 정답은 사용하지 않았다.",
        "동점 후보는 같은 검토 순위를 가지며, 표 안의 동점 표시 순서만 Source와 "
        "Target 이름으로 고정했다.",
        "",
        "- [RRF 원 논문(Cormack, Clarke, Büttcher, SIGIR 2009)]"
        "(https://doi.org/10.1145/1571941.1572114)",
        "- [원본 실행 순서 CSV](../outputs/reference_demo/predictions.csv)",
        "- [RRF 전역 검토 우선순위 CSV]"
        "(../outputs/reference_demo/predictions_global_priority.csv)",
        "",
        "## 전체 135건",
        "",
        "| 표시 순번 | 검토 순위 | 우선순위 점수 | Source | Target | LLM 질의 순위 | "
        "Vector 원점수·질의 순위 | BM25 원점수·질의 순위 | 신호 수 |",
        "|---:|---:|---:|---|---|---:|---:|---:|---:|",
    ]

    for row in enriched:
        source = f"`{row['source_table']}.{row['source_column']}`"
        target = f"`{row['target_object_type']}.{row['target_property']}`"
        vector = (
            f"{row['vector_score']} · #{row['vector_query_rank']}"
            if row["vector_score"]
            else "—"
        )
        bm25 = (
            f"{row['bm25_score']} · #{row['bm25_query_rank']}"
            if row["bm25_score"]
            else "—"
        )
        lines.append(
            f"| {row['display_order']} | {row['global_priority_rank']} | "
            f"{row['global_priority_score']} | {source} | {target} | "
            f"#{row['llm_query_rank']} | {vector} | {bm25} | "
            f"{row['contributing_signals']}/3 |"
        )

    lines.extend(
        [
            "",
            "## 재생성",
            "",
            "```bash",
            "python3 experiments/render_ranked_results.py",
            "```",
            "",
        ]
    )
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {len(enriched)} rows to {GLOBAL_CSV.relative_to(ROOT)}")
    print(f"Wrote {len(enriched)} rows to {MARKDOWN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
