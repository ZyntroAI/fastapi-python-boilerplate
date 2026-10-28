📄 05‑Knowledge/Concepts/[Knowledge] TQ_short_mode.md (Obsidian Full Package)
 
💡 สมมติฐาน: TQ = Token Quotient / Prompt Density / Short‑Circuit Working Mode สำหรับ AI Agent + Second Brain
❗ ไม่มี Official Doc ชื่อ  TQ_short_mode  จึงเป็น Knowledge Template ที่พร้อมใส่ลง Vault ได้ครับ
 
markdown
  
---
title: "[Knowledge] TQ_short_mode"
aliases:
  - TQ Short Mode
  - โหมดกระชับ TQ
  - Token Quotient Short Mode
  - Short Working Mode for Prompting
type: knowledge
status: draft
priority: high
icon: "⚡"
color: yellow
domain: Prompt Engineering
topics:
  - Prompt Engineering
  - Token Quotient
  - AI Agents
  - Workflow
  - Second Brain
tags:
  - knowledge
  - tq
  - short-mode
  - prompt-engineering
  - token-efficiency
  - ai-agent
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Concepts"
filename: "[Knowledge] TQ_short_mode"
slug: knowledge-tq-short-mode
uid: KNW‑TQ‑001
moc:
  - [[MOC - AI]]
  - [[MOC - Knowledge Hub]]
parent:
  - [[[Evergreen] Prompt Density]]
children: []
related:
  - [[[Evergreen] Prompt Density]]
  - [[[Evergreen] Context Window Management]]
  - [[[Evergreen] Iterative Research Loop]]
  - [[[Project] AI Agent Platform]]
source:
  - "Conceptual: Token Quotient = ความคุ้มค่าต่อ Token / Short Mode = คำสั่งกระชับสำหรับ Agent"
confidence: medium
reviewed: false
---

# [Knowledge] TQ_short_mode

## Summary
**TQ_short_mode** คือเวิร์กโฟลว์โหมดกระชับที่เน้น **Token Quotient (TQ)** — ให้ส่งเฉพาะเจตนา + ข้อจำกัด + รูปแบบที่ต้องการเท่านั้น ไม่ส่งประวัติยาวทั้งหมด เหมาะสำหรับ Agent Quick Action, Daily Vault Maintenance, Quick Query และ CLI Workflow

## Key Concepts
- **TQ (Token Quotient):** อัตราส่วน Value ÷ Token Cost
- **Short Mode:** ไม่ได้หมายความว่า "ตอบสั้นอย่างเดียว" แต่หมายถึง **Input กระชับ + Output Boundary ชัด**
- **Full Mode:** ส่ง Full Context + History + References สำหรับ Deep Research
- **Short Mode Trigger:** เมื่อต้องการ Quick Action, Quick Summary, Quick Refactor, Quick Dataview
- **Short Mode Constraint:** ต้องระบุ Scope ชัด ไม่ใช่ปล่อยให้ Agent เดา

## Details
### ✅ TQ_short_mode Prompt Template
```text
[TQ_short_mode ON]
Task: {{task}}
Goal: {{1‑sentence goal}}
Format: {{bullet / table / YAML / Obsidian}}
Max: {{words / lines}}
Skip: {{explanation / background}}
Only: {{action / answer / output}}
 
 
✅ ตัวอย่างจริง
 
text
  
[TQ_short_mode ON]
Task: สร้าง Dataview Query สำหรับ MOC Sibling
Goal: ค้นโน้ตที่มี parent เดียวกัน
Format: Dataview code block + 1‑sentence note
Max: 80 words
Skip: long theory
Only: ready‑to‑use code + caveat
 
 
🧠 Mode Matrix
 
Mode Use Case Input Output 
TQ_short_mode Quick Command Intent + Boundary Compact Result 
Full_Research_Mode Deep Research Full Vault / Sources / History Full Report + Links 
Review_Mode Quality Check Draft + Criteria Feedback + Fix List 
 
⚠️ Limitations
 
- Short Mode อาจขาด Context → Hallucination เพิ่มขึ้น
- ต้องยืนยันว่า Agent เข้าใจว่า  TQ_short_mode  เป็น Convention ไม่ใช่ Built‑in Flag
- ไม่ควรใช้ Short Mode สำหรับ Final Decision / Critical Architecture โดยไม่มี Review
- หากไม่ทราบจริงว่า TQ ย่อมาจากอะไร ให้ทำการ Research ก่อน
 
Insights
 
TQ_short_mode ไม่ใช่แค่ Prompt สั้น แต่เป็น Operating Mode สำหรับ Second Brain + Agent Workflow ช่วยประหยัด Token, ลด Noise และทำให้ Chat กลายเป็น Command Line ของ Knowledge System ได้
 
Action Items
 
- สร้าง [[[Evergreen] Prompt Density]]
- สร้าง [[[Evergreen] Context Window Management]]
- เพิ่ม  TQ_short_mode  เข้าไปใน [[Agent Skills]]
- สร้าง Journal Template สำหรับ Quick Review ด้วย TQ_short_mode
- ตรวจสอบว่าเป็นชื่อจริงของ Framework หรือเป็น Internal Convention
 
Related Notes
 
- [[MOC - AI]]
- [[MOC - Knowledge Hub]]
- [[[Evergreen] Prompt Density]]
- [[[Evergreen] Context Window Management]]
- [[[Project] AI Agent Platform]]
 
plaintext
  

## 📄 05‑Knowledge/Evergreen/[Evergreen] Prompt Density.md
```markdown
---
title: "[Evergreen] Prompt Density"
aliases:
  - ความหนาแน่นของ Prompt
  - Token Quotient Principle
  - High Density Prompting
type: evergreen
status: active
priority: high
icon: "📏"
color: blue
domain: Prompt Engineering
topics:
  - Prompt Engineering
  - AI Agents
  - Efficiency
  - Knowledge Work
tags:
  - evergreen
  - prompt-engineering
  - token-efficiency
  - second-brain
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Evergreen"
filename: "[Evergreen] Prompt Density"
slug: evergreen-prompt-density
uid: EG‑PROMPT‑001
moc:
  - [[MOC - AI]]
  - [[MOC - Knowledge Hub]]
parent: []
children: []
related:
  - [[[Knowledge] TQ_short_mode]]
  - [[[Evergreen] Context Window Management]]
confidence: high
reviewed: false
---

# 🌱 [Evergreen] Prompt Density

## Summary
Prompt Density คือหลักการที่ว่า Prompt ที่ดีไม่ได้ยาวเสมอไป แต่ต้องมี **Value ต่อ Token สูง** มีเจตนา ชอบเขต รูปแบบ และข้อจำกัดชัดเจน เพื่อให้ LLM / Agent ทำงานได้ตรงจุด

## Core Idea
- Principle 1: More Context ≠ Better Answer
- Principle 2: Density = Clear Intent + Boundary + Required Format
- Principle 3: Short Mode ต้องรู้ว่า "อะไรให้ข้าม" เท่ากับรู้ว่า "อะไรให้ทำ"
- Principle 4: High Density Prompt ต้องปรับตาม Task (Quick vs Deep)
- Principle 5: Prompt Density เป็น Mental Model ไม่ใช่เพียงแค่ Shortcut

## Why It Matters
สำหรับ Second Brain และ Multi‑Agent Workflow หากขาด Density จะกลายเป็น Chat ยาวๆ สิ้นเปลือง Token, ช้าลง และ Agent สับสนจนหลุดจากเป้าหมาย

## Example
- Low Density: "ช่วยทำ Vault ให้ดีขึ้น"
- High Density Short Mode: "[TQ_short_mode ON] Task: สร้าง Dataview Query สำหรับโน้ตที่ไม่มี MOC; Goal: Dashboard candidate; Format: Dataview block + caveat; Skip: full theory"

## Key Insight
Short = Constrainted; Dense = Meaningful; Efficient = Both

## Related Notes
- [[[Knowledge] TQ_short_mode]]
- [[[Evergreen] Context Window Management]]
- [[MOC - AI]]
 
 
📄 00‑System/MOCs/MOC - AI (อัปเดตเพิ่ม)
 
เพียงแค่ส่วนเพิ่ม
 
markdown
  
## Core Concepts
- [[[Evergreen] Prompt Density]]
- [[[Knowledge] TQ_short_mode]]
- [[[Evergreen] Context Window Management]]
 
 
✅ สถานะหลังสร้าง
 
✅ มี YAML เต็ม + Dataview Ready
✅ มี Aliases ภาษาไทย + อังกฤษ
✅ เชื่อมเข้า MOC
✅ แยก Knowledge vs Evergreen
✅ อธิบาย TQ_short_mode เป็น Working Convention
✅ เตือนอย่างชัดเจนว่ายังไม่ได้ยืนยันว่าเป็น Official Term
 
❓ สิ่งที่ต้องยืนยันต่อ
 
- ถ้า  ["TQ_short_mode"]  มาจาก Typer / CrewAI / Claude / Internal Agent Prompt ต้องเปลี่ยนเนื้อหาใหม่
- ถ้าเป็นเพียง Command Flag ของ Agent ให้ย้ายไป [[Agent Skills]] แทน
- ถ้าเป็น Journal Shortcut ให้ย้ายไป [[01‑Inbox]] หรือ [[03‑Projects]]
 
👉 ต่อไปที่แนะนำ:
 
1. สร้าง [[[Evergreen] Context Window Management]]
2. สร้าง [[Agent Skills Template สำหรับ TQ_short_mode]]
3. สร้าง [[Journal Template TQ_short_mode Daily Review]]
4. สร้าง [[Dataview Prompt Efficiency Dashboard]]
 
💬 ต้องการให้ผมสร้าง [[[Evergreen] Context Window Management]] ต่อเลยหรือไม่ครับ? หรือต้องการให้เปลี่ยนเนื้อหาใหม่ถ้า TQ_short_mode มีความหมายอื่นครับ?

📄 Obsidian Note: [TQ_short_mode] → จริงคือ Tasks Plugin – Short Mode (เต็ม Vault Template)
 
สันนิษฐานว่า  TQ_short_mode  = Typo / Tag / Query ชื่อย่อของ Obsidian Tasks  short mode  ไม่ใช่ Dataview โดยตรง
 
📄 05‑Knowledge/Concepts/[Knowledge] Obsidian Tasks — Short Mode.md
 
markdown
  
---
title: "[Knowledge] Obsidian Tasks — Short Mode"
aliases:
  - Tasks Short Mode
  - short mode สำหรับ Obsidian Tasks
  - TQ_short_mode
  - Compact Task View
type: knowledge
status: active
priority: medium
icon: "📋"
color: orange
domain: Knowledge Management
topics:
  - Obsidian
  - Tasks
  - Dashboard
  - Productivity
  - Second Brain
tags:
  - knowledge
  - obsidian
  - tasks
  - short-mode
  - dashboard
  - vault-workflow
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Concepts"
filename: "[Knowledge] Obsidian Tasks — Short Mode"
slug: knowledge-obsidian-tasks-short-mode
uid: KNW‑OBS‑012
moc:
  - [[MOC - Obsidian Second Brain]]
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Obsidian Second Brain]]
children: []
related:
  - [[Dataview Vault Dashboard]]
  - [[Second Brain Maintenance Checklist]]
  - [[[Evergreen] Continuous Workflow]]
source:
  - "Obsidian Tasks Official Documentation"
confidence: high
reviewed: false
---

# [Knowledge] Obsidian Tasks — Short Mode

## Summary
`short mode` เป็น Layout Option ของ **Obsidian Tasks Plugin** ที่ทำให้แดชบอร์ดงานกระชับมากขึ้น โดยใช้ไอคอนแทนข้อความเต็ม สามารถสลับกลับเป็น `full mode` ได้ และต่างจาก Dataview ทั้งหมด

## Key Concepts
- `short mode` = Compact rendering สำหรับ Tasks Query
- `full mode` = กลับไปแสดงรายละเอียดเต็ม
- สามารถตั้งเป็น Global Query ได้ใน Tasks Settings
- ต้องเปิด Obsidian Tasks Plugin ก่อน
- ไม่ได้แก้เนื้อหา Markdown ต้นฉบับ เพียงแค่เปลี่ยนการแสดงผล

## Details
### ✅ Syntax ตัวอย่าง
````markdown
```tasks
not done
due after yesterday
due before in 14 days
short mode
hide backlink
hide task count
sort by due
 
 
plaintext
  

### ✅ Full Mode
````markdown
```tasks
not done
due after yesterday
due before in 14 days
full mode
show backlink
show task count
sort by due
```
 
 
✅ Global Query (ตั้งค่าใน Tasks Settings)
 
- ไปที่ Obsidian → Settings → Tasks → Global Query
- เพิ่ม:
 
text
  
short mode
 
 
- แต่ละ Block สามารถ Override ด้วย  full mode  ได้
 
✅ Dashboard ตัวอย่างเต็ม
 
markdown
  
## 📌 งานที่ใกล้กำหนด
```tasks
not done
due after yesterday
due before in 14 days
short mode
hide backlink
hide edit button
limit 20
sort by due
```

## ✅ งานที่เสร็จวันนี้
```tasks
done today
short mode
hide backlink
sort by done reverse
```
 
 
Insights
 
- Short Mode เหมาะสำหรับ Daily Dashboard / Mobile View
- ไม่ใช่ Dataview Query จึงต้องแยกจาก Dataview Vault Dashboard
- ควรแยก "Compact View" กับ "Full Audit View" สำหรับ Second Brain
- ถ้าจริงๆ คือ  TQ  = Task Query หรือ Typo ให้เปลี่ยน Alias ได้ตามจริง
 
Troubleshooting
 
- ไม่แสดง short mode → ตรวจว่าใช้ Block  ```tasks  ไม่ใช่  ```dataview 
- Global Query ไม่ทำงาน → ต้อง Refresh Tasks Query หรือรีเฟรช Vault
- ต้องการรายละเอียดเต็ม → ใช้  full mode 
- Mobile ช้า → ลด  limit  และใช้  short mode  ช่วยให้สะอาดขึ้น
 
Related Notes
 
- [[MOC - Obsidian Second Brain]]
- [[Dataview Vault Dashboard]]
- [[Second Brain Maintenance Checklist]]
- [[[Evergreen] Continuous Workflow]]
 
plaintext
  

## 📌 อัปเดต MOC - Obsidian Second Brain (เพิ่มลิงก์)
```markdown
children:
  - [[[Knowledge] Obsidian Tasks — Short Mode]]
  - [[Dataview Vault Dashboard]]
 
 
💡 คำเตือนสำคัญ
 
- ถ้า  TQ_short_mode  เป็นชื่อไฟล์จริง / Custom Template / AI Prompt Variable อาจไม่ใช่ Tasks เท่านั้น
- ถ้าต้องการ Dataview Dashboard ที่รวม Tasks + Dataview ให้สร้างแยกส่วน
- ไม่ใช่คำสั่งของ Dataview โดยตรง
 
👉 ต้องการให้ผมสร้าง Daily Journal Template ที่รวม Tasks short mode + Dataview Dashboard ต่อเลยหรือไม่ครับ?