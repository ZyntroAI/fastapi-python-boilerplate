#!/usr/bin/env bash
# ติดตั้ง workflow ที่ซ่อมแล้วจาก deliverables/ci/workflows-repaired/ เข้า .github/
#
# ทำไมต้องมีสคริปต์นี้: Fig GitHub App ไม่มี `workflows` scope จึง push
# `.github/workflows/**` ไม่ได้ (403 refusing to allow a GitHub App to create or
# update workflow) ไฟล์ที่ซ่อมแล้วจึงเดินทางมาใน PR ใต้ deliverables/ แล้วค่อย
# ย้ายเข้า .github/ ด้วยสคริปต์นี้
#
# ใช้:
#   bash deliverables/ci/workflows-repaired/install.sh          # dry-run
#   bash deliverables/ci/workflows-repaired/install.sh --apply  # ติดตั้งจริง
#
# สคริปต์เป็น dry-run โดยค่าเริ่มต้น ต้องส่ง --apply ถึงจะเขียน

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SRC/../../.." && pwd)"
DST="$ROOT/.github/workflows"
APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

if [ ! -d "$ROOT/.github" ]; then
    echo "ไม่พบ .github/ — รันสคริปต์จากใน repo (root: $ROOT)" >&2
    exit 1
fi

run() {
    if [ "$APPLY" = "1" ]; then
        "$@"
    else
        printf '  [dry-run] %s\n' "$*"
    fi
}

echo "ต้นทาง : $SRC"
echo "ปลายทาง: $DST"
echo

# 1. ไฟล์ workflow ทุกตัว ยกเว้น config ของ release-drafter
echo "คัดลอก workflow:"
for f in "$SRC"/*.yml "$SRC"/*.yaml "$SRC"/github-actions-autodebug-autorerun; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    case "$base" in
        release-drafter.config.yml) continue ;;   # จัดการแยกด้านล่าง
        install.sh) continue ;;
    esac
    printf '  %s\n' "$base"
    run cp "$f" "$DST/$base"
done

# 2. release_drafter.yaml เดิม = config ไม่ใช่ workflow -> ย้ายไปที่ที่ release-drafter อ่านจริง
echo
echo "ย้าย config ของ release-drafter:"
echo "  .github/workflows/release_drafter.yaml -> .github/release-drafter.yml"
run mv -f "$ROOT/.github/workflows/release_drafter.yaml" "$ROOT/.github/release-drafter.yml"

# 3. เขียนทับ config ด้วยตัวที่ปรับแล้ว (ถ้ามี #5.5)
if [ -f "$SRC/release-drafter.config.yml" ] && [ ! -f "$ROOT/.github/release-drafter.yml" ]; then
    echo "  เขียน .github/release-drafter.yml จาก config ใน deliverables"
    run cp "$SRC/release-drafter.config.yml" "$ROOT/.github/release-drafter.yml"
fi

echo
if [ "$APPLY" = "1" ]; then
    echo "ติดตั้งแล้ว ตรวจด้วย:"
else
    echo "ยังไม่ได้เขียน — รันซ้ำด้วย --apply เพื่อติดตั้งจริง ตรวจด้วย:"
fi
echo "  python deliverables/ci/verify_workflows.py"
