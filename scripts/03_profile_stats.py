"""สร้าง profile statistics จากไฟล์ Excel ดิบ

แยกแต่ละคอลัมน์เป็น 3 ประเภทแล้วเก็บสถิติที่เหมาะสม:
- numeric: min, max, mean, median, std
- categorical (unique < 50): value counts ที่ผ่าน k-anonymity (count >= k)
- high_cardinality: length statistics เท่านั้น (ไม่เก็บค่า)

ทุก distribution กรอง count < SUPPRESS_THRESHOLD ออก เพื่อป้องกัน
re-identification ทางอ้อม

ตัวอย่างการใช้งาน:
    python scripts/03_profile_stats.py --input data/file.xlsx --output outputs/profile.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import duckdb

DEFAULT_SUPPRESS_THRESHOLD = 5
DEFAULT_CATEGORICAL_LIMIT = 50  # unique count ที่ถือว่าเป็น categorical


def _profile_numeric(
    con: duckdb.DuckDBPyConnection, table: str, col: str
) -> dict | None:
    """พยายาม cast เป็น DOUBLE แล้วคำนวณสถิติ ถ้าไม่ได้คืน None"""
    row = con.execute(
        f'''
        WITH numeric_values AS (
            SELECT TRY_CAST("{col}" AS DOUBLE) AS val
            FROM "{table}"
        ),
        finite_values AS (
            SELECT val
            FROM numeric_values
            WHERE isfinite(val)
        )
        SELECT
            MIN(val) AS min_v,
            MAX(val) AS max_v,
            AVG(val) AS mean_v,
            MEDIAN(val) AS median_v,
            STDDEV(val) AS std_v,
            QUANTILE_CONT(val, 0.25) AS p25,
            QUANTILE_CONT(val, 0.75) AS p75
        FROM finite_values
        '''
    ).fetchone()

    if row is None or row[0] is None:
        return None

    return {
        "kind": "numeric",
        "min": float(row[0]),
        "max": float(row[1]),
        "mean": round(float(row[2]), 2),
        "median": float(row[3]),
        "std": round(float(row[4]), 2) if row[4] is not None else None,
        "p25": float(row[5]) if row[5] is not None else None,
        "p75": float(row[6]) if row[6] is not None else None,
    }


def _profile_categorical(
    con: duckdb.DuckDBPyConnection,
    table: str,
    col: str,
    suppress_threshold: int,
) -> dict:
    """ดึง distribution พร้อม suppress ค่าที่ count < threshold"""
    rows = con.execute(
        f'''
        SELECT "{col}" AS val, COUNT(*) AS cnt
        FROM "{table}"
        WHERE "{col}" IS NOT NULL
        GROUP BY "{col}"
        HAVING COUNT(*) >= {int(suppress_threshold)}
        ORDER BY cnt DESC
        '''
    ).fetchall()

    return {
        "kind": "categorical",
        "distribution": [
            {"value": str(v), "count": int(c)} for v, c in rows
        ],
    }


def _profile_high_cardinality(
    con: duckdb.DuckDBPyConnection, table: str, col: str
) -> dict:
    """เก็บแค่ length statistics — ไม่เก็บค่าจริงเพื่อความปลอดภัย"""
    row = con.execute(
        f'''
        SELECT
            MIN(LENGTH("{col}")),
            MAX(LENGTH("{col}")),
            AVG(LENGTH("{col}"))
        FROM "{table}"
        WHERE "{col}" IS NOT NULL
        '''
    ).fetchone()

    return {
        "kind": "high_cardinality",
        "min_length": int(row[0]) if row[0] is not None else None,
        "max_length": int(row[1]) if row[1] is not None else None,
        "avg_length": round(float(row[2]), 1) if row[2] is not None else None,
    }


def profile_table(
    con: duckdb.DuckDBPyConnection,
    table: str,
    suppress_threshold: int,
    categorical_limit: int,
) -> dict:
    """สร้าง profile ของทุกคอลัมน์ใน table"""
    cols = con.execute(f'DESCRIBE "{table}"').fetchall()
    profile: dict = {
        "table_name": table,
        "suppress_threshold": suppress_threshold,
        "columns": {},
    }

    for col_name, *_ in cols:
        numeric_stat = _profile_numeric(con, table, col_name)
        if numeric_stat is not None:
            profile["columns"][col_name] = numeric_stat
            continue

        unique_cnt = con.execute(
            f'SELECT COUNT(DISTINCT "{col_name}") FROM "{table}"'
        ).fetchone()[0]

        if unique_cnt < categorical_limit:
            profile["columns"][col_name] = _profile_categorical(
                con, table, col_name, suppress_threshold
            )
        else:
            profile["columns"][col_name] = _profile_high_cardinality(
                con, table, col_name
            )

    return profile


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="สร้าง profile statistics จากไฟล์ Excel (k-anonymized)",
    )
    parser.add_argument(
        "--input", "-i",
        type=Path, required=True,
        help="path ของไฟล์ Excel ต้นทาง",
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
        "--suppress-threshold", "-k",
        type=int, default=DEFAULT_SUPPRESS_THRESHOLD,
        help="k-anonymity threshold (default: 5)",
    )
    parser.add_argument(
        "--categorical-limit",
        type=int, default=DEFAULT_CATEGORICAL_LIMIT,
        help="unique count สูงสุดที่ถือว่าเป็น categorical (default: 50)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if not args.input.exists():
        print(f"ผิดพลาด: ไม่พบไฟล์ input: {args.input}", file=sys.stderr)
        return 1

    con = duckdb.connect()
    con.execute(
        f'''
        CREATE TABLE "{args.table_name}" AS
        SELECT * FROM read_xlsx(?, all_varchar=true)
        ''',
        [str(args.input)],
    )

    profile = profile_table(
        con,
        table=args.table_name,
        suppress_threshold=args.suppress_threshold,
        categorical_limit=args.categorical_limit,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

    n_cols = len(profile["columns"])
    print(f"สำเร็จ: บันทึก profile ลง {args.output}")
    print(f"จำนวนคอลัมน์ที่ profile: {n_cols}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
