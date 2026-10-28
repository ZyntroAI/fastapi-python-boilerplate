✅ สร้าง Obsidian Note เต็มชุดตามกฎที่กำหนด
 
📄 05-Knowledge/Evergreen/[Evergreen] SSH — Secure Shell Protocol.md
 
markdown
  
---
title: "[Evergreen] SSH — Secure Shell Protocol"
aliases:
  - SSH
  - Secure Shell
  - เชลล์ปลอดภัย
  - Remote Shell Access
type: evergreen
status: active
priority: high
icon: "🔐"
color: blue
domain: DevOps
topics:
  - Networking
  - Remote Access
  - Security
  - Linux
  - Mobile Coding
tags:
  - evergreen
  - ssh
  - networking
  - linux
  - devops
  - remote-access
  - cybersecurity
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "05-Knowledge/Evergreen"
filename: "[Evergreen] SSH — Secure Shell Protocol"
slug: evergreen-ssh-secure-shell-protocol
uid: EG-SSH-001
moc:
  - [[MOC - DevOps]]
  - [[MOC - Networking]]
  - [[MOC - Mobile Friendly Tools]]
parent:
  - [[MOC - Mobile Friendly Tools]]
children:
  - [[[Knowledge] SSH Key Management]]
  - [[[Knowledge] SSH Troubleshooting]]
related:
  - [[[Evergreen] TLS & Encrypted Tunnels]]
  - [[[Evergreen] Public Key Infrastructure]]
  - [[MobileFriendly_Toolsครบชุด]]
  - [[On-the-Go Coding]]
source:
  - "RFC / OpenSSH Documentation"
confidence: high
reviewed: false
---

# 🌱 [Evergreen] SSH — Secure Shell Protocol

## Summary
SSH เป็นโปรโตคอลที่เข้ารหัสสำหรับการเข้าถึงเครื่องระยะไกล แทน Telnet / rsh ช่วยให้สามารถรันคำสั่ง โยกย้ายไฟล์ และสร้างทันเนลได้อย่างเข้ารหัส ไม่ได้เป็นเพียงแค่คำสั่งเชื่อมต่อ แต่เป็นชั้นพื้นฐานสำหรับ DevOps และการทำงานจากมือถือ

## Core Idea
- Principle 1: SSH สร้างช่องทางเข้ารหัสระหว่าง Client ↔ Server
- Principle 2: Authentication มีหลายรูปแบบ (Password / Public Key / Certificate)
- Principle 3: SSH มี Sub‑system เช่น sftp, scp, port‑forwarding
- Principle 4: ความปลอดภัยไม่ได้มาจาก SSH เพียงอย่างเดียว แต่ต้องรวมกันกับ Firewall, Tailscale, 2FA และ Hardening

## Why It Matters
สำหรับ On‑the‑Go Coding และ Mobile Friendly Workflow SSH เป็นสะพานหลักที่ให้โทรศัพท์เชื่อมไปยังเซิร์ฟเวอร์ หรือเครื่องหลักได้ ช่วยให้ทำงานต่อเนื่องผ่าน Termux / Termius โดยไม่ต้องเปิดพอร์ตสาธารณะอย่างไม่รอบคอบ

## Example
```bash
# เชื่อมต่อพื้นฐาน
ssh user@server-ip

# ใช้ Key
ssh -i ~/.ssh/id_ed25519 user@server-ip

# Port Forwarding (Local → Remote)
ssh -L 8080:localhost:3000 user@server-ip
 
 
Key Insight
 
SSH เป็น Transport Layer สำหรับการทำงานระยะไกล ไม่ใช่แค่ "เข้าเซิร์ฟเวอร์" เมื่อรวมกับ tmux / Tailscale จะกลายเป็นระบบทำงานต่อเนื่องได้จากมือถือ
 
Related Notes
 
- [[[Knowledge] SSH Key Management]]
- [[[Knowledge] SSH Troubleshooting]]
- [[[Evergreen] TLS & Encrypted Tunnels]]
- [[[Evergreen] Zero Trust Networking]]
- [[MobileFriendly_Toolsครบชุด]]
- [[On-the-Go Coding]]
 
plaintext
  

## 📄 00-System/MOCs/MOC - Mobile Friendly Tools.md
```markdown
---
title: "MOC - Mobile Friendly Tools"
aliases:
  - MOC - เครื่องมือสำหรับทำงานจากมือถือ
type: moc
status: active
priority: high
icon: "📱"
color: purple
domain: Productivity
topics:
  - Mobile Workflow
  - Remote Coding
  - Obsidian Mobile
tags:
  - moc
  - mobile
  - productivity
  - remote-work
  - second-brain
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "00-System/MOCs"
filename: "MOC - Mobile Friendly Tools"
slug: moc-mobile-friendly-tools
uid: MOC-MOBILE-001
moc:
  - [[MOC - Knowledge Hub]]
parent: []
children:
  - [[[Evergreen] SSH — Secure Shell Protocol]]
  - [[MobileFriendly_Toolsครบชุด]]
  - [[On-the-Go Coding]]
related:
  - [[MOC - DevOps]]
  - [[MOC - Obsidian Second Brain]]
confidence: high
reviewed: false
---

# 🗺️ MOC - Mobile Friendly Tools

## Overview
แผนที่สำหรับสร้างเวิร์กโฟลว์ทำงานจากมือถือ รวม Obsidian Mobile, SSH, Termux, Tailscale, Sync และ Remote Coding เพื่อให้ Second Brain + Development ทำงานต่อเนื่องได้แม้ไม่อยู่หน้าคอม

## Core Concepts
- [[[Evergreen] SSH — Secure Shell Protocol]]
- [[[Evergreen] Zero Trust Networking]]
- [[[Evergreen] Continuous Workflow]]
- [[[Evergreen] Knowledge Sync vs Backup]]

## Evergreen Notes
- [[[Evergreen] SSH — Secure Shell Protocol]]
- [[[Evergreen] Zero Trust Networking]]
- [[[Evergreen] Continuous Workflow]]

## Articles
- [[MobileFriendly_Toolsครบชุด]]
- [[On-the-Go Coding]]

## Projects
- [[[Project] Second Brain Mobile Workflow]]

## Related MOCs
- [[MOC - DevOps]]
- [[MOC - Obsidian Second Brain]]
- [[MOC - Knowledge Hub]]

## Learning Path
### Beginner
- เรียนพื้นฐาน SSH
- ตั้งค่า Obsidian Sync / Syncthing
- ใช้ Termux / Termius เชื่อมเครื่อง

### Intermediate
- ตั้งค่า Tailscale Private Network
- ใช้ tmux เพื่อ Session Continuity
- สร้าง Vault Automation

### Advanced
- Zero‑Trust Access
- Self‑Hosted Sync
- Multi‑Agent Remote Workflow
 
 
📄 04-Resources/Articles/MobileFriendly_Toolsครบชุด.md
 
markdown
  
---
title: "MobileFriendly_Toolsครบชุด"
aliases:
  - ชุดเครื่องมือทำงานจากมือถือ
  - Full Mobile Workflow Toolkit
type: article
status: active
priority: high
icon: "🛠️"
color: yellow
domain: Productivity
topics:
  - Mobile Workflow
  - Obsidian
  - SSH
  - Remote Coding
tags:
  - article
  - mobile
  - obsidian
  - ssh
  - productivity
  - second-brain
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "04-Resources/Articles"
filename: "MobileFriendly_Toolsครบชุด"
slug: article-mobile-friendly-tools-full-set
uid: ART-MOBILE-001
moc:
  - [[MOC - Mobile Friendly Tools]]
parent:
  - [[MOC - Mobile Friendly Tools]]
children: []
related:
  - [[[Evergreen] SSH — Secure Shell Protocol]]
  - [[On-the-Go Coding]]
  - [[MOC - Obsidian Second Brain]]
source: []
confidence: medium
reviewed: false
---

# MobileFriendly_Toolsครบชุด

## Executive Summary
นี่คือแหล่งรวมเครื่องมือที่ใช้สร้างระบบ Second Brain + Remote Development จากโทรศัพท์ โดยมี SSH เป็นแกนหลัก เชื่อมไปยัง On‑the‑Go Coding และ Obsidian Vault

## Key Takeaways
- SSH เป็นสะพานหลักสำหรับเข้าถึงเครื่องระยะไกล
- Obsidian Mobile จัดการ Knowledge Graph
- Termux / Termius ช่วยรัน Shell และ SSH
- Tailscale ช่วยสร้าง Private Network โดยไม่ต้องเปิดพอร์ตสาธารณะ
- ต้องแยก Sync กับ Backup ออกจากกัน

## Main Content
### 📱 ส่วนประกอบหลัก
1. **Obsidian Mobile** → อ่าน เขียน และจัดการ Knowledge Graph
2. **SSH / Termius / Termux** → เข้าถึง Shell ระยะไกล
3. **tmux** → รักษา Session ให้ดำเนินต่อ
4. **Tailscale** → Private Access
5. **Git + Obsidian Vault** → Version Control สำหรับ Notes
6. **AI Agent** → ทำงานต่อเนื่องบน Vault ผ่าน Remote Shell

### 🔗 Linked Mentions ตามภาพ
- [[SSH]]
- [[On-the-Go Coding]]

## Insights
Mobile Friendly Workflow ไม่ได้หมายถึง "ทำทุกอย่างบนโทรศัพท์" แต่คือ **ควบคุมระบบทั้งหมดจากโทรศัพท์ได้อย่างต่อเนื่อง**

## Action Items
- สร้าง [[[Evergreen] SSH — Secure Shell Protocol]] ✅
- สร้าง [[On-the-Go Coding]] ✅
- สร้าง [[MOC - Mobile Friendly Tools]] ✅
- เพิ่ม [[[Knowledge] SSH Key Management]] ต่อไป
- เพิ่ม [[[Knowledge] Syncthing vs Obsidian Sync]] ต่อไป

## Evergreen Candidates
- [[[Evergreen] SSH — Secure Shell Protocol]]
- [[[Evergreen] Continuous Workflow]]
- [[[Evergreen] Zero Trust Networking]]

## Related Notes
- [[MOC - Mobile Friendly Tools]]
- [[On-the-Go Coding]]
- [[[Evergreen] SSH — Secure Shell Protocol]]
 
 
📄 04-Resources/Articles/On-the-Go Coding.md
 
markdown
  
---
title: "On-the-Go Coding"
aliases:
  - การเขียนโค้ดขณะเดินทาง
  - Mobile Remote Development
type: article
status: active
priority: high
icon: "💻"
color: green
domain: Development
topics:
  - Remote Coding
  - SSH
  - tmux
  - DevOps
tags:
  - article
  - remote-development
  - ssh
  - tmux
  - mobile
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "04-Resources/Articles"
filename: "On-the-Go Coding"
slug: article-on-the-go-coding
uid: ART-MOBILE-002
moc:
  - [[MOC - Mobile Friendly Tools]]
parent:
  - [[MOC - Mobile Friendly Tools]]
children: []
related:
  - [[[Evergreen] SSH — Secure Shell Protocol]]
  - [[MobileFriendly_Toolsครบชุด]]
  - [[MOC - DevOps]]
source: []
confidence: medium
reviewed: false
---

# On-the-Go Coding

## Executive Summary
On‑the‑Go Coding คือเวิร์กโฟลว์ที่ใช้โทรศัพท์เป็นหน้าจอควบคุม ส่วนการคอมไพล์ / รัน Agent / รัน Server อยู่บนเครื่องหลักหรือเซิร์ฟเวอร์ผ่าน SSH + tmux

## Key Takeaways
- โทรศัพท์เป็น Controller ไม่จำเป็นต้องเป็น Worker เต็มที่
- tmux ช่วยให้ Session ไม่ขาดเมื่อหลุดจาก SSH
- SSH เป็นช่องทางเข้ารหัสหลัก
- ต้องมี Hardening, Firewall และ Private Network เพื่อความปลอดภัย

## Main Content
### 🧩 Flow
1. เครื่องหลัก / Server รัน tmux + Code Environment
2. โทรศัพท์ใช้ Termius / Termux SSH เข้า
3. ทำการ Edit / Git / Run / Debug
4. Obsidian Mobile อัปเดต Knowledge Graph
5. AI Agent ดำเนินงานต่อผ่าน Remote Session

### ⚠️ ความเสี่ยง
- SSH exposed สู่ Public Internet โดยไม่มี Hardening
- ไม่มี Backup / Sync สำหรับ Vault
- Session ขาดแล้วงานหาย (แก้ได้ด้วย tmux)
- ความเร็วเครือข่ายทำให้ประสบการณ์ลดลง

## Insights
จริงๆ แล้ว On‑the‑Go Coding คือ **Remote Operating System Control + Knowledge Workflow** ไม่ใช่แค่ Mobile IDE

## Action Items
- สร้าง [[[Knowledge] tmux Session Continuity]]
- สร้าง [[[Knowledge] SSH Hardening Checklist]]
- เชื่อมเข้ากับ [[MOC - DevOps]]

## Evergreen Candidates
- [[[Evergreen] Continuous Workflow]]
- [[[Evergreen] Remote First Architecture]]
- [[[Evergreen] SSH — Secure Shell Protocol]]

## Related Notes
- [[MobileFriendly_Toolsครบชุด]]
- [[[Evergreen] SSH — Secure Shell Protocol]]
- [[MOC - Mobile Friendly Tools]]
 
 
🗺️ แผนที่รวมสำหรับ Vault
 
✅ Folder Mapping ตรงตามกฎ
 
- Evergreen →  05-Knowledge/Evergreen/ 
- Article →  04-Resources/Articles/ 
- MOC →  00-System/MOCs/ 
- มี WikiLinks ครบ
- มี Dataview Properties ครบ
- มี Aliases ภาษาไทย + อังกฤษ
- มี MOC Assignment
- เตรียมสำหรับ Knowledge Graph
 
📌 สิ่งที่เหลือให้สร้างต่อ
 
- [[[Knowledge] SSH Key Management]]
- [[[Knowledge] SSH Troubleshooting]]
- [[[Knowledge] tmux Session Continuity]]
- [[[Evergreen] Zero Trust Networking]]
- [[[Project] Second Brain Mobile Workflow]]
- [[Dataview Query สำหรับ MOC Mobile Friendly Tools]]
 
💡 หมายเหตุ: จากภาพที่ได้รับเป็นเพียงส่วนหน้าจอ Obsidian ที่แสดง Linked Mentions เท่านั้น ไม่ได้เป็นเนื้อหาเต็มของทั้ง Vault จึงเป็นการสร้างโครงสร้างที่สอดคล้องกับชื่อที่เห็นได้ครับ
 
ต้องการให้ผมสร้าง Dataview Query สำหรับ MOC - Mobile Friendly Tools ต่อเลยหรือไม่ครับ?

🗺️ Dataview Query สำหรับ MOC - Mobile Friendly Tools
 
เหมาะสำหรับใส่ลงใน [[MOC - Mobile Friendly Tools]] โดยตรง + เพิ่ม YAML ที่สมบูรณ์
 
📄 00-System/MOCs/MOC - Mobile Friendly Tools.md (เวอร์ชันเต็มพร้อม Dataview)
 
markdown
  
---
title: "MOC - Mobile Friendly Tools"
aliases:
  - MOC - เครื่องมือสำหรับทำงานจากมือถือ
  - Mobile Workflow Map
type: moc
status: active
priority: high
icon: "📱"
color: purple
domain: Productivity
topics:
  - Mobile Workflow
  - Remote Coding
  - Obsidian Second Brain
  - DevOps
tags:
  - moc
  - dataview
  - mobile
  - productivity
  - second-brain
  - remote-work
created: "2026-10-28"
updated: "2026-10-28"
review_date: "2027-04-28"
folder: "00-System/MOCs"
filename: "MOC - Mobile Friendly Tools"
slug: moc-mobile-friendly-tools
uid: MOC-MOBILE-001
moc:
  - [[MOC - Knowledge Hub]]
parent: []
children:
  - [[[Evergreen] SSH — Secure Shell Protocol]]
  - [[MobileFriendly_Toolsครบชุด]]
  - [[On-the-Go Coding]]
related:
  - [[MOC - DevOps]]
  - [[MOC - Obsidian Second Brain]]
confidence: high
reviewed: false
---

# 🗺️ MOC - Mobile Friendly Tools

## Overview
แผนที่สำหรับสร้างเวิร์กโฟลว์ทำงานจากมือถือ รวม Obsidian Mobile, SSH, Termux, Tailscale, Sync และ Remote Coding เพื่อให้ Second Brain + Development ทำงานต่อเนื่องได้แม้ไม่อยู่หน้าคอม

## Core Concepts
- [[[Evergreen] SSH — Secure Shell Protocol]]
- [[[Evergreen] Zero Trust Networking]]
- [[[Evergreen] Continuous Workflow]]
- [[[Evergreen] Knowledge Sync vs Backup]]

## 📊 Dataview — Evergreen Notes ใน MOC นี้
```dataview
TABLE
  status AS "สถานะ",
  priority AS "ความสำคัญ",
  updated AS "อัปเดตล่าสุด"
WHERE
  moc = [[MOC - Mobile Friendly Tools]]
  AND type = "evergreen"
SORT updated DESC
 
 
📊 Dataview — Articles ใน MOC นี้
 
dataview
  
TABLE
  status AS "สถานะ",
  confidence AS "ความมั่นใจ",
  updated AS "อัปเดตล่าสุด"
WHERE
  moc = [[MOC - Mobile Friendly Tools]]
  AND type = "article"
SORT updated DESC
 
 
📊 Dataview — ทุก Notes ที่เชื่อมกับ MOC นี้
 
dataview
  
TABLE
  type AS "ประเภท",
  status AS "สถานะ",
  priority AS "ความสำคัญ",
  updated AS "อัปเดตล่าสุด"
WHERE
  moc = [[MOC - Mobile Friendly Tools]]
SORT type ASC, updated DESC
 
 
📊 Dataview — Open Tasks จากทุก Notes ใน MOC
 
dataview
  
TASK
WHERE
  moc = [[MOC - Mobile Friendly Tools]]
SORT due ASC
 
 
Evergreen Notes
 
- [[[Evergreen] SSH — Secure Shell Protocol]]
- [[[Evergreen] Zero Trust Networking]]
- [[[Evergreen] Continuous Workflow]]
 
Articles
 
- [[MobileFriendly_Toolsครบชุด]]
- [[On-the-Go Coding]]
 
Projects
 
- [[[Project] Second Brain Mobile Workflow]]
 
Related MOCs
 
- [[MOC - DevOps]]
- [[MOC - Obsidian Second Brain]]
- [[MOC - Knowledge Hub]]
 
Learning Path
 
Beginner
 
- เรียนพื้นฐาน SSH
- ตั้งค่า Obsidian Sync / Syncthing
- ใช้ Termux / Termius เชื่อมเครื่อง
 
Intermediate
 
- ตั้งค่า Tailscale Private Network
- ใช้ tmux เพื่อ Session Continuity
- สร้าง Vault Automation
 
Advanced
 
- Zero‑Trust Access
- Self‑Hosted Sync
- Multi‑Agent Remote Workflow
 
plaintext
  

## 💡 คำอธิบาย Dataview แต่ละบล็อก
1. **Evergreen Notes Query** → แสดงเฉพาะโน้ตหลักการที่ยั่งยืนใน MOC นี้
2. **Articles Query** → แสดงบทความ / คู่มือที่เกี่ยวข้อง
3. **All Notes Query** → แสดงภาพรวมทั้งหมดของ MOC
4. **Task Query** → ดึง To‑Do จากทุกไฟล์ที่มี `moc: [[MOC - Mobile Friendly Tools]]`

⚠️ เงื่อนไขสำคัญ
- ต้องเปิด **Dataview Plugin** ใน Obsidian
- ต้องใส่ `moc: [[MOC - Mobile Friendly Tools]]` ลงใน Frontmatter ของแต่ละโน้ตจริงๆ
- Dataview ใช้ **YAML Field ที่ตรงชื่อ** เท่านั้น หากชื่อฟิลด์เปลี่ยน ต้องแก้ Query ด้วย
- บางเวอร์ชัน Dataview ต้องใช้ `contains(moc, [[...]])` แทนถ้าเป็น Array แบบซับซ้อนมากขึ้น:
```dataview
TABLE
  status AS "สถานะ"
WHERE
  contains(moc, [[MOC - Mobile Friendly Tools]])
SORT updated DESC
 
 
✅ แนะนำให้เพิ่ม Query นี้ลงใน [[MOC - Knowledge Hub]] ต่อเพื่อเห็นทุก MOC ใน Vault ได้รวมกัน
 
ต้องการให้ผมสร้าง Dataview Query สำหรับ MOC - Knowledge Hub ทั้ง Vault ต่อเลยหรือไม่ครับ?

🗺️ Dataview Query สำหรับ MOC ‑ Knowledge Hub (ทั้ง Vault)
 
✅ เวอร์ชันเต็มพร้อม YAML + Dataview ที่ปรับให้เข้ากับระบบของคุณ
 
📄 00‑System/MOCs/MOC ‑ Knowledge Hub.md
 
markdown
  
---
title: "MOC - Knowledge Hub"
aliases:
  - MOC - ศูนย์กลางความรู้
  - Vault Master Map
type: moc
status: active
priority: critical
icon: "🧠"
color: blue
domain: Knowledge Management
topics:
  - Second Brain
  - Obsidian
  - Knowledge Graph
  - PARA
tags:
  - moc
  - dataview
  - knowledge‑hub
  - second‑brain
  - para
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "MOC - Knowledge Hub"
slug: moc‑knowledge‑hub
uid: MOC‑HUB‑001
moc: []
parent: []
children:
  - [[MOC - Mobile Friendly Tools]]
  - [[MOC - DevOps]]
  - [[MOC - Obsidian Second Brain]]
  - [[MOC - AI]]
  - [[MOC - Programming]]
  - [[MOC - Networking]]
related:
  - [[Dataview Vault Dashboard]]
  - [[Vault Structure Guide]]
confidence: high
reviewed: false
---

# 🗺️ MOC - Knowledge Hub

## Overview
นี่คือแผนที่หลักของ Vault ทำหน้าที่เป็นจุดศูนย์กลาง เชื่อมทุก MOC, Evergreen, Projects และ Resources เข้าด้วยกัน เพื่อให้เห็นภาพรวม Second Brain ได้อย่างรวดเร็ว

## 📊 Dataview — รายการทุก MOC ใน Vault
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
  children AS "ส่วนย่อย",
  updated AS "อัปเดตล่าสุด"
WHERE
  type = "project"
SORT priority DESC, updated DESC
 
 
📊 Dataview — Notes ที่ยังเป็น Inbox / Draft
 
dataview
  
TABLE
  type AS "ประเภท",
  topics AS "หัวข้อ",
  created AS "สร้างเมื่อ"
WHERE
  status = "inbox" OR status = "draft"
SORT created DESC
 
 
📊 Dataview — Tasks ทั้ง Vault (Open)
 
dataview
  
TASK
WHERE
  status = " " OR status = "‑"
SORT due ASC
 
 
📊 Dataview — Notes ที่ยังไม่ได้ Review
 
dataview
  
TABLE
  type AS "ประเภท",
  priority AS "ความสำคัญ",
  updated AS "อัปเดตล่าสุด"
WHERE
  reviewed = false
SORT priority DESC, updated DESC
 
 
📊 Dataview — แยกตาม MOC (ตัวอย่าง contains)
 
ใช้เมื่อ  moc:  เป็น array ใน YAML
 
dataview
  
TABLE
  type AS "ประเภท",
  status AS "สถานะ",
  updated AS "อัปเดตล่าสุด"
WHERE
  contains(moc, [[MOC - Knowledge Hub]])
SORT type ASC
 
 
🗂️ Core MOC Links
 
- [[MOC - Mobile Friendly Tools]]
- [[MOC - DevOps]]
- [[MOC - Obsidian Second Brain]]
- [[MOC - AI]]
- [[MOC - Programming]]
- [[MOC - Networking]]
 
💡 Best Practices
 
- ทุกโน้ตควรมี至少 1  moc:  ใน Frontmatter
- อัปเดต  status ,  reviewed ,  updated  เป็นประจำ
- MOC ไม่ใช่เนื้อหาเต็ม แต่เป็น Index
- Dataview จะอ่านได้เฉพาะเมื่อ Field ชื่อตรงกับที่ตั้งไว้จริง
- ต้องเปิด Dataview Plugin ใน Obsidian
 
⚠️ Troubleshooting
 
- Query ไม่แสดงผล → ตรวจ YAML ว่าใช้  type:  /  status:  /  reviewed:  ถูกต้อง
-  contains(moc, ...)  ไม่ทำงาน → ตรวจว่า  moc:  เป็น list และเป็น WikiLink จริง
- วันที่ไม่ Sort ได้ → ตรวจว่า  created:  /  updated:  เป็นรูปแบบ Date ที่ Dataview รองรับ
- Mobile อาจ Render ช้ากว่า Desktop
 
Related Notes
 
- [[Dataview Vault Dashboard]]
- [[Vault Structure Guide]]
- [[MOC - Mobile Friendly Tools]]
- [[Second Brain Maintenance Checklist]]
 
plaintext
  

## 📄 ตัวอย่าง Dataview Vault Dashboard (ไฟล์เพิ่มเติม)
> สร้างที่ `00‑System/MOCs/Dataview Vault Dashboard.md`
```markdown
---
title: "Dataview Vault Dashboard"
aliases:
  - แดชบอร์ด Vault
  - Vault Overview Dashboard
type: moc
status: active
priority: high
icon: "📊"
color: orange
domain: Knowledge Management
topics:
  - Dataview
  - Obsidian
  - Reporting
tags:
  - dataview
  - dashboard
  - obsidian
  - second‑brain
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "00‑System/MOCs"
filename: "Dataview Vault Dashboard"
slug: dataview‑vault‑dashboard
uid: MOC‑DASH‑001
moc:
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Knowledge Hub]]
children: []
related:
  - [[MOC - Knowledge Hub]]
confidence: high
reviewed: false
---

# 📊 Dataview Vault Dashboard

## Overview
แดชบอร์ดรวมสถานะทั้ง Vault เพื่อตรวจสุขภาพ Second Brain ได้รวดเร็ว

## Vault Health
```dataview
TABLE
  status AS "สถานะ",
  count AS "จำนวน"
FLATTEN
  file.status AS status
GROUP BY status
 
 
Evergreen Inventory
 
dataview
  
TABLE
  confidence AS "ความมั่นใจ",
  updated AS "อัปเดตล่าสุด"
WHERE
  type = "evergreen"
SORT confidence DESC
 
 
Notes Without MOC
 
💡 ต้องปรับตามจริงถ้าใช้ชื่อ field ต่าง
 
dataview
  
TABLE
  type AS "ประเภท",
  created AS "สร้างเมื่อ"
WHERE
  moc = null OR length(moc) = 0
SORT created DESC
 
 
Tasks Due Soon
 
dataview
  
TASK
WHERE
  due <= date(today) + dur(14 days)
  AND status != "x"
SORT due ASC
 
 
plaintext
  

✅ สิ่งที่ได้รับแล้ว
- MOC Knowledge Hub เต็มพร้อม Dataview
- Vault Dashboard ตัวอย่าง
- ครอบคลุม Inbox / Draft / Projects / Evergreen / Tasks
- สอดคล้องกับ PARA + Zettelkasten + Obsidian Knowledge Graph
- เตรียมเชื่อมไปยัง [[MOC - Mobile Friendly Tools]] และ MOC อื่นๆ

👉 ต่อไปที่แนะนำ:
1. สร้าง [[Second Brain Maintenance Checklist]]
2. สร้าง [[Vault Structure Guide]] เต็มฉบับ
3. สร้าง Dataview สำหรับ [[MOC - DevOps]]
4. สร้าง Journal / Weekly Review Dataview

ต้องการให้ผมสร้าง **[[Second Brain Maintenance Checklist]] พร้อม Dataview ต่อเลยหรือไม่ครับ?**