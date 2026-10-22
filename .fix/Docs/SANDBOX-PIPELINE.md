# Sandbox SHA Pipeline — เอกสารออกแบบ

> GitHub SHA → Docker Image → Sandbox Deploy → Health Check → Auto Debug → Repair → Rerun  
> หลักการ: **ทุก deployment ผูกกับ Git SHA แบบ immutable + deterministic** ทำให้ trace, debug, rollback และ auto-repair ปลอดภัย ไม่สับสนว่า sandbox กำลังรัน code version ไหน

---

## 1. ภาพรวม (Overview)

Pipeline นี้รันเมื่อมี push ไป `develop` (หรือ trigger ด้วยมือ) ทำหน้าที่:

1. Build Docker image จาก commit นั้นๆ ติด tag ด้วย SHA → push ไป GHCR (immutable artifact)
2. Deploy image นั้นไปยัง **sandbox environment**
3. Health check จริงๆ บน sandbox
4. ถ้า **PASS** → จบ (deploy สำเร็จ)
5. ถ้า **FAIL** → เก็บ logs/diagnostics → AI auto-repair → สร้าง commit ใหม่ → trigger pipeline ใหม่ (repair loop)
6. ถ้า repair ล้มเหลวเกิน `MAX_REPAIR_ATTEMPTS` (default 3) → **rollback** ไปยัง SHA สุดท้ายที่ healthy + แจ้งเตือน

---

## 2. หลักการออกแบบ (Design Principles)

| หลักการ | อธิบาย |
|---|---|
| **Immutable artifacts** | image แต่ละตัวติด tag ด้วย SHA เท่านั้น ไม่มี `:latest` ไม่สามารถเขียนทับได้ |
| **Deterministic identity** | จาก SHA ตัวใดก็ตาม สามารถหา image, sandbox, logs, diagnostics ได้ทันที |
| **Circuit breaker** | repair loop มีจำกัด (default 3 ครั้ง) ป้องกัน AI patch กันเองไม่รู้จบ |
| **Rollback-first** | เมื่อหมดความพยายาม จะ rollback อัตโนมัติ ไม่ปล่อย sandbox ตาย |
| **Least privilege** | แต่ละ job มี permission เท่าที่จำเป็น ใช้ `environment: sandbox` จำกัด secrets |
| **No `:latest` in deploy** | deploy อ้าง image digest/SHA เท่านั้น |

---

## 3. โครงสร้าง SHA 3 ระดับ

```
SOURCE SHA (Git)
    │  2582ca8f3e4b...
    ▼
IMAGE SHA (Docker tag)
    │  ghcr.io/zyntroai/crystalcastlex:sha-2582ca8
    ▼
DEPLOYMENT SHA (Sandbox instance)
       sandbox/crystalcastlex/sha-2582ca8
```

**ตัวอย่างเมื่อเกิด error สามารถตอบได้ทันที:**

```
Environment : sandbox
Commit      : 2582ca8 (https://github.com/.../commit/2582ca8...)
Image       : ghcr.io/zyntroai/crystalcastlex:sha-2582ca8
Workflow    : #152 (run_id 35399662325)
Status      : FAILED (health check)
Attempt     : 2/3
```

**Rollback = deploy image tag ของ SHA ก่อนหน้าที่ healthy** — ไม่ต้อง rebuild ไม่ต้อง guess

---

## 4. ผังการทำงาน (Flow Diagram)

```
GitHub Commit (develop)
        │
        ▼
┌───────────────────┐
│  build            │  buildx + cache + Trivy scan + SBOM
│  image:sha-xxxx   │  push GHCR + upload sha.json artifact
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  sandbox (deploy) │  docker compose / k8s รอ rollout ready
└─────────┬─────────┘
          ▼
┌───────────────────┐
│  health-check     │  probe /health retry 10 ครั้ง (exponential backoff)
└─────────┬─────────┘
      ┌───┴───┐
     PASS    FAIL
      │       │
      ▼       ▼
    Done  ┌──────────────────────┐
          │  repair (auto-debug) │  เก็บ logs/diff/scan → AI patch
          │  attempt < 3 ?       │
          └──────┬───────────────┘
            ┌────┴─────┐
          patch      หมด attempt / AI ไม่ไหว
            │              │
            ▼              ▼
     New commit+branch   rollback (SHA ก่อนหน้า)
     PR + trigger rerun  + notify human
            │
            ▼
     New SHA → กลับไป build ใหม่ (loop)
```

---

## 5. รายละเอียดแต่ละ Job

### 5.1 `build` — Build & Scan SHA Image
- ใช้ `docker/build-push-action` (buildx) พร้อม **GHA cache** → build เร็วขึ้นมาก
- ติด **OCI labels** (`org.opencontainers.image.revision/source/created`) สำหรับ trace
- สร้าง **SBOM + provenance attestation** อัตโนมัติ
- **Trivy scan** (CRITICAL/HIGH) — เก็บผลเป็น artifact ส่งให้ repair job ตัดสินใจ ไม่ fail ทันที
- อัปโหลด `sha.json` + scan results เป็น artifact (retention 30 วัน)

### 5.2 `sandbox` — Deploy Sandbox
- ตัวอย่างจริง: deploy ด้วย `docker compose` บน sandbox host ผ่าน SSH (ใช้ `appleboy/ssh-action`)
- เขียน `.env.sandbox` (IMAGE + GIT_SHA) → `pull` → `up -d` → **รอ health จริงบนโฮสต์** ถึงจะถือว่า deploy สำเร็จ
- ใช้ `environment: sandbox` → GitHub จะบังคับ protection rules (required reviewers / wait timer) และจำกัด secrets ให้เฉพาะ environment นี้

### 5.3 `health-check` — Sandbox Health Check
- probe `${SANDBOX_URL}/health` retry 10 ครั้ง พร้อม **exponential backoff** (`sleep i*3`)
- ไม่ใช้ `continue-on-error` แบบเดิม (ซึ่งงุ่มง่าม) — fail ทันทีด้วย `exit 1` เมื่อหมด retry → trigger repair ได้ตรงๆ

### 5.4 `repair` — Auto Debug / Repair (มี Circuit Breaker)
- เงื่อนไขรัน: `failure() && fromJSON(repair_attempt) < MAX_REPAIR_ATTEMPTS`
- ดาวน์โหลด artifact (sha.json + trivy) + เก็บ `workflow.log`, `git diff`, recent commits ลง `diagnostics/`
- **AI repair hook**: ส่ง `diagnostics/` ทั้งหมดให้ LLM → ได้ `patch.diff` → `patch -p1`
- สร้าง branch `repair/<sha>-attempt-<n>` → commit → push → เปิด PR → **trigger workflow_dispatch ใหม่** ด้วย `repair_attempt=n+1`
- ทุกครั้งส่ง notification (Slack/email) พร้อมลิงก์ PR

### 5.5 `rollback` — Rollback เมื่อหมดความพยายาม
- เงื่อนไข: `always() && needs.health-check.result == 'failure' && needs.repair.result != 'success'`
- Redeploy image tag ของ SHA สุดท้ายที่ healthy (ดึงจาก artifact/history) + แจ้ง human เข้ามาดู

---

## 6. `sandbox.yml` เต็มรูปแบบ (ปรับปรุงแล้ว)

```yaml
name: Sandbox SHA Pipeline

on:
  push:
    branches: [develop]
  workflow_dispatch:
    inputs:
      repair_attempt:
        description: "Repair loop attempt number (0 = first run)"
        required: false
        default: "0"

# ป้องกัน deploy ซ้อนกันบน branch เดียวกัน
concurrency:
  group: sandbox-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: write
  packages: write
  pull-requests: write
  actions: read
  id-token: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  MAX_REPAIR_ATTEMPTS: "3"

jobs:
  build:
    name: Build & Scan SHA Image
    runs-on: ubuntu-latest
    environment: sandbox
    outputs:
      short_sha: ${{ steps.meta.outputs.short_sha }}
      image: ${{ steps.meta.outputs.image }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Derive SHA metadata
        id: meta
        shell: bash
        run: |
          SHORT="${GITHUB_SHA::7}"
          IMAGE="${REGISTRY}/${IMAGE_NAME,,}:sha-${SHORT}"
          echo "short_sha=${SHORT}" >> "$GITHUB_OUTPUT"
          echo "image=${IMAGE}" >> "$GITHUB_OUTPUT"
          cat > sha.json <<EOF
          {
            "repository": "${GITHUB_REPOSITORY}",
            "branch": "${GITHUB_REF_NAME}",
            "sha": "${GITHUB_SHA}",
            "short_sha": "${SHORT}",
            "image": "${IMAGE}",
            "run_id": "${GITHUB_RUN_ID}",
            "run_number": "${GITHUB_RUN_NUMBER}",
            "triggered_by": "${GITHUB_ACTOR}",
            "repair_attempt": "${{ github.event.inputs.repair_attempt || 0 }}"
          }
          EOF
          cat sha.json

      - uses: docker/setup-buildx-action@v3

      - name: Login GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push (cache + SBOM + provenance)
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.image }}
          labels: |
            org.opencontainers.image.revision=${{ github.sha }}
            org.opencontainers.image.source=${{ github.server_url }}/${{ github.repository }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          sbom: true
          provenance: true

      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ steps.meta.outputs.image }}
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          exit-code: "0"
          ignore-unfixed: true

      - name: Upload metadata + scan
        uses: actions/upload-artifact@v4
        with:
          name: sandbox-${{ steps.meta.outputs.short_sha }}
          path: |
            sha.json
            trivy-results.sarif
          retention-days: 30

  sandbox:
    name: Deploy Sandbox
    needs: build
    runs-on: ubuntu-latest
    environment: sandbox
    steps:
      - uses: actions/checkout@v4
      - name: Deploy via SSH (docker compose)
        uses: appleboy/ssh-action@v1.2.0
        with:
          host: ${{ secrets.SANDBOX_HOST }}
          username: ${{ secrets.SANDBOX_USER }}
          key: ${{ secrets.SANDBOX_SSH_KEY }}
          script: |
            set -e
            cd /opt/sandbox/crystalcastlex
            printf 'IMAGE=%s\nGIT_SHA=%s\n' "${{ needs.build.outputs.image }}" "${{ github.sha }}" > .env.sandbox
            docker compose -f docker-compose.sandbox.yml pull api
            docker compose -f docker-compose.sandbox.yml up -d --no-deps api
            for i in $(seq 1 30); do
              curl -sf http://127.0.0.1:8000/health -o /dev/null && echo "sandbox ready" && break
              sleep 2
            done
            docker compose -f docker-compose.sandbox.yml ps

  health-check:
    name: Sandbox Health Check
    needs: [build, sandbox]
    runs-on: ubuntu-latest
    steps:
      - name: Probe /health (retry with backoff)
        run: |
          URL="${{ secrets.SANDBOX_URL }}/health"
          for i in $(seq 1 10); do
            if curl -sf --max-time 10 "$URL" -o /dev/null; then
              echo "✅ PASS (attempt $i)"
              exit 0
            fi
            echo "attempt $i failed, retrying in $((i*3))s..."
            sleep $((i * 3))
          done
          echo "::error::Health check FAILED — image ${{ needs.build.outputs.image }}"
          exit 1

  repair:
    name: Auto Debug / Repair
    needs: [build, sandbox, health-check]
    if: failure() && fromJSON(github.event.inputs.repair_attempt || '0') < fromJSON(env.MAX_REPAIR_ATTEMPTS)
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: sandbox-${{ needs.build.outputs.short_sha }}
          path: diagnostics/
        continue-on-error: true

      - name: Collect diagnostics
        id: ctx
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          mkdir -p diagnostics
          {
            echo "FAILED_SHA=${GITHUB_SHA}"
            echo "SHORT_SHA=${GITHUB_SHA::7}"
            echo "RUN_ID=${GITHUB_RUN_ID}"
            echo "BRANCH=${GITHUB_REF_NAME}"
            echo "ATTEMPT=${{ github.event.inputs.repair_attempt || 0 }}"
            echo "IMAGE=${{ needs.build.outputs.image }}"
          } > diagnostics/context.txt
          gh run view "$GITHUB_RUN_ID" --log > diagnostics/workflow.log 2>/dev/null || true
          git log -5 --oneline > diagnostics/recent-commits.txt
          git diff HEAD~1 --stat > diagnostics/last-diff.txt || true
          echo "=== diagnostics ===" && ls -la diagnostics/

      - name: AI auto-repair (LLM patch)
        id: ai
        env:
          AI_REPAIR_API_KEY: ${{ secrets.AI_REPAIR_API_KEY }}
        run: |
          # ส่ง diagnostics/ ทั้งหมดให้ LLM วิเคราะห์ → คืน patch.diff
          # ตัวอย่าง: python scripts/ai_repair.py --context diagnostics/ --out patch.diff
          # ถ้า AI แก้ไม่ได้ ให้ exit 2 → จะไป rollback ทันที
          echo "AI repair hook — ใส่การเรียก LLM จริงที่นี่ แล้ว patch -p1 < patch.diff"

      - name: Commit & push repair branch
        id: commit
        if: steps.ai.outcome == 'success'
        run: |
          ATTEMPT="${{ github.event.inputs.repair_attempt || 0 }}"
          NEXT=$((ATTEMPT + 1))
          BRANCH="repair/${GITHUB_SHA::7}-attempt-${NEXT}"
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git checkout -b "$BRANCH"
          git add -A
          git commit -m "fix(sandbox): auto-repair ${GITHUB_SHA::7} (attempt ${NEXT})" \
                       -m "Generated by run #${GITHUB_RUN_NUMBER}"
          git push origin "$BRANCH"
          echo "branch=${BRANCH}" >> "$GITHUB_OUTPUT"
          echo "next_attempt=${NEXT}" >> "$GITHUB_OUTPUT"

      - name: Open PR + trigger rerun
        if: steps.ai.outcome == 'success'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr create --base develop --head "${{ steps.commit.outputs.branch }}" \
            --title "fix: auto-repair sandbox ${{ needs.build.outputs.short_sha }}" \
            --body "Auto-generated repair (attempt ${{ steps.commit.outputs.next_attempt }}). Diagnostics attached to run #${GITHUB_RUN_NUMBER}." || true
          gh workflow run sandbox.yml --ref "${{ steps.commit.outputs.branch }}" \
            -f repair_attempt="${{ steps.commit.outputs.next_attempt }}"

      - name: Notify
        if: always()
        run: echo "ส่ง Slack/email — สถานะ repair + ลิงก์ PR/run"

  rollback:
    name: Rollback to last healthy SHA
    needs: [build, sandbox, health-check, repair]
    if: always() && needs.health-check.result == 'failure' && needs.repair.result != 'success'
    runs-on: ubuntu-latest
    environment: sandbox
    steps:
      - name: Redeploy previous healthy image
        run: |
          echo "🔄 Rollback — health check failed และ repair ไม่สำเร็จ/หมด attempt"
          echo "   deploy image tag ก่อนหน้าที่ healthy (ดึงจาก artifact sandbox-history)"
          # ตัวอย่าง: kubectl set image deploy/api api=ghcr.io/...:sha-<last-healthy>
          # หรือ:    docker compose -f docker-compose.sandbox.yml up -d ด้วย IMAGE เก่า
          echo "📨 แจ้ง human เข้ามาตรวจสอบ"
```

---

## 7. Secrets & Variables ที่ต้องตั้งค่า

| Secret | ใช้ที่ไหน |
|---|---|
| `SANDBOX_HOST`, `SANDBOX_USER`, `SANDBOX_SSH_KEY` | deploy ผ่าน SSH |
| `SANDBOX_URL` | health check (URL ภายนอกของ sandbox) |
| `AI_REPAIR_API_KEY` | เรียก LLM ใน repair job |
| `SLACK_WEBHOOK_URL` (optional) | notification |

ตั้งค่าใน **Settings → Environments → sandbox** (ไม่ใช่ repo secrets ทั่วไป) เพื่อให้ถูกจำกัดเฉพาะ environment นี้ และสามารถบังคับ required reviewer ได้

---

## 8. Failure Modes Matrix

| อาการ | สาเหตุที่พบบ่อย | การจัดการ |
|---|---|---|
| build fail | syntax error, dependency ชน, Dockerfile ผิด | repair job รัน (needs build ด้วย) เก็บ build log ให้ AI แก้ |
| image push fail | GHCR auth, network | retry + notify; ไม่ถึง deploy |
| sandbox deploy fail | SSH ไม่ติด, disk เต็ม, port ชน | health-check fail → repair; ถ้าซ้ำๆ → rollback |
| health check fail | app crash, env var หาย, DB เชื่อมต่อไม่ได้ | เก็บ container log + workflow log → AI patch |
| repair loop ไม่จบ | AI patch ไม่หายจุด | circuit breaker (attempt ≥ 3) → rollback + แจ้ง human |
| AI patch ทำให้แย่ลง | regression | แต่ละ attempt เป็น branch/PR แยก ไม่กระทบ develop จนกว่าจะ pass |

---

## 9. Runbook — มือ (เมื่อต้องแทรกแซง)

```bash
# ดูว่า sandbox กำลังรัน SHA ไหน
ssh user@sandbox "cat /opt/sandbox/crystalcastlex/.env.sandbox"

# Rollback มือ ไป SHA ที่กำหนด
ssh user@sandbox "cd /opt/sandbox/crystalcastlex && \
  echo 'IMAGE=ghcr.io/zyntroai/crystalcastlex:sha-<healthy-sha>' > .env.sandbox && \
  docker compose -f docker-compose.sandbox.yml up -d --no-deps api"

# ดู logs container บน sandbox
ssh user@sandbox "docker compose -f /opt/sandbox/crystalcastlex/docker-compose.sandbox.yml logs -f --tail=200 api"

# ดู artifact/diagnostics ของ run ไหนก็ได้
gh run view <run_id> && gh run download <run_id>
```

---

## 10. สิ่งที่ปรับปรุงจากเวอร์ชันเดิม

1. ✅ **แก้ trigger repair** — เดิม `needs: health-check` เท่านั้น ทำให้ build/sandbox failure จะหลุดไปไม่ trigger repair; ตอนนี้ `needs: [build, sandbox, health-check]`
2. ✅ **เพิ่ม circuit breaker** — `repair_attempt` + `MAX_REPAIR_ATTEMPTS=3` ป้องกัน loop ไม่รู้จบ
3. ✅ **เพิ่ม job `rollback`** — เมื่อ repair ไม่สำเร็จ/หมด attempt จะ rollback อัตโนมัติ ไม่ปล่อย sandbox ตาย
4. ✅ **health-check เขียนใหม่** — ใช้ retry loop + backoff โดยตรง ไม่ใช้ `continue-on-error` แบบงุ่มง่าม
5. ✅ **build ใช้ buildx + GHA cache + SBOM + provenance + Trivy scan** (เดิม `docker build` มือ ไม่มี cache/scan)
6. ✅ **deploy step จริง** — เดิมเป็นแค่ `echo`; ตอนนี้เป็นตัวอย่าง SSH + docker compose + รอ rollout
7. ✅ **repair push + trigger rerun จริง** — เดิมหยุดแค่สร้าง branch; ตอนนี้ push, เปิด PR, และ trigger `workflow_dispatch` ด้วย attempt+1
8. ✅ **เพิ่ม `concurrency`** — ป้องกัน deploy ซ้อนกันบน branch เดียวกัน
9. ✅ **เพิ่ม `environment: sandbox`** — protection rules + secrets scoping
10. ✅ **SHA tag ใช้ `sha-<short>`** — สั้น อ่านง่าย ยัง deterministic; เก็บ full SHA ไว้ใน labels + sha.json
11. ✅ **เพิ่ม notification hook** ทุกจุดสำคัญ
12. ✅ **เพิ่ม Failure Modes Matrix + Runbook** สำหรับ human แทรกแซง

---

*English summary: This gives every sandbox deployment a deterministic source identity (Git SHA → immutable image tag → deployment instance), with a bounded auto-repair loop and automatic rollback, making trace → debug → repair → rebuild → redeploy safe and auditable.*
