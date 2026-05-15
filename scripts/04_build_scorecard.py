"""สร้าง Data Quality Scorecard HTML สำหรับมนุษย์อ่าน

อ่าน schema_summary.json และ profile_stats.json แล้วสร้างรายงาน HTML
ที่อ่านง่าย ใช้ในการ review คุณภาพข้อมูลกับผู้บริหารหรือทีม

มิติคุณภาพที่วัด:
- Completeness: 100 - null_pct%
- Uniqueness: unique_count
- Kind: numeric / categorical / high_cardinality

ตัวอย่างการใช้งาน:
    python scripts/04_build_scorecard.py \\
        --schema outputs/schema.json \\
        --profile outputs/profile.json \\
        --output outputs/scorecard.html
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path


def completeness_score(col: dict) -> float:
    return round(100 - float(col.get("null_pct", 0)), 1)


def grade(score: float) -> tuple[str, str]:
    """คืน (letter grade, hex color)"""
    if score >= 95:
        return ("A", "#2E7D32")
    if score >= 85:
        return ("B", "#558B2F")
    if score >= 70:
        return ("C", "#F9A825")
    if score >= 50:
        return ("D", "#EF6C00")
    return ("F", "#C62828")


def render_row(col: dict, kind: str) -> str:
    score = completeness_score(col)
    letter, color = grade(score)
    return (
        "    <tr>\n"
        f"      <td>{html.escape(str(col.get('name', '')))}</td>\n"
        f"      <td>{html.escape(str(col.get('type', '')))}</td>\n"
        f"      <td>{html.escape(kind)}</td>\n"
        f"      <td>{col.get('null_pct', 0)}%</td>\n"
        f"      <td>{int(col.get('unique_count', 0)):,}</td>\n"
        f"      <td style=\"color:{color};font-weight:bold\">{letter} ({score}%)</td>\n"
        "    </tr>"
    )


def build_html(schema: dict, profile: dict) -> str:
    """ประกอบ HTML ฉบับเต็มจาก schema + profile dicts"""
    profile_cols = profile.get("columns", {}) if isinstance(profile, dict) else {}
    rows_html = "\n".join(
        render_row(col, profile_cols.get(col.get("name", ""), {}).get("kind", "—"))
        for col in schema.get("columns", [])
    )

    table_name = html.escape(str(schema.get("table_name", "")))
    total_rows = int(schema.get("total_rows", 0))
    total_cols = int(schema.get("total_columns", 0))
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <title>Data Quality Scorecard — {table_name}</title>
  <style>
    body {{
      font-family: 'Sarabun', 'Segoe UI', system-ui, sans-serif;
      max-width: 1100px;
      margin: 30px auto;
      padding: 20px;
      color: #333;
      line-height: 1.5;
    }}
    h1 {{ color: #1F4E79; border-bottom: 3px solid #1F4E79; padding-bottom: 8px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th {{ background: #1F4E79; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 8px 10px; border-bottom: 1px solid #ddd; }}
    tr:nth-child(even) {{ background: #F4F8FB; }}
    .meta {{ background: #FFF4CE; padding: 12px; border-radius: 4px; margin: 15px 0; }}
    .legend {{ font-size: 0.9em; color: #666; margin-top: 12px; }}
  </style>
</head>
<body>
  <h1>Data Quality Scorecard</h1>
  <div class="meta">
    <b>ตาราง:</b> {table_name}<br>
    <b>วันที่:</b> {now}<br>
    <b>จำนวน:</b> {total_rows:,} แถว × {total_cols} คอลัมน์
  </div>
  <table>
    <thead>
      <tr>
        <th>คอลัมน์</th><th>ชนิด</th><th>Profile Kind</th>
        <th>Null %</th><th>Unique</th><th>เกรด</th>
      </tr>
    </thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
  <p class="legend">
    เกรดคำนวณจาก completeness (100% − null%) — A ≥ 95, B ≥ 85, C ≥ 70, D ≥ 50, F &lt; 50
  </p>
</body>
</html>
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="สร้าง Data Quality Scorecard HTML จาก schema + profile",
    )
    parser.add_argument(
        "--schema", "-s",
        type=Path, required=True,
        help="path ของ schema_summary.json",
    )
    parser.add_argument(
        "--profile", "-p",
        type=Path, required=True,
        help="path ของ profile_stats.json",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path, required=True,
        help="path ของไฟล์ HTML ปลายทาง",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    for label, path in [("schema", args.schema), ("profile", args.profile)]:
        if not path.exists():
            print(f"ผิดพลาด: ไม่พบไฟล์ {label}: {path}", file=sys.stderr)
            return 1

    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    profile = json.loads(args.profile.read_text(encoding="utf-8"))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(schema, profile), encoding="utf-8")

    print(f"สร้าง scorecard เสร็จ — เปิดที่ {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
