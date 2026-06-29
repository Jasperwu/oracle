"""
Pairing algorithm — pure functions, zero I/O, fully unit-testable.

Compatibility rules (per spec):
  1. Price ratio:  0.67 ≤ A/B ≤ 1.5  (high-end ≥ ¥2億: relaxed to 1.8)
  2. Room type:    bedroom-count difference ≤ 1
                   (1LDK↔2LDK ✓, 1LDK↔3LDK ✗)
  3. Area:         |area_a - area_b| ≤ max(area_a, area_b) × 0.20
"""
import re
import random
from typing import List, Optional, Set, Tuple

from .models import Property, PropertyPair

# ── Tier definitions ──────────────────────────────────────────────────────────

TIERS: dict[str, Tuple[int, int]] = {
    "入門層": (30_000_000,  60_000_000),
    "中端層": (70_000_000, 150_000_000),
    "高端層": (200_000_000, 10_000_000_000),
}

HIGH_END_THRESHOLD = 200_000_000
NORMAL_MAX_RATIO   = 1.5
HIGHEND_MAX_RATIO  = 1.8


def get_tier(price_jpy: int) -> Optional[str]:
    """Return tier name for a price, or None if it falls in a gap between tiers."""
    for name, (lo, hi) in TIERS.items():
        if lo <= price_jpy <= hi:
            return name
    return None


# ── Room-type compatibility ───────────────────────────────────────────────────

def _bedroom_count(room_type: str) -> Optional[int]:
    """Extract the leading digit from room type strings like '2LDK'."""
    m = re.match(r"(\d+)", room_type.strip())
    return int(m.group(1)) if m else None


def are_room_types_compatible(rt_a: str, rt_b: str) -> bool:
    """
    Compatible means bedroom-count difference ≤ 1.

    Examples:
      1LDK vs 2LDK → |1-2| = 1 ✓
      2LDK vs 3LDK → |2-3| = 1 ✓
      1LDK vs 3LDK → |1-3| = 2 ✗
      Unknown type → require exact string match as fallback.
    """
    ba = _bedroom_count(rt_a)
    bb = _bedroom_count(rt_b)
    if ba is None or bb is None:
        return rt_a.strip().upper() == rt_b.strip().upper()
    return abs(ba - bb) <= 1


# ── Area compatibility ────────────────────────────────────────────────────────

def are_areas_compatible(area_a: float, area_b: float) -> bool:
    """Area difference ≤ 20% of the larger area."""
    if area_a <= 0 or area_b <= 0:
        return False
    return abs(area_a - area_b) <= max(area_a, area_b) * 0.20


# ── Price ratio ───────────────────────────────────────────────────────────────

def price_ratio(price_a: int, price_b: int) -> float:
    return price_a / price_b


# ── Main compatibility check ──────────────────────────────────────────────────

def is_pair_compatible(prop_a: Property, prop_b: Property) -> bool:
    """
    Return True iff prop_a and prop_b are a valid comparable pair.

    Caller is responsible for ensuring both properties belong to the same
    price tier before calling this function.
    """
    if prop_a.price_jpy <= 0 or prop_b.price_jpy <= 0:
        return False

    # 1. Price ratio
    ratio = price_ratio(prop_a.price_jpy, prop_b.price_jpy)
    high_end = (
        prop_a.price_jpy >= HIGH_END_THRESHOLD
        and prop_b.price_jpy >= HIGH_END_THRESHOLD
    )
    max_ratio = HIGHEND_MAX_RATIO if high_end else NORMAL_MAX_RATIO
    if not (1 / max_ratio <= ratio <= max_ratio):
        return False

    # 2. Room type
    if not are_room_types_compatible(prop_a.room_type, prop_b.room_type):
        return False

    # 3. Area
    if not are_areas_compatible(prop_a.area_sqm, prop_b.area_sqm):
        return False

    return True


# ── Pair finder ───────────────────────────────────────────────────────────────

def find_pairs_for_tier(
    props_a: List[Property],
    props_b: List[Property],
    tier: str,
    excluded_keys: Set[str],
) -> Tuple[List[PropertyPair], List[str]]:
    """
    Find all compatible, non-duplicate pairs across props_a and props_b for
    a single price tier.

    Returns (pairs, warnings) where warnings is a list of warning strings.
    Pairs are sorted by |ratio - 1.0| ascending (most comparable first).
    """
    lo, hi = TIERS[tier]
    tier_a = [p for p in props_a if lo <= p.price_jpy <= hi]
    tier_b = [p for p in props_b if lo <= p.price_jpy <= hi]

    warnings: List[str] = []

    if len(tier_a) < 2 or len(tier_b) < 2:
        warnings.append("insufficient_candidates")
        return [], warnings

    found: List[PropertyPair] = []
    for pa in tier_a:
        for pb in tier_b:
            pair = PropertyPair(property_a=pa, property_b=pb, tier=tier)
            if pair.pair_key in excluded_keys:
                continue
            if is_pair_compatible(pa, pb):
                found.append(pair)

    found.sort(key=lambda p: abs(p.price_ratio - 1.0))
    return found, warnings


def select_daily_pairs(
    all_candidates: List[PropertyPair],
    target_min: int = 8,
    target_max: int = 10,
) -> Tuple[List[PropertyPair], List[str]]:
    """
    From a combined cross-tier candidate list, select 8–10 pairs.

    Selection strategy:
      - If > target_max candidates: keep the target_max pairs with
        ratio closest to 1.0 (most comparable).
      - If < target_min candidates: return all and emit warning.
    """
    warnings: List[str] = []
    # Already sorted by |ratio - 1| within each tier; stable-sort preserves that.
    candidates = sorted(all_candidates, key=lambda p: abs(p.price_ratio - 1.0))

    if len(candidates) < target_min:
        warnings.append("below_target_count")
        return candidates, warnings

    return candidates[:target_max], warnings
