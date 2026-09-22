from __future__ import annotations

from pymysql.connections import Connection

from jbj_etl.taxonomy.types import TaxonomyRow


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

        return int(
            result["occupation_taxonomy_id"]
        )


def import_nodes(
    connection: Connection,
    taxonomy_id: int,
    rows: list[TaxonomyRow],
) -> int:

    sorted_rows = sorted(
        rows,
        key=lambda row: (
            row["level"],
            row["code"],
        ),
    )

    node_ids: dict[str, int] = {}

    with connection.cursor() as cursor:

        for row in sorted_rows:
            parent_id = None

            if row["parent_code"] is not None:
                parent_id = node_ids[
                    row["parent_code"]
                ]

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
                        VALUES(
                            parent_occupation_taxonomy_node_id
                        ),
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
                    f"node 조회 실패: "
                    f"{row['code']}"
                )

            node_ids[row["code"]] = int(
                result[
                    "occupation_taxonomy_node_id"
                ]
            )

    return len(sorted_rows)