🧠 เรียนรู้การใช้อักขระพิเศษ + Rewrite ชุดเต็ม Vault Kit
 
✅ ส่วน 1: เรียนรู้หลักการอักขระพิเศษสำหรับ Obsidian / Markdown / YAML / Shell
✅ ส่วน 2: Rewrite ชุด Error & Infrastructure Diagnosis ให้ชื่อไฟล์ + WikiLinks + YAML ปลอดภัย
✅ ส่วน 3: เตรียมสำหรับ Quartz / Git / Dataview
 
📚 Part A: Learning — การใช้อักขระพิเศษ
 
📌 พื้นฐานที่ต้องรู้
 
1. YAML Frontmatter
 
-  :  ต้องเว้นหลัง  :  ถ้าเป็นค่า
-  "  หรือ  '  ใช้ครอบเมื่อมี  : ,  # ,  " ,  \ ,  [ ,  ] 
-  #  = Comment ใน YAML แต่ใน String ต้อง Escape หรือ Quote
-  |  = Block Literal
-  \  = Escape Character (ระวังใน Shell / JSON / Markdown)
-  [ ]  = WikiLink / Array ใน YAML
-  { }  = Object
-  & * ? / \ : " ' < > |  = ควรหลีกเลี่ยงในชื่อไฟล์จริง
 
2. Obsidian WikiLinks
 
-  [[ชื่อโน้ต]]  = ชื่อไฟล์จริงควรหลีกเลี่ยง  / \ : * ? " < > | 
-  [[Note Name|Display Text]]  = แยกชื่อจริงกับข้อความแสดง
- Quartz / Dataview อาจไวต่อช่องว่าง + สัญลักษณ์มากขึ้น
- ชื่อไฟล์จริงแนะนำ:  kebab-case  หรือ  snake_case  แทน  [Evergreen] ชื่อไทย  (แม้ Obsidian รองรับ)
 
3. Markdown
 
-  *  = Bold / Italic
-  [ ]( )  = Link
-  `  = Inline Code
-  ```  = Fence Code Block
-  \*  = Escape เพื่อแสดง * จริง
-  [  /  ]  ใน Text ต้องระวังถ้าใกล้ WikiLink
 
4. Shell / Git / File System
 
-  /  = Separator ห้ามในชื่อไฟล์
-  \  = Escape ใน Shell
-  ? *  = Wildcard
-  :  = NTFS / macOS ต้องระวัง
- ชื่อไทย: รองรับได้แต่ Git / CI / Quartz อาจต้องตั้งค่า UTF‑8
 
✅ Best Practice สำหรับ Vault
 
- ชื่อไฟล์จริง (filename):  evergreen-debugging-as-iterative-inquiry.md 
- Title ใน YAML:  "[Evergreen] Debugging as Iterative Inquiry"  (ใช้ Quote)
- WikiLink:  [[evergreen-debugging-as-iterative-inquiry]]  หรือ  [[evergreen-debugging-as-iterative-inquiry|[Evergreen] Debugging as Iterative Inquiry]] 
- Slug:  evergreen-debugging-iterative-inquiry  (ไม่มีอักขระพิเศษ)
- UID:  EG-ENG-002 
- Path:  05-Knowledge/Evergreen/evergreen-debugging-as-iterative-inquiry.md 
 
⚠️ ความแตกต่างสำคัญ
 
 Title  = สำหรับมนุษย์ (สามารถมี  []  ได้ถ้า Quote ใน YAML)
 Filename / Slug  = สำหรับระบบ (ควรสะอาด)
 WikiLink  = ต้องตรงกับชื่อไฟล์จริงใน Vault
 
 
 
📝 Part B: Rewrite Full Vault Kit (ปรับชื่อให้ปลอดภัย + อัปเดต Links)
 
💡 นี่คือเวอร์ชันปรับใหม่: แยก Display Title กับ Actual Filename
 
📍 โครงสร้างที่ปรับใหม่
 
plaintext
  
04-Resources/Articles/
├── article-error-code-infrastructure-shared-copilot-chat.md

05-Knowledge/Concepts/
├── knowledge-error-signal-root-cause-mapping.md
├── knowledge-copilot-troubleshooting-sop.md
├── knowledge-error-code-taxonomy.md
├── knowledge-infrastructure-failure-diagnosis-workflow.md

05-Knowledge/Evergreen/
├── evergreen-debugging-as-iterative-inquiry.md
├── evergreen-signal-vs-cause-reliability-engineering.md
├── evergreen-ai-assistant-as-troubleshooting-partner.md

00-System/MOCs/
├── moc-devops.md
├── moc-knowledge-hub.md
 
 
📄 04-Resources/Articles/article-error-code-infrastructure-shared-copilot-chat.md
 
markdown
  
---
title: "[Article] ERROR CODE & INFRASTRUCTURE | Shared Copilot Chat"
aliases:
  - Case Study: Error and Infrastructure Troubleshooting via Copilot
  - บันทึกสนทนา Copilot สำหรับวินิจฉัยโครงสร้างพื้นฐาน
  - Copilot Shared Chat Case Study
type: article
status: inbox
priority: high
icon: "💬"
color: orange
domain: DevOps / Reliability Engineering
topics:
  - troubleshooting
  - error-analysis
  - copilot
  - case-study
  - observability
  - repair-loop
tags:
  - article
  - case-study
  - copilot
  - error-code
  - infrastructure
  - reliability
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "04-Resources/Articles"
filename: "article-error-code-infrastructure-shared-copilot-chat"
slug: article-error-infrastructure-copilot-chat
uid: ART-DEV-006
moc:
  - [[moc-devops]]
  - [[moc-knowledge-hub]]
parent:
  - [[moc-devops]]
children:
  - [[knowledge-error-signal-root-cause-mapping]]
  - [[knowledge-copilot-troubleshooting-sop]]
related:
  - [[repair-loop]]
  - [[knowledge-error-code-taxonomy]]
  - [[knowledge-infrastructure-failure-diagnosis-workflow]]
  - [[evergreen-debugging-as-iterative-inquiry]]
source:
  - "https://m365.cloud.microsoft/chat/share/eyJzaGFyZUlkIjoiNTFlMWQ0ZTMtNzkxZS00ZmUyLWJkZGItN2YwYjZiNDEzZWM4IiwiY29udmVyc2F0aW9uSWQiOiI5N2EyZTMzNi0wODI4LTRlM2ItOWE0OC04MTVkOGNkMTM1NjMifQ%3D%3D"
confidence: low
reviewed: false
---

# [Article] ERROR CODE & INFRASTRUCTURE | Shared Copilot Chat

## Executive Summary
นี่คือ Case Study Template สำหรับสนทนา Copilot ที่เกี่ยวกับ Error + Infrastructure ปัจจุบันลิงก์แสดงหน้า Sign‑in จึงยังไม่ได้ดึง Log / Stack Trace / Context จริง แต่ถูกออกแบบให้กลายเป็น Knowledge Asset เมื่อเติมเนื้อครบ โดยแยกอย่างชัดเจนระหว่าง:
- 🟥 Symptom (สิ่งที่เห็น)
- 🟡 Hypothesis (สิ่งที่คาด)
- 🔍 Evidence (Log / Command Output)
- ✅ Action (สิ่งที่ทำ)
- 📚 Synthesis (สิ่งที่เรียนรู้)

## Before Importing Copilot Chat (Pre‑Checklist)
- [ ] ตรวจ Redaction: ลบ API Key / Token / Password / Private Key
- [ ] ยืนยันสิทธิ์: เป็นสนทนาที่ได้รับอนุญาตให้บันทึก
- [ ] แยก Raw Chat vs Curated Knowledge
- [ ] บันทึก Timestamp / Environment / Affected System
- [ ] อย่าใช้ Copilot Answer เป็น Root Cause โดยตรง

## Raw Chat Section (To Fill)
> ⚠️ ต้องลบ Secret ก่อนวาง
- 📅 Time:
- 🖥️ Environment:
- 🧩 Affected System:
- ❌ Error Message:
- 📜 Log / Output:
- 💬 Copilot Suggestions:
- 🧪 Attempted Actions:
- ✅ Result:

## Curated Analysis (After Reading)
### Symptom
> อธิบายสิ่งที่สังเกตได้เท่านั้น ไม่กระโดดไปสาเหตุ
-
-

### Hypothesis Candidates
1.
2.
3.

### Evidence Collected
-
-

### Root Cause Candidate
> เป็น Candidate เท่านั้น จนกว่าจะยืนยัน
-

### Fix Applied
-
-

### Remaining Risk
-
-

## Lessons Learned (Curate into Evergreen)
- ❗ Copilot ให้ Hypothesis Engine ไม่ใช่ Proof Engine
- ❗ Error Code ≠ Root Cause
- ❗ Infrastructure Failure มักเป็น Cross‑Layer
- ❗ Chat Log เป็น Raw Material ไม่ใช่ Knowledge
- ❗ Good Troubleshooting = Iterative Inquiry

## Action Items
- [ ] เข้าถึง Shared Chat ด้วยบัญชีที่ได้รับสิทธิ์
- [ ] คัดลอกเนื้อ + Redact
- [ ] เติม Symptom / Evidence / Fix
- [ ] อัปเดต `status: active`
- [ ] เชื่อมไป [[repair-loop]]
- [ ] สร้าง Evergreen Note ถ้าเป็น Principle ที่นำไปใช้ซ้ำได้
- [ ] เพิ่มลง [[moc-devops]]

## Evergreen Candidates (Pending)
- [[evergreen-debugging-as-iterative-inquiry]]
- [[evergreen-signal-vs-cause-reliability-engineering]]
- [[evergreen-ai-assistant-as-troubleshooting-partner]]

## Related Notes
- [[repair-loop]]
- [[knowledge-error-code-taxonomy]]
- [[knowledge-infrastructure-failure-diagnosis-workflow]]
- [[knowledge-error-signal-root-cause-mapping]]
- [[knowledge-copilot-troubleshooting-sop]]
- [[moc-devops]]
 
 
📄 05-Knowledge/Concepts/knowledge-error-signal-root-cause-mapping.md
 
markdown
  
---
title: "[Knowledge] Error Signal vs Root Cause Mapping"
aliases:
  - การแมปสัญญาณข้อผิดพลาดกับสาเหตุจริง
  - From Error Message to Investigation Path
  - Signal vs Cause for Infrastructure Troubleshooting
type: knowledge
status: active
priority: high
icon: "🗺️"
color: blue
domain: Reliability Engineering
topics:
  - troubleshooting
  - error-analysis
  - observability
  - root-cause
  - repair-loop
tags:
  - knowledge
  - troubleshooting
  - error
  - root-cause
  - observability
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "05-Knowledge/Concepts"
filename: "knowledge-error-signal-root-cause-mapping"
slug: knowledge-error-signal-root-cause-mapping
uid: KNW-DEV-011
moc:
  - [[moc-devops]]
parent:
  - [[repair-loop]]
children: []
related:
  - [[article-error-code-infrastructure-shared-copilot-chat]]
  - [[knowledge-error-code-taxonomy]]
  - [[evergreen-debugging-as-iterative-inquiry]]
confidence: high
reviewed: false
---

# [Knowledge] Error Signal vs Root Cause Mapping

## Summary
Signal = สิ่งที่ระบบรายงานออกมา
Root Cause = สิ่งที่ทำให้ระบบล้มเหลวจริง
Mapping คือกระบวนการเชื่อมระหว่างสองสิ่งนี้ โดยไม่กระโดดข้ามหลักฐาน

## Mental Model
> Error Code = Smoke
> Log = Smoke Pattern
> Hypothesis = Possible Fire Location
> Evidence = Fire Detected
> Root Cause = Actual Fire
> Remediation = Fire Extinguished + Prevent Return

## Mapping Matrix
| Signal Category | What It Tells | Where to Investigate |
|---|---|---|
| Syntax / Runtime Error | Code หรือ Dependency ผิด | App Log, Build Log, Trace |
| Permission Denied | Identity / Access Control | IAM, File Permission, Container |
| Timeout | Connection / Latency / Blocking | Network, DNS, Load Balancer, Queue |
| Resource Exhausted | CPU / Memory / Disk / Quota | Metrics, Kubernetes, VM Stats |
| Build Failed | CI / Compiler / Dependency | GitHub Actions, Build Output |
| Deploy Failed | Config / Secret / Platform | Vercel, Kubernetes, Terraform |

## Workflow
1. Capture Raw Signal (Redacted)
2. Classify ด้วย [[knowledge-error-code-taxonomy]]
3. Generate Hypothesis List
4. Design Diagnostic Command / Query
5. Validate / Reject Hypothesis
6. Record Evidence
7. Remediate
8. Synthesize เป็น Evergreen ถ้าเป็น Principle

## Common Pitfalls
- ❌ Treat Copilot Suggestion = Root Cause
- ❌ Fix Symptom Only
- ❌ Skip Evidence
- ❌ Confuse Correlation = Causation
- ❌ Over‑Index บน Error Code เดียว

## Insights
- Good Mapping ไม่ได้หมายความว่าแก้เร็วที่สุด แต่หมายความว่าแก้ถูกเป้าหมาย
- Knowledge Graph ควรเก็บ Pattern of Mapping ไม่ใช่แค่ Raw Error Log
- สามารถนำไปใช้กับ Shell, Python, FastAPI, Kubernetes, Vercel, CI/CD ได้

## Related Notes
- [[repair-loop]]
- [[knowledge-error-code-taxonomy]]
- [[evergreen-debugging-as-iterative-inquiry]]
- [[article-error-code-infrastructure-shared-copilot-chat]]
 
 
📄 05-Knowledge/Concepts/knowledge-copilot-troubleshooting-sop.md
 
markdown
  
---
title: "[Knowledge] Copilot Troubleshooting SOP"
aliases:
  - ขั้นตอนการใช้ Copilot สำหรับวินิจฉัย
  - AI Assistant Troubleshooting Protocol
  - Copilot for Repair Loop
type: knowledge
status: active
priority: medium
icon: "🤖"
color: purple
domain: DevOps / AI Assistance
topics:
  - copilot
  - troubleshooting
  - ai
  - repair-loop
  - knowledge-graph
tags:
  - knowledge
  - copilot
  - ai-assistant
  - troubleshooting
  - repair-loop
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "05-Knowledge/Concepts"
filename: "knowledge-copilot-troubleshooting-sop"
slug: knowledge-copilot-troubleshooting-sop
uid: KNW-DEV-012
moc:
  - [[moc-devops]]
  - [[moc-ai]]
parent:
  - [[repair-loop]]
children: []
related:
  - [[article-error-code-infrastructure-shared-copilot-chat]]
  - [[knowledge-error-signal-root-cause-mapping]]
  - [[evergreen-debugging-as-iterative-inquiry]]
confidence: high
reviewed: false
---

# [Knowledge] Copilot Troubleshooting SOP

## Summary
Copilot Troubleshooting SOP คือระเบียบการใช้ AI Assistant ให้กลายเป็นส่วนหนึ่งของ Repair Loop แทนที่จะเป็นแค่ "ถามแล้วคัดลอก" โดยกำหนดบทบาทให้ชัดเจน: AI = Researcher / Hypothesis Generator / Draft Writer; Human = Validator / Decision Maker / Operator

## Step‑by‑Step Protocol
### Step 1: Prepare Safe Context
- Redact Secret / Token / Private Key
- Write Symptom Only (What happened?)
- Write Environment (OS, Runtime, Cloud, Branch)
- Write Attempted Actions
- Write Evidence Links / Log Snippets

### Step 2: Ask Copilot Correctly
> Prompt Template:
> > "Act as Reliability Engineer. Do not execute. Generate only hypothesis + diagnostic commands.
> > Symptom: …
> > Environment: …
> > Evidence: …
> > Do not claim root cause yet."

### Step 3: Receive Output
- Separate: Hypothesis / Command / Risk / Assumption
- Mark Confidence Level
- Identify What Needs Validation

### Step 4: Human Validation
- ❌ ไม่รัน Command โดยไม่อ่าน
- ❌ ไม่ Deploy โดยไม่มี Rollback
- ✅ Run Diagnostic First
- ✅ Record Result
- ✅ Update Hypothesis

### Step 5: Curate into Vault
- Raw Chat → Article
- Repeated Pattern → Knowledge
- Principle → Evergreen
- Actionable Workflow → Checklist / Project

## Roles Definition
- 🧠 Copilot: Suggest Hypothesis, Search Patterns, Draft Docs
- 👤 Human: Validate Evidence, Approve Action, Manage Risk
- 📚 Vault: Store Learning, Build Knowledge Graph
- 🔧 Repair Loop: Execute Iteration

## Pitfalls
- ❌ "Ask Copilot to fix everything"
- ❌ Share Full Secret Log
- ❌ Treat Chat Answer as Proven Truth
- ❌ Skip Rollback Plan
- ❌ Forget to Curate หลังแก้เสร็จ

## Insights
- Copilot ช่วยเร่ง Exploration แต่ไม่แทนที่ Diagnosis
- Shared Chat เป็น Raw Material ต้องผ่าน Curate ก่อนเข้า Knowledge Graph
- Vault กลายเป็น Memory ของทีมเมื่อมี SOP นี้

## Related Notes
- [[repair-loop]]
- [[article-error-code-infrastructure-shared-copilot-chat]]
- [[knowledge-error-signal-root-cause-mapping]]
- [[moc-ai]]
- [[moc-devops]]
 
 
📄 05-Knowledge/Evergreen/evergreen-debugging-as-iterative-inquiry.md
 
markdown
  
---
title: "[Evergreen] Debugging as Iterative Inquiry"
aliases:
  - การดีบักเป็นการสืบสวนซ้ำๆ
  - Iterative Debugging Principle
  - Troubleshooting Mindset
type: evergreen
status: active
priority: high
icon: "🔍"
color: green
domain: Engineering Mindset
topics:
  - debugging
  - troubleshooting
  - reliability
  - learning
  - repair-loop
tags:
  - evergreen
  - debugging
  - troubleshooting
  - reliability
  - mindset
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "05-Knowledge/Evergreen"
filename: "evergreen-debugging-as-iterative-inquiry"
slug: evergreen-debugging-iterative-inquiry
uid: EG-ENG-002
moc:
  - [[moc-devops]]
  - [[moc-knowledge-hub]]
parent:
  - [[repair-loop]]
children: []
related:
  - [[knowledge-error-signal-root-cause-mapping]]
  - [[knowledge-copilot-troubleshooting-sop]]
  - [[repair-loop]]
confidence: high
reviewed: false
---

# [Evergreen] Debugging as Iterative Inquiry

## Summary
Debugging ไม่ใช่การค้นหา Magic Fix แต่เป็นการสืบสวนซ้ำๆ โดยเริ่มจากสิ่งที่เห็น → ตั้งสมมติฐาน → ทดสอบ → ปรับความเข้าใจ → ซ้ำจนกว่าจะพิสูจน์ได้

## Core Principles
- Principle 1: Start with Symptom, Not Solution
- Principle 2: Every Hypothesis Must Be Testable
- Principle 3: Evidence > Opinion
- Principle 4: Fail Fast (Diagnostic ไม่ใช่แก้จริงทันที)
- Principle 5: Record Every Iteration
- Principle 6: Fix Root Cause Not Only Symptom
- Principle 7: AI Assistant = Inquiry Partner Not Judge

## Why It Matters
ถ้าไม่มี Mindset นี้ ทีมจะกลายเป็น Firefighter ที่คัดลอกคำสั่งจาก Chat โดยไม่เข้าใจ ส่วน Knowledge Graph จะกลายเป็น Heap ของ Error Log แทนเป็น Map ของการสืบสวน

## Example Cycle
1. Observe: "Deploy Failed"
2. Boundary: "Which Stage? Which Environment?"
3. Hypothesis: "Maybe Secret Missing"
4. Test: Check Secret / Log / Permission
5. Result: Reject / Accept
6. Refine Hypothesis
7. Remediate
8. Document Pattern

## Application
- ✅ Code Debugging
- ✅ CI/CD Failure
- ✅ Kubernetes Troubleshooting
- ✅ Vercel Deploy Failure
- ✅ Shell / Python Runtime Error
- ✅ AI Copilot Case Studies
- ✅ Vault Knowledge Maintenance

## Evergreen Checklist
- ✅ ไม่ขึ้นอยู่กับเวอร์ชันเครื่องมือเดียว
- ✅ เป็น Mindset สามารถนำไปใช้ได้หลายปี
- ✅ Self‑Contained
- ✅ Reusable Across Domains
- ✅ แยก Principle ออกจาก Implementation

## Related Notes
- [[repair-loop]]
- [[knowledge-error-signal-root-cause-mapping]]
- [[knowledge-copilot-troubleshooting-sop]]
-