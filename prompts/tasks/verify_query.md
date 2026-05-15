# Task Template — Verify AI-Generated Query

> ใช้ **ก่อนรัน** SQL ที่ AI gen มา กับข้อมูลจริง
> เพื่อให้ AI ตัวเดิม (หรืออีกตัว) ช่วยตรวจ catch bugs

---

# Task

ตรวจสอบ SQL query ด้านล่างก่อนผู้ใช้รันกับ raw_data
ตอบเป็น checklist พร้อมระบุ **PASS/FAIL** ในแต่ละข้อ

# Query to Review

```sql
<paste SQL ที่ต้องการ review ที่นี่>
```

# Checklist

ตรวจตามลำดับนี้:

1. **Column existence** — ทุกคอลัมน์ที่ query ใช้อยู่ใน schema_summary.json จริงไหม?
2. **TRY_CAST** — VARCHAR ที่เก็บตัวเลขมีการ cast ก่อนเปรียบเทียบ/sort ไหม?
3. **NULL handling** — มีคอลัมน์ที่ null rate สูง (>10%) ที่ใช้ใน WHERE/JOIN/GROUP BY ไหม? ถ้ามี ผลอาจ bias
4. **k-anonymity** — GROUP BY ที่อาจ expose ให้คนนอก มี `HAVING COUNT(*) >= 5` ไหม?
5. **Date conversion** — ถ้าใช้คอลัมน์วันที่ (พ.ศ. หรือ Excel serial) มีการแปลงให้ถูกต้องไหม?
6. **Aggregation correctness** — `COUNT(*)` vs `COUNT(col)` ใช้ถูกหรือเปล่า (null behavior ต่าง)
7. **Expected row count** — คาดว่าจะได้กี่แถว ระบุ range
8. **Side effects** — มี `CREATE TABLE`, `INSERT`, `DELETE`, `UPDATE` ไหม? (ควรไม่มีในงาน read-only)

# Output Format

````markdown
## Verification Result: PASS / FAIL

| # | Check | Status | Note |
|---|-------|--------|------|
| 1 | Column existence | ✅ / ❌ | ... |
| 2 | TRY_CAST | ✅ / ❌ | ... |
| ... | ... | ... | ... |

## Issues to Fix (ถ้ามี)

1. **[Severity: High/Med/Low]** <ปัญหา>
   - แก้ยังไง: ...

## Suggested Fix

```sql
-- query ที่แก้แล้ว
```

## Test Steps ก่อน Production Use

1. รันบน sample 100 แถวก่อน (`LIMIT 100`)
2. เปรียบเทียบจำนวนกับ baseline ที่รู้
3. spot-check 5 แถวด้วยตา
````
