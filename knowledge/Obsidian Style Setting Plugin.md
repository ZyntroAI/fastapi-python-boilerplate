📄 Obsidian Note: [Knowledge] Obsidian Style Settings Plugin
 
ตาม Vault Architecture + GitHub README ของ obsidian‑style‑settings (Community Archive)
 
markdown
  
---
title: "[Knowledge] Obsidian Style Settings Plugin"
aliases:
  - Obsidian Style Settings
  - Style Settings Plugin
  - ปลั๊กอินปรับธีม CSS Obsidian
  - CSS Settings Manager Obsidian
type: knowledge
status: draft
priority: medium
icon: "🎨"
color: purple
domain: Obsidian Customization
topics:
  - Obsidian
  - Plugin
  - CSS
  - Theme
  - Snippets
  - UI
  - Vault Branding
tags:
  - knowledge
  - obsidian
  - plugin
  - style-settings
  - css
  - theme
  - snippets
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Concepts"
filename: "[Knowledge] Obsidian Style Settings Plugin"
slug: knowledge-obsidian-style-settings-plugin
uid: KNW‑OBS‑013
moc:
  - [[MOC - Obsidian Second Brain]]
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Obsidian Second Brain]]
children:
  - [[[Knowledge] Obsidian CSS Snippet Authoring for Style Settings]]
related:
  - [[Vault Structure Guide]]
  - [[Second Brain Maintenance Checklist]]
  - [[[Evergreen] Knowledge Graph Edge Types]]
source:
  - "https://github.com/community-archive/obsidian-style-settings"
confidence: high
reviewed: false
---

# [Knowledge] Obsidian Style Settings Plugin

## Summary
Obsidian Style Settings เป็นปลั๊กอิน (ปัจจุบันเป็น Community Archive) ที่ให้ UI แผงเดียวสำหรับปรับตัวแปร CSS ของธีม, Plugin และ Snippet ภายใน Obsidian โดยใช้คอมเมนต์ `/* @settings */` ในไฟล์ CSS เพื่อประกาศเมนูปรับแต่งเองได้

## Key Concepts
- `/* @settings */` = คอมเมนต์ YAML ภายใน CSS เพื่อลงทะเบียนเมนู
- Body Class Toggle = เปิด/ปิด CSS Class บน `<body>`
- CSS Variable Controls = Color / Number / Slider / Text / Select
- Theme + Snippet + Plugin Support = สแกนจาก `.obsidian/themes`, `.obsidian/snippets`, `.obsidian/plugins`
- Archived Status = Community Archive ไม่ได้หมายความว่าใช้ไม่ได้ แต่ควรตรวจความเข้ากันได้กับ Obsidian เวอร์ชันใหม่
- ไม่แก้ Vault Content โดยตรง เป็นเพียงการปรับ UI Rendering

## Details
### 🧩 วิธีการทำงาน
1. ผู้เขียน Snippet / Theme เขียน `/* @settings */` ลงในไฟล์ CSS
2. Style Settings สแกนและสร้าง Settings Pane อัตโนมัติ
3. ผู้ใช้เลือกค่า → เปลี่ยน CSS Variables / Body Classes
4. Plugin ต้องเรียก `app.workspace.trigger("parse-style-settings")` เพื่อแจ้งเมื่อ CSS เปลี่ยน
5. ไม่ได้เป็นธีมเอง แต่เป็น **Manager สำหรับธีมและ Snippet**

### 📌 ตัวอย่าง Syntax จาก Repository
```css
/* @settings
name: My Theme Controls
id: my-theme-controls
settings:
  - id: accent
    title: Accent Color
    type: variable-color
    format: hex
    default: '#007AFF'
  - id: ui-font
    title: UI Font
    type: variable-text
    default: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
*/
 
 
นี่จะสร้างเมนูให้ผู้ใช้ปรับ  --accent  และ  --ui-font  ผ่าน UI ได้
 
🎛️ ประเภทของ Controls ที่รองรับ
 
-  heading  = หัวข้อสำหรับจัดกลุ่ม
-  info-text  = ข้อความอธิบาย (รองรับ Markdown)
-  class-toggle  = เปิด/ปิด Class บน body
-  class-select  = Dropdown สำหรับเลือก Class
-  variable-text  = Text CSS Variable
-  variable-number  = Number CSS Variable
-  variable-number-slider  = Slider สำหรับ Number
-  variable-select  = Dropdown สำหรับ CSS Variable
-  variable-color  = Color Picker
-  variable-themed-color  = Light + Dark สองสี
-  color-gradient  = สร้าง Gradient Variables ระหว่างสองสี
 
⚠️ Archived Note
 
- Repository เป็น  community‑archive  → ไม่มีการพัฒนาใหม่อย่างเป็นทางการใน Repo นี้
- อาจยังทำงานได้บนเวอร์ชันเก่า
- อาจต้องหา Alternative หรือ Maintainer ใหม่สำหรับ Vault Production
- ไม่ควรพึ่งเป็นส่วนหลักถ้า Obsidian อัปเดตใหญ่โดยไม่มีการทดสอบ
- License: GPL‑3.0
 
📂 Vault Path ที่เกี่ยวข้อง
 
-  .obsidian/snippets/*.css 
-  .obsidian/themes/*.css 
-  .obsidian/plugins/*/main.css 
-  05‑Knowledge/Concepts/[Knowledge] Obsidian Style Settings Plugin.md 
-  05‑Knowledge/Concepts/[Knowledge] Obsidian CSS Snippet Authoring for Style Settings.md 
 
Insights
 
- Style Settings ทำให้ Vault Branding กลายเป็น "Configurable System" ไม่ใช่แค่คัดลอก CSS
- ต้องแยก Authoring Snippet กับ User Adjustment ออกจากกัน
- Archive = สัญญาณให้สร้าง Documentation สำหรับ Vault Maintenance
- สามารถเชื่อมกับ [[MOC - Obsidian Second Brain]] เพื่อสร้าง Vault Identity ที่สอดคล้องกัน
- ไม่ใช่ Evergreen Principle โดยตรง แต่เป็น Knowledge สำหรับ Vault Tooling
 
Action Items
 
- ตรวจว่าใช้ได้กับ Obsidian เวอร์ชันปัจจุบัน
- สร้าง [[[Knowledge] Obsidian CSS Snippet Authoring for Style Settings]]
- สร้าง Vault CSS Snippet Template
- เพิ่มลง [[Second Brain Maintenance Checklist]]
- ค้นหา Alternatives ถ้าเกิด Broken หลังอัปเดต Obsidian
 
Related Notes
 
- [[MOC - Obsidian Second Brain]]
- [[MOC - Knowledge Hub]]
- [[Vault Structure Guide]]
- [[[Knowledge] Obsidian CSS Snippet Authoring for Style Settings]]
- [[Second Brain Maintenance Checklist]]
 
plaintext
  

## 📄 [[[Knowledge] Obsidian CSS Snippet Authoring for Style Settings]] (ตัวอย่างเบื้องต้น)
```markdown
---
title: "[Knowledge] Obsidian CSS Snippet Authoring for Style Settings"
aliases:
  - เขียน CSS Snippet สำหรับ Style Settings
  - Style Settings Snippet Guide
type: knowledge
status: draft
priority: low
icon: "✏️"
color: gray
domain: Obsidian Customization
topics:
  - CSS
  - Obsidian
  - Snippets
  - Style Settings
  - Vault Branding
tags:
  - knowledge
  - css
  - obsidian
  - snippets
  - style-settings
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Concepts"
filename: "[Knowledge] Obsidian CSS Snippet Authoring for Style Settings"
slug: knowledge-obsidian-css-snippet-authoring-style-settings
uid: KNW‑OBS‑014
moc:
  - [[MOC - Obsidian Second Brain]]
parent:
  - [[[Knowledge] Obsidian Style Settings Plugin]]
related:
  - [[Vault Structure Guide]]
source:
  - "https://github.com/community-archive/obsidian-style-settings"
confidence: medium
reviewed: false
---

# [Knowledge] Obsidian CSS Snippet Authoring for Style Settings

## Summary
นี่คือคู่มือสำหรับเขียน CSS Snippet ที่มี `/* @settings */` เพื่อให้ Style Settings สร้างเมนูปรับแต่ง UI ของ Vault ได้

## Key Concepts
- คอมเมนต์ต้องอยู่ในไฟล์ CSS ที่โหลดโดย Obsidian
- `id` ต้อง Unique
- `title` = ชื่อที่แสดงใน Settings
- `type` กำหนดว่าเป็น Color / Slider / Text / Toggle
- ค่า Default ต้องถูกต้องตาม Format เช่น Hex ต้องอยู่ใน Quote
- Archived Plugin = ต้องทดสอบหลังอัปเดต Obsidian

## Example Snippet
```css
/* @settings
name: Vault Branding
id: vault-branding
settings:
  - id: vault-accent
    title: Vault Accent Color
    type: variable-color
    format: hex
    default: '#38bdf8'
  - id: note-title-size
    title: Note Title Size
    type: variable-number-slider
    default: 2rem
    min: 1rem
    max: 3rem
    step: 0.1
    format: rem
*/

:root {
  --vault-accent: #38bdf8;
  --note-title-size: 2rem;
}
 
 
Workflow
 
1. สร้างไฟล์ใน  .obsidian/snippets/vault-branding.css 
2. เขียน  /* @settings */  ที่ด้านบน
3. เปิด Style Settings (ถ้ามี)
4. ปรับค่าใน UI
5. รีเฟรช Obsidian
6. บันทึกใน Vault Documentation ว่าเป็น Archived Dependency
 
Insights
 
- Snippet Documentation ควรอยู่ใน Vault ไม่ใช่แค่ไฟล์ CSS
- Vault Branding ควรถูกจัดเป็นส่วนหนึ่งของ Second Brain Identity
- Archived Plugin หมายถึงต้องมี Exit Strategy เมื่อพัง
- ไม่ควรพึ่งสำหรับ Mobile Production โดยไม่ทดสอบก่อน
 
Related Notes
 
- [[[Knowledge] Obsidian Style Settings Plugin]]
- [[Vault Structure Guide]]
- [[MOC - Obsidian Second Brain]]
 
plaintext
  

## 📌 อัปเดต MOC - Obsidian Second Brain
```markdown
children:
  - [[[Knowledge] Obsidian Style Settings Plugin]]
  - [[[Knowledge] Obsidian CSS Snippet Authoring for Style Settings]]
 
 
✅ สิ่งที่ได้แล้ว
 
- สร้าง Knowledge Note สำหรับ Style Settings
- อธิบาย Archived Status
- อธิบาย Syntax หลักจาก GitHub README
- สร้าง Child Note สำหรับ CSS Authoring
- เชื่อมเข้ากับ MOC - Obsidian Second Brain
- เพิ่ม Action Items สำหรับ Vault Maintenance
- สอดคล้องกับ Vault Structure ของคุณ
 
📌 สิ่งที่ควรสร้างต่อ
 
- [[[Evergreen] Vault Identity & Branding]]
- [[[Knowledge] Obsidian Snippet Maintenance Checklist]]
- [[Vault Custom Theme Template]]
- [[Mobile Obsidian UI Customization Guide]]
- [[Obsidian Archived Plugin Risk Checklist]]
 
💡 หมายเหตุ: นี่เป็นการสร้าง Knowledge ตาม README ของ community‑archive เท่านั้น ไม่ได้รับประกันว่าจะทำงานบน Obsidian เวอร์ชันล่าสุดจริง
 
ต้องการให้ผมสร้าง [[[Evergreen] Vault Identity & Branding]] ต่อเลยหรือไม่ครับ?