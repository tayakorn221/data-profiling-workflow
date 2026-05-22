"""สแกนหา PII (Personally Identifiable Information) ใน schema_summary.json

ตรวจสอบทุก top_values ในไฟล์ schema ว่ามี pattern ของข้อมูลส่วนบุคคลหลุดเข้ามาไหม:
- เลขบัตรประชาชนไทย (13 หลัก)
- เบอร์โทรไทย (เริ่มด้วย 0 ตามด้วย 8-9 หลัก)
- อีเมล
- รหัสนักศึกษา (8-11 หลัก)
- วันที่ในรูป YYYY-MM-DD

ผลลัพธ์: text report + exit code (0 = ปลอดภัย, 1 = พบ PII)

ตัวอย่างการใช้งาน:
    python scripts/02_scan_pii.py --input outputs/schema.json --report outputs/pii_report.txt
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "thai_citizen_id": re.compile(r"(?<![\d.])\d{13}(?![\d.])"),
    "thai_phone": re.compile(r"(?<![\d.])0\d{8,9}(?![\d.])"),
    "email": re.compile(r"[\w.+-]+@[\w.-]+\.\w+"),
    "student_code": re.compile(r"(?<![\d.])\d{8,11}(?![\d.])"),
    "date_iso": re.compile(r"\d{4}-\d{2}-\d{2}"),
}


def scan_text(text: str) -> list[str]:
    """คืน list ของชื่อ pattern ที่พบใน text"""
    return [name for name, pat in PII_PATTERNS.items() if pat.search(text)]


def scan_schema(schema: dict) -> list[dict]:
    """สแกนทุก top_values ในแต่ละคอลัมน์ของ schema คืน list ของ findings"""
    findings: list[dict] = []
    for col in schema.get("columns", []):
        for tv in col.get("top_values", []) or []:
            value_str = str(tv.get("value", ""))
            hits = scan_text(value_str)
            if hits:
                findings.append({
                    "column": col.get("name"),
                    "value": value_str,
                    "patterns": hits,
                })
    return findings


def write_report(report_path: Path, findings: list[dict], schema_path: Path) -> None:
    """เขียน text report สรุปผล PII scan"""
    lines: list[str] = [
        "PII Scan Report",
        "==================",
        f"schema file: {schema_path}",
        "",
    ]
    if not findings:
        lines.append("ผลการตรวจสอบ: PII-FREE ✓")
        lines.append("ไฟล์ schema ปลอดภัยสำหรับการแชร์")
    else:
        lines.append(f"พบความเสี่ยง {len(findings)} จุด — ห้ามแชร์จนกว่าจะแก้ไข:")
        lines.append("")
        for hit in findings:
            lines.append(f"- คอลัมน์: {hit['column']}")
            lines.append(f"  ค่า: {hit['value']}")
            lines.append(f"  รูปแบบที่ตรงกัน: {', '.join(hit['patterns'])}")
            lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="สแกน PII ใน schema summary JSON",
    )
    parser.add_argument(
        "--input", "-i",
        type=Path, required=True,
        help="path ของ schema_summary.json",
    )
    parser.add_argument(
        "--report", "-r",
        type=Path, required=True,
        help="path ของไฟล์ report ปลายทาง (.txt)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit ด้วย code 1 ถ้าพบ PII (สำหรับ CI)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.input.exists():
        print(f"ผิดพลาด: ไม่พบไฟล์ input: {args.input}", file=sys.stderr)
        return 2

    schema = json.loads(args.input.read_text(encoding="utf-8"))
    findings = scan_schema(schema)
    write_report(args.report, findings, args.input)

    print(f"ตรวจสอบเสร็จ — ดูผลที่ {args.report}")
    print(f"พบ {len(findings)} จุดเสี่ยง")

    if findings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
