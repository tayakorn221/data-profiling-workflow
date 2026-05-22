from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import duckdb


def load_script(name: str):
    script_path = Path(__file__).resolve().parents[1] / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


scan_pii = load_script("02_scan_pii.py")
extract_schema = load_script("01_extract_schema.py")
profile_stats = load_script("03_profile_stats.py")


class PiiScanTests(unittest.TestCase):
    def test_decimal_date_serial_is_not_student_code(self):
        hits = scan_pii.scan_text("244480.78555555554")

        self.assertNotIn("student_code", hits)

    def test_whole_value_student_code_candidate_is_detected(self):
        hits = scan_pii.scan_text("20001000")

        self.assertIn("student_code", hits)


class ExtractSchemaArgsTests(unittest.TestCase):
    def test_extra_sensitive_columns_are_accepted(self):
        args = extract_schema.parse_args(
            [
                "--input",
                "data/input.xlsx",
                "--output",
                "outputs/schema_summary.json",
                "--extra-sensitive",
                "FD02",
                "Date modified",
            ]
        )

        self.assertEqual(args.extra_sensitive, ["FD02", "Date modified"])


class ProfileNumericTests(unittest.TestCase):
    def test_non_finite_numeric_casts_are_ignored(self):
        con = duckdb.connect()
        con.execute('CREATE TABLE raw_data ("FD04" VARCHAR)')
        con.executemany(
            'INSERT INTO raw_data VALUES (?)',
            [("9E0103000",), ("99",), ("100",)],
        )

        stats = profile_stats._profile_numeric(con, "raw_data", "FD04")

        self.assertIsNotNone(stats)
        self.assertEqual(stats["min"], 99.0)
        self.assertEqual(stats["max"], 100.0)


if __name__ == "__main__":
    unittest.main()
