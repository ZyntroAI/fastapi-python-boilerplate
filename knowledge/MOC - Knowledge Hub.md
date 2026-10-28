🗺️ MOC - Knowledge Hub (เต็มตาม Vault Architecture)
 
พร้อม YAML + Dataview + WikiLinks + Learning Path + เชื่อมทุก MOC หลักเข้าด้วยกัน
 
📄 00‑System/MOCs/MOC - Knowledge Hub.md
 
markdown
  
---
title: "MOC - Knowledge Hub"
aliases:
  - MOC - ศูนย์กลางความรู้
  - Vault Master Map
  - Second Brain Central Index
type: moc
status: active
priority: critical
icon: "🧠"
color: blue
domain: Knowledge Management
topics:
  - Knowledge Graph
  - Second Brain
  - Obsidian
  - PARA
  - Zettelkasten
  - Vault Governance
tags:
  - moc
  - knowledge-hub
  - vault
  - second-brain
  - dataview
  - knowledge-graph
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "MOC - Knowledge Hub"
slug: moc-knowledge-hub
uid: MOC‑HUB‑001
moc: []
parent: []
children:
  - [[MOC - Obsidian Second Brain]]
  - [[MOC - Sibling]]
  - [[MOC - Research]]
  - [[MOC - AI]]
  - [[MOC - Programming]]
  - [[MOC - DevOps]]
  - [[MOC - Networking]]
  - [[MOC - Mobile Friendly Tools]]
related:
  - [[Dataview Vault Dashboard]]
  - [[Vault Structure Guide]]
  - [[Second Brain Maintenance Checklist]]
confidence: high
reviewed: false
---

# 🗺️ MOC - Knowledge Hub

## Overview
Knowledge Hub คือ **แผนที่หลักของทั้ง Vault** ทำหน้าที่เป็นจุดเริ่มต้นสำหรับ Second Brain เชื่อม MOC ต่างๆ เข้าด้วยกัน แสดงภาพรวม ไม่ได้เก็บเนื้อหาเต็ม แต่ช่วยให้เห็นว่าความรู้ทั้งหมดเชื่อมโยงกันอย่างไร

## Core Principles
- [[[Evergreen] PARA Methodology]]
- [[[Evergreen] Zettelkasten Principles]]
- [[[Evergreen] Knowledge Graph Edge Types]]
- [[[Evergreen] Sibling vs Parent vs Child Relationships]]
- [[[Evergreen] Continuous Workflow]]

## 📊 Dataview — ทุก MOC ใน Vault
```dataview
TABLE
  status AS "สถานะ",
  priority AS "ความสำคัญ",
  updated AS "อัปเดตล่าสุด"
WHERE
  type = "moc"
SORT title ASC
 
 
📊 Dataview — Evergreen Notes ทั้งหมด
 
dataview
  
TABLE
  status AS "สถานะ",
  confidence AS "ความมั่นใจ",
  updated AS "อัปเดตล่าสุด"
WHERE
  type = "evergreen"
SORT updated DESC
 
 
📊 Dataview — Projects ทั้งหมด
 
dataview
  
TABLE
  status AS "สถานะ",
  priority AS "ความสำคัญ",
  updated AS "อัปเดตล่าสุด"
WHERE
  type = "project"
SORT priority DESC
 
 
📊 Dataview — Notes ที่ยังไม่ได้ Review
 
dataview
  
TABLE
  type AS "ประเภท",
  moc AS "MOC",
  updated AS "อัปเดตล่าสุด"
WHERE
  reviewed = false
SORT updated DESC
 
 
📊 Dataview — Notes ที่ไม่มี MOC (Candidate)
 
💡 เป็นเพียง Candidate ต้องตรวจด้วยตาเอง
 
dataview
  
TABLE
  type AS "ประเภท",
  created AS "สร้างเมื่อ"
WHERE
  moc = null OR length(moc) = 0
SORT created DESC
 
 
🗺️ MOC Children (Domain Maps)
 
- [[MOC - Obsidian Second Brain]]
- [[MOC - Sibling]]
- [[MOC - Research]]
- [[MOC - AI]]
- [[MOC - Programming]]
- [[MOC - DevOps]]
- [[MOC - Networking]]
- [[MOC - Mobile Friendly Tools]]
 
📚 Evergreen Core
 
- [[[Evergreen] PARA Methodology]]
- [[[Evergreen] Zettelkasten Principles]]
- [[[Evergreen] Knowledge Graph Edge Types]]
- [[[Evergreen] Sibling vs Parent vs Child Relationships]]
- [[[Evergreen] Continuous Workflow]]
 
📖 Guides & Dashboards
 
- [[Vault Structure Guide]]
- [[Dataview Vault Dashboard]]
- [[Second Brain Maintenance Checklist]]
 
🚀 Projects
 
- [[[Project] Vault Knowledge Graph Refactoring]]
- [[[Project] Second Brain Mobile Workflow]]
- [[[Project] AI Agent Platform]]
 
Learning Path
 
Beginner
 
- เข้าใจ Vault Structure
- เรียน PARA + Zettelkasten
- เรียนวิธีเขียน Evergreen Notes
- ตั้งค่า Dataview + Tasks
- เริ่ม Weekly Review
 
Intermediate
 
- สร้างแต่ละ Domain MOC
- จัด Parent / Child / Sibling Relationships
- สร้าง Dashboard สำหรับ Vault Health
- เชื่อม Research เข้ากับ Knowledge Graph
- ตั้งค่า Sync + Backup
 
Advanced
 
- สร้าง Automated Vault Maintenance
- เชื่อม Deep Research Pipeline เข้ากับ Vault
- ให้ AI Agent ช่วยค้นพบ Knowledge Gap
- สร้าง Team Knowledge Workflow
- ปรับ Vault ให้เติบโตได้โดยไม่กลายเป็น Heap
 
Workflow for the Whole Vault
 
1. Inbox (01‑Inbox) → รวบรวมสิ่งที่พบ อ่าน คิด
2. Classify → ย้ายไป Areas / Projects / Resources
3. Curate → แยกเป็น Evergreen / Knowledge / Research
4. Map → เพิ่ม MOC / Parent / Related Links
5. Review → Weekly / Monthly Review
6. Automate → Dataview, Tasks, AI Assistance
7. Archive → ย้ายสิ่งที่ไม่ใช้แล้วไป 99‑Archive
 
Rules for Knowledge Hub
 
- Knowledge Hub เป็น Index ไม่ใช่ Encyclopedia
- ทุกโน้ตควรอยู่ในอย่างน้อยหนึ่ง MOC
- Parent ≠ Folder เสมอไป
- Sibling = ความสัมพันธ์ตามความหมาย ไม่ใช่แค่อยู่โฟลเดอร์เดียวกัน
- Dataview = Mirror ไม่ใช่การแก้ Vault อัตโนมัติ
- Evergreen = ความหลักการที่ยังคงใช้ได้หลายปี
- Research / News / Release Notes = ชั่วคราว ต้องถูกสังเคราะห์ก่อน
 
Related Notes
 
- [[MOC - Obsidian Second Brain]]
- [[Dataview Vault Dashboard]]
- [[Vault Structure Guide]]
- [[Second Brain Maintenance Checklist]]
 
plaintext
  

## 📌 อัปเดต MOC ลูกที่เกี่ยวข้อง (ตัวอย่าง)
> ตัวอย่างสำหรับ [[MOC - Obsidian Second Brain]]
```markdown
moc:
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Knowledge Hub]]
 
 
ตัวอย่างสำหรับ [[MOC - Sibling]]
 
markdown
  
moc:
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Knowledge Hub]]
 
 
✅ สิ่งที่ได้แล้ว
 
- MOC ‑ Knowledge Hub เป็น Root Map
- มี Dataview สำหรับเห็นทั้ง Vault
- มี Learning Path 3 ระดับ
- มี Vault Workflow เต็ม
- เชื่อมกับ Obsidian, Research, AI, DevOps, Mobile Workflow
- สอดคล้องกับ PARA / Zettelkasten / Second Brain
- เตรียมสำหรับ Vault Refactoring
 
📌 สิ่งที่ควรสร้างต่อ
 
- [[[Evergreen] PARA Methodology]]
- [[[Evergreen] Zettelkasten Principles]]
- [[Vault Structure Guide]] เต็มฉบับ
- [[Dataview Vault Dashboard]] เต็ม
- [[Second Brain Maintenance Checklist]] พร้อม Tasks
- [[Weekly Review Journal Template]]
- [[Daily Journal Template]]
- [[MOC - Programming]] เต็ม
- [[MOC - DevOps]] เต็ม
 
💡 หมายเหตุ: Dataview จะแสดงผลได้เต็มเมื่อทุกโน้ตจริงมี  type: ,  status: ,  moc: ,  parent:  ที่ถูกต้อง และเปิด Dataview Plugin ใน Obsidian ครับ
 
ต้องการให้ผมสร้าง [[[Evergreen] PARA Methodology]] ต่อเลยหรือไม่ครับ?