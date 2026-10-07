# JBJ

**Job by Job — 직업을 데이터로 비교하다.**

JBJ(직바직)는 여러 공식 직업·노동시장 데이터를 연결해 직업을 탐색하고 비교할 수 있도록 만드는 커리어 데이터 서비스입니다. 채용 공고 게시판이 아닙니다.

핵심 질문: **「나는 뭐하고 살지?」** — 상세는 [Product Vision](docs/product-vision.md).

현재 저장소 초점: 직업분류(KSCO/KECO), KOSIS 노동수요 ETL(우선 24스코프), Laravel labor-demand API.

> **문서 SoT:** 구현·해석 규칙의 기준은 이 저장소의 `README.md` / `docs/**` / `AGENTS.md`다.

## Architecture

```text
Official Files / KOSIS
        ↓
    Python ETL
        ↓
       MySQL
        ↑
  Laravel 13 API
        ↑
      Nginx
```

현재 주요 기술:

- PHP 8.5 + Laravel 13
- Python 3.12
- MySQL 8.4
- Nginx
- Docker Compose
- WSL2 내부 Docker Engine
- SQL Migration Runner (`database/migrations/*.sql`)
- ETL provenance (`data_source`, `etl_run`)

## Current Data

### Occupation Taxonomies

```text
KSCO8      1,999 nodes
KECO2025     680 nodes
```

### KOSIS Labor Demand

```text
ORG_ID=118 / TABLE_ID=DT_118N_DEN062
직종별·규모별(2026년 이후)
우선 수집 스코프: 24
  (전국×전규모 1 + 시도×전규모 17 + 전국×비중첩 규모 6)
```

Fact grain:

```text
period
× region
× establishment size
× KECO occupation
```

공식 지표 (`metrics.official`):

```text
current_workers, openings, hires, unfilled,
shortage, planned_hires, shortage_rate
```

파생 지표 (`metrics.derived`):

```text
unfilled_rate, opening_intensity, planned_hire_rate
```

원천 grain·**missing ≠ 0** 규칙·202601 관측값은 [KOSIS Labor Demand](docs/kosis-labor-demand.md)를 본다.

## API

### Health

```text
GET /api/health
```

```bash
curl http://localhost:8081/api/health
```

### Occupation Labor Demand

```text
GET /api/occupations/{occupationCode}/labor-demand
GET /api/occupations/{occupationCode}/labor-demand/history
```

Query (optional, FormRequest 검증):

| 파라미터 | 기본값 | 의미 |
|---|---|---|
| `region_code` | 전국 | 지역 |
| `size_code` | 전규모 | 사업체 규모 |

```bash
curl http://localhost:8081/api/occupations/133/labor-demand
curl 'http://localhost:8081/api/occupations/133/labor-demand?region_code=15118REG2012_00&size_code=13102110322SIZES.00'
curl http://localhost:8081/api/occupations/133/labor-demand/history
```

`133`은 KECO2025 `소프트웨어 개발자`다.  
해당 region×size에 행이 없으면 **404**이며, 0을 합성하지 않는다.

## Documentation

상세 개발환경 구축 및 데이터 초기화:

- [Development Setup](docs/development-setup.md)
- [Database Convention](docs/database-convention.md)
- [KOSIS Labor Demand](docs/kosis-labor-demand.md)
- [EIS Employment Statistics](docs/eis-employment-statistics.md)

## Quick Start

```bash
git clone <repository-url> jbj
cd jbj

cp .env.example .env
cp app/php/.env.example app/php/.env

make build
make up
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

새 DB에서는 `make migrate-baseline`을 실행하지 않는다.

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

확인:

```bash
make migrate-status
make etl-status
make test

curl http://localhost:8081/api/health
curl http://localhost:8081/api/occupations/133/labor-demand
```

## Common Commands

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
make test
```

## Ports

| Service | Host | Container |
|---|---:|---:|
| Nginx | 8081 | 80 |
| MySQL | 3308 | 3306 |
| PHP-FPM | - | 9000 |

## Database Policy

JBJ는 Laravel migration을 사용하지 않습니다.

PHP와 Python이 공유하는 DB schema는 프로젝트 루트의:

```text
/database/migrations
```

에서 관리합니다. 현재 `001`–`006`이 있으며, Python migration runner로 적용합니다.

```bash
make migrate
```

**`php artisan migrate`로 JBJ 공유 스키마를 변경하지 않습니다.**  
이미 적용된 migration은 수정하지 않고 새 migration을 추가합니다.

## Docker Context

JBJ는 Docker Desktop Docker Engine이 아니라 WSL Ubuntu 내부 Docker Engine을 사용합니다.

```bash
docker context show
```

정상:

```text
default
```

## Git / Local Files

Git 제외:

```text
.env
app/php/.env
app/php/vendor/
app/php/node_modules/
data/raw/
```

Raw는 provenance용으로 보존하되, **일반 Git에 raw JSON을 커밋하지 않는 것이 현재 정책**입니다.

Artisan/Composer가 bind mount에 파일을 생성할 때는 가능한 한 `www-data` 사용자로 실행합니다.

## Done (현재)

```text
[완료] Docker / Laravel 13 / PHP 8.5 / MySQL 8.4 / Python 3.12
[완료] SQL migration runner (001–006) / provenance
[완료] KSCO8 / KECO2025 taxonomy
[완료] KOSIS 우선 24스코프 수집·fact 적재
[완료] labor-demand latest / history API
[완료] region_code · size_code 필터 + FormRequest
[완료] official / derived metrics
[완료] Feature · Unit 테스트 (`make test`)
```

## Next

```text
KOSIS Labor Demand Finish (completed: scope test + missing≠0)
→ Canonical Occupation Mapping (active: naming/mapping policy/API)
→ EIS Technical Spike
→ EIS Schema / ETL (only after successful spike)
→ Wage
→ Other Employment Data
→ NCS / Q-Net
→ Search / Detail / Compare UI
```

EIS 기술 조사·개발은 가능하지만, EIS 콘텐츠를 활용한 상용 프로덕션 출시는 고용노동부 사전 협의 완료 전까지 준비 완료 상태가 아니다. 상세 정책과 수집 제약은 [EIS Employment Statistics](docs/eis-employment-statistics.md)를 따른다.
