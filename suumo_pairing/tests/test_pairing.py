"""
Unit tests for the pairing algorithm (no I/O — pure functions only).

Run:
    python -m pytest suumo_pairing/tests/test_pairing.py -v
"""
import pytest

from suumo_pairing.models import Property
from suumo_pairing.pairing import (
    are_areas_compatible,
    are_room_types_compatible,
    find_pairs_for_tier,
    get_tier,
    is_pair_compatible,
    select_daily_pairs,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_prop(
    nc_id: str,
    price: int,
    room_type: str,
    area: float,
    area_name: str = "A区",
) -> Property:
    return Property(
        nc_id=nc_id,
        name=f"TestBuilding {nc_id}",
        price_jpy=price,
        room_type=room_type,
        area_sqm=area,
        url=f"https://suumo.jp/ms/chuko/tokyo/sc_test/nc_{nc_id}/",
        area_name=area_name,
    )


# ── get_tier ──────────────────────────────────────────────────────────────────

class TestGetTier:
    def test_entry_lower_bound(self):
        assert get_tier(30_000_000) == "入門層"

    def test_entry_upper_bound(self):
        assert get_tier(60_000_000) == "入門層"

    def test_gap_below_mid(self):
        assert get_tier(65_000_000) is None  # 6000万–7000万 gap

    def test_mid_lower_bound(self):
        assert get_tier(70_000_000) == "中端層"

    def test_mid_upper_bound(self):
        assert get_tier(150_000_000) == "中端層"

    def test_gap_above_mid(self):
        assert get_tier(180_000_000) is None  # 1.5億–2億 gap

    def test_high_lower_bound(self):
        assert get_tier(200_000_000) == "高端層"

    def test_high_very_large(self):
        assert get_tier(1_000_000_000) == "高端層"


# ── Room-type compatibility ───────────────────────────────────────────────────

class TestRoomTypeCompatibility:
    def test_identical(self):
        assert are_room_types_compatible("2LDK", "2LDK")

    def test_adjacent_up(self):
        assert are_room_types_compatible("2LDK", "3LDK")

    def test_adjacent_down(self):
        assert are_room_types_compatible("3LDK", "2LDK")

    def test_1ldk_vs_2ldk(self):
        # Confirmed by the spec's output format example
        assert are_room_types_compatible("1LDK", "2LDK")

    def test_gap_of_two(self):
        assert not are_room_types_compatible("1LDK", "3LDK")

    def test_1k_vs_3ldk(self):
        assert not are_room_types_compatible("1K", "3LDK")

    def test_dk_vs_ldk_same_bedroom(self):
        # 2DK → 2 bedrooms, 2LDK → 2 bedrooms  (diff = 0)
        assert are_room_types_compatible("2DK", "2LDK")

    def test_unknown_requires_exact_match(self):
        assert are_room_types_compatible("SHOP", "SHOP")
        assert not are_room_types_compatible("SHOP", "OFFICE")


# ── Area compatibility ────────────────────────────────────────────────────────

class TestAreaCompatibility:
    def test_identical(self):
        assert are_areas_compatible(50.0, 50.0)

    def test_within_20pct(self):
        # diff 5, max 55 → 5/55 ≈ 9% ✓
        assert are_areas_compatible(50.0, 55.0)

    def test_exactly_20pct(self):
        # diff 10, max 50 → 10/50 = 20% ✓
        assert are_areas_compatible(40.0, 50.0)

    def test_just_over_20pct(self):
        # diff 10.1, max 50 → 10.1/50 = 20.2% ✗
        assert not are_areas_compatible(39.9, 50.0)

    def test_zero_area_invalid(self):
        assert not are_areas_compatible(0.0, 50.0)
        assert not are_areas_compatible(50.0, 0.0)


# ── is_pair_compatible ────────────────────────────────────────────────────────

class TestIsPairCompatible:
    def test_valid_mid_pair(self):
        a = make_prop("1", 100_000_000, "2LDK", 60.0, "A区")
        b = make_prop("2", 120_000_000, "2LDK", 65.0, "B区")
        assert is_pair_compatible(a, b)

    def test_price_ratio_just_within_limit(self):
        # ratio = 1.5 exactly → should pass
        a = make_prop("1", 150_000_000, "2LDK", 60.0, "A区")
        b = make_prop("2", 100_000_000, "2LDK", 60.0, "B区")
        assert is_pair_compatible(a, b)

    def test_price_ratio_exceeds_limit(self):
        # ratio = 1.6 → should fail
        a = make_prop("1", 160_000_000, "2LDK", 60.0, "A区")
        b = make_prop("2", 100_000_000, "2LDK", 60.0, "B区")
        assert not is_pair_compatible(a, b)

    def test_high_end_relaxed_ratio_passes(self):
        # Both ≥ ¥2億, ratio = 1.8 → should pass
        a = make_prop("1", 360_000_000, "3LDK", 90.0, "A区")
        b = make_prop("2", 200_000_000, "3LDK", 92.0, "B区")
        assert is_pair_compatible(a, b)

    def test_high_end_ratio_exceeds_relaxed_limit(self):
        # Both ≥ ¥2億, ratio > 1.8 → should fail
        a = make_prop("1", 400_000_000, "3LDK", 90.0, "A区")
        b = make_prop("2", 200_000_000, "3LDK", 90.0, "B区")
        assert not is_pair_compatible(a, b)

    def test_incompatible_room_types(self):
        a = make_prop("1", 100_000_000, "1LDK", 45.0, "A区")
        b = make_prop("2", 110_000_000, "3LDK", 47.0, "B区")
        assert not is_pair_compatible(a, b)

    def test_area_too_different(self):
        a = make_prop("1", 100_000_000, "2LDK", 40.0, "A区")
        b = make_prop("2", 105_000_000, "2LDK", 80.0, "B区")
        assert not is_pair_compatible(a, b)

    def test_zero_price_invalid(self):
        a = make_prop("1", 0, "2LDK", 60.0, "A区")
        b = make_prop("2", 100_000_000, "2LDK", 60.0, "B区")
        assert not is_pair_compatible(a, b)


# ── find_pairs_for_tier ───────────────────────────────────────────────────────

class TestFindPairsForTier:
    def _mid_props(self, area: str, start_id: int = 0) -> list:
        return [
            make_prop(str(start_id + i), 90_000_000 + i * 3_000_000, "2LDK", 55.0 + i * 0.5, area)
            for i in range(10)
        ]

    def test_finds_valid_pairs(self):
        props_a = self._mid_props("A区", 0)
        props_b = self._mid_props("B区", 100)
        pairs, warnings = find_pairs_for_tier(props_a, props_b, "中端層", set())
        assert len(pairs) > 0
        assert "insufficient_candidates" not in warnings

    def test_excluded_keys_respected(self):
        props_a = self._mid_props("A区", 0)
        props_b = self._mid_props("B区", 100)
        pairs_first, _ = find_pairs_for_tier(props_a, props_b, "中端層", set())
        excluded = {p.pair_key for p in pairs_first}
        pairs_second, _ = find_pairs_for_tier(props_a, props_b, "中端層", excluded)
        for p in pairs_second:
            assert p.pair_key not in excluded

    def test_empty_pool_warns(self):
        _, warnings = find_pairs_for_tier([], [], "中端層", set())
        assert "insufficient_candidates" in warnings

    def test_sorted_by_ratio_closeness(self):
        props_a = self._mid_props("A区", 0)
        props_b = self._mid_props("B区", 100)
        pairs, _ = find_pairs_for_tier(props_a, props_b, "中端層", set())
        ratios = [abs(p.price_ratio - 1.0) for p in pairs]
        assert ratios == sorted(ratios)

    def test_no_cross_tier_contamination(self):
        # High-end properties should not appear in mid-tier results
        props_a = [make_prop("1", 500_000_000, "3LDK", 90.0, "A区")]
        props_b = [make_prop("2", 400_000_000, "3LDK", 95.0, "B区")]
        pairs, _ = find_pairs_for_tier(props_a, props_b, "中端層", set())
        assert len(pairs) == 0


# ── select_daily_pairs ────────────────────────────────────────────────────────

class TestSelectDailyPairs:
    def _make_pairs(self, n: int) -> list:
        pairs = []
        for i in range(n):
            a = make_prop(str(i),     100_000_000, "2LDK", 60.0, "A区")
            b = make_prop(str(i+100), 100_000_000 + i * 1_000_000, "2LDK", 61.0, "B区")
            from suumo_pairing.models import PropertyPair
            pairs.append(PropertyPair(property_a=a, property_b=b, tier="中端層"))
        return pairs

    def test_capped_at_10(self):
        candidates = self._make_pairs(20)
        selected, warnings = select_daily_pairs(candidates)
        assert len(selected) <= 10
        assert "below_target_count" not in warnings

    def test_warns_below_target(self):
        candidates = self._make_pairs(5)
        selected, warnings = select_daily_pairs(candidates)
        assert len(selected) == 5
        assert "below_target_count" in warnings

    def test_exactly_8_is_ok(self):
        candidates = self._make_pairs(8)
        selected, warnings = select_daily_pairs(candidates)
        assert len(selected) == 8
        assert "below_target_count" not in warnings
