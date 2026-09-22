from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jbj_etl.providers.kosis.client import (
    KosisClient,
)


ITEMS = {
    "current_workers":
        "13103110322DD_1",

    "openings":
        "13103110322DD_2",

    "hires":
        "13103110322DD_3",

    "unfilled":
        "13103110322DD_4",

    "shortage":
        "13103110322DD_5",

    "planned_hires":
        "13103110322DD_7",

    "shortage_rate":
        "13103110322DD_6",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect one KOSIS labor demand "
            "data point."
        )
    )

    parser.add_argument(
        "--output",
        required=True,
    )

    return parser.parse_args()


def save_json(
    file_path: Path,
    payload: Any,
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

    client = KosisClient()

    rows: list[dict] = []

    for metric_name, item_id in ITEMS.items():

        payload = client.get_parameter_data(
            org_id="118",
            table_id="DT_118N_DEN062",

            # 전국
            obj_l1="15118REG2012_00",

            # 전규모(1인이상)
            obj_l2="13102110322SIZES.00",

            # KECO 133 소프트웨어 개발자
            obj_l3="keco2026_133",

            item_id=item_id,

            # 반기
            period_type="S",

            # 2026년 상반기
            start_period="202601",
            end_period="202601",
        )

        if not payload:
            raise RuntimeError(
                f"데이터가 없습니다: "
                f"{metric_name}"
            )

        for row in payload:
            row["_metric_name"] = (
                metric_name
            )

            rows.append(row)

    print()
    print(
        "=== KOSIS LABOR DEMAND SAMPLE ==="
    )

    for row in rows:
        print(
            f"{row.get('_metric_name')}: "
            f"{row.get('DT')} "
            f"{row.get('UNIT_NM', '')}"
        )

        print(
            f"  period: "
            f"{row.get('PRD_DE')}"
        )

        print(
            f"  region: "
            f"{row.get('C1')} / "
            f"{row.get('C1_NM')}"
        )

        print(
            f"  size: "
            f"{row.get('C2')} / "
            f"{row.get('C2_NM')}"
        )

        print(
            f"  occupation: "
            f"{row.get('C3')} / "
            f"{row.get('C3_NM')}"
        )

    output_path = Path(
        args.output
    )

    save_json(
        output_path,
        rows,
    )

    print()
    print(
        f"Raw sample saved: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()