# JBJ

Job by Job — 직업 데이터를 비교하는 서비스

## Development

개발환경 구축 및 데이터 초기화 방법은 아래 문서를 참고합니다.

- [Development Setup](docs/development-setup.md)
- [Database Convention](docs/database-convention.md)

### Quick Start

```bash
git clone <repository-url> jbj
cd jbj

cp .env.example .env

docker compose build
docker compose up -d
```

### DB 초기화:
```bash
docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/migrations/001_create_occupation_taxonomy.sql
```

### 샘플 데이터:
```bash
docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/seeds/001_seed_taxonomy_sample.sql
```

### 접속:
http://localhost:8081

## Ports

| Service | Host | Container |
|---|---:|---:|
| Nginx | 8081 | 80 |
| MySQL | 3308 | 3306 |
| PHP-FPM | - | 9000 |




### Docker Desktop과 WSL Docker Engine 구분

JBJ는 Docker Desktop의 Docker Engine을 사용하지 않는다.

WSL Ubuntu 내부에 설치된 Docker Engine을 사용한다.

확인:

```bash
docker context show
```

정상:
```bash
default
```

Docker daemon 확인:
```bash
systemctl status docker
```