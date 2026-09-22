from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect HWPX tables."
    )

    parser.add_argument(
        "file",
        help="Path to HWPX file",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Maximum rows to print",
    )

    return parser.parse_args()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def extract_text(element: ET.Element) -> str:
    texts = []

    for child in element.iter():
        if local_name(child.tag) != "t":
            continue

        if child.text:
            texts.append(child.text)

    return "".join(texts).strip()


def inspect_hwpx(
    file_path: Path,
    limit: int,
) -> None:

    with ZipFile(file_path) as archive:
        section_files = sorted(
            name
            for name in archive.namelist()
            if name.startswith("Contents/section")
            and name.endswith(".xml")
        )

        print(f"Sections: {len(section_files)}")

        printed_rows = 0

        for section_file in section_files:
            xml_data = archive.read(section_file)

            root = ET.fromstring(xml_data)

            tables = [
                element
                for element in root.iter()
                if local_name(element.tag) == "tbl"
            ]

            if not tables:
                continue

            print()
            print(
                f"[{section_file}] "
                f"tables={len(tables)}"
            )

            for table_index, table in enumerate(
                tables,
                start=1,
            ):
                print()
                print(f"Table #{table_index}")

                rows = [
                    element
                    for element in table.iter()
                    if local_name(element.tag) == "tr"
                ]

                for row in rows:
                    cells = [
                        element
                        for element in row.iter()
                        if local_name(element.tag) == "tc"
                    ]

                    values = [
                        extract_text(cell)
                        for cell in cells
                    ]

                    if not any(values):
                        continue

                    print(" | ".join(values))

                    printed_rows += 1

                    if printed_rows >= limit:
                        return


def main() -> None:
    args = parse_args()

    file_path = Path(args.file)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    inspect_hwpx(
        file_path,
        args.limit,
    )


if __name__ == "__main__":
    main()