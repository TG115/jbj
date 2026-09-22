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
```

## 5. 프로젝트 Clone

## 6. .env 설정

## 7. Docker Build

## 8. Docker 실행

## 9. Migration 실행

## 10. Seed 실행

## 11. 개발환경 확인

## 12. 자주 사용하는 Docker 명령어

## 문제 해결

### 한글이 ì... 형태로 깨지는 경우

SQL import 시 utf8mb4를 명시한다.

```bash
mysql --default-character-set=utf8mb4
```

SQL 파일도 UTF-8인지 확인한다.

```bash
file -bi database/seeds/001_seed_taxonomy_sample.sql
```

