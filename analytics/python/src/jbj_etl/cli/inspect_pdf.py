from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect text contained in a PDF file."
    )

    parser.add_argument(
        "file",
        help="PDF file path",
    )

    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Page number to start from (1-based)",
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=10,
        help="Number of pages to inspect",
    )

    return parser.parse_args()


def inspect_pdf(
    file_path: Path,
    start_page: int,
    page_count: int,
) -> None:

    reader = PdfReader(file_path)

    print(f"Total pages: {len(reader.pages)}")

    start_index = start_page - 1
    end_index = min(
        start_index + page_count,
        len(reader.pages),
    )

    for page_index in range(
        start_index,
        end_index,
    ):
        page = reader.pages[page_index]

        text = page.extract_text() or ""

        print()
        print("=" * 70)
        print(f"Page {page_index + 1}")
        print("=" * 70)

        print(text.strip())


def main() -> None:
    args = parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    inspect_pdf(
        file_path,
        args.start_page,
        args.pages,
    )


if __name__ == "__main__":
    main()