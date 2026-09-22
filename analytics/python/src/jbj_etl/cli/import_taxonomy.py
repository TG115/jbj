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
from jbj_etl.etl import (
    complete_etl_run,
    fail_etl_run,
    get_data_source,
    start_etl_run,
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

    parser.add_argument(
        "--source-code",
        required=True,
    )

    parser.add_argument(
        "--source-file",
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

        etl_run_id = None

        try:
            data_source = get_data_source(
                connection,
                args.source_code,
            )

            source_file = (
                Path(args.source_file)
                if args.source_file
                else None
            )

            etl_run_id = start_etl_run(
                connection,
                data_source_id=int(
                    data_source["data_source_id"]
                ),
                job_name="import_taxonomy",
                source_file=source_file,
                parameters={
                    "taxonomy_code": args.code,
                    "taxonomy_version": args.version,
                },
            )

            # RUNNING 상태를 먼저 확정한다.
            connection.commit()

            taxonomy_id = upsert_taxonomy(
                connection,
                code=args.code,
                version=args.version,
                name=args.name,
                country=args.country,
                source_url=data_source[
                    "source_url"
                ],
            )

            imported_count = import_nodes(
                connection,
                taxonomy_id,
                rows,
            )

            complete_etl_run(
                connection,
                etl_run_id=etl_run_id,
                processed_count=imported_count,
            )

            connection.commit()

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