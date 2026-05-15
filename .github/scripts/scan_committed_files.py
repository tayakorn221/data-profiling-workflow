"""สแกนไฟล์ที่ commit หา PII patterns — block CI ถ้าพบ

ใช้ใน GitHub Actions เพื่อตรวจสอบ pull request / push ว่าไม่มี
ข้อมูลส่วนบุคคล (PII) หลุดเข้าไปในไฟล์ที่จะถูก merge

รับ list ของไฟล์จากสองทาง:
- `--files-from <file>`: อ่านชื่อไฟล์จากแต่ละบรรทัด (รูปแบบที่ GH Actions ใช้)
- positional args: ระบุชื่อไฟล์ตรง ๆ

ตัวอย่าง:
    python .github/scripts/scan_committed_files.py --files-from changed_files.txt
    python .github/scripts/scan_committed_files.py docs/notes.md data/people.csv
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# whitelist สำหรับไฟล์ตัวอย่างที่ตรวจแล้วว่าเป็น synthetic
WHITELIST_PATHS = {
    "examples/sample_schema_summary.json",
    "examples/sample_data_quality_scorecard.html",
}

# ข้าม binary และไฟล์ที่ไม่เกี่ยวข้อง
SKIP_EXTENSIONS = {
    ".docx", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg",
    ".gif", ".svg", ".ico", ".zip", ".tar", ".gz", ".whl",
}

# scan เฉพาะ text-y extensions
SCAN_EXTENSIONS = {
    ".md", ".json", ".yaml", ".yml", ".txt", ".py", ".sql",
    ".html", ".csv", ".tsv", ".ini", ".cfg", ".toml",
}

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    "thai_citizen_id": re.compile(r"\b\d{13}\b"),
    "thai_phone": re.compile(r"\b0\d{8,9}\b"),
    "email": re.compile(r"[\w.+-]+@[\w.-]+\.\w+"),
}

# patterns ที่ดูเหมือน PII แต่ปลอดภัย (เช่น regex เอง, placeholder)
ALLOWLIST_LINE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"r['\"]\\b\\d\{13\}\\b['\"]"),  # regex literal
    re.compile(r"r['\"]\\b0\\d\{8,9\}\\b['\"]"),
    re.compile(r"\bexample\.com\b", re.IGNORECASE),
    re.compile(r"\bplaceholder\b", re.IGNORECASE),
    re.compile(r"\bnoreply@", re.IGNORECASE),
    re.compile(r"\bname@example", re.IGNORECASE),
]


def should_scan(path: Path) -> bool:
    """กรองไฟล์ที่ไม่ควร scan"""
    if str(path).replace("\\", "/") in WHITELIST_PATHS:
        return False
    ext = path.suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return False
    if ext and ext not in SCAN_EXTENSIONS:
        return False
    return True


def is_allowlisted_line(line: str) -> bool:
    return any(pat.search(line) for pat in ALLOWLIST_LINE_PATTERNS)


def scan_file(path: Path) -> list[dict]:
    """สแกนไฟล์เดียว คืน list of findings"""
    findings: list[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        print(f"ข้อผิดพลาด: อ่าน {path} ไม่ได้ — {exc}", file=sys.stderr)
        return findings

    for lineno, line in enumerate(text.splitlines(), start=1):
        if is_allowlisted_line(line):
            continue
        for name, pat in PII_PATTERNS.items():
            match = pat.search(line)
            if match:
                findings.append({
                    "file": str(path).replace("\\", "/"),
                    "line": lineno,
                    "pattern": name,
                    "match": match.group(0),
                    "context": line.strip()[:200],
                })
    return findings


def collect_files(args: argparse.Namespace) -> list[Path]:
    files: list[Path] = []
    if args.files_from:
        text = args.files_from.read_text(encoding="utf-8")
        for raw in text.splitlines():
            name = raw.strip()
            if name:
                files.append(Path(name))
    files.extend(Path(p) for p in args.files)
    return files


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="สแกนไฟล์ที่ commit หา PII patterns (เลขบัตร 13 หลัก, เบอร์, อีเมล)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="ชื่อไฟล์ที่ต้องการ scan",
    )
    parser.add_argument(
        "--files-from",
        type=Path,
        help="อ่านชื่อไฟล์จากไฟล์ text นี้ (บรรทัดละ 1 ชื่อ)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    files = collect_files(args)

    all_findings: list[dict] = []
    scanned = 0
    for path in files:
        if not path.exists():
            continue
        if not should_scan(path):
            continue
        scanned += 1
        all_findings.extend(scan_file(path))

    print(f"สแกน {scanned} ไฟล์ — พบ {len(all_findings)} จุดเสี่ยง")

    if all_findings:
        print("\nจุดที่พบ PII pattern:", file=sys.stderr)
        for hit in all_findings:
            print(
                f"  {hit['file']}:{hit['line']}  [{hit['pattern']}]  "
                f"match={hit['match']!r}  context={hit['context']!r}",
                file=sys.stderr,
            )
        print(
            "\nFAIL: ห้าม merge — กรุณาลบ PII ออกจากไฟล์ที่ระบุ "
            "หรือเพิ่ม path ลงใน WHITELIST_PATHS ถ้ายืนยันว่าเป็น synthetic",
            file=sys.stderr,
        )
        return 1

    print("PASS: ไม่พบ PII pattern ในไฟล์ที่ commit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
