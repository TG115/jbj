from __future__ import annotations

import argparse
from pathlib import Path

from jbj_etl.db import get_connection
from jbj_etl.migration import (
    baseline_migrations,
    run_migrations,
    show_migration_status,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="JBJ database migration runner."
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    migrate_parser = (
        subparsers.add_parser(
            "up",
            help=(
                "Apply pending migrations."
            ),
        )
    )

    migrate_parser.add_argument(
        "directory",
    )

    status_parser = (
        subparsers.add_parser(
            "status",
            help=(
                "Show migration status."
            ),
        )
    )

    status_parser.add_argument(
        "directory",
    )

    baseline_parser = (
        subparsers.add_parser(
            "baseline",
            help=(
                "Register already-applied "
                "migrations."
            ),
        )
    )

    baseline_parser.add_argument(
        "directory",
    )

    baseline_parser.add_argument(
        "--through",
        type=int,
        required=True,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    directory = Path(
        args.directory
    )

    if not directory.exists():
        raise FileNotFoundError(
            f"Migration directory "
            f"not found: {directory}"
        )

    connection = get_connection(
        allow_multi_statements=True
    )

    try:
        if args.command == "up":
            run_migrations(
                connection,
                directory,
            )

        elif args.command == "status":
            show_migration_status(
                connection,
                directory,
            )

        elif args.command == "baseline":
            baseline_migrations(
                connection,
                directory,
                args.through,
            )

    finally:
        connection.close()


if __name__ == "__main__":
    main()