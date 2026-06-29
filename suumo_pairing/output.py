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


def format_email_html(result: "DailyResult") -> str:
    """Render DailyResult as a self-contained HTML email body."""

    def _fmt_price(yen: int) -> str:
        if yen >= 100_000_000:
            oku = yen // 100_000_000
            man = (yen % 100_000_000) // 10_000
            return f"{oku}億{man:,}万円" if man else f"{oku}億円"
        return f"{yen // 10_000:,}万円"

    warning_html = ""
    if result.warnings:
        labels = {
            "below_target_count":    "⚠️ 新配對數量低於目標 8 組",
            "insufficient_candidates": "⚠️ 某分層候選物件不足，已略過",
        }
        items = "".join(
            f"<li>{labels.get(w, w)}</li>" for w in result.warnings
        )
        warning_html = f"""
        <div style="background:#fff8e1;border-left:4px solid #f59e0b;
                    padding:10px 14px;margin:16px 0;border-radius:4px;">
          <ul style="margin:0;padding-left:18px;color:#92400e;">{items}</ul>
        </div>"""

    pair_rows = ""
    for i, pair in enumerate(result.pairs, 1):
        pa, pb = pair.property_a, pair.property_b
        tier_badge = {
            "入門層": "#22c55e", "中端層": "#3b82f6", "高端層": "#a855f7"
        }.get(pair.tier, "#6b7280")

        pair_rows += f"""
        <tr style="background:{'#fafafa' if i % 2 else '#fff'};">
          <td style="padding:12px 8px;text-align:center;vertical-align:top;">
            <span style="background:{tier_badge};color:#fff;
                         font-size:11px;padding:2px 7px;border-radius:10px;">
              {pair.tier}
            </span>
          </td>
          <td style="padding:12px 8px;vertical-align:top;">
            <div style="font-weight:500;color:#111827;">{pa['name']}</div>
            <div style="color:#6b7280;font-size:13px;margin:2px 0 4px;">
              {pa['room_type']} · {pa['area_sqm']}㎡ · {_fmt_price(pa['price_jpy'])}
            </div>
            <a href="{pa['url']}" style="font-size:12px;color:#1d4ed8;word-break:break-all;">
              🔗 {pa['url']}
            </a>
          </td>
          <td style="padding:12px 8px;text-align:center;color:#9ca3af;font-size:20px;vertical-align:top;">⇄</td>
          <td style="padding:12px 8px;vertical-align:top;">
            <div style="font-weight:500;color:#111827;">{pb['name']}</div>
            <div style="color:#6b7280;font-size:13px;margin:2px 0 4px;">
              {pb['room_type']} · {pb['area_sqm']}㎡ · {_fmt_price(pb['price_jpy'])}
            </div>
            <a href="{pb['url']}" style="font-size:12px;color:#1d4ed8;word-break:break-all;">
              🔗 {pb['url']}
            </a>
          </td>
          <td style="padding:12px 8px;text-align:center;color:#374151;font-size:13px;">
            {pair.price_ratio:.2f}×
          </td>
        </tr>"""

    no_pairs_html = ""
    if not result.pairs:
        no_pairs_html = """
        <p style="text-align:center;color:#9ca3af;padding:24px 0;">
          今天沒有找到符合條件的新配對。
        </p>"""

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
             background:#f3f4f6;margin:0;padding:24px;">
  <div style="max-width:780px;margin:0 auto;background:#fff;
              border-radius:12px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.1);">

    <!-- Header -->
    <div style="background:#1e3a5f;padding:24px 28px;">
      <h1 style="margin:0;color:#fff;font-size:20px;font-weight:600;">
        🏠 AiSumai 每日配對報告
      </h1>
      <p style="margin:6px 0 0;color:#93c5fd;font-size:14px;">
        {result.run_date} &nbsp;·&nbsp; {result.area_pair_used}
      </p>
    </div>

    <!-- Stats bar -->
    <div style="display:flex;gap:0;border-bottom:1px solid #e5e7eb;">
      <div style="flex:1;padding:16px 24px;border-right:1px solid #e5e7eb;">
        <div style="font-size:28px;font-weight:700;color:#1e3a5f;">
          {result.new_pairs_found}
        </div>
        <div style="font-size:13px;color:#6b7280;">今日新配對</div>
      </div>
      <div style="flex:1;padding:16px 24px;border-right:1px solid #e5e7eb;">
        <div style="font-size:28px;font-weight:700;color:#1e3a5f;">
          {result.target_range}
        </div>
        <div style="font-size:13px;color:#6b7280;">目標區間</div>
      </div>
      <div style="flex:1;padding:16px 24px;">
        <div style="font-size:28px;font-weight:700;
                    color:{'#ef4444' if result.warnings else '#22c55e'};">
          {'⚠' if result.warnings else '✓'}
        </div>
        <div style="font-size:13px;color:#6b7280;">狀態</div>
      </div>
    </div>

    <div style="padding:20px 28px;">
      {warning_html}

      {'<table style="width:100%;border-collapse:collapse;font-size:14px;">' if result.pairs else ''}
        {'<thead><tr style="border-bottom:2px solid #e5e7eb;">' if result.pairs else ''}
          {'<th style="padding:8px;text-align:left;color:#6b7280;font-weight:500;">分層</th>' if result.pairs else ''}
          {'<th style="padding:8px;text-align:left;color:#6b7280;font-weight:500;">' + result.area_pair_used.split("-")[0] + '</th>' if result.pairs else ''}
          {'<th></th>' if result.pairs else ''}
          {'<th style="padding:8px;text-align:left;color:#6b7280;font-weight:500;">' + (result.area_pair_used.split("-")[1] if "-" in result.area_pair_used else "") + '</th>' if result.pairs else ''}
          {'<th style="padding:8px;text-align:center;color:#6b7280;font-weight:500;">價格比</th>' if result.pairs else ''}
        {'</tr></thead>' if result.pairs else ''}
        {'<tbody>' if result.pairs else ''}
          {pair_rows}
        {'</tbody>' if result.pairs else ''}
      {'</table>' if result.pairs else ''}
      {no_pairs_html}
    </div>

    <div style="padding:14px 28px;background:#f9fafb;
                border-top:1px solid #e5e7eb;font-size:12px;color:#9ca3af;">
      由 AiSumai SUUMO 配對系統自動產生 · 物件連結指向 SUUMO 即時頁面，可能已下架
    </div>
  </div>
</body>
</html>"""
