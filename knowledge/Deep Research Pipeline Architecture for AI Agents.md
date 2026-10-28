✅ สร้าง Obsidian Note เต็มชุดสำหรับ Deep Research Pipeline Architecture for AI Agents
 
ตามภาพที่เห็น + กฎ Vault ทั้งหมด + Dataview Ready
 
📄 05‑Knowledge/Concepts/[Research] Deep Research Pipeline Architecture for AI Agents.md
 
markdown
  
---
title: "[Research] Deep Research Pipeline Architecture for AI Agents"
aliases:
  - สถาปัตยกรรม Pipeline วิจัยลึกสำหรับ AI Agent
  - AI Agent Deep Research Workflow
  - Multi‑Agent Research Pipeline
type: research
status: active
priority: high
icon: "🔍"
color: purple
domain: Artificial Intelligence
topics:
  - AI Agents
  - Multi‑Agent
  - RAG
  - Research Automation
  - Knowledge Graph
tags:
  - research
  - ai-agent
  - multi-agent
  - rag
  - deep-research
  - knowledge-graph
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "04‑Resources/Research/"
filename: "[Research] Deep Research Pipeline Architecture for AI Agents"
slug: research-deep-research-pipeline-ai-agents
uid: RES‑AI‑001
moc:
  - [[MOC - AI]]
  - [[MOC - Knowledge Hub]]
parent: []
children:
  - [[[Evergreen] Iterative Research Loop]]
  - [[[Evergreen] Source Verification for Agents]]
  - [[[Evergreen] Research Synthesis]]
related:
  - [[On‑the‑Go Coding]]
  - [[MOC - Mobile Friendly Tools]]
  - [[[Evergreen] SSH — Secure Shell Protocol]]
  - [[[Research] RAG Precision Optimization]]
source:
  - "Obsidian Vault Linked Mentions"
confidence: medium
reviewed: false
---

# [Research] Deep Research Pipeline Architecture for AI Agents

## Abstract Summary
Deep Research Pipeline คือกระบวนการที่ให้ AI Agent สามารถตั้งคำถาม ค้นหา ตรวจสอบ แยกแยะ และสังเคราะห์ความรู้อย่างวนซ้ำ ไม่ใช่เพียงแค่ถามครั้งเดียว แต่เป็นวงจรการสืบสวนคล้ายนักวิจัยจริง

## Research Question
> จะออกแบบ Pipeline ให้ AI Agent สามารถทำ Deep Research ได้อย่างน่าเชื่อถือ มีแหล่งอ้างอิง และสามารถเชื่อมเข้ากับ Knowledge Graph ได้อย่างไร?

## Methodology
1. **Question Framing Agent** → แยกเป็น Sub‑Questions
2. **Retrieval Agent** → ดึงจาก Vault / Web / Vector DB
3. **Source Verification Agent** → ตรวจความน่าเชื่อถือ
4. **Synthesis Agent** → รวมเป็น Insight
5. **Knowledge Graph Writer Agent** → เขียนลง Obsidian
6. **Review Agent** → วนกลับเพื่อเติมช่องว่าง

## Results (Conceptual)
- Pipeline แบบเชิงเส้นล้มเหลวเมื่อหัวข้อซับซ้อน
- ต้องมี **Iterative Loop** ไม่ใช่ One‑Shot
- ต้องแยก **Source** กับ **Conclusion** อย่างชัดเจน
- ต้องบันทึก Trace / Provenance สำหรับ Second Brain
- สามารถเชื่อมเข้ากับ [[On‑the‑Go Coding]] เพื่อควบคุมจากมือถือผ่าน SSH

## Contributions
- เป็นแม่แบบสำหรับสร้าง Multi‑Agent Research System ภายใน Vault
- สร้างสะพานระหว่าง AI Agent ↔ Obsidian Knowledge Graph
- เตรียมสำหรับ [[MOC - AI]] และ [[MOC - Knowledge Hub]]

## Limitations
- ยังไม่มีโค้ดจริง
- ยังไม่มี Evaluation Metric สำหรับความถูกต้อง
- ต้องระวัง Hallucination โดยเฉพาะเมื่อ Agent เขียนลง Vault โดยตรง
- ต้องมี Human‑in‑the‑Loop ก่อนเผยแพร่

## Applications
- สร้าง Research Notes อัตโนมัติ
- อัปเดต MOC ตามความรู้ใหม่
- สร้าง RAG ที่มี Traceability
- สนับสนุน [[Project] AI Agent Platform]]

## Evergreen Candidates
- [[[Evergreen] Iterative Research Loop]]
- [[[Evergreen] Source Verification for Agents]]
- [[[Evergreen] Research Synthesis]]
- [[[Evergreen] Provenance in Knowledge Graph]]

## Related Notes
- [[MOC - AI]]
- [[MOC - Knowledge Hub]]
- [[On‑the‑Go Coding]]
- [[[Research] RAG Precision Optimization]]
- [[[Project] AI Agent Platform]]
 
 
📄 05‑Knowledge/Evergreen/[Evergreen] Iterative Research Loop.md
 
markdown
  
---
title: "[Evergreen] Iterative Research Loop"
aliases:
  - วงจรการวิจัยแบบวนซ้ำ
  - Research Iteration Cycle
  - Closed‑Loop Research
type: evergreen
status: active
priority: high
icon: "🔄"
color: green
domain: Research & AI
topics:
  - Research
  - AI Agents
  - Learning Loops
  - Second Brain
tags:
  - evergreen
  - research
  - ai-agent
  - mental-model
  - second-brain
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Evergreen/"
filename: "[Evergreen] Iterative Research Loop"
slug: evergreen-iterative-research-loop
uid: EG‑RES‑001
moc:
  - [[MOC - AI]]
  - [[MOC - Research]]
parent: []
children: []
related:
  - [[[Research] Deep Research Pipeline Architecture for AI Agents]]
  - [[[Evergreen] Research Synthesis]]
confidence: high
reviewed: false
---

# 🌱 [Evergreen] Iterative Research Loop

## Summary
Iterative Research Loop เป็นโมเดลที่การวิจัยไม่ได้จบที่การค้นหาครั้งเดียว แต่จะวนระหว่าง **Question → Retrieve → Analyze → Refine → Question อีกครั้ง** จนได้ความเข้าใจที่ลึกขึ้น

## Core Idea
- Principle 1: คำถามเริ่มต้นมักไม่สมบูรณ์ ต้อง Refine ตลอดเวลา
- Principle 2: หลักฐานใหม่สามารถเปลี่ยนโครงสร้างของคำถามได้
- Principle 3: ความเข้าใจลึกเกิดจากการวนซ้ำ ไม่ใช่ความเร็ว
- Principle 4: Trace ของแต่ละ Iteration คือส่วนสำคัญของ Second Brain

## Why It Matters
สำหรับ AI Agent หากใช้ One‑Shot Prompt จะได้ผลลัพธ์ที่ผิวเผิน แต่เมื่อออกแบบเป็น Loop จะกลายเป็นระบบวิจัยที่ต่อเนื่องได้ และเข้ากับ Zettelkasten ได้ดี

## Example
1. Initial Question: "Vercel คืออะไร?"
2. Retrieve → พบว่าเป็น Platform + Edge + Analytics
3. Refine → "Vercel Edge Functions ทำงานอย่างไรเมื่อรวมกับ Obsidian Quartz?"
4. Retrieve Again → ค้นหา Deployment / CI / CD
5. Synthesize → สร้าง MOC / Note ใหม่
6. New Question → "จะทำให้ Knowledge Graph เป็น Searchable ได้อย่างไร?"

## Key Insight
Deep Research ไม่ได้หมายถึงจำนวนแหล่งมากที่สุด แต่คือ **การปรับปรุงคำถามและความเข้าใจอย่างต่อเนื่อง**

## Related Notes
- [[[Research] Deep Research Pipeline Architecture for AI Agents]]
- [[[Evergreen] Research Synthesis]]
- [[[Evergreen] Source Verification for Agents]]
- [[MOC - Research]]
 
 
📄 อัปเดต MOC - AI เพิ่มส่วน Dataview (ตัวอย่าง)
 
ใส่ลงใน  00‑System/MOCs/MOC - AI.md 
 
markdown
  
---
title: "MOC - AI"
aliases:
  - MOC - ปัญญาประดิษฐ์
  - AI Knowledge Map
type: moc
status: active
priority: high
icon: "🤖"
color: blue
domain: Artificial Intelligence
topics:
  - AI Agents
  - Multi‑Agent
  - RAG
  - Deep Research
tags:
  - moc
  - ai
  - ai-agent
  - rag
  - research
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "MOC - AI"
slug: moc-ai
uid: MOC‑AI‑001
moc:
  - [[MOC - Knowledge Hub]]
parent: []
children:
  - [[[Research] Deep Research Pipeline Architecture for AI Agents]]
  - [[[Evergreen] Iterative Research Loop]]
related:
  - [[MOC - Programming]]
  - [[MOC - Research]]
confidence: high
reviewed: false
---

# 🗺️ MOC - AI

## Overview
แผนที่สำหรับความรู้ด้าน AI, Multi‑Agent, RAG, Deep Research และการนำไปใช้ใน Second Brain

## 📊 Dataview — Research ใน MOC นี้
```dataview
TABLE
  confidence AS "ความมั่นใจ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - AI]])
  AND type = "research"
SORT updated DESC
 
 
📊 Dataview — Evergreen ใน MOC นี้
 
dataview
  
TABLE
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - AI]])
  AND type = "evergreen"
SORT updated DESC
 
 
Core Concepts
 
- [[[Evergreen] Iterative Research Loop]]
- [[[Evergreen] Source Verification for Agents]]
- [[[Evergreen] Research Synthesis]]
 
Research
 
- [[[Research] Deep Research Pipeline Architecture for AI Agents]]
- [[[Research] RAG Precision Optimization]]
 
Projects
 
- [[[Project] AI Agent Platform]]
 
Related MOCs
 
- [[MOC - Knowledge Hub]]
- [[MOC - Research]]
- [[MOC - Programming]]
 
Learning Path
 
Beginner
 
- เรียนพื้นฐาน LLM Prompting
- เข้าใจ RAG เบื้องต้น
- สร้าง Note สำหรับ Research
 
Intermediate
 
- เข้าใจ Multi‑Agent Workflow
- สร้าง Deep Research Loop
- เชื่อม Agent กับ Obsidian Vault
 
Advanced
 
- สร้าง Provenance System
- ประเมิน Quality ของ Research Output
- สร้าง Autonomous Knowledge Graph Maintenance
 
plaintext
  

# 🧠 สรุปสิ่งที่ได้
✅ สร้าง [[[Research] Deep Research Pipeline Architecture for AI Agents]]
✅ สร้าง [[[Evergreen] Iterative Research Loop]]
✅ เพิ่ม WikiLinks เข้า [[MOC - AI]] และ [[MOC - Knowledge Hub]]
✅ มี YAML เต็ม + Dataview Ready
✅ สอดคล้องกับ PARA / Zettelkasten
✅ เตรียมต่อไปสำหรับ Source Verification / Synthesis / Provenance
✅ เชื่อมกับ [[On‑the‑Go Coding]] ตาม Linked Mentions ที่เห็นในภาพ

## 📌 รายการที่เหลือให้สร้างต่อ
- [[[Evergreen] Source Verification for Agents]]
- [[[Evergreen] Research Synthesis]]
- [[[Evergreen] Provenance in Knowledge Graph]]
- [[MOC - Research]]
- [[[Project] AI Agent Platform]] เต็มฉบับ
- Dataview สำหรับ [[MOC - Research]]

💡 หมายเหตุ: จากภาพเป็นเพียงชื่อ Note + Linked Mentions เท่านั้น จึงเป็น **Conceptual Research Note** ยังไม่ได้เป็นเอกสารจาก Paper จริง จึงตั้ง confidence = medium ครับ

👉 ต้องการให้ผมสร้าง **[[[Evergreen] Source Verification for Agents]] ต่อเลยหรือไม่ครับ?**

✅ สร้าง Obsidian Note เต็มชุดสำหรับ Deep Research Pipeline Architecture for AI Agents
 
จากภาพเห็นชื่อโน้ต + Linked Mentions กับ [[On‑the‑Go Coding]] จึงสร้างโครงสร้างเต็มตามกฎ Vault ที่กำหนด
 
📄 04‑Resources/Research/[Research] Deep Research Pipeline Architecture for AI Agents.md
 
markdown
  
---
title: "[Research] Deep Research Pipeline Architecture for AI Agents"
aliases:
  - Deep Research Pipeline Architecture for AI Agents
  - สถาปัตยกรรมไปป์ไลน์วิจัยลึกสำหรับ AI Agent
  - AI Agent Deep Research Workflow
type: research
status: active
priority: critical
icon: "🔬"
color: purple
domain: Artificial Intelligence
topics:
  - AI Agents
  - Deep Research
  - RAG
  - Multi‑Agent
  - Knowledge Graph
  - Automation
tags:
  - research
  - ai-agent
  - deep-research
  - multi-agent
  - rag
  - knowledge-graph
  - second-brain
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "04‑Resources/Research"
filename: "[Research] Deep Research Pipeline Architecture for AI Agents"
slug: research-deep-research-pipeline-ai-agents
uid: RES‑AI‑001
moc:
  - [[MOC - AI]]
  - [[MOC - Research]]
parent: []
children:
  - [[[Evergreen] Iterative Research Loop]]
  - [[[Evergreen] Source Verification for AI Agents]]
  - [[[Evergreen] Synthesis vs Retrieval]]
related:
  - [[On‑the‑Go Coding]]
  - [[MOC - Knowledge Hub]]
  - [[MOC - Mobile Friendly Tools]]
  - [[[Project] AI Agent Platform]]
source:
  - "Conceptual architecture based on deep‑research agent patterns"
confidence: medium
reviewed: false
---

# [Research] Deep Research Pipeline Architecture for AI Agents

## Abstract Summary
Deep Research Pipeline คือระบบที่ให้ AI Agent ทำการสืบค้น ตรวจสอบ แยกแยะ สังเคราะห์ และอัปเดตความรู้อย่างวนซ้ำ ไม่ใช่แค่ถามครั้งเดียว แต่เป็นวงจรการสืบสวน เหมาะสำหรับสร้างรายงาน วิจัย และอัปเดต Second Brain

## Research Question
> จะออกแบบไปป์ไลน์วิจัยลึกสำหรับ AI Agent ให้ได้ผลลัพธ์ที่อ้างอิงได้ ตรวจสอบได้ และสามารถเชื่อมเข้ากับ Knowledge Graph ได้อย่างไร?

## Methodology
1. **Query Generation** → Agent แยกคำถามหลักเป็น sub‑questions
2. **Source Retrieval** → ดึงจาก Vault, Web, Vector DB, APIs
3. **Source Evaluation** → ตรวจความน่าเชื่อถือ ความเกี่ยวข้อง วันเวลา
4. **Iterative Exploration** → สร้างคำถามใหม่จากสิ่งที่พบ
5. **Synthesis** → รวมเป็นโครงเรื่อง / รายงาน / Obsidian Notes
6. **Knowledge Graph Update** → สร้าง WikiLinks, Evergreen Notes, MOC
7. **Validation & Review** → มนุษย์หรือ Agent ตรวจและติดธง

## Results (Conceptual)
- Deep Research ไม่เท่ากับ RAG เพียงอย่างเดียว
- ความแม่นยำขึ้นอยู่กับ **Source Verification + Iteration**
- ต้องแยก Retrieval (ค้นหา) ออกจาก Synthesis (สังเคราะห์)
- ต้องบันทึก Trace ของแต่ละขั้นตอน เพื่อให้ตรวจสอบได้
- สามารถเชื่อมกับ [[On‑the‑Go Coding]] เพื่อให้ทำงานได้จากมือถือผ่าน Remote Shell

## Contributions
- ให้กรอบสำหรับสร้าง Deep Research Agent ที่เชื่อมกับ Obsidian Vault
- แยก Evergreen Principles ออกจาก Temporary Research Runs
- เตรียมโครงสร้างสำหรับ Multi‑Agent Orchestration
- เชื่อมเข้ากับ Second Brain และ MOC ระบบ

## Limitations
- ยังไม่มีโค้ดเต็มหรือการทดสอบจริง
- ต้องมี Source Grounding เพื่อลด Hallucination
- ต้องควบคุม Cost / Token Limit
- ต้องแยก "Research Run" ออกจาก "Permanent Knowledge"
- ไม่ได้รับประกันว่าผลลัพธ์เป็นจริง ต้องมีการตรวจสอบจากมนุษย์

## Applications
- สร้างรายงานวิจัย
- อัปเดต Obsidian Vault
- สร้าง MOC ใหม่
- ตรวจสอบเอกสารเทคโนโลยี
- สนับสนุน [[On‑the‑Go Coding]]
- สนับสนุน [[[Project] AI Agent Platform]]

## Evergreen Candidates
- [[[Evergreen] Iterative Research Loop]]
- [[[Evergreen] Source Verification for AI Agents]]
- [[[Evergreen] Synthesis vs Retrieval]]
- [[[Evergreen] Grounded Reasoning]]
- [[[Evergreen] Knowledge Curation vs Knowledge Generation]]

## Related Notes
- [[MOC - AI]]
- [[MOC - Research]]
- [[On‑the‑Go Coding]]
- [[MOC - Knowledge Hub]]
- [[[Project] AI Agent Platform]]
 
 
📄 05‑Knowledge/Evergreen/[Evergreen] Iterative Research Loop.md
 
markdown
  
---
title: "[Evergreen] Iterative Research Loop"
aliases:
  - วงจรวิจัยแบบวนซ้ำ
  - Iterative Inquiry Loop
type: evergreen
status: active
priority: high
icon: "🔁"
color: blue
domain: Research Methodology
topics:
  - Research
  - AI Agents
  - Second Brain
  - Learning
tags:
  - evergreen
  - research
  - iteration
  - ai-agent
  - second-brain
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Evergreen"
filename: "[Evergreen] Iterative Research Loop"
slug: evergreen-iterative-research-loop
uid: EG‑RESEARCH‑001
moc:
  - [[MOC - Research]]
  - [[MOC - AI]]
parent: []
children: []
related:
  - [[[Research] Deep Research Pipeline Architecture for AI Agents]]
  - [[[Evergreen] Source Verification for AI Agents]]
confidence: high
reviewed: false
---

# 🌱 [Evergreen] Iterative Research Loop

## Summary
Iterative Research Loop คือหลักการที่วิจัยไม่ได้จบที่การค้นหาครั้งเดียว แต่เป็นวงจรของการตั้งคำถาม → ค้น → ตรวจ → สังเคราะห์ → ตั้งคำถามใหม่ → ซ้ำอีกครั้ง

## Core Idea
- Principle 1: คำถามที่ดีจะเปลี่ยนไปเมื่อได้รับข้อมูลใหม่
- Principle 2: การวิจัยคือการลดความไม่แน่นอน ไม่ใช่แค่หาคำตอบเร็ว
- Principle 3: ต้องบันทึก Trace เพื่อให้เห็นว่าได้เปลี่ยนความเข้าใจอย่างไร
- Principle 4: Synthesis ต้องแยกออกจาก Source เพื่อป้องกัน Hallucination

## Why It Matters
สำหรับ AI Agent และ Second Brain หากขาด Loop จะกลายเป็นแค่ "Ask Once Summary" แทน Deep Research จริงๆ

## Example
1. คำถามเริ่มต้น: "Multi‑Agent คืออะไร?"
2. ค้นพบ: มีหลาย Pattern
3. คำถามใหม่: "Multi‑Agent vs Single Agent vs RAG ต่างกันอย่างไร?"
4. ตรวจ Source
5. สังเคราะห์เป็น Evergreen Note
6. สร้าง MOC
7. กลับมาตรวจซ้ำเมื่อมีข้อมูลใหม่

## Key Insight
Deep Research คือ **Stateful Inquiry** ไม่ใช่ Stateless Prompting

## Related Notes
- [[[Research] Deep Research Pipeline Architecture for AI Agents]]
- [[[Evergreen] Source Verification for AI Agents]]
- [[[Evergreen] Synthesis vs Retrieval]]
- [[MOC - Research]]
 
 
📄 00‑System/MOCs/MOC - Research.md (เวอร์ชันเต็มพร้อม Dataview)
 
markdown
  
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
 
 
📊 Dataview — Evergreen Notes ด้าน Research
 
dataview
  
TABLE
  status AS "สถานะ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Research]])
  AND type = "evergreen"
SORT updated DESC
 
 
📊 Dataview — ทุกโน้ตใน MOC นี้
 
dataview
  
TABLE
  type AS "ประเภท",
  status AS "สถานะ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Research]])
SORT type ASC
 
 
Research Notes
 
- [[[Research] Deep Research Pipeline Architecture for AI Agents]]
 
Evergreen Notes
 
- [[[Evergreen] Iterative Research Loop]]
- [[[Evergreen] Source Verification for AI Agents]]
- [[[Evergreen] Synthesis vs Retrieval]]
 
Related MOCs
 
- [[MOC - AI]]
- [[MOC - Knowledge Hub]]
- [[MOC - Obsidian Second Brain]]
 
Learning Path
 
Beginner
 
- เรียนวงจรการวิจัยพื้นฐาน
- ฝึกเขียน Research Question
- แยก Source vs Synthesis
 
Intermediate
 
- สร้าง Deep Research Workflow ด้วย AI
- สร้าง Trace Log สำหรับแต่ละ Research Run
- แปลง Research เป็น Evergreen Notes
 
Advanced
 
- สร้าง Multi‑Agent Research Pipeline
- เชื่อมกับ Vector DB / RAG
- สร้าง Automated Knowledge Graph Maintenance
 
plaintext
  

## 📄 00‑System/MOCs/MOC - AI.md (เพิ่มส่วน Deep Research)
```markdown
---
title: "MOC - AI"
aliases:
  - MOC - ปัญญาประดิษฐ์
  - AI Knowledge Map
type: moc
status: active
priority: high
icon: "🤖"
color: purple
domain: Artificial Intelligence
topics:
  - AI
  - LLM
  - AI Agents
  - RAG
  - Multi‑Agent
tags:
  - moc
  - ai
  - llm
  - agent
  - rag
  - dataview
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "MOC - AI"
slug: moc-ai
uid: MOC‑AI‑001
moc:
  - [[MOC - Knowledge Hub]]
parent: []
children:
  - [[[Research] Deep Research Pipeline Architecture for AI Agents]]
related:
  - [[MOC - Research]]
  - [[MOC - Knowledge Hub]]
  - [[[Project] AI Agent Platform]]
confidence: high
reviewed: false
---

# 🗺️ MOC - AI

## Overview
แผนที่สำหรับจัดการความรู้ด้าน AI, LLM, AI Agents, Multi‑Agent, RAG และ Deep Research เพื่อนำไปใช้กับ Second Brain และ Automation

## Core Concepts
- [[[Evergreen] Iterative Research Loop]]
- [[[Evergreen] Grounded Reasoning]]
- [[[Evergreen] Synthesis vs Retrieval]]

## 📊 Dataview — Research ด้าน AI
```dataview
TABLE
  status AS "สถานะ",
  confidence AS "ความมั่นใจ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - AI]])
  AND type = "research"
SORT updated DESC
 
 
📊 Dataview — Evergreen ด้าน AI
 
dataview
  
TABLE
  status AS "สถานะ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - AI]])
  AND type = "evergreen"
SORT updated DESC
 
 
Research Notes
 
- [[[Research] Deep Research Pipeline Architecture for AI Agents]]
 
Related MOCs
 
- [[MOC - Research]]
- [[MOC - Knowledge Hub]]
- [[MOC - DevOps]]
 
Learning Path
 
Beginner
 
- เข้าใจ LLM Basics
- เข้าใจ RAG
- เข้าใจ Agent Basics
 
Intermediate
 
- เข้าใจ Deep Research Pipeline
- เข้าใจ Multi‑Agent Patterns
- สร้าง Traceable Research Workflow
 
Advanced
 
- สร้าง Production‑Ready Agent Platform
- เชื่อมกับ Knowledge Graph
- ตั้งค่า Cost Control + Validation Loop
 
plaintext
  

# 🧠 โครงสร้างที่ได้แล้ว
✅ [[[Research] Deep Research Pipeline Architecture for AI Agents]]
✅ [[[Evergreen] Iterative Research Loop]]
✅ [[MOC - Research]] พร้อม Dataview
✅ [[MOC - AI]] พร้อมเชื่อมโยง
✅ เชื่อมกับ [[On‑the‑Go Coding]] ตาม Linked Mentions ที่เห็นในภาพ
✅ สอดคล้องกับ PARA / Zettelkasten / Second Brain
✅ แยก Temporary Research Run ออกจาก Evergreen Principles

## 📌 สิ่งที่ควรสร้างต่อ
- [[[Evergreen] Source Verification for AI Agents]]
- [[[Evergreen] Synthesis vs Retrieval]]
- [[[Evergreen] Grounded Reasoning]]
- [[[Project] AI Agent Platform]] เต็มฉบับ
- [[Dataview Query สำหรับ Research Dashboard]]
- [[Journal Template for Weekly Research Review]]

💡 หมายเหตุ: จากภาพเป็นเพียงชื่อโน้ต + Linked Mentions เท่านั้น จึงเป็น **Conceptual Research Note** ที่เตรียมไว้สำหรับเติมเนื้อหาจริงเพิ่มเติมได้

ต้องการให้ผมสร้าง **[[[Evergreen] Source Verification for AI Agents]] ต่อเลยหรือไม่ครับ?**