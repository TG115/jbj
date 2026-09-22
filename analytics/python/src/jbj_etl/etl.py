from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pymysql.connections import Connection


def calculate_sha256(
    file_path: Path,
) -> str:

    sha256 = hashlib.sha256()

    with file_path.open("rb") as fp:
        while True:
            chunk = fp.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def get_data_source(
    connection: Connection,
    source_code: str,
) -> dict:

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                data_source_id,
                source_code,
                name,
                source_url
            FROM data_source
            WHERE source_code = %s
              AND is_active = TRUE
            """,
            (source_code,),
        )

        result = cursor.fetchone()

    if result is None:
        raise ValueError(
            "등록되지 않은 data source입니다: "
            f"{source_code}"
        )

    return result


def start_etl_run(
    connection: Connection,
    *,
    data_source_id: int,
    job_name: str,
    source_file: Path | None = None,
    parameters: dict[str, Any] | None = None,
) -> int:

    source_file_name = None
    checksum = None

    if source_file is not None:
        if not source_file.exists():
            raise FileNotFoundError(
                f"Source file not found: "
                f"{source_file}"
            )

        source_file_name = (
            source_file.name
        )

        checksum = calculate_sha256(
            source_file
        )

    parameters_json = None

    if parameters is not None:
        parameters_json = json.dumps(
            parameters,
            ensure_ascii=False,
        )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO etl_run (
                data_source_id,
                job_name,
                status_code,
                source_file_name,
                source_checksum_sha256,
                parameters_json
            )
            VALUES (
                %s,
                %s,
                'RUNNING',
                %s,
                %s,
                %s
            )
            """,
            (
                data_source_id,
                job_name,
                source_file_name,
                checksum,
                parameters_json,
            ),
        )

        return int(
            cursor.lastrowid
        )


def complete_etl_run(
    connection: Connection,
    *,
    etl_run_id: int,
    processed_count: int,
    inserted_count: int = 0,
    updated_count: int = 0,
    rejected_count: int = 0,
) -> None:

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE etl_run
            SET
                status_code = 'SUCCESS',
                processed_count = %s,
                inserted_count = %s,
                updated_count = %s,
                rejected_count = %s,
                finished_at = CURRENT_TIMESTAMP
            WHERE etl_run_id = %s
            """,
            (
                processed_count,
                inserted_count,
                updated_count,
                rejected_count,
                etl_run_id,
            ),
        )


def fail_etl_run(
    connection: Connection,
    *,
    etl_run_id: int,
    error_message: str,
) -> None:

    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE etl_run
            SET
                status_code = 'FAILED',
                error_message = %s,
                finished_at = CURRENT_TIMESTAMP
            WHERE etl_run_id = %s
            """,
            (
                error_message,
                etl_run_id,
            ),
        )