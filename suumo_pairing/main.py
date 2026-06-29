#!/usr/bin/env python3
"""
SUUMO daily property-pairing runner.

Usage examples
--------------
# Manually specify a pair and run all tiers:
    python -m suumo_pairing.main --pair "港区-世田谷区"

# Auto-rotate to the least-used area pair:
    python -m suumo_pairing.main --auto-rotate

# Run only the mid-tier, with URL validation:
    python -m suumo_pairing.main --pair "新宿区-渋谷区" --tier 中端層 --validate

# Test the acceptance-test property parser:
    python -m suumo_pairing.main --test-parse
"""
import argparse
import logging
import sys
from datetime import datetime, timezone

from .areas import AREA_PAIRS
from .dedup import open_db, load_seen_keys, record_pairs, least_used_pair_index
from .models import DailyResult
from .output import setup_logging, save_result, print_summary
from .pairing import TIERS, find_pairs_for_tier, select_daily_pairs
from .scraper import Scraper

logger = logging.getLogger(__name__)

TARGET_MIN = 8
TARGET_MAX = 10


def run(
    area_a: str,
    area_b: str,
    tiers: list[str] | None = None,
    validate: bool = False,
    db_path: str | None = None,
) -> DailyResult:
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = setup_logging(run_date)
    logger.info("=== SUUMO Pairing  %s  |  %s vs %s ===", run_date, area_a, area_b)

    db = open_db(db_path) if db_path else open_db()
    seen_keys = load_seen_keys(db)
    logger.info("Dedup DB: %d seen pair keys loaded", len(seen_keys))

    scraper = Scraper()

    logger.info("Scraping %s …", area_a)
    props_a = scraper.fetch_area_properties(area_a)

    logger.info("Scraping %s …", area_b)
    props_b = scraper.fetch_area_properties(area_b)

    if validate:
        from .validator import filter_active_properties
        logger.info("Validating %s properties …", len(props_a) + len(props_b))
        props_a = filter_active_properties(props_a, scraper)
        props_b = filter_active_properties(props_b, scraper)

    # Enrich properties that are missing critical fields by fetching detail pages
    def _needs_enrich(p):
        return p.price_jpy <= 0 or p.area_sqm <= 0 or not p.room_type

    missing_a = [p for p in props_a if _needs_enrich(p)]
    missing_b = [p for p in props_b if _needs_enrich(p)]
    if missing_a or missing_b:
        logger.info(
            "Enriching %d incomplete cards via detail pages …",
            len(missing_a) + len(missing_b),
        )
        for lst, missing in [(props_a, missing_a), (props_b, missing_b)]:
            for prop in missing:
                enriched = scraper.enrich_from_detail(prop)
                if enriched:
                    idx = lst.index(prop)
                    lst[idx] = enriched

    # Remove properties still missing critical fields
    props_a = [p for p in props_a if not _needs_enrich(p)]
    props_b = [p for p in props_b if not _needs_enrich(p)]

    active_tiers = tiers or list(TIERS.keys())
    all_candidates = []
    tier_warnings: list[str] = []

    for tier in active_tiers:
        pairs, warnings = find_pairs_for_tier(
            props_a, props_b, tier, excluded_keys=seen_keys
        )
        all_candidates.extend(pairs)
        tier_warnings.extend(warnings)
        logger.info("  %s → %d candidate pairs", tier, len(pairs))

    selected, select_warnings = select_daily_pairs(
        all_candidates, target_min=TARGET_MIN, target_max=TARGET_MAX
    )

    all_warnings = list(set(tier_warnings + select_warnings))

    # Persist newly selected pairs to dedup DB
    area_pair_label = f"{area_a}-{area_b}"
    for pair in selected:
        record_pairs(db, [pair.pair_key], area_pair_label, pair.tier, run_date)
    db.close()

    result = DailyResult(
        run_date=run_date,
        area_pair_used=area_pair_label,
        new_pairs_found=len(selected),
        warnings=all_warnings,
        pairs=selected,
    )

    out_path = save_result(result)
    logger.info("Saved → %s", out_path)
    print_summary(result, log_path)

    return result


def _test_parse(url: str) -> None:
    """Acceptance-test helper: fetch a known SUUMO detail page and print parsed fields."""
    import json
    scraper = Scraper()
    from bs4 import BeautifulSoup
    from .parser import parse_detail_page

    resp = scraper.session.get(url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    result = parse_detail_page(soup)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SUUMO daily property-pairing runner"
    )
    parser.add_argument(
        "--pair",
        metavar="A区-B区",
        help='Area pair, e.g. "港区-世田谷区"',
    )
    parser.add_argument(
        "--auto-rotate",
        action="store_true",
        help="Auto-select the least-used area pair from the rotation list",
    )
    parser.add_argument(
        "--tier",
        choices=list(TIERS.keys()),
        help="Run a single price tier instead of all three",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Re-check each property URL before pairing (slow)",
    )
    parser.add_argument(
        "--test-parse",
        metavar="URL",
        help="Fetch a SUUMO detail page and print parsed fields (acceptance test)",
    )
    args = parser.parse_args()

    # Acceptance-test mode
    if args.test_parse:
        _test_parse(args.test_parse)
        return

    # Resolve area pair
    if args.pair:
        parts = args.pair.split("-", 1)
        if len(parts) != 2:
            print("Error: --pair must be 'A区-B区'", file=sys.stderr)
            sys.exit(1)
        area_a, area_b = parts
    elif args.auto_rotate:
        db = open_db()
        idx = least_used_pair_index(db, AREA_PAIRS)
        db.close()
        area_a, area_b = AREA_PAIRS[idx]
    else:
        # Default to first pair
        area_a, area_b = AREA_PAIRS[0]

    run(
        area_a=area_a,
        area_b=area_b,
        tiers=[args.tier] if args.tier else None,
        validate=args.validate,
    )


if __name__ == "__main__":
    main()
