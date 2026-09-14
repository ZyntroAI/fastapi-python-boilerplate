#!/usr/bin/env bash
# ชุดทดสอบสำหรับ check-mcp-environment.sh — รันกับ main ที่ merge แล้ว
# ตรวจ 4 ด้าน: syntax, flags, exit code, ความปลอดภัย (ไม่พิมพ์ secret)
set -uo pipefail

SCRIPT="./scripts/check-mcp-environment.sh"
PASS=0; FAIL=0
ok()   { printf "  [PASS] %s\n" "$1"; PASS=$((PASS+1)); }
bad()  { printf "  [FAIL] %s\n" "$1"; FAIL=$((FAIL+1)); }

echo "== T1: bash syntax =="
if bash -n "$SCRIPT" 2>/dev/null; then ok "syntax ผ่าน"; else bad "syntax ล้มเหลว"; fi

echo "== T2: executable + shebang =="
[ -x "$SCRIPT" ] && ok "executable bit ตั้งไว้" || bad "ไม่มี executable bit"
head -1 "$SCRIPT" | grep -q '^#!/usr/bin/env bash' && ok "shebang ถูกต้อง" || bad "shebang ผิด"

echo "== T3: --help ออก 0 และมีเนื้อหา =="
OUT=$("$SCRIPT" --help 2>&1); RC=$?
[ "$RC" -eq 0 ] && ok "--help exit 0" || bad "--help exit $RC"
echo "$OUT" | grep -q "MCP-ERR-001" && ok "--help อ้าง MCP-ERR-001" || bad "--help ขาดเนื้อหา"
# --help ต้องไม่รั่วโค้ดออกมา (เคยพังเพราะใช้ช่วงบรรทัดตายตัว)
if echo "$OUT" | grep -qE 'set -uo pipefail|DO_GCP=|shebang'; then
  bad "--help รั่วโค้ดออกมา"
else
  ok "--help ไม่รั่วโค้ด"
fi
# ต้องมีบรรทัด Exit code และไม่ลากโค้ดต่อท้าย
echo "$OUT" | grep -q "Exit code:" && ok "--help มีบรรทัด Exit code" || bad "--help ขาด Exit code"

echo "== T4: flag เฉพาะทาง =="
for f in --gcp --runtimes --keys; do
  OUT=$("$SCRIPT" "$f" 2>&1)
  if echo "$OUT" | grep -qE "MCP-ERR|สรุป"; then ok "$f ทำงาน"; else bad "$f ไม่ทำงาน"; fi
done

echo "== T5: flag ที่ไม่รู้จัก ต้อง exit 2 =="
"$SCRIPT" --bogus >/dev/null 2>&1; RC=$?
[ "$RC" -eq 2 ] && ok "flag ผิด exit 2" || bad "flag ผิด exit $RC (ควรเป็น 2)"

echo "== T6: ผลลัพธ์เป็น 0 หรือ 1 เท่านั้น (ไม่ crash) =="
"$SCRIPT" >/dev/null 2>&1; RC=$?
case "$RC" in
  0) ok "exit 0 (ผ่าน)" ;;
  1) ok "exit 1 (พบปัญหา — ถูกต้องเพราะ .env ถูก track)" ;;
  *) bad "exit $RC — ผิดคาด (คาด 0 หรือ 1)" ;;
esac

echo "== T7: ความปลอดภัย — ต้องไม่พิมพ์ค่า secret =="
FAKE="SUPERSECRETVALUE1234567890"
OUT=$(ANTIMETAL_API_KEY="$FAKE" "$SCRIPT" --keys 2>&1)
if echo "$OUT" | grep -q "$FAKE"; then
  bad "สคริปต์พิมพ์ค่า secret ออกมา!"
else
  ok "ไม่พิมพ์ค่า secret (แสดงแค่ set/not-set)"
fi
# ต้องรายงานว่าตั้งค่าแล้ว (ข้อความไทย)
if echo "$OUT" | grep -q "ANTIMETAL_API_KEY: ตั้งค่าแล้ว"; then
  ok "ตรวจพบ key ที่ตั้งไว้ถูกต้อง"
else
  bad "ไม่ตรวจพบ key ที่ตั้งไว้"
fi
# ต้องรายงานความยาวของ "ค่า" ไม่ใช่ความยาวชื่อตัวแปร (ชื่อยาว 17)
EXPECT_LEN=${#FAKE}
if echo "$OUT" | grep -q "ความยาว ${EXPECT_LEN} ตัวอักษร"; then
  ok "รายงานความยาวของค่าถูกต้อง (${EXPECT_LEN} ไม่ใช่ 17)"
else
  bad "รายงานความยาวผิด — นับชื่อตัวแปรแทนค่า"
fi

echo "== T8: ตรวจ .env ที่ track ผิด (fixture) =="
TMP=$(mktemp -d); cd "$TMP"
git init -q .; git config user.email t@t; git config user.name t
printf 'SECRET=x\n' > .env            # ซิมูเลต .env ถูก track
printf 'KEY=\n' > .env.example        # template ปลอดภัย
git add -A 2>/dev/null; git commit -qm init 2>/dev/null
mkdir -p scripts docs .agent
cp /dev/null .agent/settings.json
cp "$OLDPWD/$SCRIPT" scripts/ 2>/dev/null || cp "$SCRIPT" scripts/
OUT=$(bash scripts/check-mcp-environment.sh --keys 2>&1)
if echo "$OUT" | grep -q "git rm --cached"; then ok "จับ .env ที่ track ผิดได้"; else bad "ไม่จับ .env ที่ track ผิด"; fi
if echo "$OUT" | grep -q "template ที่ track (ปกติ)"; then ok ".env.example รายงานเป็น template ที่ปลอดภัย"; else bad ".env.example ถูกตีเป็นปัญหาผิด"; fi
cd - >/dev/null; rm -rf "$TMP"

echo ""
echo "=== สรุป: ผ่าน $PASS / ล้ม $FAIL ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
