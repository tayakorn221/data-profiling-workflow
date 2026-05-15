# Glossary — KMUTT Student Registration Data

> **วัตถุประสงค์:** institutional knowledge ที่ AI ไม่รู้จากข้อมูลอย่างเดียว
> เก็บกฎ business, ความหมายของรหัส, และความสัมพันธ์ระหว่างคอลัมน์
>
> **Maintainer:** สำนักงานยุทธศาสตร์ KMUTT
> **Review:** ทุกปลายภาคการศึกษา
>
> **กฎการเพิ่ม entry:**
> 1. เพิ่มเมื่อเจอ "เออ คอลัมน์นี้หมายความว่าไง?" ครั้งที่ 2
> 2. ทุก entry ต้องมีแหล่งที่มา (เอกสาร, การประชุม, หรือผู้บอก) + วันที่บันทึก
> 3. ถ้ารู้สึกว่ารูสึก "อาจไม่ตรงแล้ว" — flag ด้วย ⚠

---

## สารบัญ

1. [ปีการศึกษา (Academic Year)](#1-ปีการศึกษา-academic-year)
2. [Status Codes](#2-status-codes)
3. [Education Levels](#3-education-levels)
4. [Program Types](#4-program-types)
5. [Faculty Codes](#5-faculty-codes)
6. [Admission Groups](#6-admission-groups)
7. [Date Columns](#7-date-columns)
8. [Known Joins and Relationships](#8-known-joins-and-relationships)
9. [Data Quality Notes](#9-data-quality-notes)

---

## 1. ปีการศึกษา (Academic Year)

- ระบบใช้ **พุทธศักราช (พ.ศ.)** ในคอลัมน์ที่ลงท้ายด้วย `ACAD_YEAR`
- การแปลงเป็น ค.ศ.: `พ.ศ. - 543`
- **ปีการศึกษา ≠ ปีปฏิทิน** — ปีการศึกษา 2566 เริ่ม ส.ค. 2566 และจบ พ.ค. 2567

```sql
-- แปลง ADMIT_ACAD_YEAR (พ.ศ.) เป็น ค.ศ.
SELECT TRY_CAST(ADMIT_ACAD_YEAR AS INTEGER) - 543 AS admit_year_ce
FROM raw_data;
```

**บันทึก:** 2026-05-15 — ตรวจสอบกับ ระเบียบการรับเข้า 2566

---

## 2. Status Codes

> ⚠ ค่าที่ระบุด้านล่าง **ขึ้นกับ snapshot** — ตรวจกับ schema_summary.json ปัจจุบันก่อนใช้

### REGIS_STATUS

สถานะการลงทะเบียนในภาคปัจจุบัน

| Value (จากข้อมูลจริง) | ความหมาย |
|---|---|
| `ลงทะเบียน` | ลงทะเบียนเรียนภาคปัจจุบัน |
| `ลาพัก` | ลาพักการศึกษาในภาคปัจจุบัน |

**Note:** ตำราเก่าอาจใช้ `Y`/`N` — ระบบปัจจุบันใช้ภาษาไทย

### STUDENT_STATUS_NAME

สถานะนักศึกษาในระบบ (ระยะยาว)

| Value | ความหมาย |
|---|---|
| `ปกติ` | นักศึกษาที่ยังอยู่ในระบบ |
| `ลาพัก` | ลาพักนาน (ไม่ใช่ภาคเดียว) |
| `<เพิ่ม>` | <ถ้าเจอ value อื่น เพิ่มที่นี่> |

### ENT_STATUS_NAME

สถานะการเข้าศึกษา (entry status)

| Value | ความหมาย |
|---|---|
| `<value>` | `<ความหมาย — ต้องสอบถามฝ่ายทะเบียน>` |

---

## 3. Education Levels

จากคอลัมน์ `EDUCATION_LEVEL_NAME`:

| Value | ระดับ | จำนวนปีมาตรฐาน |
|---|---|---|
| ปริญญาตรี | Bachelor's | 4 |
| ปริญญาโท | Master's | 2 |
| ปริญญาเอก | Doctoral | 3–4 |

ใช้ร่วมกับ `PROGRAM_NUM_YEAR` (จำนวนปีของหลักสูตรนั้นโดยเฉพาะ) เพื่อคำนวณ expected graduation year

---

## 4. Program Types

จากคอลัมน์ `PROGRAMTYPE`:

| Value | ความหมาย | ข้อสังเกต |
|---|---|---|
| หลักสูตรไทย | สอนภาษาไทยเป็นหลัก | สัดส่วน 80%+ |
| หลักสูตรนานาชาติ | สอนภาษาอังกฤษ | คิดค่าเทอมต่างกัน |
| หลักสูตรร่วมกัน | dual degree | ส่วนใหญ่กับมหาวิทยาลัยต่างชาติ |
| หลักสูตรท้องถิ่น | regional program | จำนวนน้อย ระวัง k < 5 ใน breakdown ละเอียด |

---

## 5. Faculty Codes

> **TODO:** สำนัก ฯ เก็บ list mapping `<FACULTY_CODE>` → `<FACULTY_NAME_TH>` ที่ไหน?
> แนะนำให้ link ที่นี่ (Google Sheets / Notion / etc.)

ที่รู้จากข้อมูลปัจจุบัน:

- `FACULTY_NAME_TH` มี 12 ค่า unique
- `DEPT_NAME_TH` มี 35 ค่า unique (รวมทุกคณะ)
- `<เพิ่ม mapping เมื่อรู้>`

---

## 6. Admission Groups

จาก `ADMISSION_GROUP_NAME` (37 ค่า unique):

โดยทั่วไปแบ่งเป็น:
- **TCAS รอบต่าง ๆ** (รอบ 1 portfolio, รอบ 2 quota, รอบ 3 admission, รอบ 4 direct, รอบ 5 รับตรง)
- **โควตาพิเศษ** (โครงการสานฝัน, ทุน พสวท., เด็กดีมีคุณธรรม, ฯลฯ)
- **โครงการรับเข้าโดยตรงระดับบัณฑิตศึกษา**

> ⚠ ค่าจริงทั้งหมดอยู่ใน `outputs/schema_summary.json` — ดู `top_values` ของคอลัมน์นี้

---

## 7. Date Columns

### EXPORTDATE

- Type: VARCHAR ที่เก็บ Excel serial date (เลข 5 หลัก เช่น `45000`)
- ความหมาย: **วันที่ export ข้อมูลออกจากระบบ** (ไม่ใช่วันที่ event ของนักศึกษา)
- การแปลง:

```sql
SELECT
  EPOCH_MS(0) + (TRY_CAST(EXPORTDATE AS INTEGER) - 2) * INTERVAL '1 day' AS export_date
FROM raw_data
LIMIT 1;
```

**สูตร -2:** เพราะ Excel นับ 1900 เป็นปี leap year (bug ที่ Excel ตั้งใจ keep เพื่อ compat กับ Lotus 1-2-3)

---

## 8. Known Joins and Relationships

> ปัจจุบัน schema นี้เป็น **flat table** (denormalized) — ไม่มี foreign keys ที่ต้อง join
> ถ้ามี dataset อื่นที่ต้อง join เพิ่มที่นี่:

| Source column | Target table | Target column | Note |
|---|---|---|---|
| `STUDENT_ID` | `<external_table>` | `<col>` | `<purpose — ต้องผ่าน DPO ก่อน>` |

---

## 9. Data Quality Notes

จากการตรวจ schema เมื่อ 2026-05-15:

### High null rate (>50%)

- `MAJOR_CODE` — 88.6% null
- `MAJORNAME` — 88.8% null
- `MAJOR` — 80.1% null

**Hypothesis:** คอลัมน์ MAJOR ใช้เฉพาะหลักสูตรที่มี major declaration อาจไม่ครอบคลุมทุกระดับ

### Quasi-identifier risk

Combinations ที่ระบุตัวคนได้ทางอ้อม:

- FACULTY × DEPT × ADMIT_YEAR × SCHOOLPROV
- FACULTY × FIELD × ADMIT_YEAR × IS_FOREIGN_STUDENT (ในกลุ่ม foreign students ขนาดเล็ก)

**Mitigation:** ใส่ `HAVING COUNT(*) >= 5` ทุก breakdown ที่ผลจะส่งออกนอกองค์กร

### Excel serial dates

ทุกคอลัมน์ที่เก็บวันที่ใน Excel format อาจมีค่า `0` (วันที่ 1900-01-00 ที่ไม่ valid) — กรองทิ้งก่อนแปลง

---

## Maintenance Log

| Date | Editor | Change |
|---|---|---|
| 2026-05-15 | <name> | Initial creation จาก schema snapshot 14,661 rows |
| `<YYYY-MM-DD>` | `<name>` | `<change>` |
