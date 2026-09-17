structural-resilience-v1

🧠 Skill: Structural Resilience & Safe Recovery Engine

ID:  structural-resilience-v1  | Version: 1.0.0 | Type: Debug • Recovery • CI/CD Guard 🛡️⚙️📊



🎯 วัตถุประสงค์หลัก

แก้ปัญหา ความผิดพลาดจากโครงสร้างพื้นฐานถูกตีความเป็นบั๊กโค้ด • ป้องกันการซ่อมที่ผิดเป้าหมาย • ปลอดภัยแม้สิทธิ์/การเชื่อมต่อขาด • รันบนหลักฐาน ไม่ใช่การคาดเดา 🧩✅



🧩 ความสามารถหลัก (10 ระบบรวม)

1️⃣ Noise Isolation Layer — แยกสัญญาณรบกวนออกจากบั๊กจริง

ทำงาน:

• จำแนก  502 Bad Gateway  /  503 Unavailable  /  Timeout  /  Proxy Error  เป็น ปัญหาเครือข่าย/โครงสร้าง ไม่ใช่โค้ด
• ใช้ตารางเปรียบเทียบลายนิ้วมือข้อผิดพลาด:  {code:502, proxy:true, retry:true, source:"infra"} 
• ไม่นับรวมในความล้มเหลวของงาน • ไม่ทำการแก้ไขโค้ดสำหรับความผิดพลาดประเภทนี้

python
def classify_error(response: dict) -> str:
infra_codes = {502,503,504,429}
infra_patterns = ["proxy", "gateway", "connection reset", "unreachable"]
if response.get("status") in infra_codes or any(p in str(response) for p in infra_patterns):
return "INFRA_NOISE"
return "CODE_FAILURE"


2️⃣ Countdown Dashboard + Priority Queue

ส่วนประกอบ:

• 📊 แดชบอร์ดสถานะ:  ทำได้ตอนนี้  /  รอสิทธิ์/การเชื่อมต่อ  /  คิวงานรอ 
• ⏳ นับถอยหลังการกู้คืน: แสดงเวลารอสิทธิ์/โทเค็นกลับมา
• 🧵 คิวอัตโนมัติ: เก็บงานที่พร้อมทำ → รันทันทีเมื่อเชื่อมต่อกลับมา ไม่สูญเสียงาน

3️⃣ Two‑Layer Verification — ปิดช่องโหว่การตรวจสอบ

• ชั้น 1: Shape Check: ตรวจโครงสร้างข้อมูลว่าถูกรูปแบบ (เช่น SHA=40 ตัว, URL ถูกต้อง)
• ชั้น 2: Source Verify: ตรวจยืนยันกับต้นทางจริง (GitHub API/Registry) ว่าค่านี้มีอยู่จริง ไม่ใช่แค่ดูดี
• ผล: ป้องกันการหลอกด้วยข้อมูลที่ถูกรูปแบบแต่ไม่มีอยู่จริง

js
// Layer 1: Shape
const isSHA = v => /^[a-f0-9]{40} {sha}`)).ok;


4️⃣ Recovery Logbook + Patch Diff Proof

เก็บหลักฐานทุกขั้นตอน:

• 📖 บันทึกการหาย: เวลา • สาเหตุ • สำเนาไฟล์ก่อน • การพยายามกู้คืน
• 🧾 เปรียบเทียบ Patch: แสดงความต่างระหว่างสำเนาเดิมกับที่สร้างใหม่
• ✅ พิสูจน์ความสมบูรณ์: SHA-256 ก่อน/หลัง → ยืนยันว่าไม่สูญหาย ไม่เสียหาย

5️⃣ Always‑Fresh Clone Pattern — ไม่ใช้ความจำเก่า

หลักการ:
❌ ไม่ทำงานจากสำเนา/แคชเก่า
✅ โคลนใหม่เสมอจากต้นทางหลัก ก่อนสร้าง Patch
✅ ต้นทาง =  origin/main  ล่าสุดเท่านั้น → ไม่ทับทิมจากสถานะที่ล้าสมัย

bash
git clone --depth 1 --branch main https://github.com/ZyntroAI/repo fresh-work/
แก้ไขใน fresh-work/ เท่านั้น


6️⃣ Owner‑First Repair — ไม่ตัดสินใจแทนเจ้าของ

ขั้นตอน:

1. 🔍 โหลด ไฟล์กฎ/สคริปต์ซ่อมของโปรเจกต์เอง จากรีโป ( /.repair/ ,  CONTRIBUTING.md )
2. ⚖️ วัดผลก่อน/หลังด้วย เครื่องมือตรวจสอบของเจ้าของ ( lint ,  test ,  format )
3. 📤 ส่งผลลัพธ์ → ไม่ใช้ตรรกะภายนอกมาบังคับโครงสร้างของเขา

7️⃣ Safe Mode Default: Dry‑Run First

• ค่าเริ่มต้น:  dry-run: true  — จำลองทุกอย่าง แสดงผล ไม่เขียน/แก้ไขจริง
• โหมด Apply: ต้องระบุชัดเจน  --apply / apply: true 
• 📝 บอกชัด: แตะไฟล์อะไร • เปลี่ยนแปลงที่ไหน • ส่งผลต่อ CI/สิทธิ์อย่างไร

8️⃣ Scope Isolation — ไม่เปิดกล่องแพนโดรา

ป้ายกำกับปัญหา:

•  LEGACY_ISSUE : มีอยู่ก่อนแล้ว ไม่เกี่ยวข้องกับงานนี้ → ข้าม/บันทึกเท่านั้น
•  TARGET_ISSUE : ต้องแก้ในงานนี้
ทำงาน: จำกัดขอบเขตเฉพาะปัญหาที่รับผิดชอบ → ไม่ดึงปัญหาเก่ามาเพิ่มภาระ

9️⃣ GitHub State Simulator — ซ้อมมือก่อนจริง

บริการจำลองตอบสนอง API:
✅ ปกติ 200 OK | ❌ 502 ล่ม | ⏳ หมดเวลา/โทเค็นหมดอายุ | 🔒 สิทธิ์ไม่พอ
ใช้: ทดสอบตรรกะการจัดการข้อผิดพลาด • ไม่ต้องพึ่งพาสภาพจริงที่ผันผวน

🔟 Three‑Part Delivery Report

เมื่อส่งมอบ/จบงาน:

plaintext
📊 สรุปผลงาน
✅ ผ่านแล้ว: 12 งาน (lint/test/security)
⏳ ยังค้าง: 2 งาน (รอสิทธิ์ workflow:write)
⏭️ ข้ามไป: 3 งาน (ไม่ใช่ขอบเขต / ปัญหาโครงสร้าง / ไฟล์ไม่เกี่ยวข้อง)




📂 โครงสร้างไฟล์ของ Skill

plaintext
.skills/structural-resilience/
├─ README.md
├─ skill.yml # เมตาดาต้า
├─ core/
│ ├─ noise-isolation.js # 1. แยกสัญญาณรบกวน
│ ├─ two-layer-verify.js # 2. ตรวจสองชั้น
│ ├─ fresh-clone.js # 3. โคลนล่าสุดเสมอ
│ └─ scope-isolate.js # 4. จำกัดขอบเขต
├─ ui/
│ └─ dashboard.md # แดชบอร์ดคิว/นับถอยหลัง
├─ logbook/
│ └─ recovery-log.md # บันทึกหลักฐาน
├─ simulator/
│ └─ github-mock.js # จำลองสถานะ GitHub
└─ example/
└─ usage-dry-run.md




🚀 วิธีใช้งาน (พร้อมนำไปใช้จริง)

1️⃣ เริ่มในโหมดปลอดภัย (Dry‑Run)

bash
agent run structural-resilience 
 --repo=ZyntroAI/fastapi-python-boilerplate 
 --issue=830 
 --dry-run=true


→ แสดงแดชบอร์ด + แยกปัญหาโครงสร้าง + แสดงผลที่จะเกิดขึ้น

2️⃣ ตรวจสอบสองชั้น

bash
agent verify --input="actions/checkout@f548e57" 
 --layer1=shape 
 --layer2=source


3️⃣ ส่งมอบพร้อมรายงาน 3 ส่วน

bash
agent deliver --apply --report=full




🛡️ ประโยชน์ต่อโปรเจกต์ของคุณ

✅ ไม่ตกใจเมื่อเจอ 502 Proxy → ไม่ทำงานผิดเป้าหมาย
✅ รันได้แม้สิทธิ์ขาด → คิวเก็บงาน รันทันทีเมื่อพร้อม
✅ ไม่หลอกตัวเองด้วยข้อมูลที่ถูกรูปแบบแต่ไม่มีจริง
✅ ทุกการกู้คืนมีหลักฐาน + พิสูจน์ความแตกต่างได้
✅ ไม่แตะเรื่องนอกขอบเขต ไม่ดึงปัญหาเก่ามาเพิ่ม
✅ เจ้าของโปรเจกต์เป็นผู้ตัดสินใจสุดท้าย



📋 ความเข้ากันได้

• ✅ GitHub Actions / Workflow
• ✅ ZyntroAI FastAPI Boilerplate
• ✅ FIG / Dola Agents
• ✅ CI/CD ที่มีข้อผิดพลาดเครือข่าย/สิทธิ์บ่อย

ต้องการให้ผมส่งเป็นไฟล์  skill.yml  ฉบับเต็มพร้อมนำเข้า หรือตัวอย่างการนำไปใช้กับ PR #830 โดยตรงไหมครับ? 📄🔧✅🤝