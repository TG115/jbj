from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

from jbj_etl.taxonomy.types import TaxonomyRow
from jbj_etl.taxonomy.validator import validate_rows


EXPECTED_COUNTS = {
    1: 10,
    2: 35,
    3: 140,
    4: 495,
}


# 다음 형태를 모두 코드로 인식한다.
#
# 133
# 1331
# 1 1   -> 11
# 11 0  -> 110
#
# PDF 레이아웃 때문에 숫자 사이에 공백이 들어간 경우를 처리한다.
CODE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?P<code>\d(?:\s*\d){0,3})"
    r"(?=\s*[가-힣A-Za-z(])"
)


def normalize_space(value: str) -> str:
    return " ".join(value.split())


def normalize_code(value: str) -> str:
    return re.sub(r"\s+", "", value)


def extract_keco_page_text(
    file_path: Path,
) -> str:
    reader = PdfReader(file_path)

    for page in reader.pages:
        text = page.extract_text() or ""

        # 산업분류 페이지를 제외하고
        # KECO2025 직업분류 페이지를 찾는다.
        if (
            "경영·사무·금융·보험직" in text
            and "연구직 및 공학 기술직" in text
        ):
            return text

    raise ValueError(
        "KECO2025 직업분류 페이지를 찾지 못했습니다."
    )


def parse_records(text: str) -> list[tuple[str, str]]:
    records: list[tuple[str, str]] = []

    current_code: str | None = None
    current_name_parts: list[str] = []

    started = False

    def flush() -> None:
        nonlocal current_code
        nonlocal current_name_parts

        if current_code is None:
            return

        name = normalize_space(
            " ".join(current_name_parts)
        )

        if name:
            records.append(
                (
                    current_code,
                    name,
                )
            )

        current_code = None
        current_name_parts = []

    for raw_line in text.splitlines():
        line = normalize_space(raw_line)

        if not line:
            continue

        # 실제 KECO 데이터 시작점
        if not started:
            if re.match(
                r"^0\s+경영·사무·금융·보험직",
                line,
            ):
                started = True
            else:
                continue

        # PDF 마지막 footer
        if (
            line.startswith("한국고용직업분류")
            and records
        ):
            break

        matches = list(
            CODE_PATTERN.finditer(line)
        )

        if not matches:
            if current_code is not None:
                current_name_parts.append(line)

            continue

        # 첫 코드 이전에 텍스트가 있다면
        # 이전 분류명의 줄바꿈 부분으로 본다.
        prefix = line[: matches[0].start()].strip()

        if (
            prefix
            and current_code is not None
        ):
            current_name_parts.append(prefix)

        for index, match in enumerate(matches):
            flush()

            code = normalize_code(
                match.group("code")
            )

            # KECO2025는 1~4자리 숫자 코드
            if not (1 <= len(code) <= 4):
                continue

            next_start = (
                matches[index + 1].start()
                if index + 1 < len(matches)
                else len(line)
            )

            name_part = line[
                match.end() : next_start
            ].strip()

            current_code = code

            if name_part:
                current_name_parts.append(
                    name_part
                )

    flush()

    return records


def build_rows(
    records: list[tuple[str, str]],
) -> list[TaxonomyRow]:

    by_code: dict[str, TaxonomyRow] = {}

    for code, name_ko in records:
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
            "parent_code": parent_code,
        }

        existing = by_code.get(code)

        if existing is not None:
            if existing["name_ko"] != name_ko:
                raise ValueError(
                    "같은 KECO 코드에 서로 다른 이름이 "
                    f"있습니다: {code} / "
                    f"{existing['name_ko']} / "
                    f"{name_ko}"
                )

            continue

        by_code[code] = row

    rows = list(by_code.values())

    rows.sort(
        key=lambda row: (
            row["level"],
            row["code"],
        )
    )

    return rows


def validate_expected_counts(
    rows: list[TaxonomyRow],
) -> None:

    counts = Counter(
        row["level"]
        for row in rows
    )

    for level, expected in EXPECTED_COUNTS.items():
        actual = counts[level]

        if actual != expected:
            raise ValueError(
                f"KECO2025 level {level} 개수가 "
                f"올바르지 않습니다. "
                f"expected={expected}, "
                f"actual={actual}"
            )

    expected_total = sum(
        EXPECTED_COUNTS.values()
    )

    if len(rows) != expected_total:
        raise ValueError(
            "KECO2025 전체 노드 개수가 "
            "올바르지 않습니다. "
            f"expected={expected_total}, "
            f"actual={len(rows)}"
        )


def normalize_keco2025(
    file_path: Path,
) -> list[TaxonomyRow]:

    text = extract_keco_page_text(
        file_path
    )

    records = parse_records(text)

    rows = build_rows(records)

    validate_rows(rows)

    validate_expected_counts(rows)

    return rows