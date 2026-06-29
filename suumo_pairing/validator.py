"""
Standalone URL-validation module.

Usage:
    from suumo_pairing.validator import filter_active_properties
    active = filter_active_properties(properties, scraper)
"""
import logging
from typing import List

from .models import Property
from .scraper import Scraper

logger = logging.getLogger(__name__)


def filter_active_properties(
    properties: List[Property],
    scraper: Scraper,
) -> List[Property]:
    """
    Re-check each property URL and remove listings that are sold or withdrawn.

    SUUMO returns HTTP 200 even for removed listings, so this does a full GET
    and inspects the page text for sold/withdrawn markers.

    This is optional — pass --validate to the CLI to enable it.
    """
    active: List[Property] = []
    for i, prop in enumerate(properties, 1):
        alive = scraper.check_url_alive(prop.url)
        status = "✓ active" if alive else "✗ removed"
        logger.info("[%d/%d] %s  %s", i, len(properties), status, prop.url)
        if alive:
            active.append(prop)

    removed = len(properties) - len(active)
    logger.info("Validation: %d active, %d removed", len(active), removed)
    return active
