# JBJ

**Job by Job — 직업을 데이터로 비교하다.**

JBJ(직바직)는 여러 공식 직업·노동시장 데이터를 연결해 직업을 탐색하고 비교할 수 있도록 만드는 커리어 데이터 서비스입니다.

현재는 직업분류, KOSIS 노동수요 파이프라인, Laravel API 기반을 구축하고 있습니다.

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
- SQL Migration Runner
- ETL provenance (`data_source`, `etl_run`)

## Current Data

### Occupation Taxonomies

```text
KSCO8      1,999 nodes
KECO2025     680 nodes
```

### KOSIS Labor Demand

```text
DT_118N_DEN062
직종별·규모별(2026년 이후)
```

Fact grain:

```text
period
× region
× establishment size
× KECO occupation
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
```

```bash
curl http://localhost:8081/api/occupations/133/labor-demand
```

`133`은 KECO2025 `소프트웨어 개발자`다.

## Development

상세 개발환경 구축 및 데이터 초기화:

- [Development Setup](docs/development-setup.md)
- [Database Convention](docs/database-convention.md)

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

에서 관리합니다.

```bash
make migrate
```

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

Artisan/Composer가 bind mount에 파일을 생성할 때는 가능한 한 `www-data` 사용자로 실행합니다.

## Next

```text
Laravel Feature Test
→ Labor Demand Metric Layer
→ Labor Demand History / Region / Size
→ KOSIS Wage
→ Canonical Occupation Mapping
→ Employment / Region Data
→ NCS / Q-Net
→ Search / Detail / Compare UI
→ CI/CD / Deployment
```
