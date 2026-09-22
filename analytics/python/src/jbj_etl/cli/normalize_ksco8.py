from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from jbj_etl.taxonomy.normalizers.ksco8 import (
    normalize_ksco8,
)
from jbj_etl.taxonomy.types import TaxonomyRow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize KSCO8 HWPX "
            "into JBJ taxonomy CSV."
        )
    )

    parser.add_argument(
        "input",
    )

    parser.add_argument(
        "output",
    )

    return parser.parse_args()


def write_csv(
    file_path: Path,
    rows: list[TaxonomyRow],
) -> None:

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with file_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as fp:

        writer = csv.DictWriter(
            fp,
            fieldnames=[
                "code",
                "name_ko",
                "level",
                "parent_code",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)


def print_summary(
    rows: list[TaxonomyRow],
) -> None:

    counts = Counter(
        row["level"]
        for row in rows
    )

    print()
    print(
        "KSCO8 normalization complete"
    )
    print(
        "----------------------------"
    )

    for level in sorted(counts):
        print(
            f"Level {level}: "
            f"{counts[level]}"
        )

    print(
        "----------------------------"
    )
    print(
        f"Total: {len(rows)}"
    )


def main() -> None:
    args = parse_args()

    input_path = Path(
        args.input
    )

    output_path = Path(
        args.output
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"File not found: "
            f"{input_path}"
        )

    rows = normalize_ksco8(
        input_path
    )

    write_csv(
        output_path,
        rows,
    )

    print_summary(rows)

    print()
    print(
        f"Output: {output_path}"
    )


if __name__ == "__main__":
    main()