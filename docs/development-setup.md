# JBJ 개발환경 및 데이터 파이프라인 재현 가이드

> 프로젝트: **JBJ (Job by Job / 직바직)**  
> 목적: 새 PC나 다른 개발환경에서도 현재까지 구축한 Docker, DB, Migration, ETL, Laravel API, 직업분류 및 노동수요 데이터를 동일하게 재현하기 위한 문서

---

## 1. 현재 스택

JBJ는 Windows + WSL2 환경에서 개발하며, JBJ용 Docker는 **WSL Ubuntu 내부 Docker Engine**을 사용한다.

- WSL2 + Ubuntu LTS
- Docker Engine + Docker Compose Plugin
- Nginx
- PHP 8.5 FPM
- Composer 2
- Laravel 13
- MySQL 8.4
- Python 3.12


| 서비스     | Host | Container |
| ------- | ---- | --------- |
| Nginx   | 8081 | 80        |
| MySQL   | 3308 | 3306      |
| PHP-FPM | -    | 9000      |


컨테이너 간 MySQL 접속은 `mysql:3306`, PC에서 직접 접속할 때는 `localhost:3308`을 사용한다.

---



## 2. Docker Context

```bash
docker context show
```

정상:

```text
default
```

`desktop-linux`는 Docker Desktop context이므로 JBJ에서는 사용하지 않는다.

```bash
systemctl status docker
```

로 WSL 내부 Docker daemon 상태를 확인한다.

---



## 3. 프로젝트 구조

```text
~/jbj
├─ README.md
├─ Makefile
├─ compose.yml
├─ .env
├─ .env.example
├─ docs/
│  ├─ database-convention.md
│  └─ development-setup.md
├─ app/php/
│  ├─ app/
│  │  ├─ Data/
│  │  │  └─ LaborDemandSnapshot.php
│  │  ├─ Http/
│  │  │  ├─ Controllers/Api/
│  │  │  │  └─ OccupationLaborDemandController.php
│  │  │  └─ Resources/
│  │  │     └─ OccupationLaborDemandResource.php
│  │  └─ Services/
│  │     └─ OccupationLaborDemandService.php
│  ├─ bootstrap/
│  ├─ config/
│  ├─ public/index.php
│  ├─ resources/
│  ├─ routes/
│  │  ├─ api.php
│  │  ├─ console.php
│  │  └─ web.php
│  ├─ storage/
│  ├─ tests/
│  ├─ artisan
│  ├─ composer.json
│  └─ composer.lock
├─ analytics/python/
│  ├─ Dockerfile
│  ├─ requirements.txt
│  └─ src/jbj_etl/
│     ├─ config.py
│     ├─ db.py
│     ├─ etl.py
│     ├─ migration.py
│     ├─ providers/kosis/client.py
│     ├─ taxonomy/
│     │  ├─ types.py
│     │  ├─ validator.py
│     │  ├─ importer.py
│     │  └─ normalizers/
│     │     ├─ ksco8.py
│     │     └─ keco2025.py
│     ├─ labor_demand/
│     │  ├─ types.py
│     │  ├─ normalizer.py
│     │  └─ importer.py
│     └─ cli/
│        ├─ migrate.py
│        ├─ import_taxonomy.py
│        ├─ normalize_ksco8.py
│        ├─ normalize_keco2025.py
│        ├─ inspect_kosis_table.py
│        ├─ inspect_kosis_demand_sample.py
│        └─ collect_kosis_labor_demand.py
├─ database/
│  ├─ migrations/
│  │  ├─ 001_create_occupation_taxonomy.sql
│  │  ├─ 002_create_canonical_occupation.sql
│  │  ├─ 003_create_canonical_occupation_mapping.sql
│  │  ├─ 004_create_data_source.sql
│  │  ├─ 005_create_etl_run.sql
│  │  └─ 006_create_fact_labor_demand.sql
│  └─ seeds/reference/
│     └─ 001_upsert_data_source.sql
└─ data/
   ├─ raw/
   │  ├─ ksco8/ksco8_items.hwpx
   │  ├─ keco2025/keco2025_table.pdf
   │  └─ kosis/DT_118N_DEN062/
   │     ├─ metadata/
   │     └─ data/
   └─ processed/taxonomies/
      ├─ ksco8.csv
      └─ keco2025.csv
```



### Laravel 기본과 JBJ 커스텀


| 경로                             | 성격            | 역할                      |
| ------------------------------ | ------------- | ----------------------- |
| `app/php/app/Http/Controllers` | Laravel 기본    | HTTP 요청 처리              |
| `app/php/app/Http/Resources`   | Laravel 기능/관례 | API JSON 변환             |
| `app/php/app/Data`             | JBJ 커스텀       | DTO                     |
| `app/php/app/Services`         | JBJ 커스텀       | 비즈니스 로직                 |
| `app/php/resources`            | Laravel 기본    | Blade/JS/CSS 등 화면 리소스   |
| `/database/migrations`         | JBJ 커스텀       | PHP/Python 공용 DB schema |
| `/analytics/python`            | JBJ 커스텀       | ETL/분석                  |
| `/data`                        | JBJ 커스텀       | raw/processed 데이터       |


Laravel 기본 migration은 사용하지 않는다. JBJ DB schema의 Single Source of Truth는 프로젝트 루트의 `/database/migrations`이다.

---



## 4. 환경변수

Root:

```bash
cp .env.example .env
```

예:

```env
MYSQL_ROOT_PASSWORD=jbj_root_password
MYSQL_DATABASE=jbj
MYSQL_USER=jbj
MYSQL_PASSWORD=jbj_password

KOSIS_API_KEY=

LOCAL_UID=1000
LOCAL_GID=1000
```

UID/GID 확인:

```bash
id -u
id -g
```

Laravel:

```bash
cp app/php/.env.example app/php/.env
```

`/.env`, `app/php/.env`는 Git에 커밋하지 않는다.

---



## 5. PHP / Laravel 파일 권한

Artisan/Composer가 bind mount에 `root:root` 파일을 생성하지 않도록 PHP 컨테이너의 `www-data` UID/GID를 WSL 사용자와 맞춘다.

Dockerfile 예:

```dockerfile
ARG UID=1000
ARG GID=1000

RUN groupmod -o -g ${GID} www-data \
    && usermod -o -u ${UID} -g ${GID} www-data
```

Compose build args:

```yaml
build:
  args:
    UID: ${LOCAL_UID:-1000}
    GID: ${LOCAL_GID:-1000}
```

파일 생성 작업은 가능하면 `www-data`로 실행한다.

```bash
docker compose exec \
  --user www-data \
  -e HOME=/tmp \
  php php artisan route:list
```

기존 ownership 정리는 필요할 때 한 번만:

```bash
sudo chown -R "$(id -u):$(id -g)" app/php
```

---



## 6. Python 설정

Dockerfile:

```dockerfile
ENV PYTHONPATH=/app/src
```

Compose volume:

```yaml
volumes:
  - ./analytics/python:/app
  - ./data:/data
  - ./database:/database:ro
```

주요 package:

```text
PyMySQL
pypdf
requests
```

---



## 7. MySQL Timezone

```yaml
environment:
  TZ: Asia/Seoul

command:
  - --default-time-zone=+09:00
```

---



## 8. 새 환경 최초 실행

```bash
git clone <repository-url> jbj
cd jbj

cp .env.example .env
cp app/php/.env.example app/php/.env
```

`.env` 작성 후:

```bash
make build
make up
make ps
```

Laravel dependency:

```bash
docker compose exec \
  --user www-data \
  -e HOME=/tmp \
  php composer install
```

`APP_KEY`가 비어 있다면:

```bash
docker compose exec \
  --user www-data \
  -e HOME=/tmp \
  php php artisan key:generate
```

DB:

```bash
make migrate
make seed-reference
```

baseline은 migration runner 도입 전에
SQL을 수동 적용한 기존 DB를 편입할 때만 사용한다.

현재 DB가 수동으로 적용된 마지막 migration을 확인한 후:

`make migrate-baseline THROUGH=<마지막 버전>`

새 DB 또는 이미 schema_migration이 존재하는 DB에서는
baseline을 사용하지 않는다.

---



## 9. 기본 동작 확인

```bash
docker compose exec php php artisan route:list
```

```bash
curl http://localhost:8081/api/health
```

정상:

```json
{
  "service": "jbj-api",
  "status": "ok",
  "database": "connected"
}
```

Laravel 기본 health는 `/up`, JBJ DB health는 `/api/health`다.

---



## 10. Makefile 주요 명령

```bash
make up
make down
make ps
make build

make migrate
make migrate-status
make seed-reference

make normalize-ksco8
make import-ksco8

make normalize-keco2025
make import-keco2025

make inspect-kosis-demand
make inspect-kosis-demand-sample
make collect-kosis-demand

make etl-status
```

---



## 11. Migration 규칙

```text
NNN_<action>_<target>.sql
```

현재:

```text
001_create_occupation_taxonomy.sql
002_create_canonical_occupation.sql
003_create_canonical_occupation_mapping.sql
004_create_data_source.sql
005_create_etl_run.sql
006_create_fact_labor_demand.sql
```

이미 적용된 migration은 수정하지 않는다. 변경은 새 migration으로 추가한다.

`schema_migration`은 적용 여부와 SHA-256 checksum을 관리한다.

```bash
make migrate-status
```

초기 개발 DB에서만 `001~005`를 baseline 처리했고, `006`부터는 runner로 적용한다.

---



## 12. Seed 규칙

- Migration: DB 구조
- Reference Seed: 시스템 기준 데이터
- Development Seed: 로컬 테스트 데이터

현재 reference source:

```text
KSCO8
KECO2025
KOSIS_LABOR_DEMAND
```

```bash
make seed-reference
```

Reference Seed는 재실행 가능한 UPSERT 형태로 작성한다.

---



## 13. 주요 DB 테이블

- `occupation_taxonomy`: 공식 분류체계
- `occupation_taxonomy_node`: 분류 코드와 계층
- `canonical_occupation`: JBJ 기준 직업
- `canonical_occupation_mapping`: JBJ 직업과 외부 분류의 관계
- `data_source`: 데이터셋 등록부
- `etl_run`: ETL 실행/원본/checksum/건수/오류 이력
- `fact_labor_demand`: KOSIS 노동수요 공식 원자료

`fact_labor_demand` grain:

```text
period
× region
× establishment size
× KECO occupation
```

공식 지표:

```text
current_workers_count
openings_count
hires_count
unfilled_count
shortage_count
planned_hires_count
shortage_rate
```

JBJ 파생지표는 공식 Fact와 구분한다.

---



## 14. KSCO8 / KECO2025

KSCO8:

```bash
make normalize-ksco8
make import-ksco8
```

검증:

```text
Level 1: 10
Level 2: 57
Level 3: 167
Level 4: 495
Level 5: 1270
Total: 1999
```

KECO2025:

```bash
make normalize-keco2025
make import-keco2025
```

검증:

```text
Level 1: 10
Level 2: 35
Level 3: 140
Level 4: 495
Total: 680
```

총 taxonomy node: `2679`.

---



## 15. KOSIS 노동수요

```text
ORG_ID = 118
TBL_ID = DT_118N_DEN062
직종별·규모별(2026년 이후)
```

분류:

```text
시도
규모
KECO 직종
```

지표:

```text
현원
구인인원
채용인원
미충원인원
부족인원
채용계획인원
부족률
```

Metadata:

```bash
make inspect-kosis-demand
```

Sample:

```bash
make inspect-kosis-demand-sample
```

수집:

```bash
make collect-kosis-demand
```

다른 반기:

```bash
make collect-kosis-demand KOSIS_DEMAND_PERIOD=202602
```

검증된 샘플:

```text
2026 상반기 / 전국 / 전규모 / KECO 133 소프트웨어 개발자

현원        341646
구인         16408
채용         13414
미충원        2994
부족         11293
채용계획     11108
부족률          3.2
```

---



## 16. Laravel API 구조

```text
routes/api.php
   ↓
OccupationLaborDemandController
   ↓
OccupationLaborDemandService
   ↓
Query Builder
   ↓
MySQL
   ↓
LaborDemandSnapshot (DTO)
   ↓
OccupationLaborDemandResource
   ↓
JSON
```

역할:

```text
Route      = URL 연결
Controller = HTTP 요청/응답
Service    = JBJ 비즈니스 규칙/조회
DTO        = 타입이 명확한 내부 데이터
Resource   = 외부 JSON 구조
```



### 현재 API

```text
GET /api/health
GET /api/occupations/{occupationCode}/labor-demand
```

예:

```bash
curl http://localhost:8081/api/occupations/133/labor-demand
```

---



## 17. PHP 8 / Laravel 현재 사용 개념

PHP:

```text
strict_types
typed properties
nullable type
union type
constructor property promotion
readonly
named arguments
return type
```

Laravel:

```text
Routing
Controller
Dependency Injection / Service Container
Query Builder
JsonResource
Artisan
```

자동 호출 예:

```text
new 객체          → __construct()       PHP
Route match       → Controller::show() Laravel
JsonResource 응답 → toArray()          Laravel
Controller 의존성  → 자동 생성/주입      Laravel
```

`$this->resource`에는 `JsonResource` 생성자로 전달한 `LaborDemandSnapshot` DTO가 들어간다.

---



## 18. 새 PC 전체 복구 순서

```bash
git clone <repository-url> jbj
cd jbj
cp .env.example .env
cp app/php/.env.example app/php/.env
make build
make up
```

Composer / APP_KEY:

```bash
docker compose exec --user www-data -e HOME=/tmp php composer install
docker compose exec --user www-data -e HOME=/tmp php php artisan key:generate
```

DB:

```bash
make migrate
make seed-reference
```

Taxonomy raw 파일 준비 후:

```bash
make normalize-ksco8
make import-ksco8
make normalize-keco2025
make import-keco2025
```

KOSIS:

```bash
make inspect-kosis-demand
make collect-kosis-demand
```

검증:

```bash
make migrate-status
make etl-status
curl http://localhost:8081/api/health
curl http://localhost:8081/api/occupations/133/labor-demand
```

---



## 19. Git 관리 원칙

Git 포함:

```text
compose.yml
Dockerfile
requirements.txt
Makefile
PHP/Python source
composer.json
composer.lock
migration
reference seed
docs
.env.example
app/php/.env.example
```

Git 제외:

```text
.env
app/php/.env
app/php/vendor/
app/php/node_modules/
data/raw/
MySQL Docker volume
```

---



## 20. 현재까지 완료

```text
[완료] WSL2 + Docker Engine / Compose
[완료] Nginx / PHP 8.5 / Composer / Laravel 13
[완료] MySQL 8.4 / Python 3.12
[완료] timezone / UID-GID 대응
[완료] SQL migration runner / schema_migration
[완료] data_source / etl_run / SHA-256 provenance
[완료] KSCO8 1,999 nodes
[완료] KECO2025 680 nodes
[완료] 006 fact_labor_demand
[완료] KOSIS metadata / sample / collector
[완료] KOSIS raw JSON 보존
[완료] KECO2025 FK 기반 fact 적재
[완료] GET /api/health
[완료] GET /api/occupations/{code}/labor-demand
[완료] Route → Controller → Service → DTO → Resource
```

---



## 21. 다음 개발 단계

```text
1. Laravel Feature Test
2. 노동수요 Metric 계층
3. 노동수요 history / 지역 / 규모 API
4. KOSIS 임금 데이터
5. Canonical occupation mapping
6. 전국/지역 고용 데이터
7. NCS
8. Q-Net
9. 검색/상세/비교 UI
10. CI/CD / 정적분석 / 배포 / 모니터링
```

---



## 22. 핵심 주의사항

1. Docker context는 `default`.
2. WSL 내부 Docker Engine 사용.
3. `.env`, `app/php/.env`는 Git 제외.
4. 새 DB에서 `make migrate-baseline` 금지.
5. 적용된 migration 수정 금지.
6. DB 변경은 새 migration 추가.
7. Laravel migration과 root migration 혼용 금지.
8. DB schema 기준은 `/database/migrations`.
9. 공식 raw/API 응답은 원본 보존.
10. taxonomy 검증 실패 시 import 중단.
11. ETL checksum/실행이력 기록.
12. 공식 통계와 JBJ 파생 Metric 구분.
13. 컨테이너 간 MySQL은 `mysql:3306`.
14. Artisan/Composer 파일 생성은 `www-data` 우선.

