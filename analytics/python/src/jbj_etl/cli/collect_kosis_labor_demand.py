from __future__ import annotations

import argparse
import json
from pathlib import Path

from jbj_etl.db import get_connection

from jbj_etl.etl import (
    attach_source_file,
    complete_etl_run,
    fail_etl_run,
    get_data_source,
    start_etl_run,
)

from jbj_etl.labor_demand.collection_plan import (
    LaborDemandScope,
    build_priority_scopes,
)

from jbj_etl.labor_demand.importer import (
    import_labor_demand,
)

from jbj_etl.labor_demand.normalizer import (
    normalize_labor_demand,
)

from jbj_etl.providers.kosis.client import (
    KosisClient,
)


ORG_ID = "118"
TABLE_ID = "DT_118N_DEN062"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect KOSIS labor demand data."
        )
    )

    parser.add_argument(
        "--period",
        required=True,
        help=(
            "Half-year period. "
            "Example: 202601"
        ),
    )

    return parser.parse_args()


def save_raw_json(
    file_path: Path,
    payload: object,
) -> None:

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as fp:
        json.dump(
            payload,
            fp,
            ensure_ascii=False,
            indent=2,
        )

def collect_scope(
    connection,
    client: KosisClient,
    data_source_id: int,
    period: str,
    scope: LaborDemandScope,
) -> None:
    raw_file = (
        Path("/data/raw/kosis")
        / TABLE_ID
        / "data"
        / period
        / f"{scope.slug}.json"
    )

    etl_run_id = None

    try:
        etl_run_id = start_etl_run(
            connection,
            data_source_id=data_source_id,
            job_name=(
                "collect_kosis_labor_demand"
            ),
            parameters={
                "org_id": ORG_ID,
                "table_id": TABLE_ID,
                "period": period,

                "scope_kind": scope.kind,

                "region_code":
                    scope.region.code,

                "region_name":
                    scope.region.name,

                "size_code":
                    scope.size.code,

                "size_name":
                    scope.size.name,

                "occupation": "ALL",
                "items": "ALL",
            },
        )

        connection.commit()

        payload = client.get_parameter_data(
            org_id=ORG_ID,
            table_id=TABLE_ID,

            obj_l1=scope.region.code,
            obj_l2=scope.size.code,

            obj_l3="ALL",
            item_id="ALL",

            period_type="S",

            start_period=period,
            end_period=period,
        )

        if not isinstance(
            payload,
            list,
        ):
            raise RuntimeError(
                "KOSIS 응답이 list가 아닙니다."
            )

        save_raw_json(
            raw_file,
            payload,
        )

        attach_source_file(
            connection,
            etl_run_id=etl_run_id,
            source_file=raw_file,
        )

        rows = normalize_labor_demand(
            payload
        )

        result = import_labor_demand(
            connection,
            data_source_id=data_source_id,
            etl_run_id=etl_run_id,
            rows=rows,
        )

        complete_etl_run(
            connection,
            etl_run_id=etl_run_id,

            processed_count=(
                result.processed_count
            ),

            inserted_count=(
                result.inserted_count
            ),

            updated_count=(
                result.updated_count
            ),
        )

        connection.commit()

        print(
            f"  Processed: "
            f"{result.processed_count}"
        )
        print(
            f"  Inserted: "
            f"{result.inserted_count}"
        )
        print(
            f"  Updated: "
            f"{result.updated_count}"
        )
        print(
            f"  Raw: {raw_file}"
        )

    except Exception as exc:
        connection.rollback()

        if etl_run_id is not None:
            fail_etl_run(
                connection,
                etl_run_id=etl_run_id,
                error_message=str(exc),
            )

            connection.commit()

        raise


def main() -> None:
    args = parse_args()

    period = args.period

    if (
        len(period) != 6
        or not period.isdigit()
        or period[-2:] not in {
            "01",
            "02",
        }
    ):
        raise ValueError(
            "period는 YYYY01 또는 YYYY02 "
            "형식이어야 합니다."
        )

    connection = get_connection()

    try:
        source = get_data_source(
            connection,
            "KOSIS_LABOR_DEMAND",
        )

        data_source_id = int(
            source["data_source_id"]
        )

        client = KosisClient()

        scopes = build_priority_scopes()

        print()
        print(
            "KOSIS labor demand collection start"
        )
        print(
            f"Period: {period}"
        )
        print(
            f"Scopes: {len(scopes)}"
        )
        print()

        for index, scope in enumerate(
            scopes,
            start=1,
        ):
            print(
                f"[{index}/{len(scopes)}] "
                f"{scope.region.name} / "
                f"{scope.size.name}"
            )

            collect_scope(
                connection=connection,
                client=client,
                data_source_id=data_source_id,
                period=period,
                scope=scope,
            )

            print(
                "  Status: SUCCESS"
            )
            print()

        print(
            "KOSIS labor demand collection complete"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    main()