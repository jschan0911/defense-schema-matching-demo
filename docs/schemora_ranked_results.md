# SCHEMORA 전체 매칭 결과 — 순위별 정렬

실제 SCHEMORA 실행에서 반환된 후보 **135건 전체**를 `rank` 오름차순으로 정렬했다.
같은 순위 안에서는 Source 테이블·필드와 Target 테이블·필드순이다.
원본 실행 순서는 [`predictions.csv`](../outputs/reference_demo/predictions.csv)에 보존되어 있다.

표시된 Vector와 BM25는 서로 다른 검색 점수이며 확률이 아니다.
최종 `rank`는 SCHEMORA의 LLM column-ranking 결과다.

## 순위 분포

| 순위 | 후보 수 |
|---:|---:|
| 1 | 28 |
| 2 | 28 |
| 3 | 28 |
| 4 | 26 |
| 5 | 25 |

## 전체 135건

| 순위 | Source | Target | Vector | BM25 | 검색 경로 | 등급 |
|---:|---|---|---:|---:|---|---|
| 1 | `교전규칙.condition` | `작전명령.operation_name` | 0.53794438 | 1.19911718 | bm25_match · embedding_match | High |
| 1 | `교전규칙.priority` | `작전명령.applies_rule` | 0.57027102 | 1.78161919 | bm25_match · bm25_match_syn · embedding_match | High |
| 1 | `교전규칙.requirement` | `작전명령.applies_rule` | 0.65640652 | 1.78161919 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `교전규칙.rule_id` | `작전명령.opord_id` | 0.55904764 | — | embedding_match_syn | Medium |
| 1 | `교전규칙.rule_name` | `작전명령.applies_rule` | 0.50353932 | 1.37127435 | bm25_match · bm25_match_syn · embedding_match | High |
| 1 | `교전규칙.rule_type` | `작전명령.applies_rule` | 0.64042711 | 1.78161919 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `아군_부대.available_firepower` | `적군_부대.available_firepower` | 0.86869001 | 4.17253876 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `아군_부대.operation` | `작전명령.operation_name` | 0.63587856 | 1.04857707 | bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `아군_부대.unit_id` | `적군_부대.unit_id` | 1.00072670 | 3.08132124 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `아군_부대.unit_name` | `적군_부대.unit_name` | 0.95049882 | 3.46120501 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `작전명령.applies_rule` | `교전규칙.rule_id` | 0.59071583 | — | embedding_match · embedding_match_syn | Medium |
| 1 | `작전명령.deadline` | `교전규칙.rule_name` | 0.52003193 | 1.13787580 | bm25_match_syn · embedding_match_syn | High |
| 1 | `작전명령.issued_to_unit` | `아군_부대.unit_id` | 0.77413464 | 1.59374774 | bm25_match · embedding_match · embedding_match_syn | High |
| 1 | `작전명령.mission` | `교전규칙.rule_name` | 0.74617708 | 2.51665211 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `작전명령.operation_name` | `아군_부대.operation` | 0.50248486 | 1.37877619 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `작전명령.operation_type` | `아군_부대.operation` | 0.60334861 | 1.37877619 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `작전명령.opord_id` | `아군_부대.operation` | 0.56391150 | 1.89033604 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `작전명령.target_terrain` | `지형_정보.key_terrain` | 0.76881814 | 2.10961127 | bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `적군_부대.available_firepower` | `아군_부대.available_firepower` | 0.73488468 | 1.77524996 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `적군_부대.operation` | `아군_부대.unit_id` | 0.54483271 | 1.57687104 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `적군_부대.unit_id` | `아군_부대.unit_id` | 0.99985754 | 2.60461187 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `적군_부대.unit_name` | `아군_부대.unit_name` | 0.82306647 | 2.04746222 | bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `지형_정보.elevation` | `작전명령.target_terrain` | 0.54737127 | 1.68026090 | bm25_match · bm25_match_syn · embedding_match | High |
| 1 | `지형_정보.key_terrain` | `작전명령.target_terrain` | 0.54737127 | 1.68026090 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `지형_정보.name` | `작전명령.target_terrain` | 0.59197438 | 1.68026090 | bm25_match · bm25_match_syn · embedding_match_syn | High |
| 1 | `지형_정보.note` | `작전명령.target_terrain` | 0.59435260 | 1.68026090 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `지형_정보.terrain_id` | `작전명령.target_terrain` | 0.53304082 | 1.68026090 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | High |
| 1 | `지형_정보.terrain_type` | `작전명령.target_terrain` | 0.58677554 | 1.68026090 | bm25_match_syn · embedding_match_syn | High |
| 2 | `교전규칙.condition` | `작전명령.issued_to_unit` |  | 1.19911718 | bm25_match | Medium |
| 2 | `교전규칙.priority` | `작전명령.opord_id` | 0.51893330 | 1.14227045 | bm25_match · embedding_match | Medium |
| 2 | `교전규칙.requirement` | `작전명령.issued_to_unit` |  | 1.19911718 | bm25_match | Medium |
| 2 | `교전규칙.rule_id` | `작전명령.applies_rule` | 0.55457079 | 1.37127435 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 2 | `교전규칙.rule_name` | `작전명령.operation_name` |  | 1.78161919 | bm25_match | Medium |
| 2 | `교전규칙.rule_type` | `작전명령.issued_to_unit` |  | 1.19911718 | bm25_match_syn | Medium |
| 2 | `아군_부대.available_firepower` | `지형_정보.elevation` |  | 1.85313499 | bm25_match | Medium |
| 2 | `아군_부대.operation` | `작전명령.mission` | 0.82734811 | 1.68821990 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 2 | `아군_부대.unit_id` | `적군_부대.unit_name` | 0.75240171 | 2.41262794 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 2 | `아군_부대.unit_name` | `적군_부대.unit_id` | 0.66801852 | 1.70761251 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 2 | `작전명령.applies_rule` | `교전규칙.rule_name` | 0.62772745 | 1.13787580 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 2 | `작전명령.deadline` | `교전규칙.priority` | 0.66532469 | 1.34655392 | bm25_match_syn · embedding_match_syn | Medium |
| 2 | `작전명령.issued_to_unit` | `아군_부대.unit_name` | 0.72758150 | — | embedding_match · embedding_match_syn | Medium |
| 2 | `작전명령.mission` | `교전규칙.condition` | 0.52543610 | 1.13787580 | bm25_match_syn · embedding_match_syn | Medium |
| 2 | `작전명령.operation_name` | `적군_부대.operation` | 0.57645714 | — | embedding_match · embedding_match_syn | Medium |
| 2 | `작전명령.operation_type` | `적군_부대.operation` | 0.66589987 | — | embedding_match · embedding_match_syn | Medium |
| 2 | `작전명령.opord_id` | `아군_부대.unit_id` | 0.64565653 | 1.20244694 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 2 | `작전명령.target_terrain` | `지형_정보.terrain_id` | 0.62158549 | 1.13787580 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 2 | `적군_부대.available_firepower` | `교전규칙.condition` |  | 1.15022552 | bm25_match_syn | Medium |
| 2 | `적군_부대.operation` | `아군_부대.unit_name` | 0.51561415 | 1.30421495 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 2 | `적군_부대.unit_id` | `아군_부대.available_firepower` | 0.59818512 | 1.80734015 | bm25_match · bm25_match_syn · embedding_match | Medium |
| 2 | `적군_부대.unit_name` | `아군_부대.unit_id` | 0.78224987 | 2.03560686 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 2 | `지형_정보.elevation` | `교전규칙.priority` |  | 1.32284486 | bm25_match | Medium |
| 2 | `지형_정보.key_terrain` | `교전규칙.requirement` |  | 1.24445295 | bm25_match | Medium |
| 2 | `지형_정보.name` | `아군_부대.unit_name` |  | 1.83568299 | bm25_match_syn | Medium |
| 2 | `지형_정보.note` | `교전규칙.condition` |  | 1.75201690 | bm25_match_syn | Medium |
| 2 | `지형_정보.terrain_id` | `교전규칙.condition` | 0.50626206 | 1.17919350 | bm25_match · bm25_match_syn · embedding_match | Medium |
| 2 | `지형_정보.terrain_type` | `교전규칙.rule_type` |  | 1.83568299 | bm25_match · bm25_match_syn | Medium |
| 3 | `교전규칙.condition` | `작전명령.operation_type` | 0.50301170 | — | embedding_match | Medium |
| 3 | `교전규칙.priority` | `지형_정보.elevation` |  | 1.86004531 | bm25_match_syn | Medium |
| 3 | `교전규칙.requirement` | `작전명령.operation_name` | 0.54860044 | 1.19911718 | bm25_match · embedding_match | Medium |
| 3 | `교전규칙.rule_id` | `작전명령.issued_to_unit` |  | 1.26547945 | bm25_match | Medium |
| 3 | `교전규칙.rule_name` | `작전명령.mission` | 0.50809854 | 1.57869399 | bm25_match · embedding_match | Medium |
| 3 | `교전규칙.rule_type` | `작전명령.mission` |  | 1.19911718 | bm25_match_syn | Medium |
| 3 | `아군_부대.available_firepower` | `적군_부대.unit_id` |  | 1.33605766 | bm25_match | Medium |
| 3 | `아군_부대.operation` | `작전명령.operation_type` | 0.74774563 | 1.05087090 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 3 | `아군_부대.unit_id` | `적군_부대.available_firepower` |  | 1.33605766 | bm25_match | Medium |
| 3 | `아군_부대.unit_name` | `작전명령.issued_to_unit` | 0.61828411 | — | embedding_match · embedding_match_syn | Medium |
| 3 | `작전명령.applies_rule` | `교전규칙.condition` | 0.56979454 | 1.13787580 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 3 | `작전명령.deadline` | `교전규칙.condition` |  | 1.13787580 | bm25_match_syn | Medium |
| 3 | `작전명령.issued_to_unit` | `아군_부대.available_firepower` | 0.63182914 | — | embedding_match · embedding_match_syn | Medium |
| 3 | `작전명령.mission` | `교전규칙.priority` | 0.59789729 | 1.34655392 | bm25_match_syn · embedding_match_syn | Medium |
| 3 | `작전명령.operation_name` | `아군_부대.unit_name` | 0.60530639 | 1.51589847 | bm25_match_syn · embedding_match_syn | Medium |
| 3 | `작전명령.operation_type` | `아군_부대.unit_name` |  | 1.08218789 | bm25_match_syn | Medium |
| 3 | `작전명령.opord_id` | `아군_부대.available_firepower` | 0.62259912 | — | embedding_match_syn | Medium |
| 3 | `작전명령.target_terrain` | `지형_정보.terrain_type` | 0.64701629 | 1.37877619 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 3 | `적군_부대.available_firepower` | `교전규칙.priority` | 0.55396783 | 1.77524996 | bm25_match · embedding_match | Medium |
| 3 | `적군_부대.operation` | `작전명령.target_terrain` | 0.60612011 | 1.29258513 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 3 | `적군_부대.unit_id` | `아군_부대.unit_name` | 0.75880754 | 1.02774096 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 3 | `적군_부대.unit_name` | `아군_부대.operation` | 0.75679868 | 1.35055876 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 3 | `지형_정보.elevation` | `교전규칙.rule_id` |  | 1.24445295 | bm25_match | Medium |
| 3 | `지형_정보.key_terrain` | `교전규칙.rule_id` |  | 1.24445295 | bm25_match | Medium |
| 3 | `지형_정보.name` | `아군_부대.unit_id` |  | 1.02157843 | bm25_match | Medium |
| 3 | `지형_정보.note` | `아군_부대.available_firepower` |  | 1.75201690 | bm25_match_syn | Medium |
| 3 | `지형_정보.terrain_id` | `적군_부대.operation` | 0.54871321 | 1.17919350 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 3 | `지형_정보.terrain_type` | `작전명령.operation_name` |  | 1.47148156 | bm25_match_syn | Medium |
| 4 | `교전규칙.condition` | `작전명령.applies_rule` | 0.61617190 | 1.37127435 | bm25_match · embedding_match | Medium |
| 4 | `교전규칙.priority` | `지형_정보.key_terrain` |  | 1.34584332 | bm25_match | Low |
| 4 | `교전규칙.requirement` | `작전명령.mission` |  | 1.19911718 | bm25_match | Low |
| 4 | `교전규칙.rule_id` | `작전명령.mission` | 0.50527108 | — | embedding_match_syn | Low |
| 4 | `교전규칙.rule_type` | `작전명령.operation_name` | 0.60104179 | 1.19911718 | bm25_match_syn · embedding_match_syn | Medium |
| 4 | `아군_부대.available_firepower` | `교전규칙.condition` |  | 1.13952446 | bm25_match_syn | Low |
| 4 | `아군_부대.operation` | `작전명령.opord_id` | 0.89762557 | 1.47145832 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 4 | `아군_부대.unit_id` | `적군_부대.operation` | 0.53769207 | — | embedding_match_syn | Low |
| 4 | `아군_부대.unit_name` | `작전명령.mission` | 0.58619654 | — | embedding_match · embedding_match_syn | Low |
| 4 | `작전명령.applies_rule` | `교전규칙.priority` | 0.65993482 | 1.34655392 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 4 | `작전명령.deadline` | `아군_부대.available_firepower` |  | 1.13787580 | bm25_match_syn | Low |
| 4 | `작전명령.issued_to_unit` | `아군_부대.operation` | 0.66422659 | 1.89033604 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 4 | `작전명령.mission` | `아군_부대.unit_id` | 0.60917568 | — | embedding_match | Low |
| 4 | `작전명령.operation_name` | `적군_부대.unit_name` | 0.63067758 | 1.51589847 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 4 | `작전명령.operation_type` | `적군_부대.unit_name` |  | 1.28065324 | bm25_match_syn | Low |
| 4 | `작전명령.opord_id` | `적군_부대.unit_id` | 0.68340826 | 1.42296696 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 4 | `작전명령.target_terrain` | `지형_정보.name` | 0.58885580 | 1.13787580 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 4 | `적군_부대.available_firepower` | `교전규칙.rule_id` |  | 1.34860432 | bm25_match | Low |
| 4 | `적군_부대.operation` | `작전명령.operation_type` | 0.68653107 | 2.16978216 | bm25_match_syn · embedding_match_syn | Medium |
| 4 | `적군_부대.unit_id` | `아군_부대.operation` | 0.70617247 | 2.78266954 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 4 | `적군_부대.unit_name` | `작전명령.operation_name` | 0.71839774 | 2.03560686 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 4 | `지형_정보.elevation` | `교전규칙.requirement` |  | 1.32284486 | bm25_match | Low |
| 4 | `지형_정보.key_terrain` | `작전명령.applies_rule` | 0.54233086 | 1.55246329 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 4 | `지형_정보.name` | `작전명령.opord_id` |  | 1.24445295 | bm25_match | Low |
| 4 | `지형_정보.terrain_id` | `아군_부대.unit_id` | 0.51732105 | 1.02157843 | bm25_match · bm25_match_syn · embedding_match | Medium |
| 4 | `지형_정보.terrain_type` | `작전명령.operation_type` |  | 2.07164168 | bm25_match · bm25_match_syn | Low |
| 5 | `교전규칙.condition` | `작전명령.mission` |  | 1.19911718 | bm25_match | Low |
| 5 | `교전규칙.priority` | `지형_정보.name` |  | 1.14227045 | bm25_match | Low |
| 5 | `교전규칙.requirement` | `작전명령.target_terrain` |  | 1.19911718 | bm25_match | Low |
| 5 | `교전규칙.rule_id` | `아군_부대.operation` |  | 1.09921205 | bm25_match | Low |
| 5 | `교전규칙.rule_type` | `작전명령.operation_type` | 0.60159510 | 1.57869399 | bm25_match · bm25_match_syn · embedding_match_syn | Medium |
| 5 | `아군_부대.available_firepower` | `교전규칙.priority` |  | 1.24385738 | bm25_match | Low |
| 5 | `아군_부대.operation` | `적군_부대.operation` | 0.67160642 | 2.08626938 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 5 | `아군_부대.unit_id` | `교전규칙.condition` |  | 1.01007128 | bm25_match | Low |
| 5 | `아군_부대.unit_name` | `작전명령.operation_name` | 0.68163753 | 1.75873399 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 5 | `작전명령.applies_rule` | `교전규칙.rule_type` | 0.61652482 | 1.78658581 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 5 | `작전명령.issued_to_unit` | `적군_부대.unit_id` | 0.80491042 | 1.42296696 | bm25_match · embedding_match · embedding_match_syn | Medium |
| 5 | `작전명령.mission` | `아군_부대.unit_name` | 0.71928889 | — | embedding_match | Low |
| 5 | `작전명령.operation_name` | `지형_정보.name` |  | 1.37877619 | bm25_match · bm25_match_syn | Low |
| 5 | `작전명령.operation_type` | `아군_부대.available_firepower` | 0.51239729 | — | embedding_match | Low |
| 5 | `작전명령.opord_id` | `아군_부대.unit_name` | 0.60683531 | — | embedding_match_syn | Low |
| 5 | `작전명령.target_terrain` | `지형_정보.elevation` | 0.58645999 | — | embedding_match · embedding_match_syn | Low |
| 5 | `적군_부대.available_firepower` | `교전규칙.rule_name` |  | 1.16727936 | bm25_match | Low |
| 5 | `적군_부대.operation` | `작전명령.operation_name` | 0.59433955 | 1.82519841 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 5 | `적군_부대.unit_id` | `작전명령.opord_id` | 0.83417797 | 2.25441217 | bm25_match · bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 5 | `적군_부대.unit_name` | `작전명령.opord_id` | 0.67430782 | 1.76191187 | bm25_match_syn · embedding_match · embedding_match_syn | Medium |
| 5 | `지형_정보.elevation` | `교전규칙.condition` |  | 1.17919350 | bm25_match | Low |
| 5 | `지형_정보.key_terrain` | `작전명령.issued_to_unit` | 0.50885040 | 1.24445295 | bm25_match · embedding_match_syn | Medium |
| 5 | `지형_정보.name` | `적군_부대.operation` | 0.51243913 | 1.17919350 | bm25_match · embedding_match | Medium |
| 5 | `지형_정보.terrain_id` | `작전명령.opord_id` | 0.52002263 | 1.24445295 | bm25_match · embedding_match | Medium |
| 5 | `지형_정보.terrain_type` | `작전명령.mission` |  | 1.24445295 | bm25_match_syn | Low |

## 재생성

```bash
python3 experiments/render_ranked_results.py
```
