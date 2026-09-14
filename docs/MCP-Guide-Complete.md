# คู่มือแก้ไขปัญหา & การติดตั้ง MCP

> Model Context Protocol (MCP) — Troubleshooting & Setup Guide
> รหัสเอกสาร: **MCP-DOC-2026-0912** · วันที่: 12 กันยายน 2026
> ผู้จัดทำ: ZyntroAI/zyntromedia

---

## เอกสารนี้ใช้ทำอะไร

คู่มือนี้รวบรวม **3 ปัญหาที่พบบ่อยที่สุด** ในการติดตั้งและใช้งาน MCP บนเครื่องนักพัฒนา
พร้อมขั้นตอนแก้ทีละขั้น สคริปต์ตรวจสอบอัตโนมัติ และแบบฟอร์มบันทึกผล

ใช้คู่กับ:

- [AI Agent Security & DevSecOps 2026](./knowledge-ai-agent-security-devsecops-2026.md) — trust tier T1–T4
- [gh CLI Reference](./github-cli-gh-reference.md) — คำสั่ง GitHub CLI
- `deliverables/agent-security-suite/` — MCP client ตัวอย่าง (`agent_security_suite/mcp_client.py`)

---

## สารบัญปัญหา

| รหัส | ปัญหา | อาการที่เห็น | ระดับ |
| --- | --- | --- | --- |
| [MCP-ERR-001](#mcp-err-001--แก้สิทธิ์-google-cloud-adc) | สิทธิ์ Google Cloud ADC | `Could not automatically determine credentials` | สูง |
| [MCP-ERR-002](#mcp-err-002--ติดตั้ง-runtime-nodejs--dart--go--แก้-path) | Runtime หาย (Node/Dart/Go) | `command not found`, server ไม่ start | สูง |
| [MCP-ERR-003](#mcp-err-003--ตั้งค่า-api-key-antimetallovablemobbinwindsor) | API Key ของ third-party | `401 Unauthorized`, `Invalid API key` | กลาง |

**ก่อนเริ่ม:** รันสคริปต์ตรวจสอบเพื่อดูว่าติดปัญหาข้อไหน

```bash
bash scripts/check-mcp-environment.sh
```

---

## MCP-ERR-001 — แก้สิทธิ์ Google Cloud ADC

### อาการ

เมื่อ MCP server ต้องเรียก Google Cloud API (Vertex AI, BigQuery, Secret Manager):

```
google.auth.exceptions.DefaultCredentialsError:
  Could not automatically determine credentials. Please set GOOGLE_APPLICATION_CREDENTIALS
  or explicitly create credentials and re-run the application.
```

### สาเหตุ

ยังไม่มี **Application Default Credentials (ADC)** บนเครื่อง — ไม่ใช่ปัญหาที่ MCP server
แต่เป็นเรื่อง authentication ของ Google Cloud เอง

### ขั้นตอนแก้

**1) ติดตั้ง gcloud CLI** (ถ้ายังไม่มี) — ดู [Install gcloud CLI](https://cloud.google.com/sdk/docs/install)

**2) ล็อกอินแบบ user (สำหรับงาน local)**

```bash
gcloud auth login
gcloud auth application-default login
```

คำสั่งที่สองจะเปิดเบราว์เซอร์และเขียน ADC ไปที่:

- Linux/macOS — `~/.config/gcloud/application_default_credentials.json`
- Windows — `%APPDATA%\gcloud\application_default_credentials.json`

> ⚠️ **ความปลอดภัย:** การล็อกอินต้องทำผ่านเบราว์เซอร์เท่านั้น อย่าส่ง credential,
> refresh token หรือ service-account key ผ่านแชทหรือ commit ลง repo

**3) ตั้งค่า project ให้ตรง**

```bash
gcloud config set project <PROJECT_ID>
gcloud auth application-default set-quota-project <PROJECT_ID>
```

**4) ถ้าใช้ Service Account (สำหรับ CI/server)**

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

⚠️ ไฟล์ service-account.json **ต้องไม่ถูก commit** — ตรวจว่า `.gitignore`
ครอบคลุม path ของ key แล้ว (ดูแนวทาง sandbox/trust tier ใน
[AI Agent Security & DevSecOps 2026](./knowledge-ai-agent-security-devsecops-2026.md))

**5) ทดสอบ**

```bash
python3 -c "import google.auth; c,_=google.auth.default(); print('ADC OK:', c.quota_project_id or c.project_id)"
```

### เช็คลิสต์

- [ ] `gcloud auth application-default login` ผ่าน
- [ ] ไฟล์ ADC อยู่ที่ path ที่ถูกต้อง
- [ ] ตั้ง quota-project แล้ว
- [ ] ไม่มี key ถูก commit ลง repo
- [ ] ทดสอบ `google.auth.default()` ผ่าน

**อ้างอิง:** [ADC docs](https://cloud.google.com/docs/authentication/application-default-credentials)

---

## MCP-ERR-002 — ติดตั้ง runtime (Node.js / Dart / Go) + แก้ PATH

### อาการ

MCP server ไม่ start และ log ขึ้น:

```
Error: command not found: node
Error: command not found: dart
Error: command not found: go
```

หรือ server ที่เขียนด้วย TypeScript/Dart/Go ไม่ทำงาน ทั้งที่ config ถูก

### สาเหตุ

MCP server ส่วนใหญ่เขียนด้วย **Node.js**, บางตัวเป็น **Dart** หรือ **Go** —
ถ้า runtime ไม่ได้ติดตั้ง หรือติดตั้งแล้วแต่ **PATH** ไม่ถูกตั้ง
process ที่ spawn server จะหา executable ไม่เจอ

### ขั้นตอนแก้

**1) ตรวจว่ามีอะไรบ้าง**

```bash
node --version && npm --version
dart --version
go version
```

**2) ติดตั้ง runtime ที่ขาด**

- **Node.js** (แนะนำ LTS) — [nodejs.org/en/download](https://nodejs.org/en/download)
  หลังติดตั้งตรวจ `node -v` และ `npm -v`
- **Dart SDK** — [dart.dev/get-dart](https://dart.dev/get-dart)
- **Go** — [go.dev/dl](https://go.dev/dl/)

**3) ตั้ง PATH ให้ถูก**

| OS | ไฟล์ที่แก้ |
| --- | --- |
| Linux/macOS (bash) | `~/.bashrc` หรือ `~/.bash_profile` |
| Linux/macOS (zsh) | `~/.zshrc` |
| Windows | System Properties → Environment Variables |

```bash
# ตัวอย่าง Linux/macOS
export PATH="$PATH:$HOME/.local/bin"
export PATH="$PATH:/usr/local/go/bin"
export PATH="$PATH:$HOME/.pub-cache/bin"   # Dart global packages
```

จากนั้นโหลดใหม่: `source ~/.zshrc` (หรือเปิด terminal ใหม่)

> ⚠️ **สำคัญ:** MCP client ที่รันเป็น GUI app (เช่น VS Code, app บนเดสก์ท็อป)
> อาจ**ไม่อ่าน** PATH จาก shell profile — ต้องตั้ง PATH ในระดับระบบ
> หรือใช้ path เต็มใน config ของ server (`"command": "/usr/local/bin/node"`)

**4) ตั้งค่า MCP server config**

ใน repo นี้ `.agent/settings.json` ประกาศ `"mcpServers"` พร้อมชี้ `"configPath": "./mcp/servers.json"`

> ⚠️ ไฟล์ `mcp/servers.json` **ยังไม่มีใน repo** — path นี้เป็นที่ที่ควรวางไฟล์ config
> (ไฟล์มักมีความลับ จึงไม่ควร commit) ตรวจว่า client อ่าน path นี้จริงก่อนใช้งาน

```json
{
  "mcpServers": {
    "example-server": {
      "command": "/usr/local/bin/node",
      "args": ["/path/to/server.js"],
      "env": { "API_KEY": "${EXAMPLE_API_KEY}" }
    }
  }
}
```

**5) ทดสอบ**

```bash
which -a node dart go
node -e "console.log('node ok')"
```

### เช็คลิสต์

- [ ] `node`, `npm`, `dart`, `go` รันได้ตามที่โปรเจกต์ต้องใช้
- [ ] PATH ตั้งในไฟล์ที่ shell จริงอ่าน
- [ ] GUI client เห็น runtime (ทดสอบด้วย path เต็มถ้าจำเป็น)
- [ ] `.agent/settings.json` ชี้ `configPath` ถูก
- [ ] MCP server start โดยไม่ error

**อ้างอิง:** [Node.js downloads](https://nodejs.org/en/download) · [Dart SDK](https://dart.dev/get-dart) · [Go downloads](https://go.dev/dl/)

---

## MCP-ERR-003 — ตั้งค่า API Key (Antimetal / Lovable / Mobbin / Windsor)

### อาการ

MCP server start ได้ แต่เรียกเครื่องมือแล้วได้:

```
401 Unauthorized
Invalid API key
Missing required environment variable: <SERVICE>_API_KEY
```

### สาเหตุ

server ต้องใช้ API key ของ third-party แต่ยังไม่ได้ตั้งค่า environment variable
หรือตั้งชื่อไม่ตรงกับที่ server คาดหวัง

### ขั้นตอนแก้

**1) หาชื่อ env var ที่ server ต้องการ**

อ่าน README ของ MCP server นั้น หรือดูใน source (`process.env.X_API_KEY` / `os.environ["X_API_KEY"]`)

**2) ตั้งค่า — ห้าม hardcode**

วิธีที่ปลอดภัย เรียงตามความเหมาะสม:

| วิธี | เหมาะกับ | หมายเหตุ |
| --- | --- | --- |
| OS keychain / secret manager | เครื่องเดี่ยว | ปลอดภัยสุด |
| `.env` ที่ gitignore (ไฟล์ `.env.example` ไว้แชร์ชื่อ) | dev local | ต้องมั่นใจว่า gitignore |
| Environment variable ของ OS | CI/server | ตั้งผ่าน secret store ของ CI |

ตัวอย่าง `.env.example` (commit ได้ — มีแต่ชื่อ ไม่มีค่า):

```bash
ANTIMETAL_API_KEY=
LOVABLE_API_KEY=
MOBBIN_API_KEY=
WINDSOR_API_KEY=
```

**3) ตรวจว่าไม่หลุดเข้า git**

```bash
git check-ignore -v .env          # ต้องมี output
git ls-files | grep -E '^\.env'   # ต้องว่าง
```

> ⚠️ ถ้า key เคยถูก commit ไปแล้ว **ให้ rotate ทันที** — การลบ commit ไม่ได้ลบ
> key ออกจากประวัติ clone ของคนอื่น ใช้ `git-filter-repo` ล้างประวัติถ้าจำเป็น

**4) ทดสอบ**

```bash
# ตรวจว่าตั้งค่าแล้วโดยไม่โชว์ค่า
for v in ANTIMETAL_API_KEY LOVABLE_API_KEY MOBBIN_API_KEY WINDSOR_API_KEY; do
  [ -n "${!v}" ] && echo "$v: set" || echo "$v: MISSING"
done
```

### เช็คลิสต์

- [ ] รู้ชื่อ env var ที่แต่ละ server ต้องใช้
- [ ] ตั้งค่าแล้ว (ไม่ hardcode ในโค้ด)
- [ ] `.env` ถูก gitignore และไม่ถูก track
- [ ] ไม่มี key ในประวัติ git
- [ ] ทดสอบเรียกเครื่องมือของ server ผ่าน

**อ้างอิง:** [MCP specification](https://modelcontextprotocol.io/specification)

---

## เครื่องมือ: `check-mcp-environment.sh`

สคริปต์ตรวจสอบอัตโนมัติสำหรับ 3 ปัญหาข้างต้น อยู่ใน [`scripts/check-mcp-environment.sh`](../scripts/check-mcp-environment.sh)

```bash
# ตรวจทั้งหมด
bash scripts/check-mcp-environment.sh

# เลือกเฉพาะหัวข้อ
bash scripts/check-mcp-environment.sh --gcp
bash scripts/check-mcp-environment.sh --runtimes
bash scripts/check-mcp-environment.sh --keys
```

สคริปต์คืนค่า exit code `0` เมื่อผ่าน และ `1` เมื่อพบปัญหา — ใช้ต่อใน CI ได้

---

## แบบฟอร์มบันทึกผลการตรวจสอบ

คัดลอกตารางนี้ไปใช้เมื่อบันทึกผล (หรือแนบใน PR/issue)

| หัวข้อ | ผลที่ได้ | ผ่าน? | หมายเหตุ |
| --- | --- | --- | --- |
| Google Cloud ADC | | ☐ | |
| Node.js / npm | | ☐ | |
| Dart SDK | | ☐ | |
| Go | | ☐ | |
| PATH ถูกต้อง | | ☐ | |
| API Keys ครบ | | ☐ | |
| MCP server start | | ☐ | |
| `.env` ไม่ถูก track | | ☐ | |

**ผู้ตรวจ:** ______________________ **วันที่:** ____ / ____ / ______

---

## ตัวอย่างบันทึกการดำเนินงาน

> **2026-09-12 — ติดตั้ง MCP บนเครื่อง dev ใหม่**
>
> - พบ MCP-ERR-002: `node` ไม่มี → ติดตั้ง Node.js LTS แล้วเพิ่ม PATH ใน `~/.zshrc`
> - พบ MCP-ERR-001: ADC ยังไม่ล็อกอิน → `gcloud auth application-default login`
> - ตรวจ `.env`: `git check-ignore .env` ผ่าน ไม่มี key ถูก track
> - ผล: `check-mcp-environment.sh` ผ่านทั้งหมด ✅

---

## แหล่งอ้างอิงทางการ

- [Model Context Protocol — specification](https://modelcontextprotocol.io/specification)
- [Google Cloud — Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
- [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Node.js downloads](https://nodejs.org/en/download)
- [Dart SDK](https://dart.dev/get-dart)
- [Go downloads](https://go.dev/dl/)
