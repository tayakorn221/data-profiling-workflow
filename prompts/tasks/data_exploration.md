# Task Template — Exploratory Analysis Suggestions

> ใช้เมื่อยังไม่รู้ว่าควรวิเคราะห์อะไร แต่อยากให้ AI **เสนอ ideas**
> ก่อนจะกระโดดไปเขียน SQL

---

# Task

ดู `schema_summary.json` และ `profile_stats.json` ที่ให้ไป
แล้วเสนอ **5 คำถามวิเคราะห์ที่น่าสนใจ** ที่:

1. ตอบได้ด้วยข้อมูลที่มี (ไม่ต้องไปดึงเพิ่ม)
2. มีนัยสำคัญทางยุทธศาสตร์ของมหาวิทยาลัย
3. ผ่าน k-anonymity (ทุก breakdown มีคนอย่างน้อย 5)

# Output Format

````markdown
## คำถามที่ 1: <ชื่อคำถาม>

**Business value:** <ทำไมต้องตอบ คนได้ประโยชน์ยังไง>

**คอลัมน์ที่ใช้:** `<col1>`, `<col2>`, `<col3>`

**Sketch ของ query:**
```sql
SELECT ... FROM raw_data GROUP BY ... HAVING COUNT(*) >= 5
```

**สิ่งที่ต้องระวัง:** <PDPA / data quality issues>

---

## คำถามที่ 2: ...
````

# Constraints

- ห้ามเสนอคำถามที่ต้องใช้ row-level join กับ identifier
- ห้ามเสนอคำถามที่ผลลัพธ์อาจมี cell < 5 คน
- เสนอ trade-off ระหว่างความสำคัญและ feasibility
- เน้น actionable insights — ไม่ใช่แค่ "น่าสนใจ"

# Additional Context

`<เช่น "ทีมเน้นยุทธศาสตร์ด้าน retention และ international students ในปี 2026">`
