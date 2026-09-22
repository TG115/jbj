from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from zipfile import ZipFile

from jbj_etl.taxonomy.types import TaxonomyRow
from jbj_etl.taxonomy.validator import validate_rows


CODE_PATTERN = re.compile(
    r"^[0-9A-Z]{1,5}$"
)

EXPECTED_COUNTS = {
    1: 10,
    2: 57,
    3: 167,
    4: 495,
    5: 1270,
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalize_text(text: str) -> str:
    return " ".join(
        text.split()
    )


def extract_text(
    element: ET.Element,
) -> str:

    texts: list[str] = []

    for child in element.iter():
        if local_name(child.tag) != "t":
            continue

        if child.text:
            texts.append(
                child.text
            )

    return normalize_text(
        "".join(texts)
    )


def extract_rows(
    file_path: Path,
) -> list[TaxonomyRow]:

    by_code: dict[str, TaxonomyRow] = {}

    with ZipFile(file_path) as archive:

        section_files = sorted(
            name
            for name in archive.namelist()
            if name.startswith(
                "Contents/section"
            )
            and name.endswith(".xml")
        )

        for section_file in section_files:

            xml_data = archive.read(
                section_file
            )

            root = ET.fromstring(
                xml_data
            )

            tables = [
                element
                for element in root.iter()
                if local_name(
                    element.tag
                ) == "tbl"
            ]

            for table in tables:

                table_rows = [
                    element
                    for element in table.iter()
                    if local_name(
                        element.tag
                    ) == "tr"
                ]

                for table_row in table_rows:

                    cells = [
                        element
                        for element
                        in table_row.iter()
                        if local_name(
                            element.tag
                        ) == "tc"
                    ]

                    values = [
                        extract_text(cell)
                        for cell in cells
                    ]

                    values = [
                        value
                        for value in values
                        if value
                    ]

                    if len(values) != 2:
                        continue

                    code = values[0].strip()
                    name_ko = values[1].strip()

                    if not CODE_PATTERN.fullmatch(
                        code
                    ):
                        continue

                    level = len(code)

                    parent_code = (
                        code[:-1]
                        if level > 1
                        else None
                    )

                    row: TaxonomyRow = {
                        "code": code,
                        "name_ko": name_ko,
                        "level": level,
                        "parent_code":
                            parent_code,
                    }

                    existing = by_code.get(
                        code
                    )

                    if existing is not None:
                        if (
                            existing["name_ko"]
                            != name_ko
                        ):
                            raise ValueError(
                                "같은 코드에 "
                                "다른 이름이 있습니다: "
                                f"{code}"
                            )

                        continue

                    by_code[code] = row

    return list(
        by_code.values()
    )


def validate_expected_counts(
    rows: list[TaxonomyRow],
) -> None:

    counts = Counter(
        row["level"]
        for row in rows
    )

    for level, expected in (
        EXPECTED_COUNTS.items()
    ):
        actual = counts[level]

        if actual != expected:
            raise ValueError(
                f"KSCO8 level {level} "
                "개수가 올바르지 않습니다. "
                f"expected={expected}, "
                f"actual={actual}"
            )

    expected_total = sum(
        EXPECTED_COUNTS.values()
    )

    if len(rows) != expected_total:
        raise ValueError(
            "KSCO8 전체 노드 개수가 "
            "올바르지 않습니다. "
            f"expected={expected_total}, "
            f"actual={len(rows)}"
        )


def normalize_ksco8(
    file_path: Path,
) -> list[TaxonomyRow]:

    rows = extract_rows(
        file_path
    )

    rows.sort(
        key=lambda row: (
            row["level"],
            row["code"],
        )
    )

    validate_rows(rows)

    validate_expected_counts(rows)

    return rows