Title: AI Gateway Architecture Review — Resilience & Cost Control
Kicker: Weakness Analysis and Improved Architecture
Theme: AI Infrastructure / API Gateway
Genre: project-status

```figexec
จุดอ่อนที่แพงที่สุดคือ resilience (R1, R2 — 16/16) แต่ถูกที่สุดในการแก้ด้วย per-provider timeout + circuit breaker แบบ half-open กลุ่ม security (S1, S2) อันตรายเชิงธุรกิจสุดเพราะข้อมูลรั่ว/compliance และแก้ทีหลังแพงที่สุด กลุ่ม cost มี 4 จุดติด Top 10 สะท้อนภารกิจหลักของระบบ แนะนำ rollout 6 ระยะ เริ่มจาก resilience ก่อน แล้วปิด security ก่อนข้อมูล sensitive เข้าระบบจำนวนมาก
```

```figkpi
[{"value": "32", "unit": "จุด", "label": "จุดอ่อนเฉพาะที่พบ", "delta": "6 มิติ", "dir": "neutral"},{"value": "10", "unit": "จุด", "label": "วิกฤต (≥12)", "delta": "31% ของทั้งหมด", "dir": "up"},{"value": "16", "unit": "/16", "label": "คะแนนสูงสุด R1·R2", "delta": "timeout + breaker", "dir": "up"},{"value": "6", "unit": "ระยะ", "label": "Rollout ที่แนะนำ", "delta": "8–16 สัปดาห์", "dir": "neutral"}]
```

---

## ระบบ AI Gateway มีจุดอ่อน 32 จุดเฉพาะ โดย 10 จุดอยู่ในระดับวิกฤตที่ต้องแก้ก่อน deployment

สถาปัตยกรรม baseline (CDN → API Gateway → Redis Cache → Fallback Router → AI Providers) ถูกออกแบบมาเพื่อความยืดหยุ่นและการควบคุมต้นทุนผ่านชั้น cache, fallback หลายระดับ, context reuse และ token budget อย่างไรก็ตาม เมื่อประเมินด้วยเกณฑ์ **Severity (1–4) × Likelihood (1–4) = Risk (สูงสุด 16)** พบว่าการกระจายความเสี่ยงไม่สม่ำเสมอ — กลุ่ม resilience ครอง 2 อันดับสูงสุด ส่วนกลุ่ม security แม้เกิดน้อยกว่าแต่มีความเสียหายสูงสุดหากเกิดจริง

```figchart
{"type":"bar","title":"จุดอ่อนจำแนกตามระดับความเสี่ยง","unit":"จุด","data":[{"label":"วิกฤต (12–16)","value":10},{"label":"สูง (8–11)","value":12},{"label":"กลาง (5–7)","value":8},{"label":"ต่ำ (≤4)","value":2}]}
```

**การกระจาย** — จุดอ่อนเกือบครึ่ง (22 จาก 32) อยู่ในกลุ่มวิกฤตและสูง หมายความว่าระบบปัจจุบันมีความเสี่ยงเชิงโครงสร้างที่ต้องจัดการเชิงรุก ไม่ใช่แค่ปรับจูนปลีกย่อย

## resilience และ security คือจุดที่ระบบเปราะที่สุด — คะแนนสูงสุด 16/16 สองจุด

จุดอ่อน R1 (circuit breaker ไม่มี half-open) และ R2 (ไม่มี per-provider timeout) ได้คะแนน 16/16 สูงสุด เพราะทั้งรุนแรงและเกิดบ่อย — provider ล้ม/ช้าเป็นเหตุการณ์ปกติของการเรียก AI ภายนอก ในทางกลับกัน กลุ่ม security (S1 ไม่มี data classification, S2 cache ไม่มี tenant isolation) ได้ 12/12 เพราะความเสียหายจากข้อมูลรั่วหรือ compliance สูงมากแม้โอกาสเกิดจะน้อยกว่า

```figchart
{"type":"bar","title":"จุดอ่อนวิกฤต+สูง จำแนกรายมิติ","unit":"จุด","data":[{"label":"Security (S)","value":5},{"label":"Structural (ST)","value":5},{"label":"Resilience (R)","value":4},{"label":"Cost (C)","value":3},{"label":"Observability (O)","value":3},{"label":"Cost ลึก (CC)","value":2}]}
```

**จุดที่ต้องให้ความสำคัญสูง** — Security และ Structural มีจุดอ่อนระดับวิกฤต+สูงครบทุกจุด (5/5 ทั้งคู่) คือมิติที่ไม่มีจุดอ่อน "เบาๆ" เลย ส่วน Resilience มี 4/4 — ระบบปัจจุบันเปราะในทุกจุดที่เกี่ยวข้องกับความอยู่รอดและข้อมูล จึงควรเริ่ม rollout จากสองมิตินี้

## ตาราง Risk Register ครบทั้ง 6 มิติ พร้อมลิงก์ mitigation

| ID | จุดอ่อน | ผลกระทบ | S | L | Risk | Mitigation |
|----|---------|---------|:-:|:-:|:--:|------|
| **R2** | ไม่มี timeout budget ต่อ provider — ตอบ "down" แต่ไม่ตอบ "slow" | Primary ช้าแต่ไม่ตาย กิน budget ทั้ง request → fail ทั้งที่ secondary พร้อม | 4 | 4 | 🔴 **16** | M2 |
| **R1** | Circuit breaker ไม่มี half-open / health probe | ฟื้นตัวแล้วยัง fail หรือ flapping | 4 | 4 | 🔴 **16** | M1 |
| **S1** | ไม่มี data classification ต้นทาง | ข้อมูลลับ/PII ไหลไป cache+provider ไม่มีทางบังคับ policy | 4 | 3 | 🔴 **12** | M12 |
| **S2** | Cache ไม่มี tenant isolation / encryption | ข้อมูล tenant A รั่วถึง tenant B | 4 | 3 | 🔴 **12** | M13 |
| **ST5** | Gateway เป็น SPOF (deploy เดียว) | Gateway ล้ม = ทั้งระบบ offline | 4 | 3 | 🔴 **12** | M19 |
| **ST1** | Context Compiler เป็น SPOF | Compiler ล้ม = pipeline ตายทั้งเส้น | 4 | 3 | 🔴 **12** | M9 |
| **C1** | Token budget แค่ request-scoped ไม่ใช่ rolling window | Burst ข้าม request/tenant พังงบระบบ | 4 | 3 | 🔴 **12** | M6 |
| **R3** | Cache miss พร้อมกัน = thundering herd | จ่ายซ้ำซ้อน + ทุบ upstream ตอน cache หมดอายุ | 3 | 4 | 🟠 **12** | M3+M5 |
| **C2** | Cache เป็น exact-match เท่านั้น | Hit rate ต่ำ → prompt ใกล้กันแต่ต้องจ่ายเต็ม | 3 | 4 | 🟠 **12** | M5 |
| **CC3** | ไม่มี model tiering ตาม task complexity | งานง่ายจ่ายราคา model ใหญ่ | 3 | 4 | 🟠 **12** | M21 |
| **O4** | Cost ไม่ real-time ต่อ call | งบพุ่งแล้วค่อยรู้ ขัดนโยบายประหยัด | 3 | 3 | 🟠 **9** | M16 |
| **O1** | ไม่มี distributed tracing ตลอด lifecycle | ไม่รู้ request ตาย/ช้าที่ชั้นไหน → แก้เดาสุ่ม | 3 | 3 | 🟠 **9** | M15 |
| **ST2** | Redis เป็น SPOF, fail-open/closed ไม่ชัด | พฤติกรรมไม่ deterministic ใต้ cache outage | 3 | 3 | 🟠 **9** | M8 |
| **ST3** | ไม่มี idempotency/dedup ฝั่งรับ | Client retry → เรียก provider ซ้ำ → จ่ายซ้ำ | 3 | 3 | 🟠 **9** | M10 |
| **R4** | ไม่มี queue / admission control | ล้มแบบ hard ใต้ spike แทน graceful | 3 | 3 | 🟠 **9** | M4 |
| **S4** | ไม่มี audit trail ของ routing | สืบไม่ได้เมื่อ data leak / compliance | 3 | 3 | 🟠 **9** | M14 |
| **C4** | ไม่มี cost attribution ต่อ tenant/route | จับไม่ได้ว่าใครกินงบ, ตั้ง alert/cap ไม่ได้ | 3 | 3 | 🟠 **9** | M16 |
| **ST4** | ไม่มี provider capability registry | Router ตัดสินใจแบบ static ไม่รู้ความสามารถจริง | 3 | 3 | 🟠 **9** | M11 |
| **S3** | ไม่มี redaction ก่อนส่ง provider | ข้อมูลส่วนตัวหลุดไป training ของผู้ให้บริการ | 4 | 2 | 🟠 **8** | M12 |
| **S5** | ไม่มี provider policy (region/retention) | Request ต้องอยู่ region ถูกส่งออกนอก | 4 | 2 | 🟠 **8** | M11 |
| **O2** | Error taxonomy ยังไม่แยก | Alert ท่วม, escalate ผิดลำดับ | 2 | 4 | 🟠 **8** | M15 |
| **CC2** | ไม่ downgrade output ตามความต้องการ | จ่าย output token เกิน | 2 | 4 | 🟠 **8** | M21 |
| **O5** | ไม่มี canary/progressive rollout | อัปเกรด model → regression ทั้งระบบ ถอยยาก | 3 | 2 | 🟡 **6** | M17 |
| **O6** | Self-Healing เชิงรับ ไม่มี preventive probe | รู้ว่าระบบป่วยก็เมื่อ user เริ่มเจ็บแล้ว | 3 | 2 | 🟡 **6** | M18 |
| **ST6** | ไม่มี runtime config / feature flag | เปลี่ยน routing policy ต้อง redeploy | 2 | 3 | 🟡 **6** | M20 |
| **C5** | Fallback ไป degraded ไร้ policy ระดับ request | คุณภาพลดเงียบ ไม่รู้ trade-off | 2 | 3 | 🟡 **6** | M7 |
| **C6** | Context reuse แบบต่อตรง ไม่ prune | จ่าย input token เกินจำเป็น | 2 | 3 | 🟡 **6** | M9 |
| **C3** | Cache ไม่ versioning ตาม model/prompt | เปลี่ยน model → cache เก่า (stale) | 2 | 3 | 🟡 **6** | M5 |
| **CC1** | ไม่มี forecast งบ | งบ burst ล่วงหน้าไม่รู้ | 2 | 3 | 🟡 **6** | M16 |
| **CC4** | Cache size/eviction ไม่สัมพันธ์ต้นทุน | Hit rate ต่ำ หรือเปลือง storage | 2 | 3 | 🟡 **6** | M5 |
| **O3** | ไม่มี golden signals / SLO ต่อ route | ไม่รู้ว่า "ปกติ" คืออะไร จนกว่าจะพัง | 2 | 2 | 🟢 **4** | M15 |
| **CC5** | ไม่ batch request ที่ delay ได้ | เสียโอกาสรวม request ประหยัด | 2 | 2 | 🟢 **4** | M4 |

> **หมายเหตุ:** R5 และ R6 (Context Compiler SPOF / Redis SPOF) ทับซ้อนกับ ST1 และ ST2 ซึ่งเป็นจุดเดียวกันมองข้ามคนละมิติ — จึงนับรวมเป็นจุดอ่อนเฉพาะ 32 จุดจาก 34 รายการ

## จุดที่อันตรายที่สุดคือรอยต่อข้ามมิติ — cache รั่ว + SPOF และข้อมูลไหลไป provider ผิดนโยบาย

จุดอ่อนที่ "ร่วมกัน" สร้างความเสี่ยงสูงสุดคือจุดที่อยู่รอยต่อของหลายมิติ ซึ่งตารางแยกมิติอาจมองไม่เห็น:

1. **S2 + ST2 (cache leak + SPOF)** — cache ที่ทั้งรั่วระหว่าง tenant และเป็นจุดพังจุดเดียว = เสี่ยงทั้งข้อมูลและ availability พร้อมกัน
2. **S1 + S3 + S5 (ข้อมูลไหลไป provider ผิดที่/ผิดนโยบาย)** — รวมกันเป็น compliance risk ที่แพงที่สุดในการแก้ทีหลัง
3. **O4 + CC (cost ไม่ real-time)** — ขัดกับหัวใจนโยบาย "หลีกเลี่ยงค่า AI" ของระบบโดยตรง
4. **ST1 + ST5 (SPOF สองจุด)** — compiler + gateway ล้มพร้อมกัน = ทั้งระบบ offline

## สถาปัตยกรรมที่ปรับปรุงปิดจุดอ่อนด้วย 21 กลไก ครอบคลุมทุกมิติ

```
Client → [Edge: auth, rate-limit, tenant quota, request-id]
              ↓
        API Gateway (multi-instance / active-active)
              ↓
┌──────────── Routing & Resilience Core ────────────┐
│ 1. Data Classification (tag payload: pii/secret)   │
│ 2. Semantic/Normalized Cache → Exact Cache         │
│    (single-flight + versioned key + SWR)           │
│ 3. Fallback Router (async): per-provider timeout   │
│    + retry(jitter) + cost cap + capability lookup  │
│ 4. Circuit Breaker per provider: closed→open→      │
│    half-open (health probe)                        │
│ 5. Bounded queue + admission control (load shed)   │
│ 6. Idempotency / dedup (request id)                │
└────────────────────────────────────────────────────┘
        ↓
  Cost Governance: rolling token budget (global+tenant),
                   cost-aware routing, budget short-circuit,
                   cost attribution ทุก call + forecast
        ↓
  Context Layer: compiler แยกบริการ (scale แยกได้),
                 prune policy, degrade เป็น raw context
        ↓
  Security: tenant-isolated encrypted cache,
            redaction ก่อนออกขอบเขต, immutable audit log
        ↓
  AI Providers: primary / secondary / degraded
                (เลือกผ่าน capability registry + canary rollout)
        ↓
  Ops: full-lifecycle tracing, error taxonomy, SLO ต่อ route,
       active health probe, cost dashboard + alert
```

กลไก M1–M21 แก้จุดอ่อนแบบ one-to-many: M5 (semantic cache) ปิด C2/C3/CC4 พร้อมกัน, M12 (classification+redaction) ปิด S1/S3, M15 (tracing+taxonomy+SLO) ปิด O1/O2/O3 และ M16 (cost attribution) ปิด O4/C4/CC1 — กลไกหลักไม่กี่ตัวครอบคลุมจุดอ่อนส่วนใหญ่ จึงควรทำเป็นแพ็กเกจเดียวกัน

## rollout 6 ระยะ เริ่มจากจุดที่ "แพงและถูก" (resilience) แล้วปิด security ก่อนข้อมูล sensitive เข้าระบบ

```figchart
{"type":"timeline","title":"Rollout 6 ระยะ — จุดอ่อนที่ปิดได้","unit":"สัปดาห์","data":[{"label":"P1 resilience","value":2},{"label":"P2 budget+policy","value":2},{"label":"P3 semantic+router","value":3},{"label":"P4 security","value":3},{"label":"P5 observability","value":4},{"label":"P6 scale","value":4}]}
```

| ระยะ | เนื้อหา | จุดอ่อนที่ปิด | ระยะเวลา |
|------|--------|-------------|:--:|
| **P1** | Timeout + circuit breaker + single-flight | R1, R2, R3 | 1–2 สัปดาห์ |
| **P2** | Rolling budget + cache policy + health probe | C1, ST2, O6 | 1–2 สัปดาห์ |
| **P3** | Semantic cache + cost-aware router + degrade policy | C2, C3, C5, C6, CC4 | 2–3 สัปดาห์ |
| **P4** | Data classification + encrypted tenant cache + audit log | S1–S4 | 2–3 สัปดาห์ |
| **P5** | Tracing + SLO + canary + cost dashboard real-time | O1–O5, C4 | 2–4 สัปดาห์ |
| **P6** | Compiler แยก service + multi-instance + registry + tiering | ST1, ST4, ST5, CC2, CC3 | 3–4 สัปดาห์ |

**ข้อเสนอแนะเชิงปฏิบัติ:** เริ่ม P1 (resilience) ก่อนเพราะปิดความเสี่ยงสูงสุดด้วยงานเล็กที่สุด จากนั้นเลื่อน P4 (security) ให้เร็วที่สุดเท่าที่ทำได้ — ควรเริ่ม data classification ก่อนข้อมูล sensitive จำนวนมากเข้าสู่ระบบ เนื่องจากเป็นจุดที่แก้ทีหลังแพงที่สุด

---

## Sources

รายงานนี้ตั้งอยู่บนหลักสถาปัตยกรรมที่ยอมรับโดยทั่วไปสำหรับระบบ resilient gateway และ cost governance:

- Circuit breaker pattern (closed → open → half-open) — มาตรฐานความยืดหยุ่นของ microservices
- Retry with exponential backoff + jitter — หลักการ network resilience
- Single-flight / request coalescing — ลด load ซ้ำซ้อนบน cache miss
- Semantic / normalized caching พร้อม versioned key + stale-while-revalidate — เพิ่ม hit rate ลดค่า AI
- Rolling token budget (global + per-tenant) + cost-aware routing — การควบคุมงบ AI
- Data classification + tenant isolation + encryption-at-rest — แนวปฏิบัติความปลอดภัยข้อมูล
- Distributed tracing + SLO/error budget + canary rollout — observability และ deploy ปลอดภัย

> **ข้อจำกัด:** เอกสาร baseline ที่ใช้อ้างอิงถูกบันทึกไว้ในบริบทก่อนหน้า ตัวเลข severity/likelihood เป็น structured estimate เพื่อจัดลำดับความสำคัญ ควรปรับเทียบกับข้อมูลจริง (metrics, SLO, ค่าใช้จ่าย) ก่อนลงมือในแต่ละ phase
