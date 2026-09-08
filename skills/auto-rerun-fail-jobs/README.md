# 🧠 Skill: Auto-Rerun Fail Jobs — **Failure-Aware CI Recovery Engine**
**ไม่ใช่แค่กดรันซ้ำ — แต่เป็นระบบวิเคราะห์สาเหตุ → ตัดสินใจ → กู้คืน CI แบบชาญฉลาด** 🛡️🔄📉

---

## 📋 ภาพรวมหลักการ
**แก่นของระบบ:** อย่า rerun แบบตาบอด — **แยกประเภทความล้มเหลวก่อน**
- ✅ **Transient:** Network timeout, runner ขัดข้อง → **ลองใหม่ได้**
- ❌ **Permanent:** Code ผิด, Test ล้ม, สิทธิ์ไม่พอ, ความปลอดภัย → **หยุด! ไม่ลองใหม่**

**ทำไมสำคัญ:**
- กดรันซ้ำ 14 ครั้ง ไม่ทำให้ assertion ผิด → ถูก
- ลดค่าใช้จ่าย CI, ประหยัดทรัพยากร
- ลดความสับสน, ชี้เป้าหมายการแก้ไขชัดเจน

---

## 📂 โครงสร้างเต็ม (Standard Skill Layout)
```
skills/
└── auto-rerun-fail-jobs/
    ├── SKILL.md                 # 📄 Manifest, Flow, Policy
    ├── detect/                  # 🔍 ค้นหา + รวบรวมความล้มเหลว
    │   ├── workflow.py          # อ่านสถานะ Workflow
    │   ├── jobs.py              # ดึงรายการ Job ที่ล้ม
    │   ├── steps.py             # วิเคราะห์ Step ที่ล้ม
    │   └── failures.py          # ดึง Log + Fingerprint
    ├── classify/                # 🧩 จำแนกประเภทความล้มเหลว
    │   ├── transient.py         # Network, Runner, Rate Limit
    │   ├── infrastructure.py    # VM, Resource, System
    │   ├── dependency.py        # Package, Image, Registry
    │   ├── test.py              # Assertion, Logic, Test Fail
    │   ├── permission.py        # Token, Scope, Access
    │   ├── security.py          # Secret, Policy, Vulnerability
    │   └── code.py              # Compile, Syntax, Runtime
    ├── decide/                  # ⚖️ ตัดสินใจ: Rerun หรือ หยุด
    │   ├── retry.py              # ควรลองหรือไม่
    │   ├── backoff.py           # คำนวณช่วงเวลา Exponential
    │   ├── budget.py            # ควบคุมจำนวนครั้งรวม
    │   └── policy.py             # กฎการอนุญาต
    ├── execute/                 # 🚀 ทำการ Rerun (Job-Level!)
    │   ├── rerun-job.py         # รันเฉพาะ Job ที่ล้ม
    │   ├── rerun-failed.py      # รันทั้งกลุ่มที่ล้ม
    │   └── rerun-workflow.py    # (สำรอง) รันทั้ง Workflow
    ├── observe/                 # 📊 ติดตาม + บันทึกสถานะ
    │   ├── logs.py               # ดึง + วิเคราะห์ Log
    │   ├── status.py             # อัปเดตสถานะเรียลไทม์
    │   └── result.py             # บันทึกผลลัพธ์
    ├── recover/                 # 🛠️ กู้คืนเมื่อไม่สามารถ Rerun ได้
    │   ├── debug.py              # ส่งให้ Debug-Error Skill
    │   ├── patch.py              # ตรวจสอบ Diff / Patch อัตโนมัติ
    │   └── verify.py             # ตรวจสอบก่อนส่งต่อ
    ├── report/                  # 📝 แจ้งผล + อัปเดตสถานะ
    │   ├── comment.py            # แสดงใน PR Comment
    │   ├── summary.py            # สรุปผลภาพรวม
    │   └── history.py            # บันทึกประวัติการลอง
    └── tests/                   # 🧪 ทดสอบครบทุกส่วน
        ├── test_classification.py
        ├── test_retry_policy.py
        ├── test_budget.py
        ├── test_backoff.py
        └── test_integration.py
```

---

## 📄 SKILL.md — Manifest & Core Spec
```yaml
id: auto-rerun-fail-jobs
name: Failure-Aware CI Recovery Engine
version: 2.0.0
type: devops/ci/automation
description: >
  Intelligent CI rerun: Detect → Fingerprint → Classify → Decide → Rerun Job-Level → Observe → Report
  Never retry permanent failures: code, test, permission, security.
  Save cost, reduce noise, accelerate feedback.

core_flow:
  - GitHub Events → Workflow Failed
  - Detect → Collect Jobs/Logs/Fingerprint
  - Classify → Transient/Infra/Dependency/Test/Code/Permission/Security
  - Decide → Policy + Budget + Backoff
  - Execute → Rerun ONLY failed JOB (not full workflow)
  - Observe → Monitor + Log
  - Recover → Debug/Patch if non-retryable
  - Report → PR Comment + Status Sync

policy:
  max_attempts: 3
  auto_retry:
    transient: true
    infrastructure: true
    rate_limit: true
    dependency: false
    test: false
    code: false
    permission: false
    security: false
  require_approval:
    production_deploy: true
    destructive_job: true
  audit: true
  comments: true
  status_sync: true

permissions:
  required:
    actions: [read, write]      # ✅ สำหรับ Rerun Job
    contents: [read]
  not_required:
    workflows: [write]          # ❌ ไม่ต้องแก้ Workflow

retry:
  strategy: exponential
  initial_sec: 30
  max_sec: 300
  formula: delay = min(initial × 2^attempt, max_sec)
  stop_conditions:
    - success
    - non_retryable
    - budget_exceeded
    - permission_denied
    - security_failure

integration:
  upstream: [github-actions]
  downstream: [debug-error, credential-management, project-status-auto-update, pull-request-comment]
```

---

## 🔄 Core Flow Diagram
```
GitHub Actions: Workflow Failed
        ↓
[Detect] → Collect Jobs/Logs → Fingerprint
        ↓
[Classify] → Transient | Infra | Dependency | Test | Code | Permission | Security
        ↓
[Decide] → Permission Check → Budget → Backoff
        ↓ YES (Transient)
[Execute] → RERUN ONLY FAILED JOB (not full workflow!)
        ↓
[Observe] → Track Status → Log → History
        ↓
[Pass] → ✅ SUCCESS → Update Status + PR Comment
        ↓
[Fail] → ↓
        ├─ Still Retryable? → [Decide] → [Backoff] → [Rerun]
        └─ Non-Retryable / Budget Exceeded → [Recover] → Debug → Patch → Handoff
```

---

## 🧩 Failure Classification & Policy
### `classify/policy.yaml`
```yaml
failure_policy:
  transient:
    patterns: ["timed out", "network error", "connection reset", "runner offline", "rate limit"]
    action: retry
    max_retries: 3
    backoff: exponential

  infrastructure:
    patterns: ["no space left", "resource exhausted", "vm error", "internal server error"]
    action: retry
    max_retries: 2
    backoff: exponential

  dependency:
    patterns: ["package not found", "pull failed", "registry unreachable"]
    action: diagnose
    auto_retry: false

  test_failure:
    patterns: ["assertion failed", "expected vs actual", "test failed"]
    action: debug
    auto_retry: false

  code_failure:
    patterns: ["compile error", "syntax error", "runtime error"]
    action: block
    auto_retry: false

  permission:
    patterns: ["permission denied", "not authorized", "token expired", "insufficient scopes"]
    action: block
    max_retries: 0
    note: "Requires Credential Management / Admin"

  security:
    patterns: ["secret leak", "vulnerability", "policy violation", "blocked"]
    action: quarantine
    max_retries: 0
```

### ✅ Job-Level Rerun (Key Optimization)
**ไม่รันทั้ง Workflow!**
```
Workflow:
├── build  ✅ PASS
├── lint   ✅ PASS
├── test   ❌ FAIL ← ONLY RERUN THIS
├── security ✅ PASS
└── deploy ⏭️ SKIP

❌ Bad: rerun entire workflow
✅ Good: ci.job.rerun("test-python")
```

---

## 🧮 Retry Budget & Algorithm
### `decide/budget.py`
```python
def calculate_backoff(attempt: int, initial=30, max=300):
    """Exponential backoff: delay = min(initial × 2^attempt, max)"""
    return min(initial * (2 ** (attempt - 1)), max)

# ตัวอย่าง:
# ครั้งที่ 1 → 30 วินาที
# ครั้งที่ 2 → 60 วินาที
# ครั้งที่ 3 → 120 วินาที (หยุดเมื่อครบ 3 ครั้ง)
```

### `decide/should_retry.py`
```python
def should_retry(failure_type: str, attempt: int, max_attempts: int, has_permission: bool):
    """Logic: ประเภท + จำนวนครั้ง + สิทธิ์"""
    if not has_permission: return False, "no_permission"
    if attempt >= max_attempts: return False, "budget_exceeded"
    if failure_type in ["test", "code", "permission", "security"]:
        return False, "non_retryable"
    return True, "retry_allowed"
```

---

## 🔐 Permission Integration
**แยกสิทธิ์ชัดเจน:**
- ✅ ต้องการ: `actions:read`, `actions:write` → **สำหรับ Rerun Job**
- ❌ **ไม่ต้องการ:** `workflows:write` → ไม่เกี่ยวข้องกับการรันซ้ำ
- **เชื่อมกับ Credential Management:**
```
auto-rerun → credential.resolve("github") → permission.check("actions:write")
    ↓ YES ↓
RERUN JOB
    ↓ NO ↓
BLOCK → PR Comment: "Missing `actions:write` permission"
```

---

## 📡 Core API
```python
# Detect
ci.fail.detect(run_id)
ci.fail.jobs.failed(run_id)
ci.fail.fingerprint(log_text)

# Classify
ci.fail.classify(fingerprint, logs)
ci.fail.is_retryable(type)

# Decide
ci.retry.should_retry(type, attempt)
ci.retry.plan(attempt)
ci.retry.budget.check(run_id)

# Execute
ci.job.rerun(job_id)                  # ✅ เฉพาะ Job
ci.jobs.rerun_failed(run_id)          # ✅ เฉพาะที่ล้ม
ci.workflow.rerun(run_id)             # ❌ ใช้น้อย

# Observe
ci.retry.status(run_id)
ci.retry.history(job_id)

# Report
ci.pr.comment(run_id, summary)
ci.status.sync(run_id, metadata)
```

---

## 🔗 Integration Ecosystem
### Flow
```
GitHub Actions ↓
auto-rerun-fail-jobs ↓
Permission Check (Broker) ↓
Failure Classifier ↓
┌───────────────┼───────────────┐
↓               ↓               ↓
RETRY        DEBUG           BLOCK
(transient)  (code/test)     (perm/sec)
    ↓             ↓
RERUN JOB    ↓ debug-error ↓ patch ↓ verify ↓
    ↓
Observe ↓
Report ↓ PR Comment + Status ↓
project-status-auto-update
```

### Status Metadata
```json
{
  "ci_status": {
    "state": "RETRYING",
    "run_id": "123456",
    "failed_jobs": ["test-python"],
    "attempt": 2,
    "max_attempts": 3,
    "failure_type": "transient/network",
    "next_retry_at": "2026-09-09T03:25:00+07:00",
    "permission_ok": true
  }
}
```

### PR Comment Template
```markdown
<!-- auto-rerun-fail-jobs -->
**CI Recovery Update**
🔹 Job: `test-python`
🔹 Failure: `transient / network timeout`
🔹 Attempt: 2/3
🔹 Status: ✅ RETRYING — Next in 60s
🔹 Strategy: Exponential Backoff

**If fail again:** Will handoff to `debug-error`
```

---

## ✅ Final Architecture Strengths
1. **Smart Classification:** ไม่กดรันตาบอด → ประหยัดเงิน/เวลา
2. **Job-Level Rerun:** ไม่เสียเวลารันส่วนที่ผ่านแล้ว
3. **Permission-Safe:** แยกสิทธิ์ `actions:write` / `workflows:write`
4. **Closed-Loop:** เชื่อมกับ Debug/Patch/Status/Comment
5. **Audit Full:** บันทึกทุกขั้นตอน, ประวัติการลอง
6. **Budget Control:** จำกัดจำนวนครั้ง, หยุดเมื่อครบ

---

## 🚀 พร้อมใช้งาน
**Skill นี้เติมเต็มระบบ CI ให้ชาญฉลาด — ไม่ใช่แค่ "ปุ่มรันซ้ำ"** แต่เป็น **Engine กู้คืนความล้มเหลว** ที่ทำงานร่วมกับ Credential, Debug, Status ได้สมบูรณ์ ✅🔐🔄

ต้องการให้ผมเขียน **Python Implementation จริง** หรือ **Workflow YAML** สำหรับนำไปใช้ใน GitHub Actions ทันทีไหมครับ? 🧩💻✅
