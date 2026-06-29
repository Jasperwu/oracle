"""
Area name → SUUMO URL components, and daily rotation pairs.
"""
from typing import Dict, List, Tuple

AREA_CONFIG: Dict[str, dict] = {
    # Tokyo 23 wards
    "港区":    {"prefecture": "tokyo", "sc": "minato"},
    "世田谷区": {"prefecture": "tokyo", "sc": "setagaya"},
    "渋谷区":  {"prefecture": "tokyo", "sc": "shibuya"},
    "新宿区":  {"prefecture": "tokyo", "sc": "shinjuku"},
    "千代田区": {"prefecture": "tokyo", "sc": "chiyoda"},
    "中央区":  {"prefecture": "tokyo", "sc": "chuo"},
    "文京区":  {"prefecture": "tokyo", "sc": "bunkyo"},
    "台東区":  {"prefecture": "tokyo", "sc": "taito"},
    "墨田区":  {"prefecture": "tokyo", "sc": "sumida"},
    "江東区":  {"prefecture": "tokyo", "sc": "koto"},
    "品川区":  {"prefecture": "tokyo", "sc": "shinagawa"},
    "目黒区":  {"prefecture": "tokyo", "sc": "meguro"},
    "大田区":  {"prefecture": "tokyo", "sc": "ota"},
    "中野区":  {"prefecture": "tokyo", "sc": "nakano"},
    "杉並区":  {"prefecture": "tokyo", "sc": "suginami"},
    "豊島区":  {"prefecture": "tokyo", "sc": "toshima"},
    "北区":    {"prefecture": "tokyo", "sc": "kita"},
    "荒川区":  {"prefecture": "tokyo", "sc": "arakawa"},
    "板橋区":  {"prefecture": "tokyo", "sc": "itabashi"},
    "練馬区":  {"prefecture": "tokyo", "sc": "nerima"},
    "足立区":  {"prefecture": "tokyo", "sc": "adachi"},
    "葛飾区":  {"prefecture": "tokyo", "sc": "katsushika"},
    "江戸川区": {"prefecture": "tokyo", "sc": "edogawa"},
    # Osaka
    "大阪市中央区": {"prefecture": "osaka", "sc": "osakashichuo"},
    "大阪市北区":   {"prefecture": "osaka", "sc": "osakashikita"},
    "大阪市天王寺区": {"prefecture": "osaka", "sc": "osakashitennoji"},
    # Fukuoka
    "福岡市中央区": {"prefecture": "fukuoka", "sc": "fukuokashichuo"},
    "福岡市博多区": {"prefecture": "fukuoka", "sc": "fukuokashibakata"},
    # Sapporo
    "札幌市中央区": {"prefecture": "hokkaido", "sc": "sapporoshichuo"},
}


def get_area_url(area_name: str) -> str:
    cfg = AREA_CONFIG[area_name]
    return f"https://suumo.jp/ms/chuko/{cfg['prefecture']}/sc_{cfg['sc']}/"


# Pairs rotated daily, ordered by candidate pool richness.
# Format: (area_a, area_b)
AREA_PAIRS: List[Tuple[str, str]] = [
    ("港区", "世田谷区"),
    ("新宿区", "渋谷区"),
    ("港区", "渋谷区"),
    ("港区", "新宿区"),
    ("渋谷区", "世田谷区"),
    ("港区", "目黒区"),
    ("渋谷区", "目黒区"),
    ("新宿区", "中野区"),
    ("渋谷区", "杉並区"),
    ("港区", "中央区"),
    ("千代田区", "中央区"),
    ("品川区", "目黒区"),
    ("港区", "品川区"),
    ("新宿区", "豊島区"),
    ("渋谷区", "品川区"),
]
