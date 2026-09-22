# JBJ 개발환경 및 데이터 파이프라인 재현 가이드

> 프로젝트: **JBJ (Job by Job / 직바직)**  
> 목적: 새 PC나 다른 개발환경에서도 현재까지 구축한 Docker, DB, Migration, ETL, 직업분류 데이터를 동일하게 재현하기 위한 문서

## 1. 현재 스택

JBJ는 Windows + WSL2 환경에서 개발하며, JBJ용 Docker는 **WSL 내부 Docker Engine**을 사용한다.

- WSL2 + Ubuntu LTS
- Docker Engine + Docker Compose Plugin
- Nginx
- PHP 8.5 FPM
- MySQL 8.4
- Python 3.12

기본 포트:

| 서비스 | Host | Container |
|---|---:|---:|
| Nginx | 8081 | 80 |
| MySQL | 3308 | 3306 |

컨테이너끼리 통신할 때는 `mysql:3306`, PC에서 MySQL에 접근할 때는 `localhost:3308`을 사용한다.

## 2. Docker Context

```bash
docker context show
```

JBJ에서는 다음이 정상이다.

```text
default
```

`desktop-linux`가 활성화되어 있으면 Docker Desktop context이므로 JBJ에서는 사용하지 않는다.

## 3. 현재 프로젝트 구조

```text
~/jbj
├─ README.md
├─ Makefile
├─ compose.yml
├─ .env
├─ .env.example
├─ .gitignore
├─ docs/
│  ├─ database-convention.md
│  └─ development-setup.md
├─ app/php/public/index.php
├─ analytics/python/
│  ├─ Dockerfile
│  ├─ requirements.txt
│  └─ src/jbj_etl/
│     ├─ __init__.py
│     ├─ config.py
│     ├─ db.py
│     ├─ etl.py
│     ├─ migration.py
│     ├─ taxonomy/
│     │  ├─ __init__.py
│     │  ├─ types.py
│     │  ├─ validator.py
│     │  ├─ importer.py
│     │  └─ normalizers/
│     │     ├─ __init__.py
│     │     ├─ ksco8.py
│     │     └─ keco2025.py
│     └─ cli/
│        ├─ __init__.py
│        ├─ migrate.py
│        ├─ import_taxonomy.py
│        ├─ normalize_ksco8.py
│        ├─ normalize_keco2025.py
│        ├─ inspect_hwpx.py
│        └─ inspect_pdf.py
├─ database/
│  ├─ migrations/
│  │  ├─ 001_create_occupation_taxonomy.sql
│  │  ├─ 002_create_canonical_occupation.sql
│  │  ├─ 003_create_canonical_occupation_mapping.sql
│  │  ├─ 004_create_data_source.sql
│  │  └─ 005_create_etl_run.sql
│  └─ seeds/
└─ data/
   ├─ raw/
   │  ├─ ksco8/ksco8_items.hwpx
   │  └─ keco2025/keco2025_table.pdf
   └─ processed/taxonomies/
      ├─ ksco8.csv
      └─ keco2025.csv
```

`__init__.py`는 비어 있어도 정상이다.

## 4. `.env`

예시:

```env
MYSQL_ROOT_PASSWORD=jbj_root_password
MYSQL_DATABASE=jbj
MYSQL_USER=jbj
MYSQL_PASSWORD=jbj_password
```

`.env`는 Git에 커밋하지 않는다. 새 환경에서는:

```bash
cp .env.example .env
```

후 값을 입력한다.

## 5. Python Docker 설정

Python Dockerfile에는 다음 설정이 필요하다.

```dockerfile
ENV PYTHONPATH=/app/src
```

`compose.yml`의 Python 서비스에는 다음 mount가 필요하다.

```yaml
volumes:
  - ./analytics/python:/app
  - ./data:/data
  - ./database:/database:ro
```

주요 Python package:

```text
PyMySQL
pypdf
```

## 6. MySQL Timezone

JBJ는 한국 서비스 기준으로 MySQL session timezone을 `+09:00`으로 맞춘다.

```yaml
environment:
  TZ: Asia/Seoul

command:
  - --default-time-zone=+09:00
```

확인:

```bash
docker compose exec mysql \
  sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
  -e "
SELECT
    @@system_time_zone,
    @@global.time_zone,
    @@session.time_zone,
    NOW(),
    UTC_TIMESTAMP();
"'
```

## 7. 최초 실행

```bash
git clone <repository>
cd jbj
cp .env.example .env
```

`.env` 작성 후:

```bash
make build
make up
make ps
```

브라우저:

```text
http://localhost:8081
```

정상 확인 예:

```text
JBJ API is running
PHP: 8.5.x
Database: connected
```

## 8. Makefile

반복되는 긴 Docker 명령은 Makefile로 감싼다.

```bash
make up
make down
make ps
make build

make migrate
make migrate-status

make normalize-ksco8
make import-ksco8

make normalize-keco2025
make import-keco2025

make etl-status
```

Makefile은 Docker를 대체하는 것이 아니라 반복 명령에 짧은 이름을 붙인 것이다.

## 9. Migration 규칙

Migration 파일 규칙:

```text
NNN_<action>_<target>.sql
```

예:

```text
001_create_occupation_taxonomy.sql
004_create_data_source.sql
005_create_etl_run.sql
006_create_fact_labor_demand.sql
```

이미 적용된 migration은 수정하지 않는다. 구조 변경이 필요하면 새 migration을 추가한다.

예:

```text
004_create_data_source.sql 수정 X
006_alter_data_source.sql 추가 O
```

### schema_migration

Migration runner는 `schema_migration` 테이블로 적용 여부와 checksum을 관리한다.

```bash
make migrate-status
```

### 새 DB

새 DB에서는 다음만 실행한다.

```bash
make migrate
```

`001`부터 미적용 migration을 자동 실행한다.

### 기존 개발 DB의 baseline

초기 개발 DB에서는 migration runner 도입 전에 `001~005`를 수동 적용했기 때문에 한 번만:

```bash
make migrate-baseline
```

을 실행했다.

이후:

```bash
make migrate
```

결과 `0 applied`까지 확인 완료.

**새 PC의 새 DB에서는 `make migrate-baseline`을 실행하지 않는다.**

## 10. Seed 규칙

Migration과 Seed는 역할이 다르다.

- Migration: DB 구조 변경, 한 번만 실행
- Reference Seed: `data_source` 같은 시스템 기준 데이터
- Development Seed: 로컬 테스트용 데이터

Reference Seed는 재실행 가능하도록 `INSERT ... ON DUPLICATE KEY UPDATE` 형태를 권장한다.

향후 권장 구조:

```text
database/seeds/
├─ reference/
└─ development/
```

## 11. 주요 DB 테이블

### occupation_taxonomy
공식 직업분류 체계 자체.

```text
KSCO 8
KECO 2025
```

### occupation_taxonomy_node
각 분류체계 내부의 실제 코드.

```text
KSCO8 222
컴퓨터 시스템 및 소프트웨어 전문가

KECO2025 133
소프트웨어 개발자
```

### canonical_occupation
JBJ가 사용자에게 보여주는 기준 직업.

### canonical_occupation_mapping
JBJ 기준 직업과 공식 분류체계를 연결한다.

### data_source
데이터셋 등록부.

### etl_run
ETL 실행 이력.

기록 예:

```text
source
job
status
source file
SHA-256 checksum
parameters
processed count
started_at
finished_at
error message
```

## 12. Python ETL 구조

```text
공식 원본
   ↓
Source-specific Normalizer
   ↓
TaxonomyRow
   ↓
Validator
   ↓
Generic Importer
   ↓
MySQL
```

TaxonomyRow:

```python
{
    "code": "133",
    "name_ko": "소프트웨어 개발자",
    "level": 3,
    "parent_code": "13",
}
```

## 13. KSCO8

원본:

```text
data/raw/ksco8/ksco8_items.hwpx
```

정규화:

```bash
make normalize-ksco8
```

검증된 결과:

```text
Level 1: 10
Level 2: 57
Level 3: 167
Level 4: 495
Level 5: 1270
Total: 1999
```

DB Import:

```bash
make import-ksco8
```

기대:

```text
Validated: 1999 nodes
Nodes processed: 1999
```

## 14. KECO2025

원본:

```text
data/raw/keco2025/keco2025_table.pdf
```

PDF 텍스트 특성상 코드 중간 공백이나 한 줄에 여러 코드가 붙는 경우를 normalizer에서 보정한다.

정규화:

```bash
make normalize-keco2025
```

검증된 결과:

```text
Level 1: 10
Level 2: 35
Level 3: 140
Level 4: 495
Total: 680
```

DB Import:

```bash
make import-keco2025
```

기대:

```text
Validated: 680 nodes
Nodes processed: 680
```

현재 taxonomy node 총합:

```text
KSCO8     1999
KECO2025   680
----------------
Total     2679
```

## 15. ETL 실행 이력

조회:

```bash
make etl-status
```

현재 기대 상태:

```text
KSCO8     import_taxonomy   SUCCESS   1999
KECO2025  import_taxonomy   SUCCESS    680
```

원본 파일의 SHA-256 checksum을 기록하므로 같은 파일명이더라도 내용이 변경되었는지 확인할 수 있다.

## 16. 새 PC에서 전체 복구 순서

```bash
git clone <repository>
cd jbj

cp .env.example .env
# .env 작성

make build
make up
make migrate
```

Reference Seed가 필요하면 적용한다.

공식 raw 파일은 Git에 포함하지 않는 것을 원칙으로 하므로 다음 위치에 준비한다.

```text
data/raw/ksco8/ksco8_items.hwpx
data/raw/keco2025/keco2025_table.pdf
```

그 다음:

```bash
make normalize-ksco8
make import-ksco8

make normalize-keco2025
make import-keco2025

make migrate-status
make etl-status
```

## 17. Git 관리 원칙

Git에 포함:

```text
compose.yml
Dockerfile
requirements.txt
Makefile
Python/PHP source
migration
seed
docs
.env.example
```

Git에서 제외:

```text
.env
data/raw/
MySQL Docker volume
개인 로컬 설정
```

## 18. 현재까지 완료

```text
[완료] WSL2 + Docker Engine
[완료] Docker Compose
[완료] Nginx
[완료] PHP 8.5
[완료] MySQL 8.4
[완료] Python 3.12
[완료] PHP → MySQL
[완료] Python → MySQL
[완료] Asia/Seoul timezone
[완료] DB naming convention
[완료] taxonomy schema
[완료] canonical occupation schema
[완료] KSCO8 HWPX normalizer
[완료] KSCO8 1,999개 import
[완료] KECO2025 PDF normalizer
[완료] KECO2025 680개 import
[완료] 공통 validator/importer
[완료] data_source
[완료] etl_run
[완료] SHA-256 source tracking
[완료] Makefile
[완료] migration runner
[완료] schema_migration
[완료] 기존 001~005 baseline
[완료] make migrate → 0 applied
```

## 19. 다음 개발 단계

다음 migration부터 migration runner를 실제 사용한다.

예정:

```text
006_create_fact_labor_demand.sql
```

이후:

```bash
make migrate
```

다음 데이터 파이프라인:

```text
KOSIS
DT_118N_DEN062
   ↓
API Client
   ↓
Raw Response
   ↓
Normalizer
   ↓
KECO2025 연결
   ↓
fact_labor_demand
   ↓
etl_run
```

## 20. 핵심 주의사항

1. JBJ Docker context는 `default`.
2. JBJ는 WSL 내부 Docker Engine 사용.
3. `.env`는 Git에 올리지 않는다.
4. 새 DB에서는 `make migrate-baseline`을 실행하지 않는다.
5. 이미 적용된 migration SQL은 수정하지 않는다.
6. DB 변경은 새 migration으로 추가한다.
7. 공식 raw 파일은 원본 그대로 보존한다.
8. expected count 검증 실패 시 DB import를 중단한다.
9. ETL 실행 시 checksum과 실행이력을 기록한다.
10. 컨테이너 간 MySQL 주소는 `mysql:3306`.
