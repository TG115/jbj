# JBJ Agent Guidelines

저장소 작업 시 지켜야 할 **내구성 있는 엔지니어링 불변 조건**만 적는다.
제품 배경·KOSIS 해석 규칙·관측 수치는 아래 문서를 본다.

- [Product Vision](docs/product-vision.md)
- [KOSIS Labor Demand](docs/kosis-labor-demand.md)
- [Development Setup](docs/development-setup.md)
- [Database Convention](docs/database-convention.md)

---

## 조사 우선

- 클래스·DTO·프로퍼티·스키마·라우트·컬럼 이름을 **추측하지 않는다**.
- 편집 전에 실제 코드를 검색·확인한다.

## 공유 스키마

- JBJ 공유 스키마 SSOT는 루트 `/database/migrations/*.sql` + Python migration runner다.
- **`php artisan migrate`로 JBJ 공유 스키마를 변경하지 않는다.**
- 이미 적용된 SQL migration 파일을 수정하지 않는다. 변경은 새 `NNN_*.sql` 추가.
- 새 DB에서 `make migrate-baseline`을 사용하지 않는다.

## 데이터 무결성

- provenance를 유지한다: `data_source`, `etl_run`, raw 파일, SHA-256 checksum.
- **공식(official) 지표와 파생(derived) 지표를 혼동·혼합하지 않는다.**
- **부재(missing) ≠ 0.** 해당 grain에 원천 행이 없으면 0을 만들지 않는다.
- 상위(L2 등) 집계를 하위(L3) 직종 값처럼 조용히 대체하지 않는다.
- 상위 집계를 보여줄 때는 집계 수준이 다름을 명시한다.

## 코드 구조

- 불필요한 Repository/추상화 레이어를 추가하지 않는다.
- Labor demand API 관례: Route → Controller → FormRequest → Service → Query Builder → DTO → Resource.

## 테스트

- PHP 변경 후 관련 테스트를 먼저 돌리고, 마무리로 `make test`를 실행한다.
- Feature 테스트는 MySQL `jbj_test` 전제다. 일상적으로는 `make test`를 사용한다.

## 외부 데이터

- 새 외부 데이터셋을 들이기 전에 라이선스·재배포·재가공 가능 여부를 확인한다.
- 확인 후 `data_source` 등록과 provenance 설계를 선행한다.
- EIS 등 라이선스/활용 범위가 미확정인 소스는 production ETL 계획으로 문서화하지 않는다.

## Raw 데이터

- Raw는 출처 추적용으로 로컬/볼륨에 보존한다.
- **일반 Git에 raw JSON을 커밋하지 않는 것이 현재 정책**이다. 이를 구현 공백으로 취급하지 않는다.
