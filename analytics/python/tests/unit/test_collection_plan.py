"""Regression tests for KOSIS labor-demand priority scopes.

Hardens the *plan structure* (24 = 1 + 17 + 6), not period-specific
row counts such as 2060 / 185 / 45 (those are 202601 observations only).
"""

from __future__ import annotations

import unittest

from jbj_etl.labor_demand.collection_plan import (
    ALL_SIZE,
    NATIONWIDE,
    REGIONS,
    SIZE_BANDS,
    build_priority_scopes,
)


# Non-overlapping size suffixes used by priority size scopes (excludes .00).
NON_OVERLAPPING_SIZE_SUFFIXES = frozenset(
    {"02", "03", "04", "05", "06", "07"},
)


class BuildPriorityScopesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.scopes = build_priority_scopes()

    def test_returns_exactly_24_scopes(self) -> None:
        self.assertEqual(len(self.scopes), 24)

    def test_kind_counts_are_one_baseline_seventeen_region_six_size(self) -> None:
        by_kind = {
            "baseline": 0,
            "region": 0,
            "size": 0,
        }
        for scope in self.scopes:
            by_kind[scope.kind] = by_kind.get(scope.kind, 0) + 1

        self.assertEqual(
            by_kind,
            {"baseline": 1, "region": 17, "size": 6},
        )

    def test_scope_slugs_are_unique(self) -> None:
        slugs = [scope.slug for scope in self.scopes]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_region_size_pairs_are_unique(self) -> None:
        pairs = [(scope.region.code, scope.size.code) for scope in self.scopes]
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_baseline_is_nationwide_all_size(self) -> None:
        baselines = [s for s in self.scopes if s.kind == "baseline"]
        self.assertEqual(len(baselines), 1)

        baseline = baselines[0]
        self.assertEqual(baseline.region, NATIONWIDE)
        self.assertEqual(baseline.size, ALL_SIZE)

    def test_region_scopes_cover_each_sido_with_all_size(self) -> None:
        region_scopes = [s for s in self.scopes if s.kind == "region"]
        self.assertEqual(len(region_scopes), len(REGIONS))

        region_codes = {s.region.code for s in region_scopes}
        self.assertEqual(region_codes, {r.code for r in REGIONS})

        for scope in region_scopes:
            self.assertEqual(scope.size, ALL_SIZE)
            self.assertNotEqual(scope.region, NATIONWIDE)

    def test_size_scopes_are_nationwide_non_overlapping_bands(self) -> None:
        size_scopes = [s for s in self.scopes if s.kind == "size"]
        self.assertEqual(len(size_scopes), len(SIZE_BANDS))

        size_codes = {s.size.code for s in size_scopes}
        self.assertEqual(size_codes, {band.code for band in SIZE_BANDS})

        for scope in size_scopes:
            self.assertEqual(scope.region, NATIONWIDE)
            # Priority size comparison excludes the all-size aggregate.
            self.assertNotEqual(scope.size, ALL_SIZE)
            self.assertNotEqual(scope.size.code, ALL_SIZE.code)

            suffix = scope.size.code.rsplit(".", 1)[-1]
            self.assertIn(suffix, NON_OVERLAPPING_SIZE_SUFFIXES)

    def test_size_band_constants_exclude_all_size_aggregate(self) -> None:
        """SIZE_BANDS itself must stay free of the .00 aggregate."""
        band_codes = {band.code for band in SIZE_BANDS}
        self.assertNotIn(ALL_SIZE.code, band_codes)
        self.assertEqual(len(SIZE_BANDS), 6)


if __name__ == "__main__":
    unittest.main()
