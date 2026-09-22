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

REGION_NATIONWIDE = (
    "15118REG2012_00"
)

SIZE_ALL = (
    "13102110322SIZES.00"
)


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

    raw_file = Path(
        "/data/raw/kosis/"
        f"{TABLE_ID}/data/"
        f"{period}_nationwide_all_size.json"
    )

    connection = get_connection()

    etl_run_id = None

    try:
        source = get_data_source(
            connection,
            "KOSIS_LABOR_DEMAND",
        )

        etl_run_id = start_etl_run(
            connection,
            data_source_id=int(
                source["data_source_id"]
            ),
            job_name=(
                "collect_kosis_labor_demand"
            ),
            parameters={
                "org_id": ORG_ID,
                "table_id": TABLE_ID,
                "period": period,
                "region": REGION_NATIONWIDE,
                "size": SIZE_ALL,
                "occupation": "ALL",
                "items": "ALL",
            },
        )

        connection.commit()

        client = KosisClient()

        payload = (
            client.get_parameter_data(
                org_id=ORG_ID,
                table_id=TABLE_ID,

                obj_l1=(
                    REGION_NATIONWIDE
                ),

                obj_l2=SIZE_ALL,

                obj_l3="ALL",

                item_id="ALL",

                period_type="S",

                start_period=period,
                end_period=period,
            )
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
            data_source_id=int(
                source["data_source_id"]
            ),
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

        print()
        print(
            "KOSIS labor demand import complete"
        )
        print(
            f"Period: {period}"
        )
        print(
            f"Processed: "
            f"{result.processed_count}"
        )
        print(
            f"Inserted: "
            f"{result.inserted_count}"
        )
        print(
            f"Updated: "
            f"{result.updated_count}"
        )
        print(
            f"Raw: {raw_file}"
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

    finally:
        connection.close()


if __name__ == "__main__":
    main()