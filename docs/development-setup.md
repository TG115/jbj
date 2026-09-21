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

## 4. Docker Compose 확인

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

