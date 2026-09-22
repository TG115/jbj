from __future__ import annotations

from jbj_etl.taxonomy.types import TaxonomyRow


def validate_rows(
    rows: list[TaxonomyRow],
) -> None:
    if not rows:
        raise ValueError(
            "가져올 데이터가 없습니다."
        )

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
                    f"{row['code']}는 "
                    f"level {row['level']}인데 "
                    "parent_code가 없습니다."
                )

            continue

        parent = by_code.get(parent_code)

        if parent is None:
            raise ValueError(
                f"{row['code']}의 parent_code "
                f"{parent_code}가 존재하지 않습니다."
            )

        expected_parent_level = (
            row["level"] - 1
        )

        if (
            parent["level"]
            != expected_parent_level
        ):
            raise ValueError(
                f"{row['code']}의 부모 level이 "
                "올바르지 않습니다. "
                f"child={row['level']}, "
                f"parent={parent['level']}"
            )