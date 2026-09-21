# JBJ Database Convention

> 문서 상태: v1  
> 대상: JBJ(Job by Job) 데이터베이스 / ETL / 통계 스키마  
> DBMS: MySQL 8.4  
> 기본 문자셋: `utf8mb4`

---

## 1. 목적

JBJ는 일반적인 CRUD 서비스보다 다음 성격이 강한 데이터 서비스다.

- 여러 직업 분류체계(KSCO, KECO, NCS 등)를 함께 다룬다.
- 서로 다른 분류체계 사이의 매핑이 필요하다.
- 임금, 고용, 구인, 미충원 등 시계열 통계 데이터를 저장한다.
- Python ETL과 PHP 애플리케이션이 같은 데이터베이스를 사용한다.
- 향후 데이터 출처와 수집 이력을 추적해야 한다.

따라서 테이블과 컬럼 이름만 보고도 데이터의 역할과 관계를 가능한 한 파악할 수 있도록 명명 규칙을 통일한다.

---

## 2. 기본 원칙

### 2.1 테이블명

- 영문 소문자만 사용한다.
- `snake_case`를 사용한다.
- 기본적으로 **단수형**을 사용한다.
- 테이블임을 나타내는 `tb_`, `tbl_`, `_tb` 등의 접두사/접미사는 사용하지 않는다.
- 지나치게 축약된 이름보다 의미가 명확한 이름을 우선한다.

좋은 예:

```text
occupation_taxonomy
occupation_taxonomy_node
canonical_occupation
data_source
etl_run
```

피해야 할 예:

```text
tb_occupation
tbl_job
occupation_tb
occ_mst
job_info_tbl
```

---

## 3. JBJ 핵심 테이블 명명

### 3.1 직업 분류체계

```text
occupation_taxonomy
occupation_taxonomy_node
```

#### `occupation_taxonomy`

직업 분류체계 자체를 나타낸다.

예:

```text
KSCO 7
KSCO 8
KECO 2025
```

#### `occupation_taxonomy_node`

각 분류체계 안의 개별 분류 노드를 나타낸다.

예:

```text
KSCO8 2
KSCO8 22
KSCO8 222
KECO2025 13
KECO2025 133
```

`occupation`이 아니라 `node`를 사용하는 이유는 상위 분류와 중간 분류도 포함되기 때문이다.

### 3.2 JBJ 기준 직업

```text
canonical_occupation
```

여러 공식 분류체계를 JBJ 서비스에서 사용할 하나의 기준 직업으로 통합한 엔터티다.

공식 분류코드 자체와 JBJ 서비스 기준 직업을 혼동하지 않는다.

### 3.3 분류체계 매핑

```text
occupation_mapping
canonical_occupation_mapping
```

- `occupation_mapping`: 공식 분류체계 노드와 다른 공식 분류체계 노드 사이의 관계
- `canonical_occupation_mapping`: JBJ의 `canonical_occupation`과 공식 직업분류 노드 사이의 관계

### 3.4 통계 Fact 테이블

통계값을 저장하는 테이블은 `fact_` 접두사를 사용한다.

```text
fact_labor_demand
fact_wage
fact_employment
fact_regional_employment
```

`fact_` 테이블은 복수형을 적용하지 않고 측정 대상의 도메인명을 그대로 사용한다.

### 3.5 ETL 및 데이터 관리

```text
data_source
etl_run
```

필요한 경우 다음과 같이 확장한다.

```text
etl_run_log
data_source_snapshot
```

중간 적재 테이블이 실제로 필요해질 경우 `stg_` 접두사를 사용한다.

```text
stg_kosis_wage
stg_kosis_employment
stg_kosis_labor_demand
```

원본 API 응답이나 CSV/JSON은 가능하면 DB의 `raw_` 테이블보다 파일 영역에 보존한다.

```text
data/raw/
data/processed/
```

---

## 4. Primary Key

Primary Key는 다음 형식을 사용한다.

```text
<table_name>_id
```

예:

```text
occupation_taxonomy_id
occupation_taxonomy_node_id
canonical_occupation_id
data_source_id
etl_run_id
```

예시:

```sql
CREATE TABLE canonical_occupation (
    canonical_occupation_id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
);
```

`id` 하나로 통일하지 않는 이유는 JOIN이 많은 데이터 플랫폼에서 SQL의 의미를 더 명확하게 하기 위해서다.

---

## 5. Foreign Key

Foreign Key 컬럼명은 **참조하는 Primary Key 이름을 그대로 사용**한다.

예:

```text
occupation_taxonomy.occupation_taxonomy_id
        ↓
occupation_taxonomy_node.occupation_taxonomy_id
```

다음과 같은 축약은 사용하지 않는다.

```text
taxonomy_id
tax_id
occupation_tax_id
```

단, 자기참조 관계에서는 역할이 드러나도록 접두어를 추가할 수 있다.

```text
parent_occupation_taxonomy_node_id
```

---

## 6. 일반 컬럼 명명

모든 컬럼은 소문자 `snake_case`를 사용한다.

좋은 예:

```text
country_code
region_code
name_ko
name_en
source_url
worker_count
shortage_rate
```

피해야 할 예:

```text
countryCode
COUNTRY_CD
strRegion
workerCnt
shortagePct
```

---

## 7. Boolean 컬럼

Boolean 성격의 컬럼은 다음 접두어를 사용한다.

```text
is_
has_
```

예:

```text
is_active
is_public
is_verified
has_children
```

JBJ 내부에서는 `active_yn`, `use_yn`, `del_yn` 같은 표현은 사용하지 않는다.

---

## 8. 날짜와 시각

날짜만 의미하는 값:

```text
*_date
```

예:

```text
base_date
published_date
```

유효기간:

```text
valid_from
valid_to
```

시각까지 필요한 값:

```text
*_at
```

예:

```text
created_at
updated_at
collected_at
verified_at
published_at
```

`reg_date`, `mod_date`, `wdate`, `insert_dt`, `update_dt` 같은 표현은 사용하지 않는다.

---

## 9. 수량, 금액, 비율

수량:

```text
*_count
```

예:

```text
worker_count
opening_count
hire_count
unfilled_count
planned_hire_count
```

금액:

```text
*_amount
```

예:

```text
monthly_wage_amount
annualized_wage_amount
```

비율:

```text
*_rate
```

예:

```text
shortage_rate
unfilled_rate
employment_rate
```

단위가 혼동될 수 있는 값은 컬럼명 또는 별도 메타데이터에서 단위를 명확하게 관리한다.

---

## 10. 코드 컬럼

외부 또는 내부 코드 값은 기본적으로 다음 형식을 사용한다.

```text
*_code
```

예:

```text
country_code
region_code
industry_code
```

다만 테이블 자체가 코드 엔터티인 경우 문맥이 명확하면 `code`를 사용할 수 있다.

```text
occupation_taxonomy.code
occupation_taxonomy_node.code
```

통계 Fact 테이블에서 의미가 모호한 단순 `code` 컬럼은 사용하지 않는다.

---

## 11. 다국어 컬럼

다국어 텍스트는 언어 코드를 접미어로 사용한다.

```text
name_ko
name_en
description_ko
description_en
```

---

## 12. Index 명명

일반 인덱스:

```text
idx_<table>_<column>
```

예:

```text
idx_occupation_taxonomy_node_level
idx_occupation_taxonomy_node_parent
```

복합 인덱스:

```text
idx_<table>_<column1>_<column2>
```

예:

```text
idx_fact_wage_occupation_period
```

MySQL 식별자 길이 제한을 고려하여 지나치게 긴 경우 의미를 유지하는 범위에서 축약한다.

---

## 13. Unique Constraint 명명

Unique 제약조건:

```text
uq_<table>_<column>
```

복합키:

```text
uq_<table>_<column1>_<column2>
```

예:

```text
uq_occupation_taxonomy_code_version
uq_occupation_taxonomy_node_code
```

---

## 14. Foreign Key Constraint 명명

Foreign Key:

```text
fk_<source_table>_<target>
```

예:

```text
fk_occupation_taxonomy_node_taxonomy
fk_occupation_taxonomy_node_parent
```

---

## 15. Migration 파일 명명

Migration은 실행 순서를 알 수 있도록 숫자 prefix를 사용한다.

형식:

```text
NNN_<action>_<target>.sql
```

예:

```text
001_create_occupation_taxonomy.sql
002_create_canonical_occupation.sql
003_create_occupation_mapping.sql
004_create_fact_wage.sql
```

가능하면 하나의 migration에는 서로 밀접한 변경만 포함한다.

이미 적용된 migration 파일을 임의로 수정하기보다 새로운 migration을 추가하는 것을 원칙으로 한다.

예:

```text
005_add_source_version_to_data_source.sql
```

---

## 16. Seed 파일 명명

Seed 파일 역시 실행 순서를 표시한다.

```text
NNN_seed_<target>.sql
```

예:

```text
001_seed_taxonomy_sample.sql
002_seed_canonical_occupation_sample.sql
```

테스트용 샘플 데이터와 실제 기준 데이터는 향후 필요 시 분리한다.

```text
database/seeds/dev/
database/seeds/reference/
```

---

## 17. 문자셋과 한글

JBJ의 문자열 데이터는 `utf8mb4`를 기준으로 한다.

테이블 생성 시 프로젝트 전체에서 동일한 문자셋과 collation을 유지한다.

현재 기준 예:

```sql
ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;
```

SQL 파일 역시 UTF-8로 저장한다.

확인:

```bash
file -bi database/seeds/001_seed_taxonomy_sample.sql
```

SQL import 시 MySQL Client 문자셋을 명시한다.

```bash
docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/migrations/001_create_occupation_taxonomy.sql
```

Seed 파일 첫 부분에서 필요한 경우 다음을 명시한다.

```sql
SET NAMES utf8mb4;
```

---

## 18. SQL 작성 스타일

SQL 키워드는 대문자로 작성한다.

```sql
SELECT
    n.code,
    n.name_ko
FROM occupation_taxonomy_node n
JOIN occupation_taxonomy t
    ON t.occupation_taxonomy_id = n.occupation_taxonomy_id
WHERE n.is_active = TRUE
ORDER BY n.code;
```

복잡한 SQL에서는 의미 있는 짧은 alias를 사용한다.

```text
t = taxonomy
n = taxonomy node
c = canonical occupation
m = mapping
```

---

## 19. NULL 사용 원칙

값이 존재하지 않을 수 있는 경우에만 `NULL`을 허용한다.

예:

```text
valid_to
name_en
description
parent_occupation_taxonomy_node_id
```

`NULL`, 빈 문자열(`''`), `0`을 같은 의미로 혼용하지 않는다.

상위 노드가 없는 경우:

```text
parent_occupation_taxonomy_node_id = NULL
```

을 사용한다.

---

## 20. 공식 분류 코드와 JBJ 직업을 한 테이블에 섞지 않는다

다음과 같은 wide-table 구조는 사용하지 않는다.

```text
occupation
├─ ksco7_code
├─ ksco8_code
├─ keco2025_code
├─ ncs_code
├─ onet_code
└─ esco_code
```

분류체계 사이에는 다음 관계가 발생할 수 있다.

```text
1 : 1
1 : N
N : 1
부분 대응
상위/하위 대응
유사 관계
```

따라서 공식 분류체계는 `occupation_taxonomy_node`로 관리하고 관계는 별도 mapping 테이블로 관리한다.

---

## 21. 현재 기준 핵심 스키마

```text
occupation_taxonomy
        │
        ▼
occupation_taxonomy_node
        │
        ├──────────── occupation_mapping
        │
        └──────────── canonical_occupation_mapping
                              │
                              ▼
                     canonical_occupation


canonical_occupation
        │
        ├──────────── fact_wage
        ├──────────── fact_employment
        ├──────────── fact_labor_demand
        └──────────── fact_regional_employment


data_source
etl_run
```

실제 Fact 테이블이 공식 분류 노드를 직접 참조할지 `canonical_occupation`을 참조할지는 데이터셋의 원래 분류체계와 분석 목적을 고려해 결정한다.

원천 통계의 분류 수준과 의미를 보존하는 것을 우선한다.

---

## 22. Naming Checklist

새로운 테이블 또는 컬럼을 추가할 때 아래 항목을 확인한다.

- [ ] 테이블명은 단수형 `snake_case`인가?
- [ ] `tb_`, `tbl_`, `_tb` 같은 불필요한 접두어/접미사가 없는가?
- [ ] PK가 `<table_name>_id` 형식인가?
- [ ] FK가 참조 PK 이름과 일치하는가?
- [ ] Boolean 컬럼이 `is_` 또는 `has_` 형식인가?
- [ ] 날짜와 시각을 `_date`, `_at`, `_from`, `_to`로 구분했는가?
- [ ] 수량과 비율이 `_count`, `_rate` 등으로 명확한가?
- [ ] 의미가 모호한 축약어를 사용하지 않았는가?
- [ ] 공식 분류 코드와 JBJ canonical 직업을 혼합하지 않았는가?
- [ ] 외부 데이터의 원래 분류체계와 단위를 보존하고 있는가?
- [ ] UTF-8 / `utf8mb4` 기준을 지키고 있는가?

---

## 23. 현재 확정된 JBJ DB Naming Convention

```text
Table
────────────────────────────────────────
단수형
lowercase
snake_case
tb_, tbl_, _tb 사용하지 않음

Primary Key
────────────────────────────────────────
<table_name>_id

Foreign Key
────────────────────────────────────────
참조 Primary Key 이름 그대로 사용

Boolean
────────────────────────────────────────
is_*
has_*

Date / Time
────────────────────────────────────────
*_date
*_at
valid_from
valid_to

Count / Rate
────────────────────────────────────────
*_count
*_rate

Job Taxonomy
────────────────────────────────────────
occupation_taxonomy
occupation_taxonomy_node
canonical_occupation
occupation_mapping
canonical_occupation_mapping

Fact
────────────────────────────────────────
fact_labor_demand
fact_wage
fact_employment
fact_regional_employment

ETL / Source
────────────────────────────────────────
data_source
etl_run
stg_*

Migration
────────────────────────────────────────
001_create_occupation_taxonomy.sql
002_create_canonical_occupation.sql
003_create_occupation_mapping.sql
...
```

이 문서는 JBJ 데이터베이스 설계가 확장되면서 필요할 때 버전을 올려 수정한다.
