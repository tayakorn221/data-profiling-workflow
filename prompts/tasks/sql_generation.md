# Task Template — Write DuckDB SQL

> Copy ข้อความนี้ paste ใน chat **หลังจาก** system prompt และ context pack
> แล้วแก้ส่วน `<...>` ให้ตรงกับคำถาม

---

# Task

เขียน DuckDB SQL query สำหรับ:

**<ระบุคำถามวิเคราะห์ที่เป็นภาษามนุษย์ เช่น:>**
- หาอัตราการคงอยู่ของนักศึกษาแต่ละคณะ แยกตามชั้นปี ของรุ่นที่รับเข้าปี 2566
- เปรียบเทียบจำนวนนักศึกษาต่างชาติระหว่างหลักสูตรไทยกับนานาชาติ ในแต่ละคณะ
- หาคณะที่มีสัดส่วนนักศึกษาพ้นสภาพสูงที่สุด 5 อันดับ

# Constraints

- ใช้ column names ตาม schema เท่านั้น — ถ้าจะใช้คอลัมน์ที่ไม่อยู่ใน schema ให้ถามก่อน
- คอลัมน์ที่เป็น VARCHAR แต่เก็บตัวเลข → ต้อง `TRY_CAST` ก่อน
- GROUP BY ที่อาจ expose ให้คนนอกเห็น → ใส่ `HAVING COUNT(*) >= 5`
- ใช้ DuckDB syntax (รองรับ `QUALIFY`, window functions, `PIVOT`)
- ถ้ามี business rule ที่ต้องเดา — ระบุเป็น assumption พร้อมขอผู้ใช้ confirm

# Expected Output Format

````markdown
## Assumptions
- ...

## Query
```sql
WITH cleaned AS (
  SELECT ... FROM raw_data WHERE ...
)
SELECT ...
```

## Verification Steps
1. `SELECT COUNT(*) FROM cleaned` — ควรได้ ~<n> แถว
2. ตรวจ NULL ในคอลัมน์ key
3. spot-check 5 แถวแรกของผลลัพธ์

## Caveats
- ...
````

# Additional Context (optional)

`<เช่น "ผลนี้จะใช้ใน dashboard ผู้บริหาร เน้นเร็วและอ่านง่าย ไม่ต้อง over-engineer">`
