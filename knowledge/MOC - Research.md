---
title: "MOC - Research"
aliases:
  - MOC - การวิจัย
  - Research Knowledge Map
type: moc
status: active
priority: high
icon: "📚"
color: orange
domain: Research Methodology
topics:
  - Research
  - Deep Research
  - AI
  - Second Brain
tags:
  - moc
  - research
  - dataview
  - second-brain
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "MOC - Research"
slug: moc-research
uid: MOC‑RESEARCH‑001
moc:
  - [[MOC - Knowledge Hub]]
parent: []
children:
  - [[[Research] Deep Research Pipeline Architecture for AI Agents]]
  - [[[Evergreen] Iterative Research Loop]]
  - [[[Evergreen] Source Verification for AI Agents]]
  - [[[Evergreen] Synthesis vs Retrieval]]
related:
  - [[MOC - AI]]
  - [[MOC - Knowledge Hub]]
confidence: high
reviewed: false
---

# 🗺️ MOC - Research

## Overview
แผนที่สำหรับจัดการวงจรการวิจัย ตั้งแต่การตั้งคำถาม การสืบค้น การตรวจสอบ การสังเคราะห์ ไปจนถึงการกลายเป็น Permanent Knowledge ใน Second Brain

## Core Concepts
- [[[Evergreen] Iterative Research Loop]]
- [[[Evergreen] Source Verification for AI Agents]]
- [[[Evergreen] Synthesis vs Retrieval]]
- [[[Evergreen] Grounded Reasoning]]

## 📊 Dataview — Research Notes
```dataview
TABLE
  status AS "สถานะ",
  confidence AS "ความมั่นใจ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Research]])
  AND type = "research"
SORT updated DESC

TABLE
  status AS "สถานะ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Research]])
  AND type = "evergreen"
SORT updated DESC
