# KOSIS 노동수요 (DT_118N_DEN062)

> 목적: KOSIS 직종별·규모별 노동수요의 **수집 범위, 원천 grain, 해석 규칙**을 저장소에 고정한다.  
> 재현 절차·Makefile 명령은 [Development Setup](development-setup.md)을 본다.

---

## 1. 소스

| 항목 | 값 |
|---|---|
| ORG_ID | `118` |
| TABLE_ID | `DT_118N_DEN062` |
| 표 제목 | 직종별·규모별(2026년 이후) |
| Fact 테이블 | `fact_labor_demand` |
| 분류 | KECO2025 taxonomy node FK 필수 |

Fact grain:

```text
period
× region
× establishment size
× KECO occupation
```

### 공식 지표 (DB / `metrics.official`)

```text
current_workers   (현원)
openings          (구인인원)
hires             (채용인원)
unfilled          (미충원인원)
shortage          (부족인원)
planned_hires     (채용계획인원)
shortage_rate     (부족률)
```

### 파생 지표 (API 계산 / `metrics.derived`)

```text
unfilled_rate
opening_intensity
planned_hire_rate
```

공식 Fact에 파생값을 섞어 저장하지 않는다.

---

## 2. 우선 수집 스코프 (24)

구현: `analytics/python/src/jbj_etl/labor_demand/collection_plan.py`  
`build_priority_scopes()` → collector가 전부 순회한다.

| kind | 구성 | 개수 |
|---|---|---:|
| `baseline` | 전국 × 전규모 | 1 |
| `region` | 17 시도 × 전규모 | 17 |
| `size` | 전국 × 비중첩 사업체 규모 6종 | 6 |
| **합계** | | **24** |

### 규모 밴드 (기본 비교 스코프)

비중첩 구간만 우선 스코프에 포함한다. 전규모·중첩 집계 규모는 기본 비교 스코프에서 제외한다.

| 코드 접미 | 의미 |
|---|---|
| `SIZES.02` | 5인 미만 |
| `SIZES.03` | 5–9인 |
| `SIZES.04` | 10–29인 |
| `SIZES.05` | 30–99인 |
| `SIZES.06` | 100–299인 |
| `SIZES.07` | 300인 이상 |

전규모는 `SIZES.00` (baseline / region 스코프용).

Raw 경로 예:

```text
data/raw/kosis/DT_118N_DEN062/data/{period}/{scope.slug}.json
```

스코프마다 별도 `etl_run` + checksum을 남긴다.

---

## 3. 원천 grain (해석에 필수)

KOSIS가 **스코프마다 다른 KECO 계층**을 내려준다.

| 스코프 | KECO 계층 | 직종 행 수(구조) |
|---|---|---|
| 전국 × 전규모 / 전국 × 규모 | L1 + L2 + L3 | 10 + 35 + 140 = **185** |
| 시도 × 전규모 | L1 + L2 (**L3 없음**) | 10 + 35 = **45** |

예: 직업 코드 `133`(소프트웨어 개발자)은 **전국/규모 스코프에는 있을 수 있으나**, `서울 × 133` 행은 원천에 없을 수 있다.  
이는 수요가 0이라는 뜻이 아니라 **해당 grain에서 원천이 L3를 제공하지 않음**이다.

---

## 4. 해석 원칙

1. **missing ≠ zero**  
   원천에 없는 occupation×region×size 조합을 0으로 채우지 않는다.
2. **가짜 0 금지**  
   API/UI/ETL에서 부재 행을 합성하지 않는다. (현재 latest API는 행 없으면 404.)
3. **상위→하위 조용한 대체 금지**  
   L2 집계를 L3 직종 값처럼 자동 대입하지 않는다.
4. **집계 수준 공개**  
   상위 분류 집계를 보여줄 때는 그 수준이 L3와 다름을 명시한다.

---

## 5. 관측값: period `202601` (불변 조건 아님)

아래는 **202601 수집에서 관측·교차검증된 수치**다.  
KOSIS 분류·공표 범위가 바뀌면 달라질 수 있다. **영구 규칙으로 취급하지 않는다.**

| 스코프 | 관측 행 수 |
|---|---:|
| 전국 × 전규모 | 185 |
| 전국 × 규모 밴드 각각 | 185 |
| 시도 × 전규모 각각 | 45 |
| **`fact_labor_demand` 합계** | **2,060** |

검산: `185 + (17 × 45) + (6 × 185) = 2,060`.

코드에 이 건수를 상수로 박아 두지 않았다. 회귀 가드가 필요하면 별도 테스트/체크로 추가한다.

---

## 6. Raw / Git 정책

- Raw JSON은 provenance용으로 로컬·볼륨에 보존한다.
- **일반 Git에 raw를 커밋하지 않는 것이 현재 정책**이다.
- 이를 “구현이 덜 된 상태”로 문서화하지 않는다.

---

## 7. EIS (참고 · 미결정)

지역 L3 한계를 보완할 **후보**로 EIS 등을 검토할 수 있다.  
고용노동부(국민신문고 등)에 상업적 이용·저장·재가공·파생지표·자동수집에 대한 **공식 문의가 진행 중**이며, 답변이 오기 전에는:

- EIS production ETL을 **결정된 계획으로 문서화하지 않는다.**
- 라이선스·활용 범위 확정 전 적재를 전제로 한 설계를 확정하지 않는다.

---

## 8. 관련 코드

- `analytics/python/src/jbj_etl/labor_demand/collection_plan.py`
- `analytics/python/src/jbj_etl/cli/collect_kosis_labor_demand.py`
- `app/php/app/Http/Controllers/Api/OccupationLaborDemandController.php`
- `app/php/app/Services/LaborDemandMetricCalculator.php`
