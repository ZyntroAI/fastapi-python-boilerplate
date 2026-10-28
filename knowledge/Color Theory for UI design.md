[Evergreen] Color Theory for UI Design Full Obsidian Vault Kit
🎨 [Evergreen] Color Theory for UI Design (เต็ม Obsidian Vault)
สร้างตาม Vault Architecture: Evergreen + YAML + Dataview + WikiLinks + Learning Path + เชื่อมกับ Obsidian Style Settings / CSS / Vault Branding
📄 05‑Knowledge/Evergreen/[Evergreen] Color Theory for UI [Design.md](Design.md)
---
title: "[Evergreen] Color Theory for UI Design"
aliases:
  - ทฤษฎีสีสำหรับ UI
  - Color Theory for Interfaces
  - ระบบสีสำหรับผลิตภัณฑ์ดิจิทัล
  - Color Psychology & Accessibility
type: evergreen
status: active
priority: high
icon: "🎨"
color: purple
domain: UI Design
topics:
  - Color Theory
  - UI Design
  - Design System
  - Accessibility
  - CSS
  - Vault Branding
tags:
  - evergreen
  - color-theory
  - ui
  - design-system
  - accessibility
  - css
  - vault-branding
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Evergreen"
filename: "[Evergreen] Color Theory for UI Design"
slug: evergreen-color-theory-ui-design
uid: EG‑UI‑001
moc:
  - [[MOC - Obsidian Second Brain]]
  - [[MOC - Knowledge Hub]]
parent:
  - [[MOC - Obsidian Second Brain]]
children:
  - [[[Knowledge] Color Codes — Hex RGB HSL OKLCH]]
  - [[[Knowledge] Color Contrast & WCAG]]
  - [[[Knowledge] Design Tokens for Color Palette]]
related:
  - [[[Knowledge] Obsidian Style Settings Plugin]]
  - [[[Knowledge] Obsidian CSS Snippet Authoring for Style Settings]]
  - [[Vault Structure Guide]]
  - [[Second Brain Maintenance Checklist]]
confidence: high
reviewed: false
---

# 🌱 [Evergreen] Color Theory for UI Design

## Summary
Color Theory for UI คือหลักการเลือกและจัดการสีให้สื่อสารได้ชัดเจน อ่านง่าย สอดคล้องกับ Brand และเข้ากับ Dark / Light Mode ไม่ใช่แค่เลือกสีที่สวย แต่เป็น **ภาษาของระบบ** สำหรับปุ่ม ข้อความ สถานะ และความสำคัญ

## Core Idea
- Principle 1: สีต้องสื่อความหมาย ไม่ใช่แค่ความสวย
- Principle 2: Contrast > Aesthetics สำหรับข้อความ
- Principle 3: Lightness เป็นแกนหลักสำหรับ Hierarchy
- Principle 4: Color Blind + Dark Mode ต้องถูกทดสอบ
- Principle 5: Design Token แยก "Meaning" ออกจาก "Hex Value"
- Principle 6: OKLCH / HSL เป็นเครื่องมือ ไม่ใช่จุดหมายปลายทาง

## Why It Matters
สำหรับ Obsidian Vault, Quartz, เว็บไซต์ และ Dashboard การมี Color Theory ที่ชัดเจนทำให้ UI กลายเป็น **Knowledge Interface** ที่ช่วยอ่านข้อมูลได้เร็วขึ้น ถ้าไม่มีหลักการ UI จะกลายเป็นการตกแต่งสุ่ม

## Key Concepts
- [[[Knowledge] Color Codes — Hex RGB HSL OKLCH]]
- [[[Knowledge] Color Contrast & WCAG]]
- [[[Knowledge] Design Tokens for Color Palette]]
- [[[Evergreen] Visual Hierarchy]]
- [[[Evergreen] Accessibility First Mindset]]

## Mental Model
### 🟦 Primary (สีหลัก)
- ใช้สำหรับ Brand, Primary Button, Header Accent
- ไม่ควรใช้ทั่วทั้งหน้า
- ควรมี Shade / Tint สำหรับ Hover / Active

### 🟢 Success / Positive
- สื่อความสำเร็จ, Completed, Healthy
- ไม่ควรพึ่งสีอย่างเดียว ต้องมี Icon / Text

### 🔴 Danger / Error
- สื่อความผิดพลาด, Critical Alert
- ควรมี Contrast เพียงพอ
- ระวัง Color Blind Conflict

### 🟡 Warning
- สื่อเตือน, Pending, Attention
- ควรอยู่ระหว่าง Neutral กับ Danger

### ⚪ Neutral
- เทา, ขาว, ดำ สำหรับ Background / Text
- เป็นโครงกระดูกของ UI
- Lightness คือสิ่งที่สำคัญที่สุด

## Example
> ❌ Bad: Hardcode `#38bdf8` ทุกที่
> ✅ Good:
```css
:root {
  --color-primary: oklch(0.68 0.18 220);
  --color-primary-hover: oklch(0.62 0.18 220);
  --color-text: oklch(0.18 0 0);
  --color-bg: oklch(0.98 0 0);
  --color-error: oklch(0.65 0.22 25);
}
- --color-primary = ความหมาย
- oklch(...) = ค่า
- สามารถเปลี่ยน Theme ได้โดยไม่ต้องแก้ Logic
Color Psychology Notes
- น้ำเงิน = ความน่าเชื่อถือ, เทคโนโลยี, สงบ
- เขียว = ความสำเร็จ, การเติบโต, ความปลอดภัย
- แดง = ความผิดพลาด, ความสำคัญ, ความเตือน
- ส้ม = พลังงาน, ความกระตือรือร้น
- ม่วง = ความคิดสร้างสรรค์, ปัญญาประดิษฐ์
- เทา = ความเป็นกลาง, โครงสร้าง, ความสงบ
⚠️ นี่เป็นแนวโน้ม ไม่ใช่กฎสากล ต้องปรับตาม Brand + Context
Accessibility Rules
- Text Normal: ≥ 4.5:1
- Large Text: ≥ 3:1
- Icon / Decoration: ไม่ต้องเข้มงวดเท่า
- อย่าใช้สีอย่างเดียวเพื่อสื่อสถานะ
- ทดสอบ Dark / Light
- ทดสอบ Color Blind Simulation
- ตรวจหลังเปลี่ยน Palette
Application to Obsidian Vault
- Vault Branding: สีสำหรับ MOC / Evergreen / Project Tags
- Style Settings: ให้ผู้ใช้ปรับ Theme Variables ได้
- Dataview Dashboard: ใช้ Neutral ส่วนใหญ่ ใช้ Accent เฉพาะสิ่งสำคัญ
- Quartz Website: สอดคล้องกับ Design System
- Journal / Review: UI ควรช่วยให้ความคิดชัดเจน ไม่รบกวน
Learning Path
Beginner
- เรียน Hex / RGB / HSL
- เข้าใจ Hue / Saturation / Lightness
- เรียน Contrast พื้นฐาน
- สร้าง Neutral Palette
Intermediate
- เรียน OKLCH
- สร้าง Design Tokens
- สร้าง Dark / Light Palette
- ทดสอบ WCAG
- เชื่อมกับ CSS Snippets
Advanced
- สร้าง Vault Brand System
- สร้าง Theme Config ผ่าน Style Settings
- สร้าง Automated Color Audit
- เชื่อมกับ Quartz / Next.js Design System
- สร้าง Documentation สำหรับทีม
Evergreen Checklist
- ✅ ไม่ขึ้นอยู่กับเวอร์ชันปลั๊กอินเดียว
- ✅ ใช้ได้หลายปี
- ✅ เป็นหลักการ ไม่ใช่แค่ Tutorial
- ✅ สามารถนำไปใช้กับ Obsidian, เว็บ, Dashboard ได้
- ✅ แยก Principle ออกจาก Implementation
Related Notes
- [[[Knowledge] Color Codes — Hex RGB HSL OKLCH]]
- [[[Knowledge] Color Contrast & WCAG]]
- [[[Knowledge] Design Tokens for Color Palette]]
- [[[Knowledge] Obsidian Style Settings Plugin]]
- [[[Evergreen] Visual Hierarchy]]
- [[[Evergreen] Accessibility First Mindset]]
- [[MOC - Obsidian Second Brain]]
## 📄 [[[Knowledge] Color Codes — Hex RGB HSL OKLCH]]
```markdown
---
title: "[Knowledge] Color Codes — Hex RGB HSL OKLCH"
aliases:
  - รหัสสี Hex RGB HSL OKLCH
  - Color Format Reference
  - แปลงรหัสสีสำหรับ CSS
type: knowledge
status: active
priority: medium
icon: "📚"
color: gray
domain: UI Design
topics:
  - Color
  - CSS
  - Design System
  - OKLCH
  - Hex
  - HSL
tags:
  - knowledge
  - color
  - css
  - oklch
  - design-system
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Concepts"
filename: "[Knowledge] Color Codes — Hex RGB HSL OKLCH"
slug: knowledge-color-codes-hex-rgb-hsl-oklch
uid: KNW‑UI‑001
moc:
  - [[MOC - Obsidian Second Brain]]
parent:
  - [[[Evergreen] Color Theory for UI Design]]
related:
  - [[[Evergreen] Color Theory for UI Design]]
  - [[[Knowledge] Color Contrast & WCAG]]
confidence: high
reviewed: false
---

# [Knowledge] Color Codes — Hex RGB HSL OKLCH

## Summary
นี่คือเอกสารอ้างอิงสำหรับรูปแบบสีที่ใช้ใน CSS และ Design System โดย Hex / RGB เป็นการแสดงแสง HSL เป็นวงล้อสี ส่วน OKLCH เป็นรูปแบบที่ใกล้เคียงกับการรับรู้สีของมนุษย์มากขึ้น

## Key Concepts
- Hex = ตัวเลขฐาน 16 สำหรับ Red / Green / Blue
- RGB = ความเข้มของแสง
- HSL = Hue / Saturation / Lightness
- OKLCH = Perceptual Lightness / Chroma / Hue
- Alpha = ความโปร่งแสง
- Design Token = ชื่อความหมาย แยกจากค่าจริง

## Examples
```css
/* Hex */
#38bdf8;
#38bdf880;

/* RGB */
rgb(56,189,248);
rgba(56,189,248,0.5);

/* HSL */
hsl(198,92%,60%);
hsla(198,92%,60%,0.5);

/* OKLCH */
oklch(0.68 0.18 220);
oklch(0.68 0.18 220 / 0.5);
Comparison
Format
Best For
Strength
Weakness
Hex
Legacy CSS
สั้น คุ้นเคย
ยากปรับ Perceptual Lightness
RGB
Programmatic Control
ตรงกับ Channel
ยากเดา Hue
HSL
Basic Palette
เข้าใจวงล้อสี
ไม่สมจริงตามสายตาเสมอ
OKLCH
Modern Design System
ปรับ Lightness ได้ดีขึ้น
ต้องเรียนใหม่
Workflow
1. เลือก Palette ด้วย OKLCH / HSL
2. ตั้งชื่อ Design Token
3. แปลงเป็น Hex / RGB เมื่อจำเป็น
4. ทดสอบ Contrast
5. บันทึกใน Vault Documentation
Insights
- ไม่ต้องใช้ OKLCH ทุกที่ แต่ควรเข้าใจว่ามีอยู่
- ชื่อ Token ต้องสื่อความหมาย ไม่ใช่ชื่อสี เช่น --color-primary ไม่ใช่ --blue-500 เท่านั้น
- Dark Mode ไม่ใช่แค่ Invert Hex แต่เป็นการปรับ Lightness Hierarchy
Related Notes
- [[[Evergreen] Color Theory for UI Design]]
- [[[Knowledge] Color Contrast & WCAG]]
- [[[Knowledge] Design Tokens for Color Palette]]
## 📄 [[[Knowledge] Color Contrast & WCAG]]
```markdown
---
title: "[Knowledge] Color Contrast & WCAG"
aliases:
  - ความคมชัดสีสำหรับ Accessibility
  - WCAG Color Contrast Guide
  - Contrast Ratio for UI
type: knowledge
status: active
priority: high
icon: "👁️"
color: blue
domain: UI Design
topics:
  - Accessibility
  - WCAG
  - Contrast
  - Color
  - UI
tags:
  - knowledge
  - accessibility
  - wcag
  - contrast
  - color
  - ui
created: "2026‑10‑28"
updated: "2026‑10‑28"
review_date: "2027‑04‑28"
folder: "05‑Knowledge/Concepts"
filename: "[Knowledge] Color Contrast & WCAG"
slug: knowledge-color-contrast-wcag
uid: KNW‑UI‑002
moc:
  - [[MOC - Obsidian Second Brain]]
parent:
  - [[[Evergreen] Color Theory for UI Design]]
related:
  - [[[Evergreen] Color Theory for UI Design]]
  - [[[Knowledge] Color Codes — Hex RGB HSL OKLCH]]
  - [[[Evergreen] Accessibility First Mindset]]
confidence: high
reviewed: false
---

# [Knowledge] Color Contrast & WCAG

## Summary
Color Contrast คืออัตราส่วนความสว่างระหว่าง Text กับ Background WCAG เป็นแนวทางเพื่อให้ผู้ใช้อ่านได้แม้สายตาอ่อน หรือใช้ Dark Mode

## Key Rules
- Normal Text (AA): ≥ 4.5:1
- Large Text (AA): ≥ 3:1
- Decorative Text: ไม่ต้องเข้มงวด
- Links / Status: อย่าใช้สีอย่างเดียว
- Dark Mode ต้องตรวจใหม่
- OKLCH Lightness ไม่เท่ากับ Contrast Ratio โดยตรง ต้องใช้เครื่องมือจริง

## Workflow
1. ตั้ง Background Token
2. ตั้ง Text Token
3. ตรวจด้วย WebAIM / Figma Plugin
4. ปรับ Lightness
5. บันทึกใน Vault Documentation
6. ตรวจซ้ำหลังเปลี่ยน Theme

## Example Token Logic
```css
:root {
  --bg: oklch(0.98 0 0);
  --text: oklch(0.18 0 0);
  --muted: oklch(0.45 0 0);
}
นี่เป็นเพียงตัวอย่าง ต้องตรวจ Contrast จริง
Insights
- Contrast เป็นส่วนหนึ่งของ Knowledge Interface
- Vault Documentation ควรบันทึกผลการตรวจ
- Dark Mode ไม่ได้หมายความว่า Contrast ดีขึ้นอัตโนมัติ
- Color Blind + Motion + Font Size เป็นส่วนหนึ่งของ Accessibility ทั้งระบบ
Related Notes
- [[[Evergreen] Color Theory for UI Design]]
- [[[Knowledge] Color Codes — Hex RGB HSL OKLCH]]
- [[[Evergreen] Accessibility First Mindset]]
## 📌 อัปเดต MOC - Obsidian Second Brain
```markdown
children:
  - [[[Evergreen] Color Theory for UI Design]]
  - [[[Knowledge] Color Codes — Hex RGB HSL OKLCH]]
  - [[[Knowledge] Color Contrast & WCAG]]
  - [[[Knowledge] Design Tokens for Color Palette]]
  - [[[Knowledge] Obsidian Style Settings Plugin]]
✅ สิ่งที่ได้แล้ว
- Evergreen Note หลักสำหรับ Color Theory UI
- Knowledge Notes สำหรับ Color Codes + Contrast
- สอดคล้องกับ Vault Structure
- เชื่อมกับ Obsidian Style Settings / CSS / Vault Branding
- มี Learning Path 3 ระดับ
- มี Evergreen Checklist
- เตรียมสำหรับ Quartz / Next.js / Obsidian Theme
📌 สิ่งที่ควรสร้างต่อ
- [[[Knowledge] Design Tokens for Color Palette]] เต็มฉบับ
- [[[Evergreen] Visual Hierarchy]]
- [[[Evergreen] Accessibility First Mindset]]
- [[Vault Branding CSS Template]]
- [[Dark Mode Palette Guide]]
- [[Obsidian Theme Maintenance Checklist]]
- [[Dataview Dashboard UI Guidelines]]
💡 หมายเหตุ: นี่เป็น Knowledge Layer สำหรับ Vault ไม่ได้เป็นไฟล์ CSS จริง แต่เป็นแผนที่สำหรับสร้างระบบสีต่อไป
ต้องการให้ผมสร้าง [[[Knowledge] Design Tokens for Color Palette]] เต็มฉบับต่อเลยหรือไม่ครับ?