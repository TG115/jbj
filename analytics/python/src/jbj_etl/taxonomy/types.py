from __future__ import annotations

from typing import TypedDict


class TaxonomyRow(TypedDict):
    code: str
    name_ko: str
    level: int
    parent_code: str | None