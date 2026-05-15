# Quickstart — สำหรับผู้เริ่มต้น

> คู่มือนี้เขียนสำหรับ **คนที่ยังไม่เคยใช้ Python, Git, หรือ PowerShell มาก่อน**
> ถ้าคุณคุ้นเคยแล้ว ไปอ่าน [README.md](../README.md) → Quick Start แทน
>
> เวลาที่ใช้ครั้งแรก: ~10 นาที (รวมติดตั้ง) · ใช้งานปกติ: ~1 นาทีต่อ dataset

---

## สารบัญ

- [📦 Part 0: เตรียมเครื่อง (ครั้งเดียวตลอดชีวิต)](#-part-0-เตรียมเครื่อง-ครั้งเดียวตลอดชีวิต)
- [📥 Part 1: Download repo (ครั้งเดียว)](#-part-1-download-repo-ครั้งเดียว)
- [🚀 Part 2: ใช้งานทุกครั้งที่มี Excel ใหม่](#-part-2-ใช้งานทุกครั้งที่มี-excel-ใหม่)
- [🤖 Part 3: ใช้ outputs กับ Claude / ChatGPT](#-part-3-ใช้-outputs-กับ-claude--chatgpt)
- [🔧 ปัญหาที่อาจเจอ (Troubleshooting)](#-ปัญหาที่อาจเจอ-troubleshooting)
- [📌 Cheatsheet](#-cheatsheet)

---

## 📦 Part 0: เตรียมเครื่อง (ครั้งเดียวตลอดชีวิต)

### Step 0.1 — เปิด PowerShell

กดปุ่ม **Windows** บน keyboard → พิมพ์ `PowerShell` → กด Enter

จะเปิดหน้าต่างสีน้ำเงิน มี prompt `PS C:\Users\STUDENT>` — ใช้พิมพ์คำสั่งได้แล้ว

### Step 0.2 — ตรวจว่ามี Python และ Git

ใน PowerShell พิมพ์ทีละบรรทัด:

```powershell
python --version
git --version
```

**ผลที่ต้องเห็น:**
- `Python 3.13.x` (หรือสูงกว่า) ✅
- `git version 2.x.x` ✅

**ถ้าไม่มี:**
- Python → https://python.org/downloads/ → ดาวน์โหลด → ✓ ติ๊ก **"Add Python to PATH"** ตอนติดตั้ง
- Git → https://git-scm.com/download/win → ดาวน์โหลด → ติดตั้งแบบ default

ติดตั้งเสร็จแล้ว **ปิด PowerShell แล้วเปิดใหม่** (เพื่อให้รู้จักคำสั่งใหม่)

---

## 📥 Part 1: Download repo (ครั้งเดียว)

### Step 1.1 — เลือกที่เก็บ repo

ใน PowerShell ไปที่ Desktop (หรือที่ไหนก็ได้):

```powershell
cd C:\Users\STUDENT\Desktop
```

### Step 1.2 — ดาวน์โหลด repo

```powershell
git clone https://github.com/tayakorn221/data-profiling-workflow.git
```

ใช้เวลา ~10 วินาที จะได้ folder ใหม่ชื่อ `data-profiling-workflow`

### Step 1.3 — เข้าไปใน folder

```powershell
cd data-profiling-workflow
```

### Step 1.4 — ติดตั้ง libraries

```powershell
.\make.ps1 install
```

หรือ:

```powershell
pip install -r requirements.txt
```

ใช้เวลา ~1 นาที ติดตั้ง duckdb, pandas, openpyxl

> **ถ้าเจอ error เรื่อง "scripts is disabled"** ตอนรัน `.\make.ps1` — รันคำสั่งนี้ครั้งเดียว แล้วลองใหม่:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

---

## 🚀 Part 2: ใช้งานทุกครั้งที่มี Excel ใหม่

### Step 2.1 — วางไฟล์ Excel ใน `data/`

สมมุติไฟล์ Excel อยู่ที่ Downloads:

```powershell
copy "C:\Users\STUDENT\Downloads\HUB_STUDENT_FIXREPORT.xlsx" data\input.xlsx
```

> **สำคัญ:** folder `data/` ถูกใส่ใน `.gitignore` แล้ว — ไม่หลุดขึ้น GitHub ปลอดภัยตาม PDPA

### Step 2.2 — รัน pipeline (คำสั่งเดียว)

```powershell
.\make.ps1 all -InputFile data\input.xlsx
```

รอประมาณ 10–30 วินาที จะเห็นข้อความ:

```
สำเร็จ: บันทึก schema ลง outputs\schema_summary.json
จำนวน 26 คอลัมน์, 14,661 แถว
ตรวจสอบเสร็จ — ดูผลที่ outputs\pii_scan_report.txt
พบ 0 จุดเสี่ยง
สำเร็จ: บันทึก profile ลง outputs\profile_stats.json
สร้าง scorecard เสร็จ
Pipeline complete - outputs in outputs\
```

### Step 2.3 — ตรวจ PII report (สำคัญที่สุด!)

```powershell
notepad outputs\pii_scan_report.txt
```

**ต้องเห็น:** `ผลการตรวจสอบ: PII-FREE ✓`

❌ ถ้าเห็น `พบความเสี่ยง X จุด` — **หยุด!** อย่าแชร์ออกไป ปรึกษาทีม + ดู section [Troubleshooting](#-ปัญหาที่อาจเจอ-troubleshooting) ด้านล่าง

### Step 2.4 — เปิด scorecard ดูคุณภาพข้อมูล

```powershell
start outputs\data_quality_scorecard.html
```

จะเปิด browser แสดงตารางสี ๆ ระบุ grade ของแต่ละคอลัมน์ (A/B/C/D/F)

ส่งให้หัวหน้า/ทีมรีวิวได้

---

## 🤖 Part 3: ใช้ outputs กับ Claude / ChatGPT

### Step 3.1 — เปิด chat ใหม่

ไปที่:
- **Claude**: https://claude.ai → คลิก "New chat"
- **ChatGPT**: https://chat.openai.com → คลิก "New chat"

### Step 3.2 — Paste ครั้งที่ 1: System Prompt

ใน PowerShell:

```powershell
notepad prompts\system_prompt.md
```

เปิดใน Notepad แล้ว:
1. กด **Ctrl+A** เลือกทั้งหมด
2. กด **Ctrl+C** copy
3. กลับไปที่ chat
4. กด **Ctrl+V** paste
5. กด **Enter** ส่ง

AI จะตอบประมาณว่า "เข้าใจครับ พร้อมช่วยวิเคราะห์"

### Step 3.3 — Paste ครั้งที่ 2: Context Pack

```powershell
notepad prompts\context_pack.template.md
```

ใน Notepad — **แก้ 3 จุดนี้** (กด Ctrl+H เพื่อ Find & Replace):

| ค้นหา | แทนที่ด้วย |
|---|---|
| `<DATASET_NAME>` | ชื่อ dataset เช่น `STUDENT_REPORT_2569` |
| `<paste เนื้อหา outputs/schema_summary.json ทั้งไฟล์ที่นี่>` | เปิด `outputs\schema_summary.json` → Ctrl+A → Ctrl+C → paste |
| `<paste เนื้อหา outputs/profile_stats.json ทั้งไฟล์ที่นี่>` | เปิด `outputs\profile_stats.json` → Ctrl+A → Ctrl+C → paste |

แก้เสร็จแล้ว: Ctrl+A → Ctrl+C → paste ใน chat → Enter

AI จะตอบ "ได้รับ schema และ profile แล้ว มีอะไรอยากให้ช่วย?"

### Step 3.4 — Paste ครั้งที่ 3: Task

```powershell
notepad prompts\tasks\sql_generation.md
```

แก้ `<ระบุคำถามวิเคราะห์ที่เป็นภาษามนุษย์ เช่น:>` เป็นคำถามจริงของคุณ ตัวอย่าง:

```
หาจำนวนนักศึกษาในแต่ละคณะ แยกตามระดับการศึกษา
ของรุ่นที่รับเข้าปี 2566 ที่ยังอยู่ในสถานะปกติ
```

Ctrl+A → Ctrl+C → paste ใน chat → Enter

✨ AI จะส่ง SQL กลับมาพร้อม assumptions + verification steps

### Step 3.5 — Verify SQL ก่อนรันจริง (recommended)

ก่อนรัน SQL ที่ AI gen ให้รัน verification:

```powershell
notepad prompts\tasks\verify_query.md
```

paste ใน chat พร้อม SQL ที่ได้ → AI จะตอบ checklist ให้แก้ก่อน

### Step 3.6 — รัน SQL ใน DuckDB local

สร้างไฟล์ `my_query.sql` (Notepad → save as) แล้ว paste SQL ที่ AI ตอบมา จากนั้น:

```powershell
python -c "import duckdb; con = duckdb.connect(); con.execute(\"CREATE TABLE raw_data AS SELECT * FROM read_xlsx('data/input.xlsx', all_varchar=true)\"); print(con.execute(open('my_query.sql').read()).fetchdf())"
```

หรือถ้าใช้ Jupyter notebook คุ้นเคยกว่า สร้าง notebook แล้ว:

```python
import duckdb
con = duckdb.connect()
con.execute("CREATE TABLE raw_data AS SELECT * FROM read_xlsx('data/input.xlsx', all_varchar=true)")
con.execute("""
   -- paste SQL ที่ AI ตอบมาที่นี่
""").df()
```

---

## 🔧 ปัญหาที่อาจเจอ (Troubleshooting)

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `python : The term 'python' is not recognized` | ยังไม่ได้ติดตั้ง Python หรือไม่ได้ติ๊ก Add to PATH | ติดตั้ง Python ใหม่ ติ๊ก ✓ **Add Python to PATH** |
| `.\make.ps1 : File ... cannot be loaded because running scripts is disabled` | PowerShell block .ps1 by default | รันครั้งเดียว: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` แล้วตอบ Y |
| `ModuleNotFoundError: No module named 'duckdb'` | ลืม pip install | รัน `.\make.ps1 install` |
| `ผิดพลาด: ไม่พบไฟล์ input` | path ผิด หรือยังไม่ copy ไฟล์ | ตรวจด้วย `ls data\` ว่ามีไฟล์จริง |
| `Conversion Error: Could not convert string '...' to INT` | DuckDB เดา type ผิด | script ใส่ `all_varchar=true` ให้แล้ว ปกติไม่เจอ |
| `พบความเสี่ยง X จุด` ใน PII scan | มี PII หลุดเข้า top_values | 1) เปิดดู `outputs\schema_summary.json` หาคอลัมน์ที่มีค่าเป็นเลข 13 หลัก/อีเมล/เบอร์ 2) เพิ่ม `--sensitive COL1 COL2` ตอนรัน script 01 |
| Thai text แสดงเพี้ยนใน PowerShell | Console encoding ไม่ใช่ UTF-8 | รัน `chcp 65001` ก่อนใช้ |
| AI ตอบ "ขอ schema เพิ่ม" | ลืม paste context pack | ย้อนไปทำ Step 3.3 |

---

## 📌 Cheatsheet

**สำหรับใช้ทุกวัน** — copy 5 คำสั่งนี้เก็บไว้:

```powershell
# 1) ไปที่ repo
cd C:\Users\STUDENT\Desktop\data-profiling-workflow

# 2) copy Excel ใหม่ลง data/
copy "C:\path\to\new.xlsx" data\input.xlsx

# 3) รัน pipeline
.\make.ps1 all -InputFile data\input.xlsx

# 4) ตรวจ PII (ต้องเห็น "PII-FREE ✓")
notepad outputs\pii_scan_report.txt

# 5) เปิด scorecard
start outputs\data_quality_scorecard.html
```

แล้ว paste 3 ไฟล์ใน `prompts/` เข้า Claude/ChatGPT ตามลำดับ

---

## 📚 อ่านเพิ่ม

- [Tutorial ฉบับเต็ม](tutorial.md) — เข้าใจ PDPA, k-anonymity, DuckDB เชิงลึก
- [Glossary](glossary.md) — business rules + status codes ของ KMUTT
- [Prompts README](../prompts/README.md) — workflow ใช้ AI แบบ sustainable

มีคำถาม → เปิด [issue บน GitHub](https://github.com/tayakorn221/data-profiling-workflow/issues)
