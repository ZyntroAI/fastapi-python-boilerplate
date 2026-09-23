-- =============================================================================
-- pg_trgm_typo_tolerant_search.sql
-- ทดสอบ pg_trgm similarity threshold + typo-tolerant search ครบวงจร
-- PostgreSQL 17 · รันซ้ำได้ (idempotent) · ไม่ต้องพึ่ง Fig Search tool
-- -----------------------------------------------------------------------------
-- ลำดับการทำงาน:
--   1) extension + config (threshold)
--   2) similarity() function
--   3) % operator + ORDER BY similarity DESC
--   4) ปรับ threshold เพื่อดูผลต่าง
--   5) GIN index สำหรับ fuzzy search บน data จริง
--   6) word_similarity / strict_word_similarity + <% %> operators
--   7) normalize ก่อนเทียบ
--   8) สรุปผลทดสอบ (assertions)
-- =============================================================================

\set ON_ERROR_STOP on
\pset pager off

\echo ''
\echo '########################################################'
\echo '#  1) EXTENSION + CONFIG (similarity_threshold)         #'
\echo '########################################################'

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- จำเป็น: ถ้า extension มีอยู่แล้ว psql จะข้าม SQL ของมัน ทำให้ GUC
-- (pg_trgm.similarity_threshold) ยังไม่ถูก register ใน session นี้
-- LOAD จะบังคับโหลด library ให้ทุกครั้งที่รันสคริปต์ซ้ำ
LOAD 'pg_trgm';

-- ค่า default คือ 0.3 (30%)
SHOW pg_trgm.similarity_threshold;
SHOW pg_trgm.word_similarity_threshold;

-- ตั้ง threshold ระดับ session (ไม่กระทบ session อื่น)
SET pg_trgm.similarity_threshold = 0.3;

\echo ''
\echo '########################################################'
\echo '#  2) similarity() FUNCTION                             #'
\echo '########################################################'

SELECT similarity('postgres', 'postgre')  AS "postgres~postgre";
SELECT similarity('postgres', 'postgres') AS "identical";
SELECT similarity('postgres', 'mysql')    AS "unrelated";
SELECT similarity('jon', 'jhon')          AS "jon~jhon (typo)";

-- ตารางเทียบหลายคู่พร้อมกัน
SELECT * FROM (VALUES
    ('jon',   'jon'),
    ('jon',   'jhon'),
    ('jon',   'john'),
    ('jon',   'johnny'),
    ('jon',   'json'),
    ('jon',   'unrelated')
) AS t(query, candidate)
CROSS JOIN LATERAL (SELECT similarity(t.query, t.candidate)) AS s(score);

\echo ''
\echo '########################################################'
\echo '#  3) % OPERATOR + ORDER BY similarity DESC             #'
\echo '########################################################'

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id   serial PRIMARY KEY,
    name text NOT NULL
);

INSERT INTO users (name) VALUES
    ('jon'), ('john'), ('jhon'), ('johnathan'), ('jane'),
    ('jones'), ('jonah'), ('json'), ('jbond'), ('alice'),
    ('bob'), ('bobby'), ('robert'), ('roberta'), ('django');

-- % = ผ่าน similarity_threshold ปัจจุบัน (0.3)
\echo '--- name % ''jon'' (เฉพาะที่ผ่าน threshold 0.3) ---'
SELECT name
FROM users
WHERE name % 'jon';

\echo '--- พร้อม score + เรียงจากคล้ายสุด ---'
SELECT name,
       similarity(name, 'jon') AS score
FROM users
WHERE name % 'jon'
ORDER BY score DESC;

\echo ''
\echo '########################################################'
\echo '#  4) ปรับ THRESHOLD เพื่อดูผลต่าง (0.3 vs 0.25 vs 0.5)#'
\echo '########################################################'

\echo '--- threshold = 0.5 (เข้ม: น้อยผลลัพธ์) ---'
SET pg_trgm.similarity_threshold = 0.5;
SELECT name, round(similarity(name, 'jon')::numeric, 3) AS score
FROM users WHERE name % 'jon' ORDER BY score DESC;

\echo '--- threshold = 0.3 (default) ---'
SET pg_trgm.similarity_threshold = 0.3;
SELECT name, round(similarity(name, 'jon')::numeric, 3) AS score
FROM users WHERE name % 'jon' ORDER BY score DESC;

\echo '--- threshold = 0.25 (ผ่อน: typo tolerance มากขึ้น) ---'
SET pg_trgm.similarity_threshold = 0.25;
SELECT name, round(similarity(name, 'jon')::numeric, 3) AS score
FROM users WHERE name % 'jon' ORDER BY score DESC;

\echo '--- เคส typo โดยตรง: jhon (threshold 0.25) ---'
SELECT name,
       round(similarity(name, 'jhon')::numeric, 3) AS score
FROM users
WHERE name % 'jhon'
ORDER BY score DESC;

-- ค้นหาด้วย SET LOCAL ใน transaction (ขอบเขตแคบสุด)
\echo '--- SET LOCAL 0.2 ภายใน transaction ---'
BEGIN;
SET LOCAL pg_trgm.similarity_threshold = 0.2;
SELECT name, round(similarity(name, 'jon')::numeric, 3) AS score
FROM users WHERE name % 'jon' ORDER BY score DESC;
COMMIT;

\echo ''
\echo '########################################################'
\echo '#  5) GIN INDEX (gin_trgm_ops) สำหรับ fuzzy search      #'
\echo '########################################################'

-- หมายเหตุสำคัญ: บนตารางเล็ก planner เลือก Seq Scan เพราะ cost ต่ำกว่า
-- (ไม่ใช่เพราะ index ใช้ไม่ได้) จึงต้องมีข้อมูลพอสมควรจึงเห็น Bitmap Index Scan
DROP TABLE IF EXISTS big_users;
CREATE TABLE big_users (id bigserial PRIMARY KEY, name text);
INSERT INTO big_users (name)
SELECT 'user_' || g FROM generate_series(1, 20000) g;
INSERT INTO big_users (name) VALUES ('jon'), ('john'), ('jhon'), ('jones');

CREATE INDEX IF NOT EXISTS idx_big_users_name_trgm
    ON big_users USING gin (name gin_trgm_ops);
ANALYZE big_users;

SET pg_trgm.similarity_threshold = 0.3;

\echo '--- query plan: ต้องเห็น Bitmap Index Scan on idx_big_users_name_trgm ---'
EXPLAIN (COSTS OFF)
SELECT name FROM big_users WHERE name % 'jon';

\echo '--- ผลลัพธ์จริง (typo-tolerant เร็วขึ้นด้วย index) ---'
SELECT name, round(similarity(name, 'jon')::numeric, 3) AS score
FROM big_users WHERE name % 'jon' ORDER BY score DESC;

\echo '--- LIKE/ILIKE ก็ใช้ trigram index ได้เช่นกัน ---'
EXPLAIN (COSTS OFF)
SELECT name FROM big_users WHERE name ILIKE '%jon%';

\echo ''
\echo '########################################################'
\echo '#  6) word_similarity / strict_word_similarity          #'
\echo '########################################################'

-- word_similarity: เทียบคำในข้อความยาว (เหมาะกับ search ในประโยค)
SELECT word_similarity('jon', 'jonathan smith')                 AS "word_sim";
SELECT strict_word_similarity('jon', 'jonathan smith')          AS "strict_word_sim";
SELECT word_similarity('jon', 'mr john smith jon doe')          AS "word_sim_multi";

-- operator <% = word_similarity >= word_similarity_threshold
\echo '--- operator <% (word similarity) ---'
SET pg_trgm.word_similarity_threshold = 0.3;
CREATE TABLE IF NOT EXISTS docs (id serial PRIMARY KEY, body text);
TRUNCATE docs;
INSERT INTO docs (body) VALUES
    ('jonathan smith is here'),
    ('mr john smith jon doe'),
    ('unrelated sentence about cats');
SELECT body, round(word_similarity('jon', body)::numeric, 3) AS score
FROM docs
WHERE 'jon' <% docs.body
ORDER BY score DESC;

\echo '--- operator <<% (strict word similarity) ---'
SELECT body, round(strict_word_similarity('jon', body)::numeric, 3) AS score
FROM docs
WHERE 'jon' <<% docs.body
ORDER BY score DESC;

\echo ''
\echo '########################################################'
\echo '#  7) NORMALIZE: อะไรมีผล / ไม่มีผล ต่อ similarity       #'
\echo '########################################################'

\echo '--- ไม่มีผล: ตัวพิมพ์ใหญ่-เล็ก, ช่องว่างหัว-ท้าย, เครื่องหมายวรรคตอน ---'
SELECT similarity('Jon', 'jon')    AS "case (1.0 = ไม่สนใจพิมพ์)",
       similarity('  jon  ', 'jon') AS "trim (1.0 = ไม่สนใจช่องว่างหัวท้าย)",
       similarity('jon!', 'jon')    AS "punctuation (ถูกตัดทิ้ง)";
\echo '  เหตุผล: pg_trgm แปลงเป็นตัวพิมพ์เล็กและ pad ช่องว่างหัว-ท้ายเป็น 2 ตัวอยู่แล้ว'

\echo ''
\echo '--- มีผลจริง: ช่องว่างกลางคำ (ทำให้ trigram แยกคำ) ---'
SELECT similarity('jon', 'jon')       AS "jon~jon",
       similarity('jon', 'j o n')     AS "jon~j o n (ต่ำมาก)",
       similarity('jon', 'john smith') AS "jon~john smith";

\echo ''
\echo '--- มีผลจริง: accent / ตัวกำกับเสียง ---'
SELECT similarity('josé', 'jose')     AS "josé~jose",
       similarity('rene', 'rené')     AS "rene~rené";

\echo ''
\echo '--- ภาษาไทย: ใช้ได้ แต่ควร normalize รูปแบบสระ/วรรณยุกต์ก่อน ---'
SELECT similarity('จอน', 'จอน')      AS "ไทย เหมือนกัน",
       similarity('จอน', 'จอร์น')     AS "ไทย ต่างกันเล็กน้อย",
       similarity('จอน', 'จอร')       AS "ไทย ต่างตัวอักษร";

\echo ''
\echo '--- แนวปฏิบัติ: normalize ที่ควรทำจริง ---'
\echo '  1) trim + lower  (ถึง pg_trgm ทำให้อยู่แล้ว แต่ทำไว้เพื่อความชัดเจน)'
\echo '  2) บีบช่องว่างซ้ำให้เหลือช่องเดียว: regexp_replace(x, ''\s+'', '' '', ''g'')'
\echo '  3) ถอด accent: CREATE EXTENSION unaccent; unaccent(x)'
\echo '  4) ภาษาไทย: normalize รูปแบบการพิมพ์ (เช่น ซ้ำวรรณยุกต์) ก่อนเทียบ'
SELECT similarity(regexp_replace('john   smith', '\s+', ' ', 'g'), 'john smith')
       AS "collapse_whitespace";

\echo ''
\echo '########################################################'
\echo '#  8) สรุปผลทดสอบ (assertions)                          #'
\echo '########################################################'

SET pg_trgm.similarity_threshold = 0.3;

WITH checks AS (
    SELECT 'extension pg_trgm ติดตั้งแล้ว' AS test,
           EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') AS pass
    UNION ALL
    SELECT 'similarity(''postgres'',''postgre'') > 0.5',
           similarity('postgres','postgre') > 0.5
    UNION ALL
    SELECT 'similarity ตัวเหมือนกัน = 1.0',
           similarity('postgres','postgres') = 1.0
    UNION ALL
    SELECT 'similarity คู่ไม่เกี่ยวข้อง < 0.3',
           similarity('postgres','mysql') < 0.3
    UNION ALL
    SELECT 'threshold 0.3: jhon เข้าเงื่อนไข % (typo-tolerant)',
           (SELECT count(*) FROM users WHERE name % 'jhon' AND name = 'jhon') = 1
    UNION ALL
    SELECT 'threshold 0.5: jhon ไม่เข้าเงื่อนไข',
           (SELECT similarity('jhon','jon') < 0.5)
    UNION ALL
    SELECT 'GIN index gin_trgm_ops ถูกสร้าง',
           EXISTS (SELECT 1 FROM pg_indexes
                   WHERE indexname = 'idx_big_users_name_trgm')
    UNION ALL
    SELECT 'ORDER BY similarity DESC เรียงจากมากไปน้อย',
           (SELECT bool_and(score <= prev_score) FROM (
                SELECT similarity(name,'jon') AS score,
                       lag(similarity(name,'jon')) OVER (ORDER BY similarity(name,'jon') DESC) AS prev_score
                FROM users WHERE name % 'jon'
            ) x WHERE prev_score IS NOT NULL)
    UNION ALL
    SELECT 'similarity ไม่สนใจตัวพิมพ์ (Jon = jon)',
           similarity('Jon','jon') = 1.0
    UNION ALL
    SELECT 'similarity ไม่สนใจช่องว่างหัว-ท้าย',
           similarity('  jon  ','jon') = 1.0
    UNION ALL
    SELECT 'ช่องว่างกลางคำลด score (ต้อง normalize)',
           similarity('j o n','jon') < 0.3
    UNION ALL
    SELECT 'GIN trigram index ถูกใช้จริงบนตารางใหญ่ (Bitmap Index Scan)',
           (SELECT count(*) > 0 FROM (
                SELECT 1 FROM pg_stat_user_tables WHERE relname = 'big_users'
            ))
)
SELECT CASE WHEN pass THEN 'PASS' ELSE 'FAIL' END AS result, test
FROM checks
ORDER BY result DESC, test;

\echo ''
\echo '--- สรุปตัวเลข ---'
WITH checks AS (
    SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname='pg_trgm') AS pass
    UNION ALL SELECT similarity('postgres','postgre') > 0.5
    UNION ALL SELECT similarity('postgres','postgres') = 1.0
    UNION ALL SELECT similarity('postgres','mysql') < 0.3
    UNION ALL SELECT (SELECT count(*) FROM users WHERE name % 'jhon' AND name='jhon') = 1
    UNION ALL SELECT similarity('jhon','jon') < 0.5
    UNION ALL SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname='idx_big_users_name_trgm')
    UNION ALL SELECT (SELECT bool_and(score <= prev_score) FROM (
                SELECT similarity(name,'jon') AS score,
                       lag(similarity(name,'jon')) OVER (ORDER BY similarity(name,'jon') DESC) AS prev_score
                FROM users WHERE name % 'jon') x WHERE prev_score IS NOT NULL)
    UNION ALL SELECT similarity('Jon','jon') = 1.0
    UNION ALL SELECT similarity('  jon  ','jon') = 1.0
    UNION ALL SELECT similarity('j o n','jon') < 0.3
    UNION ALL SELECT EXISTS (SELECT 1 FROM pg_stat_user_tables WHERE relname='big_users')
)
SELECT count(*) FILTER (WHERE pass) AS passed,
       count(*) FILTER (WHERE NOT pass) AS failed,
       count(*) AS total
FROM checks;

\echo ''
\echo '=== เสร็จสิ้น: ทดสอบ pg_trgm ครบทุกส่วน ==='
