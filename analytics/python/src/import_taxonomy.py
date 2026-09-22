from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import TypedDict

import pymysql
from pymysql.connections import Connection


class TaxonomyRow(TypedDict):
    code: str
    name_ko: str
    level: int
    parent_code: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import occupation taxonomy into JBJ database."
    )

    parser.add_argument("--code", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--file", required=True)

    parser.add_argument(
        "--country",
        default="KR",
    )

    parser.add_argument(
        "--source-url",
        default=None,
    )

    return parser.parse_args()


def get_connection() -> Connection:
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_DATABASE"],
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )


def load_csv(file_path: Path) -> list[TaxonomyRow]:
    rows: list[TaxonomyRow] = []

    # utf-8-sig를 사용하면 BOM이 있는 CSV도 처리 가능
    with file_path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as fp:

        reader = csv.DictReader(fp)

        required_columns = {
            "code",
            "name_ko",
            "level",
            "parent_code",
        }

        if reader.fieldnames is None:
            raise ValueError("CSV header가 없습니다.")

        missing = required_columns - set(reader.fieldnames)

        if missing:
            raise ValueError(
                f"필수 컬럼이 없습니다: {sorted(missing)}"
            )

        for line_number, raw in enumerate(reader, start=2):
            code = raw["code"].strip()
            name_ko = raw["name_ko"].strip()
            parent_code = raw["parent_code"].strip() or None

            try:
                level = int(raw["level"])
            except ValueError as exc:
                raise ValueError(
                    f"{line_number}행 level 값이 숫자가 아닙니다."
                ) from exc

            if not code:
                raise ValueError(
                    f"{line_number}행 code가 비어 있습니다."
                )

            if not name_ko:
                raise ValueError(
                    f"{line_number}행 name_ko가 비어 있습니다."
                )

            if level < 1:
                raise ValueError(
                    f"{line_number}행 level은 1 이상이어야 합니다."
                )

            rows.append(
                {
                    "code": code,
                    "name_ko": name_ko,
                    "level": level,
                    "parent_code": parent_code,
                }
            )

    return rows


def validate_rows(rows: list[TaxonomyRow]) -> None:
    if not rows:
        raise ValueError("가져올 데이터가 없습니다.")

    by_code: dict[str, TaxonomyRow] = {}

    for row in rows:
        code = row["code"]

        if code in by_code:
            raise ValueError(
                f"중복 code가 있습니다: {code}"
            )

        by_code[code] = row

    for row in rows:
        parent_code = row["parent_code"]

        if parent_code is None:
            if row["level"] != 1:
                raise ValueError(
                    f"{row['code']}는 level {row['level']}인데 "
                    "parent_code가 없습니다."
                )

            continue

        parent = by_code.get(parent_code)

        if parent is None:
            raise ValueError(
                f"{row['code']}의 parent_code "
                f"{parent_code}가 CSV에 없습니다."
            )

        expected_parent_level = row["level"] - 1

        if parent["level"] != expected_parent_level:
            raise ValueError(
                f"{row['code']}의 부모 level이 올바르지 않습니다. "
                f"child={row['level']}, "
                f"parent={parent['level']}"
            )


def upsert_taxonomy(
    connection: Connection,
    *,
    code: str,
    version: str,
    name: str,
    country: str,
    source_url: str | None,
) -> int:

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO occupation_taxonomy (
                code,
                name,
                version,
                country_code,
                source_url
            )
            VALUES (%s, %s, %s, %s, %s)

            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                source_url = VALUES(source_url),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                code,
                name,
                version,
                country,
                source_url,
            ),
        )

        cursor.execute(
            """
            SELECT occupation_taxonomy_id
            FROM occupation_taxonomy
            WHERE code = %s
              AND version = %s
              AND country_code = %s
            """,
            (
                code,
                version,
                country,
            ),
        )

        result = cursor.fetchone()

        if result is None:
            raise RuntimeError(
                "occupation_taxonomy 조회에 실패했습니다."
            )

        return int(result["occupation_taxonomy_id"])


def import_nodes(
    connection: Connection,
    taxonomy_id: int,
    rows: list[TaxonomyRow],
) -> int:

    rows = sorted(
        rows,
        key=lambda row: (
            row["level"],
            row["code"],
        ),
    )

    node_ids: dict[str, int] = {}

    with connection.cursor() as cursor:

        for row in rows:
            parent_id = None

            if row["parent_code"] is not None:
                parent_id = node_ids[row["parent_code"]]

            cursor.execute(
                """
                INSERT INTO occupation_taxonomy_node (
                    occupation_taxonomy_id,
                    code,
                    name_ko,
                    level,
                    parent_occupation_taxonomy_node_id,
                    is_active
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    TRUE
                )

                ON DUPLICATE KEY UPDATE
                    name_ko = VALUES(name_ko),
                    level = VALUES(level),
                    parent_occupation_taxonomy_node_id =
                        VALUES(parent_occupation_taxonomy_node_id),
                    is_active = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    taxonomy_id,
                    row["code"],
                    row["name_ko"],
                    row["level"],
                    parent_id,
                ),
            )

            cursor.execute(
                """
                SELECT occupation_taxonomy_node_id
                FROM occupation_taxonomy_node
                WHERE occupation_taxonomy_id = %s
                  AND code = %s
                """,
                (
                    taxonomy_id,
                    row["code"],
                ),
            )

            result = cursor.fetchone()

            if result is None:
                raise RuntimeError(
                    f"node 조회 실패: {row['code']}"
                )

            node_ids[row["code"]] = int(
                result["occupation_taxonomy_node_id"]
            )

    return len(rows)


def main() -> None:
    args = parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        print(
            f"File not found: {file_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        rows = load_csv(file_path)

        validate_rows(rows)

        print(
            f"Validated: {len(rows)} nodes"
        )

        connection = get_connection()

        try:
            taxonomy_id = upsert_taxonomy(
                connection,
                code=args.code,
                version=args.version,
                name=args.name,
                country=args.country,
                source_url=args.source_url,
            )

            imported_count = import_nodes(
                connection,
                taxonomy_id,
                rows,
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        print(
            f"Import complete: "
            f"{args.code} {args.version}"
        )

        print(
            f"Taxonomy ID: {taxonomy_id}"
        )

        print(
            f"Nodes processed: {imported_count}"
        )

    except Exception as exc:
        print(
            f"Import failed: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()