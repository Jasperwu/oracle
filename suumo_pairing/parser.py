"""
HTML parsing: listing-card parser and detail-page parser.
All functions are pure (no I/O) and can be unit-tested with static HTML strings.
"""
import re
import logging
from typing import Optional

from bs4 import BeautifulSoup, Tag

from .models import Property

logger = logging.getLogger(__name__)

# ── Price ────────────────────────────────────────────────────────────────────

def parse_price(text: str) -> int:
    """
    Convert Japanese real-estate price string to integer yen.

    Handles:
      "1億3,800万円"  → 138_000_000
      "8,500万円"     → 85_000_000
      "2億円"         → 200_000_000
    """
    text = re.sub(r"[,\s　円]", "", text)
    total = 0

    oku = re.search(r"(\d+)億", text)
    if oku:
        total += int(oku.group(1)) * 100_000_000

    man = re.search(r"(\d+)万", text)
    if man:
        total += int(man.group(1)) * 10_000

    # Bare digits with no unit (rare but handle it)
    if total == 0:
        digits = re.sub(r"\D", "", text)
        if digits:
            total = int(digits)

    return total


# ── Area ─────────────────────────────────────────────────────────────────────

def parse_area(text: str) -> float:
    """Extract ㎡ value from strings like '45.20m²', '45.2㎡', '45.20 m²'."""
    m = re.search(r"([\d.]+)\s*(?:㎡|m²|m2)", text, re.IGNORECASE)
    return float(m.group(1)) if m else 0.0


# ── Room type ─────────────────────────────────────────────────────────────────

def normalize_room_type(text: str) -> str:
    """
    Return canonical room-type string (e.g. '2LDK').
    Handles 1R / 1K / 1DK / 1LDK / 1SLDK / 2LDK … 5LDK variants.
    """
    t = text.strip().upper()
    # Canonical order — try longest match first
    for rt in [
        "1SLDK", "2SLDK", "3SLDK", "4SLDK",
        "1LDK", "2LDK", "3LDK", "4LDK", "5LDK",
        "1DK", "2DK", "3DK", "4DK",
        "1K", "2K", "3K", "4K",
        "1R",
    ]:
        if t.startswith(rt):
            return rt
    # Fallback regex
    m = re.match(r"(\d+(?:S?LDK|DK|K|R))", t)
    return m.group(1) if m else text.strip()


# ── DOM helpers ───────────────────────────────────────────────────────────────

def _find_by_label(container: Tag, labels: list[str]) -> Optional[str]:
    """
    Search <dt>/<th> elements whose text matches any label;
    return the sibling <dd>/<td> text.
    Works for both dl/dt/dd and table/tr/th/td patterns.
    """
    for dt in container.find_all(["dt", "th"]):
        if any(lbl in dt.get_text(strip=True) for lbl in labels):
            sibling = dt.find_next_sibling(["dd", "td"])
            if sibling:
                return sibling.get_text(strip=True)
    return None


def _find_by_text_pattern(container: Tag, pattern: re.Pattern) -> Optional[str]:
    """Return the first NavigableString matching pattern anywhere in container."""
    for node in container.find_all(string=pattern):
        return node.strip()
    return None


# ── Listing-card parser ───────────────────────────────────────────────────────

def parse_property_card(
    card: Tag, nc_id: str, url: str, area_name: str
) -> Optional[Property]:
    """
    Parse a SUUMO listing-page property card into a Property.
    Returns None if essential fields are missing or clearly invalid.
    """
    try:
        # ── Name ──────────────────────────────────────────────────────────
        link_el = card.find("a", href=re.compile(r"/nc_\d+/"))
        name = link_el.get_text(strip=True) if link_el else ""

        # Some cards have a separate title element
        if not name:
            title_el = card.find(
                True,
                class_=re.compile(r"title|name|bukken", re.I),
            )
            if title_el:
                name = title_el.get_text(strip=True)

        # ── Price ─────────────────────────────────────────────────────────
        price_text = (
            _find_by_label(card, ["価格", "販売価格", "物件価格"])
            or _find_by_text_pattern(card, re.compile(r"\d+[万億]円"))
        )
        price_jpy = parse_price(price_text) if price_text else 0

        # ── Room type ─────────────────────────────────────────────────────
        room_text = (
            _find_by_label(card, ["間取り", "間取"])
            or _find_by_text_pattern(card, re.compile(r"\d+(?:S?LDK|DK|K|R)", re.I))
        )
        room_type = normalize_room_type(room_text) if room_text else ""

        # ── Area ──────────────────────────────────────────────────────────
        area_text = (
            _find_by_label(card, ["専有面積", "面積"])
            or _find_by_text_pattern(card, re.compile(r"[\d.]+\s*(?:㎡|m²|m2)", re.I))
        )
        area_sqm = parse_area(area_text) if area_text else 0.0

        if not name or price_jpy <= 0 or area_sqm <= 0:
            logger.debug(
                "Card nc_%s skipped: name=%r price=%d area=%.1f",
                nc_id, name, price_jpy, area_sqm,
            )
            return None

        return Property(
            nc_id=nc_id,
            name=name,
            price_jpy=price_jpy,
            room_type=room_type,
            area_sqm=area_sqm,
            url=url,
            area_name=area_name,
        )
    except Exception as e:
        logger.debug("Card parse error nc_%s: %s", nc_id, e)
        return None


# ── Detail-page parser ────────────────────────────────────────────────────────

def is_page_removed(soup: BeautifulSoup) -> bool:
    """Return True if the page indicates the listing is sold/withdrawn."""
    page_text = soup.get_text()
    return any(
        marker in page_text
        for marker in ("販売終了", "掲載終了", "この物件は削除", "成約済み")
    )


def parse_detail_page(soup: BeautifulSoup) -> Optional[dict]:
    """
    Parse a SUUMO property detail page.
    Returns dict with keys: name, price_jpy, room_type, area_sqm.
    Returns None if the listing is sold/removed.
    """
    if is_page_removed(soup):
        return None

    # ── Name ──────────────────────────────────────────────────────────────────
    name_el = (
        soup.find("h1", class_=re.compile(r"section_h1|title|bukken", re.I))
        or soup.find("h2", class_=re.compile(r"section_h2|title", re.I))
        or soup.find("h1")
    )
    name = name_el.get_text(strip=True) if name_el else ""

    # ── Structured data via dt/th pattern ─────────────────────────────────────
    price_text = _find_by_label(soup, ["販売価格", "価格"])
    room_text  = _find_by_label(soup, ["間取り", "間取"])
    area_text  = _find_by_label(soup, ["専有面積"])

    return {
        "name":      name,
        "price_jpy": parse_price(price_text) if price_text else 0,
        "room_type": normalize_room_type(room_text) if room_text else "",
        "area_sqm":  parse_area(area_text) if area_text else 0.0,
    }
