# Context Pack — `<DATASET_NAME>`

> Template สำหรับ paste ใส่ AI ครั้งเดียวต่อ session
> หลังจาก system prompt และก่อนถามคำถามใด ๆ
>
> **วิธีใช้:**
> 1. รัน pipeline (01–04) ได้ `outputs/schema_summary.json` และ `outputs/profile_stats.json`
> 2. ตรวจสอบ `outputs/pii_scan_report.txt` ว่า PII-FREE
> 3. แทนค่าใน `< >` ทุกที่
> 4. paste ทั้งไฟล์นี้ใน chat

---

## Dataset Info

- **ชื่อตาราง (DuckDB):** `raw_data`
- **ไฟล์ต้นทาง:** `<ระบุชื่อไฟล์ — เช่น HUB_STUDENT_FIXREPORT_2569_05_14.xlsx>`
- **วันที่ export:** `<YYYY-MM-DD>`
- **จำนวนแถว × คอลัมน์:** `<ดูจาก schema_summary.json>`
- **k-anonymity threshold ที่ใช้:** `5`
- **PII scan status:** ✅ PII-FREE (ตรวจเมื่อ `<YYYY-MM-DD>`)

---

## Schema Summary

```json
<paste เนื้อหา outputs/schema_summary.json ทั้งไฟล์ที่นี่>
```

---

## Profile Statistics

```json
<paste เนื้อหา outputs/profile_stats.json ทั้งไฟล์ที่นี่>
```

---

## Business Rules / Glossary

> สิ่งที่ AI ไม่รู้จากข้อมูลอย่างเดียว — ทีมเป็นคนเพิ่ม
> ดู `docs/glossary.md` สำหรับ rules ส่วนกลาง และเพิ่มเฉพาะ dataset นี้ด้านล่าง

### Status Codes

- **REGIS_STATUS:**
  - `<value>` = `<ความหมาย>`
- **STUDENT_STATUS_NAME:**
  - `<value>` = `<ความหมาย>`

### Date Conventions

- `ADMIT_ACAD_YEAR` = ปีการศึกษาที่รับเข้า (**พ.ศ.**, ไม่ใช่ ค.ศ.)
- `EXPORTDATE` = Excel serial date — แปลงด้วย `EPOCH_MS(0) + (TRY_CAST(EXPORTDATE AS INTEGER) - 2) * INTERVAL '1 day'`

### Derived Columns ที่ใช้บ่อย

```sql
-- ปีการศึกษาเป็น ค.ศ.
TRY_CAST(ADMIT_ACAD_YEAR AS INTEGER) - 543 AS admit_year_ce

-- gap years นับจากปีรับเข้า
2026 - (TRY_CAST(ADMIT_ACAD_YEAR AS INTEGER) - 543) AS gap_years
```

### Known Pitfalls

- คอลัมน์ `MAJOR_CODE`, `MAJORNAME` มี null rate สูง (~88%) — ใช้กับเฉพาะ subset ที่กรอกครบ
- `STUDENT_ID` ไม่ unique ในระดับชั่วชีวิต — student อาจมีรหัสคนละตัวถ้า re-admit
- `<เพิ่ม pitfall อื่น ๆ ที่ทีมเจอ>`

---

## งานที่อยากให้ช่วย

`<เขียนคำถามหรือ task ที่นี่ — อ้างอิง `prompts/tasks/*.md` ได้ถ้าเป็นงานมาตรฐาน>`
