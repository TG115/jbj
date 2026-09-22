from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jbj_etl.providers.kosis.client import (
    KosisClient,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect KOSIS table metadata."
        )
    )

    parser.add_argument(
        "--org-id",
        required=True,
    )

    parser.add_argument(
        "--table-id",
        required=True,
    )

    parser.add_argument(
        "--output-dir",
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


def print_table(
    payload: Any,
) -> None:

    print()
    print("=== TABLE ===")

    for row in payload:
        print(
            row.get("TBL_NM"),
        )


def print_items(
    payload: Any,
) -> None:

    print()
    print("=== OBJECTS ===")

    objects: dict[str, str] = {}

    items: dict[str, tuple[str, str]] = {}

    for row in payload:
        obj_id = row.get("OBJ_ID")
        obj_name = row.get("OBJ_NM")

        if obj_id:
            objects[obj_id] = (
                obj_name or ""
            )

        item_id = row.get("ITM_ID")
        item_name = row.get("ITM_NM")
        unit_name = row.get("UNIT_NM")

        if item_id:
            items[item_id] = (
                item_name or "",
                unit_name or "",
            )

    for obj_id, obj_name in objects.items():
        print(
            f"{obj_id}: {obj_name}"
        )

    print()
    print("=== ITEMS ===")

    for item_id, (
        item_name,
        unit_name,
    ) in items.items():

        print(
            f"{item_id}: "
            f"{item_name} "
            f"[{unit_name}]"
        )


def print_periods(
    payload: Any,
) -> None:

    print()
    print("=== PERIODS ===")

    periods: list[str] = []

    for row in payload:
        period = row.get("PRD_DE")

        if period:
            periods.append(
                str(period)
            )

    periods = sorted(
        set(periods)
    )

    print(
        f"Count: {len(periods)}"
    )

    if periods:
        print(
            f"First: {periods[0]}"
        )

        print(
            f"Last: {periods[-1]}"
        )

        print(
            "Recent:",
            ", ".join(
                periods[-10:]
            ),
        )


def main() -> None:
    args = parse_args()

    client = KosisClient()

    output_dir = Path(
        args.output_dir
    )

    table = client.get_table(
        org_id=args.org_id,
        table_id=args.table_id,
    )

    items = client.get_items(
        org_id=args.org_id,
        table_id=args.table_id,
    )

    periods = client.get_periods(
        org_id=args.org_id,
        table_id=args.table_id,
    )

    save_json(
        output_dir / "table.json",
        table,
    )

    save_json(
        output_dir / "items.json",
        items,
    )

    save_json(
        output_dir / "periods.json",
        periods,
    )

    print_table(table)
    print_items(items)
    print_periods(periods)

    print()
    print(
        f"Raw metadata saved: "
        f"{output_dir}"
    )


if __name__ == "__main__":
    main()