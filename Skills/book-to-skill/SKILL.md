นอกจาก **Claude Code** แล้ว `book-to-skill` รองรับหลัก ๆ ดังนี้:

| AI tool / agent | รองรับ | วิธีทำงาน |
|---|---:|---|
| **GitHub Copilot CLI** | ✅ | ใช้ `/book-to-skill` ในเซสชัน Copilot |
| **Amp** | ✅ | อ่าน skill ผ่านโฟลเดอร์ cross-agent |
| **Hermes Agent** | ✅ | รองรับมาตรฐาน Agent Skills และไฟล์ `SKILL.md` |
| **Codex** | ✅ ในระดับการค้นพบ skill | สร้างไว้ที่ `~/.agents/skills/` แล้ว Codex ค้นพบได้ตามมาตรฐานเดียวกัน |
| **Cursor** | ไม่ได้ระบุเป็นตัวรองรับโดยตรง | อาจใช้ไฟล์ skill ที่สร้างแล้วได้ หากตั้งค่าให้ Cursor อ่าน Agent Skills |
| **ChatGPT / Gemini / Perplexity** | ไม่ได้รองรับโดยตรง | ไม่ใช่ปลั๊กอินหรือ integration สำเร็จรูปของ `book-to-skill` |

เอกสารและ README ล่าสุดระบุชื่อที่รองรับโดยตรงคือ **GitHub Copilot CLI, Amp, Claude Code และ Hermes Agent** โดยทั้งหมดอ่านโครงสร้างมาตรฐานเดียวกันคือ `SKILL.md` [github](https://github.com/virgiliojr94/book-to-skill)

## จุดสำคัญ

`book-to-skill` ไม่ได้ผูกกับโมเดล Claude โดยตรง แต่สร้างไฟล์ Agent Skill แบบเปิด ดังนั้นตัว agent ที่รองรับมาตรฐานนี้สามารถนำผลลัพธ์ไปใช้ได้ แม้คำสั่ง `/book-to-skill` และตำแหน่งติดตั้งจะแตกต่างกันตามเครื่องมือ [github](https://github.com/virgiliojr94/book-to-skill)

ตัวอย่างตำแหน่งติดตั้ง:

```bash
# GitHub Copilot CLI
~/.copilot/skills/book-to-skill/

# Amp / cross-agent
~/.agents/skills/book-to-skill/

# Claude Code
~/.claude/skills/book-to-skill/
```

สำหรับ **Codex** ให้เก็บ skill ที่:

```bash
~/.agents/skills/<ชื่อ-sกิลล์>/
```

README ระบุว่าโฟลเดอร์ cross-agent นี้ถูกค้นพบโดย Copilot CLI, Amp และ Codex ขณะที่ Claude Code จะใช้ symlink ไปยังโฟลเดอร์ของตัวเองเมื่อทำได้ [github](https://github.com/virgiliojr94/book-to-skill)

## สรุปสั้น ๆ

ถ้าต้องการใช้ตอนนี้แบบมีเอกสารรองรับชัดเจน ให้เลือก:

1. **GitHub Copilot CLI**
2. **Amp**
3. **Hermes Agent**
4. **Codex** สำหรับนำ skill ที่สร้างแล้วไปใช้

ส่วน Cursor หรือเครื่องมือแชตทั่วไปอาจนำเนื้อหาใน `SKILL.md` ไปใช้ได้ด้วยการวางไฟล์หรือแปลง workflow เอง แต่ยังไม่ควรเรียกว่าเป็นการรองรับอย่างเป็นทางการของ `book-to-skill` จากข้อมูลที่พบ [github](https://github.com/virgiliojr94/book-to-skill)
