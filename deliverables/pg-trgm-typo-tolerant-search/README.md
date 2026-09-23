# pg_trgm Typo-Tolerant Search — คู่มือสคริปต์ทดสอบ

คู่มือนี้อธิบายสคริปต์ `pg_trgm_typo_tolerant_search.sql` ทีละส่วน ว่าแต่ละส่วนทดสอบอะไร ทำไมจึงเขียนแบบนั้น และควรอ่านผลลัพธ์อย่างไร

**บริบทที่มา:** การค้นหาผ่าน Fig Search ที่ถามเรื่อง pg_trgm similarity threshold คืนค่า `No results captured` เพราะ **Fig Search ถึง usage limit** ไม่ใช่เพราะไม่มีข้อมูลหรือ syntax ผิด สคริปต์นี้จึงเป็นทางออกที่ทดสอบได้ตรงใน PostgreSQL เอง ไม่ต้องพึ่ง Search tool ใด ๆ

## สิ่งที่ต้องมี

- PostgreSQL 12 ขึ้นไป (ทดสอบบน PostgreSQL 17)
- สิทธิ์สร้าง extension (`pg_trgm` อยู่ใน `postgresql-contrib`)
- ฐานข้อมูลสำหรับทดสอบ (สคริปต์สร้างตารางของตัวเองทับได้ ไม่แตะตารางเดิม)

## วิธีรัน

```bash
psql -d your_db -f pg_trgm_typo_tolerant_search.sql
```

สคริปต์ตั้ง `\set ON_ERROR_STOP on` ไว้ จึงหยุดทันทีเมื่อเจอ error และปิด pager เพื่อให้อ่านผลในเทอร์มินัลได้ตรง ๆ

## ภาพรวม 8 ส่วน

| ส่วน | หัวข้อ | คำสั่ง/แนวคิดหลัก |
|---|---|---|
| 1 | Extension + config | `CREATE EXTENSION`, `LOAD`, `SHOW`/`SET similarity_threshold` |
| 2 | `similarity()` | ให้คะแนน 0.0–1.0 ระหว่างสองสตริง |
| 3 | `%` operator | กรองเฉพาะที่ผ่าน threshold + `ORDER BY similarity DESC` |
| 4 | ปรับ threshold | เทียบ 0.5 / 0.3 / 0.25 + `SET LOCAL` |
| 5 | GIN index | `gin_trgm_ops` + `EXPLAIN` ยืนยัน index ถูกใช้ |
| 6 | `word_similarity` | หาคำในข้อความยาว + operator `<%` และ `<<%` |
| 7 | normalize | อะไรมีผล/ไม่มีผลต่อคะแนน |
| 8 | assertions | 12 ข้อ ตรวจว่า pg_trgm ทำงานตามคาด |

---

## ส่วนที่ 1 — Extension + Config

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
LOAD 'pg_trgm';
SHOW pg_trgm.similarity_threshold;      -- default 0.3
SHOW pg_trgm.word_similarity_threshold; -- default 0.6
SET pg_trgm.similarity_threshold = 0.3;
```

**ทำไมต้องมี `LOAD`** — นี่คือจุดที่พลาดกันบ่อยที่สุด ถ้า extension ถูกติดตั้งไว้แล้ว `CREATE EXTENSION IF NOT EXISTS` จะไม่รัน SQL ภายในของ extension ทำให้ GUC อย่าง `pg_trgm.similarity_threshold` **ยังไม่ถูก register ใน session นั้น** แล้วสคริปต์จะล้มด้วย `unrecognized configuration parameter` เมื่อรันครั้งที่สอง

`LOAD 'pg_trgm'` บังคับโหลด library ทุกครั้งที่รัน จึงทำให้สคริปต์ **รันซ้ำได้ (idempotent)** โดยไม่ error

`SET` มีผลแค่ session ปัจจุบัน ไม่กระทบ session อื่น

## ส่วนที่ 2 — ฟังก์ชัน `similarity()`

```sql
SELECT similarity('postgres', 'postgre');  -- สูง (~0.6)
SELECT similarity('postgres', 'postgres'); -- 1.0 (เหมือนกันเป๊ะ)
SELECT similarity('postgres', 'mysql');    -- ต่ำมาก
SELECT similarity('jon', 'jhon');          -- typo แต่ยังได้คะแนนสูง
```

`similarity(a, b)` คืนค่า 0.0–1.0 บอกว่า a กับ b คล้ายกันแค่ไหน คำนวณจากจำนวน trigram (ชุดตัวอักษร 3 ตัวเรียงกัน) ที่ทับซ้อนกัน

ส่วนท้ายของส่วนนี้มีตารางเทียบหลายคู่พร้อมกัน (`jon` เทียบกับ `jon`, `jhon`, `john`, `johnny`, `json`, `unrelated`) เพื่อให้เห็นว่าคะแนนไล่ระดับอย่างไร — ใช้ `VALUES` + `CROSS JOIN LATERAL` เพื่อให้ได้ผลในคิวรีเดียว

## ส่วนที่ 3 — `%` operator + `ORDER BY similarity DESC`

```sql
SELECT name, similarity(name, 'jon') AS score
FROM users
WHERE name % 'jon'
ORDER BY score DESC;
```

`%` คือ **ตัวกรอง** ไม่ใช่ตัวให้คะแนน — มันคืน `true` เมื่อ `similarity(a,b) >= similarity_threshold` เท่านั้น จึงต้องเรียก `similarity()` แยกอีกครั้งถ้าต้องการตัวเลขมาเรียงลำดับ

**รูปแบบที่ควรใช้จริง:** `WHERE name % 'term'` คู่กับ `ORDER BY similarity(name,'term') DESC` เสมอ — `%` ทำหน้าที่ตัดแถวทิ้ง (และใช้ index ได้) ส่วน `ORDER BY` ทำหน้าที่จัดอันดับความคล้าย

ตาราง `users` ในส่วนนี้มี 15 แถว ครอบคลุมทั้งชื่อที่ใกล้เคียงและไม่ใกล้เคียง เพื่อให้เห็นว่า `%` กรองอะไรออก

## ส่วนที่ 4 — ปรับ Threshold

```sql
SET pg_trgm.similarity_threshold = 0.5;   -- เข้ม: ผลลัพธ์น้อย
SET pg_trgm.similarity_threshold = 0.3;   -- default
SET pg_trgm.similarity_threshold = 0.25;  -- ผ่อน: typo tolerance มากขึ้น
```

หลักการเลือกค่า:

- **สูงขึ้น (0.5+)** → เข้มขึ้น แม่นขึ้น แต่พลาดคำที่พิมพ์ผิดมาก
- **ต่ำลง (0.25 หรือน้อยกว่า)** → จับ typo ได้มากขึ้น แต่ได้ noise เพิ่มขึ้น
- **0.3** เป็นค่าที่สมดุลสำหรับชื่อคน/คำสั้นทั่วไป

ส่วนนี้ยังสาธิต **`SET LOCAL` ภายใน transaction** ซึ่งเป็นวิธีที่สะอาดที่สุดเมื่อต้องใช้ threshold ต่างกันในคิวรีเดียว — มีผลแค่จนจบ transaction แล้ว revert อัตโนมัติ:

```sql
BEGIN;
SET LOCAL pg_trgm.similarity_threshold = 0.2;
SELECT name, similarity(name,'jon') AS score FROM users
WHERE name % 'jon' ORDER BY score DESC;
COMMIT;
```

## ส่วนที่ 5 — GIN Index

```sql
CREATE INDEX idx_big_users_name_trgm
    ON big_users USING gin (name gin_trgm_ops);
ANALYZE big_users;
```

**ข้อควรระวังสำคัญ:** บน**ตารางเล็ก** planner จะเลือก **Seq Scan** เพราะ cost ต่ำกว่า — **ไม่ใช่เพราะ index ใช้ไม่ได้** ถ้าทดสอบบนตาราง 15 แถวแล้วไม่เห็น index อย่าด่วนสรุปว่า index เสีย

ส่วนนี้จึงสร้างตาราง `big_users` 20,000 แถวขึ้นไปเพื่อให้ planner เลือกใช้ **Bitmap Index Scan** จริง แล้วใช้ `EXPLAIN (COSTS OFF)` ยืนยัน:

```sql
EXPLAIN (COSTS OFF) SELECT name FROM big_users WHERE name % 'jon';
```

index `gin_trgm_ops` ยังรองรับ `LIKE` / `ILIKE` แบบมี `%` นำหน้าด้วย ซึ่งปกติ index ปกติทำไม่ได้

## ส่วนที่ 6 — `word_similarity` / `strict_word_similarity`

`similarity()` เทียบสตริงทั้งก้อน แต่ `word_similarity()` หาคำในข้อความยาว — เหมาะกับ search ในประโยค/ย่อหน้า

```sql
word_similarity('jon', 'jonathan smith')        -- เทียบคู่ที่คล้ายสุด
strict_word_similarity('jon', 'jonathan smith') -- เข้มกว่า: ต้องเป็นคำเต็ม
```

Operator ที่คู่กัน (ใช้ `word_similarity_threshold` ซึ่ง default 0.6):

- `<%` → `word_similarity` ผ่าน threshold
- `<<%` → `strict_word_similarity` ผ่าน threshold

ใช้เมื่อค้นหาในฟิลด์ข้อความยาว เช่น ชื่อสินค้า บทความ หรือคำอธิบาย

## ส่วนที่ 7 — Normalize: อะไรมีผล/ไม่มีผล

ส่วนนี้แก้ความเข้าใจผิดที่พบบ่อย — **`similarity()` ไม่สนใจตัวพิมพ์และช่องว่างหัว-ท้ายอยู่แล้ว** เพราะ pg_trgm แปลงเป็นตัวพิมพ์เล็กและ pad ช่องว่างหัว-ท้ายเป็น 2 ตัวให้ก่อนคำนวณ:

```sql
similarity('Jon', 'jon')     -- = 1.0
similarity('  jon  ', 'jon') -- = 1.0
similarity('jon!', 'jon')    -- เครื่องหมายวรรคตอนถูกตัดทิ้ง
```

**สิ่งที่มีผลจริงต่อคะแนน:**

- **ช่องว่างกลางคำ** — `'j o n'` เทียบ `'jon'` ได้คะแนนต่ำมาก (trigram ถูกแยก)
- **Accent** — `'josé'` กับ `'jose'` ได้คะแนนไม่เท่าเดิม
- **ภาษาไทย** — ใช้ได้ แต่รูปแบบสระ/วรรณยุกต์ที่พิมพ์ต่างกันมีผล ควร normalize ก่อน

แนวปฏิบัติที่ควรทำจริง:

1. `trim` + `lower` (ถึง pg_trgm ทำให้แล้ว ทำไว้เพื่อความชัดเจน)
2. บีบช่องว่างซ้ำ: `regexp_replace(x, '\s+', ' ', 'g')`
3. ถอด accent: `CREATE EXTENSION unaccent; unaccent(x)`
4. ภาษาไทย: normalize รูปแบบการพิมพ์ (เช่น ซ้ำวรรณยุกต์) ก่อนเทียบ

## ส่วนที่ 8 — Assertions

สคริปต์ปิดท้ายด้วย assertion 12 ข้อที่ตรวจว่า pg_trgm ทำงานตามที่คาด พร้อมตาราง `PASS`/`FAIL` และตัวเลขสรุป `passed` / `failed` / `total`

ผลรันจริงบน PostgreSQL 17:

```
 passed | failed | total
--------+--------+-------
     12 |      0 |    12
```

assertion ที่น่าสนใจ:

- `similarity('postgres','postgres') = 1.0` — ตัวเหมือนกันต้องได้ 1.0 เป๊ะ
- `similarity('jhon','jon') < 0.5` — ยืนยันว่าทำไม typo จึงหลุดที่ threshold 0.5 แต่ผ่านที่ 0.3
- `similarity('  jon  ','jon') = 1.0` — ยืนยันว่าช่องว่างหัว-ท้ายไม่มีผล
- `similarity('j o n','jon') < 0.3` — ยืนยันว่าช่องว่างกลางคำมีผลจริง
- GIN index ถูกสร้างและถูกใช้จริงบนตารางใหญ่

## สรุปแนวคิด

```
query
  ↓
normalize (trim / lower / collapse whitespace / unaccent)
  ↓
pg_trgm similarity
  ↓
similarity_threshold  ── ตัดสินว่าแถวไหนผ่าน
  ↓
candidate matches
  ↓
ORDER BY similarity DESC  ── จัดอันดับความคล้าย
```

## ข้อควรระวังที่เจอจากการทดสอบจริง

1. **`LOAD 'pg_trgm'` จำเป็น** ถ้าต้องการให้สคริปต์รันซ้ำได้ — `CREATE EXTENSION IF NOT EXISTS` ไม่ register GUC ให้
2. **ตารางเล็กไม่ใช้ index** — อย่าสรุปว่า index เสียจากตารางทดสอบขนาดเล็ก ต้องมีข้อมูลพอจึงเห็น Bitmap Index Scan
3. **`%` เป็นตัวกรอง ไม่ใช่ตัวให้คะแนน** — ต้องเรียก `similarity()` แยกถ้าจะเรียงลำดับ
4. **`similarity()` ไม่สนใจ case/trim อยู่แล้ว** — ที่ต้อง normalize จริงคือช่องว่างกลางคำและ accent
5. **threshold ระดับ session** — ใช้ `SET LOCAL` เมื่อต้องใช้หลายค่าใน transaction เดียว
