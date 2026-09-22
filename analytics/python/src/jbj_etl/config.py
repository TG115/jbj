from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def get_database_config() -> DatabaseConfig:
    return DatabaseConfig(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_DATABASE"],
    )


@dataclass(frozen=True)
class KosisConfig:
    api_key: str


def get_kosis_config() -> KosisConfig:
    api_key = os.environ.get(
        "KOSIS_API_KEY",
        "",
    ).strip()

    if not api_key:
        raise RuntimeError(
            "KOSIS_API_KEY 환경변수가 없습니다."
        )

    return KosisConfig(
        api_key=api_key,
    )