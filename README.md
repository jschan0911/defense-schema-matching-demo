# 합성 C2 데이터 SCHEMORA 실증

사용자가 제공한 데모 화면에서 확인 가능한 5개 합성 데이터셋을
SCHEMORA 입력으로 변환하고, 실제 저장 링크와 SCHEMORA Top-K 결과를
비교하는 단일 실증 저장소다.

이 저장소는 원 데모 제품이나 내부 알고리즘을 재현한다고 주장하지
않는다. 공개되지 않은 parser, graph builder, validator, 모델, 프롬프트,
점수 보정 및 온톨로지 mutation 로직은 구현 범위 밖이다. 보고 명칭은
다음으로 고정한다.

> 화면에서 관찰 가능한 기준선 대비 고정 SCHEMORA 구현

## 포함 범위

- 화면에서 전사한 합성 데이터셋 5개와 28개 스키마 필드
- 자동추천 화면에서 완전히 보이는 후보 9건
- 링크 관리 화면에서 확인한 저장 관계 4건
- 공식 SCHEMORA commit `1339fedf8113fc3746d5664f1453248e47ee310c`
- 5개 pairwise benchmark의 실제 Top-5 후보 135건
- positive-only Recall 성격의 복구 평가
- 검색, 필터, 승인, 무시, 근거 확인을 지원하는 검토 UI
- LLM 호출, embedding 호출, 토큰, 시간 및 비용 기록

## 핵심 결과

| K | 개념 관계·한 방향 이상 | 개념 관계·모든 방향 | Directed |
|---:|---:|---:|---:|
| 1 | 2/4 (0.50) | 2/4 (0.50) | 2/5 (0.40) |
| 3 | 3/4 (0.75) | 3/4 (0.75) | 3/5 (0.60) |
| 5 | 4/4 (1.00) | 3/4 (0.75) | 4/5 (0.80) |

관찰되지 않은 관계는 negative가 아니므로 Precision과 F1은 보고하지
않는다. 저장 관계는 평가에만 사용했고, 5개 SCHEMORA
`mapping.parquet`는 모두 0행이었다.

## UI 실행

```bash
python3 ui/backend/server.py
```

<http://127.0.0.1:8765>에서 다음 두 화면을 전환할 수 있다.

- `Reference · 관찰값`: 원 데모 화면에서 보이는 9개 후보를 읽기 전용으로 표시
- `SCHEMORA 결과`: 실제 SCHEMORA 후보 135건을 검토 가능하게 표시

점수와 등급의 의미는 UI 내 설명 패널과
[`docs/ui_score_guide_ko.md`](docs/ui_score_guide_ko.md)에 기록했다.

## UI 캡처

- [`Reference · 관찰값`](docs/assets/reference-ui-observed-values.jpg)
- [`SCHEMORA 결과`](docs/assets/schemora-ui-actual-results.jpg)

## 주요 문서

- [`docs/reference_reconstruction_report.md`](docs/reference_reconstruction_report.md)
- [`docs/saved_link_positive_results_ko.md`](docs/saved_link_positive_results_ko.md)
- [`docs/ui_score_guide_ko.md`](docs/ui_score_guide_ko.md)
- [`cases/reference_demo_reconstruction/transformation_spec.md`](cases/reference_demo_reconstruction/transformation_spec.md)

모든 데이터는 세미나용 합성 데이터이며 운용 부대·임무·지형·인원
정보를 포함하지 않는다. API 키와 SCHEMORA upstream 소스는 저장소에
포함하지 않는다.
