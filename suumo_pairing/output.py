"""
Output helpers: JSON file saving and logging setup.
"""
import json
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import DailyResult

_PKG_DIR  = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(_PKG_DIR, "output")
LOG_DIR    = os.path.join(_PKG_DIR, "logs")


def _ensure_dirs() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging(run_date: str) -> str:
    _ensure_dirs()
    log_path = os.path.join(LOG_DIR, f"run_{run_date}.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )
    return log_path


def save_result(result: "DailyResult") -> str:
    _ensure_dirs()
    pair_slug = result.area_pair_used.replace("-", "_").replace("区", "")
    fname = f"pairs_{result.run_date}_{pair_slug}.json"
    path = os.path.join(OUTPUT_DIR, fname)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result.to_dict(), fh, ensure_ascii=False, indent=2)
    return path


def print_summary(result: "DailyResult", log_path: str) -> None:
    bar = "=" * 55
    print(f"\n{bar}")
    print(f"  Run date   : {result.run_date}")
    print(f"  Area pair  : {result.area_pair_used}")
    print(f"  New pairs  : {result.new_pairs_found}  (target {result.target_range})")
    if result.warnings:
        print(f"  Warnings   : {', '.join(result.warnings)}")
    print(f"  Log        : {log_path}")
    print(f"{bar}\n")
