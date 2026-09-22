from __future__ import annotations

from dataclasses import dataclass

from pymysql.connections import Connection

from jbj_etl.labor_demand.types import (
    LaborDemandRow,
)


@dataclass(frozen=True)
class ImportResult:
    processed_count: int
    inserted_count: int
    updated_count: int


def get_keco_nodes(
    connection: Connection,
) -> dict[str, int]:

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                n.code,
                n.occupation_taxonomy_node_id
            FROM occupation_taxonomy_node n
            JOIN occupation_taxonomy t
              ON t.occupation_taxonomy_id =
                 n.occupation_taxonomy_id
            WHERE t.code = 'KECO'
              AND t.version = '2025'
            """
        )

        rows = cursor.fetchall()

    return {
        str(row["code"]):
        int(
            row[
                "occupation_taxonomy_node_id"
            ]
        )
        for row in rows
    }


def import_labor_demand(
    connection: Connection,
    *,
    data_source_id: int,
    etl_run_id: int,
    rows: list[LaborDemandRow],
) -> ImportResult:

    keco_nodes = get_keco_nodes(
        connection
    )

    inserted_count = 0
    updated_count = 0

    with connection.cursor() as cursor:

        for row in rows:
            occupation_node_id = (
                keco_nodes.get(
                    row["occupation_code"]
                )
            )

            if occupation_node_id is None:
                raise ValueError(
                    "KECO2025 taxonomy node를 "
                    "찾을 수 없습니다: "
                    f"{row['occupation_code']}"
                )

            cursor.execute(
                """
                INSERT INTO fact_labor_demand (
                    data_source_id,
                    etl_run_id,
                    occupation_taxonomy_node_id,

                    period_code,
                    reference_year,
                    reference_half,

                    region_member_code,
                    region_name,

                    establishment_size_member_code,
                    establishment_size_name,

                    source_occupation_member_code,
                    source_occupation_name,

                    current_workers_count,
                    openings_count,
                    hires_count,
                    unfilled_count,
                    shortage_count,
                    planned_hires_count,
                    shortage_rate
                )
                VALUES (
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s
                )

                ON DUPLICATE KEY UPDATE
                    etl_run_id =
                        VALUES(etl_run_id),

                    region_name =
                        VALUES(region_name),

                    establishment_size_name =
                        VALUES(
                            establishment_size_name
                        ),

                    source_occupation_member_code =
                        VALUES(
                            source_occupation_member_code
                        ),

                    source_occupation_name =
                        VALUES(
                            source_occupation_name
                        ),

                    current_workers_count =
                        VALUES(
                            current_workers_count
                        ),

                    openings_count =
                        VALUES(openings_count),

                    hires_count =
                        VALUES(hires_count),

                    unfilled_count =
                        VALUES(unfilled_count),

                    shortage_count =
                        VALUES(shortage_count),

                    planned_hires_count =
                        VALUES(
                            planned_hires_count
                        ),

                    shortage_rate =
                        VALUES(shortage_rate),

                    updated_at =
                        CURRENT_TIMESTAMP
                """,
                (
                    data_source_id,
                    etl_run_id,
                    occupation_node_id,

                    row["period_code"],
                    row["reference_year"],
                    row["reference_half"],

                    row["region_member_code"],
                    row["region_name"],

                    row[
                        "establishment_size_member_code"
                    ],

                    row[
                        "establishment_size_name"
                    ],

                    row[
                        "source_occupation_member_code"
                    ],

                    row[
                        "source_occupation_name"
                    ],

                    row[
                        "current_workers_count"
                    ],

                    row["openings_count"],
                    row["hires_count"],
                    row["unfilled_count"],
                    row["shortage_count"],

                    row[
                        "planned_hires_count"
                    ],

                    row["shortage_rate"],
                ),
            )

            if cursor.rowcount == 1:
                inserted_count += 1

            elif cursor.rowcount == 2:
                updated_count += 1

    return ImportResult(
        processed_count=len(rows),
        inserted_count=inserted_count,
        updated_count=updated_count,
    )