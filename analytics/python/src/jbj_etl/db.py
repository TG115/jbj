from __future__ import annotations

import pymysql
from pymysql.connections import Connection
from pymysql.constants import CLIENT

from jbj_etl.config import get_database_config


def get_connection(
    *,
    allow_multi_statements: bool = False,
) -> Connection:
    config = get_database_config()

    options = {
        "host": config.host,
        "port": config.port,
        "user": config.user,
        "password": config.password,
        "database": config.database,
        "charset": "utf8mb4",
        "autocommit": False,
        "cursorclass": pymysql.cursors.DictCursor,
    }

    if allow_multi_statements:
        options["client_flag"] = CLIENT.MULTI_STATEMENTS

    return pymysql.connect(**options)