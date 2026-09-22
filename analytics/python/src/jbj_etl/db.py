from __future__ import annotations

import pymysql
from pymysql.connections import Connection

from jbj_etl.config import get_database_config


def get_connection() -> Connection:
    config = get_database_config()

    return pymysql.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )