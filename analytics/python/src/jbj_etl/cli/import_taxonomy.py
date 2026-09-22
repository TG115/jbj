from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from jbj_etl.db import get_connection
from jbj_etl.taxonomy.importer import (
    import_nodes,
    upsert_taxonomy,
)
from jbj_etl.taxonomy.types import TaxonomyRow
from jbj_etl.taxonomy.validator import (
    validate_rows,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Import occupation taxonomy "
            "into JBJ database."
        )
    )

    parser.add_argument(
        "--code",
        required=True,
    )

    parser.add_argument(
        "--version",
        required=True,
    )

    parser.add_argument(
        "--name",
        required=True,
    )

    parser.add_argument(
        "--file",
        required=True,
    )

    parser.add_argument(
        "--country",
        default="KR",
    )

    parser.add_argument(
        "--source-url",
        default=None,
    )

    return parser.parse_args()


def load_csv(
    file_path: Path,
) -> list[TaxonomyRow]:

    rows: list[TaxonomyRow] = []

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
            raise ValueError(
                "CSV header가 없습니다."
            )

        missing = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing:
            raise ValueError(
                "필수 컬럼이 없습니다: "
                f"{sorted(missing)}"
            )

        for line_number, raw in enumerate(
            reader,
            start=2,
        ):
            code = raw["code"].strip()
            name_ko = (
                raw["name_ko"].strip()
            )

            parent_code = (
                raw["parent_code"].strip()
                or None
            )

            try:
                level = int(
                    raw["level"]
                )
            except ValueError as exc:
                raise ValueError(
                    f"{line_number}행 "
                    "level 값이 "
                    "숫자가 아닙니다."
                ) from exc

            if not code:
                raise ValueError(
                    f"{line_number}행 "
                    "code가 비어 있습니다."
                )

            if not name_ko:
                raise ValueError(
                    f"{line_number}행 "
                    "name_ko가 "
                    "비어 있습니다."
                )

            rows.append(
                {
                    "code": code,
                    "name_ko": name_ko,
                    "level": level,
                    "parent_code":
                        parent_code,
                }
            )

    return rows


def main() -> None:
    args = parse_args()

    file_path = Path(
        args.file
    )

    if not file_path.exists():
        print(
            f"File not found: "
            f"{file_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        rows = load_csv(
            file_path
        )

        validate_rows(rows)

        print(
            f"Validated: "
            f"{len(rows)} nodes"
        )

        connection = get_connection()

        try:
            taxonomy_id = (
                upsert_taxonomy(
                    connection,
                    code=args.code,
                    version=args.version,
                    name=args.name,
                    country=args.country,
                    source_url=(
                        args.source_url
                    ),
                )
            )

            imported_count = (
                import_nodes(
                    connection,
                    taxonomy_id,
                    rows,
                )
            )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

        print(
            "Import complete: "
            f"{args.code} "
            f"{args.version}"
        )

        print(
            f"Taxonomy ID: "
            f"{taxonomy_id}"
        )

        print(
            f"Nodes processed: "
            f"{imported_count}"
        )

    except Exception as exc:
        print(
            f"Import failed: {exc}",
            file=sys.stderr,
        )

        sys.exit(1)


if __name__ == "__main__":
    main()