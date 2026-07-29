from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "reference_demo" / "predictions.csv"
SORTED_CSV = ROOT / "outputs" / "reference_demo" / "predictions_by_rank.csv"
MARKDOWN = ROOT / "docs" / "schemora_ranked_results.md"


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def sort_key(row: dict[str, str]) -> tuple[int, str, str, str, str]:
    return (
        int(row["rank"]),
        row["source_table"],
        row["source_column"],
        row["target_object_type"],
        row["target_property"],
    )


def main() -> None:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = sorted(reader, key=sort_key)
        fieldnames = reader.fieldnames

    if not rows or fieldnames is None:
        raise SystemExit(f"No prediction rows found in {SOURCE}")

    with SORTED_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(int(row["rank"]) for row in rows)
    lines = [
        "# SCHEMORA 전체 매칭 결과 — 순위별 정렬",
        "",
        f"실제 SCHEMORA 실행에서 반환된 후보 **{len(rows)}건 전체**를 "
        "`rank` 오름차순으로 정렬했다.",
        "같은 순위 안에서는 Source 테이블·필드와 Target 테이블·필드순이다.",
        "원본 실행 순서는 "
        "[`predictions.csv`](../outputs/reference_demo/predictions.csv)에 보존되어 있다.",
        "",
        "표시된 Vector와 BM25는 서로 다른 검색 점수이며 확률이 아니다.",
        "최종 `rank`는 SCHEMORA의 LLM column-ranking 결과다.",
        "",
        "## 순위 분포",
        "",
        "| 순위 | 후보 수 |",
        "|---:|---:|",
    ]
    lines.extend(f"| {rank} | {counts[rank]} |" for rank in sorted(counts))
    lines.extend(
        [
            "",
            "## 전체 135건",
            "",
            "| 순위 | Source | Target | Vector | BM25 | 검색 경로 | 등급 |",
            "|---:|---|---|---:|---:|---|---|",
        ]
    )

    for row in rows:
        source = f"`{row['source_table']}.{row['source_column']}`"
        target = f"`{row['target_object_type']}.{row['target_property']}`"
        bm25 = row["bm25_score"] or "—"
        retrieval = markdown_cell(row["retrieval_methods"].replace("|", " · "))
        lines.append(
            f"| {row['rank']} | {source} | {target} | "
            f"{row['vector_score']} | {bm25} | {retrieval} | "
            f"{markdown_cell(row['rank_grade'])} |"
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

    print(f"Wrote {len(rows)} rows to {SORTED_CSV.relative_to(ROOT)}")
    print(f"Wrote {len(rows)} rows to {MARKDOWN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
