# 저장 관계 positive-only 대비 SCHEMORA 실제 결과

## 평가 경계

새 링크 관리 화면에서 직접 확인되는 저장 관계 4개만 positive로
사용했다. 아군·적군 `operation` 관계는 방향성 SCHEMORA 결과를 확인하기
위해 두 방향으로 펼쳐 총 5개 directed row를 평가했다.

이 positive 파일은 SCHEMORA 입력이나 프롬프트에 사용하지 않았다. 5개
benchmark의 `mapping.parquet`는 모두 동일한 열 구조의 0행 파일이다.
따라서 본 수치는 정답 주입 없는 사후 평가 결과다.

사진에 보이지 않는 관계를 negative로 간주하지 않았으므로
Precision@K와 F1@K는 계산하지 않는다.

## 관계별 결과

| 저장 관계 | 실제 후보 | 순위 | Vector | BM25 | Top-1 | Top-3 | Top-5 |
|---|---|---:|---:|---:|:---:|:---:|:---:|
| `opord.applies_rule → rule.rule_id` | `작전명령.applies_rule → 교전규칙.rule_id` | 1 | 0.59071583 | — | 포함 | 포함 | 포함 |
| `opord.issued_to_unit → friendly_unit.unit_id` | `작전명령.issued_to_unit → 아군_부대.unit_id` | 1 | 0.77413464 | 1.59374774 | 포함 | 포함 | 포함 |
| `opord.target_terrain → terrain.terrain_id` | `작전명령.target_terrain → 지형_정보.terrain_id` | 2 | 0.62158549 | 1.13787580 | 미포함 | 포함 | 포함 |
| `friendly_unit.operation → enemy_unit.operation` | `아군_부대.operation → 적군_부대.operation` | 5 | 0.67160642 | 2.08626938 | 미포함 | 미포함 | 포함 |
| `enemy_unit.operation → friendly_unit.operation` | 반환되지 않음 | — | — | — | 미포함 | 미포함 | 미포함 |

`target_terrain`의 실제 순서는 다음과 같다.

1. `지형_정보.key_terrain`
2. `지형_정보.terrain_id`
3. `지형_정보.terrain_type`
4. `지형_정보.name`
5. `지형_정보.elevation`

따라서 이전 추천 화면에 표시됐던 `target_terrain → name`은 이번
SCHEMORA 실행에서 4위였고, 저장 관계인 `terrain_id` 2위보다 낮았다.
SCHEMORA의 Vector/BM25 값과 원 데모의 95·47 등의 점수는 의미가 다른
척도이므로 직접 비교하지 않는다.

## UI 표시 기준

`Reference · 관찰값`의 큰 숫자는 원 데모 화면에 표시된 값을 그대로
옮긴 것이다. 화면에서 확인되는 구간은 높음 `90 이상`, 중간 `70–89`,
낮음 `70 미만`이다. 다만 점수 산식, 정규화 및 확률 보정 방식은
공개되지 않았으므로 신뢰확률로 해석하지 않는다.

`SCHEMORA 결과`의 큰 숫자는 `vector score × 100`을 반올림한
가독성용 표시값이다. 후보 순서는 이 숫자순이 아니라 최종 LLM
column-ranking 순서다. 표시 등급은 다음의 결정론적 검토 규칙이다.

- 높음: 1위이면서 embedding과 BM25가 모두 지지
- 중간: 1–3위이거나 두 검색 방식이 모두 지지
- 낮음: 나머지 반환 후보

표시 점수와 등급은 성능 지표나 calibration된 confidence가 아니다.
원 vector, BM25, 쿼리 내 순위는 각 후보의 `추천 근거`에서 별도로
확인한다.

## Positive-only recovery

| K | 개념 관계·한 방향 이상 | 개념 관계·모든 방향 | Directed |
|---:|---:|---:|---:|
| 1 | 2/4 (0.50) | 2/4 (0.50) | 2/5 (0.40) |
| 3 | 3/4 (0.75) | 3/4 (0.75) | 3/5 (0.60) |
| 5 | 4/4 (1.00) | 3/4 (0.75) | 4/5 (0.80) |

양방향 관계를 하나의 개념 링크로 보고 어느 한 방향의 복구를
인정하면 Conceptual Recall@5는 1.00이다. 두 방향을 모두 요구하면
0.75이며, directed 기준은 0.80이다.

## 실행 환경과 자원

- 공식 SCHEMORA commit:
  `1339fedf8113fc3746d5664f1453248e47ee310c`
- 고정 호환성·telemetry patch SHA-256:
  `491efc93e9672ed13387ccba6feedbfa6014886a4239de6dccfa38cdd663f7d0`
- LLM: `gpt-5-nano`
- embedding: `text-embedding-3-large`
- benchmark: 5개
- prediction: 135행
- chat 호출: 346회
- embedding 호출: 420회
- 전체 측정 토큰: 348,253
- 단계 실행 시간 합계: 903.04초
- 측정 토큰 기반 추정 비용: USD 0.058650

자세한 후보와 각 쿼리의 Top-5는
`outputs/reference_demo/comparison.json`, 전체 UI 입력은
`outputs/reference_demo/predictions.csv`, 자원 및 파일 해시는
`outputs/reference_demo/resource_summary.json`에 기록했다.
