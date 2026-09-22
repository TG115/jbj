# JBJ Development Setup

## 1. 개발환경 구성

- Windows
- WSL2
- Ubuntu 24.04
- Docker Engine
- Docker Compose
- PHP 8.5
- MySQL 8.4
- Python 3.12
- Nginx

## 2. WSL 설치

## 3. Docker Engine 설치

```bash
sudo apt update

sudo apt install -y git ca-certificates curl

sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

sudo systemctl enable --now docker

sudo usermod -aG docker $USER
```



## 4. Docker Compose 확인

```bash
docker --version
docker compose version
docker context show
docker info
docker compose config
```

아래 정보 확인

```bash
published: "8081"
target: 80

published: "3308"
target: 3306
```



## 5. 프로젝트 Clone



## 6. .env 설정



## 7. Docker Build

```bash
docker compose build
```



## 8. Docker 실행

```bash
#실행
docker compose up -d

#확인
docker compose ps
```

아래 정보 확인

```bash
jbj-nginx-1    Up
jbj-php-1      Up
jbj-mysql-1    Up (healthy)
jbj-python-1   Up
```



## 9. Migration 실행

```bash
docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/migrations/001_create_occupation_taxonomy.sql

docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/migrations/002_create_canonical_occupation.sql

docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/migrations/003_create_canonical_occupation_mapping.sql
```



## 10. Seed 실행

```bash
docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/seeds/001_seed_taxonomy_sample.sql

docker compose exec -T mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  < database/seeds/002_seed_canonical_occupation_sample.sql
```

```bash
#테이블 확인
docker compose exec mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
  -e "SHOW TABLES;"'

#데이터 확인
docker compose exec mysql \
  sh -c 'mysql --default-character-set=utf8mb4 \
  -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" \
  -e "
SELECT
    code,
    name_ko
FROM occupation_taxonomy_node;
"'
```



### 한글이 ì... 형태로 깨지는 경우

SQL import 시 utf8mb4를 명시한다.

```bash
mysql --default-character-set=utf8mb4
```

SQL 파일도 UTF-8인지 확인한다.

```bash
file -bi database/seeds/001_seed_taxonomy_sample.sql
```



## 11. 개발환경 확인



## 12. 자주 사용하는 Docker 명령어



## 문제 해결

