"""ดึง schema summary จากไฟล์ Excel โดยใช้ DuckDB

อ่านไฟล์ .xlsx โหลดเข้า DuckDB แล้วสรุปโครงสร้าง:
- ชื่อคอลัมน์, ชนิดข้อมูล
- จำนวน null / null %
- จำนวน unique values
- top-5 values สำหรับคอลัมน์ที่ไม่ใช่ PII (ผ่าน k-anonymity threshold)

ผลลัพธ์เป็น JSON ที่ปลอดภัยสำหรับการแชร์กับ AI (ไม่มี row-level data)

ตัวอย่างการใช้งาน:
    python scripts/01_extract_schema.py --input data/file.xlsx --output outputs/schema.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import duckdb

# คอลัมน์ที่ห้ามดึง top values (ระบุตัวบุคคลโดยตรง)
DEFAULT_SENSITIVE_COLUMNS = {
    "STUDENT_CODE", "CITIZEN_ID", "PASSPORT_NO",
    "FIRST_NAME_TH", "LAST_NAME_TH", "FIRST_NAME_EN", "LAST_NAME_EN",
    "EMAIL", "PHONE", "MOBILE", "ADDRESS", "BIRTHDATE",
}

# k-anonymity เบื้องต้น: ไม่รายงาน value ที่ count < SUPPRESS_THRESHOLD
DEFAULT_SUPPRESS_THRESHOLD = 5

# ดึง top values เฉพาะคอลัมน์ที่ unique count ต่ำกว่านี้
TOP_VALUES_UNIQUE_LIMIT = 100


def extract_schema(
    con: duckdb.DuckDBPyConnection,
    table_name: str,
    sensitive_columns: set[str],
    suppress_threshold: int,
) -> dict:
    """ดึงโครงสร้างของตารางและคืนค่าเป็น dict สำหรับ serialize เป็น JSON"""
    cols = con.execute(f'DESCRIBE "{table_name}"').fetchall()
    total_rows = con.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]

    schema = {
        "table_name": table_name,
        "extracted_at": datetime.now().isoformat(timespec="seconds"),
        "total_rows": total_rows,
        "total_columns": len(cols),
        "suppress_threshold": suppress_threshold,
        "columns": [],
    }

    for col_name, col_type, *_ in cols:
        col_info: dict = {"name": col_name, "type": col_type}

        stats = con.execute(
            f'''
            SELECT
                COUNT(*) - COUNT("{col_name}") AS null_count,
                COUNT(DISTINCT "{col_name}") AS unique_count
            FROM "{table_name}"
            '''
        ).fetchone()

        col_info["null_count"] = stats[0]
        col_info["null_pct"] = (
            round(stats[0] / total_rows * 100, 2) if total_rows else 0.0
        )
        col_info["unique_count"] = stats[1]

        if col_name not in sensitive_columns and stats[1] < TOP_VALUES_UNIQUE_LIMIT:
            top = con.execute(
                f'''
                SELECT "{col_name}" AS val, COUNT(*) AS cnt
                FROM "{table_name}"
                WHERE "{col_name}" IS NOT NULL
                GROUP BY "{col_name}"
                ORDER BY cnt DESC
                LIMIT 5
                '''
            ).fetchall()
            col_info["top_values"] = [
                {"value": str(v), "count": int(c)}
                for v, c in top
                if c >= suppress_threshold
            ]

        schema["columns"].append(col_info)

    return schema


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ดึง schema summary จากไฟล์ Excel (PDPA-safe)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input", "-i",
        type=Path, required=True,
        help="path ของไฟล์ Excel ต้นทาง (.xlsx)",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path, required=True,
        help="path ของไฟล์ JSON ปลายทาง",
    )
    parser.add_argument(
        "--table-name",
        default="raw_data",
        help="ชื่อ table ใน DuckDB (default: raw_data)",
    )
    parser.add_argument(
        "--sensitive",
        nargs="*",
        default=None,
        help="ชื่อคอลัมน์ที่เป็น PII (override default list)",
    )
    parser.add_argument(
        "--extra-sensitive",
        nargs="*",
        default=[],
        help="ชื่อคอลัมน์เพิ่มเติมที่ต้อง suppress top values นอกเหนือจาก default list",
    )
    parser.add_argument(
        "--suppress-threshold", "-k",
        type=int, default=DEFAULT_SUPPRESS_THRESHOLD,
        help="k-anonymity threshold (default: 5)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.input.exists():
        print(f"ผิดพลาด: ไม่พบไฟล์ input: {args.input}", file=sys.stderr)
        return 1

    sensitive = (
        set(args.sensitive)
        if args.sensitive is not None
        else set(DEFAULT_SENSITIVE_COLUMNS)
    )
    sensitive.update(args.extra_sensitive)

    con = duckdb.connect()
    # ใช้ all_varchar=true เพื่อหลีกเลี่ยง type inference error
    con.execute(
        f'''
        CREATE TABLE "{args.table_name}" AS
        SELECT * FROM read_xlsx(?, all_varchar=true)
        ''',
        [str(args.input)],
    )

    schema = extract_schema(
        con,
        args.table_name,
        sensitive_columns=sensitive,
        suppress_threshold=args.suppress_threshold,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    print(f"สำเร็จ: บันทึก schema ลง {args.output}")
    print(f"จำนวน {schema['total_columns']} คอลัมน์, {schema['total_rows']:,} แถว")
    return 0


if __name__ == "__main__":
    sys.exit(main())
