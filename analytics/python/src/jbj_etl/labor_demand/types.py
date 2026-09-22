from __future__ import annotations

from typing import TypedDict


class LaborDemandRow(TypedDict):
    period_code: str
    reference_year: int
    reference_half: int

    region_member_code: str
    region_name: str

    establishment_size_member_code: str
    establishment_size_name: str

    source_occupation_member_code: str
    source_occupation_name: str

    occupation_code: str

    current_workers_count: int | None
    openings_count: int | None
    hires_count: int | None
    unfilled_count: int | None
    shortage_count: int | None
    planned_hires_count: int | None

    shortage_rate: float | None