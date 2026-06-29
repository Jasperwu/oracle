from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Property:
    nc_id: str
    name: str
    price_jpy: int
    room_type: str      # e.g. "1LDK", "2LDK"
    area_sqm: float
    url: str
    area_name: str      # e.g. "港区"

    @property
    def tier(self) -> Optional[str]:
        if 30_000_000 <= self.price_jpy <= 60_000_000:
            return "入門層"
        if 70_000_000 <= self.price_jpy <= 150_000_000:
            return "中端層"
        if self.price_jpy >= 200_000_000:
            return "高端層"
        return None


@dataclass
class PropertyPair:
    property_a: Property
    property_b: Property
    tier: str

    @property
    def price_ratio(self) -> float:
        return round(self.property_a.price_jpy / self.property_b.price_jpy, 3)

    @property
    def pair_key(self) -> str:
        ids = sorted([self.property_a.nc_id, self.property_b.nc_id])
        return f"{ids[0]}_{ids[1]}"

    def to_dict(self) -> dict:
        return {
            "tier": self.tier,
            "property_a": {
                "name": self.property_a.name,
                "price_jpy": self.property_a.price_jpy,
                "room_type": self.property_a.room_type,
                "area_sqm": self.property_a.area_sqm,
                "url": self.property_a.url,
            },
            "property_b": {
                "name": self.property_b.name,
                "price_jpy": self.property_b.price_jpy,
                "room_type": self.property_b.room_type,
                "area_sqm": self.property_b.area_sqm,
                "url": self.property_b.url,
            },
            "price_ratio": self.price_ratio,
        }


@dataclass
class DailyResult:
    run_date: str
    area_pair_used: str
    new_pairs_found: int
    target_range: str = "8-10"
    warnings: list = field(default_factory=list)
    pairs: list = field(default_factory=list)   # List[PropertyPair]

    def to_dict(self) -> dict:
        return {
            "run_date": self.run_date,
            "area_pair_used": self.area_pair_used,
            "new_pairs_found": self.new_pairs_found,
            "target_range": self.target_range,
            "warnings": self.warnings,
            "pairs": [p.to_dict() for p in self.pairs],
        }
