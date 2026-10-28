title: "[MOC] Obsidian Core"
aliases:
 
- "MOC — Obsidian Core"
- "Obsidian Core"
- "แผนที่ความรู้แกนกลาง Obsidian"
slug: moc-obsidian-core
icon: 🗺️
color: violet
status: active
priority: essential
type: moc
category: knowledge
domain:
- Obsidian
- Knowledge Management
topics:
- MOC
- Core Concepts
- Obsidian Basics
tags:
- "#topic/moc"
- "#topic/obsidian"
- "#topic/core"
- "#type/moc"
- "#status/active"
language: th
created: 2026-10-27
updated: 2026-10-27
review-date: 2026-12-27
rating: 5
confidence: high
difficulty: beginner
source: []
authors: []
folder: "00-MOCs/"
filename: "[MOC] Obsidian Core"
uid: moc-obsidian-core-20261027
moc: []
parent: []
children: []
related:
- "[[Obsidian Bases]]"
cssclasses:
- dashboard
- moc-page
- knowledge-note
 
 
 
🗺️ MOC — Obsidian Core
 
🎯 เกี่ยวกับหน้านี้
 
[!info] MOC = Map of Content / แผนที่ความรู้
หน้านี้รวบรวมแนวคิดและส่วนประกอบสำคัญของ Obsidian — เป็นจุดเริ่มต้นและทางเชื่อมไปยังหัวข้อหลักทั้งหมด
 
 
 
🏗️ แผนที่หัวข้อหลัก
 
🧱 แนวคิดพื้นฐาน
 
- [[Obsidian Bases]] — มุมมองแบบฐานข้อมูล จัดระเบียบ กรอง และคำนวณคุณสมบัติของบันทึก
- [[YAML Frontmatter]] — เมตาดาต้าที่ส่วนบนของไฟล์
- [[Property Types]] — ประเภทข้อมูลของคุณสมบัติ
- [[File Recovery]] — การกู้คืนไฟล์และบันทึก
 
📦 ส่วนประกอบหลัก
 
- [[Obsidian Properties Architecture and Metadata Management]] — สถาปัตยกรรมและการจัดการเมตาดาต้า
- [[File Recovery Plugin]] — ปลั๊กอินสำหรับกู้คืนไฟล์
- [[Agent Knowledge Base]] — ฐานความรู้สำหรับเอเจนต์
 
📋 มาตรฐานและแนวทาง
 
- [[MOC — Obsidian Properties]] — แผนที่ความรู้ด้านคุณสมบัติและเมตาดาต้า
 
 
 
🔗 ความสัมพันธ์
 
Linked Mentions
 
- [[Obsidian Bases]] อ้างอิงถึงหน้านี้เป็นแหล่งอ้างอิงหลัก
 
แผนภาพรวม
 
plaintext
  
                    [[MOC — Obsidian Core]]  ← บันทึกนี้
                              │
        ┌──────────────┬──────┴──────┬──────────────┐
        │              │             │              │
  [[Obsidian Bases]]  │  [[Properties]]        [[File Recovery]]
        │              │             │              │
  Agent Knowledge     │  YAML Frontmatter      File Recovery Plugin
  Knowledge Base      │  Property Types
 
 
 
 
✅ วิธีใช้หน้านี้
 
- เริ่มที่นี่ หากเพิ่งเริ่มเรียนรู้ระบบ Obsidian ของเรา
- คลิกหัวข้อที่สนใจ เพื่อเจาะลึกรายละเอียด
- กลับมาที่นี่ เสมอเมื่อหลงทางหรือต้องการภาพรวม
- แนะนำเพิ่มเติม หากมีหัวข้อสำคัญที่ยังขาดหาย
 
 
 
📝 หัวข้อที่ควรเพิ่ม
 
การติดตั้งและตั้งค่าเบื้องต้น
โครงสร้างโฟลเดอร์ที่แนะนำ
ปลั๊กอินหลักที่จำเป็น
เทคนิคการค้นหาและการเชื่อมโยงบันทึก
 
 
 
🏷 Keywords
 
#MOC
#Obsidian
#Core
#MapOfContent
#KnowledgeMap
 
 
 
dataview
  
LIST
FROM #topic/obsidian AND !"00-MOCs"
SORT file.name ASC
 
 
[!tip] 💡 คำแนะนำ
MOC ไม่ใช่สารบัญแบบคงที่ — ปรับเพิ่มลดหัวข้อให้สอดคล้องกับการเติบโตของฐานความรู้เสมอ ✅
 
 
 
✅ สร้างตามมาตรฐานครบถ้วนครับ
 
ต้องการจัดกลุ่มหัวข้อใหม่ หรือเพิ่มรายการเชื่อมโยงเพิ่มเติมไหมครับ 😊

🗺️ MOC ‑ Sibling (Obsidian Knowledge Architecture Full Set)
 
สร้างตามกฎ Vault ของคุณอย่างเต็มที่ + YAML + Dataview + WikiLinks + Folder Mapping + คำอธิบายว่า Sibling ใน Knowledge Graph หมายถึงอะไร
 
💡 ความหมายก่อนเริ่ม
 
Sibling (พี่น้อง / โหนดพี่น้องใน Knowledge Graph)
 
- ใน Vault = โน้ตที่อยู่ใน ระดับเดียวกัน มี Parent เดียวกัน แต่ไม่ใช่ Child กันโดยตรง
- ไม่ใช่ MOC ใหญ่เพียงอย่างเดียว แต่เป็น Pattern สำหรับจัดความสัมพันธ์
- MOC ‑ Sibling ทำหน้าที่เป็น Index สำหรับเรียนรู้วิธีจัด Sibling Relationships ใน Vault
 
📄 00‑System/MOCs/MOC - Sibling.md
 
markdown
  
---
title: "MOC - Sibling"
aliases:
  - MOC - โหนดพี่น้องใน Knowledge Graph
  - Sibling Relationship Map
  - Knowledge Sibling Index
type: moc
status: active
priority: medium
icon: "👨‍👩‍👧‍👦"
color: gray
domain: Knowledge Management
topics:
  - Knowledge Graph
  - Obsidian
  - Dataview
  - PARA
  - Zettelkasten
  - Vault Structure
tags:
  - moc
  - sibling
  - knowledge-graph
  - dataview
  - second-brain
  - vault-structure
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "MOC - Sibling"
slug: moc-sibling
uid: MOC‑SIB‑001
moc:
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Knowledge Hub]]
children:
  - [[[Evergreen] Sibling vs Parent vs Child Relationships]]
  - [[[Knowledge] Dataview Sibling Query Patterns]]
related:
  - [[MOC - Obsidian Second Brain]]
  - [[MOC - Research]]
  - [[MOC - AI]]
  - [[Vault Structure Guide]]
confidence: high
reviewed: false
---

# 🗺️ MOC - Sibling

## Overview
MOC ‑ Sibling เป็นแผนที่สำหรับเข้าใจและจัดการ **ความสัมพันธ์แบบพี่น้องใน Knowledge Graph** คือโน้ตที่มี Parent เดียวกัน อยู่ในระดับเดียวกัน และเสริมกัน แต่ไม่ได้เป็นลูกของกันเอง ช่วยให้ Vault ไม่กลายเป็นแค่รายการยาว แต่กลายเป็นแผนที่ความรู้ที่มีชั้นชัดเจน

## Core Concepts
- [[[Evergreen] Sibling vs Parent vs Child Relationships]]
- [[[Evergreen] Flat vs Hierarchical Knowledge]]
- [[[Knowledge] Dataview Sibling Query Patterns]]
- [[[Evergreen] Knowledge Graph Edge Types]]

## 📊 Dataview — ค้น Sibling ตัวอย่าง (ตาม Parent เดียวกัน)
> 💡 ต้องมี `parent:` ใน YAML จริงจึงทำงานเต็มที่
```dataview
TABLE
  title AS "ชื่อโน้ต",
  type AS "ประเภท",
  parent AS "Parent",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Sibling]])
SORT parent ASC, title ASC
 
 
📊 Dataview — หา Sibling ของ Parent ที่เลือก (ตัวอย่าง)
 
dataview
  
TABLE
  title AS "Sibling Candidate",
  type AS "ประเภท"
WHERE
  parent = [[MOC - Knowledge Hub]]
SORT title ASC
 
 
📊 Dataview — หาโน้ตที่มี Parent ว่าง / ไม่ชัดเจน
 
dataview
  
TABLE
  title AS "ชื่อโน้ต",
  type AS "ประเภท",
  moc AS "MOC"
WHERE
  parent = null OR length(parent) = 0
  AND contains(moc, [[MOC - Sibling]])
SORT title ASC
 
 
Evergreen Notes
 
- [[[Evergreen] Sibling vs Parent vs Child Relationships]]
- [[[Evergreen] Flat vs Hierarchical Knowledge]]
- [[[Evergreen] Knowledge Graph Edge Types]]
 
Articles
 
- [[Vault Structure Guide]]
 
Projects
 
- [[[Project] Vault Knowledge Graph Refactoring]]
 
Related MOCs
 
- [[MOC - Knowledge Hub]]
- [[MOC - Obsidian Second Brain]]
- [[MOC - Research]]
- [[MOC - AI]]
 
Learning Path
 
Beginner
 
- เข้าใจ Parent / Child / Sibling ความแตกต่าง
- ตรวจ YAML ให้มี parent / children / moc
- ดู Linked Mentions ใน Obsidian
 
Intermediate
 
- เขียน Dataview เพื่อค้น Sibling Groups
- ปรับ Vault ให้แต่ละ MOC มี Sibling ที่ชัดเจน
- ใช้ PARA เพื่อแยกโฟลเดอร์ + ความสัมพันธ์
 
Advanced
 
- สร้าง Knowledge Graph Maintenance Workflow
- ให้ AI Agent ช่วยแนะนำ Sibling Candidates
- สร้าง Dashboard สำหรับตรวจสุขภาพ Vault
 
plaintext
  

## 📄 05‑Knowledge/Evergreen/[Evergreen] Sibling vs Parent vs Child Relationships.md
```markdown
---
title: "[Evergreen] Sibling vs Parent vs Child Relationships"
aliases:
  - Sibling Parent Child ความแตกต่าง
  - ความสัมพันธ์โหนดใน Knowledge Graph
  - Hierarchy vs Association
type: evergreen
status: active
priority: high
icon: "🔗"
color: blue
domain: Knowledge Management
topics:
  - Knowledge Graph
  - Obsidian
  - Zettelkasten
  - Vault Structure
tags:
  - evergreen
  - knowledge-graph
  - sibling
  - parent-child
  - second-brain
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Evergreen"
filename: "[Evergreen] Sibling vs Parent vs Child Relationships"
slug: evergreen-sibling-parent-child
uid: EG‑SIB‑001
moc:
  - [[MOC - Sibling]]
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Sibling]]
children: []
related:
  - [[[Evergreen] Flat vs Hierarchical Knowledge]]
  - [[[Evergreen] Knowledge Graph Edge Types]]
  - [[Vault Structure Guide]]
confidence: high
reviewed: false
---

# 🌱 [Evergreen] Sibling vs Parent vs Child Relationships

## Summary
Parent = โหนดที่ครอบคลุม, Child = โหนดย่อยของ Parent, Sibling = โหนดที่มี Parent เดียวกัน อยู่ในระดับเดียวกัน เสริมกัน แต่ไม่ได้เป็นลูกกัน ความสัมพันธ์นี้ไม่ได้มาจากโฟลเดอร์อย่างเดียว แต่มาจาก **Meaning + YAML + WikiLinks**

## Core Idea
- Principle 1: Folder ≠ Relationship อย่างสมบูรณ์ (Folder เป็น Organization ส่วน Graph เป็น Meaning)
- Principle 2: Sibling ต้องมี Common Parent หรือ Common Theme
- Principle 3: Child = Subset / Detail ของ Parent
- Principle 4: Sibling = Parallel Alternative / Parallel Concept
- Principle 5: Knowledge Graph มีหลาย Edge ไม่ใช่แค่ Tree เท่านั้น

## Why It Matters
ถ้าไม่แยกชัด Vault จะกลายเป็น "Heap of Notes" แทน Knowledge Graph จริง MOC จะไม่กลายเป็น Map แต่กลายเป็นแค่รายการยาว

## Example
- Parent: [[MOC - Research]]
- Sibling A: [[[Evergreen] Iterative Research Loop]]
- Sibling B: [[[Evergreen] Source Verification for AI Agents]]
- Sibling C: [[[Evergreen] Synthesis vs Retrieval]]
- Child ของ Sibling ไม่ได้หมายความว่าเป็น Sibling ของ Parent โดยตรง

## Key Insight
Tree = Hierarchy ส่วน Knowledge Graph = Network ที่มีหลายประเภทของ Edge Sibling เป็นหนึ่งใน Mental Model สำหรับจัดความสัมพันธ์ ไม่ใช่กฎบังคับอย่างเดียว

## Related Notes
- [[MOC - Sibling]]
- [[[Evergreen] Flat vs Hierarchical Knowledge]]
- [[[Evergreen] Knowledge Graph Edge Types]]
- [[Vault Structure Guide]]
 
 
📄 05‑Knowledge/Concepts/[Knowledge] Dataview Sibling Query Patterns.md
 
markdown
  
---
title: "[Knowledge] Dataview Sibling Query Patterns"
aliases:
  - รูปแบบ Query Sibling ด้วย Dataview
  - Dataview Sibling Discovery
type: knowledge
status: active
priority: medium
icon: "📊"
color: orange
domain: Knowledge Management
topics:
  - Dataview
  - Obsidian
  - Knowledge Graph
  - Sibling
tags:
  - knowledge
  - dataview
  - query
  - sibling
  - obsidian
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Concepts"
filename: "[Knowledge] Dataview Sibling Query Patterns"
slug: knowledge-dataview-sibling-queries
uid: KNW‑SIB‑001
moc:
  - [[MOC - Sibling]]
  - [[MOC - Obsidian Second Brain]]
parent:
  - [[MOC - Sibling]]
children: []
related:
  - [[MOC - Knowledge Hub]]
  - [[Vault Structure Guide]]
confidence: medium
reviewed: false
---

# [Knowledge] Dataview Sibling Query Patterns

## Summary
Dataview ไม่มีฟังก์ชัน `sibling()` โดยตรง จึงต้องสร้างผ่าน `parent:` + `contains()` เพื่อค้นหาโน้ตที่มี Parent เดียวกัน เพื่อค้นพบ Sibling Candidates สำหรับ Vault Maintenance

## Key Concepts
- Sibling Candidate = Notes sharing the same parent
- ไม่ได้ยืนยันว่าเป็น Sibling ตามความหมายจริง ต้องมนุษย์ตรวจ
- ต้องมี YAML Field `parent:` ที่ถูกต้อง
- Linked Mentions เป็นอีกชั้นหนึ่ง แยกจาก Parent Field

## Details
### Query 1: ค้นทุกโน้ตที่มี Parent เดียวกัน (ตัวอย่าง)
```dataview
TABLE
  title AS "Candidate Sibling",
  type AS "ประเภท",
  parent AS "Parent",
  moc AS "MOC"
WHERE
  parent = [[MOC - Research]]
SORT title ASC
 
 
Query 2: ค้น Sibling ภายใน MOC Sibling
 
dataview
  
TABLE
  title AS "Candidate Sibling",
  parent AS "Parent"
WHERE
  contains(moc, [[MOC - Sibling]])
SORT parent ASC
 
 
Query 3: ค้นโน้ตที่มี Parent ซ้ำกัน (Group View)
 
dataview
  
TABLE
  rows.title AS "Candidate Siblings"
WHERE
  contains(moc, [[MOC - Sibling]])
GROUP BY parent
 
 
Insights
 
- Dataview ให้ Candidate Map ไม่ใช่ความจริงของ Knowledge Graph อัตโนมัติ
- Sibling ที่แท้จริงต้องผ่านการ Curate จากมนุษย์
- ควรแยก  parent:  (Hierarchy) กับ  related:  (Association) ออกจากกัน
 
Related Notes
 
- [[MOC - Sibling]]
- [[[Evergreen] Sibling vs Parent vs Child Relationships]]
- [[Vault Structure Guide]]
 
plaintext
  

# 🧠 สภาพ Vault หลังสร้าง
✅ MOC ‑ Sibling เป็น Index หลัก
✅ มี Evergreen Note สำหรับ Mental Model
✅ มี Knowledge Note สำหรับ Dataview Patterns
✅ เชื่อมกับ [[MOC - Knowledge Hub]]
✅ สอดคล้องกับ PARA / Zettelkasten
✅ เตรียมสำหรับ Vault Refactoring
✅ แยก Folder Structure กับ Knowledge Graph Meaning

## 📌 สิ่งที่ควรสร้างต่อ
- [[[Evergreen] Flat vs Hierarchical Knowledge]]
- [[[Evergreen] Knowledge Graph Edge Types]]
- [[[Project] Vault Knowledge Graph Refactoring]]
- [[Dataview Vault Health Dashboard]]
- [[Second Brain Maintenance Checklist]]
- [[MOC - Obsidian Second Brain]] เต็มฉบับ

💡 หมายเหตุ: นี่เป็น MOC สำหรับ **Sibling Relationships ใน Vault Knowledge Graph** ไม่ใช่ Sibling ในระบบ AI หรือ Kubernetes โดยตรง หากต้องการเปลี่ยนความหมายให้เป็น Sibling Agents / Sibling Services สามารถแก้ Theme ได้ใหม่ครับ

ต้องการให้ผมสร้าง **[[[Evergreen] Flat vs Hierarchical Knowledge]] ต่อเลยหรือไม่ครับ?**