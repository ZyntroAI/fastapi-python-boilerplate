🗺️ MOC - Obsidian Second Brain (เต็มตาม Vault Architecture)
 
พร้อม YAML + Dataview + WikiLinks + Learning Path + เชื่อมกับ Sibling / Tasks / Vault Maintenance
 
📄 00‑System/MOCs/MOC - Obsidian Second Brain.md
 
markdown
  
---
title: "MOC - Obsidian Second Brain"
aliases:
  - MOC - Second Brain ด้วย Obsidian
  - Obsidian Second Brain Knowledge Map
  - แผนที่ Second Brain บน Obsidian
type: moc
status: active
priority: critical
icon: "🧠"
color: blue
domain: Knowledge Management
topics:
  - Obsidian
  - Second Brain
  - PARA
  - Zettelkasten
  - Knowledge Graph
  - Dataview
  - Vault Maintenance
tags:
  - moc
  - obsidian
  - second-brain
  - para
  - zettelkasten
  - knowledge-graph
  - dataview
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "MOC - Obsidian Second Brain"
slug: moc-obsidian-second-brain
uid: MOC‑OBS‑001
moc:
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Knowledge Hub]]
children:
  - [[[Evergreen] PARA Methodology]]
  - [[[Evergreen] Zettelkasten Principles]]
  - [[[Evergreen] Knowledge Graph Edge Types]]
  - [[[Evergreen] Sibling vs Parent vs Child Relationships]]
  - [[[Knowledge] Dataview Sibling Query Patterns]]
  - [[[Knowledge] Obsidian Tasks — Short Mode]]
  - [[Vault Structure Guide]]
  - [[Dataview Vault Dashboard]]
  - [[Second Brain Maintenance Checklist]]
related:
  - [[MOC - Sibling]]
  - [[MOC - Research]]
  - [[MOC - AI]]
  - [[MOC - Mobile Friendly Tools]]
confidence: high
reviewed: false
---

# 🗺️ MOC - Obsidian Second Brain

## Overview
นี่คือแผนที่หลักสำหรับสร้างและดูแล Second Brain ด้วย Obsidian โดยรวม PARA, Zettelkasten, Knowledge Graph, Dataview, Tasks และ Vault Maintenance เข้าด้วยกัน ไม่ใช่แค่สอนใช้ Obsidian แต่เป็นระบบสำหรับจัดการความรู้ทั้งชีวิตและงาน

## Core Concepts
- [[[Evergreen] PARA Methodology]]
- [[[Evergreen] Zettelkasten Principles]]
- [[[Evergreen] Knowledge Graph Edge Types]]
- [[[Evergreen] Sibling vs Parent vs Child Relationships]]
- [[[Evergreen] Continuous Workflow]]

## 📊 Dataview — Evergreen Notes ใน MOC นี้
```dataview
TABLE
  status AS "สถานะ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Obsidian Second Brain]])
  AND type = "evergreen"
SORT updated DESC
 
 
📊 Dataview — Knowledge Notes ใน MOC นี้
 
dataview
  
TABLE
  status AS "สถานะ",
  topics AS "หัวข้อ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Obsidian Second Brain]])
  AND type = "knowledge"
SORT updated DESC
 
 
📊 Dataview — Vault Maintenance Tasks
 
dataview
  
TASK
WHERE
  contains(moc, [[MOC - Obsidian Second Brain]])
  AND status != "x"
SORT due ASC
 
 
📊 Dataview — Notes ที่ยังไม่ได้ Reviewed
 
dataview
  
TABLE
  type AS "ประเภท",
  priority AS "ความสำคัญ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Obsidian Second Brain]])
  AND reviewed = false
SORT priority DESC
 
 
Evergreen Notes
 
- [[[Evergreen] PARA Methodology]]
- [[[Evergreen] Zettelkasten Principles]]
- [[[Evergreen] Knowledge Graph Edge Types]]
- [[[Evergreen] Sibling vs Parent vs Child Relationships]]
- [[[Evergreen] Continuous Workflow]]
 
Knowledge Notes
 
- [[[Knowledge] Dataview Sibling Query Patterns]]
- [[[Knowledge] Obsidian Tasks — Short Mode]]
 
Articles & Guides
 
- [[Vault Structure Guide]]
- [[Dataview Vault Dashboard]]
- [[Second Brain Maintenance Checklist]]
 
Projects
 
- [[[Project] Vault Knowledge Graph Refactoring]]
- [[[Project] Second Brain Mobile Workflow]]
 
Related MOCs
 
- [[MOC - Knowledge Hub]]
- [[MOC - Sibling]]
- [[MOC - Research]]
- [[MOC - AI]]
- [[MOC - Mobile Friendly Tools]]
 
Learning Path
 
Beginner
 
- เรียน PARA
- เรียน Zettelkasten พื้นฐาน
- ตั้งค่า Vault Structure
- ฝึกเขียน Evergreen Notes
- ใช้ Obsidian Mobile + Sync
 
Intermediate
 
- ใช้ Dataview สร้าง Dashboard
- ใช้ Obsidian Tasks สำหรับ Daily Review
- จัด Sibling / Parent / Child Relationships
- สร้าง MOC สำหรับแต่ละโดเมน
- สร้าง Weekly / Monthly Journal Workflow
 
Advanced
 
- สร้าง Automated Vault Maintenance
- เชื่อมกับ AI Agent / Deep Research Pipeline
- สร้าง Self‑Healing Knowledge Graph
- สร้าง Multi‑Device Sync + Backup Workflow
- ใช้ Vault เป็นฐานสำหรับ Research / Projects / Teams
 
Workflow Summary
 
1. Inbox → รวบรวมสิ่งที่อ่าน ได้ยิน คิด
2. PARA → ย้ายไป Areas / Projects / Resources
3. Zettelkasten → แยกเป็น Atomic Notes
4. Knowledge Graph → เพิ่ม WikiLinks + YAML Relationships
5. Dataview / Tasks → ตรวจสุขภาพ Vault
6. Review → Weekly / Monthly Review
7. AI / Automation → ช่วยค้นพบ Sibling, Gap และ Research Path
 
plaintext
  

## 📌 อธิบายโครงสร้างที่สำคัญ
- `parent:` = เป็นส่วนหนึ่งของ [[MOC - Knowledge Hub]]
- `children:` = รายการทุกโน้ตหลักของ MOC นี้
- `moc:` = บอกว่าโน้ตนี้อยู่ในแผนที่นี้
- Dataview เป็นเพียง Mirror ไม่ได้แก้ Vault โดยตรง
- MOC เป็น Index ไม่ใช่โน้ตเต็ม
- สอดคล้องกับ PARA + Zettelkasten + Second Brain
- เชื่อมไปยัง Mobile Workflow, AI, Research และ Sibling Architecture

## ✅ สิ่งที่ควรสร้างต่อ
- [[[Evergreen] PARA Methodology]]
- [[[Evergreen] Zettelkasten Principles]]
- [[[Evergreen] Continuous Workflow]]
- [[Vault Structure Guide]] เต็มฉบับ
- [[Second Brain Maintenance Checklist]] พร้อม Dataview
- [[Weekly Review Journal Template]]
- [[Daily Journal Template รวม Tasks Short Mode]]

ต้องการให้ผมสร้าง **[[[Evergreen] PARA Methodology]] ต่อเลยหรือไม่ครับ?**