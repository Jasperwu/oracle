"""
HTTP fetching module.

Responsibilities:
- Paginate through SUUMO listing pages for a given area
- Extract nc_ property URLs and parse cards
- Enforce ≥2 s delay between requests
"""
import re
import time
import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from .models import Property
from .parser import parse_property_card, parse_detail_page, is_page_removed
from .areas import get_area_url

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Accept": (
        "text/html,application/xhtml+xml,application/xhtml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
}

REQUEST_DELAY = 2.0     # seconds between any two requests
VALIDATE_DELAY = 1.0    # lighter delay during validation passes

NC_URL_RE = re.compile(r"/nc_(\d+)/")


class Scraper:
    def __init__(self, delay: float = REQUEST_DELAY):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.delay = delay

    # ── Low-level fetch ───────────────────────────────────────────────────────

    def _get(self, url: str) -> Optional[BeautifulSoup]:
        try:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            time.sleep(self.delay)
            return BeautifulSoup(resp.text, "html.parser")
        except requests.HTTPError as e:
            logger.warning("HTTP %s for %s", e.response.status_code, url)
        except Exception as e:
            logger.warning("Fetch error %s: %s", url, e)
        return None

    # ── Listing page ──────────────────────────────────────────────────────────

    def fetch_area_properties(
        self, area_name: str, max_pages: int = 20
    ) -> List[Property]:
        """
        Fetch all currently listed properties in `area_name`.

        Paginates through SUUMO listing pages (pn=1, 2, …) and parses each
        property card. Only nc_-format links are collected; to_-format links
        (building history pages) are silently ignored.
        """
        base_url = get_area_url(area_name)
        properties: List[Property] = []
        seen_nc_ids: set = set()

        for page in range(1, max_pages + 1):
            url = f"{base_url}?pn={page}" if page > 1 else base_url
            logger.info("Fetching %s page %d …", area_name, page)
            soup = self._get(url)
            if soup is None:
                break

            page_props = self._parse_listing_page(soup, area_name, seen_nc_ids)
            properties.extend(page_props)
            logger.info("  → %d properties on page %d", len(page_props), page)

            if not self._has_next_page(soup):
                break

        logger.info("%s: %d total properties", area_name, len(properties))
        return properties

    def _parse_listing_page(
        self, soup: BeautifulSoup, area_name: str, seen_nc_ids: set
    ) -> List[Property]:
        """Extract property cards from a single listing page."""
        # SUUMO uses several wrapper classes depending on property type / version.
        # We try them in preference order.
        cards = (
            soup.select("div.property_unit-content")
            or soup.select("div.cassette_object-detail")
            or soup.select("li.js-bukkenList")
            or soup.select("div.item_unit")
            or soup.select("div[class*='property_']")
        )

        if not cards:
            # Last resort: find any element that directly contains an nc_ link
            nc_links = soup.find_all("a", href=NC_URL_RE)
            # Group by nearest common ancestor (approximate)
            cards = [lnk.find_parent(["li", "div", "article"]) for lnk in nc_links]
            cards = [c for c in cards if c]

        props: List[Property] = []
        for card in cards:
            link = card.find("a", href=NC_URL_RE)
            if not link:
                continue

            href = link["href"]
            if not href.startswith("http"):
                href = "https://suumo.jp" + href

            m = NC_URL_RE.search(href)
            if not m:
                continue

            nc_id = m.group(1)
            if nc_id in seen_nc_ids:
                continue
            seen_nc_ids.add(nc_id)

            prop = parse_property_card(card, nc_id, href, area_name)
            if prop:
                props.append(prop)

        return props

    @staticmethod
    def _has_next_page(soup: BeautifulSoup) -> bool:
        """Detect whether a SUUMO listing page has a 'next' page link."""
        return bool(
            soup.find("a", string=re.compile(r"次へ|次のページ"))
            or soup.select_one("ol.pagination-parts li.is-current + li a")
            or soup.find("a", class_=re.compile(r"pagination.*next|next.*page", re.I))
        )

    # ── Detail-page fallback ──────────────────────────────────────────────────

    def enrich_from_detail(self, prop: Property) -> Optional[Property]:
        """
        Re-fetch a property's detail page and override fields that were missing
        from the listing card. Returns the enriched property or None if removed.
        """
        soup = self._get(prop.url)
        if soup is None:
            return None

        detail = parse_detail_page(soup)
        if detail is None:
            return None  # listing removed

        return Property(
            nc_id=prop.nc_id,
            name=detail["name"] or prop.name,
            price_jpy=detail["price_jpy"] or prop.price_jpy,
            room_type=detail["room_type"] or prop.room_type,
            area_sqm=detail["area_sqm"] or prop.area_sqm,
            url=prop.url,
            area_name=prop.area_name,
        )

    # ── URL validation ────────────────────────────────────────────────────────

    def check_url_alive(self, url: str) -> bool:
        """
        Return True iff the property page still shows an active listing.
        SUUMO returns HTTP 200 even for removed listings, so we also inspect
        the page text for sold/withdrawn markers.
        """
        try:
            resp = self.session.get(url, timeout=15)
            time.sleep(VALIDATE_DELAY)
            if resp.status_code != 200:
                return False
            soup = BeautifulSoup(resp.text, "html.parser")
            return not is_page_removed(soup)
        except Exception:
            return False
