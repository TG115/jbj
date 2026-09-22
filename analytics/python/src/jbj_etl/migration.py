from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass
from pathlib import Path

from pymysql.connections import Connection


MIGRATION_PATTERN = re.compile(
    r"^(?P<version>\d{3})_(?P<name>.+)\.sql$"
)


@dataclass(frozen=True)
class Migration:
    version: int
    file_name: str
    path: Path
    checksum: str


def calculate_checksum(
    file_path: Path,
) -> str:
    sha256 = hashlib.sha256()

    with file_path.open("rb") as fp:
        while True:
            chunk = fp.read(
                1024 * 1024
            )

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def discover_migrations(
    directory: Path,
) -> list[Migration]:
    migrations: list[Migration] = []

    versions: set[int] = set()

    for file_path in sorted(
        directory.glob("*.sql")
    ):
        match = MIGRATION_PATTERN.match(
            file_path.name
        )

        if match is None:
            print(
                "Ignoring migration file "
                f"with invalid name: "
                f"{file_path.name}"
            )

            continue

        version = int(
            match.group("version")
        )

        if version in versions:
            raise ValueError(
                "중복 migration version입니다: "
                f"{version:03d}"
            )

        versions.add(version)

        migrations.append(
            Migration(
                version=version,
                file_name=file_path.name,
                path=file_path,
                checksum=calculate_checksum(
                    file_path
                ),
            )
        )

    migrations.sort(
        key=lambda migration:
        migration.version
    )

    return migrations


def ensure_schema_migration_table(
    connection: Connection,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS
            schema_migration (
                schema_migration_id
                    BIGINT UNSIGNED
                    AUTO_INCREMENT
                    PRIMARY KEY,

                migration_version
                    INT UNSIGNED
                    NOT NULL,

                migration_name
                    VARCHAR(255)
                    NOT NULL,

                checksum_sha256
                    CHAR(64)
                    NOT NULL,

                is_baseline
                    BOOLEAN
                    NOT NULL
                    DEFAULT FALSE,

                execution_time_ms
                    INT UNSIGNED
                    NOT NULL
                    DEFAULT 0,

                applied_at
                    TIMESTAMP
                    NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT
                    uq_schema_migration_version
                    UNIQUE (
                        migration_version
                    ),

                CONSTRAINT
                    uq_schema_migration_name
                    UNIQUE (
                        migration_name
                    )
            )
            ENGINE=InnoDB
            DEFAULT CHARSET=utf8mb4
            COLLATE=utf8mb4_unicode_ci
            """
        )

    connection.commit()


def get_applied_migrations(
    connection: Connection,
) -> dict[int, dict]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                migration_version,
                migration_name,
                checksum_sha256,
                is_baseline,
                execution_time_ms,
                applied_at
            FROM schema_migration
            ORDER BY migration_version
            """
        )

        rows = cursor.fetchall()

    return {
        int(row["migration_version"]):
        row
        for row in rows
    }


def verify_checksum(
    migration: Migration,
    applied: dict,
) -> None:
    if (
        applied["checksum_sha256"]
        != migration.checksum
    ):
        raise RuntimeError(
            "이미 적용된 migration이 "
            "수정되었습니다.\n"
            f"Migration: "
            f"{migration.file_name}\n"
            "기존 migration 파일은 "
            "수정하지 말고 새 migration을 "
            "추가해야 합니다."
        )


def execute_migration(
    connection: Connection,
    migration: Migration,
) -> None:
    sql = migration.path.read_text(
        encoding="utf-8"
    )

    started = time.perf_counter()

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)

            # 여러 SQL statement의 결과를
            # 끝까지 소비한다.
            while cursor.nextset():
                pass

        elapsed_ms = int(
            (
                time.perf_counter()
                - started
            )
            * 1000
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO schema_migration (
                    migration_version,
                    migration_name,
                    checksum_sha256,
                    is_baseline,
                    execution_time_ms
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    FALSE,
                    %s
                )
                """,
                (
                    migration.version,
                    migration.file_name,
                    migration.checksum,
                    elapsed_ms,
                ),
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise


def run_migrations(
    connection: Connection,
    directory: Path,
) -> None:
    ensure_schema_migration_table(
        connection
    )

    migrations = discover_migrations(
        directory
    )

    applied = get_applied_migrations(
        connection
    )

    applied_count = 0

    for migration in migrations:
        existing = applied.get(
            migration.version
        )

        if existing is not None:
            verify_checksum(
                migration,
                existing,
            )

            print(
                "[SKIP] "
                f"{migration.file_name}"
            )

            continue

        print(
            "[RUN ] "
            f"{migration.file_name}"
        )

        execute_migration(
            connection,
            migration,
        )

        print(
            "[DONE] "
            f"{migration.file_name}"
        )

        applied_count += 1

    print()
    print(
        "Migration complete: "
        f"{applied_count} applied"
    )


def baseline_migrations(
    connection: Connection,
    directory: Path,
    through_version: int,
) -> None:
    ensure_schema_migration_table(
        connection
    )

    migrations = discover_migrations(
        directory
    )

    applied = get_applied_migrations(
        connection
    )

    baseline_count = 0

    for migration in migrations:
        if (
            migration.version
            > through_version
        ):
            continue

        existing = applied.get(
            migration.version
        )

        if existing is not None:
            verify_checksum(
                migration,
                existing,
            )

            print(
                "[SKIP] "
                f"{migration.file_name}"
            )

            continue

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO schema_migration (
                    migration_version,
                    migration_name,
                    checksum_sha256,
                    is_baseline,
                    execution_time_ms
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    TRUE,
                    0
                )
                """,
                (
                    migration.version,
                    migration.file_name,
                    migration.checksum,
                ),
            )

        connection.commit()

        print(
            "[BASELINE] "
            f"{migration.file_name}"
        )

        baseline_count += 1

    print()
    print(
        "Baseline complete: "
        f"{baseline_count} registered"
    )


def show_migration_status(
    connection: Connection,
    directory: Path,
) -> None:
    ensure_schema_migration_table(
        connection
    )

    migrations = discover_migrations(
        directory
    )

    applied = get_applied_migrations(
        connection
    )

    print(
        "VERSION  STATUS     MIGRATION"
    )

    print(
        "-------  ---------  "
        "----------------------------------------"
    )

    for migration in migrations:
        existing = applied.get(
            migration.version
        )

        if existing is None:
            status = "PENDING"

        elif (
            existing["checksum_sha256"]
            != migration.checksum
        ):
            status = "CHANGED"

        elif existing["is_baseline"]:
            status = "BASELINE"

        else:
            status = "APPLIED"

        print(
            f"{migration.version:03d}"
            f"      "
            f"{status:<9}"
            f"  "
            f"{migration.file_name}"
        )