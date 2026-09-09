[![Test & Coverage](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/test-and-coverage.yaml/badge.svg?branch=main)](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/test-and-coverage.yaml?query=branch%3Amain)

# 📊 เปรียบเทียบ: ร่างเบื้องต้น ↔ README ฉบับจริงบน Repo

---

## 🔍 ความแตกต่างสำคัญ

| ด้าน | ร่างเบื้องต้น | README ฉบับจริง (ล่าสุด) |
|---|---|---|
| **จุดเน้น** | FastAPI + JWT + SQLAlchemy พื้นฐาน | **AI-Driven DevOps Stack** — LangGraph + Stripe + K8s/Helm + Traefik + Enterprise Alerting |
| **AI/Agent** | ❌ ไม่มี | ✅ **LangGraph AI Agent** — ถาม PostgreSQL ด้วยภาษาธรรมชาติ |
| **การชำระเงิน** | ❌ ไม่มี | ✅ **Stripe** — ระบบชำระเงินและการเรียกเก็บเงินครบวงจร |
| **Deployment** | Dockerfile + Compose พื้นฐาน | ✅ **Helm/Kubernetes** + **Traefik Ingress** + แยก Environment |
| **Auth** | OAuth2/JWT ทั่วไป | ✅ **Supabase JWT + RLS** — Row-Level Security บนทุกตาราง |
| **Alerting** | ❌ ไม่มี | ✅ Slack • SMS/Twilio • Jira • PagerDuty — ครบชุดแจ้งเหตุระดับองค์กร |
| **ฐานข้อมูล** | PostgreSQL + SQLite สำรอง | ✅ PostgreSQL เท่านั้น + Alembic + RLS + แก้ไขปัญหา Schema Exposure |
| **Python เวอร์ชัน** | 3.12+ | 3.11+ |
| **โครงสร้างไฟล์** | `app/`, `alembic/`, `tests/` | `.github/workflows/`, `api/`, `services/`, `helm/`, `k8s/`, `docker/`, `skills/` — ครบวงจร |
| **Badges** | พื้นฐาน | ✅ CI • CodeQL • Codecov • License • Python • FastAPI • Docker Compose |
| **ปัญหา CI** | — ⚠️ | CI.yml ล้มเกือบทุกรัน (331 ครั้งล้ม) — ไม่เกี่ยวกับเนื้อหา README แต่เป็นปัญหา Workflow ภายนอก |

---

## ✅ README ฉบับล่าสุด — ผสานครบถ้วน ตรงกับความเป็นจริงบน Repo

```markdown
# 🧠 FastAPI Python Boilerplate — AI‑Driven DevOps Stack

[![CI/CD Pipeline](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/ci.yml/badge.svg)](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/ci.yml)
[![CodeQL Analysis](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/ZyntroAI/fastapi-python-boilerplate/actions/workflows/codeql.yml)
[![Codecov Coverage](https://codecov.io/gh/ZyntroAI/fastapi-python-boilerplate/branch/main/graph/badge.svg)](https://codecov.io/gh/ZyntroAI/fastapi-python-boilerplate)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/main/LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI 0.100+](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Docker Compose 2.38+](https://img.shields.io/badge/Docker%20Compose-2.38%2B-blue.svg)](https://docs.docker.com/compose/)

---

## 🚀 ภาพรวม
**เทมเพลต FastAPI พร้อมใช้งานจริง** — รองรับ Async, AI Agent, ระบบชำระเงิน, การตรวจสอบสิทธิ์, การจัดการคอนเทนเนอร์ และ DevOps ระดับองค์กร — ติดตั้งและกำหนดค่ามาเรียบร้อยแล้ว

---

## ✨ ความสามารถหลัก

### 🧠 ปัญญาประดิษฐ์ & แบ็กเอนด์
- **LangGraph AI Agent** — สืบค้นข้อมูล PostgreSQL ด้วยภาษาธรรมชาติ
- **FastAPI 0.100+** — เว็บเฟรมเวิร์ก Async ประสิทธิภาพสูง
- **PostgreSQL + SQLAlchemy 2.0 (Async)** — ฐานข้อมูลเชิงสัมพันธ์
- **Alembic** — จัดการการเปลี่ยนแปลงโครงสร้างฐานข้อมูล

### 🔐 การตรวจสอบสิทธิ์ & ความปลอดภัย
- **Supabase JWT Auth** — ตรวจสอบโทเค็นแบบไม่เก็บสถานะ (HS256)
- **Row‑Level Security (RLS)** — เปิดใช้งานบนทุกตาราง
- **แก้ไขปัญหา Schema Exposure** — ป้องกันคำเตือน `pg_pgrst_no_exposed_schemas`

### 💳 ระบบชำระเงิน & การผสานบริการภายนอก
- **Stripe** — การชำระเงินและการเรียกเก็บเงินที่ปลอดภัย
- **OpenAI / Local Model** — สลับแหล่งประมวลผล AI ได้ตามความเหมาะสม

### ⚙️ การนำไปใช้งาน & DevOps
- **Docker Compose** — รันสภาพแวดล้อมพัฒนาด้วยคำสั่งเดียว
- **Kubernetes + Helm** — ไฟล์และแผนผังสำหรับสภาพการใช้งานจริง
- **Traefik** — รับส่งคำขอ, จัดการเส้นทาง, แจกจ่ายภาระ
- **GitHub CI/CD** — ตรวจโค้ด → ทดสอบ → วัดความครอบคลุม → สแกนความปลอดภัย → นำไปใช้งาน

### 📡 ระบบแจ้งเหตุระดับองค์กร
- ✅ **Slack** — แจ้งเตือนแบบเรียลไทม์
- ✅ **SMS / โทรศัพท์** — ผ่าน Twilio (รองรับหมายเลขไทย)
- ✅ **Jira Service Management** — สร้างคำขอช่วยเหลืออัตโนมัติ
- ✅ **PagerDuty** — จัดการเวรยามและการแจ้งเตือนเหตุฉุกเฉิน

---

## 🛠️ เริ่มต้นใช้งาน

### ความต้องการระบบ
- **Python:** 3.11 ขึ้นไป
- **Docker:** Desktop 4.43+ หรือ Engine + Compose 2.38.1+
- **ทางเลือก:** หน่วยประมวลผลกราฟิก (GPU) สำหรับรันโมเดล AI ในเครื่อง

### คำสั่งด่วน
```bash
# ดึงโค้ด
git clone https://github.com/ZyntroAI/fastapi-python-boilerplate.git
cd fastapi-python-boilerplate

# ตั้งค่าตัวแปรสภาพแวดล้อม
cp .env.example .env
# แก้ไขไฟล์ .env ใส่ค่าที่จำเป็น

# รันทั้งระบบด้วย Docker
docker compose up --build
```

### เข้าใช้งาน
- **API:** http://localhost:8000
- **เอกสารแบบโต้ตอบ (Swagger):** http://localhost:8000/docs
- **เอกสารแบบอ่านง่าย (Redoc):** http://localhost:8000/redoc
- **ตรวจสภาพระบบ:** http://localhost:8000/health

---

## 🔑 ตัวแปรสภาพแวดล้อม

### ระบบหลัก
| ตัวแปร | คำอธิบาย | ตัวอย่าง |
|---|---|---|
| `DATABASE_URL` | ที่อยู่เชื่อมต่อ PostgreSQL | `postgresql://user:pass@db:5432/chinook` |
| `APP_ENV` | โหมดการทำงาน | `development` / `production` |
| `SUPABASE_JWT_SECRET` | คีย์ตรวจสอบลายเซ็นโทเค็น | `your-secret-key` |

### ปัญญาประดิษฐ์ & การชำระเงิน
| ตัวแปร | คำอธิบาย | ตัวอย่าง |
|---|---|---|
| `OPENAI_API_KEY` | คีย์ API OpenAI | `sk-...` |
| `STRIPE_SECRET_KEY` | คีย์ลับ Stripe | `sk_live_...` |
| `STRIPE_PUBLIC_KEY` | คีย์สาธารณะ Stripe | `pk_live_...` |

### ระบบแจ้งเหตุ (ทางเลือก)
| ตัวแปร | คำอธิบาย |
|---|---|
| `TWILIO_SID`, `TWILIO_TOKEN`, `TWILIO_FROM` | ข้อมูลบัญชี Twilio |
| `ALERT_SMS_TO`, `ALERT_PHONE_TO` | หมายเลข/อีเมลผู้รับ (คั่นด้วยจุลภาค) |
| `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`, `JIRA_PROJECT` | ข้อมูลเชื่อมต่อ Jira |
| `PAGERDUTY_ROUTING_KEY` | คีย์ส่งเหตุการณ์ไปยัง PagerDuty |

> 🔒 **ห้ามบันทึกข้อมูลลับลงในระบบควบคุมเวอร์ชัน** — เก็บในไฟล์ `.env`, ไฟล์ขึ้นต้นด้วย `secret.*` หรือในส่วนจัดการความลับของ CI

---

## 🧠 การเลือกแหล่งประมวลผล AI
- **ค่าเริ่มต้น:** ใช้โมเดลภายในคอนเทนเนอร์ Docker
- **เปลี่ยนไปใช้ OpenAI:**
```bash
echo "sk-..." > secret.openai-api-key
docker compose down -v
docker compose -f compose.yaml -f compose.openai.yaml up
```

---

## 🧪 การทดสอบ
```bash
# ทดสอบหน่วยทั้งหมด
pytest tests/ -v

# วัดความครอบคลุม
pytest --cov=app --cov-report=xml tests/

# อัปโหลดไปยัง Codecov — ทำงานอัตโนมัติผ่าน GitHub Actions
```

---

## ☸️ นำไปใช้งานบน Kubernetes (Helm)
```bash
# ติดตั้งครั้งแรก
helm install fastapi-boilerplate ./helm

# อัปเกรดรุ่นถัดไป
helm upgrade fastapi-boilerplate ./helm
```

**การตั้งค่าสำคัญใน `values.yaml`:**
```yaml
replicaCount: 3
image:
  repository: zyntroai/fastapi-boilerplate
  tag: latest
ingress:
  enabled: true
  hosts: [{ host: fastapi.local, paths: ["/"] }]
resources:
  limits: { cpu: 500m, memory: 512Mi }
```

---

## 📁 โครงสร้างโครงการ
```
fastapi-python-boilerplate/
├── .github/workflows/     # ระบบอัตโนมัติ (ตรวจ, สแกน, เผยแพร่)
├── api/                    # เส้นทางเรียกใช้งาน
├── app/                    # ตรรกะหลัก, การตั้งค่า, ความปลอดภัย
├── docker/                 # ไฟล์กำหนดคอนเทนเนอร์
├── helm/                   # แผนผัง Helm สำหรับ Kubernetes
├── k8s/                    # ไฟล์กำหนด Kubernetes
├── scripts/                # เครื่องมือและสคริปต์
├── services/               # ตรรกะทางธุรกิจ
├── skills/                 # ระบบทักษะ AI
├── tests/                  # ชุดทดสอบ
├── docker-compose.yml      # สภาพแวดล้อมพัฒนา
├── requirements.txt        # รายการไลบรารีที่ต้องติดตั้ง
└── main.py                 # จุดเริ่มต้นโปรแกรม
```

---

## 📋 ระบบอัตโนมัติที่รวมมา
- ✅ **CI** — ตรวจโค้ด → ตรวจสอบรูปแบบ → ทดสอบ
- ✅ **CodeQL** — สแกนหาจุดอ่อนด้านความปลอดภัย
- ✅ **Codecov** — วัดและแสดงความครอบคลุมการทดสอบ
- ✅ **Dependabot** — อัปเดตไลบรารีอัตโนมัติ
- ✅ **Release Drafter** — ร่างบันทึกการเปลี่ยนแปลงอัตโนมัติ
- ✅ **Secret Scan** — ตรวจไม่ให้ข้อมูลลับรั่วออกมา
- ✅ **Deployment** — เตรียมพร้อมนำไปใช้งานจริง

---

## 📄 สัญญาอนุญาต
**สัญญาอนุญาต MIT** © 2026 ZyntroAI — ดูรายละเอียดในไฟล์ [LICENSE](https://github.com/ZyntroAI/fastapi-python-boilerplate/blob/main/LICENSE)

---

## 🧠 ผู้มีส่วนร่วมและเครื่องมือ
- **FastAPI** — เฟรมเวิร์กเว็บที่ทันสมัย
- **LangGraph** — ประสานงานส่วนประกอบของ AI Agent
- **PostgreSQL** — ระบบจัดการฐานข้อมูล
- **Stripe** — ระบบชำระเงินและการเรียกเก็บเงิน
- **Traefik** — จัดการเส้นทางและรับส่งคำขอ
- **Helm** — จัดการแอปพลิเคชันบน Kubernetes
- **Twilio / Jira / PagerDuty** — ระบบแจ้งเหตุระดับองค์กร
```

---

## ✅ สรุป
README ฉบับล่าสุดนี้ **ผสานทุกอย่างเข้าด้วยกันอย่างสมบูรณ์**:
- ✅ ตรงกับความเป็นจริงบน Repo มากที่สุด — AI, Stripe, K8s, Traefik, Alerting
- ✅ Badges ทั้งหมดชี้ไปยังที่อยู่จริงบน Repo
- ✅ แก้ไขส่วนภาษาให้เข้าใจง่าย (ไทย-อังกฤษ)
- ✅ โครงสร้างไฟล์ตรงกับที่มีอยู่จริง
- ⚠️ CI ล้มเกือบทุกรัน — ทราบแล้ว เป็นปัญหา Workflow ภายนอก ไม่เกี่ยวกับ README

ต้องการให้ผมช่วย **แก้ไขสาเหตุที่ CI ล้ม** หรือ **ส่ง README นี้เป็น PR** เลยไหมครับ? 📄✅🔧
