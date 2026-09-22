from __future__ import annotations

from collections import defaultdict
from typing import Any

from jbj_etl.labor_demand.types import (
    LaborDemandRow,
)


ITEM_TO_FIELD = {
    "13103110322DD_1":
        "current_workers_count",

    "13103110322DD_2":
        "openings_count",

    "13103110322DD_3":
        "hires_count",

    "13103110322DD_4":
        "unfilled_count",

    "13103110322DD_5":
        "shortage_count",

    "13103110322DD_7":
        "planned_hires_count",

    "13103110322DD_6":
        "shortage_rate",
}


def parse_number(
    value: str | None,
    *,
    decimal: bool = False,
) -> int | float | None:

    if value is None:
        return None

    value = value.strip()

    if value in {
        "",
        "-",
        "...",
    }:
        return None

    value = value.replace(
        ",",
        "",
    )

    if decimal:
        return float(value)

    return int(
        float(value)
    )


def extract_occupation_code(
    member_code: str,
) -> str | None:

    prefix = "keco2026_"

    if not member_code.startswith(
        prefix
    ):
        raise ValueError(
            "예상하지 못한 KECO member code입니다: "
            f"{member_code}"
        )

    code = member_code[
        len(prefix):
    ]

    # keco2026_ 자체는 전직종 집계
    if not code:
        return None

    if (
        not code.isdigit()
        or not (1 <= len(code) <= 3)
    ):
        raise ValueError(
            "올바르지 않은 KECO code입니다: "
            f"{member_code}"
        )

    return code


def normalize_labor_demand(
    payload: list[dict[str, Any]],
) -> list[LaborDemandRow]:

    grouped: dict[
        tuple[str, str, str, str],
        dict[str, Any],
    ] = defaultdict(dict)

    for source_row in payload:
        period_code = str(
            source_row["PRD_DE"]
        )

        region_code = str(
            source_row["C1"]
        )

        size_code = str(
            source_row["C2"]
        )

        occupation_member_code = str(
            source_row["C3"]
        )

        occupation_code = (
            extract_occupation_code(
                occupation_member_code
            )
        )

        # 전직종 aggregate는 제외
        if occupation_code is None:
            continue

        key = (
            period_code,
            region_code,
            size_code,
            occupation_member_code,
        )

        row = grouped[key]

        if not row:
            row.update(
                {
                    "period_code":
                        period_code,

                    "reference_year":
                        int(period_code[:4]),

                    "reference_half":
                        int(period_code[-2:]),

                    "region_member_code":
                        region_code,

                    "region_name":
                        source_row["C1_NM"],

                    "establishment_size_member_code":
                        size_code,

                    "establishment_size_name":
                        source_row["C2_NM"],

                    "source_occupation_member_code":
                        occupation_member_code,

                    "source_occupation_name":
                        source_row["C3_NM"],

                    "occupation_code":
                        occupation_code,

                    "current_workers_count":
                        None,

                    "openings_count":
                        None,

                    "hires_count":
                        None,

                    "unfilled_count":
                        None,

                    "shortage_count":
                        None,

                    "planned_hires_count":
                        None,

                    "shortage_rate":
                        None,
                }
            )

        item_id = source_row[
            "ITM_ID"
        ]

        field_name = ITEM_TO_FIELD.get(
            item_id
        )

        if field_name is None:
            continue

        row[field_name] = parse_number(
            source_row.get("DT"),
            decimal=(
                field_name
                == "shortage_rate"
            ),
        )

    result: list[LaborDemandRow] = []

    for row in grouped.values():
        if (
            row["reference_half"]
            not in (1, 2)
        ):
            raise ValueError(
                "올바르지 않은 반기 코드입니다: "
                f"{row['period_code']}"
            )

        missing_metrics = [
            field
            for field in ITEM_TO_FIELD.values()
            if row[field] is None
        ]

        if missing_metrics:
            raise ValueError(
                "노동수요 지표가 누락되었습니다. "
                f"occupation="
                f"{row['occupation_code']}, "
                f"missing="
                f"{missing_metrics}"
            )

        result.append(
            row  # type: ignore[arg-type]
        )

    result.sort(
        key=lambda row: (
            row["period_code"],
            row["occupation_code"],
        )
    )

    return result