from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class KosisMember:
    code: str
    name: str


@dataclass(frozen=True)
class LaborDemandScope:
    kind: Literal["baseline", "region", "size"]

    region: KosisMember
    size: KosisMember

    @property
    def slug(self) -> str:
        return (
            f"{self.kind}_"
            f"{self.region.code.split('_')[-1]}_"
            f"{self.size.code.split('.')[-1]}"
        )


NATIONWIDE = KosisMember(
    code="15118REG2012_00",
    name="전국",
)


REGIONS = (
    KosisMember(
        code="15118REG2012_11",
        name="서울특별시",
    ),
    KosisMember(
        code="15118REG2012_21",
        name="부산광역시",
    ),
    KosisMember(
        code="15118REG2012_22",
        name="대구광역시",
    ),
    KosisMember(
        code="15118REG2012_23",
        name="인천광역시",
    ),
    KosisMember(
        code="15118REG2012_24",
        name="광주광역시",
    ),
    KosisMember(
        code="15118REG2012_25",
        name="대전광역시",
    ),
    KosisMember(
        code="15118REG2012_26",
        name="울산광역시",
    ),
    KosisMember(
        code="15118REG2012_29",
        name="세종특별자치시",
    ),
    KosisMember(
        code="15118REG2012_31",
        name="경기도",
    ),
    KosisMember(
        code="15118REG2012_32",
        name="강원특별자치도",
    ),
    KosisMember(
        code="15118REG2012_33",
        name="충청북도",
    ),
    KosisMember(
        code="15118REG2012_34",
        name="충청남도",
    ),
    KosisMember(
        code="15118REG2012_35",
        name="전북특별자치도",
    ),
    KosisMember(
        code="15118REG2012_36",
        name="전라남도",
    ),
    KosisMember(
        code="15118REG2012_37",
        name="경상북도",
    ),
    KosisMember(
        code="15118REG2012_38",
        name="경상남도",
    ),
    KosisMember(
        code="15118REG2012_39",
        name="제주특별자치도",
    ),
)


ALL_SIZE = KosisMember(
    code="13102110322SIZES.00",
    name="전규모(1인이상)",
)


SIZE_BANDS = (
    KosisMember(
        code="13102110322SIZES.02",
        name="0규모(5인미만)",
    ),
    KosisMember(
        code="13102110322SIZES.03",
        name="1규모(5~9인)",
    ),
    KosisMember(
        code="13102110322SIZES.04",
        name="2규모(10~29인)",
    ),
    KosisMember(
        code="13102110322SIZES.05",
        name="3규모(30~99인)",
    ),
    KosisMember(
        code="13102110322SIZES.06",
        name="4규모(100~299인)",
    ),
    KosisMember(
        code="13102110322SIZES.07",
        name="5규모(300인이상)",
    ),
)


def build_priority_scopes() -> tuple[LaborDemandScope, ...]:
    scopes: list[LaborDemandScope] = []

    # 1. 전국 × 전규모
    scopes.append(
        LaborDemandScope(
            kind="baseline",
            region=NATIONWIDE,
            size=ALL_SIZE,
        )
    )

    # 2. 지역 비교: 각 시도 × 전규모
    for region in REGIONS:
        scopes.append(
            LaborDemandScope(
                kind="region",
                region=region,
                size=ALL_SIZE,
            )
        )

    # 3. 규모 비교: 전국 × 비중첩 규모
    for size in SIZE_BANDS:
        scopes.append(
            LaborDemandScope(
                kind="size",
                region=NATIONWIDE,
                size=size,
            )
        )

    return tuple(scopes)