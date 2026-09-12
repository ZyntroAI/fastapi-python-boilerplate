#!/usr/bin/env bash
#
# check-mcp-environment.sh — ตรวจสภาพแวดล้อมสำหรับ MCP servers
#
# ตรวจ 3 ปัญหาหลักตามเอกสาร docs/MCP-Guide-Complete.md (MCP-DOC-2026-0912):
#   MCP-ERR-001  Google Cloud ADC
#   MCP-ERR-002  Runtime (Node.js / Dart / Go) + PATH
#   MCP-ERR-003  API Keys (Antimetal / Lovable / Mobbin / Windsor)
#
# ใช้งาน:
#   bash scripts/check-mcp-environment.sh              # ตรวจทั้งหมด
#   bash scripts/check-mcp-environment.sh --gcp        # เฉพาะ ADC
#   bash scripts/check-mcp-environment.sh --runtimes   # เฉพาะ runtime
#   bash scripts/check-mcp-environment.sh --keys       # เฉพาะ API keys
#
# Exit code: 0 = ผ่านทั้งหมด, 1 = พบปัญหา
#
# หมายเหตุความปลอดภัย: สคริปต์นี้ไม่พิมพ์ค่า secret ใด ๆ — แสดงแค่ว่ามี/ไม่มี

set -uo pipefail

DO_GCP=0
DO_RUNTIMES=0
DO_KEYS=0
FAIL=0
WARN=0

# ---------- สี (ปิดอัตโนมัติถ้าไม่ใช่ TTY) ----------
if [ -t 1 ]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; BOLD='\033[1m'; NC='\033[0m'
else
  GREEN=''; RED=''; YELLOW=''; BOLD=''; NC=''
fi

pass() { printf "  ${GREEN}[PASS]${NC} %s\n" "$1"; }
fail() { printf "  ${RED}[FAIL]${NC} %s\n" "$1"; FAIL=$((FAIL + 1)); }
warn() { printf "  ${YELLOW}[WARN]${NC} %s\n" "$1"; WARN=$((WARN + 1)); }
info() { printf "  ${BOLD}[INFO]${NC} %s\n" "$1"; }
head2() { printf "\n${BOLD}== %s ==${NC}\n" "$1"; }

# ---------- parse args ----------
if [ $# -eq 0 ]; then
  DO_GCP=1; DO_RUNTIMES=1; DO_KEYS=1
else
  for arg in "$@"; do
    case "$arg" in
      --gcp|--adc)      DO_GCP=1 ;;
      --runtimes|--rt)  DO_RUNTIMES=1 ;;
      --keys)           DO_KEYS=1 ;;
      -h|--help)
        sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'
        exit 0 ;;
      *)
        printf "ไม่รู้จัก option: %s (ใช้ --help)\n" "$arg" >&2
        exit 2 ;;
    esac
  done
fi

printf "${BOLD}ตรวจสภาพแวดล้อม MCP — MCP-DOC-2026-0912${NC}\n"

# =====================================================================
# MCP-ERR-001 — Google Cloud ADC
# =====================================================================
if [ "$DO_GCP" -eq 1 ]; then
  head2 "MCP-ERR-001: Google Cloud ADC"

  # 1) gcloud CLI ติดตั้งไหม
  if command -v gcloud >/dev/null 2>&1; then
    pass "gcloud CLI ติดตั้งแล้ว ($(gcloud --version 2>/dev/null | head -1))"
  else
    warn "gcloud CLI ไม่พบ — ต้องติดตั้งถ้าใช้ Google Cloud (ดู https://cloud.google.com/sdk/docs/install)"
  fi

  # 2) ADC ไฟล์อยู่ไหม
  ADC_PATH=""
  if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]; then
    ADC_PATH="$GOOGLE_APPLICATION_CREDENTIALS"
    if [ -f "$ADC_PATH" ]; then
      pass "GOOGLE_APPLICATION_CREDENTIALS ชี้ไฟล์ที่มีอยู่"
    else
      fail "GOOGLE_APPLICATION_CREDENTIALS ตั้งไว้แต่ไม่พบไฟล์"
    fi
  else
    case "$(uname -s)" in
      Darwin)  ADC_PATH="$HOME/.config/gcloud/application_default_credentials.json" ;;
      Linux)   ADC_PATH="$HOME/.config/gcloud/application_default_credentials.json" ;;
      MINGW*|MSYS*|CYGWIN*) ADC_PATH="${APPDATA:-$HOME}/gcloud/application_default_credentials.json" ;;
      *)       ADC_PATH="$HOME/.config/gcloud/application_default_credentials.json" ;;
    esac
    if [ -f "$ADC_PATH" ]; then
      pass "พบ ADC ที่ตำแหน่งมาตรฐาน"
    else
      fail "ไม่พบ ADC — รัน: gcloud auth application-default login"
    fi
  fi

  # 3) ตรวจ credential ใช้งานได้จริงด้วย python (ถ้ามี google.auth)
  if command -v python3 >/dev/null 2>&1; then
    if python3 -c "import google.auth" >/dev/null 2>&1; then
      if python3 -c "
import google.auth
c, _ = google.auth.default()
print('project=', c.quota_project_id or c.project_id or 'unknown')
" >/dev/null 2>&1; then
        pass "google.auth.default() ทำงานได้"
      else
        fail "google.auth.default() ล้มเหลว — credential ยังใช้ไม่ได้"
      fi
    else
      info "ไม่พบโมดูล google.auth (ข้ามการทดสอบ) — pip install google-auth"
    fi
  fi

  # 4) quota project
  if command -v gcloud >/dev/null 2>&1; then
    QP="$(gcloud config get-value project 2>/dev/null || true)"
    if [ -n "$QP" ] && [ "$QP" != "(unset)" ]; then
      pass "gcloud project ตั้งไว้แล้ว"
    else
      warn "ยังไม่ได้ตั้ง project — gcloud config set project <PROJECT_ID>"
    fi
  fi
fi

# =====================================================================
# MCP-ERR-002 — Runtimes + PATH
# =====================================================================
if [ "$DO_RUNTIMES" -eq 1 ]; then
  head2 "MCP-ERR-002: Runtime + PATH"

  check_runtime() {
    _name="$1"; _cmd="$2"; _verflag="$3"; _required="$4"; _url="$5"
    if command -v "$_cmd" >/dev/null 2>&1; then
      _v="$("$_cmd" "$_verflag" 2>&1 | head -1)"
      pass "$_name: $_v"
    else
      if [ "$_required" -eq 1 ]; then
        fail "$_name ไม่พบ — ติดตั้งจาก $_url"
      else
        warn "$_name ไม่พบ (ไม่บังคับ) — $_url"
      fi
    fi
  }

  # Node.js จำเป็นสำหรับ MCP server ส่วนใหญ่
  check_runtime "Node.js" "node" "--version" 1 "https://nodejs.org/en/download"
  check_runtime "npm"     "npm"  "--version" 1 "https://nodejs.org/en/download"
  # Dart / Go — ขึ้นกับว่าใช้ server เขียนด้วยอะไร
  check_runtime "Dart"    "dart" "--version" 0 "https://dart.dev/get-dart"
  check_runtime "Go"      "go"   "version"   0 "https://go.dev/dl/"

  # PATH ของ global bin ที่มักตกหล่น
  # เตือนเฉพาะกรณีที่โฟลเดอร์มีอยู่จริง แต่ไม่อยู่ใน PATH — ไม่เตือนโฟลเดอร์ที่ไม่มี
  head2 "PATH check"
  _missing_paths=""
  _to_check="$HOME/.local/bin /usr/local/go/bin $HOME/.pub-cache/bin"
  for _d in $_to_check; do
    [ -d "$_d" ] || continue
    case ":$PATH:" in
      *":$_d:"*) ;;
      *) _missing_paths="$_missing_paths $_d" ;;
    esac
  done

  if [ -n "$_missing_paths" ]; then
    warn "PATH ขาดโฟลเดอร์ที่มีอยู่จริง:$_missing_paths  (เพิ่มใน ~/.zshrc หรือ ~/.bashrc)"
  else
    pass "PATH ครบสำหรับ global bin ที่มีในเครื่อง"
  fi

  # config ของ MCP ในโปรเจกต์
  if [ -f ".agent/settings.json" ]; then
    if grep -q '"mcpServers"' .agent/settings.json 2>/dev/null; then
      pass ".agent/settings.json มี mcpServers block"
      _cfg="$(grep -o '"configPath"[^,}]*' .agent/settings.json 2>/dev/null | head -1)"
      [ -n "$_cfg" ] && info "  configPath: $_cfg"
    else
      warn ".agent/settings.json ไม่มี mcpServers block"
    fi
  else
    info "ไม่พบ .agent/settings.json (รันจาก root ของโปรเจกต์หรือเปล่า?)"
  fi
fi

# =====================================================================
# MCP-ERR-003 — API keys
# =====================================================================
if [ "$DO_KEYS" -eq 1 ]; then
  head2 "MCP-ERR-003: API Keys"

  check_key() {
    _var="$1"
    if [ -n "${!_var:-}" ]; then
      pass "$_var: ตั้งค่าแล้ว (ความยาว ${#_var} ตัวอักษร... ไม่แสดงค่า)"
    else
      warn "$_var: ยังไม่ได้ตั้งค่า"
    fi
  }

  for k in ANTIMETAL_API_KEY LOVABLE_API_KEY MOBBIN_API_KEY WINDSOR_API_KEY; do
    check_key "$k"
  done

  head2 "ความปลอดภัย: ตรวจว่า secret ไม่หลุดเข้า git"
  if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
    # ไฟล์ template ที่ปลอดภัยต่อการ track (มีแต่ชื่อ ไม่มีค่า)
    # ยกเว้น .env.example / .env.sample / .env.template
    _tracked_env="$(git ls-files 2>/dev/null \
      | grep -E '^\.env$|^\.env\.' \
      | grep -vE '\.(example|sample|template)$' || true)"

    if [ -n "$_tracked_env" ]; then
      fail "มีไฟล์ .env ที่ไม่ใช่ template ถูก track: $(echo "$_tracked_env" | tr '\n' ' ')— ใช้ git rm --cached"
    else
      pass "ไม่มีไฟล์ .env ที่ไม่ใช่ template ถูก track"
    fi

    # แจ้งไฟล์ template ที่ track อยู่ (ไม่ใช่ปัญหา)
    _tracked_tmpl="$(git ls-files 2>/dev/null | grep -E '^\.env\.' | grep -E '\.(example|sample|template)$' || true)"
    [ -n "$_tracked_tmpl" ] && info "ไฟล์ template ที่ track (ปกติ): $(echo "$_tracked_tmpl" | tr '\n' ' ')"

    # ตรวจว่า .env (ถ้ามี) ถูก ignore — ไฟล์ที่ track แล้วจะไม่ถูก ignore
    if [ -f ".env" ]; then
      if git ls-files --error-unmatch .env >/dev/null 2>&1; then
        : # tracked แล้ว — รายงานไปแล้วข้างบน
      elif git check-ignore -q .env 2>/dev/null; then
        pass ".env ถูก gitignore แล้ว"
      else
        fail ".env ไม่ถูก gitignore — เสี่ยง secret หลุด!"
      fi
    else
      info "ไม่พบไฟล์ .env ในเครื่อง"
    fi
  else
    info "ไม่ใช่ git repo (ข้ามการตรวจ)"
  fi
fi

# =====================================================================
# สรุป
# =====================================================================
printf "\n${BOLD}== สรุป ==${NC}\n"
if [ "$FAIL" -eq 0 ] && [ "$WARN" -eq 0 ]; then
  printf "${GREEN}ผ่านทั้งหมด — สภาพแวดล้อมพร้อมใช้${NC}\n"
  exit 0
elif [ "$FAIL" -eq 0 ]; then
  printf "${YELLOW}ผ่าน แต่มี %d คำเตือน${NC}\n" "$WARN"
  exit 0
else
  printf "${RED}พบปัญหา %d รายการ (คำเตือน %d)${NC}\n" "$FAIL" "$WARN"
  printf "ดูวิธีแก้ใน docs/MCP-Guide-Complete.md\n"
  exit 1
fi
